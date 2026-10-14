"""Konfigurasi: LlmConfig dari CLI (base, key, model) dan konstanta tuning tetap."""

from dataclasses import dataclass, field

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "nemotron-3-super:cloud"
CLOUD_URL = "https://ollama.com"


def normalize_base_url(raw: str) -> str:
    """Pastikan base url memiliki skema http(s) dan tanpa slash akhir."""
    url = raw.strip()
    url = url if url.startswith(("http://", "https://")) else f"http://{url}"
    return url.rstrip("/")


@dataclass(frozen=True, slots=True)
class LlmConfig:
    """Konfigurasi LLM: satu model dipakai semua agen."""

    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = field(default=None, repr=False)

    @property
    def is_cloud(self) -> bool:
        """True jika base url adalah Ollama Cloud."""
        return self.base_url == CLOUD_URL


@dataclass(frozen=True, slots=True)
class Settings:
    """Konstanta tuning tetap (bukan konfigurasi LLM)."""

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


settings = Settings()
