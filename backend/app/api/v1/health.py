from fastapi import APIRouter, Depends, Request

from app.core.config import Settings
from app.core.deps import get_app_settings
from app.schemas.health import HealthResponse
from app.services import health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health(request: Request, settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    return health_service.get_health(settings, request.app.state.session_factory)
