"""LLM providers: real BharatCode model API + deterministic mock.

Real BharatCode path (shape verified 2026-11-05 from the public
Build League entrant Marg, github.com/Mqhnish/marg):
- Auth: `BHARATCODE_API_KEY` from the environment only, sent as a
  Bearer token. Never logged, never printed, never in an error string.
- Default model: `qwen-3.8-27b`. Fallback: `deepseek-v4.1-flash`
  (both live on https://www.bharatcode.ai/).
- OpenAI-compatible Chat Completions: POST `{base}/chat/completions`
  with `{"model", "messages", "max_tokens"}`; answer at
  `choices[0].message.content`.
- Marg's documented behaviour, replicated here: requests that come
  back `503` (model busy) or `429` are retried with backoff.

UNVERIFIED: the API base URL default (`https://api.bharatcode.ai/v1`)
is the conventional OpenAI-compatible guess — confirm it in your
BharatCode account and override with BHARATCODE_API_BASE if needed.
The client is stdlib-only (urllib), no extra dependency.

Mock path: deterministic, offline, no network. Used when no key is
configured, so the demo and tests always run. Mock output is always
prefixed "[mock]" so it can never be mistaken for a real answer.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Protocol

from .config import Config

# Retryable statuses, per Marg's documented BharatCode behaviour.
RETRYABLE = {429, 503}
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = (1.0, 2.0, 4.0)
REQUEST_TIMEOUT_SECONDS = 60
MAX_TOKENS = 1024


class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class MockProvider:
    """Deterministic extractive stand-in. Tracks calls for tests."""

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        # Answer from the note data, not from the question preamble: take
        # the text after the <notes-data>/<note-data> marker, if present.
        body = user
        for marker in ("<notes-data>", "<note-data"):
            if marker in user:
                body = user.split(marker, 1)[1]
                body = re.sub(r"^[^>]*>", "", body, count=1) if marker == "<note-data" else body
                break
        body = re.sub(r"^---.*$", "", body, flags=re.M).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
        content = next((s for s in sentences if len(s) > 20), sentences[0] if sentences else "")
        return f"[mock] {content}"


def _extract_chat_content(payload: Any) -> str:
    """Pull the assistant text out of a Chat Completions payload."""
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("BharatCode returned an empty or unrecognised response") from exc
    if not content or not str(content).strip():
        raise RuntimeError("BharatCode returned an empty response")
    return str(content)


def _default_request(url: str, headers: dict, body: bytes) -> tuple[int, dict]:
    """One real HTTP POST. Returns (status, parsed JSON). Raises on
    transport failure; HTTP errors are returned as (status, payload)
    so the caller can decide on retries. Never logs the key."""
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload: dict = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            payload = {"error": raw[:200]}
        return exc.code, payload


class BharatCodeProvider:
    """Thin stdlib client for the BharatCode model API (Chat Completions).

    Pass `request_fn=` in tests to inject a fake transport; production
    code passes nothing and the real urllib transport is used. The key
    is read from the environment by config, never from a file.
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        request_fn: Callable[[str, dict, bytes], tuple[int, dict]] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if not api_key:
            raise RuntimeError(
                "No BharatCode API key: set BHARATCODE_API_KEY "
                "(from your BharatCode account) or run with --provider mock."
            )
        if not model or not model.strip():
            raise RuntimeError("BharatCode model id is empty; set BHARATCODE_MODEL, e.g. qwen-3.8-27b")
        self.model = model.strip()
        self.api_key = api_key
        self.api_base = (api_base or "").rstrip("/") or "https://api.bharatcode.ai/v1"
        self._request = request_fn or _default_request
        self._sleep = sleep_fn or time.sleep

    def complete(self, system: str, user: str) -> str:
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        body = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": MAX_TOKENS,
            }
        ).encode("utf-8")
        last_status = 0
        last_payload: dict = {}
        for attempt in range(MAX_ATTEMPTS):
            try:
                status, payload = self._request(url, headers, body)
            except Exception as exc:  # transport failure: do not retry blindly
                raise RuntimeError(f"BharatCode request failed (network): {exc}") from exc
            last_status, last_payload = status, payload
            if status == 200:
                return _extract_chat_content(payload)
            if status in RETRYABLE and attempt < MAX_ATTEMPTS - 1:
                self._sleep(BACKOFF_SECONDS[attempt])
                continue
            detail = ""
            if isinstance(payload, dict):
                err = payload.get("error")
                if isinstance(err, dict):
                    detail = str(err.get("message", ""))[:200]
                elif isinstance(err, str):
                    detail = err[:200]
            raise RuntimeError(
                f"BharatCode API error: HTTP {status}" + (f" — {detail}" if detail else "")
            )
        raise RuntimeError(f"BharatCode API error: HTTP {last_status} after {MAX_ATTEMPTS} attempts")


def build_provider(
    config: Config,
    request_fn: Callable[[str, dict, bytes], tuple[int, dict]] | None = None,
) -> LLMProvider:
    """Resolve provider from config. 'auto' -> bharatcode if a key exists,
    otherwise mock. Explicit 'bharatcode' with no key raises."""
    effective = config.resolve_provider()
    if effective == "mock":
        return MockProvider()
    if effective == "bharatcode":
        return BharatCodeProvider(
            model=config.model,
            api_key=config.api_key,
            api_base=config.api_base,
            request_fn=request_fn,
        )
    raise ValueError(f"Unknown provider: {config.provider!r}")
