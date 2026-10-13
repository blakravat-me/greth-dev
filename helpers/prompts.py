"""Pemuat system prompt per agen dari folder prompts/."""

from functools import cache
from pathlib import Path

from greth.types import AgentName

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@cache
def load_prompt(agent: AgentName) -> str:
    """Baca prompts/<agent>.md."""
    return (PROMPTS_DIR / f"{agent}.md").read_text(encoding="utf-8")
