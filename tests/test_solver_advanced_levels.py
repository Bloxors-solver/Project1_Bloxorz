import unittest

from game.block import Block
from game.board import Board
from search_algorithms import (
    Problem,
    a_star,
    breadth_first_search,
    run_search,
    uniform_cost_search,
)


class AdvancedSolverLevelTests(unittest.TestCase):
    """End-to-end checks that solvers preserve advanced level state."""

    @staticmethod
    def solve(level_name, algorithm_name, solver):
        board = Board(level_name)
        block = Block(*board.level.start)
        board.refresh_layout(block)

        problem = Problem(block, board)
        result = run_search(
            algorithm_name,
            solver,
            problem,
        )

        state = problem.initial
        visited_states = [state]

        for action in result.actions:
            state = problem.result(state, action)
            visited_states.append(state)

        return problem, result, visited_states

    def test_bfs_solves_soft_switch_bridge_level(self):
        problem, result, states = self.solve(
            "LEVEL4",
            "BFS",
            breadth_first_search,
        )

        self.assertTrue(result.solved)
        self.assertTrue(problem.is_goal(states[-1]))
        self.assertTrue(
            any(
                state.bridge_states
                != problem.initial.bridge_states
                for state in states
            )
        )

    def test_ucs_solves_heavy_switch_bridge_level(self):
        problem, result, states = self.solve(
            "LEVEL9",
            "UCS",
            uniform_cost_search,
        )

        self.assertTrue(result.solved)
        self.assertTrue(problem.is_goal(states[-1]))
        self.assertTrue(
            any(
                state.bridge_states
                != problem.initial.bridge_states
                for state in states
            )
        )

    def test_a_star_solves_split_and_rejoin_level(self):
        problem, result, states = self.solve(
            "LEVEL10",
            "A*",
            a_star,
        )

        self.assertTrue(result.solved)
        self.assertTrue(problem.is_goal(states[-1]))
        self.assertTrue(
            any(state.is_split for state in states)
        )
        self.assertFalse(states[-1].is_split)
        self.assertEqual(
            states[-1].orientation,
            "upright",
        )


if __name__ == "__main__":
    unittest.main()