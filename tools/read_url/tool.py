"""Tool Operator: membaca halaman web (httpx polos + ekstraksi teks HTML)."""

import httpx
from langchain.tools import tool

from greth.config import settings
from helpers.html_text import extract
from tools.policy import ToolOutput, register
from tools.read_url.schema import ReadUrlArgs

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; greth/0.1)"}


async def _get(url: str) -> httpx.Response:
    """Ambil halaman; dipisah agar mudah di-monkeypatch saat tes."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=settings.request_timeout, headers=_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp


@register("operator")
@tool("read_url", args_schema=ReadUrlArgs)
async def read_url(url: str, displaying: bool = False) -> list[ToolOutput]:
    """Ambil isi teks sebuah halaman web dari url."""
    try:
        resp = await _get(url)
    except httpx.HTTPError as exc:
        return [ToolOutput.failure("read_url", exc, displaying)]
    title, text = extract(resp.text)
    return [ToolOutput(url=str(resp.url), title=title, body=text[: settings.page_limit], displaying=displaying)]
