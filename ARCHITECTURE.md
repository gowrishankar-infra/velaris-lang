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
| The HTTP door | `serve_main`: the token, `--no-auth`, the ceiling, the endpoints |
| SARIF, the invocation log, the MCP tool manifest | section 16, after the pool: `_SarifRun` and `sarif_check`/`sarif_proofs`/`sarif_audit`; `InvocationLog`; `mcp_manifest_main` and `mcp_verify_main`, kept out of `velaris_mcp.py` so the server file cannot vouch for itself |

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
| `velaris test examples/std_test.vel` | does the standard library behave |

`check_termination.py`, `check_sandbox.py`, `check_refusals.py`,
`check_fallible.py` and `check_library.py` together constitute the
conformance suite for [velaris-spec](https://github.com/gowrishankar-infra/velaris-spec),
the capability format published separately. An implementation claiming
velaris.capabilities compliance must pass the subset that does not
require the prover: each of the five as it runs with no z3 installed
(rule 7 below says how to make that Python). velaris-spec's SPEC.md
section 10 says what the claim covers and what the suites do not yet
test.

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

## Working on it

    pip install -e ".[full]" pyinstaller
    python run_tests.py          # 92 examples, expected verdicts
    velaris test examples/std_test.vel
    python fuzz_native.py 60     # both engines must agree
    velaris fmt examples/*.vel stdlib/*.vel --check

All four must pass before a release. CI runs them on Linux, Windows
and macOS, with and without the optional solver.
