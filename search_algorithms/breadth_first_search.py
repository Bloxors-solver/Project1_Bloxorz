from collections import deque
from .node import Node
from .expand import expand


def breadth_first_search(problem):
    node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node

    frontier = deque([node])
    reached = {problem.initial: node}

    while frontier:
        node = frontier.popleft()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                return child

            if s not in reached:
                reached[s] = child
                frontier.append(child)

    return None


'''
def breadth_first_search(problem) return solution node or failure
    node <- NODE(problem.INITIAL)
    if problem.IS_GOAL(node.state) return node
    frontier <- FIFO queue, with node as an element
    reached <- {problem.INITIAL}
    while frontier:
        node <- POP(frontier)
        for child in EXPAND(problem, node)
            s <- child.STATE
            if problem.IS_GOAL(s) return child
            if s not in reached
                add s to reached
                add child to frontier
'''
