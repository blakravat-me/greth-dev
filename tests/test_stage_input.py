"""Tes rendering markdown tiap stage: tanggal, status OK/FAIL, Next Strategy."""

from greth.agents.stage_input import evaluator_input, leader_input, operator_input
from greth.session import Session
from greth.state import LastStrategy
from tools.add_strategy.schema import Strategy


def strategy(**over: object) -> Strategy:
    base = {"type": "RECON", "strategy": "cari fakta", "reason": "r", "fallback": "f", "date": "2026-01-01T00:00:00+00:00"}
    base.update(over)
    return Strategy(**base)


def test_leader_input_has_mission_date_and_history_status() -> None:
    session = Session()
    state = session.begin("misi uji")
    state["history"] = [{"strategy": "s1", "status": "OK", "observed": "obs", "date": "2026-01-01T00:00:00+00:00"}]
    state["feedback"] = "perbaiki X"

    text = leader_input(state)

    assert f"## Current Mission\nmisi uji\nDate: {state['mission_date']}" in text
    assert "## History\n1. [OK] Strategy: s1 | Observed: obs (2026-01-01T00:00:00+00:00)" in text
    assert "## Last Feedback\nperbaiki X" in text


def test_leader_input_empty_history_and_feedback() -> None:
    state = Session().begin("m")
    text = leader_input(state)
    assert "## History\n-" in text
    assert "## Last Feedback\n-" in text


def test_operator_input_no_fallback_and_last_strategy_status() -> None:
    state = Session().begin("m")
    state["strategy"] = strategy(type="EXPLOIT", strategy="current")
    state["last_strategy"] = LastStrategy(strategy=strategy(type="RECON", strategy="before"), status="FAIL")
    state["last_result"] = "hasil kemarin"

    text = operator_input(state)

    assert "## Current Strategy\nType: EXPLOIT\nStrategy: current\nReason: r\nDate: 2026-01-01T00:00:00+00:00" in text
    assert "Fallback" not in text.split("## Last Result")[0].split("## Current Strategy\n")[1]
    assert "## Last Strategy (FAIL)\nType: RECON\nStrategy: before" in text
    assert "## Last Result\nhasil kemarin" in text


def test_operator_input_no_last_strategy_yet() -> None:
    state = Session().begin("m")
    state["strategy"] = strategy()
    text = operator_input(state)
    assert "## Last Strategy\n-" in text


def test_evaluator_input_has_fallback_and_next_strategy_peek() -> None:
    state = Session().begin("m")
    state["strategy"] = strategy(type="EXPLOIT", strategy="current", fallback="plan B")
    state["queue"] = [strategy(type="POST-EXPLOIT", strategy="berikutnya", fallback="plan C")]
    state["runs"] = ["[internet_search] {...}"]

    text = evaluator_input(state)

    assert "## Current Strategy\nType: EXPLOIT\nStrategy: current\nReason: r\nFallback: plan B\nDate:" in text
    assert "## Next Strategy\nType: POST-EXPLOIT\nStrategy: berikutnya\nReason: r\nFallback: plan C\nDate:" in text
    assert "## Current Strategy Result\n[internet_search] {...}" in text


def test_evaluator_input_no_next_strategy() -> None:
    state = Session().begin("m")
    state["strategy"] = strategy()
    text = evaluator_input(state)
    assert "## Next Strategy\n-" in text
