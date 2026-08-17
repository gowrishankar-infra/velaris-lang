#!/usr/bin/env python3
"""Velaris test suite: runs every example and checks its expected verdict.

    python run_tests.py              # uses native compilation if available
    python run_tests.py --no-native  # force full interpretation
"""
import subprocess
import sys
from pathlib import Path

# every example, with its expected verdict
EXPECT = {
    "hello.vel": "RUNS",            "effects.vel": "RUNS",
    "sneaky_fixed.vel": "RUNS",     "loop.vel": "RUNS",
    "contract.vel": "RUNS",         "features.vel": "RUNS",
    "compose.vel": "RUNS",          "bench.vel": "RUNS",
    "loop_proof.vel": "RUNS",
    "list_proof.vel": "RUNS",
    "text_tools.vel": "RUNS",
    "records.vel": "RUNS",
    "uses_import.vel": "RUNS",
    "import_bad.vel": "REJECTED",
    "escapes.vel": "RUNS",
    "floats.vel": "RUNS",
    "maps.vel": "RUNS",
    "failing.vel": "RUNS",
    "funcs.vel": "RUNS",
    "generics.vel": "RUNS",
    "ledger.vel": "RUNS",
    "rec_proof.vel": "RUNS",
    "native_float.vel": "RUNS",
    "qlist_proof.vel": "RUNS",
    "fail_proof.vel": "RUNS",
    "fp_proof.vel": "RUNS",
    "std_tour.vel": "RUNS",
    "builtin_unhandled.vel": "REJECTED",
    "std_bad.vel": "REJECTED",
    "fp_proof_bad.vel": "REJECTED",
    "fail_proof_bad.vel": "REJECTED",
    "qlist_bad.vel": "REJECTED",
    "rec_proof_bad.vel": "REJECTED",
    "generics_bad.vel": "REJECTED",
    "funcs_bad.vel": "REJECTED",
    "failing_bad.vel": "REJECTED",
    "maps_bad.vel": "REJECTED",
    "floats_bad.vel": "REJECTED",
    "many_errors.vel": "REJECTED",
    "records_bad.vel": "REJECTED",
    "loop_proof_bad.vel": "REJECTED",
    "list_proof_bad.vel": "REJECTED",
    "sneaky.vel": "REJECTED",       "caught.vel": "REJECTED",
    "types_bad.vel": "REJECTED",    "loop_bad.vel": "REJECTED",
    "contract_broken.vel": "REJECTED",
    "contract_impure.vel": "REJECTED",
    "list_mixed.vel": "REJECTED",   "list_oob.vel": "REJECTED",
    "proof_catch.vel": "REJECTED",  "callsite_bad.vel": "REJECTED",
}

# scripted keyboard input for interactive examples
STDIN = {
    "ledger.vel": ("add\nchai\n2500\n1\nadd\nbook\n45000\n2\n"
                   "add\nauto\n12000\n2\n"
                   "list\ntotal\nreport\nsave\nload\nreport\n"
                   "add\npen\nabc\nquit\n"),
}


def main() -> int:
    here = Path(__file__).parent
    examples = here / "examples"
    extra = [a for a in sys.argv[1:] if a.startswith("--")]
    expect = dict(EXPECT)
    try:
        import z3  # noqa: F401
    except ImportError:
        # Without the prover, proof_catch's bug is only reachable for
        # years > 30, which its main deliberately never calls - that IS
        # the demo's point. It runs clean under runtime checks.
        expect["proof_catch.vel"] = "RUNS"
        expect["fail_proof_bad.vel"] = "RUNS"
        print("note: z3-solver absent - proof_catch.vel and "
              "fail_proof_bad.vel expected to RUN "
              "(their bugs are only findable by proof)")
    failed = 0
    for name, want in expect.items():
        path = examples / name
        if not path.exists():
            print(f"MISSING   {name}")
            failed += 1
            continue
        r = subprocess.run(
            [sys.executable, str(here / "velaris.py"), str(path)] + extra,
            capture_output=True, text=True, timeout=300,
            input=STDIN.get(name))
        got = "RUNS" if r.returncode == 0 else "REJECTED"
        ok = got == want
        print(f"{'PASS' if ok else 'FAIL':4}  {name:22} expected {want:8} got {got}")
        if not ok:
            failed += 1
    total = len(EXPECT)
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
