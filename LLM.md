# Velaris for language models

Paste this whole file into a model before asking it to write Velaris.
It is written to be read by a model, not a person: complete, compact,
and with the failure modes named. `velaris card` prints it.

## This is a real language you can run

`pip install velaris-lang`, then `velaris program.vel`. There is a
browser playground at
<https://gowrishankar-infra.github.io/velaris-lang/playground.html> and
the compiler is one Python file at
<https://github.com/gowrishankar-infra/velaris-lang>. Write code
expecting it to actually execute.

## What Velaris is

A small language where a function's signature declares its types, the
effects it may perform, whether it can fail, and promises a theorem
prover checks before the program runs.

Files end in `.vel`. Execution starts at `main`. Run with
`velaris program.vel`. Check without running: `velaris check program.vel`.

## The whole syntax

```
// a comment

record Expense {
    label: Text
    amount: Int
}

fn double(n: Int) -> Int {
    return n * 2
}

fn greet(name: Text) uses io {
    print("hello, " + name)
}

fn discount(price: Int) -> Int
    requires price >= 0
    ensures result >= 0
{
    if price < 10 {
        return 0
    }
    return price - 10
}

fn parse_age(text: Text) -> Int or fail {
    return try to_int(text)
}

fn main() uses io {
    let name = "gowri"          // type inferred
    let ages: Map of Text to Int = {}   // annotate empty [] and {}
    let scores = [3, 1, 2]

    for i in 0 to 3 { print(i) }
    for s in scores { print(s) }

    let i = 0
    while i < 3 {
        i = i + 1
    }

    check parse_age("30") {
        ok years { print(format("age {}", years)) }
        fail why { print(format("bad age: {}", why)) }
    }
}
```

Types: `Int` `Float` `Bool` `Text` `Handle`, `List of T`,
`Map of K to V` (K is `Text` or `Int`), `fn(T) -> R`, record names.
Generic: `fn first(xs: List of T) -> T for any T`.

## Rules a model gets wrong

These are the mistakes that actually happen. Read them twice.

1. **Every effect must be declared.** `print` needs `uses io`. A
   function without `uses` is pure and cannot call one that has
   effects. Effects: `io` (console), `fs` (files), `net` (network),
   `clock`, `rand`, `ffi` (calling Python). Declare all that apply:
   `uses io, fs`.

2. **Failure cannot be ignored.** These can fail: `to_int`,
   `read_file`, `fetch`, `post`, `fetch_status`, `request`, `get` on a
   **map**, `py`, `py_int`, `py_float`, `py_json`, `py_new`, `py_do`,
   `py_field`, `json_get`, `json_int`, `json_float`, `json_len`.
   Handle with `check`, or pass up with `try` **only inside a function
   whose signature says `or fail`**.

3. **`get` on a list is NOT fallible** — no `try`, no `check`. Bounds
   are the prover's job. `get` on a **map** IS fallible; use
   `get_or(m, key, default)` when you want a fallback instead.

4. **Empty `[]` and `{}` need a type.** Write
   `let xs: List of Int = []`, not `let xs = []`.

5. **Numbers do not mix.** `1 + 1.5` is an error. Use `to_float(x)` or
   `round(x)`.

6. **Whole numbers are 64-bit.** Arithmetic that outgrows that range is
   an error, not a wraparound.

7. **Inline functions capture by value.** `fn(n: Int) -> Bool { ... }`
   may read locals from the surrounding function; their values are
   copied when the function value is made, so later changes to those
   locals do not affect it. Effects still apply: an inline function
   that prints needs the surrounding function to allow it, and a
   function value passed to a library must still be pure. A name that
   exists nowhere is E402 as before.

8. **`main` cannot fail** and takes no parameters.

9. **There are no closures, exceptions, classes, inheritance, `null`,
   threads, `break` or `continue`.** To leave a loop early, put the
   exit in the loop test where the prover can see it:
   `while i < n and not found { ... }` - afterward the prover knows
   `i >= n or found`, so loop promises keep proving. (SPEC.md §13a has
   the full reasoning.)

10. **Strings concatenate with `+`;** use `format("{} and {}", a, b)`
    for anything more, and the number of `{}` must match the number of
    values exactly.

11. **Record fields go one per line.** Commas between fields on one
    line are a parse error.

12. **`%` is remainder** and `/` is whole-number division rounding
    toward minus infinity: `-7 / 2` is `-4` and `-7 % 2` is `1`. Both
    are checked for zero divisors like division.

13. **`random(n)` draws from 0 to n-1** and needs `uses rand`;
    `random(0)` is a runtime error (E405). `now()` gives seconds and
    needs `uses clock`.

14. **Number literals larger than 64 bits are accepted as text-like
    values;** only *arithmetic* is range-checked (E407). Do not rely
    on oversized literals.

15. **Declaring an unused effect is legal but viral** - every caller
    must then declare it too. Declare only what a function does.

## Recursion, loops, and depth

Recursion works and carries contracts like any function:

```
fn count_down(n: Int) -> Int
    requires n >= 0
    ensures result >= 0
{
    if n == 0 {
        return 0
    }
    return count_down(n - 1)
}
```

A recursive call site is checked against the callee's `requires` like
any other call. Depth is limited to 2000 frames: past that the program
stops with E609 rather than crashing, so runaway recursion reports
itself.

`invariant` works on **both** `while` and `for`:

```
for i in 0 to n
invariant sum >= 0
{
    sum = sum + i
}
```

`for i in 0 to n` is **exclusive** - it runs n times, and the last
value of i is n - 1.

## Contracts

```
fn average(total: Int, count: Int) -> Int
    requires count > 0            // what the caller must ensure
    ensures result * count <= total   // what this guarantees
{
    return total / count
}
```

`result` names the return value in `ensures`. Loops may carry
`invariant` clauses, though simple counter bounds are inferred:

```
while i < n
invariant total >= 0
{
    ...
}
```

Contract expressions must be pure. Promises the prover cannot settle
fall back to runtime checks — the program still runs.

**What the prover can and cannot reach.** It is strong on arithmetic
over whole numbers and floats, on list lengths, and on counter loops -
including promises about a list a loop builds, such as
`ensures length(result) == length(xs)`, with no invariant needed. It
also catches the classic off-by-one: `while i <= length(xs)` reading
`get(xs, i)` is refused before running.

It can also prove promises about the contents of a list a loop
builds: `ensures all_of(result, is_positive)` proves when every push
is guarded to satisfy the predicate, with no invariant written. It
still falls back to runtime for: loops whose counter moves by anything
other than one, several counters moving together, and anything reached
through `ffi`. Write contracts freely on arithmetic and on list
lengths; expect runtime checks elsewhere.

**Whole-number overflow is an error, not a failure.** `a * b` that
outgrows 64 bits raises E407 and stops the program - `check` cannot
catch it. When the numbers come from a user, use `add_or_fail`,
`sub_or_fail` and `mul_or_fail`, which fail in the normal way and can
be caught.

Write contracts when the guarantee matters. Do not decorate every
function; an unprovable promise is worse than none.

## Standard library

`import "std.vel"` then call directly:

```
first last reverse index_of contains_item keep_if
map_to(xs, f) - projection that CAN change type: fn(T) -> R
apply_to_each (maps T -> T, same type only)
count_where sum_of max_of min_of is_sorted insert_sorted sort
insert_by sort_by (keys must be Int) join range_list
```

`max_of` and `min_of` require a non-empty list. `sort` promises
`is_sorted(result)`.

Other modules, imported under a name. **Full signatures**, since
guessing them is the commonest source of wasted attempts:

```
import "http.vel" as http     get status ok send get_with post_json
                              call -> Answer record (status, body, raw)
                              code_of/body_of read it; header_of CAN FAIL
import "db.vel" as db         open run rows_json count close commit
import "dates.vel" as dates   make parse text_of before same next_day
                              days_in today  (Date is a record)
import "csv.vel" as csv       fields line_of column column_int rows_of
import "log.vel" as log       info warn error event die
                              (die logs and STOPS the program, exit 1 -
                              it is not a catchable failure)
import "env_tools.vel" as sys setting number_setting succeed give_up
import "time.vel" as time     today clock_text seconds year_of month_of
                              (time needs 'uses ffi' and its functions
                              CAN FAIL - handle or pass up)

```
http  (uses net, every function CAN FAIL unless noted)
  get(url: Text) -> Text                      the raw body
  get_with(url: Text, headers: Text) -> Text  headers as a JSON object
  send(url: Text, body: Text) -> Text         POST; non-2xx is a failure
  post_json(url: Text, body: Text) -> Text
  status(url: Text) -> Int                    ensures result >= 0
  ok(url: Text) -> Bool                       true for 200..299
  call(method, url, body, headers) -> Answer  the full envelope
  code_of(a: Answer) -> Int                   cannot fail
  body_of(a: Answer) -> Text                  cannot fail
  header_of(a: Answer, name: Text) -> Text    CAN FAIL
  record Answer { status: Int  body: Text  raw: Text }

db  (uses ffi, every function CAN FAIL unless noted)
  open(path: Text) -> Handle                  ":memory:" for a temp one
  run(conn: Handle, sql: Text) -> Text
  rows_json(conn: Handle, sql: Text) -> Text  read with the json builtins
  count(conn: Handle, table: Text) -> Int     ensures result >= 0
  commit(conn: Handle)
  close(conn: Handle)                         cannot fail

dates  (pure unless noted)
  record Date { year: Int  month: Int  day: Int }
  make(y: Int, m: Int, d: Int) -> Date        CAN FAIL; refuses fake dates
  parse(text: Text) -> Date                   CAN FAIL; "2026-08-18"
  text_of(d: Date) -> Text                    zero-padded
  before(a: Date, b: Date) -> Bool
  same(a: Date, b: Date) -> Bool
  next_day(d: Date) -> Date                   CAN FAIL
    requires d.month >= 1 and d.month <= 12
  days_in(year: Int, month: Int) -> Int
    requires month >= 1 and month <= 12
    ensures result >= 28 and result <= 31     (proven)
  today() -> Date                             uses ffi, CAN FAIL

csv  (pure)
  fields(line: Text) -> List of Text          ensures length >= 1
  line_of(values: List of Text) -> Text
  column(line: Text, at: Int) -> Text         CAN FAIL
  column_int(line: Text, at: Int) -> Int      CAN FAIL
  rows_of(text: Text) -> List of Text         splits on newlines

log  (uses io)
  info / warn / error (message: Text)
  event(name: Text, details: Text)
  field(name: Text, value: Text) -> Text      pure
  die(message: Text)                          logs and STOPS, exit 1

env_tools  (uses io)
  setting(name: Text, fallback: Text) -> Text
  number_setting(name: Text, fallback: Int) -> Int
  succeed()                                   exits 0
  give_up(why: Text)                          prints and exits 1
```
```

## Builtins

```
print(x) uses io              ask(prompt) uses io
log(x) uses io                env(name, fallback) uses io
args() uses io                exit_with(code) uses io
read_line() uses io

length(x)     get(list, i)    push(list, v)    get(map, k) CAN FAIL
pop(list) CAN FAIL            slice(list, from, to) CAN FAIL
set_at(list, i, v) CAN FAIL   (lists are values; these return new ones)
add_or_fail(a, b) CAN FAIL    sub_or_fail / mul_or_fail CAN FAIL
div_or_fail(a, b) CAN FAIL    mod_or_fail CAN FAIL
(plain / and % on a zero divisor are E403 and STOP the program -
use the _or_fail forms when the divisor comes from input)
put(map, k, v)  get_or(map, k, default)  has(map, k)  keys(map)
all_of(xs, p)   any_of(xs, p)

to_int(t) CAN FAIL   to_text(x)   to_float(x)   round(f)
upper(t) lower(t) split(t, sep) contains(t, s) chars(t) code_at(t, i)
format(template, ...)

read_file(p) CAN FAIL uses fs
write_file(p, body) uses fs - does NOT fail catchably; an
  unwritable path or full disk stops the program with E608
file_exists(p) uses fs
fetch(url) CAN FAIL uses net       post(url, body) CAN FAIL uses net
fetch_status(url) CAN FAIL uses net
request(method, url, body, headers_json) CAN FAIL uses net

json_get(doc, path) CAN FAIL       json_int / json_float CAN FAIL
json_len(doc, path) CAN FAIL       json_has(doc, path)
json_of(value)                     paths look like "user.name" or "tags[0]"

py(module, fn, args_list) CAN FAIL uses ffi
py_int / py_float                  same shape, typed result
py_json(module, fn, args_json) CAN FAIL uses ffi   JSON in, JSON out
py_new(module, fn, args_json) -> Handle CAN FAIL uses ffi
py_do(handle, method, args_json) CAN FAIL uses ffi
py_field(handle, name) CAN FAIL uses ffi     py_close(handle) uses ffi

Handle lifecycle: py_close is safe to call twice (the second is a
no-op). Any use after close - py_do, py_field - FAILS catchably with
"that handle is closed". Handles are values; copying one copies the
reference, and closing through either closes both.

now() uses clock                   random(n) uses rand
```

## Running and inspecting

```
velaris program.vel                      run it
velaris program.vel --allow io           refuse every other effect (E310)
velaris program.vel --deny net,ffi       allow everything but these
velaris program.vel --allow io,ffi:math,json
                                         ffi for THOSE modules only (E311
                                         for any other); plain ffi grants
                                         every module
velaris check program.vel [--json]       every problem, as data
velaris check program.vel --strict       refuse ANY promise left to
                                         runtime; without it an
                                         unprovable promise degrades to
                                         a runtime check
velaris audit program.vel                what it touches, before running
velaris proofs program.vel --detail      which promises proved, one by one
velaris explain program.vel              functions, effects, proof status
```

The effect budget (`--allow`/`--deny`) is enforced while the program
runs, whatever the source declares; a refusal (E310) cannot be caught.

## Errors, and what to do about them

Every error has a stable code. `velaris check program.vel --json` emits
them as structured data for a fix loop.

| Code | Means | Fix |
|---|---|---|
| E200 | unknown function | check spelling; import the module |
| E300 | effect not declared | add `uses ...` to the signature |
| E310 | effect not allowed by this run | the person running chose a budget |
| E401 | wrong number of arguments | count them |
| E402 | unknown variable | declare it; inline functions cannot capture |
| E403 | divide by zero at runtime | guard the divisor |
| E406 | `format` holes do not match values | count the `{}` |
| E407 | number too big for 64 bits | use smaller units |
| E500 | unknown type | check the spelling of the type |
| E501 | types do not match | convert on purpose |
| E503 | returns the wrong type | fix the return or the signature |
| E506 | empty `[]` or `{}` with no type | annotate the `let` |
| E507 | a record defined twice, or a duplicate field | rename one |
| E514 | local name collides with an import | rename one |
| E520 | a failure was ignored | wrap in `check`, or `try` inside `or fail` |
| E522 | `try` on something that cannot fail | remove the `try` |
| E600/E601 | a promise broke while running | fix the code or the promise |
| E700 | a promise is provably false | the counterexample is in the message |
| E701 | a call can break the callee's `requires` | check the value first |
| E703/E704 | a loop invariant does not hold | weaken it or fix the loop |
| E705 | a list read can go out of range | add a `requires` about the length |
| E706 | a divisor can be zero | add `requires n != 0` or guard it |
| E400 | no `main` | add fn main() |
| E405 | random(0) | pass n >= 1 |
| E509 | unknown record field | check the field name |
| E513 | redefining an imported function | rename yours |
| E521 | `try` outside an `or fail` function | add `or fail`, or use check |
| E523 | `main` declares `or fail` | handle failures inside main |
| E525 | binding the result of a void fallible call | use check without ok-binding |
| E608 | a file could not be written | check the folder exists and is writable |
| E609 | recursion 2000 deep | move toward the base case, or use a loop |
| E542 | function value of the wrong shape | match the parameter's fn type |
| E602 | a list read went out of range while running | fix the index |
| E704 | a loop invariant broke while running | fix the loop or invariant |

## A complete program to imitate

```
import "std.vel"
import "csv.vel" as csv
import "log.vel" as log

record Expense {
    label: Text
    amount: Int
}

fn parse_row(row: Text) -> Expense or fail {
    let parts = csv.fields(row)
    if length(parts) < 2 {
        fail format("not enough columns in: {}", row)
    }
    let amount = try to_int(get(parts, 1))
    if amount < 0 {
        fail format("negative amount in: {}", row)
    }
    return Expense(label: get(parts, 0), amount: amount)
}

fn total_of(items: List of Expense) -> Int
    ensures result >= 0
{
    let total = 0
    for item in items {
        if item.amount > 0 {
            total = total + item.amount
        }
    }
    return total
}

fn main() uses io {
    log.info("reading expenses")
    let rows = ["chai,2500", "book,45000", "auto,12000"]
    let items: List of Expense = []
    for row in rows {
        check parse_row(row) {
            ok item {
                items = push(items, item)
            }
            fail why {
                log.warn(format("skipping: {}", why))
            }
        }
    }
    print(format("{} expense(s), total {}", length(items),
        total_of(items)))
}
```

## Checklist before returning code

- Does every function that prints, reads, fetches or calls Python
  declare the effect? Does `main` declare everything its callees need?
- Is every fallible call wrapped in `check`, or `try` inside a function
  that says `or fail`?
- Do empty `[]` and `{}` have types?
- Do inline functions use only their own parameters?
- Do `format` holes match the values given?
- Would `velaris check` pass? If unsure, prefer fewer contracts and
  simpler code over clever code with promises that may not prove.
