from __future__ import annotations

from game.levels import levels
from game.state import GameState
from game.state_adapter import block_to_state
from game.transition import (
    available_actions,
    is_goal_state,
    transition,
)


NORMAL_MOVE_COST = 1
FRAGILE_MOVE_COST = 3


class Problem:
    """
    Search-problem definition shared by BFS, DFS, UCS and A*.

    Cost model:
    - Every normal roll or split-cube switch action costs 1.
    - A transition whose successor occupies at least one fragile tile costs 3.

    The fragile penalty gives UCS a meaningful objective that differs from
    BFS while keeping every action cost positive. The heuristic can therefore
    use one as the minimum possible action cost.
    """

    def __init__(
        self,
        block,
        board,
        layout_only: bool = False,
    ) -> None:
        self.layout_only = layout_only
        self.level_name = board.level.level_name
        self.goal = board.level.goal
        self.initial: GameState = block_to_state(
            block,
            board,
        )
        self.expanded_nodes = 0

    # ---------------- Metrics ----------------

    def reset_metrics(self) -> None:
        self.expanded_nodes = 0

    def record_expansion(self) -> None:
        self.expanded_nodes += 1

    # ---------------- Search API ----------------

    def actions(self, state: GameState) -> list[str]:
        """Return legal actions in deterministic order."""
        self.record_expansion()
        return available_actions(
            state,
            self.level_name,
        )

    def result(
        self,
        state: GameState,
        action: str,
    ) -> GameState:
        next_state = transition(
            state,
            action,
            self.level_name,
        )

        if next_state is None:
            raise ValueError(
                f"Action {action!r} is illegal for state {state!r}."
            )

        return next_state

    def action_cost(
        self,
        state: GameState,
        action: str,
        next_state: GameState,
    ) -> int:
        """
        Return the transition cost used by UCS and A*.

        Fragile tiles are intentionally more expensive because they represent
        a risky surface. The penalty is charged when the successor state
        occupies at least one fragile tile. All other legal actions cost 1.
        """
        if action == "switch":
            return NORMAL_MOVE_COST

        layout = levels[self.level_name]["layout"]
        height = len(layout)
        width = len(layout[0])

        for row, column in next_state.positions:
            if (
                0 <= row < height
                and 0 <= column < width
                and layout[row][column] == 3
            ):
                return FRAGILE_MOVE_COST

        return NORMAL_MOVE_COST

    def is_goal(self, state: GameState) -> bool:
        return is_goal_state(
            state,
            self.level_name,
        )
