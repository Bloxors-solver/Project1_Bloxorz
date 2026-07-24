from __future__ import annotations

from .board import Board
from .split_logic import (
    apply_split_geometry,
    can_merge,
    merge_cubes,
    move_active_cube,
)
from .state import GameState
from .state_adapter import (
    block_to_state,
    bridge_states_from_board,
    state_to_block,
    used_switches_from_board,
)


MOVE_ACTIONS = (
    "up",
    "down",
    "left",
    "right",
)

SWITCH_ACTION = "switch"

# Giữ tên cũ để không làm hỏng những file đang import ACTIONS.
ACTIONS = MOVE_ACTIONS


def _switch_id(position: tuple[int, int]) -> str:
    row, col = position
    return f"switch-{row}-{col}"


def _sync_hidden_paths(board: Board) -> None:
    """
    Synchronize visible bridge cells with their controlling switches.
    """
    buttons = board.level.button

    if not buttons:
        return

    for _, button_data in buttons.items():
        is_open = bool(button_data[0])
        bridge_positions = button_data[1]

        for row, col in bridge_positions:
            board.level.layout[row][col] = (
                0 if is_open else -1
            )


def apply_state_to_board(
    board: Board,
    state: GameState,
) -> None:
    """
    Restore bridge and one-time-switch information from GameState.
    """
    buttons = board.level.button

    if not buttons:
        if state.bridge_states:
            raise ValueError(
                "State contains bridge information, "
                "but this level has no bridges."
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

    for position in button_positions:
        if _switch_id(position) in state.used_switches:
            buttons[position][0] = False

    _sync_hidden_paths(board)


def create_board_for_state(
    level_name: str,
    state: GameState,
) -> Board:
    board = Board(level_name)
    apply_state_to_board(board, state)

    return board


def _position_is_supported(
    board: Board,
    position: tuple[int, int],
) -> bool:
    """
    A cube is supported when its cell exists and is not void.

    A split cube is allowed on fragile tiles because it has only
    half the weight of the original upright block.
    """
    row, col = position

    if not (
        0 <= row < board.level.height
        and 0 <= col < board.level.width
    ):
        return False

    # Dynamic layout is used here because bridge cells are changed
    # between 0 (open) and -1 (closed).
    return board.level.layout[row][col] != -1


def _all_positions_supported(
    board: Board,
    state: GameState,
) -> bool:
    return all(
        _position_is_supported(board, position)
        for position in state.positions
    )


def _activate_soft_switch(
    board: Board,
    destination: tuple[int, int],
) -> None:
    """
    A single cube activates only a soft/hexagonal switch.

    It does not activate heavy X switches or one-time X switches.
    """
    if board.level.get_tiletype(destination) != "BUTTON_TYPE_HEX":
        return

    buttons = board.level.button

    if not buttons or destination not in buttons:
        return

    buttons[destination][0] = not bool(
        buttons[destination][0]
    )

    _sync_hidden_paths(board)


def _attach_board_state(
    state: GameState,
    board: Board,
) -> GameState:
    """
    Copy updated bridge/switch information into an immutable state.
    """
    return GameState(
        mode=state.mode,
        positions=state.positions,
        orientation=state.orientation,
        bridge_states=bridge_states_from_board(board),
        used_switches=used_switches_from_board(board),
        active_cube=state.active_cube,
    )


def move_geometry(
    state: GameState,
    action: str,
) -> GameState:
    """
    Apply movement geometry without board collision checks.
    """
    if action == SWITCH_ACTION:
        if not state.is_split:
            raise ValueError(
                "Only a split block can switch the active cube."
            )

        return state.switch_active_cube()

    if action not in MOVE_ACTIONS:
        raise ValueError(
            f"Invalid action {action!r}. "
            f"Expected one of {MOVE_ACTIONS} or 'switch'."
        )

    if state.is_split:
        return apply_split_geometry(
            state,
            action,
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
        active_cube=0,
    )


def _transition_split(
    state: GameState,
    action: str,
    level_name: str,
) -> GameState | None:
    """
    Apply one split-cube transition.
    """
    if action == SWITCH_ACTION:
        return state.switch_active_cube()

    if action not in MOVE_ACTIONS:
        raise ValueError(
            f"Invalid split action: {action!r}."
        )

    board = create_board_for_state(
        level_name,
        state,
    )

    try:
        moved_cubes = move_active_cube(
            state,
            action,
        )
    except ValueError:
        return None

    # Save the destination before an automatic merge changes mode.
    destination = moved_cubes.positions[state.active_cube]

    if can_merge(moved_cubes):
        next_state = merge_cubes(moved_cubes)
    else:
        next_state = moved_cubes

    # Check support before switch activation.
    if not _all_positions_supported(
        board,
        next_state,
    ):
        return None

    # Only the cube that moved can newly press a switch.
    _activate_soft_switch(
        board,
        destination,
    )

    # A switch may close a bridge underneath either cube.
    if not _all_positions_supported(
        board,
        next_state,
    ):
        return None

    return _attach_board_state(
        next_state,
        board,
    )

def _validate_split_destinations(
    board: Board,
    destinations: tuple[
        tuple[int, int],
        tuple[int, int],
    ],
) -> None:
    """
    Validate the two configured teleport destinations.

    Invalid split-switch configuration is a level-design error,
    not a normal illegal player movement.
    """
    if len(destinations) != 2:
        raise ValueError(
            "A split switch must define exactly two destinations."
        )

    if destinations[0] == destinations[1]:
        raise ValueError(
            "Split-switch destinations must be different."
        )

    for position in destinations:
        if not _position_is_supported(
            board,
            position,
        ):
            raise ValueError(
                "Split-switch destination "
                f"{position} is outside the board, "
                "inside void, or on a closed bridge."
            )


def _apply_split_switch(
    state: GameState,
    board: Board,
) -> GameState:
    """
    Split an upright normal block when it stands on a split switch.

    A block lying across a split switch does not activate it.
    """
    if state.is_split:
        return state

    if state.orientation != "upright":
        return state

    switch_position = state.positions[0]

    destinations = board.level.split_switches.get(
        switch_position
    )

    if destinations is None:
        return state

    destinations = tuple(destinations)

    _validate_split_destinations(
        board,
        destinations,
    )

    return GameState(
        mode="split",
        positions=destinations,
        orientation="split",
        bridge_states=state.bridge_states,
        used_switches=state.used_switches,
        active_cube=0,
    )


def transition(
    state: GameState,
    action: str,
    level_name: str,
) -> GameState | None:
    """
    Apply one complete legal transition.

    Returns None when the movement causes the block or cube to fall.
    """
    if state.is_split:
        return _transition_split(
            state,
            action,
            level_name,
        )

    if action == SWITCH_ACTION:
        raise ValueError(
            "A normal block cannot switch active cubes."
        )

    if action not in MOVE_ACTIONS:
        raise ValueError(
            f"Invalid action {action!r}."
        )

    board = create_board_for_state(
        level_name,
        state,
    )

    block = state_to_block(state)
    block.move(action)

    if board.is_fatal(block):
        return None

    board.refresh_layout(block)

    board_state = block_to_state(
    block,
    board,
)

# Preserve previously activated one-time switches while also
# recording switches newly activated by this movement.
    next_state = GameState(
    mode=board_state.mode,
    positions=board_state.positions,
    orientation=board_state.orientation,
    bridge_states=board_state.bridge_states,
    used_switches=(
        state.used_switches
        | board_state.used_switches
    ),
    active_cube=0,
)

    return _apply_split_switch(
    next_state,
    board,
)


def available_actions(
    state: GameState,
    level_name: str,
) -> list[str]:
    """
    Return legal actions in deterministic order.
    """
    legal_actions: list[str] = []

    for action in MOVE_ACTIONS:
        if transition(
            state,
            action,
            level_name,
        ) is not None:
            legal_actions.append(action)

    if state.is_split:
        legal_actions.append(SWITCH_ACTION)

    return legal_actions


def is_goal_state(
    state: GameState,
    level_name: str,
) -> bool:
    """
    Only a normal upright block can complete a level.
    """
    if state.is_split:
        return False

    if state.orientation != "upright":
        return False

    board = Board(level_name)

    return board.is_goal(
        state.positions[0]
    )