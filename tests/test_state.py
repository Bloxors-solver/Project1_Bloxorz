import unittest

from game.state import GameState


class GameStateTests(unittest.TestCase):

    def test_upright_state_is_hashable(self):
        state = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
        )

        visited = {state}

        self.assertIn(state, visited)

    def test_horizontal_state_has_two_cells(self):
        state = GameState(
            mode="normal",
            positions=((2, 3), (2, 4)),
            orientation="horizontal",
        )

        self.assertEqual(len(state.positions), 2)

    def test_bridge_configuration_is_part_of_state(self):
        closed_bridge = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
            bridge_states=(False,),
        )

        open_bridge = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
            bridge_states=(True,),
        )

        self.assertNotEqual(closed_bridge, open_bridge)

    def test_used_switches_are_part_of_state(self):
        before = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
        )

        after = GameState(
            mode="normal",
            positions=((2, 3),),
            orientation="upright",
            used_switches=frozenset({"switch-1"}),
        )

        self.assertNotEqual(before, after)

    def test_split_state(self):
        state = GameState(
            mode="split",
            positions=((1, 2), (5, 6)),
            orientation="split",
            active_cube=0,
        )

        self.assertTrue(state.is_split)
        self.assertEqual(state.controlled_position, (1, 2))

    def test_switch_active_cube(self):
        state = GameState(
            mode="split",
            positions=((1, 2), (5, 6)),
            orientation="split",
            active_cube=0,
        )

        switched = state.switch_active_cube()

        self.assertEqual(switched.active_cube, 1)
        self.assertEqual(switched.controlled_position, (5, 6))

    def test_invalid_upright_state(self):
        with self.assertRaises(ValueError):
            GameState(
                mode="normal",
                positions=((1, 2), (1, 3)),
                orientation="upright",
            )


if __name__ == "__main__":
    unittest.main()