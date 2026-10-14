"""Entry point: loop MissionInput tanpa exit program."""

import asyncio

from greth.cli import parse_args
from greth.config import LlmConfig
from greth.graph import build_graph
from greth.health import check_ollama
from greth.mission import run_mission
from greth.session import Session
from helpers.console import show_banner, show_goodbye, show_warning
from llm.factory import build_model
from llm.ollama import get_client
from ui.mission_input import ask_mission
from ui.reporter import ConsoleReporter


async def main(cfg: LlmConfig) -> None:
    """Loop utama: input misi -> jalankan -> kembali ke input."""
    model = build_model(cfg)
    try:
        if problems := await check_ollama(cfg):
            raise SystemExit("\n".join(problems))
        if not cfg.api_key:
            show_warning("--key belum diberikan: internet_search dan read_url akan gagal.")
        graph = build_graph(model, ConsoleReporter())
        session = Session()
        show_banner()
        while True:
            try:
                mission = await ask_mission()
            except (EOFError, KeyboardInterrupt):
                return
            if mission:
                await run_mission(graph, session, mission)
    finally:
        await get_client().aclose()


def run() -> None:
    """Jalankan aplikasi; Ctrl+C keluar manual."""
    cfg = parse_args()
    try:
        asyncio.run(main(cfg))
    except KeyboardInterrupt:
        pass
    show_goodbye()


if __name__ == "__main__":
    run()
