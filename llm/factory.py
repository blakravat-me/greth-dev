"""Pabrik model: satu model untuk seluruh agen."""

from greth.config import LlmConfig
from llm.chat import OllamaChat
from llm.ollama import configure_client


def build_model(cfg: LlmConfig) -> OllamaChat:
    """Konfigurasi klien tunggal dan buat satu OllamaChat."""
    return OllamaChat(client=configure_client(cfg), model=cfg.model)
