"""State graph misi (source of truth antar-agen)."""

from typing import Literal, TypedDict

from tools.add_strategy.schema import Strategy

Status = Literal["OK", "FAIL"]


class HistoryItem(TypedDict):
    """Satu strategi yang sudah ditutup beserta status dan hasil pengamatannya."""

    strategy: str
    status: Status
    observed: str
    date: str


class LastStrategy(TypedDict):
    """Strategi terakhir yang ditutup, beserta statusnya."""

    strategy: Strategy
    status: Status


class MissionState(TypedDict):
    """State yang mengalir di graph."""

    last_mission: str
    mission: str
    mission_date: str
    history: list[HistoryItem]
    queue: list[Strategy]
    strategy: Strategy | None
    last_strategy: LastStrategy | None
    runs: list[str]
    last_result: str
    feedback: str
    attempts: int
    to_leader: bool
    completed: bool


def current_strategy(state: MissionState) -> Strategy:
    """Ambil strategi aktif; error jika belum ada."""
    strategy = state["strategy"]
    if strategy is None:
        raise RuntimeError("Strategi aktif belum ada")
    return strategy
