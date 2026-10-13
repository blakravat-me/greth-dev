"""Pemantau tombol ESC selama misi berjalan (tanpa thread)."""

import asyncio
import os
import sys
from collections.abc import Callable
from types import TracebackType

_ESC = b"\x1b"


class EscWatcher:
    """Context manager: panggil on_esc saat ESC tunggal ditekan."""

    def __init__(self, on_esc: Callable[[], None]) -> None:
        self._on_esc = on_esc
        self.pressed = False
        self._stop: Callable[[], None] | None = None

    def __enter__(self) -> "EscWatcher":
        if sys.stdin.isatty():
            start = self._start_windows if sys.platform == "win32" else self._start_posix
            self._stop = start()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        if self._stop is not None:
            self._stop()

    def _fire(self) -> None:
        """Picu on_esc sekali saja."""
        if not self.pressed:
            self.pressed = True
            self._on_esc()

    def _start_posix(self) -> Callable[[], None]:
        """Mode cbreak + add_reader; Ctrl+C tetap berfungsi."""
        import termios
        import tty

        fd = sys.stdin.fileno()
        saved = termios.tcgetattr(fd)
        loop = asyncio.get_running_loop()
        tty.setcbreak(fd)
        loop.add_reader(fd, self._read, fd)

        def stop() -> None:
            loop.remove_reader(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, saved)

        return stop

    def _read(self, fd: int) -> None:
        """Baca byte; ESC tunggal berbeda dari urutan escape (panah, dll)."""
        if os.read(fd, 64) == _ESC:
            self._fire()

    def _start_windows(self) -> Callable[[], None]:
        """Polling msvcrt sebagai task asyncio."""
        import msvcrt

        async def poll() -> None:
            while True:
                if msvcrt.kbhit() and msvcrt.getwch() == "\x1b":
                    self._fire()
                await asyncio.sleep(0.05)

        task = asyncio.get_running_loop().create_task(poll())
        return task.cancel
