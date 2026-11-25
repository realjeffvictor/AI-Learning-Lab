from starlette.responses import Response

from app.core.config import Settings


def set_refresh_cookie(response: Response, token: str, max_age: int, settings: Settings) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=settings.refresh_cookie_path,
    )


def clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
