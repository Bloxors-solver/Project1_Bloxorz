from __future__ import annotations

from pathlib import Path
import sys


RENDERER = Path("game/renderer.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly 1 match, found {count}. "
            "The repository version may differ from the expected main branch."
        )
    return text.replace(old, new, 1)


def main() -> int:
    if not RENDERER.exists():
        print(
            "ERROR: game/renderer.py was not found. "
            "Run this script from the repository root.",
            file=sys.stderr,
        )
        return 1

    text = RENDERER.read_text(encoding="utf-8")

    old_import = """from search_algorithms.comparison import (
    run_comparison,
    save_comparison_csv,
    select_replay_result,
)
"""
    new_import = """from search_algorithms.comparison import (
    run_comparison,
    save_comparison_csv,
)
"""
    text = replace_once(
        text,
        old_import,
        new_import,
        "comparison import",
    )

    old_buttons = """        self.comparison_replay_button = Button(
            295,
            630,
            225,
            54,
            "REPLAY A*",
            SUCCESS,
            (108, 226, 170),
            WHITE,
            27,
        )
        self.comparison_back_button = Button(
            580,
            630,
            225,
            54,
            "BACK",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            27,
        )
"""
    new_buttons = """        # One replay button for each required comparison algorithm.
        # A button is shown only when that algorithm solved the level.
        self.comparison_replay_buttons = {
            algorithm: Button(
                x,
                630,
                170,
                54,
                f"REPLAY {algorithm}",
                SUCCESS,
                (108, 226, 170),
                WHITE,
                23,
            )
            for algorithm, x in (
                ("BFS", 55),
                ("DFS", 245),
                ("UCS", 435),
                ("A*", 625),
            )
        }
        self.comparison_back_button = Button(
            845,
            630,
            170,
            54,
            "BACK",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            27,
        )
"""
    text = replace_once(
        text,
        old_buttons,
        new_buttons,
        "comparison buttons",
    )

    old_handler = """    def handle_comparison(self, mouse_pos):
        self.comparison_back_button.update(mouse_pos)
        self.comparison_replay_button.update(mouse_pos)

        if self.comparison_back_button.is_clicked(mouse_pos):
            self.game_state = ALGORITHMS
            return

        if self.comparison_replay_button.is_clicked(mouse_pos):
            replay_result = select_replay_result(
                self.comparison_results,
                preferred_algorithm="A*",
            )

            if replay_result is None:
                return

            replay_level = self.comparison_level
            self.initialize_level(
                replay_level,
                AI=False,
            )

            self.search_result = replay_result
            self.search_result_level = replay_level
            self.solution = deque(replay_result.actions)
            self.algorithm = replay_result.algorithm.lower()
            self.algorithm_completed = True
            self.game_state = AI_PLAYING
"""
    new_handler = """    def _comparison_result_for(self, algorithm):
        \"\"\"Return the solved result for exactly one algorithm.\"\"\"
        for entry in self.comparison_results:
            if (
                entry.algorithm == algorithm
                and entry.solved
                and entry.result is not None
            ):
                return entry.result

        return None

    def _start_comparison_replay(self, replay_result):
        \"\"\"Replay one selected comparison result from a fresh level.\"\"\"
        replay_level = self.comparison_level

        if replay_level is None:
            return

        self.initialize_level(
            replay_level,
            AI=False,
        )

        self.search_result = replay_result
        self.search_result_level = replay_level
        self.solution = deque(replay_result.actions)
        self.algorithm = replay_result.algorithm.lower()
        self.algorithm_completed = True
        self.game_state = AI_PLAYING

    def handle_comparison(self, mouse_pos):
        self.comparison_back_button.update(mouse_pos)

        if self.comparison_back_button.is_clicked(mouse_pos):
            self.game_state = ALGORITHMS
            return

        for algorithm, button in (
            self.comparison_replay_buttons.items()
        ):
            replay_result = self._comparison_result_for(
                algorithm
            )

            if replay_result is None:
                continue

            button.update(mouse_pos)

            if button.is_clicked(mouse_pos):
                self._start_comparison_replay(
                    replay_result
                )
                return
"""
    text = replace_once(
        text,
        old_handler,
        new_handler,
        "comparison click handler",
    )

    old_draw = """        if self.comparison_results:
            self.comparison_replay_button.draw(
                self.screen
            )

        self.comparison_back_button.draw(self.screen)
"""
    new_draw = """        for algorithm, button in (
            self.comparison_replay_buttons.items()
        ):
            if self._comparison_result_for(algorithm) is not None:
                button.draw(self.screen)

        self.comparison_back_button.draw(self.screen)
"""
    text = replace_once(
        text,
        old_draw,
        new_draw,
        "comparison button drawing",
    )

    backup = RENDERER.with_suffix(".py.bak")
    if not backup.exists():
        backup.write_text(
            RENDERER.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    RENDERER.write_text(text, encoding="utf-8")

    print("Updated game/renderer.py")
    print(f"Backup: {backup}")
    print("Next commands:")
    print("  python -m py_compile game/renderer.py")
    print('  python -m unittest discover -s tests -p "test_*.py" -v')
    print("  python main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
