import unittest

from game import Block, Board
from search_algorithms import (
    Problem,
    a_star,
    breadth_first_search,
    run_search,
)


class SearchMetricsTests(unittest.TestCase):

    @staticmethod
    def create_problem(level_name="LEVEL1"):
        board = Board(level_name)
        block = Block(*board.level.start)

        board.refresh_layout(block)

        return Problem(block, board)

    def test_bfs_returns_complete_metrics(self):
        problem = self.create_problem()

        result = run_search(
            "BFS",
            breadth_first_search,
            problem,
        )

        self.assertTrue(result.solved)
        self.assertIsNotNone(result.goal_node)

        self.assertEqual(result.solution_length, 7)
        self.assertEqual(len(result.actions), 7)

        self.assertGreater(result.expanded_nodes, 0)
        self.assertGreaterEqual(result.search_time_ms, 0)
        self.assertGreaterEqual(result.peak_memory_mb, 0)

        final_state = problem.initial

        for action in result.actions:
            final_state = problem.result(
                final_state,
                action,
            )

        self.assertTrue(problem.is_goal(final_state))

    def test_a_star_returns_complete_metrics(self):
        problem = self.create_problem()

        result = run_search(
            "A*",
            a_star,
            problem,
        )

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, 7)
        self.assertGreater(result.expanded_nodes, 0)

    def test_result_can_be_exported_as_dictionary(self):
        problem = self.create_problem()

        result = run_search(
            "BFS",
            breadth_first_search,
            problem,
        )

        data = result.as_dict()

        self.assertEqual(data["algorithm"], "BFS")
        self.assertTrue(data["solved"])
        self.assertEqual(data["solution_length"], 7)


if __name__ == "__main__":
    unittest.main()