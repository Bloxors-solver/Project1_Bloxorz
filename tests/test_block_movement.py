import unittest

from game.block import Block


class BlockMovementTests(unittest.TestCase):
    """Verify all 3 orientations x 4 movement directions."""

    def assert_block(self, block, expected_positions, expected_orientation):
        actual_positions = ((block.x1, block.y1), (block.x2, block.y2))
        self.assertEqual(actual_positions, expected_positions)
        self.assertEqual(block.orientation, expected_orientation)
        self.assertEqual(block.move_counter, 1)

    def test_upright_moves_up(self):
        block = Block(5, 5)
        block.move("up")
        self.assert_block(block, ((3, 5), (4, 5)), "vertical")

    def test_upright_moves_down(self):
        block = Block(5, 5)
        block.move("down")
        self.assert_block(block, ((6, 5), (7, 5)), "vertical")

    def test_upright_moves_left(self):
        block = Block(5, 5)
        block.move("left")
        self.assert_block(block, ((5, 3), (5, 4)), "horizontal")

    def test_upright_moves_right(self):
        block = Block(5, 5)
        block.move("right")
        self.assert_block(block, ((5, 6), (5, 7)), "horizontal")

    def make_vertical_block(self):
        block = Block(4, 5)
        block.x2 = 5
        block.orientation = "vertical"
        return block

    def test_vertical_moves_up(self):
        block = self.make_vertical_block()
        block.move("up")
        self.assert_block(block, ((3, 5), (3, 5)), "upright")

    def test_vertical_moves_down(self):
        block = self.make_vertical_block()
        block.move("down")
        self.assert_block(block, ((6, 5), (6, 5)), "upright")

    def test_vertical_moves_left(self):
        block = self.make_vertical_block()
        block.move("left")
        self.assert_block(block, ((4, 4), (5, 4)), "vertical")

    def test_vertical_moves_right(self):
        block = self.make_vertical_block()
        block.move("right")
        self.assert_block(block, ((4, 6), (5, 6)), "vertical")

    def make_horizontal_block(self):
        block = Block(5, 4)
        block.y2 = 5
        block.orientation = "horizontal"
        return block

    def test_horizontal_moves_up(self):
        block = self.make_horizontal_block()
        block.move("up")
        self.assert_block(block, ((4, 4), (4, 5)), "horizontal")

    def test_horizontal_moves_down(self):
        block = self.make_horizontal_block()
        block.move("down")
        self.assert_block(block, ((6, 4), (6, 5)), "horizontal")

    def test_horizontal_moves_left(self):
        block = self.make_horizontal_block()
        block.move("left")
        self.assert_block(block, ((5, 3), (5, 3)), "upright")

    def test_horizontal_moves_right(self):
        block = self.make_horizontal_block()
        block.move("right")
        self.assert_block(block, ((5, 6), (5, 6)), "upright")

    def test_invalid_direction_is_rejected(self):
        block = Block(5, 5)
        with self.assertRaises(ValueError):
            block.move("diagonal")
        self.assertEqual(block.move_counter, 0)


if __name__ == "__main__":
    unittest.main()
