"""Coldline.

===================

File:              tests/contract/test_repository_structure.py
Component:         Repository structure contract
Purpose:           Keeps the supplied tree in place while Project 5 students add their own.
Interacts With:    Task root, src packages, docs, infrastructure, migrations, schemas, and tests
Sprint/Task:       Sprint 4 — Project 4 / Task 4.5; Project 5 starter (Task 5.1)
Concepts:          Navigability, package ownership, repository integrity
Tools:             Python 3.12, pytest
"""

import subprocess
from pathlib import Path, PurePosixPath

TASK_ROOT = Path(__file__).resolve().parents[2]
# `migrations` joins the visible tree at Task 2.6 and `config` at Task 2.7,
# where a student's work is one configuration change rather than a change to
# the application source. `schemas` joins at Task 4.3: the supplied output schema
# the guardrail enforces lives beside the code, not under docs/.
# Task 4.5 adds `security`: the gate thresholds, the local Semgrep rules, the scanner pins
# and the seed directory the security gate reads.
VISIBLE_CONTENT_DIRECTORIES = {
    "config",
    "docs",
    "infra",
    "loadtest",
    "migrations",
    "schemas",
    "security",
    "src",
    "tests",
}
# Task 4.3 adds `common`: the audit sink both the API and the worker use, which
# neither service may import from the other.
SOURCE_PACKAGES = {"api", "worker", "domain", "ports", "adapters", "common"}
IGNORED_PARTS = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tools",
    ".venv",
    "__pycache__",
}


def test_visible_content_is_grouped_into_the_expected_learning_zones() -> None:
    """Keep every supplied root directory; Project 5 students may add their own."""
    actual = {
        path.parts[0]
        for path in _tracked_task_paths()
        if len(path.parts) > 1 and not path.parts[0].startswith(".")
    }

    assert VISIBLE_CONTENT_DIRECTORIES <= actual, sorted(VISIBLE_CONTENT_DIRECTORIES - actual)


def test_source_tree_keeps_the_six_supplied_flat_packages() -> None:
    """Keep the six supplied packages flat under src/; a student package sits beside them.

    Project 5 students build the agent themselves, for example as `src/agent/`, so the
    tree may grow. A supplied package that disappears still fails, and so does code
    placed directly in `src/` instead of in a package.
    """
    tracked = _tracked_task_paths()
    packages = {path.parts[1] for path in tracked if len(path.parts) > 2 and path.parts[0] == "src"}
    loose_files = sorted(
        str(path) for path in tracked if len(path.parts) == 2 and path.parts[0] == "src"
    )

    assert SOURCE_PACKAGES <= packages, sorted(SOURCE_PACKAGES - packages)
    assert not loose_files, loose_files


def _tracked_task_paths() -> set[PurePosixPath]:
    """Return Task-relative paths in the Task repository."""
    repository = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=TASK_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if repository.returncode != 0:
        # When Git metadata is unavailable, inspect materialized files while
        # ignoring only local tool output created after installation.
        return {
            PurePosixPath(path.relative_to(TASK_ROOT).as_posix())
            for path in TASK_ROOT.rglob("*")
            if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
        }

    repository_root = Path(repository.stdout.strip())
    task_prefix = TASK_ROOT.relative_to(repository_root).as_posix()
    output = subprocess.run(
        ["git", "ls-files"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if task_prefix == ".":
        return {PurePosixPath(path) for path in output}
    prefix = f"{task_prefix}/"
    return {PurePosixPath(path.removeprefix(prefix)) for path in output if path.startswith(prefix)}
