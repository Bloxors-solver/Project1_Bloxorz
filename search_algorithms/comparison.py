from __future__ import annotations

import csv
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from game.block import Block
from game.board import Board

from .a_star import a_star
from .breadth_first_search import breadth_first_search
from .depth_first_search import depth_first_search
from .problem import Problem
from .search_result import SearchResult
from .search_runner import run_search
from .uniform_cost_search import uniform_cost_search


Solver = Callable[[Problem], object]
ProgressCallback = Callable[[str, int, int], None]


CORE_ALGORITHMS: tuple[
    tuple[str, Solver],
    ...,
] = (
    ("BFS", breadth_first_search),
    ("DFS", depth_first_search),
    ("UCS", uniform_cost_search),
    ("A*", a_star),
)


@dataclass(frozen=True, slots=True)
class ComparisonEntry:
    algorithm: str
    result: SearchResult | None
    error: str = ""

    @property
    def solved(self) -> bool:
        return (
            self.result is not None
            and self.result.solved
        )


def create_problem(level_name: str) -> Problem:
    """
    Create a fresh board and block so each algorithm receives exactly
    the same initial level state.
    """
    board = Board(level_name)
    block = Block(*board.level.start)
    board.refresh_layout(block)

    return Problem(
        block,
        board,
        layout_only=not bool(board.level.button),
    )


def run_comparison(
    level_name: str,
    algorithms: Sequence[
        tuple[str, Solver]
    ] = CORE_ALGORITHMS,
    progress_callback: ProgressCallback | None = None,
) -> list[ComparisonEntry]:
    entries: list[ComparisonEntry] = []
    total = len(algorithms)

    for index, (algorithm_name, solver) in enumerate(
        algorithms,
        start=1,
    ):
        if progress_callback is not None:
            progress_callback(
                algorithm_name,
                index,
                total,
            )

        problem = create_problem(level_name)

        try:
            result = run_search(
                algorithm_name,
                solver,
                problem,
            )

            entries.append(
                ComparisonEntry(
                    algorithm=algorithm_name,
                    result=result,
                )
            )

        except Exception as error:
            entries.append(
                ComparisonEntry(
                    algorithm=algorithm_name,
                    result=None,
                    error=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                )
            )

    return entries


def save_comparison_csv(
    entries: Sequence[ComparisonEntry],
    level_name: str,
    output_directory: Path | str = (
        "benchmark_results"
    ),
) -> Path:
    output_directory = Path(output_directory)
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"gui_comparison_{level_name}.csv"
    )

    fieldnames = [
        "level",
        "algorithm",
        "solved",
        "search_time_ms",
        "peak_memory_mb",
        "expanded_nodes",
        "solution_length",
        "total_cost",
        "actions",
        "error",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for entry in entries:
            result = entry.result

            writer.writerow(
                {
                    "level": level_name,
                    "algorithm": entry.algorithm,
                    "solved": (
                        result.solved
                        if result is not None
                        else False
                    ),
                    "search_time_ms": (
                        round(
                            result.search_time_ms,
                            6,
                        )
                        if result is not None
                        else ""
                    ),
                    "peak_memory_mb": (
                        round(
                            result.peak_memory_mb,
                            6,
                        )
                        if result is not None
                        else ""
                    ),
                    "expanded_nodes": (
                        result.expanded_nodes
                        if result is not None
                        else ""
                    ),
                    "solution_length": (
                        result.solution_length
                        if result is not None
                        else ""
                    ),
                    "total_cost": (
                        result.total_cost
                        if (
                            result is not None
                            and result.solved
                        )
                        else ""
                    ),
                    "actions": (
                        " ".join(result.actions)
                        if result is not None
                        else ""
                    ),
                    "error": entry.error,
                }
            )

    return output_path


def select_replay_result(
    entries: Sequence[ComparisonEntry],
    preferred_algorithm: str = "A*",
) -> SearchResult | None:
    for entry in entries:
        if (
            entry.algorithm == preferred_algorithm
            and entry.solved
        ):
            return entry.result

    solved_results = [
        entry.result
        for entry in entries
        if entry.solved
        and entry.result is not None
    ]

    if not solved_results:
        return None

    return min(
        solved_results,
        key=lambda result: (
            result.solution_length,
            result.search_time_ms,
        ),
    )
