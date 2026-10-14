"""Operasi riwayat strategi (maksimal N terakhir)."""

from greth.config import settings
from greth.state import HistoryItem


def push(history: list[HistoryItem], item: HistoryItem) -> list[HistoryItem]:
    """Tambah item dan pangkas ke batas terakhir."""
    return [*history, item][-settings.history_limit :]


def render(history: list[HistoryItem]) -> str:
    """Format riwayat bernomor dengan status [OK/FAIL] untuk input Leader."""
    if not history:
        return "-"
    return "\n".join(
        f"{i}. [{h['status']}] Strategy: {h['strategy']} | Observed: {h['observed']} ({h['date']})"
        for i, h in enumerate(history, start=1)
    )
