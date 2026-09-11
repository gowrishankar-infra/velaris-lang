<div align="center">

# Velaris

**An AI wrote you a script. Run it anyway.**

A language where a function's signature declares what it may touch —
and the runtime refuses anything you did not allow, whatever the code
says about itself.

[![PyPI](https://img.shields.io/pypi/v/velaris-lang)](https://pypi.org/project/velaris-lang/)
[![tests](https://github.com/gowrishankar-infra/velaris-lang/actions/workflows/test.yml/badge.svg)](https://github.com/gowrishankar-infra/velaris-lang/actions/workflows/test.yml)
[![release](https://img.shields.io/github/v/release/gowrishankar-infra/velaris-lang)](https://github.com/gowrishankar-infra/velaris-lang/releases)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[**Playground**](https://gowrishankar-infra.github.io/velaris-lang/playground.html) · [**Documentation**](https://gowrishankar-infra.github.io/velaris-lang/) · [**Reference**](SPEC.md) · [**Library**](https://gowrishankar-infra.github.io/velaris-lang/library.html) · [**Errors**](https://gowrishankar-infra.github.io/velaris-lang/errors.html)

</div>

<img src="docs/hero.png" alt="Velaris refusing a network call because the run only allowed io" width="100%">

---

```
pip install velaris-lang
velaris agent_output.vel --allow io
```

That program cannot open a socket, read a file, call Python, or ask the
clock. Not "shouldn't" — the runtime refuses, and a refusal cannot be
caught and carried past. You do not have to read the code, understand
it, or trust the compiler's analysis of it.

`--allow io,ffi:math,json` grants Python for those modules only; a call
that reaches any other module — named, or reached through an attribute of
a granted one — is refused (E311). A granted module can still do whatever
that module itself can do: `ffi:os` is the operating system. Since 3.0
the same grammar
narrows every coarse effect: `fs:read:./data`, `fs:write:./out`,
`net:api.example.com:443`, `net:*.example.com`, and `@100` for at most
that many operations in a run; `env` is its own effect, so an
`io`-only program cannot read the environment. `timeout` and
`max_memory_mb` are available through the library and every door, and
on a door the operator's limits are ceilings a caller cannot raise.
It is still not a security boundary - but the
caveats every review raised, the ffi cliff, unbounded execution, and
`fs` and `net` with no path or host list, are now precise permissions
rather than holes. It is a real guard for the situation everyone is
now in — running a program someone, or something, else wrote.

## The other half: promises, proven

```
fn discount(price: Int) -> Int
    requires price >= 0
    ensures result >= 0
{
    return price - 10
}
```

```
error[E700] promise cannot be kept: 'discount' ensures result >= 0
  proven without running the program: price = 5 gives result = -5
```

That `ensures` is not a comment or a runtime assert. The Z3 theorem
prover verifies it for **every possible input** before execution — and
refutes it with an exact counterexample when it lies.

## Related work

[TACIT](https://github.com/lampepfl/tacit) ("Securing Agents With
Tracked Capabilities", ACM CAIS '26;
[arXiv 2603.00991](https://arxiv.org/abs/2603.00991)) has agents write
Scala 3, whose capture checking tracks file, network and command
capabilities as values in the type system;
[CaMeL](https://arxiv.org/abs/2503.18813) has a model turn the user's
request into a restricted subset of Python and tags every value with its
provenance and permitted readers, checking a policy at each tool call;
[WASI](https://wasi.dev) gives a WebAssembly module only the resources
its host hands it. Velaris is a small language a model learns from a
3,300-word card, in which functions declare their effects, the runtime
enforces the operator's budget at each operation, and contracts are
checked by the Z3 theorem prover; it does not track data flow, which
CaMeL and TACIT both do, and its command line grants every effect when
no budget is given, where a WASI module given nothing reaches nothing.
The capability
format is published separately, under CC0, as
[velaris-spec](https://github.com/gowrishankar-infra/velaris-spec),
whose [PRIOR_ART.md](https://github.com/gowrishankar-infra/velaris-spec/blob/main/PRIOR_ART.md)
sets out these differences and the older work in full.

## Why Velaris

| Guarantee | What it means |
|---|---|
| **Effects are visible** | `uses io, net, fs, ffi` — a function without `uses net` can never touch the network, transitively, and one without `uses ffi` can never call out to Python. Hidden behavior does not compile. |
| **Promises are proven** | `requires` / `ensures` / loop `invariant`, verified by Z3 with modular call summaries — including records, maps, nested lists, quantified list properties, failure paths, and floats in **genuine IEEE-754** (the prover refutes `x + 0.1 + 0.1 == x + 0.2` with the exact double that breaks it). |
| **Failure is unignorable** | `-> Int or fail` in the signature; callers must `check` or `try`. Forgetting the error path is a compile error — builtins included. |
| **Fast where it's safe** | Pure functions over numbers, list reads, and text — including text built inside them — JIT to native code via LLVM (~10,000× on hot arithmetic, ~45× on text building), differential-tested against the interpreter. Native reads are bounds-guarded and text is built in a runtime-owned buffer, so results always match interpreted. |

Why floats are proven in IEEE-754 rather than as real numbers, and what
that costs: [docs/floats.md](docs/floats.md).

Loops without written invariants are handled where the boring
invariants suffice: the compiler proposes bounds on each counter and
keeps the ones a loop step cannot break (see `examples/inferred.vel`).
Anything richer — membership, sortedness — still needs an `invariant`
line.

The prover **never** claims "proven without running" unless the
counterexample is premise-complete — untranslatable assumptions abandon
the proof to runtime checks rather than risk a false alarm. Soundness
reports are treated as [security issues](SECURITY.md).

## Install

```
pip install velaris-lang
velaris doctor
velaris new hello && cd hello && velaris main.vel
```

**Standalone executable** (no Python required) — download for
Windows / Linux / macOS from the
[latest release](https://github.com/gowrishankar-infra/velaris-lang/releases),
then:

```
velaris doctor
```

**With Python 3.10+:**

```
pip install velaris-lang
velaris new hello && cd hello && velaris main.vel
```

**Zero install** — the
[playground](https://gowrishankar-infra.github.io/velaris-lang/playground.html)
runs the real compiler in your browser.

Optional extras for source installs: `pip install ".[full]"` adds
`z3-solver` (compile-time proofs) and `llvmlite` (native speed);
without them, promises are checked at runtime and everything runs
interpreted — same language, honestly degraded.

## Everyday ergonomics

```
keep_if(xs, fn(n: Int) -> Bool { return n % 2 == 0 })   // inline functions
format("hi {}, {} left", name, count)                    // text with holes
args()                                                   // command line
post(url, body) / fetch_status(url)                      // not just GET
```

Function values are lifted to real functions, so proofs and native
compilation apply to them unchanged — and they can carry their own
`requires` / `ensures`, proven like any other function's. They can't capture surrounding
variables — the compiler tells you to pass them in instead.

## Where it plugs in

```
velaris script.vel --allow io        the command
import velaris                        a Python library
velaris mcp-install                   tools inside your assistant
velaris.mcpb                          double-click install for Claude Desktop
uses: gowrishankar-infra/velaris-lang a GitHub Action, findings as SARIF
velaris capabilities check            CI fails when the capability surface widens
velaris serve                         an HTTP door for any language, token required
npx velaris-lang script.vel           npm, for the JavaScript world
%%velaris --audit --allow io          a Jupyter cell
- repo: velaris-lang (pre-commit)     a commit hook
docker run ... velaris check          a container
velaris build --for-everyone          standalone executables
```

## Use it from your own program

```python
import velaris

report = velaris.audit(source)      # what it touches, what's proven
run = velaris.run(source, allow={"io"})   # it cannot touch anything else
print(run.output, run.refused_effect)
```

The budget is enforced the same way it is on the command line. There is
an MCP server too, so an assistant can write, audit and sandbox-run
Velaris without leaving the conversation — see
[EMBEDDING.md](EMBEDDING.md) and the versioned `velaris.audit/1` format.

Calling `run` with a timeout or a memory cap starts a fresh interpreter
every time. A pool keeps workers alive under one fixed budget:

```python
pool = velaris.Pool(size=4, allow={"io"}, timeout=30, max_memory_mb=512)
result = pool.run(source)             # the same RunResult run() returns
pool.close()
```

200 sequential bounded runs of a small program: 46.6 s a process at a
time, 0.5 s on a pool. `pool.run` takes no `allow` — the budget belongs
to the pool, a worker is killed and replaced unless the run finished
cleanly, and a reused worker has every piece of mutable state reset
first. `check_pool.py` asserts each of those, including a program that
widens its own budget through `ffi` and cannot widen it for the next
one. The rules are stated in full in [EMBEDDING.md](EMBEDDING.md).

## Written by a model, audited by you, run in a box

```
velaris card > card.md          # ~3,300 words: paste into any model
velaris audit script.vel        # what it can touch, before you run it
velaris script.vel --allow io   # it cannot touch anything else
```

`velaris audit` is written for the reviewer: what the program reaches,
what it promises, how much of that is *proven* rather than checked
while running, what can fail, and the exact command to run it safely.
`agent_loop.py` closes the circle — a model writes it, `velaris check
--json` hands back errors with fixes, and it iterates until the program
compiles and its promises prove.

## Running code you did not write

```
velaris agent_output.vel --allow io      # it cannot touch anything else
velaris agent_output.vel --deny net,ffi  # everything except these
```

The runtime refuses any effect outside the budget you grant, whatever
the source claims — and a refusal cannot be caught and carried past.
Not a security boundary (`ffi` grants everything Python can do), but a
real guard for running a program you have not read.

## Checking everything at once

```
velaris examples/stress.vel     # 33 checks across the whole language
velaris examples/edges.vel      # 20 boundary, property and round-trip checks
python check_refusals.py        # 21 wrong programs, each refused correctly
python check_sandbox.py         # 30 escape attempts, all refused
python check_pool.py            # a pool must leak nothing between programs
python check_ratchet.py         # every widening fails, nothing else does
```

One command that exercises the language, the standard library, the
prover, native compilation, JSON, dates, CSV, the host language and the
network.

## Measured against other tools

63 small programs — 56 with one deliberate defect, 7 correct controls —
each written three times with the same behaviour, in Velaris, in
JavaScript for Deno, and in Python. One harness runs every program
through every tool and records what was caught before running, what was
caught while running, and what was missed.

| | caught before running | caught while running | missed | false positives on the 7 controls |
|---|---|---|---|---|
| **Velaris 3.1** | 42 | 12 | 2 | 0 |
| Deno 2.9 | 5 | 27 | 24 | 0 |
| Python 3.13 | 0 | 28 | 28 | 0 |

The two Velaris misses are in the table by design: a loop that stops
one item early with no contract to contradict, and a program that
prints `rm -rf build` for its caller and touches nothing. Both are
named, with the reason each is not catchable, in
[benchmark/RESULTS.md](benchmark/RESULTS.md) — regenerated by one
command, `python benchmark/run.py`, which also lists the rows the
prover settles only while running.

## Two real programs

`examples/ledger.vel` — an expense tracker: records, integer cents,
file persistence, sorted reports.
`examples/wordcount.vel` — text analysis: `velaris examples/wordcount.vel
<file> [n]` counts word frequencies and prints a ranked histogram.
`examples/linkcheck.vel` — a link checker you would actually run:
`velaris examples/linkcheck.vel <url> ...`, non-zero exit when
something is broken.
`examples/fetcher.vel` — an HTTP tool: checks a status, then summarises
a page, with every network call declared and every failure handled.

## JSON

```
json_get(doc, "user.name")    json_int(doc, "user.age")
json_len(doc, "tags")         json_of(Person(name: "gowri", age: 30))
```

Paths walk objects and lists, every read can fail (a missing field is
a possibility, not a crash), and none of it is an effect — parsing text
is pure.

## Reaching other languages

```
fn today() -> Text uses ffi or fail {
    let nothing: List of Text = []
    return try py("datetime.date", "today", nothing)
}
```

`py` / `py_int` / `py_float` / `py_json` call Python functions, and
`py_new` / `py_do` / `py_field` / `py_close` hold real objects — a
database connection, a session — so every library Python has is
reachable — but only from a function that declares `uses ffi`, and it
can fail like anything else that leaves your program.

## The standard library reaches outside

```
import "http.vel" as http     import "db.vel" as db
import "time.vel" as time     import "env_tools.vel" as sys

check http.get(url) { ok body { ... } fail why { ... } }
check db.count(conn, "notes") { ok n { ... } fail why { ... } }
```

Written in Velaris, so they carry their effects — a program using
`http` shows `net`, one using `db` shows `ffi`, and a pure function
can call neither.

## Libraries

```
velaris add https://example.com/geo.vel as geo   # vendored into lib/
velaris deps                                     # what you depend on
velaris deps --verify                            # unchanged since?
```

A library is compiled before it is accepted and kept in your
repository where you can read it. No registry, no resolver, nothing
fetched at build time.

`velaris add` writes `velaris.lock` beside `velaris.toml`: every
vendored library with its source, the sha256 of the exact bytes that
arrived, and the version of Velaris that added it. `velaris deps
--verify` fails if a file's hash differs from the lock or a locked
library is not on disk — a line worth having in CI. Adding a library
that is already vendored, with different bytes, is refused with both
digests printed; `--force` replaces it.

## Imports

```
import "lib/geo.vel" as geo      // named: geo.distance(a, b)
import "std.vel"                 // flat: sort(xs)
```

A named import prefixes that library's functions, so two libraries that
both export `distance` can be used in the same file.

## Shipping a program

```
velaris build myprogram.vel      # one executable, ~90 MB
./myprogram alpha beta           # runs anywhere, nothing installed

velaris build myprogram.vel --for-everyone   # a workflow that builds
                                             # Windows, Linux and macOS
```

Your program, its imports, the standard library and the compiler, in
one file. It is compiled and proof-checked before it is built.

## Tooling

`velaris trace program.vel` (watch every call as it happens) ·
`velaris test program.vel` (runs every `test_*` function written in
Velaris) ·
`velaris check program.vel` (compile without running; several files at
once, `--json` for tools) ·
`velaris explain program.vel` (a walkthrough of every function: effects,
promises, and whether they are proven — `explain <folder>` maps a whole
project) ·
`velaris repl` (definitions are proof-checked as you type them) ·
`velaris fmt` (canonical style, `--check` for CI) · `velaris lsp`
(errors as you type in any LSP editor; a VS Code extension lives in
[`editor/vscode`](editor/vscode)) ·
`velaris doctor` · `velaris new` · `--json` errors for automation.

## Standard library

Written in Velaris, in [`stdlib/std.vel`](stdlib/std.vel) — and it
keeps its own promises: `sort` carries `ensures is_sorted(result)`,
`max_of` requires a nonempty list, and violating a library `requires`
is a compile error at *your* call site. Full
[reference](https://gowrishankar-infra.github.io/velaris-lang/library.html),
generated from the real compiler.

## Numbers

Whole numbers are 64-bit. Arithmetic that outgrows that range is an
error, not a silent wrap — and the same error whether your code is
interpreted or running as machine code. Floats are IEEE-754 doubles,
proven as such.

## Remembered proofs

Proofs are cached in `.velaris/` and keyed by the function's text *and*
the contracts it depends on, so changing a promise re-proves everything
that relied on it. `--no-cache` proves from scratch; `velaris clean`
forgets.

## The reference

[SPEC.md](SPEC.md) states precisely what the language means: semantics,
evaluation order, effect propagation, what "proven" covers today, and
what Velaris deliberately does not have — including
[why it has no concurrency model](SPEC.md#13-concurrency).

## Stability

Semantic versioning: breaking changes **only at major versions**.
[STABILITY.md](STABILITY.md) says what that covers - the language, the
error codes, `velaris.audit/1`, the library API, the budget grammar and
the command line - what it does not, the rules for deprecating and
removing, and every time this project has broken the rule, 3.3 and 3.4
among them. CI tests every push on Linux, Windows and macOS, Python
3.10 and 3.12, with and without the optional dependencies. Errors are
stable, numbered, and
[fully documented](https://gowrishankar-infra.github.io/velaris-lang/errors.html).

## How much is proven

```
velaris proofs .            # 35 of 58 promise-carrying functions proven (60%)
velaris proofs . --min 80   # fails the build below 80%
```

## Using Velaris in CI

```yaml
permissions:
  contents: read
  security-events: write       # for sarif, the default
  pull-requests: write         # only for pr-comment

steps:
  - uses: actions/checkout@v5
  - uses: gowrishankar-infra/velaris-lang@v4.0.0
    with:
      files: "src/*.vel"     # optional; default is every .vel file
      format: "true"         # optional; also check formatting
      min-proven: "80"       # optional; fail below this proven share
      pr-comment: "true"     # optional; audit every changed .vel on the PR
      sarif: "true"          # the default; findings to code scanning
      capabilities: "check"  # the default once velaris.capabilities exists
```

**The capability ratchet (4.0).** `velaris capabilities init` records
the capability surface a repository's `.vel` files need - effects,
paths, hosts, Python modules, how many file and network operations a
run can perform, and each function's effects - in
`velaris.capabilities`; commit it. From then on the action runs
`velaris capabilities check` and fails any change that needs more,
naming what widened, the file, function and line that introduced it,
and the edit to the baseline that would accept it. The comparison is
always with that file, never with the previous commit: capability
added across many small commits, none alarming by itself, fails at
every one of them until someone widens the file, where the change
shows in review. With `pr-comment` the comment also reviews the pull
request against its base - surface, proven share, new fallible
functions, new hosts and paths - with a one-word risk computed from
those facts. [EMBEDDING.md](EMBEDDING.md) has the rules;
`check_ratchet.py` holds them, including a six-commit history that
fails only at the commit that reaches the network.

With `sarif` on - the default from 3.4 - the check writes its findings
as SARIF 2.1.0 and uploads them with `github/codeql-action/upload-sarif`,
pinned to a commit, so they appear in the repository's Security tab and
on the lines of a pull request. The job needs
`permissions: security-events: write`, and a private repository needs
code scanning enabled; set `sarif: "false"` if it has neither. On a
pull request from a fork the job's token cannot upload, so the step is
skipped there; the file is still written, and its path is the action's
`sarif-file` output. The findings still print to the job log either way.

The same output without the action, for SonarQube
(`sonar.sarifReportPaths`), Azure DevOps or anything else that reads
SARIF:

```
velaris check src/*.vel --sarif > velaris.sarif   # exit 1 as the plain check
velaris proofs src --sarif > proofs.sarif         # promises left to runtime
velaris audit src --sarif > audit.sarif           # what each function may touch
```

One run, driver `Velaris` with its version and a rule for every code in
the compiler's error table, each with a help link to its row on the
[errors page](https://gowrishankar-infra.github.io/velaris-lang/errors.html),
plus a rule for each finding that is not an error. Each result has the
file, the line and Velaris's message. Errors are `error`; a promise left
to runtime is a `warning` (an `error` under `check --strict`); a function
that promises nothing about the data it handles, a loop not shown to end,
and each effect a function may perform (`audit`) are `note`. Velaris's
suggested fixes are sentences, while a SARIF `fix` must hold the exact
bytes to change, so they travel in each result's `properties.fixes`
rather than as SARIF fixes with an edit made up to fill the slot.

Or without installing anything:

```
docker run --rm -v "$PWD:/work" velaris check /work/main.vel
```

Installs Velaris with the prover and fails the build if anything does
not compile or a promise cannot be kept.

With `pr-comment: "true"` on a `pull_request` event the action posts
one comment holding the `velaris audit` of every `.vel` file the pull
request changes - effects and Python modules reached, proven share,
the safe command, and any warnings such as a loop not shown to end -
and edits that same comment on later runs instead of adding another.
It uses the REST API with the job's own `GITHUB_TOKEN`, so the job
needs `permissions: pull-requests: write`. The audit is posted whether
or not the checks passed; a file that does not compile is reported as
such.

What a reviewer should read before allowing agent-written Velaris to
run: [THREAT_MODEL.md](THREAT_MODEL.md), [COMPLIANCE.md](COMPLIANCE.md)
and the verification steps in [SECURITY.md](SECURITY.md).

## Project

[Roadmap](ROADMAP.md) · [Support and expectations](SUPPORT.md) ·
[How the compiler works](ARCHITECTURE.md) · [Maintainers](MAINTAINERS.md) ·
[Security policy](SECURITY.md) · [Stability](STABILITY.md) ·
[Changelog](CHANGELOG.md)

Maintained by one person, in the open, with the limits stated plainly
in [SUPPORT.md](SUPPORT.md).

## Contributing

The entire implementation is one readable file, `velaris.py`, in
pipeline order — lexer to LSP. Start with
[ARCHITECTURE.md](ARCHITECTURE.md) for how it fits together, and
[MAINTAINERS.md](MAINTAINERS.md) for what review looks like.

**Looking for somewhere to start?** See the
[good first issues](https://github.com/gowrishankar-infra/velaris-lang/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
— small, self-contained tasks, each with the file to open and what
"done" means.

The example programs in [`examples/`](examples) each carry an expected
verdict, and about half are *designed* to be rejected — each rejection
demonstrates a guarantee. Before any change ships:

```
python run_tests.py                 # every example, expected verdicts
velaris test examples/std_test.vel  # the library's own tests
python fuzz_native.py 60            # both engines must agree
velaris fmt examples/*.vel stdlib/*.vel --check
```

## License

[MIT](LICENSE) © Gowri Shankar
