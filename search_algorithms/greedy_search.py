import heapq
from .expand import expand
from .heuristic import h1, h2
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


'''
def best_first_search(problem, f):
    node <- NODE(STATE=problem.INITIAL)
    frontier <- priority queue ordered by f, with node as an element
    reached <- a lookup table, with one entry with key problem.INITIAL
                                                and value node

    while frontier:
        node <- POP(frontier)
        if problem.IS-GOAL(node.STATE) then return node
        for child in EXPAND(problem, node) do
            s <- child.STATE
            if s not in reached or child.PATH-COST < reached[s].PATH-COST
                reached[s] <- child
                add child to frontier
    return failure
'''

