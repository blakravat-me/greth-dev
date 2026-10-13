"""Tool Leader: membuat strategi berikutnya."""

from langchain.tools import tool

from tools.add_strategy.schema import AddStrategyArgs, Strategy, StrategyType
from tools.policy import register


@register("leader")
@tool("add_strategy", args_schema=AddStrategyArgs)
async def add_strategy(type: StrategyType, strategy: str, reason: str, fallback: str) -> Strategy:
    """Tambah strategi berikutnya: type, strategy, reason, dan fallback."""
    return Strategy(type=type, strategy=strategy, reason=reason, fallback=fallback)
