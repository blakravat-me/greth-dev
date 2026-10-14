"""Konsol rich bersama dan fungsi pesan sistem."""

from rich.console import Console
from rich.markup import escape

console = Console()


def show_banner() -> None:
    """Tampilkan petunjuk kontrol."""
    console.print("[bold]Greth[/bold] · ESC = hentikan misi · Ctrl+C = keluar\n")


def show_stopped() -> None:
    """Tampilkan misi dihentikan pengguna."""
    console.print("[bold yellow]Misi dihentikan (ESC).[/bold yellow]\n")


def show_error(exc: Exception) -> None:
    """Tampilkan error misi tanpa menutup program."""
    console.print(f"[bold red]Misi gagal:[/bold red] {escape(f'{type(exc).__name__}: {exc}')}\n")


def show_goodbye() -> None:
    """Tampilkan pesan keluar."""
    console.print("\n[dim]Keluar.[/dim]")
