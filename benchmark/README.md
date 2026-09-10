# The comparison benchmark

Thirty small programs, each written three times with the same behaviour -
in Velaris, in JavaScript for Deno, and in Python - and one harness that
runs every program through every tool and records what was caught before
running, what was caught while running, and what was missed. The result
is `RESULTS.md` and `results.json`, regenerated with one command:

    python benchmark/run.py

Nothing in the harness is tuned per program. The same budget, the same
timeout, the same memory cap and the same observation checks apply to
every row. If you think a row is wrong, the program, the rule and the
command that produced it are all here; change one and rerun.

## What is being compared

| Tool | Before running | While running |
|---|---|---|
| Velaris 2.61 | `velaris check` (types, effects, unhandled failures, and the prover's E705/E706) and `velaris audit` (which effects and which Python modules the program reaches) | `velaris.run(source, allow=needs, timeout=5, max_memory_mb=256)` - the effect budget refuses anything the task does not need (E310/E311); the limits stop a runaway (E610/E611) |
| Deno 2.x | `deno check` and `deno lint --json` | `deno run --no-prompt --v8-flags=--max-old-space-size=256 file.js` with no `--allow-*` flag at all, because no program in this corpus legitimately needs one |
| Plain Python | nothing, by construction | `python file.py` in a subprocess with the same 5 second timeout and, where the platform allows, the same 256 MB cap |

"Needs" is the effect set the task legitimately requires, stated per
program in `corpus.json`. It is `io` for 29 programs and `io, ffi:math`
for the one control program that calls the host's `sqrt`. That is the
Velaris budget for the run; it is also the standard the audit is held to
(see the rules below).

The timeout for Deno and Python is the harness's own `subprocess`
timeout. Velaris's is the `timeout=` argument of `velaris.run`, which
runs the program in a child process it can kill. The difference is who
owns the limit, not whether it fires; the results say which.

Memory caps: Velaris `max_memory_mb` uses the OS address-space limit,
enforced on Linux and macOS and recorded but not enforced on Windows
(the compiler's documented limitation). Deno gets `--max-old-space-size`
on every platform. Python's child gets `RLIMIT_AS` on Linux (macOS may
ignore it) and a job object on Windows. The header of `RESULTS.md`
records which applied on the machine that produced it.

## The corpus

Ten categories, three programs each. Every program has one dangerous
line, marked `DANGER` in a trailing comment in all three source files;
the harness reads the marker, so the line numbers in the results cannot
drift from the sources. Control programs have no marker.

| # | Category | Programs |
|---|---|---|
| 1 | a file write hidden inside a helper function | `a_save_report`, `b_two_levels` (two calls deep), `c_log_in_loop` |
| 2 | a network call hidden inside a helper | `a_fetch_helper`, `b_post_summary` (sends data out), `c_quiet_fetch` (swallows every error) |
| 3 | division by a value from input that can be zero | `a_share_per_person` (`/` in a helper), `b_bucket_remainder` (`%` in a helper), `c_per_item_in_main` (`/` in main on `n - 1`) |
| 4 | an off-by-one read past the end of a list | `a_sum_inclusive` (`<=` for `<`), `b_last_item` (`xs[len]`), `c_skips_last` (stops one early - a logic error, see below) |
| 5 | integer overflow | `a_factorial_25`, `b_square_input` (4000000001²), `c_sum_of_cubes` |
| 6 | an ignored failure | `a_to_int_unhandled`, `b_json_field` (missing key), `c_map_lookup` (missing key) |
| 7 | an infinite loop | `a_never_advances`, `b_steps_past` (even counter, odd target), `c_slow_but_finite` (see below) |
| 8 | runaway memory growth | `a_rows_forever`, `b_log_kept_in_memory`, `c_split_rows` |
| 9 | reaching a dangerous module | `a_subprocess_helper`, `b_os_system` (`child_process` in JavaScript), `c_command_on_stdout` (see below) |
| 10 | a plain correct program that must not be flagged | `a_expense_total`, `b_word_count`, `c_sqrt_via_math` (declares `ffi:math`) |

Three programs are there because Velaris cannot catch them, so that the
table is not a list of things the language was built to do:

- `04c c_skips_last` - the loop stops one item early. No read is out of
  range and there is no contract, so a wrong total looks like a right
  one.
- `07c c_slow_but_finite` - two nested loops where one multiplication
  would do. It ends before the deadline, and a finite loop that ends is
  indistinguishable from useful work to a timeout.
- `09c c_command_on_stdout` - prints `rm -rf build` as a hint for the
  caller and touches nothing. The only effect is `io`, which the task
  needs. A caller that pipes stdout into a shell runs it, and nothing
  in the program can know that.

Category 10 is there so that a tool that flags everything scores badly.

The inputs are chosen to trigger the defect: `0` for the divisors, `1`
where the divisor is `n - 1`, `12a` for the parse, a document without
the field, a key that is not in the map, `4000000001` for the square.
Python's crashes in categories 3 and 6 depend on that choice; with
ordinary input those programs run clean. Velaris's E520/E705/E706 are
independent of the input, which is the point of the comparison, and the
results paragraph says so.

Every program that takes input reads exactly one line from stdin. The
file-write programs read the path to write; the network programs read
the URL to reach. Both point at things the harness owns (a scratch
directory, a listener on `127.0.0.1`), so no run touches the real
network, and the harness can observe whether the effect happened.

## The verdicts

One per program per tool:

| Verdict | Meaning |
|---|---|
| `caught-before-run` | a static step flagged the dangerous line or the dangerous effect before anything ran |
| `caught-during-run` | the run was refused, stopped or crashed, and the dangerous effect did not happen |
| `missed` | the program ran to the end, or the dangerous effect happened |
| `not-applicable` | a control program: nothing to catch, and nothing was flagged |
| `false-positive` | a control program that a tool flagged or stopped |
| `tool-absent` | the tool is not installed on this machine |

`false-positive` is not in the vocabulary the benchmark was specified
with; it was added because without it the control group could not
score against anything.

### Exact rules

**Velaris, before running.** `velaris.check(source)` is called with the
prover on. A problem on the dangerous line counts. A problem on any
other line is a corpus error and the harness exits 2 - a program that
does not compile for an unrelated reason is a bug in this benchmark,
not a data point. Then `velaris.audit(source)`: if it lists an effect
that `needs` does not include, or (when `needs` grants `ffi:` for named
modules) a module outside that list, the audit counts as flagging the
program. For a control program, any problem or any effect beyond its
needs is a false positive.

**Velaris, while running.** Only when check passed:
`velaris.run(source, allow=needs, stdin=..., timeout=5, max_memory_mb=256)`.
`ok=False` for any reason - a refused effect (E310/E311), a timeout
(E610), the memory cap (E611), a runtime error such as E403 or E407 -
counts as stopped.

**Deno, before running.** `deno check file.js` and `deno lint --json
file.js`. A diagnostic counts if it is on the dangerous line, or, when
the dangerous line is inside a loop, on that loop's header line or on
the first statement after the loop (that is where `no-unreachable`
lands for a `while (true)`, and it does say the loop never exits). A
diagnostic anywhere else is recorded in the evidence but not credited;
for instance `prefer-const` on the counter of `07a` is not credited,
because the same warning appears on ordinary code that reassigns
nothing. For a control program any diagnostic is a false positive.

**Deno, while running.** `deno run --no-prompt
--v8-flags=--max-old-space-size=256 file.js`. A non-zero exit or the
harness timeout counts as stopped. Permission denials under
`--no-prompt` exit 1 with `NotCapable`.

**Python.** `python file.py`. There is no static step. A non-zero exit
or the harness timeout counts as stopped.

**Observation.** After every run the harness checks whether the
dangerous effect actually happened: for a file write, whether the file
exists; for a network call, whether its listener received a request on
the path that names the program and the tool; for a spawned process,
whether the child's sentinel line reached stdout. If it happened, the
verdict is `missed` whatever the exit status. If it did not happen and
the process exited 0 anyway, the verdict is `caught-during-run` with the
evidence saying the denial was swallowed - this is what happens in Deno
when a program wraps `fetch` in `try/catch`, because a permission error
there is an ordinary exception. A Velaris refusal cannot be caught by
the program.

**Precedence.** A program caught before running is recorded as
`caught-before-run` even if the run would also have stopped it; the
evidence column shows both where both happened.

## Running it

    python benchmark/run.py               # everything; writes RESULTS.md and results.json
    python benchmark/run.py --quick       # one program per category, table on stdout
    python benchmark/run.py --only 03a,10c
    python benchmark/run.py --check       # exit 1 if any verdict differs from results.json
    python benchmark/run.py --deno /path/to/deno

It needs the checkout (it imports `velaris.py` from the repository
root), Python 3.10 or newer, and for the Velaris column to mean what
the results say, the prover: `pip install ".[full]"`. Without `z3`
the E705/E706 rows become runtime checks and the header of `RESULTS.md`
says the prover was absent.

Deno is found on `PATH`, in `~/.deno/bin`, in `$DENO_INSTALL/bin`, or
where winget puts it on Windows. If it is not found every Deno cell
reads `tool-absent`, the header says so, and the run still completes.
On Windows: `winget install DenoLand.Deno`. Elsewhere see deno.com.

A full run takes two to four minutes; most of it is the 5 second
timeouts in categories 7 and 8.

Continuous integration runs `python benchmark/run.py --quick --check`
on the legs that install the prover, with Deno absent there.

## Reproducing a single cell by hand

The harness uses the library calls; these are the command-line
equivalents.

    velaris check benchmark/corpus/03_div_zero/a_share_per_person.vel --json
    velaris audit benchmark/corpus/01_file_write/a_save_report.vel
    echo /tmp/out.txt | velaris benchmark/corpus/01_file_write/a_save_report.vel --allow io
    echo /tmp/out.txt | deno run --no-prompt benchmark/corpus/01_file_write/a_save_report.js
    echo /tmp/out.txt | python benchmark/corpus/01_file_write/a_save_report.py

The command line has no `--timeout`; for that use the library:

    python -c "import velaris; print(velaris.run(open('benchmark/corpus/07_infinite_loop/a_never_advances.vel').read(), allow={'io'}, timeout=5).as_dict())"

The programs read their input from stdin rather than from `args()`
because under `--allow` the Velaris command line hands the budget words
to `args()` as well (`['--allow', 'io', ...]` in 2.60); stdin behaves
the same in all three languages.

## Disputing a row

- The program is not equivalent across languages: edit it. The three
  files sit side by side under `corpus/<category>/`.
- The dangerous line is wrong: move the `DANGER` marker.
- A rule is unfair: it is one function in `run.py` (`verdict_for`, the
  `*_row` functions, `observed`), and the evidence column records the
  raw facts the rule was applied to, so the same `results.json` can be
  re-read under a different rule.
- A verdict changed between compiler versions: `--check` exits 1 and
  names the row.

Both files are regenerated from scratch on every run and carry no
timestamps, so two runs on the same machine should produce identical
output; that is checked before each release.
