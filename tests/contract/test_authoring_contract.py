"""Coldline.

===================

File:              tests/contract/test_authoring_contract.py
Component:         Repository integrity contract
Purpose:           Verifies required Task repository structure and configuration.
Interacts With:    Repository integrity checks and the complete Task tree
Sprint/Task:       Sprint 5 — Project 5 / starter (Task 5.1)
Concepts:          Dependency direction, configuration ownership, repository integrity
Tools:             Python 3.12, pytest
"""

import re
from pathlib import Path

import pytest

from tests.contract import authoring

TASK_ROOT = Path(__file__).resolve().parents[2]
BANNER_PATTERN = re.compile(r"Coldline(?: — Task \d+\.\d+)?\.")
HEADER_FIELDS = (
    "File:",
    "Component:",
    "Purpose:",
    "Interacts With:",
    "Sprint/Task:",
    "Concepts:",
    "Tools:",
)
# Supplied configuration only. The checks marked `authoring` hold the template to its own
# layout, banners and pins; they run in `poe author-verify`, never in `poe contract` or
# `poe verify`, because Project 5 students add their own packages, files and services.
COMMENTABLE_CONFIGURATION = (
    ".devcontainer/post-create.sh",
    "alembic.ini",
    "config/auth.yaml",
    "config/retrieval-baseline.yaml",
    "config/student/retrieval.yaml",
    "docs/governance/risk-register.yaml",
    "docs/security/threat-catalog.yaml",
    "tests/fixtures/credentials/test-values.yaml",
    "tests/fixtures/pii/notes.yaml",
    "tests/fixtures/tokens/fixtures.yaml",
    "infra/profiles/object-store-fidelity.yaml",
    "infra/profiles/vector-engines.yaml",
    "infra/release/manifest.yaml",
    ".devcontainer/start-stack.sh",
    ".dockerignore",
    ".env.example",
    ".gitattributes",
    ".github/workflows/verify.yml",
    ".gitignore",
    ".gitleaks.toml",
    ".semgrepignore",
    "compose.yaml",
    "infra/containers/api.Dockerfile",
    "infra/containers/worker.Dockerfile",
    "infra/observability/alertmanager.yml",
    "infra/observability/alerts.yml",
    "infra/observability/grafana/dashboards/provider.yml",
    "infra/observability/grafana/datasources/datasources.yml",
    "infra/observability/prometheus.yml",
    "infra/postgres/001_opening_checkpoint.sql",
    "infra/postgres/002_retrieval_corpus.sql",
    "infra/postgres/003_idempotency.sql",
    "infra/postgres/004_migration_baseline.sql",
    "infra/scripts/bootstrap.ps1",
    "infra/scripts/bootstrap.sh",
    "infra/scripts/preflight.ps1",
    "infra/scripts/preflight.sh",
    "pyproject.toml",
    "security/gate.yaml",
    "security/scanners.yaml",
    "security/semgrep-rules.yaml",
)


@pytest.mark.authoring
def test_current_repository_satisfies_the_integrity_contract() -> None:
    """Fail when a protected repository invariant drifts."""
    assert authoring.main() == 0


@pytest.mark.authoring
@pytest.mark.parametrize(
    ("dockerfiles", "expected"),
    [
        ({"api": True, "worker": True}, []),
        ({"app": True}, []),
        ({"app": False}, ["app runtime image must declare USER coldline"]),
        ({"api": True, "worker": False}, ["worker runtime image must declare USER coldline"]),
        ({}, ["infra/containers holds no *.Dockerfile runtime image"]),
    ],
)
def test_container_policy_checks_every_runtime_image(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    dockerfiles: dict[str, bool],
    expected: list[str],
) -> None:
    """A Task may replace the api and worker images with its own; each must stay unprivileged."""
    containers = tmp_path / "infra" / "containers"
    containers.mkdir(parents=True)
    for name, unprivileged in dockerfiles.items():
        user = "USER coldline\n" if unprivileged else ""
        (containers / f"{name}.Dockerfile").write_text(
            f'FROM python:3.12-slim\n{user}CMD ["true"]\n', encoding="utf-8"
        )
    monkeypatch.setattr(authoring, "ROOT", tmp_path)
    assert authoring._check_container_policy() == expected


@pytest.mark.parametrize(
    "fixture",
    ["infra/corpus/README.md", "infra/judge/README.md", "infra/profiles/README.md"],
)
def test_supplied_fixtures_carry_a_provenance_and_licence_record(fixture: str) -> None:
    """Every supplied fixture must say where it came from and under what terms."""
    record = (TASK_ROOT / fixture).read_text(encoding="utf-8")
    for required in ("Synthetic", "Licence", "Provenance"):
        assert required in record, f"{fixture} does not state {required.lower()}"


@pytest.mark.authoring
def test_python_files_have_the_student_navigation_banner() -> None:
    """Catch a source file that gives students no ownership or purpose context."""
    failures: list[str] = []
    roots = [TASK_ROOT / "src", TASK_ROOT / "tests", TASK_ROOT / "infra/scripts"]
    for root in roots:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            header = text[:1200]
            missing = [field for field in HEADER_FIELDS if field not in header]
            if not BANNER_PATTERN.search(header):
                missing.insert(0, "Coldline navigation banner")
            if missing:
                failures.append(f"{path.relative_to(TASK_ROOT)}: {', '.join(missing)}")

    assert failures == []


@pytest.mark.authoring
def test_commentable_configuration_files_explain_their_role() -> None:
    """Catch operational files that provide configuration without context."""
    banner = re.compile(r"(?m)^(?:#|--) Coldline(?: - Task \d+\.\d+)?$")
    missing = []
    for relative in COMMENTABLE_CONFIGURATION:
        text = (TASK_ROOT / relative).read_text(encoding="utf-8")
        if not banner.search(text[:1000]):
            missing.append(relative)

    assert missing == []


def test_released_repository_has_no_unresolved_template_tokens() -> None:
    """A student-facing README must not contain an unresolved placeholder."""
    assert authoring._check_unresolved_template_tokens([TASK_ROOT / "README.md"]) == []
