"""Implementasi Reporter untuk terminal (rich)."""

from rich.markup import escape
from rich.panel import Panel

from helpers.console import console
from tools.add_strategy.schema import Strategy
from tools.evaluate.schema import Evaluation
from tools.mission_completed.schema import Completed
from tools.policy import ToolOutput


def _yn(value: bool) -> str:
    """Terjemahkan boolean ke ya/tidak."""
    return "ya" if value else "tidak"


class ConsoleReporter:
    """Reporter yang menulis event ke terminal."""

    def strategy(self, item: Strategy) -> None:
        """Tampilkan satu strategi dari Leader (bisa dipanggil beberapa kali per giliran)."""
        body = (
            f"[b]{escape(item.strategy)}[/b]\n"
            f"[dim]alasan:[/dim] {escape(item.reason)}\n"
            f"[dim]fallback:[/dim] {escape(item.fallback)}"
        )
        console.print(Panel(body, title=f"LEADER · {item.type}", border_style="cyan"))

    def output(self, item: ToolOutput) -> None:
        """Tampilkan keluaran Operator yang displaying=true."""
        title = escape(item.title or "output")
        console.print(
            Panel(escape(item.body), title=f"OPERATOR · {title}", subtitle=escape(item.url) or None, border_style="green")
        )

    def evaluation(self, item: Evaluation) -> None:
        """Tampilkan penilaian Evaluator: status dan transisi (next, to_leader)."""
        style, label = ("green", "OK") if item.success else ("yellow", "FAIL")
        transition = f"next={_yn(item.next)} · to_leader={_yn(item.to_leader)}"
        body = f"{escape(item.observed)}\n[dim]feedback:[/dim] {escape(item.feedback)}\n[dim]{transition}[/dim]"
        console.print(Panel(body, title=f"EVALUATOR · {label}", border_style=style))

    def completed(self, item: Completed) -> None:
        """Tampilkan penutupan misi."""
        console.print("[bold green]Misi selesai.[/bold green]\n")
