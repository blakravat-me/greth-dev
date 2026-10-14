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
- `--key` API key (opsional), dikirim sebagai `Authorization: Bearer` ke `--base` untuk chat.
- `--model` model untuk semua agen (default `qwen3:8b`).

`internet_search` memakai DuckDuckGo (`ddgs`) dan `read_url` memakai HTTP biasa; keduanya tidak
butuh `--key`. Parameter tetap (temperature, num_ctx, batas history, percobaan) ada di `greth/config.py`.

## Kontrol

- Ketik misi lalu Enter.
- `ESC` menghentikan misi yang sedang berjalan (kembali ke input misi).
- `Ctrl+C` keluar dari program.

## Alur Leader -> Operator -> Evaluator

- **Leader** memanggil `add_strategy` satu kali atau beberapa kali sekaligus, membentuk antrean
  strategi (strategi pertama dikerjakan dulu), atau memanggil `mission_completed` sendirian.
- **Operator** mengeksekusi Current Strategy lewat tool (`internet_search`, `read_url`, `write_note`).
- **Evaluator** memanggil `evaluate(observed, feedback, success, next, to_leader)`:
  - `success`: status `OK`/`FAIL` strategi saat ini.
  - `next`: tutup strategi ini dan lanjut ke strategi berikutnya di antrean.
  - `to_leader`: kembali ke Leader (strategi berjalan otomatis ditutup, antrean sisa dibatalkan).
  - Jaring pengaman: jika gagal berulang sampai batas (`max_attempts`), strategi dipaksa ditutup
    sebagai `FAIL` walau Evaluator belum memilih `next=true` (anti-deadlock).

## Konteks LLM

Setiap input ke LLM diawali `Current date: <ISO 8601 UTC>` (waktu panggilan). Setiap strategi dan
History membawa `Date` masing-masing (waktu dibuat/ditutup).

## Perintah

    make test     # pytest
    make lint     # ruff check
    make format   # ruff check --fix + ruff format

## Menambah tool

1. Buat `tools/<nama>/schema.py` (argumen + keluaran) dan `tools/<nama>/tool.py`.
2. Di `tool.py` pasang `@register("<agen>")` di atas `@tool(...)`.
3. Tambahkan `<nama>` ke daftar di `tools/__init__.py`.
