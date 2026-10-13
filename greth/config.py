"""Konfigurasi tunggal (source of truth) dengan override lewat environment."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from greth.types import AGENTS, AgentName

LOCAL_URL = "http://localhost:11434"
CLOUD_URL = "https://ollama.com"
LOCAL_MODEL = "qwen3:4b"
CLOUD_MODEL = "nemotron-3-super:cloud"


def _host(raw: str) -> str:
    """Normalkan host agar memiliki skema http(s) dan tanpa slash akhir."""
    url = raw if raw.startswith(("http://", "https://")) else f"http://{raw}"
    return url.rstrip("/")


def is_cloud(host: str) -> bool:
    """True jika host adalah Ollama Cloud."""
    return host == CLOUD_URL


@dataclass(frozen=True, slots=True)
class Settings:
    """Seluruh parameter runtime."""

    ollama_host: str
    models: Mapping[AgentName, str]
    ollama_api_key: str | None = field(default=None, repr=False)
    temperature: float = 0.0
    num_ctx: int = 8192
    request_timeout: float = 120.0
    history_limit: int = 20
    max_attempts: int = 3
    tool_retries: int = 2
    recursion_limit: int = 300
    search_results: int = 5
    body_limit: int = 1500
    page_limit: int = 4000
    result_limit: int = 8000

    @property
    def is_cloud(self) -> bool:
        """True jika chat diarahkan ke Ollama Cloud."""
        return is_cloud(self.ollama_host)

    @classmethod
    def from_env(cls) -> "Settings":
        """Bangun Settings dari environment."""
        key = (os.getenv("OLLAMA_API_KEY") or "").strip() or None
        host = _host(os.getenv("OLLAMA_HOST") or (CLOUD_URL if key else LOCAL_URL))
        base = os.getenv("GRETH_MODEL") or (CLOUD_MODEL if is_cloud(host) else LOCAL_MODEL)
        return cls(
            ollama_host=host,
            ollama_api_key=key,
            models={a: os.getenv(f"GRETH_{a.upper()}_MODEL") or base for a in AGENTS},
        )


settings = Settings.from_env()
