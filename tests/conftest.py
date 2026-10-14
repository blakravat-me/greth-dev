"""Model skrip bersama."""

from typing import Any

from langchain.messages import AIMessage, AnyMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedModel(BaseChatModel):
    """Satu model palsu untuk semua agen; memutar AIMessage berurutan dan merekam input."""

    script: list[AIMessage]
    cursor: int = 0
    seen: list[list[AnyMessage]] = []

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[AnyMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        self.seen.append(list(messages))
        message = self.script[self.cursor]
        self.cursor += 1
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools, **kwargs: Any):
        return self


def call(name: str, **args: Any) -> AIMessage:
    """AIMessage berisi satu tool call."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"id-{name}"}])
