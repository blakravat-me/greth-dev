"""Render input tiap stage sebagai markdown sesuai kontrak."""

from greth import history
from greth.config import settings
from greth.state import LastStrategy, MissionState, current_strategy
from tools.add_strategy.schema import Strategy


def _text(value: str) -> str:
    """Teks atau '-' jika kosong."""
    return value.strip() or "-"


def _clip(value: str) -> str:
    """Pangkas dari depan; bukti terbaru lebih penting."""
    if len(value) <= settings.result_limit:
        return _text(value)
    return "...(dipotong)\n" + value[-settings.result_limit :]


def _dated(text: str, date: str) -> str:
    """Tambahkan baris Date di bawah teks."""
    return f"{text}\nDate: {date}"


def _block(strategy: Strategy, *, with_fallback: bool) -> str:
    """Blok Type/Strategy/Reason[/Fallback]/Date untuk satu strategi."""
    lines = [f"Type: {strategy.type}", f"Strategy: {strategy.strategy}", f"Reason: {strategy.reason}"]
    if with_fallback:
        lines.append(f"Fallback: {strategy.fallback}")
    lines.append(f"Date: {strategy.date}")
    return "\n".join(lines)


def _last_section(last: LastStrategy | None, *, with_fallback: bool) -> tuple[str, str]:
    """Judul dinamis 'Last Strategy (OK/FAIL)' beserta isinya."""
    if last is None:
        return "Last Strategy", "-"
    return f"Last Strategy ({last['status']})", _block(last["strategy"], with_fallback=with_fallback)


def _sections(*parts: tuple[str, str]) -> str:
    """Gabungkan bagian menjadi dokumen markdown."""
    return "\n\n".join(f"## {title}\n{body}" for title, body in parts)


def leader_input(state: MissionState) -> str:
    """Input stage Leader."""
    return _sections(
        ("Last Mission", _text(state["last_mission"])),
        ("Current Mission", _dated(state["mission"], state["mission_date"])),
        ("History", history.render(state["history"])),
        ("Last Feedback", _text(state["feedback"])),
    )


def operator_input(state: MissionState) -> str:
    """Input stage Operator."""
    last_title, last_body = _last_section(state["last_strategy"], with_fallback=False)
    return _sections(
        ("Current Mission", _text(state["mission"])),
        ("Current Strategy", _block(current_strategy(state), with_fallback=False)),
        (last_title, last_body),
        ("Last Result", _clip(state["last_result"])),
        ("Last Feedback", _text(state["feedback"])),
    )


def evaluator_input(state: MissionState) -> str:
    """Input stage Evaluator."""
    last_title, last_body = _last_section(state["last_strategy"], with_fallback=True)
    queue = state["queue"]
    next_body = _block(queue[0], with_fallback=True) if queue else "-"
    return _sections(
        ("Current Mission", _text(state["mission"])),
        ("Current Strategy", _block(current_strategy(state), with_fallback=True)),
        (last_title, last_body),
        ("Next Strategy", next_body),
        ("Current Strategy Result", _clip("\n".join(state["runs"]))),
    )
