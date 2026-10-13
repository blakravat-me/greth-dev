"""Fungsi routing edge dinamis."""

from langgraph.graph import END

from greth.state import MissionState


def after_leader(state: MissionState) -> str:
    """Leader -> Operator; misi selesai -> END."""
    return END if state["completed"] else "operator"


def after_evaluator(state: MissionState) -> str:
    """Evaluator -> Leader jika strategi ditutup, selain itu -> Operator."""
    return "leader" if state["closed"] else "operator"
