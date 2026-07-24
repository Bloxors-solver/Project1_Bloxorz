from __future__ import annotations

from math import ceil

from .node import Node
from .problem import Problem


def _minimum_manhattan_distance(
    node: Node,
    problem: Problem,
) -> int:
    goal_row, goal_col = problem.goal

    return min(
        abs(row - goal_row) + abs(col - goal_col)
        for row, col in node.state.positions
    )


def h1(node: Node, problem: Problem) -> int:
    """
    Admissible distance heuristic.

    In normal mode, one roll can move part of the block by at most
    two grid cells, so Manhattan distance is divided by two.

    In split mode, one cube moves only one cell per action.
    """
    distance = _minimum_manhattan_distance(
        node,
        problem,
    )

    if node.state.is_split:
        return distance

    return ceil(distance / 2)


def h2(node: Node, problem: Problem) -> int:
    """
    Orientation-aware lower bound.

    A state that is not upright cannot already be a goal state,
    therefore it requires at least one additional action.
    """
    base_distance = h1(node, problem)

    if node.state.orientation != "upright":
        return max(base_distance, 1)

    return base_distance