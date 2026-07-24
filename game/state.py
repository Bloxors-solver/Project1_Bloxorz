from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Position = tuple[int, int]

BlockMode = Literal["normal", "split"]

Orientation = Literal[
    "upright",
    "horizontal",
    "vertical",
    "split",
]


@dataclass(frozen=True, slots=True)
class GameState:
    """
    Immutable representation of one complete Bloxorz state.

    Because the class is frozen, it can safely be stored inside
    set/dict structures used by BFS, DFS, UCS, and A*.
    """

    mode: BlockMode

    # Normal mode:
    # - upright: contains one position
    # - horizontal/vertical: contains two positions
    #
    # Split mode:
    # - contains exactly two cube positions
    positions: tuple[Position, ...]

    orientation: Orientation

    # Store bridge states in a deterministic order.
    # Example: (False, True, False)
    bridge_states: tuple[bool, ...] = ()

    # IDs of one-time switches that have already been activated.
    used_switches: frozenset[str] = frozenset()

    # Only meaningful in split mode: 0 or 1.
    active_cube: int = 0

    def __post_init__(self) -> None:
        if self.mode == "normal":
            if self.orientation == "upright" and len(self.positions) != 1:
                raise ValueError(
                    "An upright block must occupy exactly one cell."
                )

            if self.orientation in {"horizontal", "vertical"}:
                if len(self.positions) != 2:
                    raise ValueError(
                        "A lying block must occupy exactly two cells."
                    )

            if self.orientation == "split":
                raise ValueError(
                    "Normal mode cannot use split orientation."
                )

        elif self.mode == "split":
            if self.orientation != "split":
                raise ValueError(
                    "Split mode must use split orientation."
                )

            if len(self.positions) != 2:
                raise ValueError(
                    "Split mode must contain exactly two cubes."
                )

            if self.active_cube not in (0, 1):
                raise ValueError(
                    "active_cube must be either 0 or 1."
                )

        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    @property
    def is_split(self) -> bool:
        return self.mode == "split"

    @property
    def controlled_position(self) -> Position:
        if not self.is_split:
            return self.positions[0]

        return self.positions[self.active_cube]

    def switch_active_cube(self) -> GameState:
        if not self.is_split:
            return self

        return GameState(
            mode=self.mode,
            positions=self.positions,
            orientation=self.orientation,
            bridge_states=self.bridge_states,
            used_switches=self.used_switches,
            active_cube=1 - self.active_cube,
        )