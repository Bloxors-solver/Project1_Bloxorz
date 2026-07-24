import unittest

from game.block import Block
from game.board import Board
from game.levels import Levels


class LevelSafetyTests(unittest.TestCase):
    def test_coordinates_on_or_beyond_matrix_edges_are_void(self):
        level = Levels("LEVEL1")
        positions = [
            (-1, 0),
            (0, -1),
            (level.height, 0),
            (0, level.width),
            (level.height + 1, level.width + 1),
        ]
        for position in positions:
            with self.subTest(position=position):
                self.assertEqual(level.get_tiletype(position), "VOID")

    def test_refresh_layout_does_not_crash_for_block_outside_board(self):
        board = Board("LEVEL1")
        block = Block(0, 0)
        block.move("up")

        # This used to risk negative-index wrapping or IndexError.
        layout = board.refresh_layout(block)

        self.assertEqual(len(layout), board.level.height)
        self.assertTrue(board.is_fatal(block))

    def test_switch_level_refreshes_all_level_metadata(self):
        level = Levels("LEVEL1")
        next_name = level.switch_level()

        self.assertEqual(next_name, "LEVEL2")
        self.assertEqual(level.start, level.level_data["start"])
        self.assertEqual(level.goal, level.level_data["goal"])
        self.assertEqual(level.button, level.level_data["button"])
        self.assertEqual(level.height, len(level.layout))
        self.assertEqual(level.width, len(level.layout[0]))


if __name__ == "__main__":
    unittest.main()
