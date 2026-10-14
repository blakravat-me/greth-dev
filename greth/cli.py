"""Argumen CLI: satu-satunya sumber konfigurasi LLM (tanpa environment)."""

import argparse
from collections.abc import Sequence

from greth.config import DEFAULT_BASE_URL, DEFAULT_MODEL, LlmConfig, normalize_base_url


def parse_args(argv: Sequence[str] | None = None) -> LlmConfig:
    """Parse --base, --key, --model menjadi LlmConfig."""
    parser = argparse.ArgumentParser(prog="greth", description="AI multi-agent: Leader, Operator, Evaluator")
    parser.add_argument("--base", default=DEFAULT_BASE_URL, help="base url Ollama (default: %(default)s)")
    parser.add_argument("--key", default=None, help="API key Ollama (opsional)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model untuk semua agen (default: %(default)s)")
    args = parser.parse_args(argv)
    return LlmConfig(
        model=args.model.strip(),
        base_url=normalize_base_url(args.base),
        api_key=(args.key or "").strip() or None,
    )
