from __future__ import annotations

from game.state import GameState
from game.state_adapter import block_to_state
from game.transition import (
    available_actions,
    is_goal_state,
    transition,
)


class Problem:
    """
    Search-problem definition shared by BFS, DFS, UCS and A*.

    The constructor keeps the legacy signature (block, board, layout_only)
    so the current Renderer does not need to be changed yet.
    """

    def __init__(
        self,
        block,
        board,
        layout_only: bool = False,
    ) -> None:
        # Retained temporarily for compatibility with the old Renderer.
        # GameState now stores the complete searchable configuration.
        self.layout_only = layout_only

        self.level_name = board.level.level_name
        self.goal = board.level.goal

        self.initial: GameState = block_to_state(
            block,
            board,
        )

    def actions(self, state: GameState) -> list[str]:
        """Return legal actions in deterministic order."""
        return available_actions(
            state,
            self.level_name,
        )

    def result(
        self,
        state: GameState,
        action: str,
    ) -> GameState:
        """Return the immutable successor state."""

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
        Temporary unit cost.

        A non-uniform UCS cost function will be implemented after
        advanced tiles and split states are complete.
        """
        return 1

    def is_goal(self, state: GameState) -> bool:
        return is_goal_state(
            state,
            self.level_name,
        )