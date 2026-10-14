"""Tes argumen CLI: konfigurasi LLM hanya dari --base, --key, --model."""

import pytest

from greth.cli import parse_args
from greth.config import DEFAULT_BASE_URL, DEFAULT_MODEL


def test_defaults() -> None:
    cfg = parse_args([])
    assert cfg.base_url == DEFAULT_BASE_URL == "http://localhost:11434"
    assert cfg.api_key is None
    assert cfg.model == DEFAULT_MODEL
    assert not cfg.is_cloud


def test_flags_and_cloud_detection() -> None:
    cfg = parse_args(["--base", "https://ollama.com", "--key", " secret ", "--model", "gpt-oss:120b"])
    assert (cfg.base_url, cfg.api_key, cfg.model) == ("https://ollama.com", "secret", "gpt-oss:120b")
    assert cfg.is_cloud
    assert "secret" not in repr(cfg)


def test_base_is_normalized() -> None:
    assert parse_args(["--base", "127.0.0.1:11434/"]).base_url == "http://127.0.0.1:11434"


def test_blank_key_means_no_key() -> None:
    assert parse_args(["--key", "  "]).api_key is None


def test_environment_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_API_KEY", "from-env")
    monkeypatch.setenv("OLLAMA_HOST", "http://elsewhere:1")
    monkeypatch.setenv("GRETH_MODEL", "from-env")
    cfg = parse_args([])
    assert (cfg.base_url, cfg.api_key, cfg.model) == (DEFAULT_BASE_URL, None, DEFAULT_MODEL)


def test_unknown_flag_exits() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--bogus"])
