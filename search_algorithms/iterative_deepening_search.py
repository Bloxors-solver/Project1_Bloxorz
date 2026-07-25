from collections import deque
from .expand import expand
from .node import Node


def depth_limited_search(problem, l):
    node = Node(problem.initial)
    frontier = deque([node])
    reached = set()
    result = None

    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        if node.depth > l:
            result = "cutoff"
        elif node not in reached:
            reached.add(node)
            for child in expand(problem, node):
                frontier.append(child)

    return result


def iterative_deepening_search(problem):
    depth = 0
    while True:
        result = depth_limited_search(problem, depth)
        if result != "cutoff":
            return result
        depth += 1

