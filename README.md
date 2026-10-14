# Greth

Multi-agent berbasis workflow komandan militer: Leader -> Operator -> Evaluator
(LangGraph + Ollama lewat httpx async). Satu model dipakai semua agen.

## Jalankan

    make install
    make run                                   # lokal: http://localhost:11434, qwen3:8b
    make run ARGS="--base https://ollama.com --key KEY --model gpt-oss:120b"

Langsung tanpa make: `uv run python main.py --help`.

## Opsi (tanpa environment variable)

- `--base` base url Ollama (default `http://localhost:11434`).
- `--key` API key Ollama (opsional), dikirim sebagai `Authorization: Bearer`.
- `--model` model untuk semua agen (default `qwen3:8b`).

`internet_search` dan `read_url` memakai Ollama web search/fetch API (`ollama.com`) dan selalu butuh `--key`.
Parameter tetap (temperature, num_ctx, batas history, percobaan) ada di `greth/config.py`.

## Kontrol

- Ketik misi lalu Enter.
- `ESC` menghentikan misi yang sedang berjalan (kembali ke input misi).
- `Ctrl+C` keluar dari program.

## Konteks LLM

Setiap input ke LLM diawali `Current date: <ISO 8601 UTC>` (input stage dan pesan koreksi retry).

## Perintah

    make test     # pytest
    make lint     # ruff check
    make format   # ruff check --fix + ruff format

## Menambah tool

1. Buat `tools/<nama>/schema.py` (argumen + keluaran) dan `tools/<nama>/tool.py`.
2. Di `tool.py` pasang `@register("<agen>")` di atas `@tool(...)`.
3. Tambahkan `<nama>` ke daftar di `tools/__init__.py`.
