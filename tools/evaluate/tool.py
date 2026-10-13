"""Tool Evaluator: menilai keberhasilan strategi."""

from langchain.tools import tool

from tools.evaluate.schema import EvaluateArgs, Evaluation
from tools.policy import register


@register("evaluator")
@tool("evaluate", args_schema=EvaluateArgs)
async def evaluate(observed: str, feedback: str, success: bool = False) -> Evaluation:
    """Nilai strategi: observed, feedback, dan success (true bila tercapai)."""
    return Evaluation(observed=observed, feedback=feedback, success=success)
