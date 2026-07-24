from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Callable

from game.block import Block
from game.board import Board
from search_algorithms.a_star import a_star
from search_algorithms.breadth_first_search import breadth_first_search
from search_algorithms.depth_first_search import depth_first_search
from search_algorithms.problem import Problem
from search_algorithms.search_runner import run_search
from search_algorithms.uniform_cost_search import uniform_cost_search


Solver = Callable[[Problem], Any]


ALGORITHMS: dict[str, Solver] = {
    "BFS": breadth_first_search,
    "DFS": depth_first_search,
    "UCS": uniform_cost_search,
    "A*": a_star,
}


CSV_FIELDS = [
    "run",
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


def create_problem(level_name: str) -> Problem:
    """
    Create a fresh independent problem for one benchmark run.

    A new Board and Block are required for every algorithm so that
    all algorithms start from exactly the same level configuration.
    """
    board = Board(level_name)
    block = Block(*board.level.start)

    board.refresh_layout(block)

    return Problem(
        block,
        board,
    )


def benchmark_once(
    level_name: str,
    algorithm_name: str,
    solver: Solver,
    run_number: int,
) -> dict[str, object]:
    """
    Run one algorithm once and return one CSV-compatible row.
    """
    problem = create_problem(level_name)

    try:
        result = run_search(
            algorithm_name,
            solver,
            problem,
        )

        return {
            "run": run_number,
            "level": level_name,
            "algorithm": algorithm_name,
            "solved": result.solved,
            "search_time_ms": round(result.search_time_ms, 6),
            "peak_memory_mb": round(result.peak_memory_mb, 6),
            "expanded_nodes": result.expanded_nodes,
            "solution_length": result.solution_length,
            "total_cost": (
                result.total_cost
                if result.solved
                else ""
            ),
            "actions": " ".join(result.actions),
            "error": "",
        }

    except Exception as error:
        return {
            "run": run_number,
            "level": level_name,
            "algorithm": algorithm_name,
            "solved": False,
            "search_time_ms": "",
            "peak_memory_mb": "",
            "expanded_nodes": problem.expanded_nodes,
            "solution_length": "",
            "total_cost": "",
            "actions": "",
            "error": f"{type(error).__name__}: {error}",
        }


def save_results(
    rows: list[dict[str, object]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
        )

        writer.writeheader()
        writer.writerows(rows)


def print_result(row: dict[str, object]) -> None:
    if row["error"]:
        print(
            f"{row['level']:8} | "
            f"{row['algorithm']:4} | "
            f"ERROR | {row['error']}"
        )
        return

    solved_text = "YES" if row["solved"] else "NO"

    print(
        f"{row['level']:8} | "
        f"{row['algorithm']:4} | "
        f"Solved: {solved_text:3} | "
        f"Time: {str(row['search_time_ms']):>12} ms | "
        f"Memory: {str(row['peak_memory_mb']):>10} MB | "
        f"Expanded: {str(row['expanded_nodes']):>8} | "
        f"Length: {str(row['solution_length']):>5}"
    )


def run_benchmark(
    levels: list[str],
    algorithm_names: list[str],
    repeats: int,
    output_path: Path,
) -> list[dict[str, object]]:
    if repeats < 1:
        raise ValueError(
            "repeats must be at least 1."
        )

    unknown_algorithms = [
        name
        for name in algorithm_names
        if name not in ALGORITHMS
    ]

    if unknown_algorithms:
        raise ValueError(
            f"Unknown algorithms: {unknown_algorithms}"
        )

    rows: list[dict[str, object]] = []

    print()
    print("Bloxorz Search Benchmark")
    print("-" * 105)

    for level_name in levels:
        for algorithm_name in algorithm_names:
            solver = ALGORITHMS[algorithm_name]

            for run_number in range(1, repeats + 1):
                row = benchmark_once(
                    level_name,
                    algorithm_name,
                    solver,
                    run_number,
                )

                rows.append(row)
                print_result(row)

    save_results(
        rows,
        output_path,
    )

    print("-" * 105)
    print(f"Saved CSV: {output_path.resolve()}")

    return rows


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Bloxorz search algorithms and export "
            "performance measurements to CSV."
        )
    )

    parser.add_argument(
        "--levels",
        nargs="+",
        default=["LEVEL1"],
        help="Levels to benchmark, for example LEVEL1 LEVEL2.",
    )

    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=list(ALGORITHMS),
        default=list(ALGORITHMS),
        help="Algorithms to benchmark.",
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Number of repetitions for each algorithm and level.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "benchmark_results/search_results.csv"
        ),
        help="Output CSV path.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    run_benchmark(
        levels=arguments.levels,
        algorithm_names=arguments.algorithms,
        repeats=arguments.repeats,
        output_path=arguments.output,
    )


if __name__ == "__main__":
    main()