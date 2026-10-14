"""Loop LLM bersama: selalu tool call, dengan retry bila tidak valid."""

from typing import Any

from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel

from greth.config import settings
from greth.types import AgentName
from helpers.clock import now_iso
from helpers.prompts import load_prompt
from tools.policy import OnResult, ToolCallError, dispatch, tools_for


class AgentError(Exception):
    """Agen gagal menghasilkan tool call valid setelah semua percobaan."""


def stamp(text: str) -> str:
    """Awali input LLM dengan tanggal saat ini."""
    return f"Current date: {now_iso()}\n\n{text}"


async def run_tools(
    model: BaseChatModel, agent: AgentName, user: str, on_result: OnResult | None = None
) -> list[tuple[str, Any]]:
    """Panggil model sampai menghasilkan tool call valid; kembalikan keluaran tool."""
    bound = model.bind_tools(tools_for(agent))
    messages: list[AnyMessage] = [SystemMessage(load_prompt(agent)), HumanMessage(stamp(user))]
    problem = ""
    for _ in range(settings.tool_retries + 1):
        reply = await bound.ainvoke(messages)
        try:
            return await dispatch(agent, reply.tool_calls, on_result)
        except ToolCallError as exc:
            problem = str(exc)
        messages.append(reply)
        messages.extend(
            ToolMessage(content=stamp(f"error: {problem}"), tool_call_id=call["id"] or "", name=call["name"])
            for call in reply.tool_calls
        )
        messages.append(HumanMessage(stamp(f"Kesalahan: {problem}. Panggil tool yang valid.")))
    raise AgentError(f"{agent}: tidak ada tool call valid ({problem})")
