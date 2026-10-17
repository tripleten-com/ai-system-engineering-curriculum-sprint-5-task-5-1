"""Coldline.

===================

File:              tests/unit/test_student_tests_runner.py
Component:         Unit tests — Student test stage
Purpose:           Prove the student-test stage passes on an empty tests/student and fails
                    on a failing test.
Interacts With:    tests/student_tests.py, pyproject.toml (`poe student-tests`)
Sprint/Task:       Sprint 5 — Project 5 / starter (Task 5.1)
Concepts:          pytest exit codes, an empty starter directory
Tools:             Python 3.12, pytest
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests import student_tests


@pytest.fixture
def student_dir(tmp_path: Path) -> Path:
    """Give the child pytest a directory that is its own rootdir.

    With no config file of its own, the child's rootdir is the common ancestor of the
    working directory and its argument. A repository cloned under the temp directory
    makes that the temp directory itself, and collection then lists every entry there;
    one another process deletes mid-walk fails the run with FileNotFoundError.
    """
    directory = tmp_path / "student"
    directory.mkdir()
    (directory / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    return directory


def test_the_child_run_is_rooted_in_its_own_directory(
    student_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """A repository beside the test directory does not widen what the child collects."""
    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.chdir(repository)
    assert student_tests.run(student_dir) == 0
    assert f"rootdir: {student_dir}" in capfd.readouterr().out


def test_an_empty_directory_passes(student_dir: Path) -> None:
    """The starter has no student tests yet; that is a pass."""
    (student_dir / "__init__.py").write_text("", encoding="utf-8")
    assert student_tests.run(student_dir) == 0


def test_a_failing_test_fails(student_dir: Path) -> None:
    """A failing student test fails the stage."""
    (student_dir / "test_x.py").write_text("def test_x():\n    assert False\n", encoding="utf-8")
    assert student_tests.run(student_dir) == 1


def test_a_passing_test_passes(student_dir: Path) -> None:
    """A passing student test passes the stage."""
    (student_dir / "test_x.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    assert student_tests.run(student_dir) == 0
