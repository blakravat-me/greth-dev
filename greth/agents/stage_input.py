"""Render input tiap stage sebagai markdown sesuai kontrak."""

from greth import history
from greth.config import settings
from greth.state import MissionState, current_strategy
from tools.add_strategy.schema import Strategy


def _text(value: str) -> str:
    """Teks atau '-' jika kosong."""
    return value.strip() or "-"


def _clip(value: str) -> str:
    """Pangkas dari depan; bukti terbaru lebih penting."""
    if len(value) <= settings.result_limit:
        return _text(value)
    return "...(dipotong)\n" + value[-settings.result_limit :]


def _current(strategy: Strategy, *, with_fallback: bool) -> str:
    """Blok Current Strategy."""
    lines = [f"Type: {strategy.type}", f"Strategy: {strategy.strategy}", f"Reason: {strategy.reason}"]
    if with_fallback:
        lines.append(f"Fallback: {strategy.fallback}")
    return "\n".join(lines)


def _last(strategy: Strategy | None) -> str:
    """Blok Last Strategy."""
    return "-" if strategy is None else f"[{strategy.type}] {strategy.strategy}"


def _sections(*parts: tuple[str, str]) -> str:
    """Gabungkan bagian menjadi dokumen markdown."""
    return "\n\n".join(f"## {title}\n{body}" for title, body in parts)


def leader_input(state: MissionState) -> str:
    """Input stage Leader."""
    return _sections(
        ("Last Mission", _text(state["last_mission"])),
        ("Current Mission", state["mission"]),
        ("History", history.render(state["history"])),
        ("Last Feedback", _text(state["feedback"])),
    )


def operator_input(state: MissionState) -> str:
    """Input stage Operator."""
    return _sections(
        ("Current Mission", state["mission"]),
        ("Current Strategy", _current(current_strategy(state), with_fallback=False)),
        ("Last Strategy", _last(state["last_strategy"])),
        ("Last Result", _clip(state["last_result"])),
        ("Last Feedback", _text(state["feedback"])),
    )


def evaluator_input(state: MissionState) -> str:
    """Input stage Evaluator."""
    return _sections(
        ("Current Mission", state["mission"]),
        ("Current Strategy", _current(current_strategy(state), with_fallback=True)),
        ("Last Strategy", _last(state["last_strategy"])),
        ("Current Strategy Result", _clip("\n".join(state["runs"]))),
    )
