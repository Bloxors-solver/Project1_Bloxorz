import heapq
from .expand import expand
from .heuristic import h1
from .node import Node


def greedy_search(problem):
    node = Node(problem.initial)
    frontier = [(h1(node, problem), node)]
    reached = {problem.initial: node}

    while frontier:
        node = heapq.heappop(frontier)[1]
        if problem.is_goal(node.state):
            return node

        for child in expand(problem, node):
            s = child.state
            if s not in reached or h1(child, problem) < h1(reached[s], problem):
                reached[s] = child
                heapq.heappush(frontier, (h1(child, problem), child))

    return None

