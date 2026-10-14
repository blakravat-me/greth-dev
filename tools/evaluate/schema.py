"""Skema evaluate."""

from pydantic import BaseModel, Field

from helpers.clock import now_iso


class EvaluateArgs(BaseModel):
    """Argumen evaluate: success (OK/FAIL), next (lanjut strategi), to_leader (kembali ke leader)."""

    observed: str
    feedback: str
    success: bool = False
    next: bool = False
    to_leader: bool = False


class Evaluation(EvaluateArgs):
    """Keluaran evaluate."""

    date: str = Field(default_factory=now_iso)
