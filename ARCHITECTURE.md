# How the compiler works

Everything is in one file, `velaris.py`, in the order the compiler
uses it. If you read it top to bottom you follow a program through the
whole pipeline. This document is the map.

    text -> lexer -> parser -> loader -> effects -> types
         -> proofs -> native codegen -> interpreter

## The stages

**Lexer** turns text into tokens. Keywords are a fixed set; everything
else is an identifier, a literal, or an operator.

**Parser** builds an AST of dataclasses (`Function`, `Call`, `BinOp`,
`If`, `While`, ...). Two things are desugared here so nothing later
has to know about them: `for` loops become `while` loops, and inline
functions are lifted into ordinary top-level functions. That is why
proofs and native compilation work on them unchanged.

**Loader** resolves `import`, tracks which file each function came
from (for error blame), and prefixes names for a named import.

**Effect checker** walks the call graph. A function may only perform
effects it declares, transitively. This runs before types because a
missing effect is a clearer error than a type mismatch downstream.

**Type checker** infers local types, checks calls, unifies generics at
call sites, and decides which builtins are fallible in context (`get`
on a map can fail; on a list it cannot).

**Prover** is the interesting part. For each function it explores the
body symbolically, building Z3 formulas, and asks whether the
`ensures` can be false given the `requires`. Calls use *summaries*:
the callee's contract is assumed, its body is never inlined. Loops use
invariants — written, or inferred for simple counter bounds. The rules
that matter most are in SPEC.md §9; the one to internalise is that an
untranslatable premise abandons the proof rather than dropping it.

**Native codegen** (llvmlite) compiles pure functions over Int, Float,
Bool, list reads and text reads — and functions whose contracts are
proven, since a proven promise needs no runtime check. Anything that
cannot be made identical to the interpreter is not compiled.

**Interpreter** runs everything, with runtime checks for promises the
prover could not settle.

## Where things live

| What | Where to look |
|---|---|
| Adding a builtin | `BUILTINS` table, then `run_builtin` |
| Making a builtin fallible | `FALLIBLE_BUILTINS` |
| A new proof capability | `to_z3` in the prover section |
| A new statement | parser, then `explore`, `run`, and codegen |
| Editor features | `editor_answer` and `lsp_serve` |
| CLI commands | `main`, near the other `argv[:1] == [...]` checks |
| Anything a program can leave behind | `MUTABLE_GLOBALS` and `reset_program_state`, and the scan in `check_pool.py` that fails when a new module-level container appears in neither list |
| A new error code | `ERROR_TABLE`, beside `VelarisError`: one line saying what it means. `check_library.py` fails if a code is raised that is not there; the errors page and the SARIF rules are built from it |
| The HTTP door | `serve_main`: the token, `--no-auth`, the ceilings, the endpoints. The time and memory ceilings both doors share are `door_ceilings` and `run_limits`, just above it |
| SARIF, the invocation log, the MCP tool manifest | section 16, after the pool: `_SarifRun` and `sarif_check`/`sarif_proofs`/`sarif_audit`; `InvocationLog`; `mcp_manifest_main` and `mcp_verify_main`, kept out of `velaris_mcp.py` so the server file cannot vouch for itself |
| The capability ratchet | section 17: `_program_capabilities` derives one file's needs (`_needs` for the grants, `_operation_bounds` for the counts), `capability_scan` a tree's, `capabilities_compare` holds a tree to a baseline - never to a previous commit - and `review` compares a git ref with the working tree. velaris-spec section 9 is the text of every rule there |
| A removed error code | `REMOVED_ERRORS`, beside `ERROR_TABLE`: STABILITY.md rule 3 |
| Conformance | section 18: `conformance` runs velaris-spec's corpus through the budget parser, the audit, the command line and the baseline writer and check; `build_conformance.py` writes that corpus from the tables of `check_sandbox.py`, `check_library.py` and `check_ratchet.py` |
| The attestation | section 19, at the end: `attest_statement` wraps `audit()`'s own output in an in-toto Statement, the audited file and its imports as subjects by sha256; `attest` does a file or a directory, `attest_main` is the command. It signs nothing; the release workflow's `attestation` job signs one with cosign and with sigstore-python and verifies both |

## The suites, and what each one is for

| Suite | Asks |
|---|---|
| `run_tests.py` | do all 92 examples reach their expected verdict |
| `fuzz_native.py` | do the native and interpreted engines agree exactly |
| `check_refusals.py` | is each wrong program refused with the RIGHT code |
| `check_sandbox.py` | can the effect budget be escaped |
| `check_fallible.py` | is every fallible builtin actually enforced |
| `check_library.py` | do the library and MCP server keep the same promises |
| `check_pool.py` | can a pooled worker leak anything to the next program |
| `check_termination.py` | does each loop get the termination verdict it must |
| `check_ratchet.py` | does every widening of the capability surface fail, against the declared baseline and not the previous commit, and does every change that does not widen pass |
| `velaris test examples/std_test.vel` | does the standard library behave |
| `velaris conformance` | does this implementation pass velaris-spec's corpus, at L1, L2 and L3 |
| `build_conformance.py --check` | is velaris-spec's corpus still what these suites' tables say |

Conformance to [velaris-spec](https://github.com/gowrishankar-infra/velaris-spec),
the capability format published separately, is its corpus: from 4.1,
444 JSON cases in velaris-spec's `tests/`, at three levels its
CONFORMANCE.md defines, which an implementation in any language runs
its own way. Until 4.1 it was six suites of this repository -
`check_termination.py`, `check_sandbox.py`, `check_refusals.py`,
`check_fallible.py`, `check_library.py` and `check_ratchet.py` - run
without the prover, which only an implementation driven through this
command line and library could run. The corpus is written by
`build_conformance.py` from the tables of three of those suites -
`check_sandbox.py` for level 2, `check_library.py` and
`check_ratchet.py` for levels 1 and 3 - where each entry is asserted
against this implementation, so a case says what its suite says.
`velaris conformance` runs the corpus against this implementation, and
CI runs it and `build_conformance.py --check` on every leg. None of it
needs the prover.

## The rules this project holds

1. **Never claim something is proven when it is not.** If a premise
   cannot be translated, abandon the proof; runtime checks still guard.
2. **Native and interpreted must agree.** If they cannot, do not
   compile that case. `fuzz_native.py` checks this on every release.
3. **Every new example gets `velaris fmt`** before it ships.
4. **A moved or deleted file needs an explicit `git rm`** — release
   archives overlay, they do not delete.
5. **Write the limitation down.** The changelog records mistakes on
   purpose; a project that only lists wins cannot be trusted about
   anything else.

6. **A worker pool must reset every mutable global between programs.**
   `velaris.Pool` runs one program after another in one process, which
   is exactly where one program's leftovers become the next program's
   starting state. Anything added to this file that a running program
   can change belongs in `MUTABLE_GLOBALS` and in
   `reset_program_state`; `check_pool.py` reads this file's own
   module-level assignments and fails if a mutable one is in neither
   that list nor its list of constants. Speed is never the reason to
   skip a reset - a fast sandbox that leaks state between programs is
   worse than a slow one.

7. **Run every new suite WITHOUT the prover before wiring it into CI.**
   This has been got wrong three times - v2.39.1, v2.44, v2.53.1 - and
   always the same way: a suite passes locally, joins CI, and every
   no-solver leg fails because some check quietly depended on proofs.
   Make a Python with no z3 and run the suite there first:

       python -m venv /tmp/bare && /tmp/bare/bin/pip install ".[test]"
       /tmp/bare/bin/python check_whatever.py

   (`[test]` is jsonschema, for the SARIF checks; it brings no solver.)

   Better than skipping the proof-dependent checks is asserting the
   FALLBACK - that the promise breaks while running instead - which is
   what `check_library.py` does now.

8. **A scenario in a suite's table is a conformance case.** An entry
   added to or changed in `ESCAPES`/`HONEST` (`check_sandbox.py`),
   `BUDGETS`/`AUDITS`/`malformed_budgets()` (`check_library.py`), or a
   table of `check_ratchet.py` changes velaris-spec's corpus. Regenerate
   it (`python build_conformance.py ../velaris-spec/tests`) and commit it
   there in step; CI's drift test fails until the two agree. A case
   that depends on Python itself says so in `not_in_corpus`, and is left
   out with the reason.

## Working on it

    pip install -e ".[full]" pyinstaller
    python run_tests.py          # 92 examples, expected verdicts
    velaris test examples/std_test.vel
    python fuzz_native.py 60     # both engines must agree
    velaris fmt examples/*.vel stdlib/*.vel --check

All four must pass before a release. CI runs them on Linux, Windows
and macOS, with and without the optional solver.
