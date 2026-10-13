"""State graph misi (source of truth antar-agen)."""

from typing import TypedDict

from tools.add_strategy.schema import Strategy


class HistoryItem(TypedDict):
    """Satu strategi selesai beserta hasil pengamatannya."""

    strategy: str
    observed: str


class MissionState(TypedDict):
    """State yang mengalir di graph."""

    last_mission: str
    mission: str
    history: list[HistoryItem]
    strategy: Strategy | None
    last_strategy: Strategy | None
    runs: list[str]
    last_result: str
    feedback: str
    attempts: int
    closed: bool
    completed: bool


def current_strategy(state: MissionState) -> Strategy:
    """Ambil strategi aktif; error jika belum ada."""
    strategy = state["strategy"]
    if strategy is None:
        raise RuntimeError("Strategi aktif belum ada")
    return strategy
