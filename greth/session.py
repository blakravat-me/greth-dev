"""Memori antar-misi dalam satu proses (tanpa exit program)."""

from dataclasses import dataclass, field

from greth.state import HistoryItem, MissionState
from helpers.clock import now_iso


@dataclass
class Session:
    """Menyimpan misi terakhir dan riwayat strategi."""

    last_mission: str = ""
    history: list[HistoryItem] = field(default_factory=list)

    def begin(self, mission: str) -> MissionState:
        """Buat state awal untuk misi baru."""
        state = MissionState(
            last_mission=self.last_mission,
            mission=mission,
            mission_date=now_iso(),
            history=list(self.history),
            queue=[],
            strategy=None,
            last_strategy=None,
            runs=[],
            last_result="",
            feedback="",
            attempts=0,
            to_leader=False,
            completed=False,
        )
        self.last_mission = mission
        return state

    def absorb(self, state: MissionState) -> None:
        """Salin riwayat terbaru dari snapshot graph."""
        self.history = state["history"]
