"""Node Evaluator: menilai hasil dan menentukan transisi (success, next, to_leader)."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from greth import history
from greth.agents.base import run_tools
from greth.agents.stage_input import evaluator_input
from greth.config import settings
from greth.reporter import Reporter
from greth.state import HistoryItem, LastStrategy, MissionState, Status, current_strategy
from helpers.clock import now_iso


def make_evaluator(model: BaseChatModel, reporter: Reporter):
    """Buat node Evaluator."""

    async def evaluator(state: MissionState) -> dict[str, Any]:
        """Nilai strategi aktif; tentukan tetap, lanjut strategi, atau kembali ke Leader."""
        _, evaluation = (await run_tools(model, "evaluator", evaluator_input(state)))[0]
        reporter.evaluation(evaluation)

        attempts = state["attempts"] + 1
        status: Status = "OK" if evaluation.success else "FAIL"
        exhausted = not evaluation.success and attempts >= settings.max_attempts
        # Percobaan habis adalah jaring pengaman (no-deadlock): paksa strategi ditutup.
        resolve = evaluation.next or evaluation.to_leader or exhausted
        to_leader = evaluation.to_leader

        update: dict[str, Any] = {"feedback": evaluation.feedback}

        if not resolve:
            update["attempts"] = attempts
            update["to_leader"] = False
            return update

        item = HistoryItem(strategy=current_strategy(state).strategy, status=status, observed=evaluation.observed, date=now_iso())
        update["history"] = history.push(state["history"], item)
        update["last_strategy"] = LastStrategy(strategy=current_strategy(state), status=status)
        update["runs"] = []
        update["attempts"] = 0

        if to_leader:
            update["strategy"] = None
            update["queue"] = []
        else:
            queue = state["queue"]
            update["strategy"] = queue[0] if queue else None
            update["queue"] = queue[1:] if queue else []
            if update["strategy"] is None:
                to_leader = True  # no-deadlock: antrean habis, tidak ada yang bisa dikerjakan Operator

        update["to_leader"] = to_leader
        return update

    return evaluator
