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
| A program cannot perform an effect the operator did not allow | The effect budget: `--allow`/`--deny`, or `allow=` in `velaris.run`; a refusal (E310) stops the program and cannot be caught | LLM06 Excessive Agency - partially addresses (bounds *what* an agent's code may touch; not which tools the agent is given, nor what it does through a granted effect). LLM05 Improper Output Handling - partially addresses (model output that is Velaris code is executed only within the budget). NIST Manage | `check_sandbox.py` | `io` includes `env()` and `args()`; `fs` and `net` have no path or host lists; code not written in Velaris |
| A program cannot reach a Python module the operator did not name | The `ffi:` allow-list (`--allow io,ffi:math`), enforced at the import gate for `py`, `py_json`, `py_new` and submodule paths, and in the bounded child | LLM06 - partially addresses. LLM03 Supply Chain - partially addresses (narrows which third-party code the program may invoke; says nothing about the provenance of that code). NIST Manage | `check_sandbox.py` | Anything a named module can do once named; plain `ffi` grants everything |
| A program that never ends, or grows without bound, is stopped | `timeout=` and `max_memory_mb=` run the program in a killable child; E610/E611 report which limit fired; defaults of 30 s / 512 MB in the MCP server and HTTP door | LLM10 Unbounded Consumption - partially addresses (time and memory; not request volume, CPU below the limit, or cost) . NIST Manage | `check_library.py` (the cap assertion runs on Linux only) | The memory cap is best-effort on macOS and not applied on Windows; use below the limits; network volume |
| A loop whose end cannot be shown is reported before running | The termination rule (SPEC.md 9.5): `loops_unshown` in the audit, E612 under `check --strict` | LLM10 - partially addresses (a static warning for one cause of unbounded consumption; the timeout remains the guard). NIST Measure | `check_termination.py` | Loops outside the one recognised shape are reported as unshown, not as infinite; a finite loop can still run for a long time |
| A promise the code does not keep is refused before running | Z3 proves `requires`/`ensures`/`invariant`, division by a possible zero and list reads against length, with a counterexample; an untranslatable premise falls back to a runtime check rather than a proof with a gap | LLM09 Misinformation - partially addresses (a contract that is proven cannot be silently false; a result with no contract is not checked). LLM05 - partially addresses. NIST Measure | `check_refusals.py`, `fuzz_native.py` | Functions with no contract; contracts the prover leaves to runtime; the prover's own limits (RESULTS.md rows 03d, 03f, 04e) |
| A failure cannot be ignored | `or fail` in the signature; E520 for any fallible call not handled with `check` or `try` | LLM05 - partially addresses (a bad parse of model output, a missing field, a failed request must be handled in code). NIST Manage | `check_fallible.py` | Overflow (E407) and refusals (E310/E311) stop the program rather than fail; a handler that ignores the reason it caught |
| What a program can touch is known before it runs | `velaris audit` / `velaris.audit()`: effects, `ffi_modules`, proven share, `can_fail`, `loops_unshown`, `contract_coverage`, `safe_command`, in a versioned format | LLM06 - partially addresses (review before execution). NIST Map, Measure | `check_library.py` | The audit describes; it does not decide. A reviewer who grants what the audit lists has granted it |
| Every release artifact is signed and its contents listed | `.github/workflows/release.yml`: sigstore signatures for the wheel and sdist, cosign for the three binaries and the `.mcpb` bundle, a CycloneDX SBOM, and a job that builds the wheel twice and compares them; every action pinned to a commit | LLM03 Supply Chain - partially addresses (provenance and integrity of Velaris itself; nothing about the model, its weights or its prompts). NIST Govern | The release workflow, on every tag; verification steps in SECURITY.md | Dependencies the operator installs alongside (`z3-solver`, `llvmlite`); the host Python |
| Soundness and sandbox reports are treated as security issues | SECURITY.md: private reporting, a fix within a week, credit in CHANGELOG.md and HALL_OF_FAME.md | NIST Govern | The record in CHANGELOG.md | No bounty; one maintainer |
| The guard is measured against other tools, and the misses are named | `benchmark/`: 60 programs in three languages, one command, results identical across ten runs | NIST Measure | `benchmark/run.py --quick --check` on every push | The benchmark measures the corpus it holds; a defect outside its categories is not measured |

## Items not addressed

LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM04
Data and Model Poisoning, LLM07 System Prompt Leakage and LLM08 Vector
and Embedding Weaknesses are outside what Velaris does. In particular
LLM02: a program run under `--allow io` can read the environment and
print it, so secrets in the environment are not protected by the
budget; see THREAT_MODEL.md.

## Reading this table

Nothing here makes an application compliant with anything. The table
says which control Velaris supplies for which item, how far, and where
the evidence is. The rest of each item - the model, the prompts, the
tools the agent holds, the data it is shown, the people operating it -
is the application's, and no row above touches it.
