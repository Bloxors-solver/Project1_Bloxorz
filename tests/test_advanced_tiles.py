import unittest

from game.board import Board
from game.state import GameState
from game.state_adapter import bridge_states_from_board
from game.transition import transition


class AdvancedTileTests(unittest.TestCase):
    """Requirement-focused tests for advanced Bloxorz tiles."""

    def test_fragile_tile_supports_a_lying_normal_block(self):
        state = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
        )

        result = transition(
            state,
            "right",
            "LEVEL8",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "horizontal")
        self.assertEqual(
            result.positions,
            ((2, 4), (2, 5)),
        )

    def test_fragile_tile_breaks_under_an_upright_normal_block(self):
        state = GameState(
            mode="normal",
            positions=((2, 3), (2, 4)),
            orientation="horizontal",
        )

        result = transition(
            state,
            "right",
            "LEVEL8",
        )

        self.assertIsNone(result)

    def test_soft_switch_is_activated_by_upright_block(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL4")
        )
        state = GameState(
            mode="normal",
            positions=((3, 11), (3, 12)),
            orientation="horizontal",
            bridge_states=initial_bridges,
        )

        result = transition(
            state,
            "left",
            "LEVEL4",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "upright")
        self.assertEqual(result.positions, ((3, 10),))
        self.assertNotEqual(
            result.bridge_states,
            initial_bridges,
        )

    def test_soft_switch_is_activated_by_lying_block(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL4")
        )
        state = GameState(
            mode="normal",
            positions=((3, 9),),
            orientation="upright",
            bridge_states=initial_bridges,
        )

        result = transition(
            state,
            "right",
            "LEVEL4",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "horizontal")
        self.assertIn((3, 10), result.positions)
        self.assertNotEqual(
            result.bridge_states,
            initial_bridges,
        )

    def test_heavy_switch_is_activated_by_upright_block(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL7")
        )
        state = GameState(
            mode="normal",
            positions=((4, 9), (4, 10)),
            orientation="horizontal",
            bridge_states=initial_bridges,
        )

        result = transition(
            state,
            "left",
            "LEVEL7",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "upright")
        self.assertEqual(result.positions, ((4, 8),))
        self.assertNotEqual(
            result.bridge_states,
            initial_bridges,
        )

    def test_heavy_switch_is_not_activated_by_lying_block(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL7")
        )
        state = GameState(
            mode="normal",
            positions=((4, 7),),
            orientation="upright",
            bridge_states=initial_bridges,
        )

        result = transition(
            state,
            "right",
            "LEVEL7",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "horizontal")
        self.assertIn((4, 8), result.positions)
        self.assertEqual(
            result.bridge_states,
            initial_bridges,
        )

    def test_toggle_switch_returns_bridge_to_original_state(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL7")
        )
        press_state = GameState(
            mode="normal",
            positions=((4, 9), (4, 10)),
            orientation="horizontal",
            bridge_states=initial_bridges,
        )

        first_press = transition(
            press_state,
            "left",
            "LEVEL7",
        )
        self.assertIsNotNone(first_press)
        self.assertNotEqual(
            first_press.bridge_states,
            initial_bridges,
        )

        second_press_state = GameState(
            mode="normal",
            positions=((4, 9), (4, 10)),
            orientation="horizontal",
            bridge_states=first_press.bridge_states,
            used_switches=first_press.used_switches,
        )
        second_press = transition(
            second_press_state,
            "left",
            "LEVEL7",
        )

        self.assertIsNotNone(second_press)
        self.assertEqual(
            second_press.bridge_states,
            initial_bridges,
        )

    def test_permanent_switch_changes_bridge_once_and_records_use(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL6")
        )
        state = GameState(
            mode="normal",
            positions=((6, 8), (7, 8)),
            orientation="vertical",
            bridge_states=initial_bridges,
        )

        result = transition(
            state,
            "down",
            "LEVEL6",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "upright")
        self.assertEqual(result.positions, ((8, 8),))
        self.assertEqual(result.bridge_states, (False,))
        self.assertIn(
            "switch-8-8",
            result.used_switches,
        )

    def test_permanent_switch_keeps_its_final_state(self):
        already_used = GameState(
            mode="normal",
            positions=((6, 8), (7, 8)),
            orientation="vertical",
            bridge_states=(False,),
            used_switches=frozenset({"switch-8-8"}),
        )

        result = transition(
            already_used,
            "down",
            "LEVEL6",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.bridge_states, (False,))
        self.assertEqual(
            result.used_switches,
            already_used.used_switches,
        )

    def test_one_time_heavy_switch_is_not_activated_while_lying(self):
        initial_bridges = bridge_states_from_board(
            Board("LEVEL6")
        )
        state = GameState(
            mode="normal",
            positions=((6, 8),),
            orientation="upright",
            bridge_states=initial_bridges,
        )

        # Moving down leaves the block lying across (7, 8) and (8, 8).
        # Because the one-time switch uses the heavy-switch shape, lying
        # across it must not activate it.
        result = transition(
            state,
            "down",
            "LEVEL6",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.orientation, "vertical")
        self.assertIn((8, 8), result.positions)
        self.assertEqual(
            result.bridge_states,
            initial_bridges,
        )
        self.assertNotIn(
            "switch-8-8",
            result.used_switches,
        )


if __name__ == "__main__":
    unittest.main()