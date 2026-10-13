"""Kontrak pelaporan ke UI (node tidak mengenal implementasi UI)."""

from typing import Protocol

from tools.add_strategy.schema import Strategy
from tools.evaluate.schema import Evaluation
from tools.mission_completed.schema import Completed
from tools.policy import ToolOutput


class Reporter(Protocol):
    """Antarmuka event yang ditampilkan ke pengguna."""

    def strategy(self, item: Strategy) -> None:
        """Strategi baru dari Leader."""

    def output(self, item: ToolOutput) -> None:
        """Keluaran tool Operator dengan displaying=true."""

    def evaluation(self, item: Evaluation) -> None:
        """Hasil penilaian Evaluator."""

    def completed(self, item: Completed) -> None:
        """Misi dinyatakan selesai."""
