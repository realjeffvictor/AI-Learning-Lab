from fastapi import Request

from app.core.config import Settings


def get_app_settings(request: Request) -> Settings:
    """Settings bound to the running app (lets tests build apps with custom settings)."""
    return request.app.state.settings
