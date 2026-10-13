"""Adaptor LangChain BaseChatModel di atas OllamaClient (tool calling native)."""

import json
from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

from llm.ollama import OllamaClient


def to_wire(messages: Sequence[AnyMessage]) -> list[dict[str, Any]]:
    """Konversi pesan LangChain ke format /api/chat."""
    wire: list[dict[str, Any]] = []
    for msg in messages:
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        if isinstance(msg, SystemMessage):
            wire.append({"role": "system", "content": content})
        elif isinstance(msg, HumanMessage):
            wire.append({"role": "user", "content": content})
        elif isinstance(msg, AIMessage):
            item: dict[str, Any] = {"role": "assistant", "content": content}
            if msg.tool_calls:
                item["tool_calls"] = [{"function": {"name": c["name"], "arguments": c["args"]}} for c in msg.tool_calls]
            wire.append(item)
        elif isinstance(msg, ToolMessage):
            item = {"role": "tool", "content": content}
            if msg.name:
                item["tool_name"] = msg.name
            wire.append(item)
        else:
            raise TypeError(f"tipe pesan tidak didukung: {type(msg).__name__}")
    return wire


def _args(raw: Any) -> dict[str, Any]:
    """Argumen tool call bisa berupa dict atau string JSON."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return dict(raw) if isinstance(raw, dict) else {}


def from_wire(message: dict[str, Any]) -> AIMessage:
    """Konversi message /api/chat ke AIMessage dengan tool_calls."""
    calls = [
        {"name": c["function"]["name"], "args": _args(c["function"].get("arguments")), "id": uuid4().hex, "type": "tool_call"}
        for c in message.get("tool_calls") or []
    ]
    return AIMessage(content=message.get("content") or "", tool_calls=calls)


class OllamaChat(BaseChatModel):
    """Chat model async-only yang memakai OllamaClient."""

    client: OllamaClient
    model: str

    @property
    def _llm_type(self) -> str:
        return "ollama-httpx"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any):
        """Ikat skema tool (format OpenAI) yang diterima Ollama."""
        return self.bind(tools=[convert_to_openai_tool(t) for t in tools], **kwargs)

    def _generate(self, *args: Any, **kwargs: Any) -> ChatResult:
        raise NotImplementedError("OllamaChat hanya mendukung pemanggilan async")

    async def _agenerate(
        self,
        messages: list[AnyMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = await self.client.chat(self.model, to_wire(messages), tools)
        return ChatResult(generations=[ChatGeneration(message=from_wire(message))])
