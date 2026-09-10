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

Memory caps use the operating system's address-space limit, enforced
on Linux and macOS; on Windows the timeout is enforced and the memory
cap is recorded but not applied. An agent framework calling `run` in a
loop should set both. The MCP server and the HTTP door default to 30
seconds and 512 MB.

## What `run` guarantees

`allow={"io"}` means the program cannot read a file, reach the
network, call Python, ask the clock or use randomness. Not "should
not" - the runtime refuses, and a refusal **cannot be caught** by the
program, so it cannot swallow the refusal and carry on.

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
| `safe_command` | the command that grants exactly what it declared |
| `warnings` | human-readable cautions, including which modules to grant |
| `ffi_modules` | top-level Python packages named in py* calls, for `ffi:` grants (added in 2.60 within schema 1) |

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

## From a language that is not Python

`velaris serve` opens a local HTTP door, so a Node service, a Go tool,
a Rust agent or a shell script can use the same three calls.

```
velaris serve --max-allow io,fs        # localhost:8787, grants at most this
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
limit: a caller asking for more gets 403 and is told what the server
grants. Start it with `--max-allow io` and no caller can touch the
disk, whatever they ask for.

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
