# Threat model

What Velaris defends against when it runs a program somebody - or
something - else wrote, what it does not, and what to do about the
gap. Written for the person who has to decide whether agent-written
code may run on a machine they are responsible for. Every claim here
names the suite that tests it; the numbers come from
[benchmark/RESULTS.md](benchmark/RESULTS.md), which one command
regenerates.

## What Velaris is for

A model hands you a script. You want to run it without reading it
line by line, and you want the things it can do to be bounded by what
you said, not by what it says about itself. Velaris is a small
language in which a function's signature declares the effects it may
perform, the failures it may raise and the promises it keeps, and a
runtime that refuses any effect outside the budget the operator set.

It is not a general sandbox. It bounds programs *written in Velaris*;
it does nothing for a Python or shell script the same model might
write instead.

## The trust boundary

| Party | Trusted? | What that means |
|---|---|---|
| The operator | yes | Sets the budget (`--allow`, `--deny`, `timeout`, `max_memory_mb`) and decides what to do with the output. Everything below depends on the budget being narrower than "everything". |
| The program | no | Written by a model or a stranger. Its `uses` clauses, its contracts and its comments are claims the compiler checks; the runtime enforces the operator's budget regardless of them. |
| The compiler and runtime (`velaris.py`) | yes | One file, in the same process as the program it runs, or in a child process when a time or memory limit is set. A defect here is a defect in the guard. The suites below exist because of that. |
| The host Python and operating system | yes | The interpreter runs on CPython; the memory cap is the OS's address-space limit; the timeout kills a process. None of these are hardened by Velaris. |
| Python modules granted through `ffi:` | yes, in full | A granted module can do whatever that module can do. Granting `ffi:subprocess` is granting a shell. |

The budget is enforced inside the interpreter loop at the moment an
effect is attempted, and a refusal (E310, E311) is not a failure the
program can `check`; it stops the program. `check_sandbox.py` holds
the escape attempts that established this, including a helper two
layers down and a program that tries to catch the refusal and carry
on.

## What it defends against

| Threat | Mechanism | Tested by |
|---|---|---|
| A program that reads or writes files, reaches the network, asks the clock, draws randomness, or calls Python when the operator did not allow it | The effect budget: `--allow io` refuses `fs`, `net`, `clock`, `rand` and `ffi` at the call, whatever the source declares, and the refusal cannot be caught | `check_sandbox.py` - 16 escape attempts refused, 6 honest programs still run |
| A program that reaches a Python module outside the ones the operator named | The module allow-list: `--allow io,ffi:math` refuses `ffi:os` with E311, through `py`, `py_json`, `py_new`, a submodule path, and the bounded child process | `check_sandbox.py` - four ways round the list, all refused |
| A program that never ends, or eats memory | `velaris.run(timeout=, max_memory_mb=)` runs the program in a child process killed on breach and reports E610 or E611; the MCP server and the HTTP door default to 30 s and 512 MB | `check_library.py` - a program that never ends is stopped in 2 s; a program that doubles a text is stopped at 150 MB on Linux and macOS |
| A promise that is false - a contract the code does not keep, a division by a value that can be zero, a list read that can go past the end | The prover: `requires`/`ensures`/`invariant` are checked by Z3 before running (E700, E701, E703, E705, E706) with an exact counterexample; a premise it cannot translate abandons the proof to a runtime check rather than proving with a gap | `check_refusals.py` - 21 wrong programs each refused with the specific code; `fuzz_native.py` - random programs run natively and interpreted must agree exactly, so a proven-and-compiled function cannot behave differently from an interpreted one |
| A failure the program ignores - a parse, a map lookup, a pop, a network call, a Python call that can fail | Fallibility in the signature (`or fail`), and E520 for any fallible call not handled with `check` or passed up with `try` | `check_fallible.py` - every builtin in `FALLIBLE_BUILTINS` is refused when ignored and formats its failure when caught; a builtin added without a recipe fails the suite |
| A loop that never ends, before running it | The termination rule (SPEC.md 9.5): a loop is `terminates` only when a counter moves one step toward a limit the body leaves alone, `unshown` otherwise; reported by `audit` as `loops_unshown` and refused by `check --strict` as E612 | `check_termination.py` - 44 adversarial loops, each with its required verdict; the rule was wrong twice while being built, both times refusing a loop that ends, never the reverse |
| Not knowing what a program does before running it | `velaris audit`: effects, Python modules named, proven share, what can fail, loops not shown to end, functions that promise nothing about the data they handle, and the exact budget to run it under | `check_library.py` - the library and the MCP server report the same audit; the format is versioned (`velaris.audit/1`) |

On the 60-program benchmark (53 dangerous, 7 harmless), Velaris caught
51 of the 53 - 41 before running and 10 while running - and flagged
none of the 7. Under the same rules Deno caught 29 and plain Python
28. The two misses are named below.

## What it explicitly does NOT defend against

- **Anything a granted `ffi` module can do.** `ffi:os` is the whole
  operating system as the current user. The allow-list narrows which
  modules; it does not narrow what a module does. Plain `ffi` grants
  every module.
- **Side channels.** Timing, CPU load, cache effects, the size or
  timing of console output. Nothing measures or bounds them.
- **Resource use below the limits.** A program may run for 29 of its
  30 seconds and hold 511 of its 512 MB, every time it is called. The
  limits stop a runaway; they do not ration.
- **Request volume within the budget.** `net` allowed means any
  number of requests to any host. There is no host allow-list, no
  rate limit, and no distinction between GET and POST.
- **Everything `io` includes.** `io` is the console - and `args()`,
  `env()` and `read_line()`. A program run under `--allow io` can read
  environment variables and print them. If secrets live in the
  environment, they are within reach of an `io`-only program.
- **Everything `fs` includes.** `fs` has no path allow-list. Allowing
  it allows any path the OS user can reach, for reading and writing.
- **Logic errors with no contract.** A function that returns the wrong
  number and promises nothing is correct as far as the compiler knows.
  Benchmark row 04c (a loop that stops one item early) is this, and
  is a miss. The audit lists such functions under `contract_coverage`
  so the gap is visible; it does not close it.
- **The meaning of text.** A program that prints `rm -rf build` for
  its caller touches nothing (benchmark row 09c, a miss); a program
  that prints the same words in a warning is harmless (row 10d). No
  effect system can tell them apart, and Velaris does not try.
- **Code not written in Velaris.** A model asked for Velaris may hand
  back Python. The guard applies only to what the Velaris runtime
  runs.
- **Memory caps on Windows.** `max_memory_mb` uses the OS
  address-space limit, which Windows does not offer the same way; the
  cap is recorded and not enforced there. The timeout is enforced on
  every platform. (The benchmark harness wraps its own children in a
  Windows job object; the compiler does not do this for you.)
- **A tampered compiler.** Velaris is one Python file running in the
  same process as the untrusted program's interpreter. If the file,
  the package or the binary you run has been altered, nothing above
  holds. The release workflow signs every artifact and publishes an
  SBOM; [SECURITY.md](SECURITY.md) says how to verify a download.
  Verify it.
- **The compiler as a target.** `velaris check` runs the parser, the
  type checker and the prover on untrusted source. The prover has a
  time budget per query; the other passes do not. A hostile source
  can make `check` slow. Run it under the same timeout you would run
  the program under.
- **Compile-time reads.** `import "path.vel"` reads that file as
  code when compiling. It reads Velaris source, not data, and the
  effect budget applies to the program's own reads, not to imports.
- **The prover's reach.** Three benchmark rows (03d, 03f, 04e) are
  caught only while running: a division on the unguarded of two
  paths, a remainder inside a loop, a read at `i + 1` in a loop over
  `length(xs)`. The runtime check stopped each; the prover did not
  settle them beforehand. These are limits of the current prover,
  listed in RESULTS.md rather than worked around.

## Residual risks, and what to do about each

| Risk | Recommendation |
|---|---|
| A granted module does harm | Grant no `ffi` unless the task needs it, then name the modules (`ffi:math,json`) and treat the grant as trust in those modules. Never grant `ffi:os`, `ffi:subprocess`, `ffi:shutil` or plain `ffi` to code you have not read. |
| Secrets in the environment | Run agent-written programs with a clean environment. `io` reads `env()`. |
| Data leaves through `net` | Do not grant `net` to code you have not read. If the task needs it, enforce host restrictions outside Velaris (a network namespace, an egress proxy, a firewall rule); Velaris has no host list. |
| A program does damage within `fs` | Do not grant `fs` to code you have not read. If the task needs it, run in a directory that holds nothing else, as a user that can reach nothing else. |
| Runaway time or memory | Always set both `timeout` and `max_memory_mb`; the MCP server and HTTP door do by default. On Windows, add a job object or run on Linux. |
| The result is wrong and no promise catches it | Require contracts on the functions that matter (`velaris proofs --min 80` in CI) and read the audit's `contract_coverage` list. A program with no promises has proven nothing. |
| Output is trusted downstream | Never pipe a program's stdout into a shell or an interpreter. Treat output as data. |
| The model wrote something other than Velaris | Check the file extension and run `velaris check` first; refuse to run anything the checker refuses. |
| A compiler defect | Pin a version, verify the signature of what you install, run the suites (`python run_tests.py`, `check_sandbox.py`, `check_library.py`, `check_refusals.py`, `check_fallible.py`, `check_termination.py`, `fuzz_native.py`) on the machine that will run untrusted code, and report anything that lies through the private channel in SECURITY.md. |
| A single maintainer | Real, and stated in [SUPPORT.md](SUPPORT.md). Fixes to soundness and sandbox reports are promised within a week; nothing else is promised. |

## What "not a security boundary" means here

The README says the effect budget is not a security boundary, and this
document is the long form of that sentence. The budget is enforced by
an interpreter written in Python, in a process that also holds the
compiler, on a host that trusts that process. It is a strong guard
against a program that does what it was not asked to - the situation
you are in when a model hands you a script - and it is tested as such
on every push. It is not a substitute for an OS-level sandbox, a
network policy or a separate user account, and it should sit inside
one of those when the stakes warrant it.
