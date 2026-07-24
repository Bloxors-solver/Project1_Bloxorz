from __future__ import annotations

from .state import GameState


MOVE_DELTAS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


def move_active_cube(
    state: GameState,
    action: str,
) -> GameState:
    """
    Move only the currently controlled cube by one cell.

    This function handles geometry only. Board collisions and
    switch activation will be handled later.
    """
    if not state.is_split:
        raise ValueError(
            "move_active_cube requires a split GameState."
        )

    if action not in MOVE_DELTAS:
        raise ValueError(
            f"Invalid split action: {action!r}."
        )

    delta_row, delta_col = MOVE_DELTAS[action]

    positions = list(state.positions)
    row, col = positions[state.active_cube]

    new_position = (
        row + delta_row,
        col + delta_col,
    )

    # A cube cannot move onto the exact position of the other cube.
    other_cube = 1 - state.active_cube

    if new_position == positions[other_cube]:
        raise ValueError(
            "A split cube cannot occupy the same cell as the other cube."
        )

    positions[state.active_cube] = new_position

    return GameState(
        mode="split",
        positions=tuple(positions),
        orientation="split",
        bridge_states=state.bridge_states,
        used_switches=state.used_switches,
        active_cube=state.active_cube,
    )


def can_merge(state: GameState) -> bool:
    """
    Two split cubes can merge when they stand on adjacent cells.
    """
    if not state.is_split:
        return False

    first, second = state.positions

    manhattan_distance = (
        abs(first[0] - second[0])
        + abs(first[1] - second[1])
    )

    return manhattan_distance == 1


def merge_cubes(state: GameState) -> GameState:
    """
    Merge two adjacent cubes into a normal lying block.
    """
    if not state.is_split:
        raise ValueError(
            "merge_cubes requires a split GameState."
        )

    if not can_merge(state):
        raise ValueError(
            "The two cubes must be adjacent before merging."
        )

    first, second = sorted(state.positions)

    if first[0] == second[0]:
        orientation = "horizontal"
    else:
        orientation = "vertical"

    return GameState(
        mode="normal",
        positions=(first, second),
        orientation=orientation,
        bridge_states=state.bridge_states,
        used_switches=state.used_switches,
        active_cube=0,
    )


def apply_split_geometry(
    state: GameState,
    action: str,
) -> GameState:
    """
    Move the active cube and automatically merge if the two cubes
    become adjacent.
    """
    moved_state = move_active_cube(
        state,
        action,
    )

    if can_merge(moved_state):
        return merge_cubes(moved_state)

    return moved_state