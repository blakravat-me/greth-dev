"""Tipe dasar bersama tanpa dependensi internal."""

from typing import Literal, get_args

AgentName = Literal["leader", "operator", "evaluator"]
AGENTS: tuple[AgentName, ...] = get_args(AgentName)
