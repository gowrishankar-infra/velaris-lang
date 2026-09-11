# Security policy

Velaris takes "you can trust code you didn't write" seriously - that
includes trusting the compiler itself. [THREAT_MODEL.md](THREAT_MODEL.md)
says what is and is not defended against; this file says how to
report, what is promised in return, and how to check that what you
downloaded is what was released.

## Reporting a vulnerability

Please do NOT open a public issue for security problems. Instead, use
GitHub's private reporting: **Security tab -> Report a vulnerability**
on this repository. You will get a response within a few days.

In scope: anything that makes Velaris's guarantees lie - an effect the
checker misses, a "proven" promise that can actually break at runtime,
a way past `--allow`, a sandbox escape through the playground, or
unsafe behavior in `fetch` / `read_file` / `write_file`. From 3.4 also:
a way into the HTTP door without its token, a way past either door's
`--max-allow`, the token appearing in a log, an error message, a
process argument or a program's environment, and a changed MCP tool
description that `velaris mcp-verify` passes. From 4.0 also: a run
through either door that gets more time or memory than its operator's
`--max-timeout` or `--max-memory-mb`, and a change to a repository's
code that needs more than its `velaris.capabilities` declares while
`velaris capabilities check` passes it.

## Soundness reports are security reports

If the prover claims something is proven and you can make it false at
runtime, that is a vulnerability in this language's core promise.
These reports get top priority.

## Standing challenge

Anyone who does either of these is credited by name in
[CHANGELOG.md](CHANGELOG.md) and in [HALL_OF_FAME.md](HALL_OF_FAME.md),
and the report is treated as a security issue and fixed within a week:

1. **Make Velaris report "proven"** (in `velaris check`, `velaris
   proofs`, `velaris explain`, `velaris audit` or the library) **for a
   promise that is false at runtime.** A `requires`, `ensures` or
   `invariant` that the compiler marks proven and that a run under
   `--no-native` or with native code then violates, or a division or
   list read the compiler passed that then fails with E403 or E602
   without a runtime-check warning having been issued.

2. **Escape `--allow io`.** A program run with `velaris program.vel
   --allow io` (or `velaris.run(source, allow={"io"})`) that reads or
   writes a file, reaches the network, or calls a Python module -
   including one outside a named `ffi:` list - and carries on.
   Reading the environment through `env()` does not count: `io`
   includes it, and THREAT_MODEL.md says so.

There is no money. There is credit, in the file every reader sees, and
a fix within the week, recorded in the changelog with what was found
and what was wrong. Report through the private channel above so the
fix ships before the details do; the credit is public either way.

What is not in scope of the challenge, because it is documented as not
defended: anything a granted `ffi` module does, resource use below a
limit, the meaning of printed text, the memory cap on macOS (where
RLIMIT_AS is best-effort; it is enforced on Linux and, since 3.1, on
Windows through a job object), and programs not written in Velaris.

## Verifying a download

Every artifact of a release from v2.63 onward is signed keylessly
through sigstore by the release workflow itself, so the signature
proves the file was built by
`.github/workflows/release.yml` in this repository at that tag. The
identity to check against is, for a release `vX.Y`:

    https://github.com/gowrishankar-infra/velaris-lang/.github/workflows/release.yml@refs/tags/vX.Y

with the OIDC issuer `https://token.actions.githubusercontent.com`.

**The wheel and the sdist** carry a sigstore bundle
(`<file>.sigstore.json`, holding the signature and the certificate
together). With `pip install sigstore`:

    sigstore verify identity \
      --bundle velaris_lang-2.63.0-py3-none-any.whl.sigstore.json \
      --cert-identity https://github.com/gowrishankar-infra/velaris-lang/.github/workflows/release.yml@refs/tags/v2.63 \
      --cert-oidc-issuer https://token.actions.githubusercontent.com \
      velaris_lang-2.63.0-py3-none-any.whl

**The three executables and `velaris.mcpb`** carry a detached
signature (`.sig`), the certificate (`.pem`) and the same bundle
(`.sigstore.json`). With [cosign](https://github.com/sigstore/cosign):

    cosign verify-blob velaris-linux \
      --bundle velaris-linux.sigstore.json \
      --certificate-identity https://github.com/gowrishankar-infra/velaris-lang/.github/workflows/release.yml@refs/tags/v2.63 \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com

or, with the detached files:

    cosign verify-blob velaris-linux \
      --signature velaris-linux.sig \
      --certificate velaris-linux.pem \
      --certificate-identity https://github.com/gowrishankar-infra/velaris-lang/.github/workflows/release.yml@refs/tags/v2.63 \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com

**The MCP tool manifest** (from 3.4). `velaris-mcp-tools-X.Y.Z.json`
lists every tool the MCP server in the wheel offers, with the sha256 of
its description and of its input schema, and is signed like the wheel
(`velaris-mcp-tools-X.Y.Z.json.sigstore.json`). `velaris mcp-verify`
checks that signature against the identity above and then the server
your MCP client runs against the manifest, and names every tool whose
description or schema differs:

    pip install sigstore
    velaris mcp-verify velaris-mcp-tools-3.4.0.json -- python -m velaris_mcp

EMBEDDING.md says what it does and does not tell you. The signature can
also be checked on its own with the `sigstore verify identity` command
above, naming the manifest and its bundle.

**Checksums.** `SHA256SUMS` (for the wheel, sdist, SBOM and tool manifest) and
`<asset>.sha256` (for each binary and the bundle) are attached too;
`sha256sum -c` checks them. A checksum proves the file is intact, not
who built it - the signature does that.

**The SBOM.** `velaris-lang-X.Y.Z.cdx.json` is a CycloneDX bill of
materials of an environment holding the wheel and its optional
dependencies (`z3-solver`, `llvmlite`), signed like the wheel. Velaris
itself has no required dependencies.

**Reproducibility.** The release workflow builds the wheel twice with
the same `SOURCE_DATE_EPOCH` and fails if the two differ. To check on
your own machine at the tagged commit:

    SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) python -m build --wheel
    sha256sum dist/*.whl          # compare with SHA256SUMS on the release

**What verification does not tell you:** that the code is correct, or
that the version you verified is the one your agent framework will
import. Pin the version, and run the suites named in THREAT_MODEL.md on
the machine that will run untrusted code.
