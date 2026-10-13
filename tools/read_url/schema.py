"""Skema read_url."""

from pydantic import BaseModel


class ReadUrlArgs(BaseModel):
    """Argumen read_url."""

    url: str
    displaying: bool = False
