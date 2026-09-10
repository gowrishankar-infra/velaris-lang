# Hall of fame

People and models who made Velaris report something false, or found a
way past what it claimed, and so made it better. The standing
challenge that adds to this list is in [SECURITY.md](SECURITY.md):
credit here and in the changelog, and a fix within a week. There is no
money.

Each line: who, when, what they found. The details are in the
CHANGELOG.md entry named.

## Adversarial reviews by model, August 2026

Three model families - a Gemini model, a ChatGPT model and a Claude
model - each read `velaris card`, wrote programs, and then set out to
break the language. The changelog entries below record what each
review found; they did not record which family produced which review,
and this file does not guess. The maintainer can attach the names to
the lines.

- **First card review** - 2026-08-18 - the first program a model wrote
  from the card was correct and crashed the prover: a record pushed
  onto a list inside a `check` inside a loop reached a comparison that
  assumed every value has a Z3 sort (2.41.1). The same day a second
  model removed a `requires length(items) > 0` guard from its own
  expense report and predicted the compiler would catch the division;
  it did not - the divide-by-zero proof was skipping itself whenever a
  loop had touched the path (2.41.2).
- **Install-and-attack review** - 2026-08-19 - a 30-function
  calculator that compiled and ran first try, then a list of what was
  missing or wrong: no way to shrink a list (`pop`, `slice`, `set_at`
  were added, and were then found to be unenforced - see the next
  line), overflow that no `check` could catch (`add_or_fail` and
  friends), a `break` that reported "unknown variable", a formatter
  that contradicted the documentation, and the prover going blind
  when a loop mutates a list - which was documented as a limit rather
  than fixed (2.42).
- **86-artifact review** - 2026-08-19 - one production program, 34
  broken fragments and 52 single-point mutations, scored 76/100, and
  found the soundness hole of that month: `pop`, `slice` and `set_at`
  were documented fallible but the checker never demanded handling,
  so a clean `velaris check` could be followed by a raw traceback. Also
  a checker that could crash instead of reporting, `main` validated
  only at runtime, and a typed FFI that sent numbers as text (2.44;
  `check_fallible.py` exists because of this review). A third pass by
  the same review held the score at 88 and found five more at the
  edges - a zero divisor from input that no `check` could see, an
  HTTP envelope that was text instead of a record, a `fail_with` that
  did not fail (2.47).

## Automated review, September 2026

- **The CrewAI pull request's review bot** - 2026-09-10 - flagged
  what three human reviews had also noted and the project kept
  deferring: nothing bounded how long a program could run or how much
  memory it could take. `timeout=` and `max_memory_mb=` in
  `velaris.run` are the result (2.59).
