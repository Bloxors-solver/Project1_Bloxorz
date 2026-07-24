from game import Board


def h1(node, problem):
    # Manhattan distance
    block, board_layout = node.state
    board = Board(problem.level_name)
    pos1 = (block.x1, block.y1)
    pos2 = (block.x2, block.y2)
    goal = board.level.goal

    dist1 = abs(pos1[0] - goal[0]) + abs(pos1[1] - goal[1])
    dist2 = abs(pos2[0] - goal[0]) + abs(pos2[1] - goal[1])

    return min(dist1, dist2)


def h2(node, problem):
    block, board_layout = node.state
    pos1 = (block.x1, block.y1)
    pos2 = (block.x2, block.y2)

    distance = h1(node, problem)
    if pos1 not in problem.goal_island or pos2 not in problem.goal_island:
        return distance + 1000
    return distance
