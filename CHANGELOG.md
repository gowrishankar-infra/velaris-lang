# Velaris changelog

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
