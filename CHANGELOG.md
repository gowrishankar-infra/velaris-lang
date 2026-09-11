# Velaris changelog

## 4.1 - Conformance you can run, provenance you can check

A minor version. Conformance to the capability format stops being a
sentence naming this repository's suites and becomes a corpus any
implementation can run; `velaris conformance` runs it here, on every CI
leg. The project gets citation files, an entry in an independent
archive, and a predicate type whose URL resolves; and a preprint is
drafted, for the maintainer to read. One defect, found by writing the
corpus, is fixed.

4.0.1 was committed and pushed but never tagged, so it was never
published; its fix to `velaris review` ships in 4.1.0.

**The conformance corpus.** velaris-spec 0.4 holds `tests/`: 444 JSON
cases, each with an id, its level, a description, the input - budget
text, Velaris source, a tree of files and a change to it - and the
outcome an implementation must produce: the grants a budget parses to
or its refusal, an audit's effect surface, a refusal and its code, a
baseline, or a verdict with every widening and the rules it fails. 298
cases at L1, declaration (280 budgets, 18 audits); 37 at L2,
enforcement (programs run under a budget, with a fixture of files and
two local HTTP servers); 109 at L3, the ratchet (14 baselines to write,
51 changes to check, two sequences, the writer's guard, and 32
covering, 3 reduction and 6 operation-bound cases). velaris-spec's
CONFORMANCE.md defines the levels and the behaviours each requires, and
says plainly that no level requires a prover; `tests/README.md` is the
runner contract. Five L3 cases are the ratchet's known limits from the
4.0 entry below, recorded with the outcome the check gives today - two
widenings that pass, three non-widenings that fail - so that another
implementation matches it rather than guessing.

The corpus is not written by hand. `build_conformance.py` transcribes
it from tables in three suites, where the same entries are asserted
against this implementation, and computes nothing itself; `--check`
regenerates it and fails when it differs from what velaris-spec
commits. For that, the suites became tables, and asserting them made
them stricter:

- `check_sandbox.py` holds each case as data, with placeholders for its
  paths and ports, and asserts the refusal code each must carry. Until
  4.1 it accepted any of the five codes, so a runtime refusing a path
  outside its prefix with E310 rather than E313 would have passed. It
  runs its fixture in a temporary directory rather than in the
  repository, and its symbolic-link case wherever the system will make
  a link, not only on POSIX. Four cases are new, the four rules
  velaris-spec 0.3 listed as untested (its Q9): `@0`, a count spent by
  an operation that then fails, a URL with no scheme taken as HTTPS, and
  an existence check under a write-only grant. 34 escape attempts and
  16 honest programs.
- `check_library.py` gains `BUDGETS`, 55 budgets each held to what
  velaris-spec sections 4 and 5 say it means - the grants for 51, a
  refusal for 4 - including the spec's own examples and denials (until
  4.1 the awkward ones were checked to round-trip, not for what they
  parse to); and `AUDITS`, 18 programs each held to the effect surface
  its audit must report, and to the schema. The malformed-budget list
  moved out of `main()` so the corpus can be written from it.
- `check_ratchet.py`'s scenarios became `DERIVE`, `CHECKS`, `SEQUENCES`,
  `WRITE_GUARD`, `COVERING`, `REDUCE` and `BOUNDS`. Each check now
  asserts the complete list of widenings, with the rules each fails,
  where most cases asserted one finding; each derivation asserts the
  whole baseline. New: 14 baselines written for trees; the writer
  refusing, unasked, to write a baseline for a tree that needs more; a
  new effect; a new program outside the surface (W1 alone); `fs`
  declared with no file named, which needs plain `fs`; another spelling
  of a path; a port under a portless grant; 9 covering and 2 reduction
  cases; and the five known limits. What only this implementation
  says, such as the call chain, `velaris review`, SARIF and warning
  text, is asserted after, on the same scenarios.

Thirteen scenarios are left out of the corpus, and `tests/index.json`
says why each: six attempts to reach an ungranted Python module through
a granted one, which depend on Python's object model; four honest
programs that need a Python host; a run given no budget, which the
format leaves to the implementation; and two about this command line's
flags.

**`velaris conformance [--level 1|2|3] [--json] [--corpus DIR]`** runs
the corpus against this implementation, through the doors another
implementation would use: the budget parser, the audit, the command
line under a budget, the baseline writer and the check. It finds the
corpus beside the working directory or the installation, prints a line
per level and a one-line verdict, and exits 1 if any case of a level
asked for fails. `--json` is `velaris.conformance/1`, one result per
case, the report shape `tests/README.md` gives any runner. `--level N`
runs the cases a claim at level N needs: L1 and N. A case that needs a
symbolic link is skipped where none can be made, and the verdict says
so; without `jsonschema` the cases that validate a document against
velaris-spec's schemas are skipped too, and the level is reported as
not shown. It passes at all three levels. Run against a copy of the
corpus with twelve expectations broken, covering all ten kinds of case,
and one case given a kind no runner knows, it fails exactly those 13
cases and exits 1.

**CI.** Every one of the twelve legs checks out velaris-spec, runs the
drift test and `velaris conformance` against its corpus. velaris-spec's
own CI runs the drift test and this implementation's conformance
against its corpus, beside its schema and sync checks.

**Found by the corpus, and fixed.** The audit of a program refused for
naming something that is not an effect in a `uses` clause (`uses io,
teleport`, E300) still listed that name in `effects` and in the
function's `effects`, and wrote a `safe_command` that does not parse.
velaris-spec had said since 0.2 that `effects` holds only the seven
names and that `safe_command` always parses; 3.3 had fixed the compile
check and not the document that reports it. From 4.1 `audit` leaves any
name that is not an effect out of all three; the E300 still names it.
This is not a breaking change under STABILITY.md: the fields' documented
meaning is unchanged, and it is the implementation that now matches it;
what changes is the content of a document whose `ok` is false, which
velaris-spec says bounds nothing. HALL_OF_FAME.md credits the corpus.
velaris-spec 0.4 corrects the sentences that had inferred from 3.3's
rejection more than the implementation did.

**Provenance.** `CITATION.cff` in both repositories (CFF 1.2.0, checked
against the format's schema), with the author, the repository, the
version and its date, and a note that a preprint is forthcoming; both
READMEs say "Cite this repository". Both repositories were submitted to
Software Heritage through its save-code-now API, and `PROVENANCE.md` in
each records the save requests' ids and dates beside the first commit
of the effect system, the date velaris-spec 0.1 was tagged, and that
velaris-lang is the reference implementation.

**A resolvable predicate type.** velaris-spec 0.4 section 8.5 defines
an in-toto predicate type for `velaris.audit/1` bound to the digests of
the files audited, and its URL is on this repository's documentation
site: `https://gowrishankar-infra.github.io/velaris-lang/capability/v1`,
which `build_docs.py` now writes, with `schema.json` beside it,
identical to velaris-spec's `schemas/capability-predicate.v1.schema.json`
(velaris-spec's `tools/check_sync.py` fails if they differ).
`velaris.dev` was not used: on 2026-09-11 it answered every path with a
Vercel `DEPLOYMENT_NOT_FOUND`, and nothing here says who controls it.
This implementation publishes the type and does not yet write
Statements of it; velaris-spec's example was assembled from `velaris
audit --json` and a file's digest. A pull request listing the type in
in-toto's predicate registry is prepared in velaris-spec's
REGISTRY_SUBMISSION.md, and not sent.

**A preprint, drafted.** `paper/velaris.md` and `paper/references.bib`:
the problem, the design, the implementation, the evaluation, related
work, limitations and a reproducibility section, with a table naming
the file each number comes from. Not submitted anywhere.

**Also corrected.** The documentation site's benchmark table said
"Velaris 3.1" and the README's did too, where `benchmark/RESULTS.md`
said the table was produced by 3.0.0. The table was regenerated with
4.1.0: every verdict and every line of evidence is what 3.0.0 produced,
and only the version line of `RESULTS.md` and `results.json` changed;
the pages now say 4.1. EMBEDDING.md's table of audit fields lacked
`ffi_any`, added in 4.0. velaris-spec's PRIOR_ART.md said this
implementation emits no SARIF, untrue since 3.4.

**Sources, named** (CONTRIBUTING.md rule): the parts of this release
were specified by the maintainer. The runner contract follows no
published harness. in-toto's `docs/new_predicate_guidelines.md` and
predicate template, read on 2026-09-11, shaped REGISTRY_SUBMISSION.md.
Hills, Caspary and Cooper Stickland, "Distributed Attacks in
Persistent-State AI Control" (arXiv:2607.02514), is cited by the paper
and by velaris-spec's PRIOR_ART.md as the gradual-attack result the
ratchet addresses; the record does not say it influenced the ratchet's
design in 4.0, and this entry does not claim it did.

**Verified**, on Windows 11 with Python 3.13, with the proof cache
cleared first. With the prover: `run_tests.py` 92/92,
`check_library.py` 184 correct (one skipped: its symbolic-link case is
POSIX only), `check_sandbox.py` 49 (its symbolic-link case skipped: this
machine will not make a link), `check_fallible.py` 26,
`check_refusals.py` 21, `check_termination.py` 44, `check_pool.py` 39,
`check_ratchet.py` 114, none wrong; `fuzz_native.py 30` agrees;
`benchmark/run.py --check` over the whole table and `--quick --check`
match `results.json`; `velaris test examples/std_test.vel` 7/7,
`velaris examples/edges.vel` 20/20, `velaris fmt --check` clean,
`velaris capabilities check .` passes; `velaris conformance` reports
L1, L2 and L3 conformant, 443 of the 444 cases run and the
symbolic-link case skipped; `build_conformance.py --check` matches
velaris-spec's corpus. Without the prover, in a fresh virtual
environment with jsonschema and no z3 or llvmlite, the same pass - the
benchmark with `--quick --check` only - with `check_library.py` 181
correct (two skipped for needing the prover, one POSIX only),
`check_refusals.py` 11 with 10 skipped for needing the prover, and
`velaris conformance` again conformant at L1, L2 and L3. velaris-spec
0.4's `tools/validate.py` (schemas, examples, the example Statement,
all 444 cases against the case schema) and `tools/check_sync.py` (the
quoted sections, and the predicate schema against
`docs/capability/v1/schema.json`) pass against this tree. The symbolic-link cases run where a link can be made - the
Linux and macOS runners, and the Windows runners if they allow it -
and whether they pass there is for this commit's CI to say.

## 4.0.1 - The review read the old files from the wrong place

4.0.0's CI failed on its four Windows legs, in `check_ratchet.py`: the
five checks that go through `velaris review` failed. The capability
check - the gate - passed every one of its cases on all twelve legs.

The cause was in `review`. To find where the checked directory sits in
the repository, it compared the working directory's path with the path
`git rev-parse --show-toplevel` prints, as text. On the Windows runners
the temporary directory is a short name (`C:\Users\RUNNER~1\...`) and
git prints the long one, so the two did not match, and the files at the
ref were materialised and read from a directory that was not the ref's
place in the tree. The review then reported the surface as widened, or
as unchanged, whatever the change was. `review` now asks git where it
is (`git rev-parse --show-prefix`) and compares no paths. The same
mismatch happens wherever the path to a checkout goes through a link or
junction, on any system.

The 4.0.0 entry's "Verified" paragraph was true of the machine it
names, from a path git spells the same way, and was not true of the
Windows runners. `check_ratchet.py` gains a case that runs `review`
from a junction (Windows) or a symbolic link (elsewhere) to a
repository whose working tree needs more than its last commit, and
requires the review to see it: the case fails against 4.0.0 and passes
now. 63 checks.

Affected: `velaris review`, and the review section of the Action's
pull-request comment, on a machine where the two paths differ.
`velaris capabilities init` and `check` were not affected, and neither
was anything else in 4.0.0. This repository's `velaris.capabilities` is
recorded again under 4.0.1; only its `velaris_version` changed.

**Verified**, on Windows 11 with Python 3.13, with the proof cache
cleared first; the new case fails against 4.0.0's `velaris.py` and
passes against this one. With the prover: `run_tests.py` 92/92,
`check_library.py` 165 correct (one skipped, POSIX only),
`check_sandbox.py` 45, `check_fallible.py` 26, `check_refusals.py` 21,
`check_termination.py` 44, `check_pool.py` 39, `check_ratchet.py` 63,
none wrong; `fuzz_native.py 30` agrees, `benchmark --quick --check`
matches, `velaris test examples/std_test.vel` 7/7, `velaris fmt
--check` clean, `velaris capabilities check .` passes. Without the
prover, in a fresh virtual environment with no z3 or llvmlite: the same
thirteen pass, `check_library.py` 162 correct (two skipped for the
prover, one POSIX only) and `check_refusals.py` 11 with 10 skipped.
Whether the Windows runners agree is for this commit's CI to say.

## 4.0 - The operator sets the limits, and the capability surface cannot widen quietly

This is a major version. Two gaps 3.4 left open on the doors are
closed, which changes what a door started without flags will grant;
the project's stability policy is written down for the first time,
with the record of the times it was broken; and a repository can now
declare the capability surface its programs may have and have CI fail
any change that widens it.

**The operator sets the limits, not the caller.** On the HTTP door and
the MCP server a request's `timeout` and `max_memory_mb` were whatever
the caller sent; the 30 seconds and 512 MB the doors have had since
2.59 were only the values used when a caller sent none. **Before 4.0 a
caller could exceed them, by asking.** Both doors now take
`--max-timeout` and `--max-memory-mb`, 30 seconds and 512 MB when the
flags are absent. A request that names neither gets the ceiling; one
that asks for less gets less; one that asks for more is refused the way
an over-wide budget is - 403 from the HTTP door, `isError` from the MCP
server - with the ceilings named in the body (`max_timeout`,
`max_memory_mb`, beside `max_allow`), and logged with outcome
`ceiling`. A value that is not a number above zero - text, `true`,
zero, a negative, a fraction of a MB - is a bad request. A flag value
that is not a limit stops the door at start. `GET /health` with the
token reports all three ceilings. The rule lives in one place,
`velaris.run_limits`, used by both doors.

**The HTTP door's default ceiling is `io`.** Without `--max-allow`,
`velaris serve` granted every effect, `ffi` included, to anyone holding
the token; the MCP server has defaulted to `io` since 3.4. The door now
does too, and starting it wider takes naming the grants:
`--max-allow io,env,fs,net,clock,rand,ffi` is what 3.4 granted by
default. Its start-up lines say which ceiling is the default.

One more change came with the flag: `velaris serve --max-memory-mb`
was accepted before, and - through the command line's process-wide
`--max-memory-mb` - set an address-space cap on the door's own process
on Linux and macOS, never documented. It is now the most each run may
have, and the door's process is not capped.

**STABILITY.md.** What semantic versioning covers here - the language
as SPEC.md states it, the error codes, `velaris.audit/1`, the library
API, the budget grammar, the command line's commands and documented
flags - and what it does not: internals, the proof cache, the wording
of messages, which promises happen to prove, the formatter's style,
anything marked provisional. The rules: breaking changes only in a
major version, security fixes included; a deprecation announced in a
minor version, warning for at least one more, removed no sooner than
the next major; an error code never reused for another meaning, and a
removed one kept listed as removed (`REMOVED_ERRORS`, and a section on
the errors page - empty today). A stronger prover refusing a program
its proof shows wrong is stated as the one exception, and why.

Its "Breaks we have made" section is longer than expected when it was
begun. 2.0 and 3.0 broke in major versions, as promised. **3.4 shipped
three breaking changes in a minor version and named them as such, and
it should have been 4.0**; it was not retagged because 3.4.0 was
already published, and this policy exists so that it does not happen
again. Reading every entry for STABILITY.md found more: 3.4 broke three
further things it did not list (`serve` and the MCP server refusing an
unknown argument, `GET /health` without the token no longer naming the
ceiling); 3.3 shipped five breaking changes as fixes and named none;
and eight earlier minor releases, 2.20 to 3.1, each broke something -
64-bit integers, the formatter's style, three builtins made fallible,
the http module's `call`, `audit().problems`, the doors' 2.59 limits,
`args()`, Windows memory caps. E610 was reused, in 2.59, for a meaning
other than the one 1.4 gave it. All of it is listed there, and 2.0 is
recorded as its entry and commit describe it: four builtins made
fallible. README and CONTRIBUTING link it; SPEC.md section 15 points
to it.

Also corrected: the 3.3 entry of this file lost its heading in the 3.4
release, so its text read as part of 3.4. The heading is restored.

**The capability ratchet.**

    velaris capabilities init [path]          # write velaris.capabilities
    velaris capabilities check [path]         # exit 1 if the surface widened
    velaris review --against <ref> [path]     # a pull request's delta, as facts

A change can add capability to a repository a little at a time - a
helper that builds a URL, a function that reads a file, a call three
levels down that sends one to the other - and no single diff looks
alarming, which is how such a change passes a reviewer and a
diff-based monitor. Capability is binary and cumulative, so the steps
add up to exactly what one large step would have done; but only a
comparison with a declared baseline sees the sum. This release makes
that comparison, and makes it the only one the gate uses.

- **`velaris capabilities init`** reads every `.vel` file under the
  path, except in `.git` and what git ignores, and writes
  `velaris.capabilities` (`velaris.capabilities/1`, velaris-spec 0.3
  section 9): the repository's surface - every grant its programs need,
  in the budget grammar, and for `fs` and `net` the most operations one
  run can perform, or `null` where the text sets no bound - and for each
  program its own grants and counts and the effects each of its
  functions declares, or that it does not compile; with the Velaris
  version and the date. One grant per line and one function per line,
  so accepting a widening is a one-line diff. It refuses to replace an
  existing file without `--force`.
- **`velaris capabilities check`** derives the same from the working
  tree and compares it with the file - never with the previous commit -
  and exits 1 when anything widened: a grant the surface does not cover
  (a new effect, a new module, a path outside every recorded one, so
  `./data` widened to `./` fails; a host, so `api.example.com` made
  `*.example.com` fails; a scoped grant made unscoped); more `fs` or
  `net` operations in a run than recorded (10 raised to 1000 fails); a
  program the file records needing something its own entry does not
  give, even when another program already had it; and a function the
  file records gaining an effect, even when its program's grants and
  counts stay the same. Narrowing never fails and is reported. A new
  program is held to the surface alone. Each widening names what
  widened, the file, function, line and call that introduced it, the
  chain of calls from `main` that reaches it, and the edit to the file
  that would accept it. A baseline from another Velaris version is
  compared with a warning, not a failure. A baseline that is missing,
  is not `/1`, or does not read exits 2 and never passes. `--json` is
  `velaris.capabilities-check/1`; `--sarif` reports each widening as an
  error at its line, through the 3.4 SARIF code, with two new error
  rules, `capability-widened` and `capability-effect-gained`, and a
  note, `capability-narrowed`, on the errors page.
- **What a program needs** is read from its text: the effect and type
  checks run and the prover does not, so the result is the same with
  and without z3. A path, URL or module is taken as named when it is a
  literal or a variable bound once to one; one built while running is
  recorded as the unscoped grant, which a scoped baseline does not
  cover. The operation bound comes from loops whose counter and limit
  the text fixes - `for i in 0 to 10`, a counter started by `let`, a
  list literal - multiplied through nesting and calls; a loop the text
  does not bound, and recursion, have none.
- **`velaris review --against <ref>`** runs the derivation and the
  audit on the files at a git ref - read with `git show <ref>:<path>`,
  nothing checked out - and on the working tree, and reports whether
  the capability surface changed, the proven share before and after,
  functions that became fallible, hosts, paths and modules newly named,
  whether `velaris.capabilities` itself changed, and one word of risk
  computed from those facts alone: `high` when the surface widened, or
  the declared surface widened or was removed; `medium` when it did not
  but a program or function the ref had came to need more, or the
  proven share fell; `low` when nothing widened and the proven share
  did not fall. No count of changed lines enters it. It informs a
  reviewer; the gate is `check`, since a review against the commit
  before loses a widening the moment it is merged.
- **The GitHub Action** has a `capabilities` input, `check` by default
  when `velaris.capabilities` exists and `off` otherwise - except that a
  pull request deleting the file fails, since that would turn the
  ratchet off; `capabilities: off` in the workflow is the visible way to
  do that. Its findings are uploaded to code scanning beside the check's
  when `sarif` is on. The pull-request comment from 2.63 now holds the
  ratchet's result, each widening with the edit to the baseline that
  would accept it, and the review delta against the pull request's
  base.
- **This repository commits its own `velaris.capabilities`**, written by
  `velaris capabilities init .`: 172 programs, 22 of them examples and
  benchmark rows built to be refused, recorded as not compiling. CI runs
  `velaris capabilities check .` on every leg.
- **`velaris.audit/1` gains `ffi_any`**, added within version 1: true
  when some Python call names its module with a value built while
  running, which `ffi_modules` cannot list. The ratchet needs it - a
  computed module name must not slip past a baseline naming `ffi:math`
  - and it closes velaris-spec's open question Q4. The audit also warns
  when it is true.

**`check_ratchet.py`**, 62 checks, proves the rules rather than
asserting them, through the command line in scratch trees and real git
histories. The gradual case: six commits, the first five adding pure
helpers, a text constant holding a URL and a call to print, each
passing against the baseline, and the sixth sending a summary to that
URL through a helper three calls below `main` - which fails, naming
`net:collector.example.net` as a new effect, `lib/deliver.vel` line 2
in `send`, and the chain `main -> summary -> deliver -> send`, while a
review of each commit against the one before calls the first five
`low`. Why the gate must be the baseline: a count widened and merged
anyway keeps failing the check at every later commit, while a review
against the previous commit reports nothing one commit later; and seven
steps from 10 to 1000 are reported as 1000 against the declared 10,
where the previous commit shows 640 to 1000. Widenings through an
import (the surface unchanged, the program's entry not), through the
standard library, through a path prefix, a count, a wildcard host, a
URL, path and module built while running, a new module, a new
direction, a hidden directory, and a program whose `main` is imported
from outside the tree. An effect added to a function whose program's
grants and counts stay exactly as they were, reported. And the changes
that must pass: narrowing; reordering functions, imports, `uses`
clauses and statements, renaming locals, reformatting and `velaris
fmt`; a file with no effects; a new program inside the surface; a
literal moved into a variable; a function renamed or moved to another
file; a program that stops compiling. Declared prefixes, wildcards and
ports; a baseline from an older and from a newer version (a warning
that never hides a widening); `init` without `--force`; four baselines
that cannot be read (exit 2); the JSON and the SARIF, which validates;
23 covering cases and 6 operation-bound cases. CI runs it on every leg.

**What the ratchet cannot do, and the cases where one of the two rules
was not achieved.** A widening never passes and a non-widening change
never fails, among the changes `check_ratchet.py` holds; beyond them,
these are the known limits, each stated in THREAT_MODEL.md:

- *A widening that passes:* a function renamed in the same change that
  gives it an effect is a new function, held to its program's entry and
  the surface but not to what its old name declared - so a pure helper
  renamed while it gains an effect its program already had is not
  reported as a function that gained one. What a granted `ffi` module
  does is outside the text. A symbolic link under a recorded directory
  is that directory's content.
- *A change that does not widen, reported as one:* the bound on
  operations comes from fixed rules, so a loop bound moved behind a
  function call (`for i in 0 to limit()`) loses its bound and is
  reported as unbounded; a path or URL passed to a helper as a
  parameter is taken as unscoped, as it always is, even when every
  caller passes a literal; and a path written with `\` is covered only
  by the same text.

**What a 3.4 user has to change.**

1. A client of `velaris serve` that relied on the door granting more
   than `io` without `--max-allow` must start the door with
   `--max-allow` naming what it needs.
2. A client of either door that sends a `timeout` over 30 seconds or a
   `max_memory_mb` over 512 must have the operator raise
   `--max-timeout` or `--max-memory-mb`, or ask for less.
3. A client that sends `timeout` or `max_memory_mb` as text (`"30"`),
   or `0` to mean the default, must send a number, or leave the field
   out.
4. An operator who passed `--max-memory-mb` to `velaris serve` to cap
   the door's own process gets a per-run ceiling instead; cap the door
   with the operating system (`ulimit -v`, a container limit) if that
   was the intent.

Additions, which break nothing: `velaris capabilities`, `velaris
review`, the Action's `capabilities` input (off unless the file
exists), `ffi_any`, and the new SARIF rules.

**velaris-spec 0.3.** Section 9 stops being provisional:
`velaris.capabilities/1` replaces the provisional `/0`, which no
version of this compiler wrote. The spec states the document, the
derivation from a program's text, the operation bound, the covering
rule (a path holding `\` now compared whole), and the comparison as
five rules, W1 to W5, with a table of what widens for each kind of
scope - effect, path, host, module, count, function - and the rule that
a check compares with the baseline and with nothing else. Q4 is
resolved by `ffi_any`. Its conformance section adds `check_ratchet.py`.
It still quotes this repository's SPEC.md sections 6, 7 and 7.1 word
for word - none of them changed - so its drift check passes; its CI now
also validates this repository's `velaris.capabilities` against the
`/1` schema.

**Sources, named** (CONTRIBUTING.md rule): the four parts of this
release were specified by the maintainer. No published work is on
record as the source of the ratchet's design, so none is named. The
CHANGELOG scan behind STABILITY.md's record was made in this release,
and its findings were checked against the entries and against git
history (E610's two meanings are in commits `616579f`, `79808fc` and
`b5a4582`).

**The MCP manifest changes, by design.** `velaris_run`'s description
and the descriptions of its `timeout` and `max_memory_mb` inputs now
name the ceilings, so the signed `velaris-mcp-tools-4.0.0.json` differs
from 3.4.0's: `velaris mcp-verify` against a 3.4.0 manifest reports
`velaris_run` as CHANGED, which is what it is for.

**Verified**, on Windows 11 with Python 3.13, before tagging, with the
proof cache cleared first. With the prover: `run_tests.py` 92/92,
`check_library.py` 165 correct (one skipped: the symlink case is POSIX
only), `check_sandbox.py` 45, `check_fallible.py` 26,
`check_refusals.py` 21, `check_termination.py` 44, `check_pool.py` 39,
`check_ratchet.py` 62, none wrong; `fuzz_native.py 30` agrees,
`benchmark/run.py --quick --check` matches `results.json`, `velaris
test examples/std_test.vel` 7/7, `velaris fmt --check` clean, and
`velaris capabilities check .` passes on the clean tree. Without the
prover, in a fresh virtual environment holding this tree, jsonschema
and no z3 or llvmlite: the same thirteen pass, with `check_library.py`
162 correct (two skipped for needing the prover, one POSIX only) and
`check_refusals.py` 11 with 10 skipped for needing the prover. Every
workflow file and `action.yml` parse as YAML. The Action's new steps
were run outside GitHub as far as they go: the ratchet step under Git
Bash in four cases (no baseline, off; a baseline and nothing widened,
pass; `clock` added, fail naming it; a pull request deleting the
baseline, fail), and the comment's Python against real `capabilities
check --json` and `review --json` output. `velaris review --against
HEAD` over this repository took 45 s with the prover. velaris-spec
0.3's `tools/check_sync.py` passes against this tree, its
`tools/validate.py` passes with `--capabilities` on this repository's
`velaris.capabilities`, and the `velaris.audit/1` documents 4.0.0
produces for all 109 files in `examples/` and `stdlib/` validate
against its audit schema, `ffi_any` included.

## 3.4 - The doors are locked, and the findings go where findings go

`velaris serve` ran any program sent to it by anyone who could reach
its port; binding to localhost and printing a warning was the whole of
the control. The MCP server granted whatever budget its caller asked
for, `ffi` included. Neither door recorded what it was asked to do, and
nothing let a client operator tell whether the MCP server's tool
descriptions were the ones that were released. This release adds the
four controls, and SARIF output so findings reach code scanning.

- **Bearer authentication on the HTTP door.** Every endpoint but
  `GET /health` needs `Authorization: Bearer <token>`. The token comes
  from `--token-file <path>`, else `VELARIS_TOKEN`, else the door makes
  one with `secrets.token_urlsafe(32)` and prints it once. It is never
  read from the command line: `--token`, in either spelling, is refused
  at start, and the refusal does not repeat the value. Tokens are
  compared with `secrets.compare_digest` over sha256 digests; a missing
  token, a wrong one, another scheme, a bare `Bearer` or the token in a
  query string all get the same 401 body and a bare
  `WWW-Authenticate: Bearer` challenge, on every path including unknown
  ones, so nothing is learned about the door without the token. The
  door removes `VELARIS_TOKEN` from its environment before any worker
  starts, so a program granted `env` cannot read it. `GET /health` no
  longer names the ceiling to a caller without the token.
- **`--no-auth`**, for local development, is refused unless `--host` is
  `127.0.0.1` or `localhost`, and prints a warning on every start. In
  its place a request must name a loopback `Host`, carry no other
  `Origin`, and post as `Content-Type: application/json`, which keeps a
  web page in a browser on the same machine (a cross-site `fetch`, or a
  DNS-rebinding page) from sending the door programs. It does not stop
  another local program, and the warning says so. These three checks
  were not in the request for this release; without them `--no-auth`
  would have let any open web page run programs.
- **The door refuses arguments it does not know**, so `--max-alow io` is
  an error instead of a door whose ceiling silently stayed at every
  effect. A non-local `--host` now also warns that the door speaks
  plain HTTP and the token crosses the network in clear without a TLS
  proxy in front. The `Server` header no longer carries the Python
  version.
- **A ceiling on the MCP server.** `--max-allow` takes the grammar the
  HTTP door takes - effects, `fs:read:`/`fs:write:` paths, `net:` hosts
  and ports, `ffi:` modules, `@N` counts - and the same `Budget.covers`
  check. A `velaris_run` asking for more at any level is refused with
  `isError` and the body the HTTP door sends with its 403: what was not
  granted, and `max_allow`. **Without the flag the ceiling is `io`**,
  and `velaris_run`'s description and the `.mcpb` manifest say so. A
  ceiling that does not parse, or an unknown argument, stops the server
  at start.
- **A signed manifest of the MCP tools.** The release workflow asks the
  MCP server inside the wheel it publishes for its tools, writes
  `velaris-mcp-tools-X.Y.Z.json` (`velaris.mcp-tools/1`: each tool's
  name, the sha256 of its description, the sha256 of its input schema
  in canonical form), signs it with sigstore alongside the wheel, sdist
  and SBOM, checks the signed manifest against the server with
  `velaris mcp-verify`, and attaches both to the release.
  `velaris mcp-verify <manifest> -- <server command>` verifies the
  signature as this workflow at the manifest's tag, starts the server
  the way a client does, and reports every tool whose description or
  schema changed and every tool added or missing (exit 1), or why it
  could not check (exit 2). It lives in `velaris.py`, not in the server
  file it checks. `velaris mcp-manifest` makes a manifest for any
  server. EMBEDDING.md says how a client operator uses it and what it
  does not tell them.
- **Invocation logging on both doors.** One JSON line per call,
  `velaris.invocation/1`: when the call arrived, the door, the endpoint
  or tool, the outcome, the duration, the budget granted, the effects
  performed, what was refused and by what, the caller's address (HTTP),
  and the sha256 of the source - never the source, the output, request
  headers, the path as sent, or the token, which is also struck out of
  any line it could appear in. To stderr, or appended to `--log-file`;
  `--log minimal` keeps six fields, and nothing turns the log off.
  "Effects performed" is new in the runtime: `RunResult.effects_used`
  counts, per effect, the builtin calls the budget let through; it
  comes back from the pool workers the doors use, and is `None` for a
  child that could not report it.
- **SARIF 2.1.0.** `velaris check --sarif`, `proofs --sarif` and
  `audit --sarif` write one run whose driver is `Velaris` at this
  version, with a rule for every code in the compiler's error table and
  for each finding that is not an error, each rule linking to its row
  on the published errors page. Results carry the file, the line and
  the message. Errors are `error`; a promise left to runtime is a
  `warning` (an `error` under `--strict`); a function promising nothing
  about its data, a loop not shown to end and each effect a function
  may perform are `note`. The output is validated against the OASIS
  schema, vendored under `tests/` and held to its digest, in
  `check_library.py`. The GitHub Action has a `sarif` input, true by
  default, that writes the file and uploads it with
  `github/codeql-action/upload-sarif` pinned to the v4.38.0 commit.
- **What SARIF output leaves out.** A Velaris fix is a sentence; a
  SARIF `fix` must carry the exact bytes to change (`artifactChanges` is
  required by the schema). Rather than make up an edit to fill the
  slot, the suggestions go in each result's `properties.fixes`. Figures
  with no line - a proven share, an audit's `safe_command` - go in the
  run's property bag, the latter as each file's `velaris.audit/1`
  document unchanged.
- **The error table.** `velaris.ERROR_TABLE` holds all 62 codes the
  compiler, runtime and library can give, one line each; the published
  errors page and the SARIF rules are both built from it, and
  `check_library.py` reads `velaris.py`'s syntax tree and fails if a code
  is given anywhere that is not in the table, or is in the table and
  given nowhere. The page used to be a scrape of `VelarisError(...)`
  calls and missed E610, E611 and E612, which are reported another way;
  it now lists all 62, with an anchor on each row.

**What a 3.3 user has to change.** README's stability rule is that
breaking changes wait for a major version; these three ship in a minor
version because each closes an open door, and they are listed here so
nobody meets them by surprise:

1. A client of `velaris serve` must send `Authorization: Bearer
   <token>`. Start the door with `--token-file` or `VELARIS_TOKEN`, or
   read the made token from its first lines of output.
2. An MCP client that relied on `velaris_run` granting more than `io`
   must start the server with `--max-allow`, as EMBEDDING.md shows.
3. A workflow using the Action needs `permissions: security-events:
   write` for the upload, and code scanning enabled on a private
   repository - or `sarif: "false"`.

THREAT_MODEL.md did not, in fact, list the unauthenticated door
anywhere, as a residual risk or otherwise; it now has the door and the
MCP server's caller in the trust boundary, the four controls in what is
defended, what they do not defend in the list of what is not, and
residual risks for the token, the ceiling, the tool manifest and the
log. COMPLIANCE.md maps the four controls to OWASP MCP Top 10 (v0.1,
beta) items MCP01, MCP02, MCP03, MCP07 and MCP08.

**Verified**, on Windows 11 with Python 3.13, before tagging, with the
proof cache cleared first. With the prover: `run_tests.py` 92/92,
`check_library.py` 142 correct (one skipped: the symlink case is POSIX
only), `check_sandbox.py` 45, `check_fallible.py` 26, `check_refusals.py`
21, `check_termination.py` 44, `check_pool.py` 39, none wrong;
`fuzz_native.py 30` agrees, `benchmark --quick --check` matches
`results.json`, `velaris test examples/std_test.vel` 7/7, `velaris fmt
--check` clean. Without the prover, in a fresh virtual environment
holding this tree, jsonschema and no z3 or llvmlite: the same eleven
pass, with `check_library.py` 139 correct (two skipped for needing the
prover, one POSIX only; the SARIF output validates there too, and
`check --strict --sarif` reports that it could not check rather than
passing) and `check_refusals.py` 11 with 10 skipped for needing the
prover. Every workflow file and `action.yml` parse as YAML.
velaris-spec's `tools/check_sync.py` and `tools/validate.py` pass
against this tree; SPEC.md §6, §7 and §7.1, the grant grammar and
`velaris.audit/1` are unchanged, so the spec stays at 0.2. The new
release steps were run by hand as far as they go without GitHub's
signing identity: the wheel was built, installed in a clean
environment, `mcp-manifest` made the manifest from its server, and
`mcp-verify --skip-signature` matched 4 of 4 tools; the signature check
itself was run against the sigstore bundle this workflow made for the
3.3.0 SBOM, accepting it and refusing it for changed bytes and for the
wrong tag.

## 3.3 - The capability check now means what the spec says

(This heading was lost from this file in the 3.4 release and restored
in 4.0; the text below it is unchanged.)

velaris-spec 0.1 was extracted from 3.1.1 and, in writing each rule down
precisely, found five places where this compiler did not do what the
format says. 3.2 recorded them and changed no compiler code. 3.3 fixes
all five, and velaris-spec goes to 0.2 in step, resolving the open
questions the fixes close.

- **`ffi:M` is bounded to the module a call actually reaches, not just
  the one it names.** The function argument of `py`, `py_int`,
  `py_float`, `py_json` and `py_new` may be a dotted path of attributes,
  and a granted module's attributes include the modules it imported. So
  `py("json", "codecs.encode", ...)` ran codecs code under `ffi:json`,
  because `json` imports `codecs` into its namespace and the chain walked
  straight into it. The whole dotted path a call names is now checked:
  the attribute chain is resolved step by step, and whenever a step
  yields an object whose owning module (a module's own name, or an
  attribute's `__module__`) has a top-level package outside the grants,
  the call is refused with E311 naming the module actually reached. The
  same check applies to a method or field reached through a handle
  (`py_do`, `py_field`) and to a non-JSON result kept as a handle. Where
  the owning module of an object reached along the chain cannot be
  determined - a bare code object, a frame, a reflective handle - the
  call is refused rather than allowed: the bound errs toward refusing
  more. Inert data (numbers, text, bytes, lists, maps) is not code from
  any module and is not checked, so a legitimate deep attribute like
  `json.decoder.JSONDecoder` still works. This is a security fix; where
  the chain cannot be placed soundly it refuses, and THREAT_MODEL.md and
  the spec say what remains reachable: a granted module can still do
  whatever that module itself can do.

- **`ffi` grants are additive, like `fs` and `net`.** SPEC.md 7.1 says
  grants are additive; the parser restricted `ffi` to the named modules
  when both `ffi` and `ffi:M` appeared, so `ffi,ffi:math` granted `math`
  alone. It now grants every module: a plain `ffi` means every module,
  and the wider grant wins in either order, matching the reference text
  and `fs`/`net`. (velaris-spec Q2.)

- **`safe_command` round-trips.** It wrote an IPv6 host without brackets
  (`net:::1`, which parses as the host `:` at port 1) and could not
  express a path or host containing `,` or `@`. An escaping rule is
  defined in the spec (v0.2 §5.1, §5.2) and implemented on both sides:
  IPv6 hosts are bracketed (`net:[::1]`, `net:[::1]:443`), and `, @ [ ]
  %` are percent-encoded inside a path or host component and decoded when
  the budget is parsed. `parse_budget` of an audit's `safe_command` now
  reproduces the exact budget for awkward paths and hosts.
  (velaris-spec Q5.)

- **The budget parser is strict.** An unknown effect name in a `uses`
  clause is a compile error (E300) naming the seven real effects;
  `uses io, teleport` no longer compiles and no longer reaches
  `velaris.audit/1`. Every malformed budget is a clean budget error, not
  a traceback: a count is ASCII digits only, so `fs@²` is a budget
  error rather than an uncaught `ValueError`; `ffi` takes no count and
  `ffi:` needs a module; an unbracketed IPv6 address, a stray bracket, a
  doubled `@` and a scope on an effect that takes none are each refused
  with a readable message. (velaris-spec Q1, Q6.)

- **The command line's `audit --json` emits `velaris.audit/1`.** It
  printed an older, unversioned shape the schema rejected; it now calls
  the library's `audit().as_dict()`, the same document the library, the
  MCP server, the HTTP door, the npm package, the CrewAI tool and the
  Action all emit. Its `safe_command` for `examples/json_ffi.vel` now
  says `ffi:math,io` rather than `ffi,io`. (velaris-spec Q3.)

**The README's claim about `ffi:M` is restored.** In 3.2 the README's
"grants Python for those modules only; any other is refused" was weakened
to say what was and was not reachable, because the claim was false: a
granted module was a door into the modules it imported. With the first
fix above it is true again, and the strong wording is back.

**velaris-spec 0.2.** The spec is revised where the behaviour changed and
bumped to 0.2 with a dated annotated tag. It resolves Q1 (unknown names
in `uses` are rejected), Q2 (`ffi` is additive; the wider grant wins),
Q3 (the command line emits `velaris.audit/1`), Q5 (`safe_command` and
`net_hosts` bracket IPv6 and the escaping rule holds `,` and `@`), and
Q6 (non-ASCII count digits, `ffi:M@N` and `ffi:` are budget errors); the
escaping rule is added to §5.1 and §5.2. Its section 2 still quotes this
repository's SPEC.md §6, §7 and §7.1 word for word - those sections did
not change, since "grants are additive" is now true for `ffi` too - so
`tools/check_sync.py` still passes.

**Sources, named** (CONTRIBUTING.md rule): every fix here comes from the
velaris-spec 0.1 extraction of 3.1.1, recorded in that spec's section 11
as open questions Q1, Q2, Q3, Q5 and Q6. HALL_OF_FAME.md credits the
extraction under the standing challenge.

**Verified**, on Windows 11 with Python 3.13, before tagging. With the
prover: `run_tests.py` 92/92, `check_library.py` 82 correct,
`check_sandbox.py` 45, `check_pool.py` 39, `check_refusals.py` 21,
`check_fallible.py` 26, `check_termination.py` 44, none wrong. Without
the prover, in a fresh virtual environment holding this tree and no z3 -
the subset the conformance suite requires: `check_termination.py` 44,
`check_sandbox.py` 45, `check_refusals.py` 11 with 10 skipped for needing
the prover, `check_fallible.py` 26, `check_library.py` with the runtime
fallback asserted where a proof was, none wrong. `fuzz_native.py 30`,
`benchmark --quick --check`, `velaris test examples/std_test.vel` and
`velaris fmt --check` all pass. velaris-spec `tools/check_sync.py` and
`tools/validate.py` pass against this tree.

## 3.2 - The capability format, published as a spec

Nothing in the compiler changed: `velaris.py` differs from 3.1.1 only
in its version string.

**velaris-spec 0.1.** The capability format has a specification of its
own now, in a separate repository,
[gowrishankar-infra/velaris-spec](https://github.com/gowrishankar-infra/velaris-spec),
tagged v0.1: the seven effects and what "transitive" means; the grant
grammar - `fs:read:path`, `net:host:port`, `net:*.domain`,
`ffi:module`, `@N` - as this compiler parses and enforces it, edge
cases included; what a budget guarantees at runtime and what it does
not; `velaris.audit/1` field by field; and `velaris.capabilities/0`, a
ratchet baseline for CI that this compiler does not read yet, marked
provisional until it does. It is written so that the format can be
implemented in another language without reading `velaris.py`, and
where a rule could not be stated precisely it says so, as one of eleven
open questions. Its section 2 quotes sections 6, 7 and 7.1 of this
repository's SPEC.md word for word; `tools/check_sync.py` there, run
weekly by its CI, fails if the two drift. The spec is CC0, so anyone
may implement it; this implementation stays MIT.

Conformance is defined here, not there. ARCHITECTURE.md now names
`check_termination.py`, `check_sandbox.py`, `check_refusals.py`,
`check_fallible.py` and `check_library.py` as the conformance suite,
and an implementation claiming velaris.capabilities compliance must
pass the subset that does not require the prover. The spec's JSON
Schema for `velaris.audit/1` was held against the audit of every one of
the 107 `.vel` files in `examples/` and `stdlib/`, and all 107
validate.

**What writing it down found.** Stating each rule precisely enough for
someone else to implement it turned up places where the compiler, its
documentation and its own SPEC.md do not say the same thing. None is
fixed here, because this release changes no compiler code; each is
recorded in the spec as what the reference does, and listed there as an
open question:

- **`velaris audit` on the command line is not `velaris.audit/1`.**
  With `--json` it prints an older, unversioned summary - `compiles`
  for `ok`, `errors` for `problems`, `functions` as a count - and both
  its `safe_command` and the command it prints under HOW TO RUN IT
  SAFELY are built from the coarse effects alone: for
  `examples/json_ffi.vel`, which calls only `math`, it says
  `--allow ffi,io` where `velaris.audit()` says `--allow ffi:math,io`.
  The library, the MCP server, the HTTP door, the npm package, the
  CrewAI tool and the Action's PR comment are all built on
  `velaris.audit/1`; the command line is the exception. The schema
  rejects the command line's output, and the spec says so rather than
  bending the schema to fit.
- **Grants are not all additive.** SPEC.md 7.1 says they are. For `fs`
  and `net` that holds; for `ffi` it does not: `ffi,ffi:math` grants
  `math` alone. The spec follows the parser, since that is the reading
  that refuses.
- **`ffi:M` checks the module name a call gives, not what is reachable
  through the module.** The function argument of `py` may be a dotted
  path of attributes, and a granted module's attributes include the
  modules it imported. THREAT_MODEL.md already said the allow-list
  narrows which modules and not what a module does; the README said
  "any other is refused", and now says what is refused and what is
  not.
- **`safe_command` is wrong in three cases.** It writes an IPv6 host
  without brackets (`net:::1`, which parses as the host `:` at port 1);
  it passes through a path containing `,` or `@`, which the grammar
  cannot hold; and it copies in any name a `uses` clause gives, because
  `uses io, teleport` compiles and `teleport` reaches the audit.
- **The budget parser reads a count with Python's `isdigit`**, so
  `fs@٣` is a count of 3 and `fs@²` stops the parser with an uncaught
  error instead of a budget error; and `ffi:math@5` is accepted as a
  module literally named `math@5`.
- **Six rules the spec states have no case in any `check_*.py`
  suite**: a dotted function path through a granted module, `ffi`
  together with `ffi:M`, a URL without a scheme taken as HTTPS, IPv6
  grants, an existence check under a write-only grant, and `@0` or a
  count spent by an operation that then fails. The spec lists them as
  its Q9; adding the cases is work for a release that may change
  behaviour if a case fails.

**Related work, cited.** The README has a Related work section after
the opening, naming TACIT (ACM CAIS '26, arXiv 2603.00991), CaMeL and
WASI, what each does, and what Velaris does differently, including what
it does not do: it tracks no data flow, and its command line grants
every effect when no budget is given. The spec's PRIOR_ART.md has the
longer account, with object capabilities, in-toto and SLSA, SARIF,
Deno's permissions and effect systems. The README's `velaris card` line
said ~1,500 words, the size of the card in 2.41; it is 3,335 words by
`wc -w` now, and the README says ~3,300 in both places.

**Sources, named.** CONTRIBUTING.md gains a rule: when a design
decision comes from published work, name the source in the CHANGELOG
entry for that release; say which person, model or bot found a review
finding; and when the origin is not known, do not guess. Applied
backwards where the record allows it. 2.41.1 (a Gemini model), 2.41.2
(a ChatGPT model), 2.42 and 2.44 to 2.47 (a Claude model) now say which
model family found what, from the maintainer's account, since none of
those entries recorded it at the time and HALL_OF_FAME.md had declined
to guess; HALL_OF_FAME.md carries the same names now. 2.59 names
CodeRabbit on crewAIInc/crewAI#7279, from the public pull request,
which also dates its review 2026-09-05; HALL_OF_FAME.md had said
2026-09-10, and is corrected. Nothing else was attributed, because no
other entry's provenance is on record.

This release's own sources, under the new rule: the schemas are JSON
Schema draft 2020-12, the spec's requirement words are those of RFC
2119 and RFC 8174, and its license is Creative Commons CC0 1.0. The
work in PRIOR_ART.md is related work, not a source - none of it is on
record as the origin of a Velaris design decision, and the spec says
so.

**Verified**, on Windows 11 with Python 3.13, before tagging. With the
prover: `run_tests.py` 92/92, `check_library.py` 75 correct,
`check_sandbox.py` 34, `check_pool.py` 39, `check_refusals.py` 21,
`check_fallible.py` 26, `check_termination.py` 44, none wrong; the one
skip in each of the first two is the symlink escape, which needs POSIX.
Without the prover, in a fresh virtual environment holding this tree
and no z3, as rule 7 asks - the subset the conformance suite requires:
`check_termination.py` 44, `check_sandbox.py` 34, `check_refusals.py`
11 with 10 skipped for needing the prover, `check_fallible.py` 26,
`check_library.py` 73 with the runtime fallback asserted where a proof
was, none wrong. The reference implementation passes its own
conformance subset.

## 3.1.1 - A pool test that passed for the wrong reason

`check_pool.py` claimed to hold a program that reaches into the
compiler through a granted `ffi` module, adds `fs` to the live budget,
and is then unable to leave it added for the next program. It did not.
The program named `py("velaris", "EFFECT_BUDGET.add", ["fs"])`, and a
worker runs `velaris.py` as `__main__` - so that name imported a
*second* copy of the module and widened that copy's budget, never the
one the interpreter was enforcing. The next program was refused `fs`
because it had never been granted, not because anything was reset. The
check passed, and would have passed just as well with
`reset_program_state` deleted.

It now names `__main__`, which is the live module, and reads a file
immediately afterwards so the suite can assert the widening really took
hold before it asserts that the next program is refused. Two checks
where there was one:

    ok  a program CAN widen its own budget through ffi - the cliff is
        real, and this is what the next check is against
    ok  ...and it cannot widen it for the next program

The reset was correct the whole time - the counted-grant check
(`fs:read:<dir>@2`, spent per program rather than per worker) was
already exercising the same reinstall from a different angle, and it
still passes. What was wrong was a test whose label was stronger than
its body, which is worse than no test at all: it is the one thing that
makes a suite untrustworthy about everything else in it. The 3.1 entry
below says "the suite has one that does exactly this"; of 3.1.0 that
sentence was false, and it is true from 3.1.1.

Also here: `check_library.py`'s skip messages said "(needs the prover)"
for skips that had nothing to do with the prover - the macOS memory cap
and the POSIX-only symlink escape now say why they were actually
skipped.

39 checks in `check_pool.py`, all passing with and without the prover.
Nothing in `velaris.py` changed.

## 3.1 - A pool that keeps its budget, memory caps on Windows, and a lockfile

**velaris.Pool: bounded runs without a new interpreter every time.**
Every run with a `timeout` or a `max_memory_mb` started a Python
process, about a tenth of a second before a line of Velaris was read.
An agent platform calling `run` thousands of times an hour paid that
every time.

    pool = velaris.Pool(size=4, allow={"io"}, timeout=30,
                        max_memory_mb=512)
    result = pool.run(source)          # the same RunResult run() returns
    pool.close()                       # also a context manager

Measured by `check_pool.py` on the machine this was written on, 200
sequential bounded runs of a small program: **46.56 s a process at a
time, 0.48 s on a pool** - 233 ms each against 2.4 ms each, 96.7x. The
suite asserts at least 3x and prints both numbers, so the claim is
re-measured wherever it runs rather than quoted from here.

The speed is why it exists. The isolation is why it can be used, and
these are the rules, each one asserted in `check_pool.py`:

- **The budget is the pool's, not the program's.** It is parsed once,
  when the pool is made, and installed by each worker at startup.
  `pool.run` takes no `allow` argument - there is nowhere for a caller
  or a program to ask for more, and a different budget means a
  different pool. The budget is re-asserted from the pool before every
  program, so an `@N` count is spent per program rather than shared
  across a worker's whole life. A program that reaches into the
  compiler through a granted `ffi` module and adds `fs` to the live
  budget - the suite has one that does exactly this - cannot leave it
  added for the next program.

- **A worker is used once unless the run was clean.** Anything other
  than `ok` - a refused effect, a failure that escaped, a program that
  did not compile, the timeout, the memory cap - kills the worker and
  starts a fresh one. This is stricter than it has to be: a program
  that failed to compile never ran, so it left nothing behind, and
  retiring its worker costs a restart. It is stricter on purpose,
  because "only a clean run hands its worker back" is a rule a reader
  can check in one line of `Pool.run`, and the weaker version is a
  rule about which failures are harmless.

- **A reused worker starts empty.** Before every program the child
  resets every module-level mutable there is. Searching for them was
  the work; the list, exhaustively, is `PROGRAM_ARGS`,
  `EFFECT_BUDGET`, `FFI_MODULES`, `FS_GRANTS`, `NET_GRANTS`,
  `OP_LIMITS`, `OP_COUNTS`, `PY_OBJECTS` (handles from `py_new`,
  closed by the program or not), `PY_NEXT` (so handle numbering starts
  again), `TRACE`, and `_NATIVE_KEEPALIVE` - which holds the JIT
  engines and, through them, the native text arena. There is no proof
  cache in memory to clear: `check_proofs` keeps its cache on disk and
  only when asked (`use_cache=True`), and the library never asks. Three
  things that belong to the process rather than the module are put
  back too, because a granted `ffi` module can change all three: the
  working directory, the environment, and the recursion limit the
  interpreter raises. They are named in `MUTABLE_GLOBALS` and
  `reset_program_state`, and `check_pool.py` parses `velaris.py`'s own
  module-level assignments and fails if a mutable one appears in
  neither that list nor its list of constants - so the next person to
  add a global cannot forget. That is now rule 6 in ARCHITECTURE.md.

- **The parent owns the deadline.** A worker that has not answered
  within `timeout` is killed by the parent, not asked to stop, and a
  replacement is started; the call returns E610.

- **A program cannot reach the pipe.** The worker keeps private
  duplicates of its own file descriptors 0 and 1 for the protocol and
  points the program's at the null device. The suite has a program
  that runs `echo` through `ffi:os` straight at file descriptor 1; the
  shell's output goes nowhere and the next program still runs.

- **Closing kills every worker**, including one still running a
  program. A pool collected without `close()` is closed by its
  finalizer, one that outlives the interpreter is closed at exit, and
  a worker whose pipe closes ends by itself. The suite checks all
  three against the operating system's own answer about the process
  ids, not the parent's bookkeeping.

`velaris.PoolRegistry` keeps one pool per distinct budget and makes
each the first time that budget is asked for - what a server needs,
since it learns the budget from the request. The MCP server and the
HTTP door each keep one and close it on shutdown; a caller who varies
the budget every time cannot make either hold processes without end,
because the registry keeps at most eight pools and closes the least
recently used. The CrewAI and LangChain tools stay on plain `run`: a
crew's tool is not called often enough for a pool to pay for itself,
and one process per call is easier for a reviewer to reason about.

**Memory caps are enforced on Windows.** Windows has no `RLIMIT_AS`.
The equivalent is a job object with `JOB_OBJECT_LIMIT_PROCESS_MEMORY`,
which has to exist before the child does: the child is created
suspended, assigned to the job, and only then resumed, so no
instruction of it runs outside the cap. An allocation past the cap
fails and reaches a Python child as `MemoryError`, which is already
what `_run_bounded` reads as E611. `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`
means closing the handle kills whatever is inside, which is also how a
pool kills a Windows worker. It is `ctypes`; no new dependency. If any
step fails - `CreateJobObject`, `SetInformationJobObject`,
`AssignProcessToJobObject` - the cap is recorded and not enforced,
which is exactly what Windows did before 3.1, rather than the run
failing.

So the platform rule is now: enforced on Linux (`RLIMIT_AS`) and on
Windows (a job object); best-effort on macOS, where the limit is set
and not reliably honoured and the timeout is what stops a runaway.
`velaris.memory_cap_is_enforced()` answers for the machine you are on,
and `check_library.py` asks it rather than reading the platform name,
so the assertion now runs on Windows as well as Linux and skips only
where the mechanism genuinely does not hold. Every place that stated
the old rule was rewritten: EMBEDDING.md, THREAT_MODEL.md,
COMPLIANCE.md, SECURITY.md, the MCP tool description, `run`'s
docstring, `benchmark/README.md` and the header `benchmark/run.py`
writes - the last of which now asks the compiler instead of guessing
from `sys.platform`.

On POSIX the cap moved from a `preexec_fn` in the parent to
`--max-memory-mb` on the child's own command line, which the child
applies before it does anything else. `preexec_fn` is documented as
unsafe when the parent has threads, and the HTTP door has had threads
since 2.54 - a latent hazard, not an observed failure, and it is gone.

**velaris.lock.** `velaris add` already recorded a sha256 in
`velaris.toml`. It now also writes `velaris.lock`: every vendored
library with its source, its sha256 and the version of Velaris that
added it, as JSON, sorted, one library per entry.

    velaris deps --verify      # do the files match the lock?
    velaris add <url> --force  # replace a library with different bytes

`velaris deps --verify` (`velaris verify` is the older spelling of the
same check) fails if a vendored file's hash differs from the lock or a
locked library is not on disk, and says which. A project with no lock
falls back to checking `velaris.toml` and says the lock is missing.
`velaris add` refuses to overwrite a library that is already vendored
when the incoming bytes differ, printing both digests; `--force`
replaces it. A library that does not compile is still not accepted -
and now the file it would have replaced is put back rather than
deleted.

One thing changed underneath: a vendored library is written as the
exact bytes that arrived, in binary, rather than decoded and rewritten
as text. Before 3.1 the same library added on Windows and on Linux
locked two different hashes, because the rewrite translated line
endings - which makes a lockfile useless for the one thing it is for.
The digest is now the digest of what the source published, and the
same everywhere.

**Fixed: an empty budget did not survive the trip to a child process.**
`velaris.run(source, allow=set(), timeout=1)` came back with E000 and
"'''' is not an effect" instead of refusing `io` with E310. The parent
spelled an empty budget as the two characters `''`, which a shell
strips and `subprocess` does not. `Budget.parse` now reads `''` and
`""` as an empty budget. Without a timeout the same call was always
correct, which is why it went unnoticed.

**Fixed: `run` left Python handles behind in a shared process.** It
restored the budget and the program's arguments afterwards and not
`PY_OBJECTS`, so a framework calling `run` in a loop accumulated every
handle every program opened and did not close. It now puts those back
the same way, which is also what a pool worker does between programs.

**The benchmark.** Rerun in full on Windows 11 with Deno 2.9.6 and
Python 3.13: identical verdicts to 3.0 on all 63 programs. Of the 56
dangerous programs Velaris caught 54 - 42 before running, 12 while
running - and missed 2; Deno caught 32 (5 before, 27 during) and
missed 24; plain Python caught 28 (all while running) and missed 28;
none of the three flagged any of the 7 controls. The Windows job
object changed no verdict: in category 8 the interpreter still reaches
the 5-second deadline before 256 MB, and `RESULTS.md` says so rather
than implying the cap did the work. THREAT_MODEL.md had been carrying
the 2.62 figures (60 programs, 53 dangerous, 51 caught) and
COMPLIANCE.md said 60 programs; both now match RESULTS.md, and the
README and docs/index.html carry the table for the first time. Two
other stale counts in the README went with them: `check_sandbox.py` is
24 escape attempts and 10 honest programs, not 11 attempts, and
`check_refusals.py` is 21 wrong programs, not 20.

**The published docs were three versions stale.** `docs/` had last
been rebuilt at 2.60, so the reference page still said the effects were
`io, fs, net, clock, rand, ffi` with no `env`, and the library page
still showed `env_tools.setting` using `io`. Rebuilding for this
release brought the site up to 3.1; the error-code count on the home
page is now read from the generated page rather than typed by hand,
where it had drifted from 49 to 59.

**New suite.** `check_pool.py` - 38 checks, run without the prover
first, as ARCHITECTURE.md rule 7 requires. `check_termination.py`
joined CI at the same time; it had existed since 2.62 and never been
wired in.

## 3.0 - Budgets that name paths, hosts, counts, and secrets
This is a major version because a program that compiled under 2.x can
be refused by 3.0: `env()` is its own effect now, and a function that
called it under `uses io` alone is refused at compile time with exactly
"env() now needs 'uses env'" and the fix. The reason is the sentence
THREAT_MODEL.md had to carry since 2.63 - an `io`-only budget could
read and print every secret in the environment. It cannot now. `io` is
the console: `print`, `read_line`, `args`. `stdlib/env_tools.vel` and
the two examples that read the environment declare `env`.

**The 2.60 module allow-list, extended to every coarse effect.** The
budget grammar (SPEC.md 7.1) narrows `fs` and `net` the way `ffi:math`
narrows `ffi`:

    fs:read:./data  fs:write:./out       one direction, under a path
    net:api.example.com:443              one host and port
    net:*.example.com                    one label in place of the star
    fs:read:./data@50  net:...@100       at most that many operations

Every path is resolved with `realpath` when the budget is parsed and
again at every `read_file`, `write_file` and `file_exists`, then
compared as a prefix, so `..` and symlinks cannot reach past a grant
(E313, naming the path). `fetch`, `post`, `fetch_status` and `request`
check the URL's host and port before any connection (E314); a
wildcard matches exactly one label and never the domain itself, and
no wildcard may stand over an IP literal. A count is the smallest
given for that effect and applies to the whole run (E315); a budget
with no count is a budget on what, not on how much. Every one of
these refusals is uncatchable, like E310 and E311. The one catchable
case is a redirect whose target lies outside the `net:` grants: the
program asked for one host and was sent to another, so the request
fails with the target named and the program hears why.

The grammar travels unchanged through `--allow`, `velaris.run(allow=)`,
the bounded child (which receives the budget re-spelled with absolute
paths), the MCP server, the HTTP door, the CrewAI and LangChain tools
and the Jupyter magic. The door's `--max-allow` takes it too, and a
caller may not ask for more than the server grants at any level - an
effect, a module, a wider path prefix, a host the server does not
name, a port, a larger count, or an unscoped `fs` or `net` against a
scoped ceiling - and is told which. The audit reads the paths and
hosts a program names in literals (`fs_paths`, `net_hosts`, added
within `velaris.audit/1`) and its `safe_command` grants exactly those,
falling back to `fs:read` or `net` where a value is built at runtime.

Stated as outside the rule rather than claimed: a hard link inside a
granted directory is that directory's content; a file system changed
by another process between the check and the open is outside the
model, and a Velaris program has no threads to race itself; where a
granted host name resolves is DNS's business.

**Tested.** `check_sandbox.py` gained twelve cases: a read outside the
prefix, a write with only read granted, a `..` escape, a symlink
escape (POSIX; skipped on Windows), a host not in the list, a wildcard
that must not match its parent domain, a port not in the list, a
redirect to an ungranted host against a local server, the count
reached on fs and on net, `env()` with only io granted, and an honest
program using exactly its grants that must run - plus a redirect to a
granted host that must be followed. `check_library.py` has the same
through `velaris.run` and through the HTTP door with a ceiling
narrower than the request at each level. `check_fallible.py` has the
redirect failure as a recipe. The benchmark gained category 11 - a
read outside the granted directory, a request to an ungranted host, a
secret read through `env` - run under the narrowest budget each task
needs, with Deno given the matching `--allow-read=<dir>` and
`--allow-net=<host:port>`; Velaris refuses all three (the path and the
URL arrive on stdin, so the first two are refused while running, and
the third is flagged before), Deno refuses all three at the call, and
Python, with no budget, does all three. THREAT_MODEL.md moves "io
includes env", "fs has no path list" and "net has no host list" from
the non-defences to the defences, each with its suite.

## 2.63.1 - The memory cap claim, narrowed to where it holds
The tests workflow had failed on every macos-latest leg since 2.62, in
`check_library.py`: "a memory cap STOPS a program that eats memory".
The cap is `RLIMIT_AS`, and macOS treats that limit as best-effort -
the doubling program ran to the 60 second timeout (E610) instead of
being stopped at 150 MB (E611). Linux honours the limit; Windows has
no equivalent and was already skipped. The CrewAI tool's test had been
narrowed to Linux for the same reason.

The assertion now runs on Linux only, unchanged there; macOS prints a
skip line saying why, Windows keeps its skip. Every place that stated
the platform truth says the same thing now - EMBEDDING.md,
THREAT_MODEL.md, COMPLIANCE.md, SECURITY.md, the MCP tool description,
the `run()` docstring (a comment-only change, the only edit to the
compiler), the benchmark README and the header the harness writes:
enforced on Linux, best-effort on macOS, not applied on Windows; the
timeout is enforced everywhere. Neither `check_termination.py` nor the
benchmark harness asserts a memory-cap outcome, so nothing else
needed narrowing.

## 2.63 - What a security reviewer looks for
Nothing in the compiler changed. Six pieces for the person who has to
decide whether agent-written Velaris may run on a machine they answer
for.

**THREAT_MODEL.md.** The trust boundary (the operator sets the budget,
the program is untrusted, the compiler and the granted `ffi` modules
are trusted in full), what is defended against with the mechanism and
the suite that tests each, and what is explicitly not: anything a
granted module does, side channels, use below the limits, request
volume within `net`, logic errors with no contract, the meaning of
text, code not written in Velaris, the memory cap on Windows, a
tampered compiler. Two items that were not in any list before: `io`
includes `env()`, so an `io`-only program can read and print the
environment; and `fs` has no path list. Each residual risk has a
recommendation. The benchmark numbers are cited; the misses are named.

**COMPLIANCE.md.** One row per guarantee against the OWASP Top 10 for
LLM Applications (2025) and NIST AI RMF functions - mechanism,
framework item, suite, what it does not cover. Nearly every cell says
"partially addresses", because that is the truth; the items Velaris
does nothing for are listed by name.

**Signed releases with an SBOM.** `release.yml` now signs the wheel and
sdist through sigstore, the three executables and `velaris.mcpb`
through cosign, attaches the bundles, signatures and certificates, adds
a CycloneDX SBOM and SHA256 checksums, builds the wheel twice under
the same `SOURCE_DATE_EPOCH` and fails if they differ, and publishes to
PyPI the same files it signed. Every third-party action is pinned to a
commit with the tag beside it. SECURITY.md says how to verify a
download, with the exact identity string. None of this could be
exercised locally; the v2.63 tag is its first run, and the recap of
this release names what to watch.

**A standing challenge.** SECURITY.md: make Velaris report "proven"
for a promise that is false at runtime, or escape `--allow io`, and
you are credited by name in the changelog and in HALL_OF_FAME.md, with
the report treated as a security issue and fixed within a week. There
is no money. HALL_OF_FAME.md opens with the three model-family reviews
of August 2026 and the review bot of September; the changelog never
recorded which family produced which review, and the file says so
rather than guessing.

**A card eval.** `evals/card_eval.py` gives a model LLM.md and five
fixed tasks - a CSV total, a grade filter with a proven contract, a
sandboxed file read, a JSON path read, a stack calculator using `pop`
and `div_or_fail` - and checks, audits and runs each answer under
`--allow io` with a 10 s timeout, writing compiled-first-try, ran
correctly and proven promises to `evals/RESULTS.md`. It skips with one
line when no key is set, and was not run against any API for this
release; the results file holds only the three August reviews, marked
as reported rather than reproduced.

**PR audit comments.** The GitHub Action gains `pr-comment`: on a pull
request it posts one comment with the audit of every changed `.vel`
file - effects, modules, proven share, safe command, warnings - and
edits that comment on later runs, found by a hidden marker. Plain
`curl` against the REST API with the job's token; no third-party
action. The comment builder was exercised locally against real files,
including one that does not compile; the posting itself was not.

## 2.62 - Loops that provably end, and a corpus built to fool it
The 2.61 benchmark named three programs Velaris could not catch. Two
stay misses, by construction: an off-by-one that stops early instead of
reading past the end (no contract, so nothing to refuse), and a program
that prints `rm -rf build` for its caller (the only effect is io, and a
harmless warning prints the same words). The third - a loop that ends,
slowly - is now shown to end before the program runs.

**Termination.** Every loop gets one of two verdicts, by a syntactic
rule that needs no solver and so answers the same with and without the
prover. `terminates` is claimed for exactly one shape: the condition
is, or has as an `and` conjunct, `v < E`, `v <= E`, `v > E` or `v >= E`,
where E mentions nothing the body assigns and calls only pure
functions, and every path through the body moves v by exactly one step
toward E, with v assigned nowhere else. Everything else - a step of two,
a step on one arm only, a counter reset on some path, a limit the body
grows, a flag-only condition, an `or` - is `unshown`, whether or not it
happens to end. A `for` loop goes through the same rule rather than
being exempted: `for i in 0 to length(xs)` with a push inside does not
end, and the rule says so. SPEC.md section 9.5 states it.

It surfaces in three places. `velaris explain` prints "loops: 2
terminate, 1 not shown" per function. `velaris audit` and
`velaris.audit()` gain `loops_unshown` per function and a warning
naming the functions, in schema velaris.audit/1 (added fields, not a
change); they also gain `contract_coverage`, the functions that take or
return a List, a Map or a record and promise nothing about it - a
coverage note, not a defect. `velaris check --strict` refuses a loop
whose end is not shown with E612; without `--strict` it is not an
error, and the time limit in `velaris.run` remains the guard.

**Stressed before trusted.** `check_termination.py` holds 44
adversarial loops with their required verdicts: the wrong direction, a
step of two, a step spelled `1 + i`, a reset on one path, a limit the
body changes, a limit changed only inside a nested if, `length(xs)`
with a push inside, nested loops where only the inner qualifies, a flag
alone, a flag with `or`, a float counter, the step inside a `check` on
both arms and on one, a return with and without a step, recursion
instead of a loop. The analysis was wrong twice on the first attempt,
both times in the same direction - refusing a loop that ends: it
counted the standard library's loops when a program imported it (a
scoping error in the report, fixed by carrying the file), and it did
not accept a text literal or a pure builtin such as `split` inside a
limit, so `for part in split(line, " ")` was `unshown` and a control
program in the benchmark was a false positive. Both are fixed in the
analysis, not the tests. No existing example changed proof status
(`velaris proofs examples --json` before and after, diffed).
`examples/termination.vel` and `examples/termination_bad.vel` join the
suite; the latter runs and is refused only by `--strict`.

**The benchmark, doubled.** Sixty programs now, thirty of them written
against the tools: effects three helpers deep or inside a record, a
division guarded on one path and not the other, an off-by-one only on
empty input, an overflow inside a record field and inside a map, a
failure ignored inside an inline function, a loop that ends only when
input says so, growth by repeated text concatenation, subprocess
reached through the JSON-shaped call and through a handle, and control
programs that look suspicious - printing "rm -rf", reading their own
arguments, importing math in a loop - and are harmless. Same three
languages, same rules. On the machine that produced RESULTS.md
(Windows, prover present, Deno 2.9.6): of 53 dangerous programs
Velaris caught 51 - 41 before running, 10 while running - and missed
the two above; Deno caught 29 (5 before, by its lint on a `while
(true)`) and Python 28; no tool flagged any of the 7 control programs,
the slow loop among them. Ten consecutive runs produce identical
output. What the doubling found: the prover does not flag a division on
an unguarded path when another path guards it, a remainder inside a
loop, or a `get(xs, i + 1)` - all three are caught while running, not
before, and the table says so.

**args().** Under `--allow io` the program's `args()` used to contain
`--allow` and `io`. It no longer contains `--allow`, `--deny`,
`--timeout` or their values, from the command line or from
`velaris.run`; `check_sandbox.py` has the case.

## 2.61 - A table anyone can rerun
Every claim this project makes about catching what a model writes has
been a claim. `benchmark/` turns it into a table that one command
regenerates: `python benchmark/run.py`. Thirty programs in ten
categories - a file write hidden in a helper, a network call hidden in
a helper, division by input, an off-by-one read, integer overflow, an
ignored failure, an infinite loop, runaway memory, reaching subprocess
or os.system, and three correct programs that must not be flagged -
each written three times with the same behaviour, in Velaris, in
JavaScript for Deno and in plain Python. The harness runs every program
through `check` + `audit` + `run` under the budget the task needs (io,
plus `ffi:math` for one control program, with timeout 5 and
max_memory_mb 256), through `deno run --no-prompt` with no flags, and
through a Python subprocess with the same timeout, and records
caught-before-run, caught-during-run, missed, not-applicable,
false-positive or tool-absent, with the evidence in the cell.

On the machine that produced the committed RESULTS.md (Windows, prover
present, Deno 2.9.6): of 27 dangerous programs Velaris caught 24 - 15
before running and 9 while running - and missed 3; Deno caught 13 and
Python 13; no tool flagged a control program. The three misses are in
the corpus on purpose and are named in the results: an off-by-one that
stops early instead of reading past the end (no contract, so nothing
to refuse), a slow but finite loop (ends before the deadline), and a
program that prints `rm -rf build` for its caller (the only effect is
io). Deno's `no-unreachable` lint flags the three memory-growth
programs before running, where Velaris only stops them while running;
and on Windows it stops them with the timeout, not the memory cap,
because the cap is not enforced there and the interpreter allocates
slowly. Both are in the table.

Two things learned while building it. Under `--allow`, `args()` hands
the budget words to the program as well (`['--allow', 'io', ...]`), so
the corpus reads its input from stdin; that is a compiler bug to fix in
its own release, not here. And a Deno permission denial is an ordinary
exception, so a `fetch` inside `try/catch` exits 0 - the harness had to
watch the socket rather than trust the exit status. A Velaris refusal
cannot be caught by the program, which is the difference the benchmark
exists to show.

`benchmark/README.md` has the rules and the exact commands so a
stranger can rerun it and dispute a row. CI runs `run.py --quick
--check` on the legs with the prover, with Deno absent there; a verdict
that changes between compiler versions fails the build and names the
row.

## 2.60 - The ffi cliff becomes a permission
Every review of this project, from three model families and one
automated reviewer, raised the same caveat: `allow ffi` grants
everything Python can do. That was true, and it was the sentence a
security reviewer would stop reading at.

The budget can now name modules. `--allow io,ffi:math,json` grants the
ffi effect for those top-level packages only; anything else is refused
with E311, and the message names the exact flag that would permit it.
Plain `ffi` still grants every module, for programs whose author you
trust. The library takes the same form: `run(source, allow={"io",
"ffi:math"})`, and `refused_effect` reports `"ffi:os"` when that is
what was reached for.

The audit reads the modules a program names in its py* calls and
reports them as `ffi_modules`; its `safe_command` grants exactly those.
A reviewer no longer has to choose between "no Python" and "all of
Python".

Four ways around it were tried and refused, in `check_sandbox.py`: a
module outside the list, a submodule path (`os.path`), the same module
through `py_json`, and through a handle via `py_new`. All three FFI
import sites go through one gate, and the bounded child process
receives the same list. An allowed module still works.

## 2.59 - Time and memory limits, prompted by a review bot
The CrewAI pull request's automated reviewer flagged what three human
reviews had also noted and this project kept deferring: the effect
budget bounds what a program may touch, but nothing bounded how long
it could run or how much memory it could take. For an agent framework
calling `run` in a loop, that is the first thing that goes wrong.

`velaris.run(source, allow={"io"}, timeout=30, max_memory_mb=512)`.
With either limit set the program runs in a separate, killable
process. A program that never ends is stopped at the deadline (E610,
`timed_out=True`); one that eats memory is stopped at the cap (E611,
`out_of_memory=True`, caught in 0.4 seconds in the test). The effect
budget still holds inside that child - verified - and an honest program
is unaffected.

Memory caps use the OS address-space limit, so they apply on Linux and
macOS; on Windows the timeout applies and the cap is recorded but not
enforced, which the docs say plainly rather than implying otherwise.

The MCP server and the HTTP door now default to 30 seconds and 512 MB.
The CrewAI tool does too, reports STOPPED with the limit it hit, and
gained the assertion the reviewer asked for: a refused effect must not
reach the program's own fail branch either.

Attribution, added in 3.2 from the public record: the reviewer was
CodeRabbit (`coderabbitai[bot]`), on
[crewAIInc/crewAI#7279](https://github.com/crewAIInc/crewAI/pull/7279)
at 2026-09-05 06:56 UTC, under the heading "Denial of Service (CWE-400):
Uncontrolled Resource Consumption"; the fail-branch assertion answers a
second finding in the same review.

## 2.58 - Ready to submit to the frameworks
Three integrations in `integrations/`, each written to the target's
own conventions and each with tests that assert the effect budget
holds through the framework's tool interface - because a budget that
leaks one layer up would be the worst kind of promise.

**CrewAI** (`crewai/`): `VelarisAuditTool` and `VelarisRunTool(allow=
["io"])`, five tests, a README, and the pull-request text ready to
paste. `crewai-tools` accepts community tools; this goes first.

**LangChain** (`langchain_velaris/`): a partner package,
`langchain-velaris`, since LangChain lists packages rather than
merging tools. Verified through `.invoke()` that a program granted
only `io` is refused `fs`.

**MCP registry** (`mcp_registry/`): the `server.json` for
registry.modelcontextprotocol.io, which every MCP client reads. A form
rather than a PR, and the highest reach of the three.

`integrations/README.md` says what to submit, where, in what order,
and what makes a maintainer say yes: a test that runs in their CI, a
description of the problem rather than the product, no marketing
words, and fast replies to review.

## 2.57 - --strict, from a question on r/Compilers
Someone asked whether users could choose between strict and flexible
proof modes rather than having leniency imposed on them. They were
right, and half the answer already existed - `velaris proofs --min 80`
holds a line across a project - but the compiler itself always
accepted a promise that fell back to a runtime check.

`velaris check program.vel --strict` refuses when any promise could not
be proven, and names them:

    examples/wordcount.vel: 2 promise(s) could not be proven, and
    --strict does not accept runtime checks:
      bar
          needs    biggest > 0
      report
          needs    top > 0

With no prover installed it refuses rather than pretending - a strict
check that silently proves nothing would be the worst of both.

The default stays lenient because the solver is optional and
strict-by-default would mean the language does not run for anyone who
has not installed z3. That is an argument about the default, not a
reason the flag should not exist.

## 2.56 - Seamless means tested, not claimed
Three gaps between "the door exists" and "the door works".

**The Jupyter magic was never installed.** `velaris_magic.py` was not
in the wheel, so `%load_ext velaris_magic` worked in the repository and
failed for everyone who installed from PyPI. Found by checking from
outside the repo rather than inside it - the difference between a door
that opens and a door that appears to.

**One shape for problems.** `audit()` returned dicts while `check()`
and `run()` returned objects, so callers - including this project's own
Jupyter magic - had to handle both. Now everything returns `Problem`
objects and `as_dict()` flattens them for JSON. The magic got simpler
by six lines, which is what an API fix should look like.

**The version guard covers every version.** It watched velaris.py,
pyproject.toml and the VS Code extension, but not the npm package or
the .mcpb manifest - either could have shipped claiming a version the
compiler never had. Both are guarded now.

`check_library.py` grew a section that asserts every door works after
a real install: all four modules importable, both APIs reporting the
same shape, the npm version following the compiler, the hooks present.
39 checks with the prover, 38 without, and rule 6 was followed - the
no-prover run happened before this was written down.

## 2.55 - Four more doors
Velaris was reachable from a terminal, Python, MCP, CI, Docker and
HTTP. Four populations were still locked out.

**npm.** `npx velaris-lang script.vel --allow io`, plus a real library
with TypeScript types: `audit(source)` and `run(source, {allow:
["io"]})` from Node. Verified through Node that a program granted only
`io` is still refused `fs` - the same guarantee, one process further
away. The compiler stays a Python package; the wrapper says so plainly
when it is missing instead of failing with a spawn error.

**Jupyter.** `%%velaris --audit --allow io` runs a cell in a box and
prints what it can touch and how much is proven first. When an effect
is refused it names the flag that would permit it. The natural home for
the finance and measurement work where proven contracts earn their
keep.

**pre-commit.** Three hooks - `velaris-check`, `velaris-fmt`,
`velaris-proofs` - so a repository can require that its Velaris
compiles, is formatted, and keeps its proven share above a threshold.

**Homebrew and winget** manifests in `packaging/`, both with tests
that assert the effect budget still holds in a packaged build. They
need a tap and a pull request respectively, which is paperwork rather
than code, and the files say exactly what to do.

Building the Jupyter magic surfaced a wart in the library: `audit()`
returns problems as dicts while `run()` returns them as objects. The
magic handles both; the API should not need it, and that is worth
straightening when the format version next moves.

## 2.54 - A door for languages that are not Python
Velaris was reachable from a terminal, from Python, from an MCP client
and from CI. Everything else - a Node service, a Go tool, a Rust
agent, a shell script - was locked out.

`velaris serve` opens a local HTTP door with the same three calls:
`POST /check`, `POST /audit`, `POST /run`, plus `GET /card` and
`GET /health`. Same library underneath, so the same guarantees.

**Two ceilings, both enforced.** The `allow` in a request is the
program's budget. `--max-allow` is the server's own limit - a caller
asking for `ffi` on a server started with `--max-allow io,fs` gets 403
and is told what it does grant. Verified both ways in
`check_library.py`, which now drives a real server on a real port.

It binds to localhost unless told otherwise, warns when it is not, and
warns when `ffi` is grantable - because this endpoint runs programs and
that should be said out loud rather than buried.

`ARCHITECTURE.md` gained a table of what each suite is for, and a
sixth rule: run every new suite without the prover BEFORE wiring it
into CI. That mistake has now been made three times; this release is
the first where the rule was followed rather than learned again.

## 2.53.1 - The library suite knows what needs the prover
Three of the 25 checks in `check_library.py` are about proofs - what
was proven, a refuted promise, a 100% proven share - and the no-solver
CI legs have no prover, so every minimal leg failed the moment the
suite joined CI. The same mistake as 2.39.1, in a new suite.

They are now conditional, and without the prover the suite asserts the
**fallback** instead: that a false promise breaks while running (E600
or E601) and that the audit reports nothing proven. That is a stronger
test than skipping, because it checks the degraded path rather than
ignoring it.

25 with the prover, 24 with the fallback. Both green.

## 2.53 - Setting it up should not be a chore
The MCP server worked; getting it into an assistant meant finding a
Python path and editing JSON. Two ways to skip that.

**`velaris mcp-install`** finds every MCP client on the machine -
Claude Code, Cline, Cursor, Windsurf, Continue, Zed - and adds a
`velaris` server to each, using the Python that is running it. It
never disturbs what is already there: tested against a config holding
another server with its own env block and an unrelated top-level key,
both of which survived, and every file is backed up before writing.
`--list` shows what it found without touching anything, `--remove`
undoes it.

**`velaris.mcpb`** is the double-click bundle, 94 KB, with the
compiler and standard library inside it - newer Claude Desktop builds
only accept remote connectors in the add-connector dialog, so a local
server has to arrive as a bundle. Verified by extracting it somewhere
with no Velaris installed, driving it as a client would, and watching
the sandbox still refuse `fs` to a program granted only `io`. It is
built and attached to every release automatically.

The bundled server now finds the compiler whether it was pip-installed,
vendored beside it, or sitting in the repo next door - a user's own
install still wins.

## 2.52 - Velaris from inside other programs
The effect budget is the idea most easily copied out of this project.
The way to make copying pointless is to make importing cheaper - so
Velaris is now a library, a documented format, and an MCP server, as
well as a command.

**The library.** `velaris.check(source)`, `velaris.audit(source)`,
`velaris.run(source, allow={"io"})` and `velaris.card()`. `run`
captures stdout and stderr, accepts stdin and args, reports which
effect was refused, and restores the previous budget afterwards so a
process can audit and run many programs. The guarantee is identical to
the command line: a refused effect stops the program and cannot be
caught by it.

**A versioned format.** `audit().as_dict()` is `velaris.audit/1`:
effects, per-function contracts with proven-or-runtime status, the
proven share, the safe command, and warnings - including that ffi
cannot be contained by a budget. Documented field by field in
EMBEDDING.md, with a stated compatibility rule. Formats outlive the
tools that produce them.

**An MCP server.** `velaris_mcp.py` offers `velaris_card`,
`velaris_check`, `velaris_audit` and `velaris_run` over the Model
Context Protocol, so an assistant can write Velaris, check it, see
what it touches and run it in a box without leaving the conversation.
`velaris_run` defaults to `allow: ["io"]` - the least that is useful.

**`check_library.py`** proves the library and the server keep the same
promises as the command: 25 checks, including that a program refused
`fs` does not carry on, that budgets are restored between runs, and
that a refusal through MCP is reported as such. In CI on every push.

## 2.51 - Smaller per-call costs, and an honest note about the ceiling
Two more measured savings on the interpreted path, both verified
against every suite and the fuzzer.

The evaluator and statement runner compared node types with
`isinstance`, which walks a class hierarchy; the AST dataclasses have
no subclasses, so 22 of those became pointer comparisons. And a
function with no `requires` or `ensures` was copying its entire scope
on every call to snapshot values for promises it does not have.

Interpreted record work is now 1073ms where it was 1314ms at the start
of this run - about 18% - on top of startup halving in 2.48.

**The honest ceiling**: the remaining cost is the sheer number of
evaluator calls, roughly 580,000 for that benchmark. Removing it needs
the AST compiled to closures or bytecode, which is a rewrite of the
execution core rather than an optimisation of it. Native compilation
for records has the same character - it is the LLVM struct ABI work
that already caused a Windows-only bug once. Both are worth doing and
neither is worth starting at the end of a long session; they need a
plan, a branch, and the fuzzer running between every step.

## 2.50 - Function values carry their surroundings
Two reviewing models named the no-capture rule as a real expressiveness
cost, and they were right: writing `fn(n: Int) -> Bool { return n >
limit }` meant hand-writing a loop instead. Inline functions now
capture **by value**.

The values are copied when the function value is made, so later
assignment to those locals cannot change what the function sees -
`examples/lambda_capture.vel` demonstrates a captured `cutoff` staying
2 after the local is set to 99. There are no reference cells, so a
function value can never observe a change it was not handed.

What did not change, verified: a capturing inline function that tries
to print is still rejected (E300 - effects cannot be smuggled past a
signature); a false promise on one is still caught while running
(E601); a name that exists nowhere is still E402. The prover treats
captured values as unknown, which is the conservative direction.

`examples/lambda_bad.vel` was the test asserting capture is an error.
It is now `examples/lambda_capture.vel` and asserts the opposite - the
right way for a language to record a change of mind.

## 2.49 - The card's gaps were hiding three real bugs
A model reviewed `LLM.md` without a compiler and reported five things
the card never explained. Writing them down meant testing them first,
and three turned out to be defects rather than omissions.

**Deep recursion crashed.** Past about 300 frames a program died with a
Python `RecursionError` traceback. Velaris now stops at 2000 frames
with E609 and says the recursion looks like it never ends - and
Python's own ceiling is lifted so that ours is the one that fires.

**`write_file` crashed on any OS failure.** An unwritable path threw a
raw traceback. It is now E608 with the reason from the operating
system. It stays non-catchable by design - a program that cannot write
where it was told to should stop - but it stops as a Velaris error.

**A dead `write_file` branch** sat unreachable in the interpreter,
left from an earlier edit.

**Two card claims were simply wrong.** Recursion works, carries
contracts, and is checked at call sites - the card never mentioned it,
so a reviewing model refused to use it. And `invariant` works on `for`
loops as well as `while`; the card documented only `while`.
`examples/recursion.vel` proves three contracts across both.

**Handle lifecycle, tested and written down**: double close is a
no-op, use after close fails catchably, handles copy by reference.

**Full module signatures** for http, db, dates, csv, log and
env_tools - every parameter type, every return type, which functions
can fail, which carry proven contracts. Guessing these was the
commonest source of wasted attempts for a model with no compiler.

## 2.48 - Speed, without touching a single guarantee
Three measured wins, none of which changes what the language promises.

**Startup halved: 133ms to 67ms.** Every run - including every hello
world - was importing z3 (about 350ms of the cold cost) whether or not
anything needed proving. The prover is now located rather than
imported at startup, and `check_proofs` returns immediately when no
function carries a contract, no division or list read creates an
obligation, and no callee has a promise to satisfy. Programs that do
need proofs pay exactly what they paid before; the counterexamples in
avg_bad, offbyone_bad and conj_bad still appear.

**Interpreted work is faster.** `sorted()` was running on every single
builtin call to check the effect budget - now precomputed once.
`length`, `get` and `push` sat behind thirty string comparisons and two
module imports - now first, with the bounds guard intact. The
evaluator and statement runner dispatch the hottest node classes
directly instead of walking an isinstance chain: 5.8 million isinstance
calls became 3.8 million on a record-heavy benchmark, and that
benchmark went from 1314ms to 1139ms.

**Measured, not claimed:** a 3-million-iteration loop on the native
path runs in about 80ms against Python's 445ms for the same loop. The
fuzzer confirms both engines still agree exactly on 30 random
programs, and all 89 examples, 25 fallible builtins, 15 sandbox cases
and both stress suites pass unchanged.

## 2.47 - The periphery round
A third adversarial pass executed everything the card mentions - every
builtin, all seven modules against live systems, every error code -
and held the score at 88 while finding the roughness had moved from
the core to the edges. All five findings, fixed:

**Division joins the catchable family.** A zero divisor from user
input was the one remaining way to kill a checked program: E403 stops
the process and no `check` sees it. `div_or_fail` and `mod_or_fail`
fail the normal way, for exactly the input-driven case; plain `/` and
`%` stay strict for divisors the code controls. The card says which to
use when.

**The http envelope is a record.** `call` returned Text and `get`
returned Text, so feeding a raw body to `code_of` compiled and died at
runtime with a misleading JSON error. `call` now returns an `Answer`
record (status, body, raw); `code_of` and `body_of` read fields and
cannot fail; the wrong pairing is a type error. `linkcheck` got
simpler for it. Writing this found a genuine language subtlety: a
local named `status` shadowed the module's `status` *function* and
produced a confusing E530 - renamed, and worth remembering.

**`log.die` says what it does.** `fail_with` logged and killed the
process - correct behaviour, wrong name in a language where "fail"
means catchable. `die` is the new name; `fail_with` remains as an
alias so nothing breaks.

**`velaris check` treats a library as a library.** Requiring `main` at
check time (v2.44) was too broad: `velaris check stdlib/http.vel` is a
legitimate thing to do. A missing main is now only an error for the
file being run - which the runtime already enforced.

**The card grew the last empirical truths**: E525 (binding a
void-returning fallible call), sort_by keys are Int, the _or_fail
guidance, the Answer record, and log.die's semantics.

Attribution, added in 3.2 from the maintainer's account: the third pass
was by the Claude model whose review is 2.44.

## 2.46 - Contents, not just lengths
Two additions, both from the adversarial rubric's remaining points.

**`map_to(xs, f)`** - projection that changes type, `fn(T) -> R`, so a
record becomes one of its fields in one call instead of a hand-written
loop. The generics system supported two type variables all along;
nobody had written the function. Its `ensures length(result) ==
length(xs)` proves.

**Quantified contents prove through loops.** `ensures all_of(result,
is_positive)` on a filtering loop was runtime-only; now the inference
harvests each all_of predicate from the function's own ensures and
tries "everything pushed so far satisfies it" as an invariant. Entry
is vacuous, each push must satisfy it on its path, and the promise
follows. The unguarded version correctly does NOT prove - the
candidate is dropped when a step can break it - and the runtime check
catches it with the actual offending list. Sound in both directions,
and the suite's wall time did not move.

Attribution, added in 3.2 from the maintainer's account: the rubric is
that of the Claude model's review in 2.44.

## 2.45 - The road from 84
Three of the four items that separate this language from the low 90s,
by its own adversarial grading.

**The v2.42 mistake cannot recur.** `check_fallible.py` reads
FALLIBLE_BUILTINS from the compiler itself, generates an
ignore-the-failure program for every member, and asserts each is
refused with E520 - then a caught-failure program for each, asserting
the failure formats and never escapes as a traceback. 23 builtins, all
enforced, in CI on every push. A fallible builtin added without
enforcement now fails the build by construction.

**The prover reads record fields through lists.** A `List of Row` is
modelled as one Int array per provable field, so
`get(rows, i).amount` is a real array read: the off-by-one over a
record list - the adversarial report's exact deferral - is refused
before running (E705), and `ensures result >= 0` on a total over
record amounts is **proven**, which was flatly impossible before.
Building this introduced a truthiness bug on a Z3 array (`or` on an
array is not a None-check) that silently un-refuted a v2.38 regression
test; the refusal harness caught it within the same session, which is
the layered suites doing exactly their job.

**The break question has an answer in writing.** SPEC.md §13a: no
`break`, because the prover's exit knowledge - "the condition is
false" - is what pins counters at boundaries and proves loop promises;
a break turns that into a disjunction over hidden paths and abandons
most loop proofs. The supported idiom is the exit in the loop test
(`while i < n and not found`), which the prover can see, and the card
now teaches it with the reasoning. The decision names the condition
under which it would be revisited.

The fourth item is not code: another adversarial round, finding less.

Attribution, added in 3.2 from the maintainer's account: the grading is
the second pass of the Claude model's review in 2.44.

## 2.44 - Everything the adversarial report found
A model ran 86 adversarial artifacts against 2.43 - one production
program, 34 broken fragments, 52 single-point mutations - and scored
the language 76/100 with a list of defects. All of them are fixed.

**The soundness hole (critical).** `pop`, `slice` and `set_at` were
documented fallible but the checker never demanded handling, so a
clean `velaris check` could be followed by a raw Python traceback at
runtime. The list-operations type check returned before the
fallibility check ran. They now require `check` or `try` like every
other fallible call (E520).

**The checker cannot crash.** An unknown parameter type escaped as a
Python traceback instead of E500, breaking `--json` consumers and any
automated fix loop. Every checker pass now reports instead of raising.

**`main` is validated at check time.** No `main` at all (E400), a
`main` with parameters (E401), and a `main` marked `or fail` (E523,
new) are all compile-time findings now, not runtime surprises.

**The typed FFI carries numbers.** `py_float("math", "sqrt", ["16"])`
sent Python the string "16" and failed. Arguments that read as numbers
are now passed as numbers, with an all-strings retry so functions
genuinely wanting text still get it.

**Conjunctions stop masking.** `requires divisor > 0 and
length(items) > 0` over a record list dropped the WHOLE clause when
one conjunct could not translate - the checkable `divisor > 0`
included. Conjunctions are now split and each part checked on its own,
and record lists carry a modelled length even where their contents
cannot be seen. The report's exact shape is rejected at the call site
with a counterexample.

**The card grew fifteen truths** the reviewer had to discover by
experiment: `%` exists, `random(n)` is 0..n-1, `random(0)` is E405,
record fields go one per line, oversized literals are accepted but
arithmetic is checked, unused effects are viral, `time` needs ffi and
can fail, `apply_to_each` maps T to T only, the `--allow`/`--deny`
budget flags, `velaris proofs --detail`, and codes E400 E405 E509 E513
E521 E523 E542 E602 E704 - plus the E506/E507 correction (E507 is
about duplicate records, not empty maps).

Attribution, added in 3.2 from the maintainer's account: the reviewing
model was a Claude model, and the same review's later passes are behind
2.45, 2.46 and 2.47.

## 2.43 - The prover crosses the loop boundary
The sharpest finding in the last review was that the prover went blind
the moment a loop touched a list: a promise like
`ensures length(result) == length(xs) - 1` would not prove even with a
hand-written invariant, and the textbook off-by-one
`while i <= length(xs) { get(xs, i) }` was caught only at runtime. Both
are fixed.

**Two invariants were missing.** A counter walking toward a limit stops
*at* the limit - without that, the state after a loop only says
`i >= limit`, so "the loop ran exactly that many times" could never
follow. And a list built one item per turn has exactly as many items as
the counter has turns. Both are inferred automatically now; the
promises in `examples/loop_lists.vel` prove with no invariant written
at all. The proven share across the examples went from 60% to 64%.

**The off-by-one is refused before running.** Reporting a bug about a
loop's index used to be unsound, because the index inside a loop stands
for *any* state the invariants allow. The sound route is the loop's
**last real turn**: a counter that starts inside the limit and steps by
exactly one takes every value up to the largest the condition allows,
so that turn genuinely happens and a read on it is a genuine read.
`examples/offbyone_bad.vel` is rejected with the position and the
length. Correct loops - `i < length(xs)`, guarded reads, and counting
backwards - are unaffected, which was checked before anything shipped.

## 2.42 - Findings from a model that installed it and tried to break it
A third model read `velaris card`, installed the language, wrote a
30-function calculator that compiled and ran correctly first try, then
spent its time attacking it. Nearly everything it reported was true.

**Lists can shrink.** `pop`, `slice` and `set_at`, all fallible, all
returning new lists. A stack machine - the natural shape for a
calculator - previously required rebuilding the whole list one element
shorter for every pop. `examples/stack.vel` is that program.

**Overflow can be caught.** `a * b` that outgrows 64 bits is still
E407, which stops the program and no `check` can catch - correct for a
bug, wrong when the numbers come from a user. `add_or_fail`,
`sub_or_fail` and `mul_or_fail` fail in the normal way instead.

**`break` says something true.** It used to report "unknown variable
'break'" and suggest declaring one. It now says the language has no
`break`, and suggests keeping a flag.

**The formatter matches the documentation.** `requires`, `ensures` and
`invariant` were being flattened to the margin, contradicting the style
in Velaris's own docs. Every shipped file is reformatted.

**The card states the ceiling.** The sharpest finding was that the
prover goes blind when a loop mutates a list: `ensures length(result)
== length(xs) - 1` will not prove even with an invariant, and
`while i <= length(xs) { get(xs, i) }` is caught at runtime rather than
before. That limit is real and unfixed; `LLM.md` now says so, along
with the overflow rule and the absence of `break`.

Left as-is, deliberately: the ffi escape hatch is total, and
`velaris audit` already says so unprompted - which the model noted
approvingly.

Attribution, added in 3.2 from the maintainer's account: the model was
a Claude model.

## 2.41.2 - A loop no longer hides a divide by zero
A second model read `velaris card`, wrote an expense report, then
deliberately removed a `requires length(items) > 0` guard and predicted
the compiler would catch the division. It did not.

The cause: the divide-by-zero proof skipped itself whenever *any*
condition on the path mentioned a value a loop had made unknown. Since
almost every average sums in a loop before dividing, the check was
hiding exactly where it was needed. The divisor itself was perfectly
knowable the whole time.

Now the divisor is judged on its own terms and loop conditions stay in
the solver rather than cancelling the proof - dropping them would have
invented counterexamples, keeping them costs nothing.
`examples/avg_bad.vel` is the shape, rejected before running.

Still runtime-checked: dividing by the length of a list of **records**,
because the prover cannot model those at all. That limit is real and
documented; this release fixes the case where the limit was being
claimed falsely.

Two models, two programs, two real defects found in one evening. The
card is doing what it was built for.

Attribution, added in 3.2 from the maintainer's account: the model was
a ChatGPT model (the one in 2.41.1 was a Gemini model).

## 2.41.1 - The card worked, and the first program it produced found a bug
Pasting `velaris card` into a model that had never heard of Velaris
produced a correct program on the first attempt - and that program
crashed the prover. Pushing a **record** onto a list inside a `check`
inside a loop reached a comparison that assumed every value has a Z3
sort. Records do not. The rule was already right (a list of records
cannot be modelled, so abandon the proof and let the runtime check);
the translator simply asked the question in a way that crashed instead
of answering it.

`examples/rec_push.vel` is that program, kept as a regression test.

Worth recording plainly: the card's first user found a real defect
within minutes, which is exactly why it was worth building.

Attribution, added in 3.2 from the maintainer's account: the model was
a Gemini model.

## 2.41 - Written by a model, audited by you, run in a box
Three pieces that make one story.

**`velaris card`** prints `LLM.md` - about 1,500 words containing the
whole language, the ten rules models actually get wrong, every builtin
with its effects and whether it can fail, the error table, and a
complete program to imitate. Paste it into any model and it can write
Velaris that compiles. Until now the language's biggest problem with
generated code was that no model had heard of it.

**`velaris audit program.vel`** answers the reviewer's question rather
than the author's: what this program can touch and which functions
reach outside, what it promises and how much of that is **proven**
before running versus checked while running, what can fail, and the
exact command to run it under a budget. When a program calls Python it
says plainly that an effect budget cannot contain that. `--json` for
tooling.

**`agent_loop.py`** writes a program with a model and iterates against
the compiler: `velaris check --json` hands back codes, lines and
numbered fixes, which go straight back to the model, up to six rounds,
then the result is audited. Most agent loops iterate against tests;
this one iterates against a proof, which is a stronger signal - the
compiler does not say "a test failed", it says which input breaks which
promise.

## 2.40.1 - Leading with the sandbox
The README now opens with the thing that matters most in 2026: an AI
wrote you a script, and you can run it anyway because the runtime
refuses whatever you did not allow. The proof story - promises checked
before the program runs - follows immediately after, where it reads as
the reason to believe the first claim rather than competing with it.
New hero image to match, and the limits stated in the same breath as
the feature.

## 2.40 - Running a program you have not read
The compiler has always checked that a function declares what it does.
This is the other half:

    velaris program.vel --allow io          refuse every other effect
    velaris program.vel --deny net,ffi      allow everything but these

The runtime refuses any effect outside the budget granted on the
command line, **whatever the source says about itself**. A refusal is
not a failure the program can catch with `check` - it stops there, so
a program cannot swallow the refusal and carry on.

`check_sandbox.py` proves it holds: eleven escape attempts - reading,
writing, the network, calling Python, opening a database through a
handle, the clock, randomness, hiding the effect behind two layers of
helper, catching the refusal to continue anyway, and both `--deny`
forms - all refused with E310, with a file-existence check confirming
nothing was actually written. Four honest programs still run untouched,
including one with no permissions at all. Needs no prover, so it
behaves identically in every CI configuration.

`examples/sandbox.vel` shows the same thing by hand.

**What this is not**: a security boundary. A program granted `ffi` can
do anything Python can, and nothing here limits memory, time, or what a
program prints. It is a strong guard against accident and casual
misbehaviour - which is the situation you are in when an AI hands you a
script - not a defence against a hostile author you have already
granted permission.

## 2.39.1 - The refusal harness knows what needs the prover
Nine of the twenty refusals in `check_refusals.py` are proof results -
a false promise, a possible divide by zero, an out-of-range read, a
broken invariant. Without z3 installed those programs simply run, so
every no-solver leg in CI failed the moment the harness joined it.
The harness now skips those cases when the prover is absent and says
so, exactly as the example suite already did.

Verified both ways: 20 refused correctly with the prover, 11 refused
and 9 skipped without it.

## 2.39 - The editor asks for what the compiler already knew
The language server has answered hover, completion, go-to-definition,
rename, an outline and proof-status lenses since 2.32 - but the
extension's hand-rolled client only ever listened for errors, so none
of it reached the editor. The client now asks:

- completion for functions in scope with their contracts, and every
  builtin with its effects and whether it can fail
- hover showing a signature with its `requires` and `ensures`
- go to definition, across imported files
- rename across the file
- an outline of the file's functions
- **proof status above every function**, from the real prover

Requests time out after eight seconds and fall back to nothing rather
than hanging the editor.

Plus 17 snippets for the shapes this language actually uses: `fnp` for
a function with promises, `fnfail` for one that can fail, `check` for
handling both outcomes, `whileinv` for a loop with an invariant,
`record`, `test`, `json`, `py`, `importas` and more.

## 2.38 - Testing the places languages break
Two new suites, because a test that only checks correct code passing
is half a test.

`examples/edges.vel` covers boundaries, properties and round trips:
empty and single-element lists, empty text, empty maps, negatives,
zero, division rounding toward minus infinity, the 64-bit limits, and
empty ranges - then **195 generated cases** asserting properties rather
than examples (sort always returns a sorted list of the same length
containing the same elements; reversing twice is the original; the
maximum is always a member; filtering never keeps what it should not),
and round trips that must come back unchanged (28 dates parsed and
printed, JSON built and read, a CSV row written and read, join then
split, upper then lower). 20 checks, all passing.

`check_refusals.py` is stricter than the example suite: it asserts that
each of **20 wrong programs is refused with the specific error the
language promises**, not merely refused. A false promise must be E700,
an undeclared effect E300, an ignored failure E520, a possible divide
by zero E706, an out-of-range read E705, a broken loop invariant E703,
and so on - so a guarantee cannot quietly degrade into a different
guarantee. Both run in CI on every push.

## 2.37 - A stress test written in Velaris
`examples/stress.vel` exercises the whole language and standard library
in one command that asks nothing and exits non-zero if anything fails:
contracts and proofs, inferred loop invariants, division proofs,
records with list fields, map proofs, nested lists, generics, function
values inline and by name, text case and containment, native list and
text scanning, failure through `try` and `check`, JSON reading and
building, dates, CSV, the host language including a real SQLite handle,
the environment, the clock, and a network request that reports itself
as skipped when offline.

33 checks. Two failed on the first run and both were the test's
arithmetic being wrong rather than the language - which is the right
way round, and is why the corrected expectations are in the file.

## 2.36.4 - The Action has its own name
GitHub's Marketplace requires an Action's name to be globally unique,
and "Velaris" was taken. The Action is now "Velaris Language Check",
which describes what it does anyway. Nothing else changed - the way
you use it is identical.

## 2.36.3 - A picture of the point
The README now opens with an image of the compiler refuting a promise
and handing back the input that breaks it. People decide in a few
seconds whether to keep reading, and the most convincing thing about
this language was previously three scrolls down.

## 2.36.2 - Somewhere to start
The README points at the open `good first issue` list and spells out
the four commands a change has to pass before it ships. The tasks
themselves are now issues rather than a paragraph in a file nobody
opens.

## 2.36.1 - Two-part tags publish the extension again
Tags here are two-part (`v2.36`) but npm requires three
(`2.36.0`), so the extension publish failed with
`Invalid version: 2.36`. The workflow now pads a short tag before
using it. Nothing about the language changed.

## 2.36 - A tool worth running, and errors that read like a language
`examples/linkcheck.vel` is a real utility rather than a demonstration:
give it URLs on the command line or pipe a list in, and it reports each
one's status, counts the broken ones, and exits non-zero so a scheduler
can act. Progress goes to the error channel and the report to the
output channel, so `linkcheck ... 2>/dev/null` is a clean report. It
uses the http, log and standard modules together - the first program
here written the way a user would write one.

Writing it found a papercut worth fixing: a failed request handed
Python's own words to the user
(`<urlopen error [Errno -2] Name or service not known>`). Network
failures now say what happened - the address did not resolve, it did
not answer in time, the connection was refused, the certificate was not
accepted - because an error message is part of a language's surface,
not a place to leak the implementation.

## 2.35 - Dates as values, HTTP with headers, and a way in for others
`request(method, url, body, headers)` is one honest HTTP builtin: any
method, headers as JSON, and the whole answer back as JSON - status,
body and response headers together. `http.vel` wraps it as `call`,
`get_with`, `post_json`, `code_of`, `body_of`, `header_of`. Still
`uses net`, still fallible.

`dates.vel` makes a date a **record**, not text: `make` and `parse`
refuse impossible dates, `days_in` is proven to return between 28 and
31, and `before`, `same`, `next_day` and `text_of` work on values.
Writing it, the prover caught a real bug in it: `next_day` called
`days_in` without knowing the month was valid, because a record cannot
promise anything about its own fields. The fix was to say what the
function needs, which is the language working as intended on its own
standard library.

`velaris proofs --detail` lists each promise-carrying function and,
for the ones not proven, the contracts involved - so "60% proven"
becomes a list you can act on.

And the part that is not code: [ARCHITECTURE.md](ARCHITECTURE.md) is a
map of the compiler with a table of where things live and the five
rules this project holds; [MAINTAINERS.md](MAINTAINERS.md) says how
someone becomes a maintainer, what a maintainer may not do (weaken a
guarantee quietly), and lists six real, small, self-contained places
to start. A second maintainer is the single thing that would most
change what this project can promise, and now there is a door.

## 2.34 - Unattended work, and building for machines you do not have
`log(text)` writes to the error channel, and `log.vel` gives it levels
(`info`, `warn`, `error`, `event`, `fail_with`). Messages and results
finally travel separately: a pipeline captures `print` output while a
person watching sees the log, and `fail_with` exits non-zero.

`csv.vel` handles the shape most data arrives in - `fields`, `column`,
`column_int`, `rows_of`, `line_of` - and `time.vel` gains `year_of`,
`month_of` and `day_number`. `examples/pipeline.vel` is what an
unattended job looks like end to end.

`velaris build --for-everyone` writes a workflow that builds your
program on Windows, Linux and macOS and attaches all three to a
release. One machine genuinely cannot build for other machines; three
machines can, and this hands you the three.

The language server also renames: every use of a function this file
owns, comments left alone, and only names the file actually defines.

## 2.33 - A number a team can watch, and an image to run it in
`velaris proofs [path]` reports, for a file or a whole project, how
many promise-carrying functions are **proven before running** versus
**checked while running** - with `--json` for tooling and `--min 80`
to fail a build when the share slips. If a language's claim is proven
promises, that number should be visible and defended, not assumed.
The GitHub Action takes `min-proven`, and this project's own CI now
prints its share on every push.

The language server also completes: functions in scope with their
signatures and contracts, every builtin with its effects and whether
it can fail, and the keywords.

A `Dockerfile` builds an image with the prover and native backend
already installed, so `docker run --rm -v "$PWD:/work" velaris check
/work/main.vel` needs nothing on the machine but Docker.

## 2.32 - The editor knows what is proven, and CI is one line
The language server answers hover (signature, effects and contracts),
go-to-definition across imported files, an outline of the file, and -
the one that matters for this language - **code lenses above every
function saying whether its promises are proven before running or
checked while running**. That status comes from the real prover, using
the proof cache, so it is the truth rather than a guess.

`action.yml` makes Velaris a GitHub Action:

    - uses: gowrishankar-infra/velaris-lang@v2.32
      with:
        files: "src/*.vel"
        format: "true"

It installs Velaris with the prover and fails the build if anything
does not compile or a promise cannot be kept.

`ROADMAP.md` says what is planned, what is deliberately not (and why),
and how to change it. `SUPPORT.md` states plainly what one maintainer
can promise - and that an organisation depending on this today is
taking a real, non-technical risk. Both exist because a company reads
those before it reads code, and silence is worse than an honest limit.

## 2.31 - A standard library that reaches outside
Four modules so nobody writes FFI plumbing by hand:

    import "http.vel" as http        get, status, ok, send, get_json
    import "db.vel" as db            open, run, rows_json, count, close
    import "time.vel" as time        today, clock_text, seconds
    import "env_tools.vel" as sys    setting, number_setting, give_up

They are written in Velaris, so they carry their effects: a program
using `http` shows `net` in `velaris explain`, one using `db` shows
`ffi`, and a pure function still cannot call either.

Three builtins the modules needed, and every real script needs anyway:
`env(name, fallback)` reads the environment, `exit_with(code)` sets the
exit status (0-255, checked), and `read_line()` reads a line from
standard input.

## 2.30 - The language reference, and a position on concurrency
`SPEC.md` is the specification: what Velaris means, precisely. Lexical
structure, types, integer and float semantics, evaluation order,
effect propagation as a property of the whole call graph, failure,
what "proven" actually means and what is proven today, modular proof
and the rule that a dropped premise abandons the proof, modules,
native-versus-interpreted equivalence, the host language boundary,
errors, and versioning.

Two sections are there because a specification that lists only
strengths is advertising. **Concurrency**: Velaris is single-threaded
by design and has no concurrency model - stated as a position, with
the reason (a signature of the current design cannot describe data
races, so adding threads would break the language's central claim) and
what would have to change first. **What this language does not have**:
no exceptions, no closures, no inheritance, no macros, no package
registry, no mutable data structures, and a compiler written in Python
that is clear to read and slower than a production one.

The reference is published with the documentation.

## 2.29 - Remembered proofs
A proof that has already been done is not done again. Results are kept
in `.velaris/proofs.json`, keyed by what the proof actually depends on:
the function's own text **and the contracts of everything it calls** -
because a modular proof assumes those, and a cache that ignored them
would keep telling you something that is no longer true. Weakening a
callee's promise re-proves its callers, as it must.

The float refutation in `examples/fp_proof_bad.vel` takes 16.6 seconds
the first time and 0.10 seconds after, with the same message. Use
`--no-cache` to prove everything again, or `velaris clean` to forget.

## 2.28 - velaris build: hand someone your program
`velaris build program.vel` produces a single executable containing
your program, everything it imports, the standard library, and the
compiler itself. The person you give it to needs nothing installed -
not Python, not Velaris - which is the difference between a language
you write scripts in and one you deliver software with.

The program is compiled and proof-checked before it is built, so a
program that does not compile is never shipped. Command line arguments
reach `args()` as usual. Building needs PyInstaller
(`pip install pyinstaller`), and the compiler says so plainly when it
is missing.

## 2.27 - Handles: real libraries, not just functions
A `Handle` is a ticket for something living on the Python side - a
database connection, an HTTP session, a file. That is the difference
between calling functions and using libraries:

    py_new(module, function, args)   -> Handle    make one
    py_do(handle, method, args)      -> Text      call a method on it
    py_field(handle, name)           -> Text      read an attribute
    py_close(handle)                              let it go

`examples/database.vel` opens a real SQLite database, creates a table,
inserts a row, counts the rows and closes the connection - all from
Velaris, and all behind `uses ffi`, so a program that talks to a
database says so in its signatures.

Arguments travel as JSON and a trailing JSON object becomes keyword
arguments, which many Python APIs require. Handles pass through calls
as arguments too, and anything Python hands back that is not JSON
comes back as a handle rather than being flattened into a string.

## 2.26 - JSON, and calling Python with real data
The FFI shipped in 2.25 could only pass text and receive a scalar,
which is not "call any Python library" - it is "call the ones that
happen to take strings". `py_json(module, function, args_json)` sends
arguments and receives the answer as JSON, so numbers, lists and
nested data survive the trip: `py_json("math", "sqrt", "[16]")` now
gives back 4.0 rather than failing on a string.

JSON is first class and **pure** - reading a document is not an effect:

    json_get(doc, "user.name")     json_int(doc, "user.age")
    json_float(doc, "price")       json_len(doc, "tags")
    json_has(doc, "user.email")    json_of(anything)

Paths walk objects and lists (`tags[1]`, `items[0].price`), records
serialise straight to JSON, and every read can fail - a missing field
is a real possibility, not a crash, and the message says exactly which
step of the path was missing.

## 2.25 - Reaching the outside world, visibly
Velaris can call Python now, which means it can reach every library
Python has - JSON, dates, hashing, databases, anything - through three
builtins:

    py(module, function, args)        -> Text
    py_int(module, function, args)    -> Int
    py_float(module, function, args)  -> Float

They need `uses ffi`, so a function that reaches outside says so in its
signature, and a pure function still cannot do it - nor can anything it
calls. All three can fail (module missing, function absent, bad
argument), so callers handle it like any other failure. `velaris
explain` lists `ffi` next to the functions that use it, which is the
whole point: the power is available and it is never hidden.

Two conveniences, both deterministic: a dotted module path like
`datetime.date` is resolved by importing what imports and reaching the
rest by name, and a function that wants bytes rather than text gets the
text as UTF-8 after the first refusal.

## 2.24.1 - The extension follows the language's version
The 2.23 release tried to publish the extension as 2.22.1 - a version
already on the Marketplace - and reported that as a failure. The
extension's version now comes from the tag itself, an
already-published version is treated as nothing to do rather than an
error, and the test suite fails if the extension's version ever drifts
from the compiler's.

## 2.24 - Lists of text, and split
`List of Text` is modelled symbolically now, so promises about lists of
words are proven rather than checked while running -
`ensures length(result) == length(words) + 1` for a push, for instance.
List literals pick their element sort from their values, and pushing a
value of the wrong sort simply falls back to a runtime check instead of
being forced into a formula that would not mean the same thing.

`split` is modelled as an unknown list with a known minimum: the pieces
themselves are opaque to the prover, but it knows there is always at
least one, which is what contracts about splitting usually rest on.

## 2.23 - Libraries you can actually share
Until now, using someone's Velaris library meant copying a file and
hoping. Three commands fix that:

    velaris add <url or path> [as name]   vendor it into lib/
    velaris deps                          what this project depends on
    velaris verify                        are they exactly as recorded?

`add` fetches the file (local path or https), **compiles it before
accepting it** - a library that does not compile is not added - and
records its exact sha256 in `velaris.toml`. It then tells you what you
just took on: how many functions, how many with proven promises, and
what effects the library performs. `verify` re-checks every hash, so a
library that changed underneath you is something you find out about
rather than run.

Deliberately not a registry: the file lives in your repository where
you can read it, there is no resolver inventing versions for you, and
nothing is fetched at build time.

## 2.22.1 - First extension publish
A version bump so the tagged release has something newer than the
Marketplace has, now that the publisher and token exist. Nothing about
the language changed.

## 2.22 - The editor extension, ready to publish
The VS Code extension is packaged properly: real publisher and
repository metadata, an icon, a license, a written README, settings
for where Velaris lives and whether to check on save, and categories
so it can be found by search. A release workflow publishes it to the
Marketplace when a `VSCE_TOKEN` secret exists, and quietly skips when
it does not - so nothing breaks while that waits on a one-time setup.

## 2.21 - Watching a program run, and case-changing proofs
`velaris trace program.vel` prints every call as it happens - indented
by depth, arguments going in, answer coming back, and `FAILED` with the
reason when a call fails. Native calls are shown too, marked as such,
so a trace never hides half the program. It is the tool a beginner
reaches for when reading is not enough.

The prover models `upper` and `lower` as functions that keep a text's
length, so `ensures length(result) == length(word)` is proven rather
than checked at runtime. Honest limit: a *false* promise about them is
still caught at runtime rather than at compile time, because the
solver cannot pin down the letters themselves - proven claims stay
true, they are just fewer.

## 2.20 - Whole numbers have a size, and outgrowing it is an error
The fuzzer added in 2.16 found a real disagreement: native code holds
whole numbers in 64 bits and wraps around, while the interpreter used
Python's unlimited integers and kept counting. Same program, two
answers, silently.

Neither behaviour is acceptable, so both are gone. A whole number in
Velaris is 64-bit, and arithmetic that outgrows it is an error (E407)
in both engines - the interpreter checks the range, native code uses
the processor's overflow flag through LLVM's checked intrinsics. The
two seeds that found the bug now agree, and so do 250 fresh random
programs.

This is the first bug the fuzzer caught on its own, which is the
entire reason it exists.

## 2.19 - pip install velaris-lang
Velaris is on PyPI. Installing is now one line with no repository URL
to remember, and every release publishes automatically from its tag
through trusted publishing. The README, tutorial and docs site lead
with it.

## 2.18.2 - Minimal-mode expectations for the newest proofs
`div_bad.vel` and `grid_bad.vel` demonstrate bugs only the prover can
see: divide-by-zero on a path that happens not to be taken, and a row
read that is in range for the example data. Without z3 installed both
programs simply run, so the test suite expected the wrong verdict and
every no-dependency leg failed on all three platforms. They are now
listed with the other proof-only examples, and the suite passes with
and without the solver.

## 2.18.1 - Releases stay green
The PyPI job added in 2.18 cannot succeed until a pending publisher
exists on pypi.org, and a release should not be reported as broken for
a step that is waiting on a one-time setup. It no longer blocks the
release; the executables build and attach as before.

## 2.18 - Records holding lists, and publishing
A record's fields may now be lists, floats or text and still take part
in proofs, so `ensures length(result.items) == length(b.items) + 1` is
proven rather than checked at runtime.

Turning that on immediately found a real bug in the ledger app: with
records fully modelled, the prover could see that `describe` calls
`money(e.amount)` on an amount nothing had constrained to be positive.
`money` is now total - a negative amount formats as a refund - and the
app compiles honestly instead of relying on an assumption nobody
checked.

Releases now publish to PyPI on every tag (trusted publishing, no
stored token), so installing becomes `pip install velaris-lang`.

Also: the version in pyproject.toml had drifted to 1.9.0 while the
compiler said 2.17. The test suite now fails if the two ever disagree.

## 2.17 - for loops, tests in Velaris, and text containment proofs
`for i in 0 to n` and `for item in xs` are here. They are turned into
the while loops the rest of the compiler already understands, so
invariant inference and proofs work through them unchanged - the
shorter form costs nothing.

`velaris test program.vel` runs every function named `test_*` that
takes no arguments and reports which returned true.
`examples/std_test.vel` is the first suite: seven tests for the
standard library, written in Velaris, and CI runs them on every push.
The language can now test itself.

The prover models `contains` on text through Z3's string theory, so
`ensures contains(result, word)` is proven rather than checked at
runtime.

## 2.16 - Catching the next one, a third app, and a current tutorial
`fuzz_native.py` generates random Velaris programs - integer maths,
loops, list scans, text scans, floats, branches - runs each one
interpreted and natively, and fails if the two ever disagree. CI runs
it on every push, now across Linux, Windows **and macOS**: the exact
combination that would have caught the 2.15 problem before it reached
anyone.

`examples/fetcher.vel` is a third real program, and the first to use
the network: it reads a URL from the command line, checks the status
before downloading a body, and summarises what it got. Every network
call is behind `uses net` and can fail, so all three failure paths
(bad status, unreachable host, no arguments) are visible in the code
rather than assumed away.

TUTORIAL.md is rewritten for the language as it actually is. The old
one predated lambdas, namespaces, format, args, map proofs, invariant
inference and the whole toolset - someone arriving today was reading a
description of a language from fifteen releases ago.

## 2.15.1 - Native text building, made portable
Two examples failed on Windows in 2.15: a function that RETURNS text
handed a small struct back across the machine-code boundary, and how
that is done depends on the platform's calling convention. Rather than
guess at an ABI this project cannot test everywhere, text results now
stay interpreted. Text built *inside* a native function still uses the
arena and is still fast (183.5 ms interpreted, 4.1 ms native here).

Native compilation is also fail-safe now: if anything about a machine's
backend disagrees with the compiler, the program runs interpreted and
behaves identically, instead of failing. A speed optimisation should
never be able to stop a correct program from running.

## 2.15 - Native text building (the arena)
Concatenation compiles to machine code. Text is built in a scratch
buffer the runtime owns, reset at every call, so native code never has
to decide who frees what. If a call needs more room than the buffer
holds, **nothing is copied**: the buffer grows and the call runs again,
so the answer is always the one the interpreter would have given. A
million characters built through a 64 KB starting buffer comes back
byte-correct, unicode and emoji included, checked against 200 random
strings.

Measured: 172.8 ms interpreted, 0.9 ms native.

Getting there needed one more fix: `length` and `code_at` now work on
any text-valued expression, not just a variable. Before that,
`length(banner(word))` kept a whole loop interpreted, and crossing the
native boundary once per iteration was *slower* than staying
interpreted - the benchmark said so before the fix, which is why the
benchmark is in the example.

## 2.14 - Native text reads, and proven functions run fast
Text scanning compiles to machine code. Text crosses into native code
as Unicode code points plus a length, so `length` still counts
characters and non-English text behaves identically - verified against
300 random strings including accents and emoji. Reads are
bounds-guarded like list reads. Measured: 696.8 ms interpreted, 22.3 ms
native.

New builtin `code_at(text, i)` gives the code point at a position with
no allocation - the operation native scanning needs, and useful
interpreted too.

Two rules changed for the better. A function whose promises are
**proven** may now compile natively: an unproven promise still needs
its runtime check, but a proven one is already true, so there is
nothing to check. And the prover learned `length` on text and a sound
uninterpreted model of `code_at`, so text-scanning loops can be proven
at all.

Building text (concatenation) stays interpreted - that allocates, and
allocation gets its own release.

## 2.13 - Native lists
Pure functions that read `List of Int` now compile to machine code.
The list crosses into native code as a pointer plus a length, and every
read is bounds-guarded: an out-of-range position records the mistake
and returns without touching memory, so you get the same E602 you would
have got interpreted rather than a segfault. Measured on a
500-element list summed 200 times: 782.6 ms interpreted, 2.7 ms native,
identical results. Differential-tested as always.

Writing to lists (push) stays interpreted - that needs allocation, and
allocation needs an ownership story this language has not designed yet.

## 2.12 - Lists of lists, proven
A grid is now modelled symbolically - its rows, each row's length, and
how many rows - so `length`, `get` and `push` on nested lists take part
in proofs, and an out-of-range row is caught before the program runs
exactly as it is for a flat list. Nested list *types* also parse now:
`List of List of Int` was previously a syntax error.

That closes the last container with no proof story. Ints, Bools,
Floats (in IEEE-754), Texts, records, lists, nested lists and maps are
all proof territory; only Text contents remain runtime-checked.

## 2.11 - Invariant inference (the boring ones, for free)
Loops without a written `invariant` can now be crossed by the prover.
Candidate invariants are proposed for every counter a loop moves - it
never goes below, or never above, the value it started at - assumed
together, and whatever one loop step can break is dropped, repeating
until the set is stable. (Houdini, kept small.) `examples/inferred.vel`
proves three promises with no invariant lines at all.

Honest about the limits: this infers simple bounds on counters, not
membership or sortedness, so the standard library's loops still need
their hand-written invariants.

Also fixed something that had been quietly lying since 2.6: `explain`
and the inspector reported a function as "proven" whenever the file had
no errors, even when the prover had actually given up and left the
promise to a runtime check. The status now comes from the prover
itself, so "proven" means proven.

## 2.10 - Contracts on function values
An inline function can carry `requires` and `ensures` of its own, and
they are proven like any other function's - so a function value is a
first class citizen rather than a convenience. Because lambdas are
lifted to real functions, this needed no new machinery in the prover.
Errors about them now say "this function value" instead of leaking the
generated name.

## 2.9 - Map proofs
Maps are now modelled symbolically - the values, plus which keys are
actually present - so `put`, `get_or` and `has` take part in proofs.
Promises like "this key now holds one more than before" are proven
before the program runs, and wrong ones are refuted with the offending
key. Text values became symbolic strings to make map keys work, which
also lets Text cross call summaries.

Lists remain arrays of Ints: anything else (Text lists, lists of
lists) is explicitly guarded now and falls back to runtime checks
rather than being forced into a sort it does not fit.

## 2.8 - A second real app, and Text ordering
`examples/wordcount.vel` reads a file, counts word frequencies and
prints a ranked histogram - a different shape of program from the
ledger, exercising maps, records, lambdas, namespaced imports, format,
args, and three separate failure paths (missing file, unreadable count
argument, no words found).

Writing it found a real hole: Text had no ordering, so `c >= "a"` did
not compile and words could not be sorted alphabetically. `<`, `>`,
`<=` and `>=` now work on Text, comparing alphabetically. Promises
about Text comparisons are checked at runtime rather than proven, and
the prover does not pretend otherwise.

Also: the error de-duplication from 2.5.1 now lives in the shared
analysis, so `check`, `explain` and the browser inspector report one
message per problem too.

## 2.7 - Reading a codebase
`velaris check program.vel` compiles without running - for CI, editors,
and pre-commit hooks - and takes several files at once. `velaris
explain` now puts *your* functions first and summarises imported
libraries in one line (`--all` expands them), because the first real
run of explain buried a ten-function app under eighteen library
functions. `velaris explain <folder>` maps every .vel file under a
directory: functions, proven promises, effects, and any errors.

## 2.6 - Division proofs, and seeing what your code promises
`velaris explain program.vel` walks through a file function by
function: what it may do, what it needs, what it promises, and whether
those promises are proven or left to runtime. The browser playground
gains an **Inspect** button showing the same thing as cards, with
errors and their fixes in place. `--json` gives the whole report as
data for tools.

Contract printing is now precedence-aware, so `(result + 1) * count`
no longer prints as `result + 1 * count` (it did, on the docs site).

## 2.6 - Division proofs
`/` and `%` on whole numbers are now proof territory: the compiler
proves the divisor is never zero (E706, with the value that breaks it)
and can prove what the result means. Translated only when the divisor
is provably positive, because Velaris floors like Python while Z3's
integer division is Euclidean - the two disagree on negative divisors,
so that case falls back to a runtime check rather than a formula that
would quietly lie.

## 2.5.1 - One problem, one message
The effect checker and type checker could both report the same unknown
function, so a single mistake printed twice. Identical errors are now
reported once.

## 2.5 - Namespaced imports
`import "lib/geo.vel" as geo` then `geo.distance(a, b)`. A named import
prefixes that library's functions, rewriting its internal references so
the library is unchanged from the inside. Two libraries exporting the
same name can now be used in one file, which was impossible before.
Unknown namespaces and unknown functions inside a namespace get their
own messages (E200 lists what the namespace does offer), and a local
variable may not shadow an import name (E514). Plus a written piece on
why float proofs use IEEE-754 rather than reals: docs/floats.md.

## 2.4 - The everyday things
Function values inline: `keep_if(xs, fn(n: Int) -> Bool { return n > 4 })`.
They are lifted to real top-level functions, so types, effects, proofs
and native codegen treat them like any other function - and they cannot
capture surrounding variables, which keeps them pure and gives a clear
error when you try. Also: `format("hi {}", name)` with placeholder
count checked at compile time, `args()` for command line arguments,
`post(url, body)` and `fetch_status(url)` alongside `fetch`. The ledger
app now uses a lambda for its report sorting.

## 2.3 - Public launch polish
New visual identity across the docs site, playground, and README:
light professional design, verified-green brand, refined typography.
Landing page rebuilt. Fixed minimal-mode CI: fail_proof_bad's bug is
only findable by proof, so without z3 it is expected to run.

## 2.2 - Out-of-the-box readiness
velaris doctor (self-diagnosing setup with exact fixes), velaris new
(scaffold a project that runs), standalone executables for
Windows/Linux/macOS built and attached to every release (no Python
required), SECURITY.md with soundness-is-security policy, issue
templates, and a semver stability promise in the README.

## 2.1 - Documentation site
build_docs.py generates docs/: landing page, tutorial, a library
reference parsed from stdlib/std.vel by the real compiler (contracts
shown), an error index scraped from velaris.py (cannot go stale), and
the playground. Built in CI; one click from GitHub Pages.

## 2.0 - The builtins keep the language's promise (BREAKING)
to_int, get-on-a-map, read_file, and fetch are now fallible: they must
be called through check or try, and their failures can finally be
handled instead of killing the program. Migration is compiler-guided -
error E520 points at every call needing a wrap. get on a LIST is
unchanged (bounds are the prover's domain, proven at compile time).
New: get_or(m, key, default), a total map lookup. All examples
migrated; guess.vel now survives typos, net.vel survives outages, and
the ledger's loader shrank.

## 1.20 - sort_by + ledger reports
std.vel gains generic sort_by(xs, key) - sort anything by an Int key
function. The ledger uses it for a new report command: sorted-by-amount
listing with biggest, smallest, and totals. The CI session exercises it.

## 1.19 - Standard library sprint
std.vel grows to sixteen functions, all in Velaris: sort (ensures
is_sorted(result)), min/max (ensures membership), sum, keep_if,
count_where, join, range_list, is_sorted, insert_sorted; apply_to_each
and reverse rewritten with typed lets, dropping their nonempty
requirements. Library requires are enforced at importer call sites.

## 1.18 - Float proofs (real IEEE-754)
Float promises proven in Z3's floating-point theory - bit-for-bit the
machine's arithmetic. The prover refutes real-number identities that
rounding breaks, with the exact double as counterexample. FP queries
get a bigger solver budget; integer proofs stay instant.

## 1.17 - Failure-aware proofs
The prover understands fail / check / try: promises on 'or fail'
functions are proven for every returning path, fail-guards become
facts on those paths, and fallible callees' promises flow through try
and check. CI actions bumped past the Node 20 deprecation.

## 1.16 - Quantified list proofs
`all_of` / `any_of` with a predicate function; in contracts they become
Z3 foralls/exists with the predicate's body symbolically inlined.
Fixed a latent soundness-of-reporting hole: an untranslatable
`requires` now aborts the proof instead of being silently dropped
(dropped premises manufacture false counterexamples).

## 1.15 - Native Float and Bool
Typed LLVM codegen (f64, typed allocas/boundaries); division stays
interpreted so divide-by-zero is always a clean error;
differential-tested against the interpreter.

## 1.14 - Record proofs
Symbolic records (one Z3 value per field): field promises proven,
record-aware summaries, records printed in counterexamples.

## 1.13 - The first real app
examples/ledger.vel expense tracker; chars/file_exists builtins; typed
let enabling empty [] and {}; order-flexible signature clauses;
scripted-stdin testing so interactive apps run in CI.

## 1.12 - Continuous integration
GitHub Actions matrix (Linux/Windows x 3.10/3.12 x full/minimal deps),
dependency-aware suite, CHANGELOG, CONTRIBUTING.

## 1.11 - Language server
`velaris lsp`: standard LSP over stdio. Effect/type errors on every
keystroke, full pipeline with Z3 proofs on save; per-file diagnostics
(bugs in imported files squiggle in those files). Dependency-free VS
Code client bundled in `editor/vscode`.

## 1.10 - Formatter
`velaris fmt` (in-place, `--stdout`, `--check`). Comment-preserving,
idempotent, proven meaning-safe by re-running the whole suite on
formatted code. All repo examples reformatted.

## 1.9 - REPL
`velaris repl`: loose lines run immediately; fn/record/import
definitions pass effects, types, and proofs before joining the session.
CLI subcommands (run / repl / version). Unknown functions became a
friendly E200 everywhere.

## 1.8 - Real installation
`pip install ".[full]"` and a `velaris` command. Standard-library
search path: `import "std.vel"` works from any folder.

## 1.7 - Generics + first stdlib
`for any T` with call-site inference and clear conflict errors
(bindings shown). `stdlib/std.vel`: first/last/reverse/index_of/
contains_item/apply_to_each - written in Velaris.

## 1.6 - First-class functions
`fn(Int) -> Int` as a type; pass by name; call through parameters.
Only pure functions travel as values, so nothing is smuggled.

## 1.5 - Unignorable failure
`-> Int or fail`, `fail "reason"`, mandatory `check { ok / fail }`
handling, `try` propagation. Ignoring failure is a compile error.

## 1.4 - Maps
`{"a": 1}` typed `Map of K to V`; get/has/put/keys/length; typed keys
and values; clean E610 for missing keys.

## 1.3 - Float
Decimal numbers with NO silent Int/Float mixing - conversion is
explicit (`to_float`, `round`). Proper negation node.

## 1.2 - Browser playground
The real compiler running in-browser via Pyodide. Zero install.

## 1.1 - Escapes + editor
String escapes (\n \t \" \\) with friendly E002; VS Code syntax
highlighting.

## 1.0 - Testers' release
Multi-error reporting (all broken functions in one run, JSON array for
agents), `to_text`, `--version`, tutorial.

## 0.x - The climb
0.1 effects (io) - 0.2 effect split (io/net/fs/clock/rand) - 0.3 type
checking - 0.4 loops - 0.5 contracts (requires/ensures) - 0.6 lists,
and/or/not, negatives - 0.7 Z3 compile-time proofs - 0.8 modular
verification with sound false-alarm discipline - 0.9 LLVM native
compilation (~10,000x on hot loops) - 0.10 loop invariants - 0.11 real
HTTP fetch - 0.12 interactive input - 0.13 list proofs via array
theory with bounds obligations - 0.14 else-if, %, text tools - 0.15
records - 0.16 imports with per-file error blame.
