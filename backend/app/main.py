from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import AIProvider
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import create_db_engine, create_session_factory
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.security import PasswordService
from app.core.throttle import LoginThrottle


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    if app.state.engine is not None:
        app.state.engine.dispose()
    close = getattr(app.state.ai_provider, "close", None)
    if callable(close):
        close()


def create_app(settings: Settings | None = None, ai_provider: AIProvider | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    if settings.database_url:
        app.state.engine = create_db_engine(settings.database_url)
        app.state.session_factory = create_session_factory(app.state.engine)
    else:
        app.state.engine = None
        app.state.session_factory = None
    app.state.passwords = PasswordService.from_settings(settings)
    app.state.login_throttle = LoginThrottle(settings.login_max_failures, settings.login_window_seconds)

    # None means the AI assistants are switched off (no key configured).
    if ai_provider is not None:
        app.state.ai_provider = ai_provider
    elif settings.ai_configured:
        app.state.ai_provider = OpenAIProvider(
            api_key=settings.openai_api_key.get_secret_value().strip(),
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.ai_timeout_seconds,
        )
    else:
        app.state.ai_provider = None

    # Middleware added last is outermost: CORS wraps everything so error responses carry CORS headers too.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Protection"],
        expose_headers=["X-Request-ID"],
    )

    register_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


_settings = get_settings()
_settings.assert_production_ready()
app = create_app(_settings)
