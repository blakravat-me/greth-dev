"""Implementasi Reporter untuk terminal (rich)."""

from rich.markup import escape
from rich.panel import Panel

from helpers.console import console
from tools.add_strategy.schema import Strategy
from tools.evaluate.schema import Evaluation
from tools.mission_completed.schema import Completed
from tools.policy import ToolOutput


class ConsoleReporter:
    """Reporter yang menulis event ke terminal."""

    def strategy(self, item: Strategy) -> None:
        """Tampilkan strategi Leader."""
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
        """Tampilkan penilaian Evaluator."""
        style, label = ("green", "BERHASIL") if item.success else ("yellow", "BELUM")
        body = f"{escape(item.observed)}\n[dim]feedback:[/dim] {escape(item.feedback)}"
        console.print(Panel(body, title=f"EVALUATOR · {label}", border_style=style))

    def completed(self, item: Completed) -> None:
        """Tampilkan penutupan misi."""
        console.print("[bold green]Misi selesai.[/bold green]\n")
