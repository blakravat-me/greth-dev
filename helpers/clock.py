"""Sumber waktu tunggal."""

from datetime import UTC, datetime


def now_iso() -> str:
    """Waktu UTC saat ini (ISO 8601, presisi detik)."""
    return datetime.now(UTC).isoformat(timespec="seconds")
