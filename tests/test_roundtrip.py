"""Sign/verify roundtrip and signer/verifier behaviour."""

from __future__ import annotations

import os

import pytest

from temp_falcon import falcon1024

MESSAGES = [
    b"",
    b"\x00",
    b"hello world",
    os.urandom(32),
    os.urandom(1024),
    b"\xff" * 4096,
]


@pytest.mark.parametrize("message", MESSAGES)
def test_sign_verify_roundtrip(
    signer: falcon1024.Signer, verifier: falcon1024.Verifier, message: bytes
) -> None:
    sig = signer.sign(message)
    assert isinstance(sig, bytes)
    assert 2 <= len(sig) <= falcon1024.COMPRESSED_SIG_MAX_SIZE
    assert sig[0] == (0x3A | 0x80)  # det1024 compressed header
    assert sig[1] == 0  # salt version
    # verify() returns None on success and raises on failure.
    assert verifier.verify(message, sig) is None
    assert verifier.is_valid(message, sig) is True


def test_verifier_from_public_key(signer: falcon1024.Signer) -> None:
    msg = b"reconstructed verifier"
    sig = signer.sign(msg)
    v = falcon1024.Verifier(signer.public_key)
    v.verify(msg, sig)


def test_signer_reconstructed_from_private_key(signer: falcon1024.Signer) -> None:
    # The constructor takes only the private key and recomputes the public one,
    # so a signer cannot hold a public key that belongs to a different keypair.
    rebuilt = falcon1024.Signer(signer.private_key)
    msg = b"same key, same signature"
    assert rebuilt.sign(msg) == signer.sign(msg)
    assert rebuilt.public_key == signer.public_key


def test_signer_cannot_be_handed_a_public_key() -> None:
    # The public key is derived, never supplied, so a signer holding a public
    # key from a different keypair is unrepresentable: the constructor takes no
    # second argument, positionally or by keyword.
    a = falcon1024.Signer.generate(seed=b"keypair-a")
    b = falcon1024.Signer.generate(seed=b"keypair-b")
    with pytest.raises(TypeError):
        falcon1024.Signer(a.private_key, b.public_key)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        falcon1024.Signer(  # type: ignore[call-arg]
            a.private_key, public_key=b.public_key
        )


def test_verifier_equality_and_hash(signer: falcon1024.Signer) -> None:
    a = signer.verifying_key()
    b = falcon1024.Verifier(signer.public_key)
    assert a == b
    assert hash(a) == hash(b)
    assert a != falcon1024.Signer.generate(seed=bytes([1] * 32)).verifying_key()
    assert a != "not a verifier"


def test_repr_hides_secret(signer: falcon1024.Signer) -> None:
    # An exact match is required because a template that interpolated the key
    # itself would still contain the word "bytes".
    assert (
        repr(signer)
        == f"falcon1024.Signer(public_key=<{falcon1024.PUBLIC_KEY_SIZE} bytes>)"
    )
    assert (
        repr(signer.verifying_key())
        == f"falcon1024.Verifier(public_key=<{falcon1024.PUBLIC_KEY_SIZE} bytes>)"
    )
    assert signer.private_key.hex() not in repr(signer)
