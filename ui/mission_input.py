"""Input misi dari pengguna (async)."""

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Dimension, HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea

PROMPT = "⟩ "
HELPER_TEXT = "ENTER: new line | CTRL+ENTER: submit | ESC: cancel | CTRL+C: exit"
MIN_LINES = 1
MAX_LINES = 5

_CONTINUATION = " " * len(PROMPT)

# Terminal yang mendukung CSI-u / modifyOtherKeys (kitty, WezTerm, dll.)
# mengirim urutan khusus untuk Ctrl+Enter; petakan ke Ctrl+J (submit).
for _seq in ("\x1b[13;5u", "\x1b[27;5;13~"):
    ANSI_SEQUENCES.setdefault(_seq, Keys.ControlJ)

_STYLE = Style.from_dict(
    {
        "rule": "ansibrightblack",
        "prefix": "bold red",
        "helper": "ansibrightblack",
    }
)


def _line_prefix(lineno: int, wrap_count: int) -> StyleAndTextTuples:
    """Prefix merah di baris pertama; baris lanjutan/wrap hanya spasi."""
    if lineno == 0 and wrap_count == 0:
        return [("class:prefix", PROMPT)]
    return [("", _CONTINUATION)]


def _build_bindings() -> KeyBindings:
    kb = KeyBindings()
    buffer_empty = Condition(lambda: not get_app().current_buffer.text)

    @kb.add("enter")
    def _newline(event: KeyPressEvent) -> None:
        event.current_buffer.insert_text("\n")

    @kb.add("c-j", eager=True)  # Ctrl+Enter (jika terdeteksi) / Ctrl+J
    @kb.add("escape", "enter")  # Alt+Enter, cadangan yang andal
    def _submit(event: KeyPressEvent) -> None:
        event.app.exit(result=event.current_buffer.text)

    @kb.add("c-c")
    def _interrupt(event: KeyPressEvent) -> None:
        event.app.exit(exception=KeyboardInterrupt)

    @kb.add("c-d", filter=buffer_empty)
    def _eof(event: KeyPressEvent) -> None:
        event.app.exit(exception=EOFError)

    return kb


def _build_app(helper_text: str) -> Application[str]:
    rule = Window(height=1, char="─", style="class:rule")
    editor = TextArea(
        multiline=True,
        wrap_lines=True,
        height=Dimension(min=MIN_LINES, max=MAX_LINES),
        dont_extend_height=True,
        get_line_prefix=_line_prefix,
    )
    helper = Window(
        FormattedTextControl([("class:helper", helper_text)]),
        height=1,
    )
    return Application(
        layout=Layout(HSplit([rule, editor, rule, helper]), focused_element=editor),
        key_bindings=_build_bindings(),
        style=_STYLE,
        full_screen=False,
        erase_when_done=True,  # UI dihapus dari terminal saat submit/keluar
    )


async def ask_mission(helper_text: str = HELPER_TEXT) -> str:
    """Baca satu misi; Ctrl+C atau Ctrl+D (saat kosong) memunculkan exception keluar."""
    return (await _build_app(helper_text).run_async()).strip()
