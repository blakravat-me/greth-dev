"""Skema mission_completed."""

from pydantic import BaseModel, Field

from helpers.clock import now_iso


class MissionCompletedArgs(BaseModel):
    """Argumen mission_completed (tanpa argumen)."""


class Completed(BaseModel):
    """Keluaran mission_completed."""

    completed: bool = True
    date: str = Field(default_factory=now_iso)
