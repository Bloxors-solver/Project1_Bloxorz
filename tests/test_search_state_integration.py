import unittest

from game import Block, Board
from game.state import GameState
from search_algorithms import (
    Problem,
    a_star,
    breadth_first_search,
    depth_first_search,
    uniform_cost_search,
)


def extract_actions(solution_node):
    actions = []
    node = solution_node

    while node is not None and node.parent is not None:
        actions.append(node.action)
        node = node.parent

    actions.reverse()
    return actions


def replay_solution(problem, actions):
    state = problem.initial

    for action in actions:
        state = problem.result(state, action)

    return state


class SearchStateIntegrationTests(unittest.TestCase):

    def create_problem(self, level_name="LEVEL1"):
        board = Board(level_name)
        block = Block(*board.level.start)

        board.refresh_layout(block)

        return Problem(
            block,
            board,
        )

    def test_problem_uses_game_state(self):
        problem = self.create_problem()

        self.assertIsInstance(
            problem.initial,
            GameState,
        )

    def test_problem_initial_state_is_hashable(self):
        problem = self.create_problem()

        visited = {problem.initial}

        self.assertIn(
            problem.initial,
            visited,
        )

    def test_bfs_solves_level_1(self):
        problem = self.create_problem()

        solution = breadth_first_search(problem)

        self.assertIsNotNone(solution)

        actions = extract_actions(solution)
        final_state = replay_solution(
            problem,
            actions,
        )

        self.assertTrue(
            problem.is_goal(final_state)
        )

        # LEVEL1's optimal solution contains seven moves.
        self.assertEqual(
            len(actions),
            7,
        )

    def test_dfs_solves_level_1(self):
        problem = self.create_problem()

        solution = depth_first_search(problem)

        self.assertIsNotNone(solution)

        actions = extract_actions(solution)
        final_state = replay_solution(
            problem,
            actions,
        )

        self.assertTrue(
            problem.is_goal(final_state)
        )

    def test_ucs_solves_level_1(self):
        problem = self.create_problem()

        solution = uniform_cost_search(problem)

        self.assertIsNotNone(solution)

        actions = extract_actions(solution)
        final_state = replay_solution(
            problem,
            actions,
        )

        self.assertTrue(
            problem.is_goal(final_state)
        )

        self.assertEqual(
            len(actions),
            7,
        )

    def test_a_star_solves_level_1(self):
        problem = self.create_problem()

        solution = a_star(problem)

        self.assertIsNotNone(solution)

        actions = extract_actions(solution)
        final_state = replay_solution(
            problem,
            actions,
        )

        self.assertTrue(
            problem.is_goal(final_state)
        )

        self.assertEqual(
            len(actions),
            7,
        )


if __name__ == "__main__":
    unittest.main()