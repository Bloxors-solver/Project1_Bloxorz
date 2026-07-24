import unittest

from game.board import Board
from game.state import GameState
from game.state_adapter import bridge_states_from_board
from game.transition import (
    available_actions,
    transition,
)


class SplitTransitionTests(unittest.TestCase):

    def test_switch_action_changes_active_cube(self):
        state = GameState(
            mode="split",
            positions=((2, 2), (2, 13)),
            orientation="split",
            active_cube=0,
        )

        result = transition(
            state,
            "switch",
            "LEVEL8",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.active_cube, 1)
        self.assertEqual(
            result.positions,
            state.positions,
        )

    def test_switch_is_available_for_split_state(self):
        state = GameState(
            mode="split",
            positions=((2, 2), (2, 13)),
            orientation="split",
        )

        actions = available_actions(
            state,
            "LEVEL8",
        )

        self.assertIn("switch", actions)

    def test_cube_cannot_move_into_void(self):
        state = GameState(
            mode="split",
            positions=((2, 2), (2, 13)),
            orientation="split",
            active_cube=0,
        )

        # LEVEL8 cell (2, 1) is void.
        result = transition(
            state,
            "left",
            "LEVEL8",
        )

        self.assertIsNone(result)

    def test_cube_can_stand_on_fragile_tile(self):
        state = GameState(
            mode="split",
            positions=((2, 4), (2, 13)),
            orientation="split",
            active_cube=0,
        )

        # LEVEL8 cell (2, 5) is a fragile/glass tile.
        result = transition(
            state,
            "right",
            "LEVEL8",
        )

        self.assertIsNotNone(result)
        self.assertTrue(result.is_split)
        self.assertEqual(
            result.positions[0],
            (2, 5),
        )

    def test_soft_switch_is_activated_by_single_cube(self):
        board = Board("LEVEL4")

        bridge_states = bridge_states_from_board(
            board
        )

        state = GameState(
            mode="split",
            positions=((3, 9), (3, 15)),
            orientation="split",
            bridge_states=bridge_states,
            active_cube=0,
        )

        # LEVEL4 cell (3, 10) is a hexagonal soft switch.
        result = transition(
            state,
            "right",
            "LEVEL4",
        )

        self.assertIsNotNone(result)
        self.assertNotEqual(
            result.bridge_states,
            bridge_states,
        )

    def test_heavy_switch_is_not_activated_by_cube(self):
        board = Board("LEVEL7")

        bridge_states = bridge_states_from_board(
            board
        )

        state = GameState(
            mode="split",
            positions=((4, 7), (8, 4)),
            orientation="split",
            bridge_states=bridge_states,
            active_cube=0,
        )

        # LEVEL7 cell (4, 8) is a heavy X switch.
        result = transition(
            state,
            "right",
            "LEVEL7",
        )

        self.assertIsNotNone(result)
        self.assertEqual(
            result.bridge_states,
            bridge_states,
        )

    def test_split_move_can_merge_on_board(self):
        state = GameState(
            mode="split",
            positions=((2, 3), (2, 5)),
            orientation="split",
            active_cube=0,
        )

        result = transition(
            state,
            "right",
            "LEVEL8",
        )

        self.assertIsNotNone(result)
        self.assertFalse(result.is_split)
        self.assertEqual(
            result.orientation,
            "horizontal",
        )
        self.assertEqual(
            result.positions,
            ((2, 4), (2, 5)),
        )

    def test_split_cube_cannot_complete_goal(self):
        board = Board("LEVEL8")

        state = GameState(
            mode="split",
            positions=(board.level.goal, (2, 13)),
            orientation="split",
        )

        from game.transition import is_goal_state

        self.assertFalse(
            is_goal_state(state, "LEVEL8")
        )

    def test_normal_block_cannot_use_switch_action(self):
        state = GameState(
            mode="normal",
            positions=((4, 4),),
            orientation="upright",
        )

        with self.assertRaises(ValueError):
            transition(
                state,
                "switch",
                "LEVEL1",
            )


if __name__ == "__main__":
    unittest.main()