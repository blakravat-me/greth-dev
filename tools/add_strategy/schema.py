"""Skema add_strategy."""

from typing import Literal

from pydantic import BaseModel, Field

from helpers.clock import now_iso

StrategyType = Literal["RECON", "EXPLOIT", "POST-EXPLOIT", "REPORT"]


class AddStrategyArgs(BaseModel):
    """Argumen add_strategy."""

    type: StrategyType
    strategy: str
    reason: str
    fallback: str


class Strategy(AddStrategyArgs):
    """Keluaran add_strategy."""

    date: str = Field(default_factory=now_iso)
