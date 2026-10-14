"""Tool Evaluator: menilai keberhasilan strategi dan menentukan transisi alur."""

from langchain.tools import tool

from tools.evaluate.schema import EvaluateArgs, Evaluation
from tools.policy import register


@register("evaluator")
@tool("evaluate", args_schema=EvaluateArgs)
async def evaluate(
    observed: str,
    feedback: str,
    success: bool = False,
    next: bool = False,  # noqa: A002 - nama mengikuti kontrak tool
    to_leader: bool = False,
) -> Evaluation:
    """Nilai strategi (success=OK/FAIL) dan tentukan transisi (next, to_leader)."""
    return Evaluation(observed=observed, feedback=feedback, success=success, next=next, to_leader=to_leader)
