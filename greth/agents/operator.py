"""Node Operator: menerjemahkan strategi menjadi eksekusi tool."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from greth.agents.base import run_tools
from greth.agents.stage_input import operator_input
from greth.reporter import Reporter
from greth.state import MissionState
from tools.policy import ToolOutput


def _format_run(results: list[tuple[str, Any]]) -> str:
    """Serialisasi hasil mentah satu putaran Operator."""
    return "\n".join(f"[{name}] {item.model_dump_json()}" for name, items in results for item in items)


def make_operator(model: BaseChatModel, reporter: Reporter):
    """Buat node Operator."""

    def show(_name: str, items: list[ToolOutput]) -> None:
        """Tampilkan keluaran yang diberi displaying=true."""
        for item in items:
            if item.displaying:
                reporter.output(item)

    async def operator(state: MissionState) -> dict[str, Any]:
        """Eksekusi strategi aktif lewat tool."""
        results = await run_tools(model, "operator", operator_input(state), on_result=show)
        raw = _format_run(results)
        return {"runs": [*state["runs"], raw], "last_result": raw}

    return operator
