"""Tool Operator: membaca halaman web lewat Ollama web fetch API."""

from langchain.tools import tool

from greth.config import settings
from llm.ollama import OllamaError, get_client
from tools.policy import ToolOutput, register
from tools.read_url.schema import ReadUrlArgs


@register("operator")
@tool("read_url", args_schema=ReadUrlArgs)
async def read_url(url: str, displaying: bool = False) -> list[ToolOutput]:
    """Ambil isi teks sebuah halaman web dari url."""
    try:
        page = await get_client().web_fetch(url)
    except OllamaError as exc:
        return [ToolOutput.failure("read_url", exc, displaying)]
    return [
        ToolOutput(
            url=url,
            title=page.get("title", ""),
            body=page.get("content", "")[: settings.page_limit],
            displaying=displaying,
        )
    ]
