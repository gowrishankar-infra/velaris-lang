# Velaris changelog

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
