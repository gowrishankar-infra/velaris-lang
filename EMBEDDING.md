# Velaris from inside your program

Velaris is a library as well as a command. An agent framework, an MCP
server, a CI dashboard or an internal tool can check, audit and run
Velaris without shelling out - and the effect budget is enforced the
same way it is on the command line, whatever a program's source claims
about itself.

```
pip install velaris-lang
```

## Three calls

```python
import velaris

source = open("agent_output.vel").read()

result = velaris.check(source)
if not result.ok:
    for p in result.problems:
        print(p.code, p.line, p.message, p.fixes)

report = velaris.audit(source)
print(report.effects)        # ['fs', 'net'] - what it can touch
print(report.proven_share)   # 66.7 - how much is proven, not just checked
print(report.warnings)       # ffi cannot be contained by a budget

run = velaris.run(source, allow={"io"})
print(run.ok, run.output, run.refused_effect)
```

`velaris.card()` returns the language in about 2,300 words - paste it
into a model before asking for Velaris.

## Limits: time and memory

```python
run = velaris.run(source, allow={"io"}, timeout=30, max_memory_mb=512)
run.timed_out        # True if it ran past the limit and was stopped
run.out_of_memory    # True if it grew past the cap and was stopped
```

The effect budget bounds what a program may *touch*. These bound the
other two things a program can do to the machine running it: spin
forever, or eat memory. With either set, the program runs in a
separate process that is killed on breach, and the result says which
limit it hit (E610 for time, E611 for memory). The budget still holds
inside that process.

Memory caps use whatever the operating system has:

| Platform | Mechanism | Enforced? |
|---|---|---|
| Linux | `RLIMIT_AS`, set by the child on itself | yes |
| Windows | a job object with `JOB_OBJECT_LIMIT_PROCESS_MEMORY`; the child is created suspended, put in the job, and only then resumed | yes, since 3.1 |
| macOS | `RLIMIT_AS` | best-effort - the limit is set and not reliably honoured, and the timeout is what stops a runaway |

If the Windows job object cannot be made, the cap is recorded and not
enforced rather than the run failing - the behaviour before 3.1.
`velaris.memory_cap_is_enforced()` answers for the machine you are on,
so a suite can assert the cap where the mechanism holds and skip it
where it does not. The timeout is enforced on every platform.

An agent framework calling `run` in a loop should set both. The MCP
server and the HTTP door default to 30 seconds and 512 MB.

## Many runs: a pool

Every bounded run starts a Python interpreter - about a tenth of a
second before a line of Velaris is read. Calling `run` thousands of
times an hour pays that every time. A pool keeps workers alive:

```python
pool = velaris.Pool(size=4, allow={"io"}, timeout=30, max_memory_mb=512)
result = pool.run(source)        # the same RunResult run() returns
pool.close()                     # also a context manager
```

`pool.run` also takes `stdin=`, `args=` and `path=`. On one machine,
200 sequential bounded runs of a small program took 46.6 s one process
at a time and 0.5 s on a pool.

**The isolation rules matter more than the speed, and
`check_pool.py` asserts every one of them.**

* **The budget is the pool's, not the program's.** It is parsed once,
  when the pool is made, and installed by each worker at startup.
  `pool.run` takes no `allow` argument - there is nowhere for a caller
  or a program to ask for more. If you need a different budget, make a
  different pool. The budget is re-asserted from the pool before every
  program, so a `@N` count is spent per program rather than shared
  across a worker's whole life, and a program that reaches into the
  compiler through a granted `ffi` module and widens its own budget
  cannot leave it widened for the next program.

* **A worker is used once unless the run was clean.** Anything other
  than `ok` - a refused effect, a failure that escaped, a program that
  did not compile, the timeout, the memory cap - kills the worker and
  starts a fresh one. Only a run that finished cleanly hands its worker
  back. That costs a restart on every rejected program; it is the rule
  that makes the rest checkable.

* **A reused worker starts empty.** Before every program the child puts
  back every piece of module-level mutable state it has: the arguments
  `args()` answers, Python handles from `py_new` whether the program
  closed them or not, the native compiler's engines and the text arena
  they own, the tracer, the budget and its operation counts - and the
  working directory, the environment and the recursion limit, which a
  program granted `ffi` can change.

* **The parent owns the deadline.** A worker that has not answered
  within `timeout` is killed by the parent process, not asked to stop.
  The call returns E610 and a replacement worker is started.

* **A program cannot reach the pipe.** The worker keeps private copies
  of its own standard input and output for the protocol and points the
  program's at the null device, so a program writing straight at file
  descriptor 1 - which a granted `ffi` module can do - cannot corrupt
  the answer the parent is parsing.

* **Closing kills every worker**, including one still running a
  program. A pool collected without `close()` is closed by its
  finalizer, one that outlives the interpreter is closed at exit, and a
  worker whose pipe closes ends by itself - so a parent that dies
  without doing either still leaves nothing behind.

A pool changes none of the guarantees in
[THREAT_MODEL.md](THREAT_MODEL.md). A granted `ffi` module can still do
whatever that module can do, inside a worker as anywhere else; what a
pool promises is that it cannot do it to the *next* program.

`velaris.PoolRegistry()` keeps one pool per distinct budget and makes
each one the first time that budget is asked for - what a server needs,
since it learns the budget from the request. The MCP server and the
HTTP door each keep one. The CrewAI and LangChain tools stay on plain
`run`: a crew's tool is not called often enough to need a pool, and one
process per call is easier to reason about.

## What `run` guarantees

`allow={"io"}` means the program cannot read a file, reach the
network, read the environment, call Python, ask the clock or use
randomness. Not "should not" - the runtime refuses, and a refusal
**cannot be caught** by the program, so it cannot swallow the refusal
and carry on.

A grant can be narrower than an effect, in the same grammar the
command line takes (SPEC.md 7.1):

```python
velaris.run(source, allow={"io", "env",
                           "fs:read:./data", "fs:write:./out@50",
                           "net:api.example.com:443@100",
                           "ffi:math,json"})
```

`fs:read:./data` permits reads under that directory only, resolved
with realpath so `..` and symlinks cannot leave it; `net:host:port`
permits that host and port, `net:*.example.com` one label under the
domain; `@N` caps the operations of that effect for the whole run. A
path, host or count outside the grants is refused (E313, E314, E315)
and cannot be caught; the one catchable case is a redirect to a host
outside the grants, which fails the request naming the target.
`refused_effect` reports `fs:<path>`, `net:<host>` or `fs@count` /
`net@count` for those.

It is not a security boundary. `allow={"ffi"}` grants everything
Python can do, and nothing here limits memory, time, or what a program
prints. It is a real guard against accident and casual misbehaviour -
the situation you are in when a model hands you a script.

`run` captures stdout as `output` and stderr as `logs`, accepts
`stdin=` and `args=`, and restores the previous budget afterwards, so
several audits and runs can share a process.

## The audit format

`audit().as_dict()` is a stable, versioned shape. Tools can depend on
it; the `schema` field names the version.

```json
{
  "schema": "velaris.audit/1",
  "velaris_version": "2.52.0",
  "ok": true,
  "problems": [],
  "effects": ["fs", "io"],
  "functions": [
    {"name": "parse_row", "effects": [], "can_fail": true,
     "requires": [], "ensures": ["length(result) >= 1"],
     "status": "proven"}
  ],
  "proven_share": 66.7,
  "safe_command": "velaris <file> --allow fs,io",
  "warnings": []
}
```

Field meanings, all stable within `velaris.audit/1`:

| Field | Meaning |
|---|---|
| `schema` | the format's name and version |
| `velaris_version` | the compiler that produced this |
| `ok` | did it compile |
| `problems` | code, message, line, file, fixes |
| `effects` | everything the program may perform, transitively |
| `functions` | per function: effects, can_fail, contracts, and whether each contract is `proven` before running or `checked at runtime` |
| `proven_share` | percent of promise-carrying functions proven, or null when there are no promises |
| `safe_command` | the narrowest budget the audit can write: `fs:read:<path>` and `net:<host>` for the literals it read, the bare direction or effect where a value was built at runtime |
| `warnings` | human-readable cautions, including which modules to grant |
| `ffi_modules` | top-level Python packages named in py* calls, for `ffi:` grants (added in 2.60 within schema 1) |
| `loops_unshown` | loops the termination rule cannot show to end (added in 2.62) |
| `contract_coverage` | functions that take or return data and promise nothing (added in 2.62) |
| `fs_paths` | `{"read": [...], "write": [...], "read_any": bool, "write_any": bool}` - the path literals a program reads and writes; a flag says a path was built at runtime (added in 3.0) |
| `net_hosts` | `{"hosts": [...], "any": bool}` - the hosts (with ports when given) named in URL literals (added in 3.0) |

A new field may be added within version 1; a field will not change
meaning or disappear without the schema name changing.

## Setting it up in your assistant

**One command, every client on the machine:**

```
velaris mcp-install          # adds it wherever it finds a client
velaris mcp-install --list   # show what it found, change nothing
velaris mcp-install --remove # take it back out
```

It knows where Claude Code, Cline, Cursor, Windsurf, Continue and Zed
keep their configuration, adds a `velaris` server without disturbing
anything else already there, and backs up each file first. Restart the
assistant afterwards - closing the window is usually not enough.

**Claude Desktop:** newer builds only accept remote connectors in the
Add-connector dialog, so use the bundle instead. Download
`velaris.mcpb` from any release and open it, or drag it into
Settings -> Extensions. The compiler travels inside the bundle, so
nothing needs installing first. (The prover does not travel with it -
without `pip install z3-solver` promises are checked while running
rather than proven, and the tools say so rather than hiding it.)

## As an MCP server

`velaris_mcp.py` speaks the Model Context Protocol over stdin/stdout,
so an assistant can write Velaris, check it, audit it and run it in a
box without leaving the conversation.

```json
{"mcpServers": {"velaris": {"command": "python",
                            "args": ["-m", "velaris_mcp"]}}}
```

Four tools: `velaris_card`, `velaris_check`, `velaris_audit` and
`velaris_run` (which takes `allow`, defaulting to `["io"]`).

## Vendored libraries, and velaris.lock

```
velaris add https://example.com/geo.vel as geo   # vendored into lib/
velaris add https://example.com/geo.vel --force  # replace different bytes
velaris deps                                     # what you depend on
velaris deps --verify                            # do they match the lock?
```

`velaris add` writes two files. `velaris.toml` says what the project
depends on. **`velaris.lock`** says exactly which bytes were vendored:
every library with its source, its sha256 and the version of Velaris
that added it. The digest is of the fetched bytes exactly as they
arrived, so it is the digest the source published and the same on every
platform.

`velaris deps --verify` (`velaris verify` is the older spelling of the
same check) fails if a vendored file's hash differs from the lock, or
if a lock entry has no file on disk. Run it in CI: a library that
changed under you is worth looking at before trusting it.

`velaris add` refuses to overwrite a library that is already vendored
when the incoming bytes are different, and prints both digests;
`--force` replaces it. A project made before 3.1 has no lock, and
`deps --verify` says so and falls back to checking `velaris.toml`.

## From a language that is not Python

`velaris serve` opens a local HTTP door, so a Node service, a Go tool,
a Rust agent or a shell script can use the same three calls.

```
velaris serve --max-allow io,fs:read:./data,net:api.example.com@100
                                       # localhost:8787, grants at most this
```

```
GET  /health         version, whether the prover is installed, the ceiling
GET  /card           the language, for pasting into a model
POST /check          {"source": "..."}                  -> problems, proven
POST /audit          {"source": "..."}                  -> velaris.audit/1
POST /run            {"source": "...", "allow": ["io"], "stdin": "", "args": []}
```

```javascript
const answer = await fetch("http://127.0.0.1:8787/run", {
  method: "POST",
  body: JSON.stringify({ source, allow: ["io"] }),
}).then(r => r.json());

console.log(answer.ok, answer.output, answer.refused_effect);
```

There are **two ceilings**, and both are enforced. The `allow` in a
request is the program's budget. `--max-allow` is the server's own
limit, in the full grammar: a caller asking for more at any level - an
effect, a module, a wider path prefix, a host the server does not
name, a port, a larger count, or an unscoped `fs`/`net` against a
scoped ceiling - gets 403 and is told what the server grants. Start it
with `--max-allow io` and no caller can touch the disk, whatever they
ask for.

It binds to `127.0.0.1` unless told otherwise, because **this endpoint
runs programs**. Do not expose it to a network you do not control, and
prefer `--max-allow io,fs` over granting `ffi` on a shared machine -
the server warns about both.

## From JavaScript

```
npm install velaris-lang        # or: npx velaris-lang script.vel --allow io
```

```javascript
import { audit, run } from "velaris-lang";

const report = await audit(source);
const result = await run(source, { allow: ["io"] });
console.log(result.ok, result.output, result.refusedEffect);
```

The compiler is a Python package, so `pip install velaris-lang` once;
the npm package says so plainly if it is missing. Types ship with it.

## In a notebook

```
%pip install velaris-lang
%load_ext velaris_magic
```

```
%%velaris --audit --allow io
fn main() uses io {
    print("proven before it ran")
}
```

`--audit` prints what the cell can touch and how much of its promises
are proven before running - useful when the code in the cell came from
a model. Effects outside `--allow` are refused, and the cell says which
flag would permit them.

## As a GitHub Action

```yaml
permissions:
  contents: read
  pull-requests: write          # only for pr-comment

steps:
  - uses: actions/checkout@v5
  - uses: gowrishankar-infra/velaris-lang@v2.63
    with:
      min-proven: "80"
      pr-comment: "true"
```

The action installs Velaris with the prover, checks every `.vel` file
(or the `files` glob), and fails the job if anything does not compile
or a promise cannot be kept. With `pr-comment: "true"`, on a
`pull_request` event it also posts one comment holding the audit of
each changed `.vel` file - the same `velaris.audit()` this document
describes: effects, Python modules named, proven share, the safe
command, and the warnings (`loops_unshown`, `contract_coverage`) - and
on later runs edits its own comment, found by a hidden HTML marker,
rather than adding another. It talks to the REST API with the job's
`GITHUB_TOKEN` through `curl`; no third-party action is involved.

## As a commit hook

```yaml
repos:
  - repo: https://github.com/gowrishankar-infra/velaris-lang
    rev: v2.55
    hooks:
      - id: velaris-check      # it compiles, and the promises hold
      - id: velaris-fmt        # canonically formatted
      - id: velaris-proofs     # at least 80% proven, not just checked
```

## Trying it with nothing installed

```
pipx run --spec velaris-lang velaris hello.vel
```

Or open the [playground](https://gowrishankar-infra.github.io/velaris-lang/playground.html) -
the real compiler, in a browser, nothing to install.
