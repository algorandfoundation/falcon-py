# 7. Parameter-set namespace modules

Date: 2026-08-11

## Status

Accepted. Refines the surface shape of [ADR 0006](0006-minimal-public-surface.md) without changing its philosophy: the supported operations remain generate, sign, verify.

## Context

ADR 0006 exposed `FalconSigner`, `FalconVerifier`, and three size constants flat at the top level. That shape has one latent problem: every one of those names silently means "det1024". If a second parameter set ever ships, the bare names become ambiguous, and top-level constants like `PUBLIC_KEY_SIZE` become wrong for one set or the other.

Grouping each parameter set under a named namespace solves this, and the question was what the idiomatic Python shape for that is.

Precedents pull in two directions. PyNaCl namespaces by module with unprefixed classes inside (`nacl.signing.SigningKey`). pyca/cryptography namespaces by module but prefixes the classes anyway (`ed25519.Ed25519PrivateKey`), and its ML-DSA module, the closest analogue (a post-quantum lattice scheme with three parameter sets), uses a single module with prefixed classes (`MLDSA44PrivateKey`), because `from module import Class` is the dominant idiom and it erases the module qualifier at use sites.

A speculative-generality concern was weighed explicitly: the vendored C library implements deterministic mode for 1024 only (`falcon_det1024_*`; there is no det512 anywhere upstream), so no sibling can ship without upstream C work. The namespace therefore has to stand on its own merits, not on a promised sibling.

## Decision

Expose one namespace module per parameter set. Today that is exactly one: `falcon1024`, holding `Signer`, `Verifier`, `PUBLIC_KEY_SIZE`, `PRIVATE_KEY_SIZE`, and `COMPRESSED_SIG_MAX_SIZE`. The top level keeps only `__version__`, the bound namespace, and the four shared exceptions. `api.py` and `constants.py` are absorbed into `falcon1024.py`.

- **A submodule, not a class or object acting as a namespace.** Modules are Python's namespace construct: importable, transparent to type checkers and IDEs, and a module can later become a package with identical import paths.
- **Unprefixed `Signer` / `Verifier`, with discipline.** This is PyNaCl's shape rather than pyca's, chosen for how it reads at the call site (`falcon1024.Signer` over `falcon1024.Falcon1024Signer`). The discipline that makes it safe: the classes are never re-exported at the top level (pinned by `test_public_surface.py`), documentation examples are always module-qualified, and the reprs name the namespace (`falcon1024.Signer(public_key=<1793 bytes>)`).
- **Constants stay per-set, inside the namespace.** Sizes are parameter-set properties; Falcon-512's differ. They are defined in `_bindings.py`, which needs them for its length checks, and re-exported; the reverse arrow would be an import cycle.
- **Exceptions stay shared at the top level**, matching `cryptography.exceptions` and `nacl.exceptions`: code catching `InvalidSignature` should not care which parameter set produced it.
- **The namespace surface is pinned as a set contract.** `test_public_surface.py` holds every listed namespace to the identical name set, so a future sibling (`det512`, should upstream ever define one) is added by listing its module and cannot drift.
- **No sibling is promised.** Docs do not advertise a future `falcon512`; the structure merely leaves room.

The name `falcon1024` (rather than `det1024`, which matches the C prefix and the fact that these signatures are incompatible with standard salted Falcon-1024) follows the surrounding Algorand ecosystem: `py-algorand-sdk`'s `Falcon1024TransactionSigner` names the same det1024 scheme. The incompatibility is stated in the module docstring and README instead of the name.

## Consequences

Breaking change to the 0.3.0 surface: `FalconSigner` → `falcon1024.Signer`, `FalconVerifier` → `falcon1024.Verifier`, top-level constants → `falcon1024.*`. The package is Alpha with no released consumers; the cost is bounded, and it lands together with the distribution rename so the surface breaks once, not twice.

Pickles of 0.3.0 objects do not load in 0.4.0 (the class path changed). Unpickle with the old version and re-store raw key bytes; pickling long-lived private keys is discouraged regardless.

`from temp_falcon.falcon1024 import Signer` remains possible and unambiguous while one set exists; users who do this across a future second set take on the aliasing themselves. The KATs, the cdef set-equality test, and the version-metadata test are unchanged.
