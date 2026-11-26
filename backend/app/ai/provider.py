from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: str  # "system", "user" or "assistant"
    content: str


@dataclass(frozen=True)
class Completion:
    text: str
    tokens_in: int
    tokens_out: int


class ProviderError(Exception):
    """A provider failure. The message is safe to show to the learner (it never contains keys or raw responses)."""


class AIProvider(Protocol):
    """The only thing the rest of the application knows about an AI vendor."""

    name: str
    model: str

    def complete(self, messages: list[ChatMessage], max_output_tokens: int) -> Completion: ...
