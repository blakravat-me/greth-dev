"""Node Leader: memecah misi menjadi strategi bertahap."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from greth.agents.base import run_tools
from greth.agents.stage_input import leader_input
from greth.reporter import Reporter
from greth.state import MissionState
from tools.mission_completed.schema import Completed


def make_leader(model: BaseChatModel, reporter: Reporter):
    """Buat node Leader."""

    async def leader(state: MissionState) -> dict[str, Any]:
        """Pilih strategi berikutnya atau tutup misi."""
        _, output = (await run_tools(model, "leader", leader_input(state)))[0]
        if isinstance(output, Completed):
            reporter.completed(output)
            return {"completed": True}
        reporter.strategy(output)
        return {
            "completed": False,
            "last_strategy": state["strategy"],
            "strategy": output,
            "runs": [],
            "attempts": 0,
            "closed": False,
            "feedback": "",
        }

    return leader
