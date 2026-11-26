import json

import httpx
import pytest

from app.ai.openai_provider import OpenAIProvider
from app.ai.provider import ChatMessage, ProviderError


def _provider(handler) -> OpenAIProvider:
    return OpenAIProvider(
        api_key="sk-test-key",
        model="model-1",
        base_url="https://api.example.test/v1/",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )


def test_success_parses_text_and_usage_and_sends_expected_request():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "  Hello  "}}], "usage": {"prompt_tokens": 11, "completion_tokens": 7}}
        )

    result = _provider(handler).complete([ChatMessage("system", "s"), ChatMessage("user", "u")], 123)
    assert (result.text, result.tokens_in, result.tokens_out) == ("Hello", 11, 7)
    assert seen["url"] == "https://api.example.test/v1/chat/completions"
    assert seen["auth"] == "Bearer sk-test-key"
    assert seen["body"]["model"] == "model-1" and seen["body"]["max_completion_tokens"] == 123
    assert [m["role"] for m in seen["body"]["messages"]] == ["system", "user"]


@pytest.mark.parametrize(
    ("status", "expected"), [(401, "API key"), (403, "API key"), (429, "quota"), (400, "model"), (500, "problem")]
)
def test_http_errors_become_safe_messages(status, expected):
    provider = _provider(lambda request: httpx.Response(status, json={"error": {"message": "sk-test-key leaked?"}}))
    with pytest.raises(ProviderError) as caught:
        provider.complete([ChatMessage("user", "u")], 10)
    assert expected in str(caught.value)
    assert "sk-test-key" not in str(caught.value)


def test_non_json_error_body_is_handled():
    provider = _provider(lambda request: httpx.Response(502, text="<html>bad gateway</html>"))
    with pytest.raises(ProviderError, match="HTTP 502"):
        provider.complete([ChatMessage("user", "u")], 10)


@pytest.mark.parametrize("body", [{"nope": 1}, {"choices": []}, {"choices": [{"message": {"content": "   "}}]}])
def test_bad_or_empty_responses_are_rejected(body):
    provider = _provider(lambda request: httpx.Response(200, json=body))
    with pytest.raises(ProviderError):
        provider.complete([ChatMessage("user", "u")], 10)


def test_timeout_and_connection_failures():
    def slow(request):
        raise httpx.ReadTimeout("t")

    def down(request):
        raise httpx.ConnectError("c")

    with pytest.raises(ProviderError, match="too long"):
        _provider(slow).complete([ChatMessage("user", "u")], 10)
    with pytest.raises(ProviderError, match="Cannot reach"):
        _provider(down).complete([ChatMessage("user", "u")], 10)
