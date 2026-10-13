"""Pabrik model per agen."""

from greth.config import settings
from greth.types import AGENTS, AgentName
from llm.chat import OllamaChat
from llm.ollama import get_client


def build_models() -> dict[AgentName, OllamaChat]:
    """Buat satu OllamaChat per agen dengan klien bersama."""
    client = get_client()
    return {agent: OllamaChat(client=client, model=settings.models[agent]) for agent in AGENTS}
