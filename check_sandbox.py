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
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
VELARIS = HERE / "velaris.py"
SCRATCH = HERE / "_sandbox_check.vel"
WROTE = HERE / "_sandbox_wrote.txt"

REFUSED = ("E310", "E311", "E313", "E314", "E315")

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
    # 3.3: an ffi:M grant is bounded to the module a call actually
    # reaches, not merely the one it names. The attribute chain is checked
    # step by step; an object owned by a module outside the grants is
    # E311, naming that module, and an owner that cannot be placed is
    # refused rather than allowed. These are the escapes that step 2.2's
    # module-name-only check let through until 3.3.
    ("reaching codecs through a granted json",
     ["--allow", "io,ffi:json"], '''
fn main() uses io, ffi {
    check py("json", "codecs.encode", ["x"]) {
        ok o { print("GOT THROUGH") }
        fail w { print("failed") }
    }
}
''', None),
    ("reaching os.system through a granted os, subprocess-free",
     ["--allow", "io,ffi:os"], '''
fn main() uses io, ffi {
    check py_int("os", "system", ["echo GOT THROUGH"]) {
        ok n { print("GOT THROUGH") }
        fail w { print("failed") }
    }
}
''', None),
    ("using a granted importlib to reach another module",
     ["--allow", "io,ffi:importlib"], '''
fn main() uses io, ffi {
    check py_json("importlib", "import_module", "[\\"os\\"]") {
        ok o { print("GOT THROUGH") }
        fail w { print("failed") }
    }
}
''', None),
    ("reaching a builtins type through a granted module's value",
     ["--allow", "io,ffi:math"], '''
fn main() uses io, ffi {
    let none: List of Text = []
    check py("math", "pi.__class__", none) {
        ok o { print("GOT THROUGH") }
        fail w { print("failed") }
    }
}
''', None),
    ("laundering through __globals__ to reach builtins",
     ["--allow", "io,ffi:json"], '''
fn main() uses io, ffi {
    let none: List of Text = []
    check py("json", "dumps.__globals__.__class__", none) {
        ok o { print("GOT THROUGH") }
        fail w { print("failed") }
    }
}
''', None),
    ("a handle exposing an object from another module",
     ["--allow", "io,ffi:json"], '''
fn main() uses io, ffi {
    check py_new("json", "decoder.JSONDecoder", "[]") {
        ok h {
            check py_field(h, "scan_once") {
                ok f { print("GOT THROUGH") }
                fail w { print("failed") }
            }
        }
        fail w { print("failed") }
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
    # 3.3: the reach check must not break honest deep access inside a
    # granted module, and must let a grant of two modules use both.
    ("a legitimate deep attribute inside the granted module still works",
     ["--allow", "io,ffi:json"], '''
fn main() uses io, ffi {
    check py_new("json", "decoder.JSONDecoder", "[]") {
        ok h { print("made a decoder") }
        fail w { print(w) }
    }
}
''', "made a decoder"),
    ("a two-module grant, each module used correctly",
     ["--allow", "io,ffi:math,ffi:base64"], '''
fn main() uses io, ffi {
    check py_float("math", "sqrt", ["16"]) {
        ok r {
            check py("base64", "b64encode", ["aGk="]) {
                ok b { print("both modules ok") }
                fail w { print(w) }
            }
        }
        fail w { print(w) }
    }
}
''', "both modules ok"),
    # 3.3: ffi is additive like fs and net (spec v0.2, Q2). A plain ffi
    # grants every module, so ffi,ffi:math is every module - the wider
    # grant wins, in either order, and a module other than math works.
    ("additive ffi: a plain ffi widens a named-module grant",
     ["--allow", "io,ffi,ffi:math"], '''
fn main() uses io, ffi {
    let none: List of Text = []
    check py("os", "getcwd", none) {
        ok d { print("wider ffi wins") }
        fail w { print(w) }
    }
}
''', "wider ffi wins"),
    # until 2.62 `--allow io` leaked into args() as two extra words
    ("args() carries the program's arguments, not the budget",
     ["--allow", "io", "7", "eight"], '''
fn main() uses io {
    print(format("args: {}", args()))
}
''', "args: [7, eight]"),
    ("args() is clean under --deny as well",
     ["--deny", "fs,net", "only"], '''
fn main() uses io {
    print(format("args: {}", args()))
}
''', "args: [only]"),
]


# ---- scoped grants (3.0): paths, hosts, counts, and env on its own ----
#
# Built at runtime because they need a directory the test owns, a
# symlink, and two local ports. Each entry has the CASES shape.

def _read(path) -> str:
    return (
        "fn main() uses io, fs {\n"
        f'    check read_file("{path}") {{\n'
        "        ok t {\n            print(\"READ IT\")\n        }\n"
        "        fail w {\n            print(\"failed\")\n        }\n"
        "    }\n}\n")


def _write(path) -> str:
    return (
        "fn main() uses io, fs {\n"
        f'    write_file("{path}", "escaped")\n'
        "    print(\"WROTE IT\")\n}\n")


def _fetch(url) -> str:
    return (
        "fn main() uses io, net {\n"
        f'    check fetch("{url}") {{\n'
        "        ok b {\n            print(\"REACHED IT\")\n        }\n"
        "        fail w {\n            print(\"failed\")\n        }\n"
        "    }\n}\n")


def scoped_cases(box, granted_port: int, other_port: int) -> list:
    data, out = box / "data", box / "out"
    inside = (data / "a.txt").as_posix()
    outside = (box.parent / "_sandbox_outside.txt")
    fs_read = ["--allow", f"io,fs:read:{data.as_posix()}"]
    net_one = ["--allow", f"io,net:127.0.0.1:{granted_port}"]
    count_fs = (
        "fn main() uses io, fs {\n    let i = 0\n    while i < 3 {\n"
        f'        if file_exists("{inside}") {{\n'
        "            print(\"looked\")\n        }\n        i = i + 1\n"
        "    }\n    print(\"GOT THROUGH\")\n}\n")
    count_net = (
        "fn main() uses io, net {\n    let i = 0\n    while i < 3 {\n"
        f'        check fetch_status("http://127.0.0.1:{granted_port}/") {{\n'
        "            ok c {\n                print(\"asked\")\n            }\n"
        "            fail w {\n                print(\"failed\")\n            }\n"
        "        }\n        i = i + 1\n    }\n    print(\"GOT THROUGH\")\n}\n")
    env_only_io = (
        "fn main() uses io, env {\n"
        '    print("READ IT " + env("PATH", ""))\n}\n')
    cases = [
        ("reading outside the granted prefix", fs_read,
         _read(outside.as_posix()), None),
        ("writing with only read granted", fs_read,
         _write((data / "new.txt").as_posix()), data / "new.txt"),
        ("escaping the prefix with ..", fs_read,
         _read((data / ".." / ".." / outside.name).as_posix()), None),
        ("a host not in the list", net_one,
         _fetch(f"http://localhost:{granted_port}/"), None),
        ("a wildcard must not match the parent domain",
         ["--allow", "io,net:*.example.com"],
         _fetch("http://example.com/"), None),
        ("a port not in the list", net_one,
         _fetch(f"http://127.0.0.1:{other_port}/"), None),
        ("the file operation count reached",
         ["--allow", f"io,fs:read:{data.as_posix()}@2"], count_fs, None),
        ("the network operation count reached",
         ["--allow", f"io,net:127.0.0.1:{granted_port}@2"], count_net, None),
        ("env() with only io granted", ["--allow", "io"], env_only_io, None),
    ]
    link = data / "link.txt"
    if os.name != "nt":
        try:
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(outside)
            cases.append(("escaping the prefix through a symlink", fs_read,
                          _read(link.as_posix()), None))
        except OSError:
            pass
    return cases


def scoped_allowed(box, granted_port: int, other_port: int) -> list:
    data, out = box / "data", box / "out"
    inside = (data / "a.txt").as_posix()
    copy = (out / "copy.txt").as_posix()
    honest = (
        "fn main() uses io, env, fs, net {\n"
        f'    check read_file("{inside}") {{\n'
        "        ok t {\n"
        f'            write_file("{copy}", t)\n'
        f'            check fetch_status("http://127.0.0.1:{granted_port}/") {{\n'
        "                ok c {\n"
        '                    print(format("all grants used, status {}, path set: {}",\n'
        '                                 c, length(env("PATH", "")) > 0))\n'
        "                }\n"
        "                fail w {\n                    print(\"fetch failed: \" + w)\n                }\n"
        "            }\n        }\n"
        "        fail w {\n            print(\"read failed: \" + w)\n        }\n"
        "    }\n}\n")
    redirect = (
        "fn main() uses io, net {\n"
        f'    check fetch("http://127.0.0.1:{granted_port}/go") {{\n'
        "        ok b {\n            print(\"FOLLOWED IT\")\n        }\n"
        "        fail w {\n            print(\"caught: \" + w)\n        }\n"
        "    }\n}\n")
    redirect_ok = redirect.replace('print("FOLLOWED IT")', 'print("landed: " + b)')
    # fs is additive: fs:read:D and fs:write:D grant both directions, and
    # the program uses each. net is additive: two host grants grant both.
    fs_additive = (
        "fn main() uses io, fs {\n"
        f'    check read_file("{inside}") {{\n'
        "        ok t {\n"
        f'            write_file("{copy}", t)\n'
        '            print("fs additive ok")\n'
        "        }\n        fail w { print(\"read failed: \" + w) }\n"
        "    }\n}\n")
    net_additive = (
        "fn main() uses io, net {\n"
        f'    check fetch_status("http://127.0.0.1:{granted_port}/") {{\n'
        "        ok a {\n"
        f'            check fetch_status("http://localhost:{other_port}/") {{\n'
        '                ok b { print("net additive ok") }\n'
        "                fail w { print(\"second failed: \" + w) }\n"
        "            }\n        }\n        fail w { print(\"first failed: \" + w) }\n"
        "    }\n}\n")
    return [
        ("an honest program using exactly its grants",
         ["--allow", f"io,env,fs:read:{data.as_posix()},"
                     f"fs:write:{out.as_posix()}@5,"
                     f"net:127.0.0.1:{granted_port}@5"],
         honest, "all grants used, status 200"),
        ("a redirect to an ungranted host is a failure the program sees",
         ["--allow", f"io,net:127.0.0.1:{granted_port}"],
         redirect, "redirected to"),
        ("a redirect to a granted host is followed",
         ["--allow", f"io,net:127.0.0.1:{granted_port},"
                     f"net:localhost:{other_port}"],
         redirect_ok, "landed: hello"),
        ("additive fs: read and write grants both apply",
         ["--allow", f"io,fs:read:{data.as_posix()},"
                     f"fs:write:{out.as_posix()}"],
         fs_additive, "fs additive ok"),
        ("additive net: two host grants both apply",
         ["--allow", f"io,net:127.0.0.1:{granted_port},"
                     f"net:localhost:{other_port}"],
         net_additive, "net additive ok"),
    ]


def local_servers():
    """Two local http servers: the first redirects /go to the second."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    ports = {}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/go"):
                self.send_response(302)
                self.send_header("Location",
                                 f"http://localhost:{ports['other']}/landed")
                self.end_headers()
                return
            body = b"hello"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    a = HTTPServer(("127.0.0.1", 0), H)
    b = HTTPServer(("127.0.0.1", 0), H)
    ports["granted"] = a.server_address[1]
    ports["other"] = b.server_address[1]
    for srv in (a, b):
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    return a, b, ports["granted"], ports["other"]


def run(source: str, flags: list):
    SCRATCH.write_text(source.lstrip(), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(VELARIS), str(SCRATCH)] + flags,
        capture_output=True, text=True, timeout=300, cwd=HERE)
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def main() -> int:
    passed = failed = 0
    box = HERE / "_sandbox_box"
    for sub in ("data", "out"):
        (box / sub).mkdir(parents=True, exist_ok=True)
    (box / "data" / "a.txt").write_text("inside\n", encoding="utf-8")
    (HERE / "_sandbox_outside.txt").write_text("outside\n", encoding="utf-8")
    srv_a, srv_b, granted_port, other_port = local_servers()
    cases = CASES + scoped_cases(box, granted_port, other_port)
    allowed = ALLOWED + scoped_allowed(box, granted_port, other_port)
    if os.name == "nt":
        print("  skip: the symlink escape case needs a POSIX file system")
    print(f"{len(cases)} escape attempts that must be refused")
    print("-" * 62)
    for name, flags, source, must_not_exist in cases:
        WROTE.unlink(missing_ok=True)
        code, output = run(source, flags)
        escaped = must_not_exist is not None and must_not_exist.exists()
        shouted = any(word in output for word in
                      ("READ IT", "WROTE IT", "REACHED IT", "CALLED IT",
                       "OPENED IT", "GOT THROUGH", "CARRIED ON",
                       "SWALLOWED THE REFUSAL", "FOLLOWED IT"))
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
    print(f"{len(allowed)} honest programs that must still run")
    print("-" * 62)
    for name, flags, source, expect in allowed:
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
    (HERE / "_sandbox_outside.txt").unlink(missing_ok=True)
    import shutil
    shutil.rmtree(box, ignore_errors=True)
    for srv in (srv_a, srv_b):
        srv.shutdown()
    print("-" * 62)
    print(f"{passed} correct, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
