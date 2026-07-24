from collections import deque

from .expand import expand
from .node import Node


def depth_first_search(problem):
    root = Node(problem.initial)

    frontier = deque([root])
    reached = set()

    while frontier:
        node = frontier.pop()

        if problem.is_goal(node.state):
            return node

        if node.state in reached:
            continue

        reached.add(node.state)

        # Reversed so DFS explores actions according to the same
        # visible order: up, down, left, right.
        children = expand(problem, node)

        for child in reversed(children):
            if child.state not in reached:
                frontier.append(child)

    return None