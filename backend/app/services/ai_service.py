import re
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai.provider import AIProvider, ChatMessage, Completion, ProviderError
from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import utcnow
from app.models import Concept, User
from app.repositories import ai_repository, curriculum_repository, exercise_repository
from app.schemas.ai import (
    AIStatus,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    MessageRead,
    StudyPlanResponse,
    UsageRead,
)
from app.schemas.assessment import ConceptResult
from app.services import assessment_service

HISTORY_LIMIT = 10
MAX_LESSON_CHARS = 3000
MAX_EXERCISE_CHARS = 1500
WEAK_THRESHOLD = 0.7
MAX_WEAK_IN_CONTEXT = 5

_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_OUR_TAGS = re.compile(r"</?(learner_code|lesson_text|exercise_text)\s*>", re.IGNORECASE)


def strip_urls(text: str) -> str:
    """The study plan may only point at items from the database, so any URL the model writes is removed."""
    return _URL.sub("[link removed]", text)


def _clean(text: str) -> str:
    """Remove our own delimiter tags so learner text cannot close a block early."""
    return _OUR_TAGS.sub("", text)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "\n[truncated]"


def _title(message: str) -> str:
    collapsed = " ".join(message.split())
    return collapsed[:60]


def _usage(session: Session, settings: Settings, user_id: uuid.UUID) -> UsageRead:
    requests, tokens = ai_repository.get_usage(session, user_id, utcnow().date())
    return UsageRead(
        requests_used=requests,
        requests_limit=settings.ai_daily_request_limit,
        tokens_used=tokens,
        tokens_limit=settings.ai_daily_token_limit,
    )


def _check_limits(usage: UsageRead) -> None:
    if usage.requests_used >= usage.requests_limit:
        raise AppError(429, "ai_daily_limit", "You have reached today's AI request limit. It resets at midnight UTC.")
    if usage.tokens_used >= usage.tokens_limit:
        raise AppError(429, "ai_daily_limit", "You have used today's AI token allowance. It resets at midnight UTC.")


def _complete(provider: AIProvider, messages: list[ChatMessage], settings: Settings) -> Completion:
    try:
        return provider.complete(messages, settings.ai_max_output_tokens)
    except ProviderError as exc:
        raise AppError(502, "ai_provider_error", str(exc)) from None


def get_status(session: Session, settings: Settings, provider: AIProvider | None, user_id: uuid.UUID) -> AIStatus:
    return AIStatus(
        enabled=provider is not None,
        model=provider.model if provider is not None else None,
        usage=_usage(session, settings, user_id),
    )


def _weak_rows(session: Session, user_id: uuid.UUID) -> list[tuple[str, str, int, int]]:
    rows = exercise_repository.mastery(session, user_id)
    return [
        (slug, name, int(correct), int(total))
        for slug, name, _category, correct, total in rows
        if total and int(correct) / int(total) < WEAK_THRESHOLD
    ]


def _build_context(
    session: Session, user: User, lesson_id: uuid.UUID | None, exercise_id: uuid.UUID | None, code: str | None
) -> tuple[str, uuid.UUID | None, uuid.UUID | None]:
    parts = [f"Learner experience level: {user.profile.experience_level}."]
    weak = [name for _slug, name, _c, _t in _weak_rows(session, user.id)][:MAX_WEAK_IN_CONTEXT]
    if weak:
        parts.append("Concepts the learner scored below 70% on recently: " + ", ".join(weak) + ".")

    exercise = None
    if exercise_id is not None:
        exercise = exercise_repository.get(session, exercise_id)
        if exercise is None:
            raise AppError(404, "exercise_not_found", "Exercise not found.")
        lesson_id = exercise.lesson_id

    lesson = None
    if lesson_id is not None:
        lesson = curriculum_repository.get_lesson_by_id(session, lesson_id)
        if lesson is None:
            raise AppError(404, "lesson_not_found", "Lesson not found.")

    if lesson is not None:
        module = lesson.module
        parts.append(f"Current lesson: {lesson.title} (module: {module.title}, course: {module.course.title}).")
        if lesson.objectives:
            parts.append("Lesson objectives: " + "; ".join(lesson.objectives))
        if lesson.status == "published" and lesson.content_md:
            parts.append("<lesson_text>\n" + _clean(_clip(lesson.content_md, MAX_LESSON_CHARS)) + "\n</lesson_text>")

    if exercise is not None:
        parts.append(f"Exercise being attempted: {exercise.title} (type: {exercise.kind}).")
        parts.append("<exercise_text>\n" + _clean(_clip(exercise.instructions_md, MAX_EXERCISE_CHARS)) + "\n</exercise_text>")
        parts.append("The answer key is not available to you. Do not guess or invent one.")

    if code and code.strip():
        parts.append("<learner_code>\n" + _clean(code) + "\n</learner_code>")
    return "\n\n".join(parts), lesson.id if lesson else None, exercise.id if exercise else None


def chat(
    session: Session, settings: Settings, provider: AIProvider | None, user: User, request: ChatRequest
) -> ChatResponse:
    if request.mode == "independent":
        raise AppError(403, "ai_disabled_in_mode", "AI help is off in Independent mode. Choose another mode to use it.")
    if provider is None:
        raise AppError(503, "ai_not_configured", "The AI assistant is not configured on this server.")
    _check_limits(_usage(session, settings, user.id))

    conversation = None
    history: list[ChatMessage] = []
    if request.conversation_id is not None:
        conversation = ai_repository.get_conversation(session, user.id, request.conversation_id)
        if conversation is None:
            raise AppError(404, "conversation_not_found", "Conversation not found.")
        if conversation.assistant != request.assistant:
            raise AppError(409, "conversation_mismatch", "This conversation belongs to a different assistant.")
        history = [
            ChatMessage(m.role, m.content) for m in ai_repository.recent_messages(session, conversation.id, HISTORY_LIMIT)
        ]

    context, lesson_id, exercise_id = _build_context(session, user, request.lesson_id, request.exercise_id, request.code)
    mode = prompts.effective_mode(request.assistant, request.mode)
    messages = prompts.build_messages(request.assistant, mode, context, history, request.message)

    asked_at = utcnow()
    session.commit()  # release the database connection while waiting for the AI
    completion = _complete(provider, messages, settings)
    answered_at = max(utcnow(), asked_at + timedelta(microseconds=1))

    # Nothing is stored or counted unless the provider answered.
    if conversation is None:
        conversation = ai_repository.create_conversation(
            session, user.id, request.assistant, _title(request.message), lesson_id, exercise_id
        )
    ai_repository.add_message(session, conversation.id, "user", mode, request.message, asked_at)
    ai_repository.add_message(session, conversation.id, "assistant", mode, completion.text, answered_at)
    conversation.updated_at = answered_at
    ai_repository.record_usage(session, user.id, answered_at.date(), completion.tokens_in, completion.tokens_out)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        assistant=request.assistant,
        mode=mode,
        reply=completion.text,
        usage=_usage(session, settings, user.id),
    )


def study_plan(session: Session, settings: Settings, provider: AIProvider | None, user: User) -> StudyPlanResponse:
    weak = _weak_rows(session, user.id)
    usage = _usage(session, settings, user.id)
    if not weak:
        has_results = bool(exercise_repository.mastery(session, user.id))
        reply = (
            "None of your graded concepts are below 70% right now. Keep going with the next lesson."
            if has_results
            else "Submit a few exercises first. Once you have results, I can build a study plan from the concepts you found hard."
        )
        return StudyPlanResponse(reply=reply, weak_concepts=[], recommendations=[], usage=usage)
    if provider is None:
        raise AppError(503, "ai_not_configured", "The AI assistant is not configured on this server.")
    _check_limits(usage)

    stats = {slug: [correct, total] for slug, _name, correct, total in weak}
    by_slug = {c.slug: c for c in session.scalars(select(Concept).where(Concept.slug.in_(list(stats))))}
    recommendations = assessment_service._recommend(session, stats, by_slug)

    weak_lines = [f"- {name}: {correct}/{total} correct" for _slug, name, correct, total in weak]
    item_lines = []
    for index, item in enumerate(recommendations, start=1):
        if item.type == "lesson":
            item_lines.append(f"[{index}] Lesson on this platform: {item.title} (for {item.concept_name})")
        else:
            item_lines.append(f"[{index}] {item.resource_kind or 'resource'}: {item.title} (for {item.concept_name})")
    messages = prompts.build_study_plan_messages(user.profile.experience_level, weak_lines, item_lines)

    session.commit()
    completion = _complete(provider, messages, settings)
    ai_repository.record_usage(session, user.id, utcnow().date(), completion.tokens_in, completion.tokens_out)
    session.commit()

    return StudyPlanResponse(
        reply=strip_urls(completion.text),
        weak_concepts=[ConceptResult(slug=slug, name=name, correct=c, total=t) for slug, name, c, t in weak],
        recommendations=recommendations,
        usage=_usage(session, settings, user.id),
    )


def list_conversations(session: Session, user_id: uuid.UUID) -> list[ConversationSummary]:
    return [ConversationSummary.model_validate(c) for c in ai_repository.list_conversations(session, user_id)]


def get_conversation(session: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> ConversationDetail:
    conversation = ai_repository.get_conversation(session, user_id, conversation_id)
    if conversation is None:
        raise AppError(404, "conversation_not_found", "Conversation not found.")
    messages = [MessageRead.model_validate(m) for m in ai_repository.all_messages(session, conversation.id)]
    return ConversationDetail(
        id=conversation.id, assistant=conversation.assistant, title=conversation.title, messages=messages
    )


def delete_conversation(session: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
    conversation = ai_repository.get_conversation(session, user_id, conversation_id)
    if conversation is None:
        raise AppError(404, "conversation_not_found", "Conversation not found.")
    ai_repository.delete_conversation(session, conversation)
    session.commit()
