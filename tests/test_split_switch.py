import unittest

from game.block import Block
from game.board import Board
from game.state import GameState
from game.state_adapter import block_to_state
from game.transition import transition
from search_algorithms import (
    Problem,
    a_star,
    breadth_first_search,
    run_search,
)


class SplitSwitchTests(unittest.TestCase):

    @staticmethod
    def create_initial_state():
        board = Board("LEVEL10")
        block = Block(*board.level.start)

        board.refresh_layout(block)

        return block_to_state(
            block,
            board,
        )

    def test_level_contains_split_switch(self):
        board = Board("LEVEL10")

        self.assertEqual(
            board.level.get_tiletype((3, 5)),
            "SPLIT_SWITCH",
        )

        self.assertEqual(
            board.level.split_switches[(3, 5)],
            (
                (2, 7),
                (4, 9),
            ),
        )

    def test_upright_block_activates_split_switch(self):
        state = self.create_initial_state()

        first_move = transition(
            state,
            "right",
            "LEVEL10",
        )

        self.assertIsNotNone(first_move)
        self.assertEqual(
            first_move.orientation,
            "horizontal",
        )

        result = transition(
            first_move,
            "right",
            "LEVEL10",
        )

        self.assertIsNotNone(result)
        self.assertTrue(result.is_split)

        self.assertEqual(
            result.positions,
            (
                (2, 7),
                (4, 9),
            ),
        )

        self.assertEqual(
            result.active_cube,
            0,
        )

    def test_lying_block_does_not_activate_split_switch(self):
        state = GameState(
            mode="normal",
            positions=(
                (3, 5),
                (3, 6),
            ),
            orientation="horizontal",
        )

        result = transition(
            state,
            "down",
            "LEVEL10",
        )

        self.assertIsNotNone(result)
        self.assertFalse(result.is_split)

    def test_split_state_preserves_bridge_information(self):
        state = GameState(
            mode="normal",
            positions=((3, 4),),
            orientation="upright",
            bridge_states=(),
            used_switches=frozenset(
                {"example-switch"}
            ),
        )

        result = transition(
            state,
            "right",
            "LEVEL10",
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.used_switches,
            state.used_switches,
        )

    def test_manual_solution_reaches_goal(self):
        state = self.create_initial_state()

        actions = (
            "right",
            "right",
            "down",
            "right",
            "switch",
            "up",
            "right",
        )

        for action in actions:
            state = transition(
                state,
                action,
                "LEVEL10",
            )

            self.assertIsNotNone(state)

        self.assertEqual(
            state.mode,
            "normal",
        )

        self.assertEqual(
            state.orientation,
            "upright",
        )

        self.assertEqual(
            state.positions,
            ((3, 10),),
        )

    def test_bfs_solves_split_level(self):
        board = Board("LEVEL10")
        block = Block(*board.level.start)

        board.refresh_layout(block)

        problem = Problem(
            block,
            board,
        )

        result = run_search(
            "BFS",
            breadth_first_search,
            problem,
        )

        self.assertTrue(result.solved)

        self.assertEqual(
            result.solution_length,
            7,
        )

        state = problem.initial
        entered_split_mode = False

        for action in result.actions:
            state = problem.result(
                state,
                action,
            )

            if state.is_split:
                entered_split_mode = True

        self.assertTrue(
            entered_split_mode
        )

        self.assertTrue(
            problem.is_goal(state)
        )

    def test_a_star_solves_split_level(self):
        board = Board("LEVEL10")
        block = Block(*board.level.start)

        board.refresh_layout(block)

        problem = Problem(
            block,
            board,
        )

        result = run_search(
            "A*",
            a_star,
            problem,
        )

        self.assertTrue(result.solved)

        self.assertEqual(
            result.solution_length,
            7,
        )

        state = problem.initial
        entered_split_mode = False

        for action in result.actions:
            state = problem.result(
                state,
                action,
            )

            if state.is_split:
                entered_split_mode = True

        self.assertTrue(
            entered_split_mode
        )

        self.assertTrue(
            problem.is_goal(state)
        )


if __name__ == "__main__":
    unittest.main()