"""Eksekusi satu misi; ESC menghentikan misi tanpa menutup program."""

import asyncio

from langgraph.graph.state import CompiledStateGraph

from greth.config import settings
from greth.session import Session
from helpers.console import show_error, show_stopped
from ui.esc import EscWatcher


async def _drive(graph: CompiledStateGraph, session: Session, mission: str) -> None:
    """Jalankan graph dan sinkronkan riwayat ke session di tiap langkah."""
    config = {"recursion_limit": settings.recursion_limit}
    async for snapshot in graph.astream(session.begin(mission), config, stream_mode="values"):
        session.absorb(snapshot)


async def run_mission(graph: CompiledStateGraph, session: Session, mission: str) -> None:
    """Jalankan misi sampai selesai, dihentikan ESC, atau gagal."""
    task = asyncio.create_task(_drive(graph, session, mission))
    with EscWatcher(task.cancel) as esc:
        try:
            await task
        except asyncio.CancelledError:
            if not esc.pressed:
                raise
            show_stopped()
        except Exception as exc:  # batas aplikasi: misi gagal, program lanjut
            show_error(exc)
