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
