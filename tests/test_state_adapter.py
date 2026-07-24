import unittest

from game.block import Block
from game.board import Board
from game.state import GameState
from game.state_adapter import (
    block_to_state,
    bridge_states_from_board,
    state_to_block,
    update_block_from_state,
    used_switches_from_board,
)


class StateAdapterTests(unittest.TestCase):

    def test_convert_upright_block_to_state(self):
        block = Block(4, 5)

        state = block_to_state(block)

        self.assertEqual(state.mode, "normal")
        self.assertEqual(state.orientation, "upright")
        self.assertEqual(state.positions, ((4, 5),))

    def test_convert_vertical_block_to_state(self):
        block = Block(3, 5)
        block.x2 = 4
        block.orientation = "vertical"

        state = block_to_state(block)

        self.assertEqual(state.orientation, "vertical")
        self.assertEqual(
            state.positions,
            ((3, 5), (4, 5)),
        )

    def test_convert_horizontal_block_to_state(self):
        block = Block(5, 3)
        block.y2 = 4
        block.orientation = "horizontal"

        state = block_to_state(block)

        self.assertEqual(state.orientation, "horizontal")
        self.assertEqual(
            state.positions,
            ((5, 3), (5, 4)),
        )

    def test_bridge_states_are_deterministic(self):
        board = Board("LEVEL4")

        states = bridge_states_from_board(board)

        # LEVEL4 contains two switch-controlled bridge groups.
        self.assertEqual(states, (True, False))

    def test_board_information_is_added_to_state(self):
        block = Block(3, 15)
        board = Board("LEVEL4")

        state = block_to_state(block, board)

        self.assertEqual(state.bridge_states, (True, False))

    def test_one_time_switch_is_recorded_after_use(self):
        board = Board("LEVEL6")

        switch_position = (8, 8)
        board.level.button[switch_position][0] = False

        used = used_switches_from_board(board)

        self.assertIn("switch-8-8", used)

    def test_state_to_block_round_trip(self):
        original = Block(5, 4)
        original.y2 = 5
        original.orientation = "horizontal"

        state = block_to_state(original)
        restored = state_to_block(state)

        self.assertEqual(restored, original)

    def test_update_existing_block(self):
        block = Block(0, 0)

        state = GameState(
            mode="normal",
            positions=((3, 4), (4, 4)),
            orientation="vertical",
        )

        update_block_from_state(block, state)

        self.assertEqual(block.x1, 3)
        self.assertEqual(block.y1, 4)
        self.assertEqual(block.x2, 4)
        self.assertEqual(block.y2, 4)
        self.assertEqual(block.orientation, "vertical")

    def test_split_state_cannot_become_legacy_block(self):
        state = GameState(
            mode="split",
            positions=((2, 3), (7, 8)),
            orientation="split",
            active_cube=0,
        )

        with self.assertRaises(ValueError):
            state_to_block(state)


if __name__ == "__main__":
    unittest.main()