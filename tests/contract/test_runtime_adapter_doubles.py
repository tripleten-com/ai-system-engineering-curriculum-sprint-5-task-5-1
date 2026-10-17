"""Coldline.

===================

File:              tests/contract/test_runtime_adapter_doubles.py
Component:         Contract tests — Runtime adapter verifier doubles
Purpose:           Prove the queue verifier's failing provider fails every port member,
                    including one a later Task adds to ModelProvider.
Interacts With:    tests/contract/runtime_adapters.py, src/ports/model_provider.py
Sprint/Task:       Sprint 5 — Project 5 / starter (Task 5.1)
Concepts:          Protocol extension, test doubles that survive a growing port
Tools:             Python 3.12, pytest
"""

from __future__ import annotations

import pytest

from domain.contracts import ModelRequest
from tests.contract.runtime_adapters import AlwaysFailProvider

# The verifier is curriculum-owned: its doubles are checked in `poe author-verify`, not in
# `poe verify`, so a student who reshapes the worker never sees this file fail.
pytestmark = pytest.mark.authoring


def _request() -> ModelRequest:
    return ModelRequest(
        exception_id="exception-double",
        shipment_id="shipment-double",
        temperature_c=9.2,
        allowed_min_c=2.0,
        allowed_max_c=8.0,
    )


async def test_summarize_fails_with_the_integration_failure() -> None:
    """The published port member keeps its fixed failure."""
    with pytest.raises(TimeoutError, match="integration provider failure"):
        await AlwaysFailProvider().summarize(_request())


async def test_a_member_added_to_the_port_fails_the_same_way() -> None:
    """A method a later Task adds to ModelProvider needs no edit to the double."""
    provider = AlwaysFailProvider()
    with pytest.raises(TimeoutError, match="integration provider failure"):
        await provider.propose(_request())


def test_dunder_lookups_are_not_answered() -> None:
    """Copying, pickling and introspection still see an ordinary object."""
    assert not hasattr(AlwaysFailProvider(), "__deepcopy__")
