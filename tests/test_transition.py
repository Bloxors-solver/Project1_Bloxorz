import unittest

from game.block import Block
from game.board import Board
from game.state import GameState
from game.state_adapter import block_to_state
from game.transition import (
    available_actions,
    is_goal_state,
    move_geometry,
    transition,
)


class TransitionTests(unittest.TestCase):

    def setUp(self):
        self.level_name = "LEVEL1"
        self.board = Board(self.level_name)

        start_row, start_col = self.board.level.start
        self.block = Block(start_row, start_col)

        self.initial_state = block_to_state(
            self.block,
            self.board,
        )

    def test_move_geometry_from_upright_to_horizontal(self):
        next_state = move_geometry(
            self.initial_state,
            "right",
        )

        self.assertEqual(
            next_state.orientation,
            "horizontal",
        )
        self.assertEqual(
            next_state.positions,
            ((4, 5), (4, 6)),
        )

    def test_move_geometry_does_not_change_original_state(self):
        original = self.initial_state

        move_geometry(original, "right")

        self.assertEqual(
            original.orientation,
            "upright",
        )
        self.assertEqual(
            original.positions,
            ((4, 4),),
        )

    def test_valid_transition(self):
        next_state = transition(
            self.initial_state,
            "right",
            self.level_name,
        )

        self.assertIsNotNone(next_state)
        self.assertEqual(
            next_state.orientation,
            "horizontal",
        )
        self.assertEqual(
            next_state.positions,
            ((4, 5), (4, 6)),
        )

    def test_illegal_transition_returns_none(self):
        # Moving upward from LEVEL1's starting position falls into void.
        next_state = transition(
            self.initial_state,
            "up",
            self.level_name,
        )

        self.assertIsNone(next_state)

    def test_available_actions_are_deterministic(self):
        actions = available_actions(
            self.initial_state,
            self.level_name,
        )

        self.assertEqual(
            actions,
            ["down", "right"],
        )

    def test_goal_requires_upright_block(self):
        goal = self.board.level.goal

        state = GameState(
            mode="normal",
            positions=(goal,),
            orientation="upright",
        )

        self.assertTrue(
            is_goal_state(state, self.level_name)
        )

    def test_lying_on_goal_does_not_win(self):
        goal_row, goal_col = self.board.level.goal

        state = GameState(
            mode="normal",
            positions=(
                (goal_row, goal_col),
                (goal_row, goal_col + 1),
            ),
            orientation="horizontal",
        )

        self.assertFalse(
            is_goal_state(state, self.level_name)
        )

    def test_split_cube_cannot_win(self):
        state = GameState(
            mode="split",
            positions=((7, 10), (7, 11)),
            orientation="split",
            active_cube=0,
        )

        self.assertFalse(
            is_goal_state(state, self.level_name)
        )

    def test_invalid_action_raises_error(self):
        with self.assertRaises(ValueError):
            move_geometry(
                self.initial_state,
                "jump",
            )


if __name__ == "__main__":
    unittest.main()