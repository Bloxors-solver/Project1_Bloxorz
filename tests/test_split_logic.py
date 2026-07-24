import unittest

from game.split_logic import (
    apply_split_geometry,
    can_merge,
    merge_cubes,
    move_active_cube,
)
from game.state import GameState


class SplitLogicTests(unittest.TestCase):

    @staticmethod
    def create_split_state(
        first=(2, 2),
        second=(6, 6),
        active_cube=0,
    ):
        return GameState(
            mode="split",
            positions=(first, second),
            orientation="split",
            bridge_states=(False, True),
            used_switches=frozenset({"switch-1"}),
            active_cube=active_cube,
        )

    def test_move_first_cube_right(self):
        state = self.create_split_state()

        result = move_active_cube(
            state,
            "right",
        )

        self.assertEqual(
            result.positions,
            ((2, 3), (6, 6)),
        )

    def test_move_second_cube_up(self):
        state = self.create_split_state(
            active_cube=1,
        )

        result = move_active_cube(
            state,
            "up",
        )

        self.assertEqual(
            result.positions,
            ((2, 2), (5, 6)),
        )

    def test_move_preserves_active_cube(self):
        state = self.create_split_state(
            active_cube=1,
        )

        result = move_active_cube(
            state,
            "left",
        )

        self.assertEqual(result.active_cube, 1)

    def test_original_state_is_not_modified(self):
        state = self.create_split_state()

        move_active_cube(state, "right")

        self.assertEqual(
            state.positions,
            ((2, 2), (6, 6)),
        )

    def test_switch_active_cube_then_move(self):
        state = self.create_split_state()

        switched = state.switch_active_cube()

        result = move_active_cube(
            switched,
            "left",
        )

        self.assertEqual(result.active_cube, 1)
        self.assertEqual(
            result.positions,
            ((2, 2), (6, 5)),
        )

    def test_horizontal_cubes_can_merge(self):
        state = self.create_split_state(
            first=(3, 4),
            second=(3, 5),
        )

        self.assertTrue(can_merge(state))

        result = merge_cubes(state)

        self.assertEqual(result.mode, "normal")
        self.assertEqual(result.orientation, "horizontal")
        self.assertEqual(
            result.positions,
            ((3, 4), (3, 5)),
        )

    def test_vertical_cubes_can_merge(self):
        state = self.create_split_state(
            first=(3, 4),
            second=(4, 4),
        )

        result = merge_cubes(state)

        self.assertEqual(result.mode, "normal")
        self.assertEqual(result.orientation, "vertical")
        self.assertEqual(
            result.positions,
            ((3, 4), (4, 4)),
        )

    def test_non_adjacent_cubes_cannot_merge(self):
        state = self.create_split_state()

        self.assertFalse(can_merge(state))

        with self.assertRaises(ValueError):
            merge_cubes(state)

    def test_move_automatically_merges(self):
        state = self.create_split_state(
            first=(3, 3),
            second=(3, 5),
            active_cube=0,
        )

        result = apply_split_geometry(
            state,
            "right",
        )

        self.assertEqual(result.mode, "normal")
        self.assertEqual(result.orientation, "horizontal")
        self.assertEqual(
            result.positions,
            ((3, 4), (3, 5)),
        )

    def test_bridge_and_switch_information_is_preserved(self):
        state = self.create_split_state()

        result = move_active_cube(
            state,
            "up",
        )

        self.assertEqual(
            result.bridge_states,
            state.bridge_states,
        )

        self.assertEqual(
            result.used_switches,
            state.used_switches,
        )

    def test_cube_cannot_move_onto_other_cube(self):
        state = self.create_split_state(
            first=(3, 3),
            second=(3, 4),
            active_cube=0,
        )

        with self.assertRaises(ValueError):
            move_active_cube(
                state,
                "right",
            )

    def test_duplicate_positions_are_invalid(self):
        with self.assertRaises(ValueError):
            GameState(
                mode="split",
                positions=((3, 3), (3, 3)),
                orientation="split",
            )

    def test_normal_state_cannot_move_as_split_cube(self):
        state = GameState(
            mode="normal",
            positions=((3, 3),),
            orientation="upright",
        )

        with self.assertRaises(ValueError):
            move_active_cube(
                state,
                "right",
            )

    def test_invalid_action_is_rejected(self):
        state = self.create_split_state()

        with self.assertRaises(ValueError):
            move_active_cube(
                state,
                "jump",
            )


if __name__ == "__main__":
    unittest.main()