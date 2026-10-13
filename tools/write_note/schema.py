"""Skema write_note."""

from pydantic import BaseModel


class WriteNoteArgs(BaseModel):
    """Argumen write_note."""

    title: str
    body: str
    displaying: bool = False
