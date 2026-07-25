from __future__ import annotations

import json
from pathlib import Path

from game.levels import EMBEDDED_LEVELS


OUTPUT_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "levels"
)


def _coordinate(value):
    return [value[0], value[1]]


def _flatten_coordinates(value):
    if (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    ):
        return [_coordinate(value)]

    result = []

    for item in value:
        result.extend(_flatten_coordinates(item))

    return result


def export_levels():
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for level_name, data in EMBEDDED_LEVELS.items():
        buttons = []

        for position, config in (data.get("button") or {}).items():
            initial_state, bridges = config
            buttons.append(
                {
                    "position": _coordinate(position),
                    "initial_state": initial_state,
                    "bridges": _flatten_coordinates(bridges),
                }
            )

        split_switches = [
            {
                "position": _coordinate(position),
                "destinations": [
                    _coordinate(destination)
                    for destination in destinations
                ],
            }
            for position, destinations in data.get(
                "split_switches",
                {},
            ).items()
        ]

        output = {
            "schema_version": 1,
            "name": level_name,
            "layout": data["layout"],
            "start": _coordinate(data["start"]),
            "goal": _coordinate(data["goal"]),
            "buttons": buttons,
            "split_switches": split_switches,
        }

        output_path = (
            OUTPUT_DIRECTORY
            / f"{level_name.lower()}.json"
        )
        output_path.write_text(
            json.dumps(output, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Exported {output_path}")


if __name__ == "__main__":
    export_levels()
