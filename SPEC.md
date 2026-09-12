# The Velaris language reference

This is the specification: what Velaris means, precisely. It is not a
tutorial ([TUTORIAL.md](TUTORIAL.md) is), and it does not teach
programming. It exists so that anyone deciding whether to depend on
this language can find out exactly what it promises — and what it
does not.

Version 2.30. Where this document and the implementation disagree,
that is a bug in one of them; please report it.

## 1. Programs

A program is one or more files of UTF-8 text with the extension
`.vel`. Execution begins at `main`, which takes no parameters and
cannot fail. A program without `main` is rejected (E400).

Files are combined by `import` (§10). There is no separate linking
step and no build configuration: the entry file plus what it imports
is the program.

## 2. Lexical structure

Comments run from `//` to end of line. Whitespace is insignificant
except as a separator; there is no layout rule and no significant
indentation.

Identifiers begin with a letter or underscore and continue with
letters, digits or underscores. They are case-sensitive.

Keywords: `fn let return if else uses true false while for requires
ensures and or not invariant record import fail check try`.

Literals:

| Kind | Examples | Notes |
|---|---|---|
| Int | `0`, `42`, `-7` | 64-bit, signed (§4.1) |
| Float | `1.5`, `0.0`, `-2.25` | IEEE-754 binary64 (§4.2) |
| Bool | `true`, `false` | |
| Text | `"hello"`, `"a\nb"` | escapes: `\n \t \\ \" \r \0` |
| List | `[1, 2, 3]` | all elements one type |
| Map | `{"a": 1}` | keys `Text` or `Int` |

An empty `[]` or `{}` has no inferable element type; give it one with
a typed `let` (E506, E507).

## 3. Types

    Int  Float  Bool  Text  Handle
    Money of CUR             (an amount in a currency, §4.4)
    List of T
    Map of K to V            (K is Text or Int)
    fn(T, ...) -> R          (a function value; pure only)
    <record name>

There is no null, no undefined, no implicit conversion, and no
subtyping. A value has exactly one type, known at compile time.

`Handle` is an opaque reference to a value living in the host language
(§12). It can be passed and stored; it has no operations of its own.

Generic functions are written `for any T` and are instantiated at each
call site by unification with the argument types. There are no
constraints or bounds.

## 4. Numbers

### 4.1 Whole numbers

`Int` is a signed 64-bit integer: −9223372036854775808 to
9223372036854775807. Arithmetic that leaves that range is an **error**
(E407), not a wraparound and not a promotion to a larger type. This
holds identically in interpreted and natively compiled code; the two
are checked against each other by a fuzzer on every release.

`/` on two `Int`s is division that rounds toward negative infinity
(`-7 / 2` is `-4`). `%` returns the remainder with the sign of the
divisor, so `x == (x / y) * y + (x % y)` holds for all `y != 0`.
Division or remainder by zero is an error (E403), never an infinity.

### 4.2 Decimals

`Float` is IEEE-754 binary64 with round-to-nearest-even, including
signed zeros, infinities and NaN. `Float` division by zero follows
IEEE-754 and yields an infinity; this is the one place the language
does not raise an error, because it is what the hardware defines.

`Int` and `Float` never mix implicitly. `to_float(x)` widens;
`round(x)` narrows.

### 4.3 Money

`Money of CUR` is an exact amount: a whole number of **minor units** —
paise, cents, fils — in the currency `CUR`, which is part of the type.
The units are an `Int`, with the same 64-bit range and the same error
past it (E407). No `Float` is part of any of it, and there is no
conversion between currencies: a rate and a rounding policy are a
program's decisions, not a language's.

    money(1250, "INR")        12.50 rupees, as 1250 paise
    units_of(m)               its minor units, as an Int
    with_units(m, n)          n minor units, in m's currency

`money` and `parse_money` take the currency as text **written in the
call**, and it must be one the implementation knows (`CURRENCIES` in
`velaris.py`, §4.4); anything else is E551. A function may be generic in
a currency: `fn f(m: Money of C) -> Money of C for any C`.

**Arithmetic.** Two amounts in the same currency add, subtract and
compare. An amount multiplies by an `Int`. Everything else is refused
before the program runs: two currencies mixed (E550), an amount times an
amount, an amount and a number, an amount and a `Float` (E501), and `/`
or `%` on an amount (E553), because both would round without saying how.

**Rounding is named or it does not happen.** Where a result may not come
out even, the mode is a required argument, written in the call as
`"half_up"` (a half goes away from zero), `"half_even"` (to the even
neighbour) or `"down"` (toward zero). Anything else is E552.

    percent_of(amount, numerator, denominator, "half_up")
    divide_or_fail(amount, by, "half_even")          // can fail

`percent_of` multiplies before it divides and is exact in between,
however large that product; only its result must fit in 64 bits. A
denominator of zero is an error while running (E403), and one the prover
shows can be zero is E706. `divide_or_fail` fails, catchably, on zero
and on a result too large to hold.

`units_of` also takes a **list** of amounts and gives what they add up
to, as an `Int`, and 0 for an empty list. There is no `Money`-valued
total of a list, because an empty list has no currency to give one.

`text_of(m)` writes the code, then the amount with exactly as many
digits after the point as the currency has minor units: `INR 12.50`,
`JPY 1250`, `KWD 1.250`, `INR -0.05`. `to_text`, `print` and `format`
write an amount the same way; `json_of` writes it as its currency and
its units, never as a number with a point. `parse_money(text, "INR")`
reads back what `text_of` wrote, and the same without the code or with
fewer digits after the point; it fails on anything else, including a
text with more digits than the currency has.

Dividing an amount into parts that still add up to it is
`money.split(amount, n)` from `stdlib/money.vel`, which is written in
Velaris so that its promises are proven with the program that imports
it (§9.2): `length(result) == n`, `units_of(result) == units_of(amount)`,
and no part with a sign the amount does not have.

### 4.4 Which currencies

An implementation carries a table of currency codes and how many digits
each has after the point: `CURRENCIES` in `velaris.py`, which today
holds 21 of them — 2 digits for INR, USD, EUR and most others, 0 for JPY
and KRW, 3 for KWD, BHD, JOD and OMR. **It is not exhaustive.** A
currency outside it is refused (E551) rather than assumed to have two
digits, because an assumed minor unit prints and parses amounts wrongly.
Adding one is a line in that table with the count ISO 4217 gives it, and
a case in `check_money.py`. A program cannot add its own: two programs
that disagreed about a currency would write the same amount two ways.

### 4.5 Text

`Text` is a sequence of Unicode code points. `length` counts code
points, not bytes, and `code_at(t, i)` returns the code point at a
position. Comparison (`<`, `>`, `<=`, `>=`) is lexicographic by code
point. Text is immutable; `+` produces a new value.

## 5. Values and mutation

Records, lists and maps are immutable. `push`, `put` and record
construction produce new values; nothing observes a change made
elsewhere. `let` introduces a binding; assignment (`x = e`) rebinds a
local name and never mutates a value another name refers to.

Equality (`==`) is structural for records, lists and maps, `fpEQ` for
`Float` (so NaN is not equal to itself, and `0.0 == -0.0`), and
ordinary equality elsewhere.

## 6. Evaluation

Evaluation is strict, left to right, depth first. Arguments are fully
evaluated before a call. `and` and `or` short-circuit: the right side
is not evaluated when the left decides the result. `if`/`while`
conditions must be `Bool`; there is no truthiness.

There is no undefined behaviour. Every operation either produces a
value, raises a language error with a code, or fails in the sense of
§8.

## 7. Effects

A function declares what it may do:

    fn save(path: Text, body: Text) uses fs { ... }

The effects are `io` (the console: `print`, `read_line`, `args`),
`env` (environment variables, through `env()`), `fs` (files), `net`
(network), `clock` (the time), `rand` (randomness) and `ffi` (calling
the host language, §12). `env` became its own effect in 3.0; before
that it was part of `io`, which meant an io-only budget could read
every secret in the environment.

The rule is transitive and checked at compile time: a function may
only perform effects it declares, and calling a function requires
declaring everything that function declares. A function with no `uses`
clause is **pure** — it cannot perform any effect, and neither can
anything it calls, however deep. Violations are E300.

This is a property of the whole call graph, not a convention. Reading
a signature tells you the complete set of things a call can do to the
outside world.

### 7.1 The budget

Declaring an effect is the program's claim; the **budget** is the
operator's decision, given as `--allow` / `--deny` on the command line
or `allow=` in the library, and enforced by the runtime at the moment
an effect is attempted, whatever the source declares. A refusal stops
the program and cannot be caught.

A grant names an effect, and may narrow it:

| Grant | Permits |
|---|---|
| `io`, `env`, `clock`, `rand` | that effect |
| `fs` | any path, read and write |
| `fs:read`, `fs:write` | one direction, any path |
| `fs:read:P`, `fs:write:P` | one direction, for paths that resolve under `P` |
| `net` | any host |
| `net:H`, `net:H:PORT` | that host, at any port or at that port |
| `net:*.D` | hosts with exactly one label in place of the star |
| `ffi` | any Python module |
| `ffi:a,b` | those top-level modules |
| `...@N` | and at most N operations of that effect in the run |

Grants are additive. Paths are resolved with `realpath` when the budget
is parsed and again at every `read_file`, `write_file` and
`file_exists`, then compared as prefixes, so `..` and symlinks cannot
reach past a grant. A host is the URL's host name, lower-cased; a port
is the URL's port or the scheme's default; only `http` and `https` are
reachable. A wildcard matches one label and never the domain itself;
no wildcard may stand over an IP literal. A count is the smallest given
for that effect and counts every operation of that effect across the
whole run; a budget with no count is a budget on what, not on how much.

The refusals: E310 (the effect), E311 (a module outside `ffi:`), E313
(a path outside `fs:`, named), E314 (a host or port outside `net:`,
named), E315 (the count reached). One case is a catchable failure
rather than a refusal: a redirect whose target is outside the `net:`
grants fails the request, naming the target, because the program did
not choose where it was sent.

Outside the rule, and stated as such: a hard link inside a granted
directory is that directory's content; a file system changed by another
process between the check and the open is outside the model; where a
granted host name resolves is DNS's business.

## 8. Failure

A function that can fail says so:

    fn parse(t: Text) -> Int or fail { ... }

Inside it, `fail "reason"` stops that call. A caller must handle the
possibility, in one of two ways:

    check parse(t) { ok n { ... } fail why { ... } }   // handle here
    let n = try parse(t)                               // pass it up

`try` is only allowed inside a function that itself says `or fail`.
Ignoring a fallible call is a compile error (E520). `main` cannot
fail.

Fallible builtins: `to_int`, `read_file`, `fetch`, `post`,
`fetch_status`, `get` on a **map**, `divide_or_fail`, `parse_money`, the
`py_*` family, and the `json_*` readers. `get` on a **list** is not fallible: list bounds are the
prover's domain (§9.4), and `get_or(m, k, default)` gives a total map
lookup.

## 9. Contracts and proof

### 9.1 What you write

    fn f(x: Int) -> Int
        requires x >= 0            // what the caller must ensure
        ensures result >= x        // what f guarantees in return
    { ... }

    while i < n
    invariant total >= 0           // true before and after each turn
    { ... }

Contract expressions must be pure and may call pure functions.
`result` names the return value in `ensures`.

### 9.2 What "proven" means

When Velaris says a promise is **proven**, it means: for every input
permitted by the `requires`, the `ensures` holds — established by the
Z3 theorem prover before the program runs, using the semantics in this
document, with no execution and no sampling.

When it says a promise **cannot be kept** (E700), it means a
counterexample exists and is shown. This is only reported when the
counterexample involves no summarized calls, so a reported violation is
always literally realisable.

When neither can be established, the promise is **checked at runtime**
instead, and violating it is an error when it happens (E600, E601).
`velaris explain` reports which of the three applies to each function.
The compiler never reports a promise as proven when it was in fact
left to a runtime check.

### 9.3 What is proven, and what is not

Proven today: whole-number and boolean arithmetic; comparisons; loops
(with written invariants, and with inferred bounds on counters);
records, including fields that are lists, floats or text; flat lists
and lists of lists via the theory of arrays; maps, modelled as values
plus which keys are present; quantified list properties through
`all_of` / `any_of`; failure paths, so `ensures` applies to every path
that returns; division and remainder, including that the divisor is
never zero; `Float` in genuine IEEE-754 rather than as real numbers;
`length` and `contains` on text, `upper`/`lower` as length-preserving,
and `split` as producing at least one piece.

Amounts (§4.3) prove as the whole numbers they are: an amount is its
minor units to the prover, so `ensures result >= money(0, "INR")` is
settled the way `result >= 0` is, and `percent_of` is the exact rounding
the interpreter performs, translated for a denominator shown positive.
What a list of amounts adds up to is an unknown the prover is told three
true things about — that nothing adds up to zero, and that items all
`>= 0` (all `<= 0`) add up to something `>= 0` (`<= 0`) — so a promise
that needs more about a sum than those, such as one that needs induction
over the list, is left to runtime rather than claimed. `text_of`,
`parse_money` and `divide_or_fail` are not modelled at all: a function
that uses one keeps its promises as runtime checks.

Not proven, and checked at runtime instead: the contents of text
beyond the above; anything involving values that come back from the
host language; and any obligation the solver cannot settle within its
budget. Loop invariants are inferred only for simple counter bounds;
anything richer must be written.

### 9.4 Calls, and the soundness rule

Calls are proven **modularly**: at a call site the callee's `ensures`
is assumed and its `requires` becomes an obligation on the caller
(E701). A callee's body is never inlined into a caller's proof.

If any premise cannot be translated into the solver's logic, the whole
proof for that function is abandoned and its promises fall back to
runtime checks. Proving with a dropped premise could manufacture a
counterexample that is not real, so it is never done.

### 9.5 Which loops are shown to end

Every loop is given one of two verdicts, by a syntactic rule that
needs no solver and so answers the same with and without the prover:

**terminates** - the condition is, or contains as an `and` conjunct,
`v < E`, `v <= E`, `v > E` or `v >= E` (the counter `v` may stand on
either side), where

- `E` mentions no name the body assigns or binds, and calls only
  functions that read their arguments and touch nothing (`length` and
  the like, or a user function with no effects that cannot fail); and
- every path through the body that reaches its end moves `v` by exactly
  one step toward `E` - `v = v + 1` for `<` and `<=`, `v = v - 1` for
  `>` and `>=` - and `v` is assigned nowhere else in the body, nested
  loops included. A path that leaves through `return` or `fail` leaves
  the loop and needs no step.

**unshown** - every other shape. A step of two, a step on one arm of an
`if` only, a counter reset on some path, a limit the body changes, a
condition with only a flag, an `or` in the condition, a counter moved
inside a nested loop: all unshown, whether or not the loop happens to
end when run.

A `for` loop is a `while` loop by the time the rule runs (the parser
rewrites it; ARCHITECTURE.md) and goes through it unchanged: `for i in a to b` is shown to end unless the body
assigns `i` or changes `b`, and `for x in xs` unless the body assigns
`xs`.

The verdict is reported by `velaris explain` ("loops: 2 terminate, 1 not
shown") and by `velaris audit` (`loops_unshown` per function, and a
warning naming the functions). It is an error only under
`velaris check --strict`, as E612; without the flag a loop whose end is
not shown is not a problem, and the time limit in `velaris.run` remains
the guard against a loop that never ends. The compiler never reports
`terminates` for a shape outside the rule above.

## 10. Modules

    import "std.vel"                 // names merge into this file
    import "lib/geo.vel" as geo      // names live behind geo.

A plain import merges the imported file's functions and records, with
duplicate names rejected. A named import prefixes that file's
functions; the library's internal references are rewritten with it, so
a library behaves identically from the inside. A local name may not
shadow an import name (E514).

Imports are resolved relative to the importing file, with the bundled
standard library searched last. Import cycles are rejected.

### 10.1 Your names and the builtins

A builtin added in **4.3 or later** gives way to a function of the same
name that the program defines: `money`, `units_of`, `with_units`,
`percent_of`, `divide_or_fail`, `text_of` and `parse_money` are the
program's own wherever it declares one. A program written before a
builtin existed therefore keeps meaning exactly what it meant, which is
what lets a minor version add one at all. Inside a library imported
**with a name**, such a call always reaches the builtin: the library's
own functions carry its prefix, and it was not written against the
program importing it.

The builtins that existed before 4.3 keep the precedence they have
always had: a function named like one of those is never reached.

## 11. Compilation and execution

A program is lexed, parsed, effect-checked, type-checked,
proof-checked, then run. Pure functions over `Int`, `Float`, `Bool`,
list reads and text — and, since 2.14, functions whose contracts are
**proven** — may be compiled to machine code through LLVM. Everything
else is interpreted.

Native and interpreted execution are required to produce identical
results. Where they cannot be made identical, the operation is not
compiled: `/` and `%` stay interpreted so that division by zero is a
clean error in both, and results of type `Text` are not returned from
native code because that boundary is platform-specific. A fuzzer
generates random programs and compares both engines on every release.

If the native backend is unavailable or fails for any reason, the
program runs interpreted with the same behaviour.

## 12. The host language

    py(module, function, args)       -> Text
    py_int / py_float                -> Int / Float
    py_json(module, function, args)  -> Text     (JSON in, JSON out)
    py_new(module, function, args)   -> Handle
    py_do(handle, method, args)      -> Text
    py_field(handle, name)           -> Text
    py_close(handle)

All of these require `uses ffi` and all except `py_close` can fail.
Arguments travel as a JSON list; a trailing JSON object becomes
keyword arguments. A value the host returns that is not JSON comes
back as a `Handle`.

Nothing about values crossing this boundary is verified: the prover
treats them as unknown. What the language still guarantees is that
crossing it is **visible** — a function that reaches the host says
`uses ffi`, and a pure function cannot.

## 13. Concurrency

**Velaris is single-threaded, deliberately, and has no concurrency
model.** There are no threads, no async functions, no channels, and no
parallel execution. A program is one sequence of steps.

This is a position, not an oversight. The language's central claim is
that a signature tells you what a function can do; concurrency
introduces effects — data races, interleaving, deadlock — that a
signature of the current design cannot express. Adding threads without
extending the effect system to describe them would break the one
promise the language exists to make.

If concurrency is added, it will be as an effect with rules stated
here first. Until then, a Velaris program that needs parallelism should
get it outside the program: run several, or reach the host language
through `uses ffi` and accept that what happens there is unverified.

## 12a. Function values and capture

An inline function may read locals from the code around it. Those
values are **copied when the function value is made**: the function
carries the numbers, text or records that were there at that moment,
and later assignment to those locals cannot change what it sees. There
are no reference cells, so a function value can never observe a change
it did not receive as an argument.

Effects are unaffected. A function value is still pure - it may not
perform effects, and one that tries is rejected before running - so
capture cannot smuggle behaviour past a signature.

The prover treats captured values as unknown: promises on a capturing
function value fall back to runtime checks rather than being proven.
That is the conservative direction, and a false promise on such a
function is still caught while running.

## 13a. Early loop exit: considered, and answered

Velaris has no `break` or `continue`. An adversarial review argued the
absence *hurts* the invariant story it presumably protects: exiting via
a flag (`while going and i < n`) makes invariants harder to state, not
easier. That criticism is fair, and this section is the considered
answer rather than a shrug.

The reason is the prover's exit knowledge. After `while i < n` with no
early exit, exactly two facts hold: the invariants, and `not (i < n)`.
That negated condition is what lets the prover pin the counter at the
boundary - it is how promises about what a loop built are proven, and
how the final-turn bounds check works. A `break` makes the exit
condition a disjunction of every break site's path condition, and those
paths mention loop-local state the outside cannot see. Every current
loop proof would weaken from "the condition is false" to "the condition
is false OR any break fired", which in practice abandons most of them.

The invariant-friendly alternative is to put the exit in the loop test,
where the prover can see it:

    while i < n and not found {
        ...
    }
    // afterward: not (i < n and not found)
    //   == i >= n or found        - still a usable fact

This costs a Bool and reads slightly worse than `break`. What it buys
is that every promise proven about loops keeps proving. If a future
design finds a way to give `break` the same exit precision - for
example, requiring each break site to state what holds when it fires -
this decision will be revisited in those terms. Until then the answer
is: no, and the flag is the supported idiom.

## 14. Errors

Every error has a stable code (`E###`), a message in plain English, a
file and line, and numbered suggested fixes. `--json` emits them as
structured data. The complete list is generated from the compiler
source itself and published with the documentation.

Codes are grouped: E0xx lexing, E1xx parsing, E2xx names, E3xx
effects, E4xx arity and runtime arithmetic, E5xx types, E6xx runtime
contract violations, E7xx proof results.

## 15. Versioning and stability

Velaris follows semantic versioning. Breaking changes happen only at
major versions; 2.0 made four builtins fallible and the compiler
pointed at every call site that needed updating. Minor versions add;
patch versions fix. [STABILITY.md](STABILITY.md) states what that
covers, the rules for deprecation and for error codes, and the record
of the minor releases that broke the rule anyway, 3.3 and 3.4 among
them. One kind of change is not counted as breaking: a prover that
settles more may refuse a program whose promise, division or list read
it can now show wrong, for the input it names.

The test suite runs on Linux, Windows and macOS, on two Python
versions, with and without the optional solver and native backend, on
every push.

## 16. What this language does not have

Stated plainly, because a specification that only lists strengths is
advertising: no threads or async (§13); no exceptions — failure is in
the signature (§8); no traits, interfaces, classes or inheritance; no
closures — function values cannot capture their surroundings; no
mutable data structures; no reflection; no macros; no operator
overloading; no package registry (libraries are vendored, §10); no
incremental compilation beyond proof caching; and a compiler written
in Python, which is clear to read and slower than a production
compiler.
