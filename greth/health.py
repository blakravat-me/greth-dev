"""Pemeriksaan awal koneksi dan ketersediaan model Ollama."""

from greth.config import LlmConfig
from llm.ollama import OllamaError, get_client


async def check_ollama(cfg: LlmConfig) -> list[str]:
    """Kembalikan daftar masalah fatal; list kosong berarti siap."""
    try:
        installed = set(await get_client().list_models())
    except OllamaError as exc:
        return [f"Ollama tidak dapat dijangkau di {cfg.base_url}: {exc}"]
    if cfg.model in installed or f"{cfg.model}:latest" in installed:
        return []
    return [f"Model belum ada: {cfg.model} (jalankan: ollama pull {cfg.model})"]
