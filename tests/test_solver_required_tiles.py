import unittest

from game.block import Block
from game.board import Board
from game.levels import levels
from search_algorithms import (
    Problem,
    breadth_first_search,
    run_search,
)


TEST_LEVEL_NAME = "TEST_PERMANENT_SOLVER"


class RequiredTileSolverTests(unittest.TestCase):
    """
    End-to-end checks for advanced tiles that existing playable levels
    do not necessarily force every solver to use.
    """

    @classmethod
    def setUpClass(cls):
        cls.previous_level = levels.get(
            TEST_LEVEL_NAME
        )

        # A one-cell-wide corridor forces the block to stand on the
        # permanent/one-time heavy switch at (2, 5).
        #
        # Start (2, 2):
        # right -> lying on (2, 3), (2, 4)
        # right -> upright on switch (2, 5)
        # right -> lying on (2, 6), (2, 7)
        # right -> upright on goal (2, 8)
        levels[TEST_LEVEL_NAME] = {
            "layout": [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1],
                [-1, -1,  0,  0,  0,  6,  0,  0,  7, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            ],
            "start": (2, 2),
            "goal": (2, 8),
            "button": {
                (2, 5): [
                    True,
                    ((1, 5),),
                ],
            },
        }

    @classmethod
    def tearDownClass(cls):
        if cls.previous_level is None:
            levels.pop(
                TEST_LEVEL_NAME,
                None,
            )
        else:
            levels[TEST_LEVEL_NAME] = (
                cls.previous_level
            )

    @staticmethod
    def solve(level_name):
        board = Board(level_name)
        block = Block(*board.level.start)
        board.refresh_layout(block)

        problem = Problem(block, board)
        result = run_search(
            "BFS",
            breadth_first_search,
            problem,
        )

        state = problem.initial
        states = [state]

        for action in result.actions:
            state = problem.result(
                state,
                action,
            )
            states.append(state)

        return problem, result, states

    def test_bfs_is_forced_to_cross_fragile_tiles_safely(self):
        problem, result, states = self.solve(
            "LEVEL2"
        )

        self.assertTrue(result.solved)
        self.assertTrue(
            problem.is_goal(states[-1])
        )

        fragile_states = []

        for state in states:
            occupied_fragile = any(
                levels["LEVEL2"]["layout"][row][column]
                == 3
                for row, column in state.positions
            )

            if occupied_fragile:
                fragile_states.append(state)

        self.assertTrue(
            fragile_states,
            "The solution never crossed a fragile tile.",
        )

        self.assertTrue(
            all(
                state.orientation != "upright"
                for state in fragile_states
            ),
            (
                "A valid solution must distribute the block's "
                "weight while crossing fragile tiles."
            ),
        )

    def test_bfs_is_forced_to_activate_permanent_switch(self):
        problem, result, states = self.solve(
            TEST_LEVEL_NAME
        )

        self.assertTrue(result.solved)
        self.assertEqual(
            result.actions,
            (
                "right",
                "right",
                "right",
                "right",
            ),
        )
        self.assertTrue(
            problem.is_goal(states[-1])
        )

        activated_states = [
            state
            for state in states
            if "switch-2-5"
            in state.used_switches
        ]

        self.assertTrue(
            activated_states,
            (
                "The solver reached the goal without recording "
                "the permanent switch."
            ),
        )

        self.assertTrue(
            all(
                state.bridge_states == (False,)
                for state in activated_states
            )
        )

        self.assertIn(
            "switch-2-5",
            states[-1].used_switches,
        )
        self.assertEqual(
            states[-1].bridge_states,
            (False,),
        )


if __name__ == "__main__":
    unittest.main()