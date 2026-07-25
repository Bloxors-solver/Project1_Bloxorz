from __future__ import annotations

from collections import defaultdict, deque
from functools import lru_cache
from math import ceil

from game.levels import levels

from .node import Node
from .problem import Problem


Position = tuple[int, int]


@lru_cache(maxsize=None)
def _relaxed_goal_distances(
    level_name: str,
) -> dict[Position, int]:
    """
    Compute point-object distances to the goal on a relaxed level graph.

    Relaxation rules:
    - Ignore block orientation and fragile restrictions.
    - Treat hidden/closed bridge cells as traversable.
    - Keep void cells blocked.
    - Add a one-step directed edge from each split switch to each teleport
      destination.

    Ignoring constraints can only shorten a path, so the resulting distance
    is a lower bound. Teleport edges are included so split switches cannot
    make the heuristic overestimate the true remaining cost.
    """
    level_data = levels[level_name]
    layout = level_data["layout"]

    passable = {
        (row, column)
        for row, line in enumerate(layout)
        for column, tile in enumerate(line)
        if tile != -1
    }

    reverse_edges: dict[
        Position,
        list[Position],
    ] = defaultdict(list)

    for row, column in passable:
        for row_delta, column_delta in (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ):
            neighbour = (
                row + row_delta,
                column + column_delta,
            )

            if neighbour in passable:
                reverse_edges[neighbour].append(
                    (row, column)
                )

    for switch_position, destinations in (
        level_data.get(
            "split_switches",
            {},
        ).items()
    ):
        if switch_position not in passable:
            continue

        for destination in destinations:
            if destination in passable:
                reverse_edges[destination].append(
                    switch_position
                )

    goal = level_data["goal"]
    distances: dict[Position, int] = {
        goal: 0,
    }
    frontier = deque([goal])

    while frontier:
        current = frontier.popleft()
        next_distance = distances[current] + 1

        for predecessor in reverse_edges[current]:
            if predecessor in distances:
                continue

            distances[predecessor] = next_distance
            frontier.append(predecessor)

    return distances


def _minimum_relaxed_distance(
    node: Node,
    problem: Problem,
) -> int:
    distances = _relaxed_goal_distances(
        problem.level_name
    )

    reachable_distances = [
        distances[position]
        for position in node.state.positions
        if position in distances
    ]

    if not reachable_distances:
        # Zero is always a safe lower bound if the relaxed graph cannot
        # connect an occupied position to the goal.
        return 0

    return min(reachable_distances)


def h1(node: Node, problem: Problem) -> int:
    """
    Admissible and consistent relaxed-distance heuristic.

    One normal roll can change an occupied cell by at most two grid edges,
    so the relaxed point distance is divided by two and rounded upward.
    Split-cube moves travel only one cell, but the same division is retained
    as a conservative lower bound. Every real action costs at least 1.
    """
    return ceil(
        _minimum_relaxed_distance(
            node,
            problem,
        )
        / 2
    )


def h2(node: Node, problem: Problem) -> int:
    """
    Orientation-aware lower bound.

    A non-upright state cannot already satisfy the goal test, so at least one
    more action is required. Taking the maximum with one preserves the lower
    bound and remains consistent with the positive cost model.
    """
    base_distance = h1(node, problem)

    if node.state.orientation != "upright":
        return max(base_distance, 1)

    return base_distance
