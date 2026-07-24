import unittest

from search_algorithms.expand import expand
from search_algorithms.node import Node


class FakeProblem:
    def actions(self, state):
        return ["up", "down", "left", "right"]

    def result(self, state, action):
        return action

    def action_cost(self, state, action, next_state):
        return 1


class ExpandOrderTests(unittest.TestCase):
    def test_expand_preserves_action_order(self):
        children = expand(FakeProblem(), Node("start"))

        self.assertIsInstance(children, list)
        self.assertEqual(
            [child.action for child in children],
            ["up", "down", "left", "right"],
        )


if __name__ == "__main__":
    unittest.main()
