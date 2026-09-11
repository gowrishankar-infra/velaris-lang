# Provenance

Dates and identifiers for this repository and the specification it
implements. Commit and tag dates are the ones git records, from the
author's clock; the GitHub and Software Heritage records are kept by
those services.

## velaris-lang

| What | Identifier | Date |
|---|---|---|
| Repository | <https://github.com/gowrishankar-infra/velaris-lang> | created on GitHub 2026-08-16T18:43:04Z |
| First commit of the effect system: `uses` clauses and the transitive effect checker, `check_effects`. It is also the repository's first commit. | `dcb44e2310291fa546405434f4698148413f3cdd`, "Velaris v0.9: effects + types + contracts + Z3 proofs + LLVM native" | 2026-08-17T00:21:33+05:30 |
| First commit enforcing an effect budget while a program runs (`--allow`, `--deny`) | `dc4e3a1ecea285dae6c088507bd6d1651fec6093`, v2.40 | 2026-08-18T21:55:51+05:30 |
| Budgets scoped to paths, hosts and counts; `env` its own effect | `a76c217d0cf5dd1539e5c895576ad507740ab2a3`, v3.0.0 | 2026-09-10T23:00:21+05:30 |
| The capability ratchet (`velaris.capabilities/1`) | `ae7a04102cc9d0704be659036bcd2c535983f036`, v4.0.0; GitHub release published 2026-09-11T08:11:46Z | 2026-09-11T13:41:12+05:30 |
| This version | 4.1.0, tag `v4.1.0` | 2026-09-11 |

## velaris-spec

| What | Identifier | Date |
|---|---|---|
| Repository | <https://github.com/gowrishankar-infra/velaris-spec> | created on GitHub 2026-09-11T03:29:01Z |
| v0.1, the capability format as first written down, extracted from velaris-lang 3.1.1 (`25d2c051bb5f6925006fed2d44ba8fe809b8cf36`) | annotated tag `v0.1` on commit `f4e7babe7e961d35f6b31450c6d42f3860123acf` | tagged 2026-09-11T08:58:50+05:30 |
| v0.4, with the conformance corpus | tag `v0.4` | 2026-09-11 |

velaris-lang is the reference implementation of velaris-spec.

## Software Heritage

Both repositories were submitted to the Software Heritage archive
through its save-code-now API
(`POST https://archive.softwareheritage.org/api/1/origin/save/git/url/<origin>/`).
The request ids and dates are the ones the API returned.

| Origin | Save request id | Requested (UTC) | Status returned | Request |
|---|---|---|---|---|
| https://github.com/gowrishankar-infra/velaris-lang | 2471043 | 2026-09-11T10:39:14.948887+00:00 | accepted; task pending | <https://archive.softwareheritage.org/api/1/origin/save/2471043/> |
| https://github.com/gowrishankar-infra/velaris-spec | 2471044 | 2026-09-11T10:39:16.118803+00:00 | accepted; task pending | <https://archive.softwareheritage.org/api/1/origin/save/2471044/> |

The requests were made just before the commits that add this file were
pushed, so which commit a visit captured depends on when the archive
visited. The archive's own record of each visit and snapshot is at
<https://archive.softwareheritage.org/browse/origin/visits/?origin_url=https://github.com/gowrishankar-infra/velaris-lang>
and
<https://archive.softwareheritage.org/browse/origin/visits/?origin_url=https://github.com/gowrishankar-infra/velaris-spec>.
