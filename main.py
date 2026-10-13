"""Entry point: loop MissionInput tanpa exit program."""

import asyncio

from greth.config import settings
from greth.graph import build_graph
from greth.health import check_ollama
from greth.mission import run_mission
from greth.session import Session
from helpers.console import show_banner, show_goodbye, show_warning
from llm.factory import build_models
from llm.ollama import get_client
from ui.mission_input import ask_mission
from ui.reporter import ConsoleReporter


async def main() -> None:
    """Loop utama: input misi -> jalankan -> kembali ke input."""
    try:
        if problems := await check_ollama():
            raise SystemExit("\n".join(problems))
        if not settings.ollama_api_key:
            show_warning("OLLAMA_API_KEY belum diatur: internet_search dan read_url akan gagal.")
        graph = build_graph(build_models(), ConsoleReporter())
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    show_goodbye()


if __name__ == "__main__":
    run()
