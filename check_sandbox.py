#!/usr/bin/env python3
"""The runtime must refuse effects the person running did not allow.

The compiler checks that a function declares what it does. This checks
the other half: that `--allow` and `--deny` are enforced while the
program runs, whatever the source claims about itself - so someone can
run a program they have not read.

Needs no theorem prover: every case here is about the runtime, so this
behaves identically with and without z3.

    python check_sandbox.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
VELARIS = HERE / "velaris.py"
SCRATCH = HERE / "_sandbox_check.vel"
WROTE = HERE / "_sandbox_wrote.txt"

REFUSED = ("E310", "E311")

# (name, flags, source, a file it must not manage to create)
CASES = [
    ("reading a file", ["--allow", "io"], '''
fn peek(path: Text) -> Text uses fs or fail {
    return try read_file(path)
}

fn main() uses io, fs {
    check peek("velaris.py") {
        ok body {
            print("READ IT")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
    ("writing a file", ["--allow", "io"], '''
fn main() uses io, fs {
    write_file("_sandbox_wrote.txt", "escaped")
    print("WROTE IT")
}
''', WROTE),
    ("reaching the network", ["--allow", "io"], '''
fn main() uses io, net {
    check fetch_status("https://example.com") {
        ok code {
            print("REACHED IT")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
    ("calling Python", ["--allow", "io"], '''
fn main() uses io, ffi {
    check py("os", "getcwd", ["x"]) {
        ok out {
            print("CALLED IT")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
    ("opening a database through a handle", ["--allow", "io"], '''
fn main() uses io, ffi {
    check py_new("sqlite3", "connect", "[\\":memory:\\"]") {
        ok conn {
            print("OPENED IT")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
    ("asking the clock", ["--allow", "io"], '''
fn main() uses io, clock {
    print(now())
}
''', None),
    ("asking for randomness", ["--allow", "io"], '''
fn main() uses io, rand {
    print(random(6))
}
''', None),
    ("hiding the effect behind a helper", ["--allow", "io"], '''
fn helper(path: Text) -> Int uses fs or fail {
    let body = try read_file(path)
    return length(body)
}

fn wrapper(path: Text) -> Int uses fs or fail {
    return try helper(path)
}

fn main() uses io, fs {
    check wrapper("velaris.py") {
        ok n {
            print("GOT THROUGH")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
    ("catching the refusal to carry on anyway", ["--allow", "io"], '''
fn peek(path: Text) -> Text uses fs or fail {
    return try read_file(path)
}

fn main() uses io, fs {
    check peek("velaris.py") {
        ok body {
            print("READ IT")
        }
        fail why {
            print("SWALLOWED THE REFUSAL")
        }
    }
    print("CARRIED ON")
}
''', None),
    ("denying one effect while allowing the rest",
     ["--deny", "fs"], '''
fn main() uses io, fs {
    write_file("_sandbox_wrote.txt", "escaped")
    print("WROTE IT")
}
''', WROTE),
    ("reaching a module outside the ffi allow-list",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    let none: List of Text = []
    check py("os", "getcwd", none) {
        ok d {
            print("GOT THROUGH")
        }
        fail w {
            print("failed")
        }
    }
}
''', None),
    ("dodging the allow-list with a submodule path",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    let none: List of Text = []
    check py("os.path", "getcwd", none) {
        ok d {
            print("GOT THROUGH")
        }
        fail w {
            print("failed")
        }
    }
}
''', None),
    ("dodging the allow-list through py_json",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    check py_json("subprocess", "getoutput", "[\\"echo GOT THROUGH\\"]") {
        ok d {
            print("GOT THROUGH")
        }
        fail w {
            print("failed")
        }
    }
}
''', None),
    ("dodging the allow-list through a handle",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    check py_new("subprocess", "Popen", "[[\\"echo\\"]]") {
        ok h {
            print("GOT THROUGH")
        }
        fail w {
            print("failed")
        }
    }
}
''', None),
    ("denying several at once", ["--deny", "fs,net,ffi"], '''
fn main() uses io, net {
    check fetch_status("https://example.com") {
        ok code {
            print("REACHED IT")
        }
        fail why {
            print("failed")
        }
    }
}
''', None),
]

# things that must still work: a budget must not break honest programs
ALLOWED = [
    ("pure work with no permission at all", ["--allow", ""], '''
import "std.vel"

fn total(n: Int) -> Int
    requires n >= 0
    ensures result >= 0
{
    let sum = 0
    for i in 0 to n {
        sum = sum + i
    }
    return sum
}

fn main() {
    let answer = total(10)
    let sorted = sort([3, 1, 2])
}
''', ""),
    ("printing when io is allowed", ["--allow", "io"], '''
fn main() uses io {
    print("hello")
}
''', "hello"),
    ("the clock when clock is allowed", ["--allow", "io,clock"], '''
fn main() uses io, clock {
    if now() > 0 {
        print("time moves")
    }
}
''', "time moves"),
    ("an allowed module works under the allow-list",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    check py_float("math", "sqrt", ["16"]) {
        ok r {
            print("root ok")
        }
        fail w {
            print(w)
        }
    }
}
''', "root ok"),
    ("everything when nothing is restricted", [], '''
fn main() uses io, clock, rand {
    if now() > 0 and random(6) >= 0 {
        print("all fine")
    }
}
''', "all fine"),
]


def run(source: str, flags: list):
    SCRATCH.write_text(source.lstrip(), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(VELARIS), str(SCRATCH)] + flags,
        capture_output=True, text=True, timeout=300, cwd=HERE)
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def main() -> int:
    passed = failed = 0
    print(f"{len(CASES)} escape attempts that must be refused")
    print("-" * 62)
    for name, flags, source, must_not_exist in CASES:
        WROTE.unlink(missing_ok=True)
        code, output = run(source, flags)
        escaped = must_not_exist is not None and must_not_exist.exists()
        shouted = any(word in output for word in
                      ("READ IT", "WROTE IT", "REACHED IT", "CALLED IT",
                       "OPENED IT", "GOT THROUGH", "CARRIED ON",
                       "SWALLOWED THE REFUSAL"))
        if escaped:
            print(f"  ESCAPED      {name} (it created the file)")
            failed += 1
        elif shouted:
            print(f"  ESCAPED      {name} (the program carried on)")
            failed += 1
        elif any(r in output for r in REFUSED) and code != 0:
            print(f"  ok refused   {name}")
            passed += 1
        else:
            print(f"  WRONG        {name}")
            print(f"               expected E310/E311, got: "
                  f"{output.strip().splitlines()[:1]}")
            failed += 1
        WROTE.unlink(missing_ok=True)

    print()
    print(f"{len(ALLOWED)} honest programs that must still run")
    print("-" * 62)
    for name, flags, source, expect in ALLOWED:
        code, output = run(source, flags)
        if code == 0 and (not expect or expect in output):
            print(f"  ok runs      {name}")
            passed += 1
        else:
            print(f"  BROKEN       {name}")
            print(f"               exit {code}: "
                  f"{output.strip().splitlines()[:1]}")
            failed += 1

    SCRATCH.unlink(missing_ok=True)
    WROTE.unlink(missing_ok=True)
    print("-" * 62)
    print(f"{passed} correct, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
