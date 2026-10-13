"""Klien Ollama berbasis httpx async: chat, web search/fetch, dan daftar model."""

from functools import cache
from typing import Any

import httpx

from greth.config import CLOUD_URL, Settings, settings


class OllamaError(Exception):
    """Kegagalan komunikasi atau respons Ollama."""


def _explain(exc: httpx.HTTPStatusError) -> str:
    """Ringkas error HTTP; 401/403 diarahkan ke OLLAMA_API_KEY."""
    status = exc.response.status_code
    if status in (401, 403):
        return f"HTTP {status}: API key ditolak atau belum diatur (OLLAMA_API_KEY)"
    return f"HTTP {status}: {exc.response.text[:200]}"


class OllamaClient:
    """Klien async; Authorization Bearer dikirim bila OLLAMA_API_KEY diatur."""

    def __init__(self, cfg: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._cfg = cfg
        self._http = httpx.AsyncClient(timeout=cfg.request_timeout, transport=transport)

    def _headers(self) -> dict[str, str]:
        key = self._cfg.ollama_api_key
        return {"Authorization": f"Bearer {key}"} if key else {}

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

    def _require_key(self, feature: str) -> None:
        """Web search/fetch hanya tersedia di cloud dan wajib memakai API key."""
        if not self._cfg.ollama_api_key:
            raise OllamaError(f"{feature} membutuhkan OLLAMA_API_KEY")

    async def chat(self, model: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None) -> dict[str, Any]:
        """POST /api/chat (non-stream); kembalikan objek message."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self._cfg.temperature, "num_ctx": self._cfg.num_ctx},
        }
        if tools:
            payload["tools"] = tools
        data = await self._request("POST", f"{self._cfg.ollama_host}/api/chat", payload)
        message = data.get("message")
        if not isinstance(message, dict):
            raise OllamaError("respons /api/chat tidak memuat message")
        return message

    async def web_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """POST ollama.com/api/web_search; hasil: title, url, content."""
        self._require_key("web_search")
        payload = {"query": query, "max_results": min(max_results, 10)}
        data = await self._request("POST", f"{CLOUD_URL}/api/web_search", payload)
        return list(data.get("results", []))

    async def web_fetch(self, url: str) -> dict[str, Any]:
        """POST ollama.com/api/web_fetch; hasil: title, content, links."""
        self._require_key("web_fetch")
        return await self._request("POST", f"{CLOUD_URL}/api/web_fetch", {"url": url})

    async def list_models(self) -> list[str]:
        """GET /api/tags; nama model yang tersedia di host."""
        data = await self._request("GET", f"{self._cfg.ollama_host}/api/tags")
        return [m["name"] for m in data.get("models", [])]

    async def aclose(self) -> None:
        """Tutup koneksi httpx."""
        await self._http.aclose()


@cache
def get_client() -> OllamaClient:
    """Satu klien untuk seluruh proses."""
    return OllamaClient(settings)
