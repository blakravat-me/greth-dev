"""Pemeriksaan awal koneksi, API key, dan ketersediaan model Ollama."""

from greth.config import CLOUD_URL, LlmConfig
from llm.ollama import OllamaError, get_client


async def check_ollama(cfg: LlmConfig) -> list[str]:
    """Kembalikan daftar masalah fatal; list kosong berarti siap."""
    if cfg.is_cloud and not cfg.api_key:
        return [f"--key wajib untuk {CLOUD_URL} (buat di ollama.com/settings/keys)"]
    try:
        installed = set(await get_client().list_models())
    except OllamaError as exc:
        return [f"Ollama tidak dapat dijangkau di {cfg.base_url}: {exc}"]
    if cfg.is_cloud or cfg.model in installed or f"{cfg.model}:latest" in installed:
        return []
    return [f"Model belum ada: {cfg.model} (jalankan: ollama pull {cfg.model})"]
