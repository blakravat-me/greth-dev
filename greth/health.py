"""Pemeriksaan awal koneksi, API key, dan ketersediaan model Ollama."""

from greth.config import settings
from llm.ollama import OllamaError, get_client


async def check_ollama() -> list[str]:
    """Kembalikan daftar masalah fatal; list kosong berarti siap."""
    if settings.is_cloud and not settings.ollama_api_key:
        return ["OLLAMA_API_KEY wajib diatur untuk https://ollama.com (buat di ollama.com/settings/keys)"]
    try:
        installed = set(await get_client().list_models())
    except OllamaError as exc:
        return [f"Ollama tidak dapat dijangkau di {settings.ollama_host}: {exc}"]
    if settings.is_cloud:
        return []  # nama model cloud tidak diverifikasi lewat daftar lokal
    wanted = set(settings.models.values())
    missing = sorted(m for m in wanted if m not in installed and f"{m}:latest" not in installed)
    return [f"Model belum ada: {m} (jalankan: ollama pull {m})" for m in missing]
