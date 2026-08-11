"""The exact det1024 sizes, resolved from the C header macros in API mode."""

from __future__ import annotations

from temp_falcon import falcon1024


def test_sizes_match_spec() -> None:
    assert falcon1024.PUBLIC_KEY_SIZE == 1793
    assert falcon1024.PRIVATE_KEY_SIZE == 2305
    assert falcon1024.COMPRESSED_SIG_MAX_SIZE == 1423
