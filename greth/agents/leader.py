"""Node Leader: memecah misi menjadi strategi bertahap (boleh beberapa sekaligus)."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from greth.agents.base import run_tools
from greth.agents.stage_input import leader_input
from greth.reporter import Reporter
from greth.state import MissionState
from tools.policy import ToolCallError

_COMPLETED = "mission_completed"
_STRATEGY = "add_strategy"


def _validate(results: list[tuple[str, Any]]) -> None:
    """Satu giliran Leader: beberapa add_strategy, ATAU tepat satu mission_completed."""
    names = {name for name, _ in results}
    if names - {_COMPLETED, _STRATEGY}:
        raise ToolCallError("leader hanya boleh memanggil add_strategy atau mission_completed")
    if _COMPLETED in names and (len(results) > 1 or _STRATEGY in names):
        raise ToolCallError("mission_completed harus dipanggil sendiri, tanpa add_strategy lain")


def make_leader(model: BaseChatModel, reporter: Reporter):
    """Buat node Leader."""

    async def leader(state: MissionState) -> dict[str, Any]:
        """Pilih satu atau beberapa strategi berikutnya, atau tutup misi."""
        results = await run_tools(model, "leader", leader_input(state), validate=_validate)
        if results[0][0] == _COMPLETED:
            reporter.completed(results[0][1])
            return {"completed": True}
        strategies = [output for _, output in results]
        for item in strategies:
            reporter.strategy(item)
        return {
            "completed": False,
            "strategy": strategies[0],
            "queue": strategies[1:],
            "runs": [],
            "attempts": 0,
            "feedback": "",
            "to_leader": False,
        }

    return leader
