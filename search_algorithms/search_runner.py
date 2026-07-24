from __future__ import annotations

import gc
import tracemalloc
from collections.abc import Callable
from time import perf_counter
from typing import TYPE_CHECKING

from .search_result import SearchResult

if TYPE_CHECKING:
    from .node import Node
    from .problem import Problem


SearchFunction = Callable[["Problem"], "Node | None"]


def reconstruct_actions(
    goal_node: Node | None,
) -> tuple[str, ...]:
    if goal_node is None:
        return ()

    actions: list[str] = []
    current = goal_node

    while current.parent is not None:
        if current.action is None:
            raise ValueError(
                "A non-root search node must contain an action."
            )

        actions.append(current.action)
        current = current.parent

    actions.reverse()
    return tuple(actions)


def run_search(
    algorithm_name: str,
    solver: SearchFunction,
    problem: Problem,
) -> SearchResult:
    """
    Execute one solver and collect standardized performance metrics.

    Memory is measured with tracemalloc, so the reported value is
    peak Python memory allocated during the search.
    """
    problem.reset_metrics()

    gc.collect()
    tracemalloc.start()

    start_time = perf_counter()

    try:
        goal_node = solver(problem)
    finally:
        elapsed_ms = (perf_counter() - start_time) * 1000

        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    actions = reconstruct_actions(goal_node)

    total_cost = (
        float(goal_node.path_cost)
        if goal_node is not None
        else float("inf")
    )

    return SearchResult(
        algorithm=algorithm_name,
        goal_node=goal_node,
        actions=actions,
        search_time_ms=elapsed_ms,
        peak_memory_mb=peak_bytes / (1024 * 1024),
        expanded_nodes=problem.expanded_nodes,
        solution_length=len(actions),
        total_cost=total_cost,
    )