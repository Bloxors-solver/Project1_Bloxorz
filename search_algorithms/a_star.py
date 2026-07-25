import heapq

from .expand import expand
from .heuristic import h2
from .node import Node


def f_score(node, problem):
    """A* evaluation: accumulated path cost plus heuristic estimate."""
    return node.path_cost + h2(node, problem)


def a_star(problem):
    root = Node(problem.initial)
    frontier = [(f_score(root, problem), root)]
    best_path_cost = {
        problem.initial: root.path_cost,
    }

    while frontier:
        _, node = heapq.heappop(frontier)

        # Ignore an outdated queue entry if a cheaper route to the same state
        # was inserted after this node.
        if node.path_cost != best_path_cost.get(
            node.state
        ):
            continue

        if problem.is_goal(node.state):
            return node

        for child in expand(problem, node):
            previous_cost = best_path_cost.get(
                child.state
            )

            if (
                previous_cost is None
                or child.path_cost < previous_cost
            ):
                best_path_cost[child.state] = (
                    child.path_cost
                )
                heapq.heappush(
                    frontier,
                    (
                        f_score(child, problem),
                        child,
                    ),
                )

    return None
