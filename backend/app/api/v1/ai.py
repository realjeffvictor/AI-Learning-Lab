import uuid

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider
from app.api.deps import get_current_user, get_db
from app.core.config import Settings
from app.core.deps import get_app_settings
from app.models import User
from app.schemas.ai import (
    AIStatus,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    StudyPlanResponse,
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


def get_provider(request: Request) -> AIProvider | None:
    return request.app.state.ai_provider


@router.get("/status", response_model=AIStatus)
def read_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    provider: AIProvider | None = Depends(get_provider),
) -> AIStatus:
    return ai_service.get_status(db, settings, provider, user.id)


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    provider: AIProvider | None = Depends(get_provider),
) -> ChatResponse:
    return ai_service.chat(db, settings, provider, user, payload)


@router.post("/study-plan", response_model=StudyPlanResponse)
def post_study_plan(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    provider: AIProvider | None = Depends(get_provider),
) -> StudyPlanResponse:
    return ai_service.study_plan(db, settings, provider, user)


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ai_service.list_conversations(db, user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConversationDetail:
    return ai_service.get_conversation(db, user.id, conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    ai_service.delete_conversation(db, user.id, conversation_id)
    return Response(status_code=204)
