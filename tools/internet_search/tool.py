"""Tool Operator: pencarian web lewat Ollama web search API."""

from langchain.tools import tool

from greth.config import settings
from llm.ollama import OllamaError, get_client
from tools.internet_search.schema import InternetSearchArgs
from tools.policy import ToolOutput, register


@register("operator")
@tool("internet_search", args_schema=InternetSearchArgs)
async def internet_search(search: str, displaying: bool = False) -> list[ToolOutput]:
    """Cari informasi di internet; hasil berupa daftar url, title, body."""
    try:
        rows = await get_client().web_search(search, settings.search_results)
    except OllamaError as exc:
        return [ToolOutput.failure("internet_search", exc, displaying)]
    if not rows:
        return [ToolOutput(title="no results", body=f"Tidak ada hasil: {search}", displaying=displaying)]
    return [
        ToolOutput(
            url=row.get("url", ""),
            title=row.get("title", ""),
            body=row.get("content", "")[: settings.body_limit],
            displaying=displaying,
        )
        for row in rows
    ]
