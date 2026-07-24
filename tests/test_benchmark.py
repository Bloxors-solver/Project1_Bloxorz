import csv
import tempfile
import unittest
from pathlib import Path

from benchmark import run_benchmark


class BenchmarkTests(unittest.TestCase):

    def test_bfs_benchmark_exports_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = (
                Path(directory)
                / "results.csv"
            )

            rows = run_benchmark(
                levels=["LEVEL1"],
                algorithm_names=["BFS"],
                repeats=1,
                output_path=output_path,
            )

            self.assertEqual(len(rows), 1)

            row = rows[0]

            self.assertEqual(row["level"], "LEVEL1")
            self.assertEqual(row["algorithm"], "BFS")
            self.assertTrue(row["solved"])
            self.assertEqual(row["solution_length"], 7)
            self.assertGreater(row["expanded_nodes"], 0)
            self.assertEqual(row["error"], "")

            self.assertTrue(
                output_path.exists()
            )

            with output_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                exported_rows = list(
                    csv.DictReader(csv_file)
                )

            self.assertEqual(
                len(exported_rows),
                1,
            )

            self.assertEqual(
                exported_rows[0]["algorithm"],
                "BFS",
            )

            self.assertEqual(
                exported_rows[0]["level"],
                "LEVEL1",
            )

    def test_multiple_repetitions_create_multiple_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = (
                Path(directory)
                / "results.csv"
            )

            rows = run_benchmark(
                levels=["LEVEL1"],
                algorithm_names=["BFS"],
                repeats=2,
                output_path=output_path,
            )

            self.assertEqual(
                len(rows),
                2,
            )

            self.assertEqual(
                rows[0]["run"],
                1,
            )

            self.assertEqual(
                rows[1]["run"],
                2,
            )


if __name__ == "__main__":
    unittest.main()