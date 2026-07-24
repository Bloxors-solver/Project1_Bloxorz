from __future__ import annotations

from typing import Any


class Node:
    def __init__(
        self,
        state: Any,
        parent: Node | None = None,
        action: str | None = None,
        path_cost: float = 0,
        depth: int = 0,
    ) -> None:
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False

        return self.state == other.state

    def __hash__(self) -> int:
        return hash(self.state)

    def __lt__(self, other: Node) -> bool:
        """
        Used when two nodes in a priority queue have equal priority.
        """
        if self.path_cost != other.path_cost:
            return self.path_cost < other.path_cost

        return self.depth < other.depth