"""Configuration for the NoteVault Bharat agent.

No secrets are ever read from a file committed to the repo. The
BharatCode API key comes only from the environment, and is never
printed or logged.

API facts (verified 2026-11-05):
- BharatCode model API; key env var `BHARATCODE_API_KEY` and default
  model `qwen-3.8-27b` follow the public Build League entrant Marg
  (github.com/Mqhnish/marg), which uses the Responses API by default
  and Chat Completions with `--api chat`. This app uses Chat
  Completions (OpenAI-compatible shape, stateless, `store` not needed).
- Model IDs `qwen-3.8-27b` and `deepseek-v4.1-flash` are the two live
  models listed on https://www.bharatcode.ai/ (checked 2026-11-05).
- Student access: "Qwen free up to 10M tokens a day" per bharatcode.ai.

VERIFIED 2026-11-06 — API base URL: `https://bharatcode.ai/api/model/v1`,
taken from the public Build League entrant Marg's `marg/llm.py`
(`DEFAULT_BASE_URL`, read via the GitHub connector 6 Nov 2026). Marg
posts both its Responses API and Chat Completions calls under this base,
so this app's `{base}/chat/completions` is consistent with it. Still
overridable with `BHARATCODE_API_BASE` if your account shows otherwise.
The app works in mock mode without any key, so nothing here blocks a demo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

# Verified default — see module docstring. Override with
# BHARATCODE_API_BASE if your BharatCode account shows a different one.
DEFAULT_API_BASE = "https://bharatcode.ai/api/model/v1"
DEFAULT_MODEL = "qwen-3.8-27b"
DEFAULT_FALLBACK_MODEL = "deepseek-v4.1-flash"

LANGUAGES = {
    "en": "English",
    "hi": "Hindi (Devanagari)",
    "hinglish": "Hinglish (Hindi in Roman script)",
}


@dataclass
class Config:
    notes_root: Path
    provider: str = "auto"  # "auto" | "mock" | "bharatcode"
    model: str = DEFAULT_MODEL
    max_chars_per_note: int = 4000
    max_notes_per_answer: int = 3
    max_llm_calls_per_run: int = 5
    fallback_model: str | None = DEFAULT_FALLBACK_MODEL
    api_key: str | None = None
    api_base: str = DEFAULT_API_BASE
    language: str = "en"

    @property
    def gateway_label(self) -> str:
        """API origin for display only — never a key."""
        parsed = urlparse(self.api_base)
        return f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else self.api_base

    def resolve_provider(self) -> str:
        """Return the effective provider name, without side effects."""
        if self.provider == "auto":
            return "bharatcode" if self.api_key else "mock"
        return self.provider


def config_from_env(notes_root: Path | None = None) -> Config:
    """Build a Config from the environment. Never prints key values."""
    return Config(
        notes_root=Path(notes_root or os.environ.get("NOTES_ROOT", "notes")),
        provider=os.environ.get("BHARATCODE_PROVIDER", "auto"),
        model=os.environ.get("BHARATCODE_MODEL", DEFAULT_MODEL),
        fallback_model=os.environ.get("BHARATCODE_FALLBACK_MODEL") or DEFAULT_FALLBACK_MODEL,
        api_key=os.environ.get("BHARATCODE_API_KEY") or None,
        api_base=os.environ.get("BHARATCODE_API_BASE", DEFAULT_API_BASE),
        language=os.environ.get("BHARATCODE_LANGUAGE", "en"),
    )
