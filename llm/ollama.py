"""Klien Ollama berbasis httpx async: chat dan daftar model (--base, --key saja)."""

from typing import Any

import httpx

from greth.config import LlmConfig, settings


class OllamaError(Exception):
    """Kegagalan komunikasi atau respons Ollama."""


def _explain(exc: httpx.HTTPStatusError) -> str:
    """Ringkas error HTTP; 401/403 diarahkan ke --key."""
    status = exc.response.status_code
    if status in (401, 403):
        return f"HTTP {status}: API key ditolak atau belum diberikan (--key)"
    return f"HTTP {status}: {exc.response.text[:200]}"


class OllamaClient:
    """Klien async; Authorization Bearer dikirim bila --key diberikan."""

    def __init__(self, cfg: LlmConfig, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._cfg = cfg
        self._http = httpx.AsyncClient(timeout=settings.request_timeout, transport=transport)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._cfg.api_key}"} if self._cfg.api_key else {}

    async def _request(self, method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Kirim request dan kembalikan JSON; semua error menjadi OllamaError."""
        try:
            resp = await self._http.request(method, url, json=payload, headers=self._headers())
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise OllamaError(_explain(exc)) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"{type(exc).__name__} saat menghubungi {url}") from exc

    async def chat(self, model: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None) -> dict[str, Any]:
        """POST /api/chat (non-stream); kembalikan objek message."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": settings.temperature, "num_ctx": settings.num_ctx},
        }
        if tools:
            payload["tools"] = tools
        data = await self._request("POST", f"{self._cfg.base_url}/api/chat", payload)
        message = data.get("message")
        if not isinstance(message, dict):
            raise OllamaError("respons /api/chat tidak memuat message")
        return message

    async def list_models(self) -> list[str]:
        """GET /api/tags; nama model yang tersedia di host."""
        data = await self._request("GET", f"{self._cfg.base_url}/api/tags")
        return [m["name"] for m in data.get("models", [])]

    async def aclose(self) -> None:
        """Tutup koneksi httpx."""
        await self._http.aclose()


_client: OllamaClient | None = None


def configure_client(cfg: LlmConfig) -> OllamaClient:
    """Buat klien tunggal proses dari konfigurasi CLI."""
    global _client
    _client = OllamaClient(cfg)
    return _client


def get_client() -> OllamaClient:
    """Ambil klien tunggal; configure_client harus dipanggil lebih dulu."""
    if _client is None:
        raise RuntimeError("configure_client() belum dipanggil")
    return _client
