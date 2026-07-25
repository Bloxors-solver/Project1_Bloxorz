import json
import tempfile
import unittest
from pathlib import Path

from game.board import Board
from game.levels import (
    DEFAULT_LEVELS_DIR,
    EMBEDDED_LEVELS,
    load_level_file,
    load_levels_from_directory,
    levels,
)


class JsonLevelLoaderTests(unittest.TestCase):

    def test_all_ten_json_levels_are_loaded(self):
        loaded = load_levels_from_directory()

        self.assertEqual(
            set(loaded),
            {f"LEVEL{number}" for number in range(1, 11)},
        )
        self.assertEqual(len(loaded), 10)

    def test_active_levels_use_json_data(self):
        self.assertEqual(
            levels["LEVEL1"]["start"],
            (4, 4),
        )
        self.assertEqual(
            levels["LEVEL10"]["goal"],
            (3, 10),
        )

    def test_button_coordinates_are_restored_as_tuples(self):
        level4 = levels["LEVEL4"]

        self.assertIn((3, 10), level4["button"])
        self.assertEqual(
            level4["button"][(3, 10)][1],
            ((3, 7), (3, 8)),
        )

    def test_split_switch_destinations_are_restored(self):
        self.assertEqual(
            levels["LEVEL10"]["split_switches"][(3, 5)],
            ((2, 7), (4, 9)),
        )

    def test_board_can_use_json_loaded_levels(self):
        board = Board("LEVEL10")

        self.assertEqual(board.level.start, (3, 2))
        self.assertEqual(board.level.goal, (3, 10))
        self.assertEqual(
            board.level.get_tiletype((3, 5)),
            "SPLIT_SWITCH",
        )

    def test_loader_validates_unequal_row_widths(self):
        payload = {
            "schema_version": 1,
            "name": "LEVEL_BAD",
            "layout": [[0, 0], [0]],
            "start": [0, 0],
            "goal": [0, 1],
            "buttons": [],
            "split_switches": [],
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "level_bad.json"
            path.write_text(
                json.dumps(payload),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_level_file(path)

    def test_json_directory_exists_in_repository(self):
        self.assertTrue(DEFAULT_LEVELS_DIR.is_dir())
        self.assertEqual(
            len(list(DEFAULT_LEVELS_DIR.glob("level*.json"))),
            10,
        )


if __name__ == "__main__":
    unittest.main()
