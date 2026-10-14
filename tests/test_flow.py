"""Tes alur graph dengan satu model skrip (tanpa Ollama dan tanpa jaringan)."""

from typing import Any

import pytest
from langchain.messages import AIMessage

import tools.internet_search.tool as search_tool
from greth.graph import build_graph
from greth.session import Session
from tests.conftest import ScriptedModel, call, calls


class FakeDDGS:
    """Hasil pencarian palsu, deterministik."""

    def text(self, query: str, max_results: int) -> list[dict[str, str]]:
        return [{"href": "https://x.test", "title": "T", "body": "isi"}]


class Recorder:
    """Reporter yang merekam event."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self.outputs: list[str] = []

    def strategy(self, item: Any) -> None:
        self.events.append(f"strategy:{item.type}:{item.strategy}")

    def output(self, item: Any) -> None:
        self.events.append("output")
        self.outputs.append(item.body)

    def evaluation(self, item: Any) -> None:
        self.events.append(f"evaluation:{item.success}:{item.next}:{item.to_leader}")

    def completed(self, item: Any) -> None:
        self.events.append("completed")


def strategy_call(name: str = "cari fakta", kind: str = "RECON") -> AIMessage:
    return call("add_strategy", type=kind, strategy=name, reason="r", fallback="f")


def search(displaying: bool = False) -> AIMessage:
    return call("internet_search", search="a", displaying=displaying)


def evaluate_call(*, success: bool, next: bool, to_leader: bool) -> AIMessage:  # noqa: A002
    return call("evaluate", observed="obs", feedback="fb", success=success, next=next, to_leader=to_leader)


@pytest.fixture(autouse=True)
def fake_ddgs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_tool, "DDGS", FakeDDGS)


async def run(model: ScriptedModel, session: Session, mission: str = "misi uji") -> Recorder:
    reporter = Recorder()
    graph = build_graph(model, reporter)
    async for snapshot in graph.astream(session.begin(mission), stream_mode="values"):
        session.absorb(snapshot)
    return reporter


async def test_retry_then_resolve_then_complete() -> None:
    # urutan panggilan LLM: leader (ditolak), leader, operator, evaluator(retry), operator, evaluator(selesai), leader
    model = ScriptedModel(
        script=[
            AIMessage(content="halo"),
            strategy_call(),
            search(displaying=True),
            evaluate_call(success=False, next=False, to_leader=False),
            search(displaying=True),
            evaluate_call(success=True, next=True, to_leader=True),
            call("mission_completed"),
        ]
    )
    session = Session()
    reporter = await run(model, session)

    assert reporter.events == [
        "strategy:RECON:cari fakta",
        "output",
        "evaluation:False:False:False",
        "output",
        "evaluation:True:True:True",
        "completed",
    ]
    assert len(session.history) == 1
    assert session.history[0]["status"] == "OK"
    assert session.history[0]["strategy"] == "cari fakta"
    assert session.last_mission == "misi uji"


async def test_leader_multi_strategy_builds_queue_in_order() -> None:
    model = ScriptedModel(
        script=[
            calls(
                ("add_strategy", {"type": "RECON", "strategy": "s1", "reason": "r", "fallback": "f"}),
                ("add_strategy", {"type": "EXPLOIT", "strategy": "s2", "reason": "r", "fallback": "f"}),
                ("add_strategy", {"type": "REPORT", "strategy": "s3", "reason": "r", "fallback": "f"}),
            ),
            search(),
            evaluate_call(success=True, next=True, to_leader=False),  # -> lanjut ke s2 (queue, bukan leader)
            search(),
            evaluate_call(success=True, next=True, to_leader=False),  # -> lanjut ke s3
            search(),
            evaluate_call(success=True, next=True, to_leader=False),  # queue habis -> dipaksa to_leader
            call("mission_completed"),
        ]
    )
    reporter = await run(model, Session())

    assert [e for e in reporter.events if e.startswith("strategy:")] == [
        "strategy:RECON:s1",
        "strategy:EXPLOIT:s2",
        "strategy:REPORT:s3",
    ]
    assert reporter.events[-1] == "completed"


async def test_evaluator_to_leader_closes_current_and_clears_queue() -> None:
    model = ScriptedModel(
        script=[
            calls(
                ("add_strategy", {"type": "RECON", "strategy": "s1", "reason": "r", "fallback": "f"}),
                ("add_strategy", {"type": "EXPLOIT", "strategy": "s2", "reason": "r", "fallback": "f"}),
            ),
            search(),
            evaluate_call(success=False, next=False, to_leader=True),  # minta kembali ke leader lebih awal
            call("mission_completed"),
        ]
    )
    reporter = await run(model, Session())

    assert reporter.events == [
        "strategy:RECON:s1",
        "strategy:EXPLOIT:s2",
        "evaluation:False:False:True",
        "completed",
    ]


async def test_attempts_exhausted_forces_resolution_without_deadlock() -> None:
    model = ScriptedModel(
        script=[
            strategy_call(),
            *[search(), evaluate_call(success=False, next=False, to_leader=False)] * 3,
            call("mission_completed"),
        ]
    )
    session = Session()
    reporter = await run(model, session)

    assert reporter.events.count("evaluation:False:False:False") == 3
    assert reporter.outputs == []  # displaying default False
    assert session.history[0]["status"] == "FAIL"


async def test_history_carries_over_between_missions() -> None:
    session = Session()
    for mission in ("satu", "dua"):
        model = ScriptedModel(
            script=[strategy_call(), search(), evaluate_call(success=True, next=True, to_leader=True), call("mission_completed")]
        )
        await run(model, session, mission)
    assert len(session.history) == 2
    assert session.last_mission == "dua"


async def test_leader_mixed_calls_rejected_then_retried() -> None:
    model = ScriptedModel(
        script=[
            calls(
                ("add_strategy", {"type": "RECON", "strategy": "s1", "reason": "r", "fallback": "f"}),
                ("mission_completed", {}),
            ),
            call("mission_completed"),
        ]
    )
    reporter = await run(model, Session())
    assert reporter.events == ["completed"]


async def test_agent_cannot_use_foreign_tool() -> None:
    # Leader mencoba memakai tool milik Operator, lalu diperbaiki
    model = ScriptedModel(script=[search(), call("mission_completed")])
    reporter = await run(model, Session())
    assert reporter.events == ["completed"]


async def test_every_llm_input_is_stamped_with_current_date() -> None:
    model = ScriptedModel(
        script=[
            AIMessage(content="halo"),
            strategy_call(),
            search(),
            evaluate_call(success=True, next=True, to_leader=True),
            call("mission_completed"),
        ]
    )
    await run(model, Session())

    assert len(model.seen) == 5
    for messages in model.seen:
        humans = [m for m in messages if type(m).__name__ == "HumanMessage"]
        assert humans, "setiap panggilan LLM harus membawa input pengguna"
        assert all(str(m.content).startswith("Current date: 20") for m in humans)
