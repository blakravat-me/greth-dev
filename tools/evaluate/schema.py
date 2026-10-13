"""Skema evaluate."""

from pydantic import BaseModel, Field

from helpers.clock import now_iso


class EvaluateArgs(BaseModel):
    """Argumen evaluate."""

    observed: str
    feedback: str
    success: bool = False


class Evaluation(EvaluateArgs):
    """Keluaran evaluate."""

    date: str = Field(default_factory=now_iso)
