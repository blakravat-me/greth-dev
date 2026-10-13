"""Tes alur graph dengan model skrip (tanpa Ollama dan tanpa jaringan)."""

from typing import Any

import pytest
from langchain.messages import AIMessage

import tools.internet_search.tool as search_tool
from greth.graph import build_graph
from greth.session import Session
from tests.conftest import ScriptedModel, call


class FakeClient:
    """Klien pencarian palsu."""

    async def web_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        return [{"url": "https://x.test", "title": "T", "content": "isi"}]


class Recorder:
    """Reporter yang merekam event."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self.outputs: list[str] = []

    def strategy(self, item) -> None:
        self.events.append("strategy")

    def output(self, item) -> None:
        self.events.append("output")
        self.outputs.append(item.body)

    def evaluation(self, item) -> None:
        self.events.append(f"evaluation:{item.success}")

    def completed(self, item) -> None:
        self.events.append("completed")


def strategy_call() -> AIMessage:
    return call("add_strategy", type="recon", strategy="cari fakta", reason="r", fallback="f")


def evaluate_call(success: bool) -> AIMessage:
    return call("evaluate", observed="obs", feedback="fb", success=success)


@pytest.fixture(autouse=True)
def fake_search(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_tool, "get_client", lambda: FakeClient())


async def run(models: dict, session: Session, mission: str = "misi uji") -> Recorder:
    reporter = Recorder()
    graph = build_graph(models, reporter)
    async for snapshot in graph.astream(session.begin(mission), stream_mode="values"):
        session.absorb(snapshot)
    return reporter


async def test_retry_then_success_then_complete() -> None:
    models = {
        # respons pertama tanpa tool call harus ditolak lalu diulang
        "leader": ScriptedModel(script=[AIMessage(content="halo"), strategy_call(), call("mission_completed")]),
        "operator": ScriptedModel(script=[call("internet_search", search="a", displaying=True)] * 2),
        "evaluator": ScriptedModel(script=[evaluate_call(False), evaluate_call(True)]),
    }
    session = Session()
    reporter = await run(models, session)

    assert reporter.events == ["strategy", "output", "evaluation:False", "output", "evaluation:True", "completed"]
    assert session.history == [{"strategy": "cari fakta", "observed": "obs"}]
    assert session.last_mission == "misi uji"


async def test_attempts_exhausted_goes_back_to_leader() -> None:
    models = {
        "leader": ScriptedModel(script=[strategy_call(), call("mission_completed")]),
        "operator": ScriptedModel(script=[call("internet_search", search="a")] * 3),
        "evaluator": ScriptedModel(script=[evaluate_call(False)] * 3),
    }
    session = Session()
    reporter = await run(models, session)

    assert reporter.events.count("evaluation:False") == 3
    assert reporter.outputs == []  # displaying default False
    assert session.history[0]["observed"].startswith("GAGAL setelah 3 percobaan")


async def test_history_carries_over_between_missions() -> None:
    session = Session()
    for mission in ("satu", "dua"):
        models = {
            "leader": ScriptedModel(script=[strategy_call(), call("mission_completed")]),
            "operator": ScriptedModel(script=[call("internet_search", search="a")]),
            "evaluator": ScriptedModel(script=[evaluate_call(True)]),
        }
        await run(models, session, mission)
    assert len(session.history) == 2
    assert session.last_mission == "dua"


async def test_agent_cannot_use_foreign_tool() -> None:
    models = {
        # Leader mencoba memakai tool milik Operator, lalu diperbaiki
        "leader": ScriptedModel(script=[call("internet_search", search="x"), call("mission_completed")]),
        "operator": ScriptedModel(script=[]),
        "evaluator": ScriptedModel(script=[]),
    }
    reporter = await run(models, Session())
    assert reporter.events == ["completed"]
