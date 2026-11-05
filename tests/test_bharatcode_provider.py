"""Tests: BharatCode provider transport (fake HTTP, no network, no key).

Pins the verified API shape from the public Build League entrant
Marg (github.com/Mqhnish/marg): BHARATCODE_API_KEY Bearer auth,
default model qwen-3.8-27b, OpenAI-compatible Chat Completions, and
retries on 429/503 with backoff.
"""
import json

import pytest

from notes_bharat.config import Config
from notes_bharat.llm import BharatCodeProvider, MockProvider, build_provider


def _ok_payload(text="Real BharatCode answer."):
    return {"choices": [{"message": {"content": text}}]}


class FakeTransport:
    """Queue of (status, payload) replies; records every request."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, url, headers, body):
        self.calls.append((url, headers, json.loads(body.decode("utf-8"))))
        return self.replies.pop(0)


def _provider(replies, **overrides):
    kwargs = dict(model="qwen-3.8-27b", api_key="test-key-123", api_base="https://api.example.test/v1")
    kwargs.update(overrides)
    transport = FakeTransport(replies)
    provider = BharatCodeProvider(request_fn=transport, sleep_fn=lambda s: None, **kwargs)
    return provider, transport


def test_chat_completions_request_shape():
    provider, transport = _provider([(200, _ok_payload())])
    assert provider.complete("sys", "hello") == "Real BharatCode answer."
    url, headers, body = transport.calls[0]
    assert url == "https://api.example.test/v1/chat/completions"
    assert headers["Authorization"] == "Bearer test-key-123"
    assert headers["Content-Type"] == "application/json"
    assert body["model"] == "qwen-3.8-27b"
    assert body["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hello"},
    ]


def test_retry_on_429_then_success():
    provider, transport = _provider([(429, {"error": "busy"}), (200, _ok_payload("after retry"))])
    assert provider.complete("sys", "hello") == "after retry"
    assert len(transport.calls) == 2


def test_retry_on_503_then_success():
    provider, transport = _provider([(503, {"error": "model busy"}), (200, _ok_payload("after 503"))])
    assert provider.complete("sys", "hello") == "after 503"
    assert len(transport.calls) == 2


def test_429_exhausted_raises_without_fabrication():
    provider, transport = _provider([(429, {"error": "busy"})] * 4)
    with pytest.raises(RuntimeError, match="HTTP 429"):
        provider.complete("sys", "hello")
    assert len(transport.calls) == 4  # MAX_ATTEMPTS


def test_400_error_raises_with_status():
    provider, _ = _provider([(400, {"error": {"message": "bad model"}})])
    with pytest.raises(RuntimeError, match="HTTP 400.*bad model"):
        provider.complete("sys", "hello")


def test_empty_response_raises():
    provider, _ = _provider([(200, {"choices": []})])
    with pytest.raises(RuntimeError, match="unrecognised"):
        provider.complete("sys", "hello")


def test_missing_key_raises_before_any_request():
    with pytest.raises(RuntimeError, match="BHARATCODE_API_KEY"):
        BharatCodeProvider(model="qwen-3.8-27b", api_key=None)


def test_build_provider_auto_uses_mock_without_key():
    config = Config(notes_root="notes", provider="auto", api_key=None)
    assert isinstance(build_provider(config), MockProvider)


def test_build_provider_auto_uses_bharatcode_with_key():
    config = Config(notes_root="notes", provider="auto", api_key="k")
    provider = build_provider(config, request_fn=lambda u, h, b: (200, _ok_payload()))
    assert isinstance(provider, BharatCodeProvider)
    assert provider.complete("s", "u") == "Real BharatCode answer."


def test_build_provider_explicit_bharatcode_without_key_raises():
    config = Config(notes_root="notes", provider="bharatcode", api_key=None)
    with pytest.raises(RuntimeError, match="BHARATCODE_API_KEY"):
        build_provider(config)


def test_mock_answers_are_always_labelled():
    assert MockProvider().complete("sys", "hello world this is a long note body here.").startswith("[mock]")
