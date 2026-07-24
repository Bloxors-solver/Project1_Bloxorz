from copy import deepcopy
from game import Board
from game import GameLogic


class Problem:
    def __init__(self, block, board, layout_only=False):
        self.layout_only = layout_only
        if layout_only:
            self.initial = (block, tuple(map(tuple, board.level.layout)))
        else:
            self.initial = (block, board)
        self.level_name = board.level.level_name
        self.goal_island = self._find_goal_island(board)

    def actions(self, state):
        valid_actions = []
        '''
        print("|||||||||||||||Current state||||||||||||||||||")
        pprint(state)
        '''
        for action in ["up", "down", "left", "right"]:
            ghost_block = deepcopy(state[0])
            ghost_block.move(action)
            if self.layout_only:
                ghost_board = Board(self.level_name)
            else:
                ghost_board = deepcopy(state[1])
            ghost_game_logic = GameLogic(ghost_block, ghost_board)
            '''
            print("~~~~ACTION~~~~: ", action)
            print("GHOST: ", ghost_block)
            print("CURR STATE: ", state[0])
            print("~~~~~~~~~~~~~~")
            '''

            if not ghost_game_logic.check_lose():
                valid_actions.append(action)

        '''
        print("Valid actions:", valid_actions)
        print("||||||||||||||||||||||||||||||||||||||||||||||")
        '''
        return valid_actions

    def result(self, state, action):
        block = deepcopy(state[0])
        block.move(action)
        if self.layout_only:
            board = Board(self.level_name)
            board.refresh_layout(block)
            return (block, tuple(map(tuple, board.level.layout)))
        else:
            board = deepcopy(state[1])
            board.refresh_layout(block)
            return (block, board)

    def action_cost(self, state, action, next_state):
        return 1

    def is_goal(self, state):
        block = deepcopy(state[0])
        board = Board(self.level_name)
        game_logic = GameLogic(block, board)
        if game_logic.check_win():
            return True

        return False

    def _find_goal_island(self, board):
        """
        Performs a flood-fill from the goal to mark all reachable tiles
        without crossing a void. This defines the "goal island".
        """
        goal = board.level.goal
        goal_island_tiles = set()
        stack = [goal]

        while stack:
            x, y = stack.pop()
            if (x, y) in goal_island_tiles:
                continue
            # Check if tile is solid and not a void. Also, don't cross voids (implied by neighbor check).
            if board.level.get_tiletype((x, y)) in ["VOID", "HIDDEN_PATH"]:
                continue
            goal_island_tiles.add((x, y))
            # Check all 4 neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                # x indexes rows (height); y indexes columns (width).
                if 0 <= new_x < board.level.height and 0 <= new_y < board.level.width:
                    stack.append((new_x, new_y))

        return goal_island_tiles
