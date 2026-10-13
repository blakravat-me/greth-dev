"""Skema internet_search."""

from pydantic import BaseModel


class InternetSearchArgs(BaseModel):
    """Argumen internet_search."""

    search: str
    displaying: bool = False
