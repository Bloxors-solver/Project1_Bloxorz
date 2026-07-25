from .node import Node


def expand(problem, node):
    s = node.state
    # Keep successor order deterministic (up, down, left, right as returned by
    # Problem.actions). A set made BFS/DFS traversal order vary between runs.
    generated_nodes = []

    for action in problem.actions(s):
        s_prime = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s_prime)
        depth = node.depth + 1
        generated_nodes.append(
            Node(s_prime, parent=node, action=action, path_cost=cost, depth=depth)
        )

    return generated_nodes
