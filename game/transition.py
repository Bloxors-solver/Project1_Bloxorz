from __future__ import annotations

# from copy import deepcopy

from .board import Board
from .state import GameState
from .state_adapter import block_to_state, state_to_block


ACTIONS = ("up", "down", "left", "right")


def _switch_id(position: tuple[int, int]) -> str:
    row, col = position
    return f"switch-{row}-{col}"


def apply_state_to_board(board: Board, state: GameState) -> None:
    """
    Restore bridge and one-time-switch information from GameState
    into a newly created legacy Board.

    This ensures that two states with the same block position but
    different bridge configurations behave differently.
    """
    buttons = board.level.button

    if not buttons:
        if state.bridge_states:
            raise ValueError(
                "State contains bridge information, but this level has no bridges."
            )
        return

    button_positions = sorted(buttons)

    if state.bridge_states:
        if len(state.bridge_states) != len(button_positions):
            raise ValueError(
                "Number of bridge states does not match the level."
            )

        for position, is_open in zip(
            button_positions,
            state.bridge_states,
        ):
            buttons[position][0] = bool(is_open)

    # A used one-time switch must remain disabled.
    for position in button_positions:
        if _switch_id(position) in state.used_switches:
            buttons[position][0] = False

    # Synchronize the visible layout with the restored bridge states.
    for position in button_positions:
        is_open = bool(buttons[position][0])

        for row, col in buttons[position][1]:
            board.level.layout[row][col] = 0 if is_open else -1


def create_board_for_state(
    level_name: str,
    state: GameState,
) -> Board:
    """
    Create an independent board representing the supplied state.
    """
    board = Board(level_name)
    apply_state_to_board(board, state)
    return board


def move_geometry(
    state: GameState,
    action: str,
) -> GameState:
    """
    Apply only block movement geometry.

    Board collisions, void cells, fragile tiles and switches are not
    processed here.
    """
    if action not in ACTIONS:
        raise ValueError(
            f"Invalid action {action!r}. Expected one of {ACTIONS}."
        )

    if state.is_split:
        raise NotImplementedError(
            "Split-cube movement will be implemented in Phase 3."
        )

    block = state_to_block(state)
    block.move(action)

    moved_state = block_to_state(block)

    return GameState(
        mode=moved_state.mode,
        positions=moved_state.positions,
        orientation=moved_state.orientation,
        bridge_states=state.bridge_states,
        used_switches=state.used_switches,
        active_cube=state.active_cube,
    )


def transition(
    state: GameState,
    action: str,
    level_name: str,
) -> GameState | None:
    """
    Apply one complete legal game transition.

    Returns:
        A new immutable GameState when the action is legal.
        None when the block falls or breaks a fragile tile.
    """
    if state.is_split:
        raise NotImplementedError(
            "Split-cube transitions will be implemented in Phase 3."
        )

    board = create_board_for_state(level_name, state)
    block = state_to_block(state)

    # Move a copied representation; the original GameState is never changed.
    block.move(action)

    # Check support using the bridge configuration before activating
    # switches at the destination.
    if board.is_fatal(block):
        return None

    # Apply switch effects and update the new bridge configuration.
    board.refresh_layout(block)

    return block_to_state(block, board)


def available_actions(
    state: GameState,
    level_name: str,
) -> list[str]:
    """
    Return legal actions in deterministic order.
    """
    legal_actions: list[str] = []

    for action in ACTIONS:
        if transition(state, action, level_name) is not None:
            legal_actions.append(action)

    return legal_actions


def is_goal_state(
    state: GameState,
    level_name: str,
) -> bool:
    """
    The goal is reached only by a normal upright block.
    A split cube cannot finish the level.
    """
    if state.is_split:
        return False

    if state.orientation != "upright":
        return False

    board = Board(level_name)
    return board.is_goal(state.positions[0])