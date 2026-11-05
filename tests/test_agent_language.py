"""Tests: answer language (en / hi / hinglish) + refusal wording. No network."""
import pytest

from notes_bharat.agent import NotesAgent
from notes_bharat.config import Config
from notes_bharat.llm import MockProvider


class RecordingProvider:
    """Captures the system prompt so tests can check the language instruction."""

    def __init__(self):
        self.systems = []
        self.calls = 0

    def complete(self, system, user):
        self.systems.append(system)
        self.calls += 1
        return "Recorded answer."


def _config(tmp_path, **overrides):
    kwargs = dict(notes_root=tmp_path, provider="mock")
    kwargs.update(overrides)
    return Config(**kwargs)


def _seed(tmp_path):
    (tmp_path / "a.md").write_text("# Abhiverse idea\nPhone remote for laptop. #project", encoding="utf-8")


def test_language_instruction_reaches_system_prompt(tmp_path):
    _seed(tmp_path)
    provider = RecordingProvider()
    agent = NotesAgent(_config(tmp_path), provider=provider)
    result = agent.ask_detailed("Abhiverse kya hai?", language="hinglish")
    assert "Hinglish" in provider.systems[0]
    assert "Roman" in provider.systems[0]
    assert result.language == "hinglish"


def test_hindi_instruction_reaches_system_prompt(tmp_path):
    _seed(tmp_path)
    provider = RecordingProvider()
    agent = NotesAgent(_config(tmp_path), provider=provider)
    agent.ask_detailed("Abhiverse kya hai?", language="hi")
    assert "Devanagari" in provider.systems[0]


def test_english_is_default_and_has_no_language_override(tmp_path):
    _seed(tmp_path)
    provider = RecordingProvider()
    agent = NotesAgent(_config(tmp_path), provider=provider)
    result = agent.ask_detailed("What is Abhiverse?")
    assert "Answer in English." in provider.systems[0]
    assert result.language == "en"


def test_invalid_language_rejected_before_llm_call(tmp_path):
    _seed(tmp_path)
    provider = RecordingProvider()
    agent = NotesAgent(_config(tmp_path), provider=provider)
    with pytest.raises(ValueError, match="Unknown language"):
        agent.ask_detailed("Abhiverse", language="fr")
    assert provider.calls == 0
    assert agent.budget.used == 0


def test_refusal_wording_follows_language(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    assert agent.ask_detailed("quantum bananas", language="en").answer.startswith(
        "I couldn't find that in your notes"
    )
    assert agent.ask_detailed("quantum bananas", language="hinglish").answer.startswith(
        "Ye aapke notes mein nahi mila"
    )
    hi = agent.ask_detailed("quantum bananas", language="hi").answer
    assert "notes" in hi and "andaza" in hi
