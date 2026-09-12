# Stability

What this project will not change without a major version, what it
does not promise to keep, the rules for changing either, and the
record of the times it broke its own rule.

## What semantic versioning covers

A change to any of these is a breaking change, and ships only in a
major version.

- **The language**: its syntax and semantics as [SPEC.md](SPEC.md)
  states them. A program that compiles and runs under 4.x compiles,
  runs and means the same under every later 4.x, with the one
  exception under *The prover's reach* below.
- **The error codes** in `velaris.ERROR_TABLE`, and what each means.
  The [errors page](https://gowrishankar-infra.github.io/velaris-lang/errors.html)
  is built from that table.
- **`velaris.audit/1`**: the fields and their meanings, as
  [EMBEDDING.md](EMBEDDING.md) and
  [velaris-spec](https://github.com/gowrishankar-infra/velaris-spec)
  section 8 state them. Within version 1 fields may be added; none
  changes meaning or disappears without the `schema` value changing.
  The other versioned documents Velaris writes follow the same rule
  within their version: `velaris.capabilities/1`,
  `velaris.capabilities-check/1`, `velaris.review/1`,
  `velaris.invocation/1`, `velaris.mcp-tools/1` and, from 4.1,
  `velaris.conformance/1`.
- **The library API**: `velaris.check`, `velaris.audit`, `velaris.run`,
  `velaris.Pool`, `velaris.card` and, from 4.2, `velaris.attest` - their
  names, their parameters, and the fields of what they return
  (`CheckResult`, `AuditResult`, `RunResult`, `Problem`, and the in-toto
  Statements `attest` returns, whose predicate velaris-spec section 8.5
  defines). A new optional parameter or a new field is an addition, not
  a break.
- **The budget grammar**: SPEC.md section 7.1, stated in full in
  velaris-spec sections 4 and 5. A budget that parses keeps parsing,
  and grants the same thing.
- **The command line**: the command names, the flags documented for
  them (`velaris` with no arguments prints them, and README and
  EMBEDDING.md describe them), and the exit codes those documents give.

## What it does not cover

- **Anything else in `velaris.py`**: every function, class and
  module-level name not listed above, including those the doors and
  suites use (`Budget`, `InvocationLog`, `inspect_source`,
  `load_program`, ...). They may change in any release.
- **The proof cache** in `.velaris/`: its format and location. Delete
  it at any time; it is rebuilt.
- **The wording of messages.** Codes are stable; prose is not. That
  covers error messages, their suggested fixes, an audit's `warnings`,
  and every command's text output - read `--json`, not the text.
- **Which promises happen to prove.** A new version may prove a promise
  an older one left to runtime, or leave to runtime one an older one
  proved.
- **The canonical style `velaris fmt` writes.** A change to it is named
  in the CHANGELOG, because `fmt --check` in CI will see it.
- **Anything marked provisional**, in SPEC.md or in velaris-spec.

## The rules

1. **A breaking change ships only in a major version.** That includes a
   security fix that refuses something that used to work: if it breaks
   something covered above, it is a major version. Version numbers cost
   nothing, and a major version is how a user learns to read the
   CHANGELOG before upgrading.
2. **A deprecation is announced in a minor version**, warns when the
   deprecated thing is used for at least one minor version after that,
   and is removed no sooner than the next major version.
3. **An error code is never reused for a different meaning.** A code
   that is no longer given stays listed as removed (`REMOVED_ERRORS` in
   `velaris.py`, and the errors page), with what it meant and the
   version that removed it.
4. **Every major version's CHANGELOG entry says what a user of the
   previous major has to change**, item by item.

**The prover's reach.** A prover that settles more is not a breaking
change, even when it refuses a program that compiled before: a promise
it now shows false (E700), a call it shows can break a `requires`
(E701), a list read it shows can pass the end (E705), a divisor it
shows can be zero (E706). Each such program could already fail while
running, with the matching runtime error, for the input the prover
names. This is the one way a program that compiled under 4.x can be
refused by a later 4.x, and the CHANGELOG names each release that does
it. 4.3 widened it once: a division whose divisor mentions a loop's
values is translated when the loop's condition and invariants show the
divisor positive. 4.3.1 widened it again, not by translating more but
by allowing more time: a float proof gets 120 seconds where it had
30, so a refutation a slower machine used to abandon now lands.

**A new builtin gives way to your own function.** A builtin added in
4.3 or later is not reached in a program that defines a function of the
same name (SPEC.md 10.1). Without that rule, adding a builtin would
break every program that had already used the name - `examples/ledger.vel`
has had a function called `money` since 1.13 - and adding one would be a
major version. The builtins that existed before 4.3 are unchanged: a
function named like one of those is still never reached.

## Breaks we have made

The README has promised semantic versioning since 2.2. 2.0, 3.0 and
4.0 broke things in major versions, as promised; the rest below did
not. None of them is being undone - the versions are published - and
this section exists so the record is whole and so the rules above are
applied from 4.0 on.

**2.0 (major).** `to_int`, `get` on a map, `read_file` and `fetch`
became fallible: a call to one of them not handled with `check` or
`try` was refused with E520, and the compiler pointed at each.

**3.0 (major).** `env` became its own effect. A program that called
`env()` under `uses io` alone was refused at compile time, and an
`io`-only budget no longer let a program read the environment.

**3.4 (minor) shipped three breaking changes it named, and three it
did not.** Named in its CHANGELOG, which said they shipped in a minor
version because each closed an open door: a client of `velaris serve`
had to send a bearer token; the MCP server granted `io` only unless
started with `--max-allow`; and the GitHub Action, with `sarif` on by
default, needed `permissions: security-events: write`. Not named:
`velaris serve` refused an argument it did not know, where it had
ignored it; the MCP server did the same; and `GET /health` stopped
naming the ceiling to a caller without the token. **3.4 should have
been 4.0**: closing an open door is a reason to release soon, not a
reason to call a break something else. It was not retagged, because
3.4.0 was already published to PyPI and GitHub, and moving a published
version breaks everyone who pinned it. This policy exists so that it
does not happen again.

**3.3 (minor) shipped five breaking changes as fixes, and named none as
breaking.** A `uses` clause naming anything but the seven effects was
refused (E300). The budget parser became strict: a count in non-ASCII
digits, `ffi:M@N`, `ffi:` with no module and an unbracketed IPv6
address were refused where they had parsed. `ffi,ffi:math` came to
grant every module, where it had granted `math` alone - the same budget
text granting more. A call through a granted module into a module that
was not granted was refused (E311) where it had run. `%` followed by
`2C`, `40`, `5B`, `5D` or `25` in a path or host began to be decoded.
And `velaris audit --json` changed shape to `velaris.audit/1`. Each was
a correct fix; together they were a major version.

**Earlier minor releases** that broke something covered above:

| Release | What broke |
|---|---|
| 2.20 | Whole numbers became 64-bit: arithmetic past that range stopped with E407, where the interpreter had kept counting |
| 2.42 | `velaris fmt` changed where it puts `requires`, `ensures` and `invariant`, so `fmt --check` failed on files the previous version had formatted |
| 2.44 | `pop`, `slice` and `set_at` had to be handled with `check` or `try` (E520); a missing `main`, a `main` with parameters and a `main` marked `or fail` became compile-time errors (E400, E401, E523); Python calls began to receive arguments that read as numbers as numbers |
| 2.47 | `http.vel`'s `call` returned an `Answer` record instead of text |
| 2.56 | `audit().problems` held `Problem` objects instead of dictionaries |
| 2.59 | The MCP server and the HTTP door stopped a run at 30 seconds and 512 MB, where it had had no limit |
| 2.62 | `args()` stopped including `--allow`, `--deny`, `--timeout` and their values; `check --strict` began refusing a loop not shown to end (E612) |
| 3.1 | The memory cap began to hold on Windows, so a run past it stopped with E611 where it had continued; `velaris add` refused to replace a vendored library with different bytes without `--force` |

**Refusals from a stronger prover**, which the rule above does not
count as breaks, in 2.6, 2.9, 2.12, 2.18, 2.41.2, 2.43, 2.44 and 2.45:
each refused before running a program that had compiled, for a
division, a map promise, a nested-list read, a record promise, a call
against a `requires` the prover had been dropping, or a list read the
prover could now show wrong.

**A reused error code.** E610 meant a missing map key from 1.4; 2.0
made that lookup a failure instead, and 2.59 gave E610 to the run's
time limit. Rule 3 forbids that from 4.0 on. No code has been removed
since.

**4.0 (major).** Listed item by item in the CHANGELOG under "What a 3.4
user has to change": `velaris serve` without `--max-allow` grants `io`
only; on both doors a request's `timeout` and `max_memory_mb` may not
exceed the operator's `--max-timeout` and `--max-memory-mb`, 30 seconds
and 512 MB by default, and must be numbers; and `velaris serve
--max-memory-mb`, which on Linux and macOS capped the door's own
process, is now the most each run may have.
