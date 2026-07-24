from __future__ import annotations

from typing import TYPE_CHECKING

from .block import Block
from .state import GameState

if TYPE_CHECKING:
    from .board import Board


def _switch_id(position: tuple[int, int]) -> str:
    """Create a stable ID for a switch based on its board position."""
    row, col = position
    return f"switch-{row}-{col}"


def bridge_states_from_board(board: Board) -> tuple[bool, ...]:
    """
    Extract current bridge-group states in a deterministic order.

    The legacy project stores one open/closed value for each switch and its
    associated hidden-path group. Sorting switch positions ensures that two
    equivalent boards always produce the same tuple.
    """
    buttons = board.level.button

    if not buttons:
        return ()

    return tuple(
        bool(buttons[position][0])
        for position in sorted(buttons)
    )


def used_switches_from_board(board: Board) -> frozenset[str]:
    """
    Extract one-time switches that have already been activated.

    In the legacy project, a one-time switch has tile type
    BUTTON_ONE_TIME_USE and becomes False after activation.
    """
    buttons = board.level.button

    if not buttons:
        return frozenset()

    used_switches: set[str] = set()

    for position in sorted(buttons):
        tile_type = board.level.get_tiletype(position)
        is_active = bool(buttons[position][0])

        if tile_type == "BUTTON_ONE_TIME_USE" and not is_active:
            used_switches.add(_switch_id(position))

    return frozenset(used_switches)


def block_to_state(
    block: Block,
    board: Board | None = None,
) -> GameState:
    """
    Convert the current legacy Block into an immutable GameState.
    """
    first = (block.x1, block.y1)
    second = (block.x2, block.y2)

    if block.orientation == "upright":
        positions = (first,)
    else:
        # Stable ordering is important for equality and hashing.
        positions = tuple(sorted((first, second)))

    bridge_states = ()
    used_switches = frozenset()

    if board is not None:
        bridge_states = bridge_states_from_board(board)
        used_switches = used_switches_from_board(board)

    return GameState(
        mode="normal",
        positions=positions,
        orientation=block.orientation,
        bridge_states=bridge_states,
        used_switches=used_switches,
        active_cube=0,
    )


def state_to_block(state: GameState) -> Block:
    """
    Convert a normal GameState back into the legacy Block object.

    Split states cannot be represented by the old Block class.
    """
    if state.is_split:
        raise ValueError(
            "A split GameState cannot be converted to the legacy Block."
        )

    first = state.positions[0]
    block = Block(*first)

    if state.orientation == "upright":
        block.x1 = block.x2 = first[0]
        block.y1 = block.y2 = first[1]
        block.orientation = "upright"
        return block

    second = state.positions[1]

    block.x1 = first[0]
    block.y1 = first[1]
    block.x2 = second[0]
    block.y2 = second[1]
    block.orientation = state.orientation

    return block


def update_block_from_state(block: Block, state: GameState) -> None:
    """
    Update an existing legacy Block from a normal GameState.

    This will later allow the renderer to keep using the same Block instance.
    """
    converted = state_to_block(state)

    block.x1 = converted.x1
    block.y1 = converted.y1
    block.x2 = converted.x2
    block.y2 = converted.y2
    block.orientation = converted.orientation