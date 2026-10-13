"""Node Evaluator: menilai hasil dan menentukan arah berikutnya."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from greth import history
from greth.agents.base import run_tools
from greth.agents.stage_input import evaluator_input
from greth.config import settings
from greth.reporter import Reporter
from greth.state import HistoryItem, MissionState, current_strategy


def make_evaluator(model: BaseChatModel, reporter: Reporter):
    """Buat node Evaluator."""

    async def evaluator(state: MissionState) -> dict[str, Any]:
        """Nilai strategi; tutup bila berhasil atau percobaan habis."""
        _, evaluation = (await run_tools(model, "evaluator", evaluator_input(state)))[0]
        reporter.evaluation(evaluation)
        attempts = state["attempts"] + 1
        exhausted = not evaluation.success and attempts >= settings.max_attempts
        update: dict[str, Any] = {
            "feedback": evaluation.feedback,
            "attempts": attempts,
            "closed": evaluation.success or exhausted,
        }
        if update["closed"]:
            observed = evaluation.observed
            if exhausted:
                observed = f"GAGAL setelah {attempts} percobaan: {observed}"
            item = HistoryItem(strategy=current_strategy(state).strategy, observed=observed)
            update["history"] = history.push(state["history"], item)
        return update

    return evaluator
