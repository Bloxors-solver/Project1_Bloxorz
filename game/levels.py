from copy import deepcopy
import json
from pathlib import Path

level_menu = {
    0: "LEVEL1",
    1: "LEVEL2",
    2: "LEVEL3",
    3: "LEVEL4",
    4: "LEVEL5",
    5: "LEVEL6",
    6: "LEVEL7",
    7: "LEVEL8",
    8: "LEVEL9",
    9: "LEVEL10",
}

reverse_level_menu = {value: key for key, value in level_menu.items()}

levels = {
        "LEVEL1": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0,  0, 0,  -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0,  0, 0,  0,  0,  0,  -1, -1, -1, -1],
                       [-1, -1, -1, -1,  0,  0,  0,  0, 0,  0,  0,  0,  0,  -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, 0,  0,  7,  0,  0,  -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, 0,  0,  0,  -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],
            "start": (4, 4),

            "goal": (7, 10),

            "button": None,
        },

        "LEVEL2": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  3,  3,  3,  3,  3,  3,  3,  3, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  3,  3,  3,  3,  3,  3,  3,  3, -1, -1, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  3,  3,  3,  3,  3, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  3,  3,  3,  3,  3, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1,  0,  7,  0, -1, -1,  3,  3,  0,  3, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1,  3,  3,  3,  3, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (7, 3),

            "goal": (9, 9),

            "button": None,
        },

        "LEVEL3": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1,],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1, -1,  0, -1, -1,  0,  0,  0,  0, -1, -1,],
                       [-1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1,  0,  7,  0, -1, -1,],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1,  0,  0,  4, -1, -1,  0,  0,  0, -1, -1,],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1,],
                       [-1, -1, -1,  0,  0, -2, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,]],

            "start": (5, 3),

            "goal": (5, 15),

            "button": {  # Location, is_active, hidden_path
                    (6, 11): [False, [((8, 5))]]
            },
        },

        "LEVEL4": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0, -2, -2,  0,  5,  0,  0,  0,  0,  0,  0, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  5, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  7,  0,  0,  0, -2, -2,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (3, 15),

            "goal": (10, 3),

            "button": {  # Location, is_active, hidden_path
                    (3, 10): [True, ((3, 7), (3, 8))],
                    (8, 16): [False, ((10, 7), (10, 8))]
            },
        },

        "LEVEL5": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1,  0,  0,  7,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (5, 2),

            "goal": (6, 15),

            "button": None,
        },

        "LEVEL6": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  7,  0, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1],
                       [-1, -1, -1,  0, -1, -1, -1,  0,  0, -1, -1,  0,  0, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  6, -1, -1, -1, -1,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (7, 2),

            "goal": (3, 4),

            "button": {  # Location, is_active, hidden_path
                    (8, 8): [True, ((2, 6), (3, 6))]
            },
        },

        "LEVEL7": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  4, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  4,  0,  0,  0,  0,  0, -2, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -1,  0,  0, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  7,  0, -2, -1, -1, -1,  0,  0, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0,  0, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (8, 4),

            "goal":  (6, 6),

            "button": {  # Location, is_active, hidden_path
                    (4, 8): [False, [((4, 14))]],
                    (2, 14): [False, [((6, 8))]],
            },
        },

        "LEVEL8": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1,  0,  0,  0,  3,  0,  0,  0,  0,  3,  0,  0,  0,  0, -1, -1, -1],
                       [-1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1],
                       [-1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0,  3,  3,  3,  0,  7,  0, -1, -1,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0, -1, -1,  3,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1],
                       [-1, -1, -1, -1,  0, -1, -1,  3,  3,  3,  3,  3,  0,  0, -1, -1, -1, -1],
                       [-1, -1, -1, -1,  0,  0,  0,  3,  3,  0,  3,  3,  3, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  0,  3,  3,  3,  3,  3,  3, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  0,  0, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (5, 14),

            "goal":  (6, 9),

            "button": None

        },

        "LEVEL9": {
            "layout": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1],
                       [-1, -1,  0, -2, -2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1],
                       [-1, -1,  0, -2, -2,  0,  0,  0, -1, -1, -1, -1, -1, -1,  4,  0, -1, -1],
                       [-1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1],
                       [-1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1],
                       [-1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1],
                       [-1, -1,  0,  0,  0,  0,  0, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1],
                       [-1, -1, -1,  0,  0,  7,  0, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  0,  4, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],

            "start": (4, 6),

            "goal":  (10, 5),

            "button": {  # Location, is_active, hidden_path
                    (5, 14): [False, ((4, 3), (4, 4))],
                    (11, 15): [False, ((5, 3), (5, 4))]
            },

        },

        "LEVEL10": {
            "layout": [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1],
                [-1, -1,  0,  0,  0,  8,  0,  0,  0,  0,  7, -1],
                [-1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            ],

            "start": (3, 2),

            "goal": (3, 10),

            "button": None,

            # Split-switch position:
            #     (3, 5)
            #
            # Teleport destinations:
            #     cube 0 -> (2, 7)
            #     cube 1 -> (4, 9)
            "split_switches": {
                (3, 5): (
                    (2, 7),
                    (4, 9),
                ),
            },
        },

}


# Keep the Python definitions as a safe fallback. The JSON files are the
# primary source when the project is distributed normally.
EMBEDDED_LEVELS = deepcopy(levels)
DEFAULT_LEVELS_DIR = (
    Path(__file__).resolve().parent.parent
    / "levels"
)


def _coordinate(value, field_name):
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, int) for item in value)
    ):
        raise ValueError(
            f"{field_name} must be a two-integer JSON array."
        )

    return tuple(value)


def _validate_layout(layout, level_name):
    if not isinstance(layout, list) or not layout:
        raise ValueError(
            f"{level_name}: layout must be a non-empty matrix."
        )

    width = len(layout[0])

    if width == 0:
        raise ValueError(
            f"{level_name}: layout rows cannot be empty."
        )

    for row in layout:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError(
                f"{level_name}: all layout rows must have equal length."
            )

        if not all(isinstance(tile, int) for tile in row):
            raise ValueError(
                f"{level_name}: every layout tile must be an integer."
            )

    return deepcopy(layout)


def load_level_file(path):
    """Load and normalize one level JSON file."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as level_file:
        raw = json.load(level_file)

    level_name = raw.get("name")

    if not isinstance(level_name, str) or not level_name:
        raise ValueError(
            f"{path}: missing a valid level name."
        )

    if raw.get("schema_version", 1) != 1:
        raise ValueError(
            f"{level_name}: unsupported schema_version."
        )

    layout = _validate_layout(
        raw.get("layout"),
        level_name,
    )
    start = _coordinate(
        raw.get("start"),
        f"{level_name}.start",
    )
    goal = _coordinate(
        raw.get("goal"),
        f"{level_name}.goal",
    )

    button = {}

    for index, entry in enumerate(raw.get("buttons", [])):
        position = _coordinate(
            entry.get("position"),
            f"{level_name}.buttons[{index}].position",
        )
        bridges = tuple(
            _coordinate(
                bridge,
                f"{level_name}.buttons[{index}].bridges",
            )
            for bridge in entry.get("bridges", [])
        )
        initial_state = entry.get("initial_state")

        if not isinstance(initial_state, bool):
            raise ValueError(
                f"{level_name}.buttons[{index}].initial_state "
                "must be true or false."
            )

        button[position] = [
            initial_state,
            bridges,
        ]

    split_switches = {}

    for index, entry in enumerate(
        raw.get("split_switches", [])
    ):
        position = _coordinate(
            entry.get("position"),
            (
                f"{level_name}.split_switches"
                f"[{index}].position"
            ),
        )
        destinations = tuple(
            _coordinate(
                destination,
                (
                    f"{level_name}.split_switches"
                    f"[{index}].destinations"
                ),
            )
            for destination in entry.get(
                "destinations",
                [],
            )
        )

        if len(destinations) != 2:
            raise ValueError(
                f"{level_name}: a split switch must have "
                "exactly two destinations."
            )

        split_switches[position] = destinations

    normalized = {
        "layout": layout,
        "start": start,
        "goal": goal,
        "button": button or None,
    }

    if split_switches:
        normalized["split_switches"] = split_switches

    return level_name, normalized


def load_levels_from_directory(directory=DEFAULT_LEVELS_DIR):
    """Load every level*.json file from one directory."""
    directory = Path(directory)

    if not directory.is_dir():
        return {}

    loaded = {}

    for path in sorted(directory.glob("level*.json")):
        level_name, level_data = load_level_file(path)

        if level_name in loaded:
            raise ValueError(
                f"Duplicate JSON level name: {level_name}."
            )

        loaded[level_name] = level_data

    return loaded


JSON_LEVELS = load_levels_from_directory()

if JSON_LEVELS:
    expected_names = set(level_menu.values())
    loaded_names = set(JSON_LEVELS)

    if loaded_names != expected_names:
        missing = sorted(expected_names - loaded_names)
        extra = sorted(loaded_names - expected_names)
        raise ValueError(
            "JSON level set does not match level_menu. "
            f"Missing={missing}, extra={extra}."
        )

    levels = JSON_LEVELS

NUM_LEVELS = len(levels)


class Levels:
    def __init__(self, chosen_level):
        self.level_name = chosen_level
        self.level_data = levels[self.level_name]

        self.layout = deepcopy(self.level_data["layout"])
        self.start = self.level_data["start"]
        self.goal = self.level_data["goal"]
        self.button = deepcopy(self.level_data["button"])
        self.split_switches = deepcopy(
            self.level_data.get(
                "split_switches",
                {},
            )
        )

        self.width = len(self.layout[0])
        self.height = len(self.layout)

    def get_tiletype(self, position):
        x, y = position
        # x is the row index and y is the column index. Using <= here allows
        # x == height or y == width, which is already outside the matrix.
        if not (0 <= x < self.height and 0 <= y < self.width):
            return "VOID"

        match levels[self.level_name]["layout"][x][y]:
            case -2:
                return "HIDDEN_PATH"
            case -1:
                return "VOID"
            case 0:
                return "FLOOR"
            case 1:
                return "BLOCK_UPRIGHT"
            case 2:
                return "BLOCK_PRONE"
            case 3:
                return "GLASS_FLOOR"
            case 4:
                return "BUTTON_TYPE_X"
            case 5:
                return "BUTTON_TYPE_HEX"
            case 6:
                return "BUTTON_ONE_TIME_USE"
            case 7:
                return "GOAL"
            case 8:
                return "SPLIT_SWITCH"

    def is_goal(self, position):
        return position == self.goal

    def switch_level(self):
        level_num = reverse_level_menu[self.level_name]
        self.level_name = level_menu[(level_num + 1) % NUM_LEVELS]
        self.level_data = levels[self.level_name]
        self.layout = deepcopy(self.level_data["layout"])
        self.start = self.level_data["start"]
        self.goal = self.level_data["goal"]
        self.button = deepcopy(self.level_data["button"])
        self.split_switches = deepcopy(
            self.level_data.get(
                "split_switches",
                {},
            )
        )
        self.width = len(self.layout[0])
        self.height = len(self.layout)

        return self.level_name
