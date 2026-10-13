# Greth

Multi-agent berbasis workflow komandan militer: Leader -> Operator -> Evaluator
(LangGraph + Ollama lewat httpx async).

## Jalankan

    make install
    cp .env.example .env     # isi OLLAMA_API_KEY untuk Ollama Cloud
    make run

Lokal tanpa API key: `ollama pull qwen3:4b`, lalu `make run`.
Fitur `internet_search` dan `read_url` memakai Ollama web search/fetch API dan selalu butuh `OLLAMA_API_KEY`.

## Kontrol

- Ketik misi lalu Enter.
- `ESC` menghentikan misi yang sedang berjalan (kembali ke input misi).
- `Ctrl+C` keluar dari program.

## Environment

- `OLLAMA_API_KEY` dikirim sebagai `Authorization: Bearer`; bila diisi, host default `https://ollama.com`.
- `OLLAMA_HOST` default `http://localhost:11434` (atau cloud bila ada API key).
- `GRETH_MODEL` model semua agen (default `qwen3:4b` lokal, `nemotron-3-super:cloud` cloud).
- `GRETH_LEADER_MODEL`, `GRETH_OPERATOR_MODEL`, `GRETH_EVALUATOR_MODEL` override per agen.

Parameter lain (batas history, percobaan, timeout) ada di `greth/config.py`.

## Perintah

    make test     # pytest
    make lint     # ruff check
    make format   # ruff check --fix + ruff format

## Menambah tool

1. Buat `tools/<nama>/schema.py` (argumen + keluaran) dan `tools/<nama>/tool.py`.
2. Di `tool.py` pasang `@register("<agen>")` di atas `@tool(...)`.
3. Tambahkan `<nama>` ke daftar di `tools/__init__.py`.
