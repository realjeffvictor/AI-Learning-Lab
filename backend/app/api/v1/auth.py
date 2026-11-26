from fastapi import APIRouter, Depends, Request, Response

from app.api.cookies import clear_refresh_cookie, set_refresh_cookie
from app.api.deps import client_ip, get_auth_service, require_csrf_header
from app.api.rate_limit import ip_rate_limit
from app.core.config import Settings
from app.core.deps import get_app_settings
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService, AuthSession

router = APIRouter(prefix="/auth", tags=["auth"])

register_limit = ip_rate_limit("register", "rl_register_per_hour", 3600)
login_limit = ip_rate_limit("login", "rl_login_per_15min", 900)
refresh_limit = ip_rate_limit("refresh", "rl_refresh_per_15min", 900)


def _respond(response: Response, result: AuthSession, settings: Settings) -> TokenResponse:
    set_refresh_cookie(response, result.refresh_token, result.refresh_max_age, settings)
    response.headers["Cache-Control"] = "no-store"
    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        user=UserRead.model_validate(result.user),
    )


@router.post("/register", response_model=TokenResponse, status_code=201, dependencies=[Depends(register_limit)])
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    result = service.register(
        email=payload.email, password=payload.password, display_name=payload.display_name, ip=client_ip(request)
    )
    return _respond(response, result, settings)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_limit)])
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    result = service.login(email=payload.email, password=payload.password, ip=client_ip(request))
    return _respond(response, result, settings)


@router.post(
    "/refresh", response_model=TokenResponse, dependencies=[Depends(require_csrf_header), Depends(refresh_limit)]
)
def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    result = service.refresh(request.cookies.get(settings.refresh_cookie_name), client_ip(request))
    return _respond(response, result, settings)


@router.post("/logout", status_code=204, dependencies=[Depends(require_csrf_header)])
def logout(
    request: Request,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_app_settings),
) -> Response:
    service.logout(request.cookies.get(settings.refresh_cookie_name), client_ip(request))
    response = Response(status_code=204)
    clear_refresh_cookie(response, settings)
    return response
