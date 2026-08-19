"""Shared fixtures and helpers for the algorand-falcon test suite."""

from __future__ import annotations

import pytest

from algorand_falcon import falcon1024

# A fixed seed so the keypair (and thus signatures) are stable across the suite.
SEED = bytes(range(32))


@pytest.fixture(scope="session")
def signer() -> falcon1024.Signer:
    return falcon1024.Signer.generate(seed=SEED)


@pytest.fixture(scope="session")
def verifier(signer: falcon1024.Signer) -> falcon1024.Verifier:
    return signer.verifying_key()
