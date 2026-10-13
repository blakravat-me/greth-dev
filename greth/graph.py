"""Perakitan graph: Leader -> Operator -> Evaluator."""

from collections.abc import Mapping

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from greth.agents.evaluator import make_evaluator
from greth.agents.leader import make_leader
from greth.agents.operator import make_operator
from greth.reporter import Reporter
from greth.routing import after_evaluator, after_leader
from greth.state import MissionState
from greth.types import AgentName


def build_graph(models: Mapping[AgentName, BaseChatModel], reporter: Reporter) -> CompiledStateGraph:
    """Rakit dan compile graph misi."""
    graph = StateGraph(MissionState)
    graph.add_node("leader", make_leader(models["leader"], reporter))
    graph.add_node("operator", make_operator(models["operator"], reporter))
    graph.add_node("evaluator", make_evaluator(models["evaluator"], reporter))

    graph.add_edge(START, "leader")
    graph.add_conditional_edges("leader", after_leader, {"operator": "operator", END: END})
    graph.add_edge("operator", "evaluator")
    graph.add_conditional_edges("evaluator", after_evaluator, {"leader": "leader", "operator": "operator"})
    return graph.compile()
