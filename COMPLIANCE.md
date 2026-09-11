# Compliance mapping

Each guarantee Velaris makes, mapped to the item in the OWASP Top 10
for LLM Applications (2025) it bears on and, where one applies, to a
function of the NIST AI Risk Management Framework. Every row names the
suite that tests the guarantee and what the guarantee does not cover.
"Addresses" is used only where the whole item is covered for programs
written in Velaris; "partially addresses" everywhere else, which is
most rows. This is a mapping written by the project, not an
assessment by a third party.

OWASP items referred to: LLM01 Prompt Injection, LLM02 Sensitive
Information Disclosure, LLM03 Supply Chain, LLM05 Improper Output
Handling, LLM06 Excessive Agency, LLM09 Misinformation, LLM10
Unbounded Consumption. NIST AI RMF functions: Govern, Map, Measure,
Manage.

| Guarantee | Mechanism | Framework item | Tested by | What it does not cover |
|---|---|---|---|---|
| A program cannot perform an effect the operator did not allow | The effect budget: `--allow`/`--deny`, or `allow=` in `velaris.run`; a refusal (E310) stops the program and cannot be caught. Since 3.0 `env` is its own effect, so an `io`-only budget cannot read the environment | LLM06 Excessive Agency - partially addresses (bounds *what* an agent's code may touch; not which tools the agent is given, nor what it does through a granted effect). LLM05 Improper Output Handling - partially addresses (model output that is Velaris code is executed only within the budget). LLM02 Sensitive Information Disclosure - partially addresses (environment secrets, only) . NIST Manage | `check_sandbox.py` | `io` still includes `args()` and `read_line()`; code not written in Velaris |
| A program cannot reach a path, host, port or count the operator did not name | Scoped grants (3.0): `fs:read:./data`, `fs:write:./out`, `net:host:port`, `net:*.domain`, `@N`; paths compared after `realpath`; E313/E314/E315 cannot be caught; a redirect to an ungranted host is a catchable failure | LLM06 - partially addresses (where and how often, within an effect). LLM10 Unbounded Consumption - partially addresses (operation counts). NIST Manage | `check_sandbox.py`, `check_library.py`, `check_fallible.py` (the redirect) | Rate and size of operations; what a granted host or directory does; hard links inside a granted directory; the file system changing under the program |
| A program cannot reach a Python module the operator did not name | The `ffi:` allow-list (`--allow io,ffi:math`), enforced for `py`, `py_json`, `py_new` and submodule paths, and in the bounded child. From 3.3 the whole dotted path a call reaches is checked, not only the module it names: an object owned by a module outside the grants is refused (E311), and an owner that cannot be determined is refused | LLM06 - partially addresses. LLM03 Supply Chain - partially addresses (narrows which third-party code the program may invoke; says nothing about the provenance of that code). NIST Manage | `check_sandbox.py` | Anything a granted module can do once granted; plain `ffi` grants everything |
| A program that never ends, or grows without bound, is stopped | `timeout=` and `max_memory_mb=` run the program in a killable child - RLIMIT_AS on POSIX, a Windows job object since 3.1; E610/E611 report which limit fired; defaults of 30 s / 512 MB in the MCP server and HTTP door, whose pooled workers carry the same limits | LLM10 Unbounded Consumption - partially addresses (time and memory; not request volume, CPU below the limit, or cost) . NIST Manage | `check_library.py`, `check_pool.py` (the cap assertion runs wherever the mechanism holds - `velaris.memory_cap_is_enforced()`) | The memory cap is best-effort on macOS; use below the limits; network volume |
| A loop whose end cannot be shown is reported before running | The termination rule (SPEC.md 9.5): `loops_unshown` in the audit, E612 under `check --strict` | LLM10 - partially addresses (a static warning for one cause of unbounded consumption; the timeout remains the guard). NIST Measure | `check_termination.py` | Loops outside the one recognised shape are reported as unshown, not as infinite; a finite loop can still run for a long time |
| A promise the code does not keep is refused before running | Z3 proves `requires`/`ensures`/`invariant`, division by a possible zero and list reads against length, with a counterexample; an untranslatable premise falls back to a runtime check rather than a proof with a gap | LLM09 Misinformation - partially addresses (a contract that is proven cannot be silently false; a result with no contract is not checked). LLM05 - partially addresses. NIST Measure | `check_refusals.py`, `fuzz_native.py` | Functions with no contract; contracts the prover leaves to runtime; the prover's own limits (RESULTS.md rows 03d, 03f, 04e) |
| A failure cannot be ignored | `or fail` in the signature; E520 for any fallible call not handled with `check` or `try` | LLM05 - partially addresses (a bad parse of model output, a missing field, a failed request must be handled in code). NIST Manage | `check_fallible.py` | Overflow (E407) and refusals (E310/E311) stop the program rather than fail; a handler that ignores the reason it caught |
| What a program can touch is known before it runs | `velaris audit` / `velaris.audit()`: effects, `ffi_modules`, proven share, `can_fail`, `loops_unshown`, `contract_coverage`, `safe_command`, in a versioned format | LLM06 - partially addresses (review before execution). NIST Map, Measure | `check_library.py` | The audit describes; it does not decide. A reviewer who grants what the audit lists has granted it |
| Every release artifact is signed and its contents listed | `.github/workflows/release.yml`: sigstore signatures for the wheel and sdist, cosign for the three binaries and the `.mcpb` bundle, a CycloneDX SBOM, and a job that builds the wheel twice and compares them; every action pinned to a commit | LLM03 Supply Chain - partially addresses (provenance and integrity of Velaris itself; nothing about the model, its weights or its prompts). NIST Govern | The release workflow, on every tag; verification steps in SECURITY.md | Dependencies the operator installs alongside (`z3-solver`, `llvmlite`); the host Python |
| Soundness and sandbox reports are treated as security issues | SECURITY.md: private reporting, a fix within a week, credit in CHANGELOG.md and HALL_OF_FAME.md | NIST Govern | The record in CHANGELOG.md | No bounty; one maintainer |
| The guard is measured against other tools, and the misses are named | `benchmark/`: 63 programs in three languages (56 dangerous, 7 controls), one command, results identical across ten runs | NIST Measure | `benchmark/run.py --quick --check` on every push | The benchmark measures the corpus it holds; a defect outside its categories is not measured |

## Items not addressed

LLM01 Prompt Injection, LLM04 Data and Model Poisoning, LLM07 System
Prompt Leakage and LLM08 Vector and Embedding Weaknesses are outside
what Velaris does. LLM02 is addressed only for the environment: since
3.0 a program needs the `env` effect to read it, and an `io`-only
budget refuses it; secrets a program is handed on stdin, in a file it
may read, or from a granted host are its to print. See THREAT_MODEL.md.

## Reading this table

Nothing here makes an application compliant with anything. The table
says which control Velaris supplies for which item, how far, and where
the evidence is. The rest of each item - the model, the prompts, the
tools the agent holds, the data it is shown, the people operating it -
is the application's, and no row above touches it.
