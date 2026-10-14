"""Tool Operator: pencarian web lewat DuckDuckGo (ddgs)."""

import asyncio

from ddgs import DDGS
from langchain.tools import tool

from greth.config import settings
from tools.internet_search.schema import InternetSearchArgs
from tools.policy import ToolOutput, register


def _ddgs_text(query: str, limit: int) -> list[dict[str, str]]:
    """Pencarian DuckDuckGo (sinkron; dijalankan di thread)."""
    return list(DDGS().text(query, max_results=limit))


@register("operator")
@tool("internet_search", args_schema=InternetSearchArgs)
async def internet_search(search: str, displaying: bool = False) -> list[ToolOutput]:
    """Cari informasi di internet; hasil berupa daftar url, title, body."""
    try:
        rows = await asyncio.to_thread(_ddgs_text, search, settings.search_results)
    except Exception as exc:  # noqa: BLE001 - kegagalan pencarian dilaporkan sebagai hasil
        return [ToolOutput.failure("internet_search", exc, displaying)]
    if not rows:
        return [ToolOutput(title="no results", body=f"Tidak ada hasil: {search}", displaying=displaying)]
    return [
        ToolOutput(
            url=row.get("href", ""),
            title=row.get("title", ""),
            body=row.get("body", "")[: settings.body_limit],
            displaying=displaying,
        )
        for row in rows
    ]
