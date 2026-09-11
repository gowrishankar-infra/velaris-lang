# The comparison benchmark

Sixty-three small programs, each written three times with the same behaviour -
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
| Velaris 4.1 | `velaris check` (types, effects, unhandled failures, and the prover's E705/E706) and `velaris audit` (which effects, Python modules, paths and hosts the program names, and which loops the termination rule cannot show to end - `loops_unshown`, E612 under `--strict`) | `velaris.run(source, allow=needs, timeout=5, max_memory_mb=256)` - the budget refuses anything the task does not need: an effect (E310), a module (E311), a path outside the granted directory (E313), a host or port outside the grant (E314); the limits stop a runaway (E610/E611) |
| Deno 2.x | `deno check` and `deno lint --json` | `deno run --no-prompt --v8-flags=--max-old-space-size=256 file.js` with no `--allow-*` flag, except in category 11 where the task needs one directory or one host and Deno gets the matching `--allow-read=<dir>` or `--allow-net=<host:port>` |
| Plain Python | nothing, by construction | `python file.py` in a subprocess with the same 5 second timeout and, where the platform allows, the same 256 MB cap |

"Needs" is the effect set the task legitimately requires, stated per
program in `corpus.json`. It is `io` for 59 programs, `io, ffi:math`
for the two control programs that call the host's `sqrt`,
`io, fs:read:<the granted directory>` for 11a and
`io, net:127.0.0.1:<the listener's port>` for 11b; the harness fills
the placeholders. `env` is never a need, so a program that reads the
environment is outside its budget. That is the
Velaris budget for the run; it is also the standard the audit is held to
(see the rules below).

The timeout for Deno and Python is the harness's own `subprocess`
timeout. Velaris's is the `timeout=` argument of `velaris.run`, which
runs the program in a child process it can kill. The difference is who
owns the limit, not whether it fires; the results say which.

Memory caps: Velaris `max_memory_mb` uses the OS address-space limit
(`RLIMIT_AS`) on POSIX and a job object with
`JOB_OBJECT_LIMIT_PROCESS_MEMORY` on Windows: enforced on Linux and on
Windows, best-effort on macOS. Deno gets `--max-old-space-size` on
every platform. Python's child gets `RLIMIT_AS` on Linux and macOS
(best-effort there) and a job object on Windows. The header of
`RESULTS.md` records which applied on the machine that produced it.

## The corpus

Eleven categories: ten of six programs each, and category 11 of three
(added with the scoped budgets of 3.0). In the first ten, programs `a`
to `c` were written first; `d` to `f` were written afterwards, against
the tools, to hide the same defects better. Every dangerous program has one dangerous
line, marked `DANGER` in a trailing comment in all three source files;
the harness reads the marker, so the line numbers in the results cannot
drift from the sources. Control programs have no marker.

| # | Category | Programs |
|---|---|---|
| 1 | a file write hidden inside a helper function | `a_save_report`, `b_two_levels`, `c_log_in_loop`; `d_three_layers`, `e_path_in_record` (the path travels in a record), `f_write_in_condition` (the helper is called from an `if`) |
| 2 | a network call hidden inside a helper | `a_fetch_helper`, `b_post_summary`, `c_quiet_fetch` (swallows every error); `d_two_layers`, `e_is_valid_url` (a predicate that contacts the URL), `f_probe_with_headers` |
| 3 | division by a value from input that can be zero | `a_share_per_person`, `b_bucket_remainder`, `c_per_item_in_main` (in main, on `n - 1`); `d_guarded_one_path` (guarded on one path only), `e_range_width` (`hi - lo`), `f_remainder_in_loop` |
| 4 | an off-by-one read past the end of a list | `a_sum_inclusive`, `b_last_item`, `c_skips_last` (a logic error, see below); `d_empty_input` (only on empty input), `e_pairs` (item and next), `f_index_from_input` |
| 5 | integer overflow | `a_factorial_25`, `b_square_input`, `c_sum_of_cubes`; `d_record_field` (inside a record), `e_map_accumulate` (inside a map), `f_negate_minimum` |
| 6 | an ignored failure | `a_to_int_unhandled`, `b_json_field`, `c_map_lookup`; `d_inside_lambda` (inside an inline function), `e_pop_empty`, `f_json_parse` |
| 7 | an infinite loop | `a_never_advances`, `b_steps_past`, `c_slow_but_finite` (finite - a control row, see below); `d_ends_on_input` (ends only when input says so), `e_reset_in_if`, `f_wrong_sign` |
| 8 | runaway memory growth | `a_rows_forever`, `b_log_kept_in_memory`, `c_split_rows`; `d_text_concat` (repeated concatenation), `e_map_growth`, `f_two_layer_log` |
| 9 | reaching a dangerous module | `a_subprocess_helper`, `b_os_system`, `c_command_on_stdout` (see below); `d_via_py_json` (through the JSON-shaped call), `e_via_handle`, `f_os_listdir` |
| 10 | a plain correct program that must not be flagged | `a_expense_total`, `b_word_count`, `c_sqrt_via_math`; `d_warning_text` (prints "rm -rf" harmlessly), `e_reads_own_args`, `f_math_in_loop` (a counted loop and `ffi:math`) |
| 11 | a grant narrower than the effect (3.0) | `a_read_outside` (granted one directory, reads a file outside it - the path comes on stdin), `b_other_host` (granted one host and port, requests another port - the URL comes on stdin), `c_secret_from_env` (prints an environment variable the harness set) |

Two programs are there because Velaris cannot catch them, so that the
table is not a list of things the language was built to do:

- `04c c_skips_last` - the loop stops one item early. No read is out of
  range and there is no contract, so a wrong total looks like a right
  one.
- `09c c_command_on_stdout` - prints `rm -rf build` as a hint for the
  caller and touches nothing. The only effect is `io`, which the task
  needs. A caller that pipes stdout into a shell runs it, and nothing
  in the program can know that. `10d d_warning_text` prints the same
  words in a warning and is harmless; no tool can tell the two apart
  from the outside, which is why 09c should not be caught by any of
  them.

A third, `07c c_slow_but_finite`, was a miss in the first version of
this benchmark: two nested loops where one multiplication would do,
finishing under the deadline. Velaris 2.62 shows before running that
every loop in it ends (SPEC.md section 9.5), so it is now recorded as a
control row inside category 7 - slow, not dangerous - and a tool that
flags it scores a false positive.

Category 10, and the control row in category 7, are there so that a
tool that flags everything scores badly.

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
modules) a module outside that list, or reports `loops_unshown > 0` (a
loop the termination rule cannot show to end; E612 under `check
--strict`), the audit counts as flagging the program. For a control
program, any problem, any effect beyond its needs, or any loop not
shown to end is a false positive - so a control program with a loop
must write it in the one shape the rule accepts, and 07c and 10f do.

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
the path that names the program and the tool; for a module call,
whether the child's sentinel line (`spawned-child-ran`) or the marker
the program prints when the call came back (`module-reached`) reached
stdout. Category 11 adds three: whether the content of the file
outside the granted directory (`outside-secret`) reached stdout,
whether the *second* listener - the host no task needs - received a
request, and whether the value of `BENCH_SECRET`, which the harness
puts in every child's environment, reached stdout. If it happened, the
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

A full run takes five to eight minutes; most of it is the 5 second
timeouts in categories 7 and 8. The harness starts two listeners on
`127.0.0.1` (one granted, one not), creates a granted directory and a
file outside it under a scratch directory, and sets `BENCH_SECRET` for
its children; all of it is removed afterwards.

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

    velaris check benchmark/corpus/07_infinite_loop/a_never_advances.vel --strict   # E612

The programs read their input from stdin rather than from `args()`;
stdin behaves the same in all three languages. (Until 2.62 the Velaris
command line also handed the budget words to `args()`; that is fixed,
and 10e reads its arguments to show it.)

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
output; that is checked before each release (ten consecutive runs).
One thing had to be normalised for that to hold: in category 8 the
256 MB cap and the 5 second deadline race, and for Deno and Python
which one fires first changes with the machine's load. The verdict is
the same either way, so those cells record that the program was
stopped and not by which limit. The Velaris cell keeps its code (E610
or E611), which is stable because its child process reports it.
