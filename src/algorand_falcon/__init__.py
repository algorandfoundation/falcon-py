"""algorand-falcon: Python bindings for the Algorand deterministic Falcon (det1024)
post-quantum signature scheme.

Each parameter set is a namespace module holding `Signer`, `Verifier`, and its
sizes; the exceptions are shared at the top level. The C-mirroring layer stays
private, so the only supported way to reach a det1024 primitive is through
`falcon1024.Signer` or `falcon1024.Verifier`.

Example
-------
>>> from algorand_falcon import falcon1024
>>> signer = falcon1024.Signer.generate()
>>> sig = signer.sign(b"hello world")
>>> signer.verifying_key().verify(b"hello world", sig)  # no exception == valid
"""

from __future__ import annotations

from . import falcon1024
from .exceptions import (
    FalconError,
    InvalidSignature,
    KeygenError,
    SigningError,
)

# Managed by python-semantic-release (version_variables in pyproject.toml).
__version__ = "0.4.0"

__all__ = [
    # version
    "__version__",
    # parameter-set namespaces
    "falcon1024",
    # exceptions
    "FalconError",
    "InvalidSignature",
    "KeygenError",
    "SigningError",
]
