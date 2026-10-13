"""Fixture dan model skrip bersama."""

from typing import Any

from langchain.messages import AIMessage, AnyMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedModel(BaseChatModel):
    """Model palsu yang memutar AIMessage sesuai skrip."""

    script: list[AIMessage]
    cursor: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[AnyMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        message = self.script[self.cursor]
        self.cursor += 1
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools, **kwargs: Any):
        return self


def call(name: str, **args: Any) -> AIMessage:
    """AIMessage berisi satu tool call."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"id-{name}"}])
