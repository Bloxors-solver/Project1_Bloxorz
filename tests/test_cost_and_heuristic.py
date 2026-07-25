import unittest
from collections import deque

from game.block import Block
from game.board import Board
from game.state import GameState
from search_algorithms import (
    Problem,
    a_star,
    run_search,
    uniform_cost_search,
)
from search_algorithms.heuristic import h1, h2
from search_algorithms.node import Node


class CostFunctionTests(unittest.TestCase):

    @staticmethod
    def create_problem(level_name):
        board = Board(level_name)
        block = Block(*board.level.start)
        board.refresh_layout(block)
        return Problem(block, board)

    def test_normal_move_costs_one(self):
        problem = self.create_problem("LEVEL1")
        state = problem.initial
        next_state = problem.result(state, "right")

        self.assertEqual(
            problem.action_cost(
                state,
                "right",
                next_state,
            ),
            1,
        )

    def test_fragile_successor_costs_three(self):
        problem = self.create_problem("LEVEL2")
        state = GameState(
            mode="normal",
            positions=((4, 5),),
            orientation="upright",
        )
        next_state = problem.result(
            state,
            "up",
        )

        self.assertTrue(
            any(
                problem.action_cost(
                    state,
                    "up",
                    next_state,
                )
                == 3
                for _ in (0,)
            )
        )

    def test_split_cube_switch_action_costs_one(self):
        problem = self.create_problem("LEVEL10")
        state = GameState(
            mode="split",
            positions=((2, 7), (4, 9)),
            orientation="split",
            active_cube=0,
        )
        next_state = problem.result(
            state,
            "switch",
        )

        self.assertEqual(
            problem.action_cost(
                state,
                "switch",
                next_state,
            ),
            1,
        )


class HeuristicTests(unittest.TestCase):

    @staticmethod
    def create_problem(level_name):
        board = Board(level_name)
        block = Block(*board.level.start)
        board.refresh_layout(block)
        return Problem(block, board)

    def test_goal_heuristic_is_zero(self):
        problem = self.create_problem("LEVEL1")
        goal_state = GameState(
            mode="normal",
            positions=(problem.goal,),
            orientation="upright",
        )
        node = Node(goal_state)

        self.assertEqual(h1(node, problem), 0)
        self.assertEqual(h2(node, problem), 0)

    def test_heuristics_are_consistent_on_split_level(self):
        problem = self.create_problem("LEVEL10")
        frontier = deque([problem.initial])
        visited = {problem.initial}

        while frontier:
            state = frontier.popleft()
            node = Node(state)

            for action in problem.actions(state):
                next_state = problem.result(
                    state,
                    action,
                )
                cost = problem.action_cost(
                    state,
                    action,
                    next_state,
                )
                next_node = Node(next_state)

                self.assertLessEqual(
                    h1(node, problem),
                    cost + h1(next_node, problem),
                )
                self.assertLessEqual(
                    h2(node, problem),
                    cost + h2(next_node, problem),
                )

                if next_state not in visited:
                    visited.add(next_state)
                    frontier.append(next_state)

    def test_a_star_matches_ucs_optimal_cost(self):
        for level_name in (
            "LEVEL2",
            "LEVEL10",
        ):
            ucs_problem = self.create_problem(
                level_name
            )
            a_star_problem = self.create_problem(
                level_name
            )

            ucs_result = run_search(
                "UCS",
                uniform_cost_search,
                ucs_problem,
            )
            a_star_result = run_search(
                "A*",
                a_star,
                a_star_problem,
            )

            self.assertTrue(ucs_result.solved)
            self.assertTrue(a_star_result.solved)
            self.assertEqual(
                a_star_result.total_cost,
                ucs_result.total_cost,
            )


if __name__ == "__main__":
    unittest.main()
