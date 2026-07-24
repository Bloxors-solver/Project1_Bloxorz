from collections import deque
from .expand import expand
from .node import Node


def depth_first_search(problem):
    node = Node(problem.initial)
    frontier = deque([node])
    reached = set()

    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node

        if node not in reached:
            reached.add(node)
            for child in expand(problem, node):
                frontier.append(child)

    return None
