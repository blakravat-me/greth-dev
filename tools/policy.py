"""Policy tool: registry, hak akses per agen, dispatch, dan skema keluaran bersama."""

from collections.abc import Callable, Sequence
from typing import Any

from langchain.messages import ToolCall
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError

from greth.types import AGENTS, AgentName
from helpers.clock import now_iso

# ---------- schema ----------


class ToolOutput(BaseModel):
    """Keluaran seragam tool Operator."""

    url: str = ""
    title: str = ""
    body: str = ""
    displaying: bool = False
    date: str = Field(default_factory=now_iso)

    @classmethod
    def failure(cls, name: str, exc: Exception, displaying: bool) -> "ToolOutput":
        """Ubah error tool menjadi hasil biasa agar Evaluator bisa menilainya."""
        return cls(title=f"{name} error", body=f"{type(exc).__name__}: {exc}", displaying=displaying)


class ToolCallError(Exception):
    """Tool call tidak valid (kosong, tool asing, tidak diizinkan, atau argumen salah)."""


OnResult = Callable[[str, Any], None]

# ---------- registry ----------

_REGISTRY: dict[str, BaseTool] = {}
_POLICY: dict[AgentName, list[str]] = {agent: [] for agent in AGENTS}


def register(agent: AgentName) -> Callable[[BaseTool], BaseTool]:
    """Dekorator: daftarkan tool dan berikan hak aksesnya ke satu agen."""

    def wrap(tool: BaseTool) -> BaseTool:
        if tool.name in _REGISTRY:
            raise ValueError(f"tool sudah terdaftar: {tool.name}")
        _REGISTRY[tool.name] = tool
        _POLICY[agent].append(tool.name)
        return tool

    return wrap


# ---------- policy ----------


def tools_for(agent: AgentName) -> list[BaseTool]:
    """Tool yang boleh dipakai agen."""
    return [_REGISTRY[name] for name in _POLICY[agent]]


# ---------- dispatch ----------


def _prepare(call: ToolCall, by_name: dict[str, BaseTool]) -> tuple[BaseTool, dict[str, Any]]:
    """Validasi satu tool call terhadap skema argumen tool."""
    tool = by_name.get(call["name"])
    if tool is None:
        raise ToolCallError(f"tool tidak dikenal atau tidak diizinkan: {call['name']}")
    try:
        args = tool.args_schema.model_validate(call["args"]).model_dump()  # type: ignore[union-attr]
    except ValidationError as exc:
        detail = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
        raise ToolCallError(f"{call['name']}: argumen tidak valid ({detail})") from exc
    return tool, args


async def dispatch(agent: AgentName, calls: Sequence[ToolCall], on_result: OnResult | None = None) -> list[tuple[str, Any]]:
    """Validasi semua call dulu, lalu jalankan berurutan; kembalikan (nama, keluaran)."""
    if not calls:
        raise ToolCallError("tidak ada tool call")
    by_name = {tool.name: tool for tool in tools_for(agent)}
    prepared = [_prepare(call, by_name) for call in calls]
    results: list[tuple[str, Any]] = []
    for tool, args in prepared:
        output = await tool.ainvoke(args)
        results.append((tool.name, output))
        if on_result is not None:
            on_result(tool.name, output)
    return results
