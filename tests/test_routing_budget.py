"""Tests: BharatCode routing display, budget meter, fallback, web payloads. No network."""
import json
import threading
import urllib.request

import pytest

from notes_bharat.agent import NotesAgent
from notes_bharat.config import Config
from notes_bharat.llm import MockProvider
from notes_bharat.routing import BudgetTracker, choose_route, parse_model
from notes_bharat.web import make_server


class FailingProvider:
    def complete(self, system, user):
        raise RuntimeError("primary provider down")


def _config(tmp_path, **overrides):
    kwargs = dict(notes_root=tmp_path, provider="mock")
    kwargs.update(overrides)
    return Config(**kwargs)


def _seed(tmp_path):
    (tmp_path / "a.md").write_text("# Abhiverse idea\nPhone remote for laptop. #project", encoding="utf-8")


def test_parse_model_valid_and_invalid():
    assert parse_model("qwen-3.8-27b") == ("bharatcode", "qwen-3.8-27b")
    assert parse_model("deepseek-v4.1-flash") == ("bharatcode", "deepseek-v4.1-flash")
    for bad in ("", "   ", "bad model", "two  spaces"):
        with pytest.raises(ValueError, match="Model id"):
            parse_model(bad)


def test_choose_route_default_and_user_selected_reasons():
    default = choose_route("qwen-3.8-27b", gateway="https://api.bharatcode.ai", mode="mock")
    assert default.chosen.provider == "bharatcode"
    assert "Default model" in default.chosen.reason
    assert default.fallback_chain == []
    chosen = choose_route(
        "qwen-3.8-27b", fallback_model="deepseek-v4.1-flash",
        user_selected=True, mode="mock",
    )
    assert "User-selected" in chosen.chosen.reason
    assert chosen.fallback_chain[0].model == "deepseek-v4.1-flash"
    d = chosen.to_dict()
    assert d["gateway"] == "https://api.bharatcode.ai"
    assert "[mock]" in d["mode_label"]


def test_budget_tracker_remaining_and_exhaustion():
    b = BudgetTracker(limit=2)
    assert b.remaining == 2 and not b.exhausted
    b.charge()
    assert (b.used, b.remaining, b.percent_used) == (1, 1, 50)
    b.charge()
    assert b.exhausted
    with pytest.raises(RuntimeError, match="budget"):
        b.charge()


def test_ask_detailed_shows_routing_budget_citations_and_mock_label(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    result = agent.ask_detailed("What is Abhiverse?")
    assert result.mode == "mock"
    assert result.sources == [{"title": "Abhiverse idea", "rel_path": "a.md"}]
    assert result.routing["gateway"] == "https://api.bharatcode.ai"
    assert result.routing["chosen"]["model"] == "qwen-3.8-27b"
    assert result.routing["attempted"] == ["qwen-3.8-27b"]
    assert result.routing["fallback_used"] is False
    assert result.budget["used"] == 1 and result.budget["remaining"] == 4
    assert "[mock]" in result.answer  # mock answers are always labelled


def test_ask_detailed_refusal_spends_no_budget_and_attempts_no_route(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    result = agent.ask_detailed("quantum bananas")
    assert result.refused is True
    assert result.routing["refused_before_routing"] is True
    assert result.routing["attempted"] == []
    assert result.budget["used"] == 0


def test_fallback_used_when_primary_fails(tmp_path):
    _seed(tmp_path)
    config = _config(tmp_path, fallback_model="deepseek-v4.1-flash")
    agent = NotesAgent(config, provider=FailingProvider(), fallback_provider=MockProvider())
    result = agent.ask_detailed("Abhiverse")
    assert result.routing["fallback_used"] is True
    assert result.routing["attempted"] == ["qwen-3.8-27b", "deepseek-v4.1-flash"]
    assert result.budget["used"] == 2  # one charge per provider attempt
    assert "[mock]" in result.answer


def test_both_providers_failing_raises_no_fabricated_answer(tmp_path):
    _seed(tmp_path)
    config = _config(tmp_path, fallback_model="deepseek-v4.1-flash")
    agent = NotesAgent(config, provider=FailingProvider(), fallback_provider=FailingProvider())
    with pytest.raises(RuntimeError, match="primary provider down"):
        agent.ask_detailed("Abhiverse")


def test_user_selected_model_is_recorded_in_routing(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    result = agent.ask_detailed("Abhiverse", model="deepseek-v4.1-flash")
    assert result.routing["chosen"]["model"] == "deepseek-v4.1-flash"
    assert "User-selected" in result.routing["chosen"]["reason"]


def test_bad_user_model_rejected_before_llm_call(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    with pytest.raises(ValueError, match="Model id"):
        agent.ask_detailed("Abhiverse", model="not a model")
    assert agent.budget.used == 0


def test_status_dict_never_contains_token(tmp_path):
    _seed(tmp_path)
    config = _config(tmp_path, api_key="secret-should-not-appear")
    agent = NotesAgent(config, provider=MockProvider())
    assert "secret-should-not-appear" not in json.dumps(agent.status_dict())


def test_web_status_and_ask_endpoints(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path), provider=MockProvider())
    server = make_server(agent, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        with urllib.request.urlopen(base + "/api/status") as resp:
            status = json.loads(resp.read())
        assert status["mode"] == "mock" and status["notes_count"] == 1
        req = urllib.request.Request(
            base + "/api/ask",
            data=json.dumps({"question": "What is Abhiverse?"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read())
        assert payload["routing"]["chosen"]["provider"] == "bharatcode"
        assert payload["budget"]["used"] == 1
        assert payload["sources"][0]["title"] == "Abhiverse idea"
    finally:
        server.shutdown()
        server.server_close()
