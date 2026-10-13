"""Tes konfigurasi host, API key, dan model."""

import pytest

from greth.config import CLOUD_MODEL, CLOUD_URL, LOCAL_MODEL, LOCAL_URL, Settings

VARS = ("OLLAMA_API_KEY", "OLLAMA_HOST", "GRETH_MODEL", "GRETH_LEADER_MODEL", "GRETH_OPERATOR_MODEL", "GRETH_EVALUATOR_MODEL")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in VARS:
        monkeypatch.delenv(name, raising=False)


def test_local_defaults() -> None:
    cfg = Settings.from_env()
    assert cfg.ollama_host == LOCAL_URL and not cfg.is_cloud and cfg.ollama_api_key is None
    assert set(cfg.models.values()) == {LOCAL_MODEL}


def test_api_key_switches_to_cloud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", " secret ")
    cfg = Settings.from_env()
    assert cfg.ollama_host == CLOUD_URL and cfg.is_cloud and cfg.ollama_api_key == "secret"
    assert set(cfg.models.values()) == {CLOUD_MODEL}
    assert "secret" not in repr(cfg)


def test_explicit_host_wins_and_is_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "k")
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1:11434/")
    assert Settings.from_env().ollama_host == "http://127.0.0.1:11434"


def test_per_agent_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GRETH_MODEL", "base")
    monkeypatch.setenv("GRETH_EVALUATOR_MODEL", "judge")
    assert dict(Settings.from_env().models) == {"leader": "base", "operator": "base", "evaluator": "judge"}
