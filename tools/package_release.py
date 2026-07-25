from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "backup",
    "reference",
    "dist",
    "release",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
}

EXCLUDED_FILES = {
    "audit_test_results.txt",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a clean source submission without Git data, "
            "virtual environments, caches, backups, or cloned references."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "--name",
        default="Bloxorz_AI_Source",
    )
    return parser.parse_args()


def should_exclude(
    relative_path: Path,
) -> bool:
    if any(
        part in EXCLUDED_DIRS
        for part in relative_path.parts
    ):
        return True

    if relative_path.name in EXCLUDED_FILES:
        return True

    return (
        relative_path.suffix.lower()
        in EXCLUDED_SUFFIXES
    )


def copy_project(
    project_root: Path,
    destination: Path,
) -> None:
    for source in project_root.rglob("*"):
        relative = source.relative_to(
            project_root
        )

        if should_exclude(relative):
            continue

        target = destination / relative

        if source.is_dir():
            target.mkdir(
                parents=True,
                exist_ok=True,
            )
        else:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(source, target)


def create_zip(
    source_directory: Path,
    zip_path: Path,
) -> None:
    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:
        for file_path in source_directory.rglob(
            "*"
        ):
            if file_path.is_file():
                archive.write(
                    file_path,
                    arcname=(
                        Path(source_directory.name)
                        / file_path.relative_to(
                            source_directory
                        )
                    ),
                )


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()

    if not (project_root / "main.py").exists():
        raise FileNotFoundError(
            "Run this tool from the project root "
            "or pass --project-root."
        )

    dist = project_root / "dist"
    release_dir = dist / args.name
    zip_path = dist / f"{args.name}.zip"

    if release_dir.exists():
        shutil.rmtree(release_dir)

    if zip_path.exists():
        zip_path.unlink()

    release_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    copy_project(
        project_root,
        release_dir,
    )
    create_zip(
        release_dir,
        zip_path,
    )

    print(
        f"Clean folder: {release_dir}"
    )
    print(
        f"Clean ZIP: {zip_path}"
    )


if __name__ == "__main__":
    main()
