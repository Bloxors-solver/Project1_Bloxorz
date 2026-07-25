import heapq
from .expand import expand
from .node import Node



def uniform_cost_search(problem):
    node = Node(problem.initial)
    frontier = [node]
    reached = {problem.initial: node}

    while frontier:
        node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node

        for child in expand(problem, node):
            s = child.state
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                heapq.heappush(frontier, child)

    return None

