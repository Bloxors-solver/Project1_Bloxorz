from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev


NUMERIC_FIELDS = (
    "search_time_ms",
    "peak_memory_mb",
    "expanded_nodes",
    "solution_length",
    "total_cost",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Combine benchmark CSV files, calculate summary statistics, "
            "and generate report-ready charts."
        )
    )
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        required=True,
        help="One or more benchmark CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark_results/final"),
    )
    return parser.parse_args()


def read_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            rows.extend(csv.DictReader(csv_file))

    return [
        row
        for row in rows
        if row.get("solved", "").lower()
        in {"true", "yes", "1"}
        and not row.get("error")
    ]


def numeric_values(
    rows: list[dict[str, str]],
    field: str,
) -> list[float]:
    values: list[float] = []

    for row in rows:
        value = row.get(field, "").strip()
        if value:
            values.append(float(value))

    return values


def summarize(
    rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    groups: dict[
        tuple[str, str],
        list[dict[str, str]],
    ] = defaultdict(list)

    for row in rows:
        groups[
            (row["level"], row["algorithm"])
        ].append(row)

    summary: list[dict[str, object]] = []

    for (level, algorithm), group_rows in sorted(
        groups.items()
    ):
        record: dict[str, object] = {
            "level": level,
            "algorithm": algorithm,
            "runs": len(group_rows),
        }

        for field in NUMERIC_FIELDS:
            values = numeric_values(
                group_rows,
                field,
            )

            if not values:
                record[f"{field}_mean"] = ""
                record[f"{field}_median"] = ""
                record[f"{field}_stdev"] = ""
                continue

            record[f"{field}_mean"] = round(
                mean(values),
                6,
            )
            record[f"{field}_median"] = round(
                median(values),
                6,
            )
            record[f"{field}_stdev"] = round(
                pstdev(values),
                6,
            )

        summary.append(record)

    return summary


def write_summary(
    rows: list[dict[str, object]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "level",
        "algorithm",
        "runs",
    ]

    for field in NUMERIC_FIELDS:
        fieldnames.extend(
            [
                f"{field}_mean",
                f"{field}_median",
                f"{field}_stdev",
            ]
        )

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
        writer.writerows(rows)


def create_chart(
    summary: list[dict[str, object]],
    field: str,
    output_path: Path,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError(
            "Install chart dependencies with: "
            "python -m pip install -r requirements-report.txt"
        ) from error

    labels = [
        f"{row['level']}\n{row['algorithm']}"
        for row in summary
        if row.get(f"{field}_mean") != ""
    ]
    values = [
        float(row[f"{field}_mean"])
        for row in summary
        if row.get(f"{field}_mean") != ""
    ]

    if not values:
        return

    figure_width = max(
        8,
        len(labels) * 0.75,
    )
    plt.figure(figsize=(figure_width, 5))
    plt.bar(labels, values)
    plt.title(
        field.replace("_", " ").title()
    )
    plt.ylabel(
        field.replace("_", " ").title()
    )
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_rows = read_rows(args.input)
    summary = summarize(raw_rows)

    summary_path = (
        args.output_dir / "summary.csv"
    )
    write_summary(
        summary,
        summary_path,
    )

    for field in NUMERIC_FIELDS:
        create_chart(
            summary,
            field,
            args.output_dir
            / f"{field}.png",
        )

    print(
        f"Summary: {summary_path.resolve()}"
    )
    print(
        f"Charts: {args.output_dir.resolve()}"
    )


if __name__ == "__main__":
    main()
