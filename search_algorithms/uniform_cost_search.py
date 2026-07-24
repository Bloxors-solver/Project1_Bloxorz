import heapq
from .expand import expand
from .node import Node

'''
!!!!!!!!!!!!!
Since ACTION-COST(s, action, s') = 1,
        uniform_cost_search behaves exactly like breadth_first_search
'''


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

