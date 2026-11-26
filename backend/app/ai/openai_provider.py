import logging

import httpx

from app.ai.provider import ChatMessage, Completion, ProviderError

logger = logging.getLogger("app.ai")


def _message_for_status(status: int) -> str:
    if status in (401, 403):
        return "The AI service rejected the API key. Ask the administrator to check it."
    if status == 429:
        return "The AI service is busy or its quota is used up. Try again later."
    if status in (400, 404):
        return "The AI service rejected the request. The configured model may not be available."
    return f"The AI service had a problem (HTTP {status}). Try again."


class OpenAIProvider:
    """Chat Completions over plain HTTP. No SDK, so there is no SDK version to drift out of date."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.model = model
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def complete(self, messages: list[ChatMessage], max_output_tokens: int) -> Completion:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_completion_tokens": max_output_tokens,
        }
        try:
            response = self._client.post(self._url, json=payload)
        except httpx.TimeoutException:
            raise ProviderError("The AI service took too long to answer. Try again.") from None
        except httpx.HTTPError:
            raise ProviderError("Cannot reach the AI service.") from None

        if response.status_code >= 400:
            detail = ""
            try:
                detail = str(response.json().get("error", {}).get("message", ""))[:200]
            except (ValueError, AttributeError):
                pass
            logger.warning("ai_provider_http_error", extra={"status": response.status_code, "path": detail})
            raise ProviderError(_message_for_status(response.status_code))

        try:
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage") or {}
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            raise ProviderError("The AI service returned an unexpected response.") from None
        if not isinstance(text, str) or not text.strip():
            raise ProviderError("The AI service returned an empty answer.")
        return Completion(
            text=text.strip(),
            tokens_in=int(usage.get("prompt_tokens", 0) or 0),
            tokens_out=int(usage.get("completion_tokens", 0) or 0),
        )
