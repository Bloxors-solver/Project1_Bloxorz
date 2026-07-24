import csv
import tempfile
import unittest
from pathlib import Path

from search_algorithms.a_star import a_star
from search_algorithms.breadth_first_search import (
    breadth_first_search,
)
from search_algorithms.comparison import (
    run_comparison,
    save_comparison_csv,
    select_replay_result,
)


class ComparisonTests(unittest.TestCase):

    def test_run_comparison_uses_fresh_problems(self):
        entries = run_comparison(
            "LEVEL1",
            algorithms=(
                ("BFS", breadth_first_search),
                ("A*", a_star),
            ),
        )

        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0].solved)
        self.assertTrue(entries[1].solved)

        self.assertEqual(
            entries[0].result.solution_length,
            7,
        )
        self.assertEqual(
            entries[1].result.solution_length,
            7,
        )

    def test_a_star_is_selected_for_replay(self):
        entries = run_comparison(
            "LEVEL1",
            algorithms=(
                ("BFS", breadth_first_search),
                ("A*", a_star),
            ),
        )

        selected = select_replay_result(entries)

        self.assertIsNotNone(selected)
        self.assertEqual(selected.algorithm, "A*")

    def test_comparison_exports_csv(self):
        entries = run_comparison(
            "LEVEL1",
            algorithms=(
                ("BFS", breadth_first_search),
            ),
        )

        with tempfile.TemporaryDirectory() as directory:
            output_path = save_comparison_csv(
                entries,
                "LEVEL1",
                output_directory=Path(directory),
            )

            self.assertTrue(output_path.exists())

            with output_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                rows = list(csv.DictReader(csv_file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0]["algorithm"],
                "BFS",
            )
            self.assertEqual(
                rows[0]["level"],
                "LEVEL1",
            )


if __name__ == "__main__":
    unittest.main()
