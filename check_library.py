#!/usr/bin/env python3
"""The library and the MCP server must give the same guarantees.

Velaris as a command has four suites behind it. Velaris as a library is
what an agent framework would actually import, and an effect budget
that holds on the command line but leaks through `velaris.run()` would
be worse than no budget at all - it would be a false promise in the
place people trust most.

    python check_library.py
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import velaris  # noqa: E402

# three checks below are about PROOFS, so they can only be made when the
# prover is installed. Without it those promises are checked while the
# program runs, which is correct behaviour, not a failure - the same
# rule the example suite and the refusal harness already follow.
HAVE_PROVER = velaris.HAVE_Z3

PURE = '''
fn double(n: Int) -> Int
    requires n >= 0
    ensures result >= 0
{
    return n * 2
}

fn main() uses io {
    print(double(21))
}
'''

READS_A_FILE = '''
fn peek(path: Text) -> Text uses fs or fail {
    return try read_file(path)
}

fn main() uses io, fs {
    print("start")
    check peek("velaris.py") {
        ok body {
            print("READ IT")
        }
        fail why {
            print("failed")
        }
    }
}
'''

BROKEN = '''
fn discount(price: Int) -> Int
    requires price >= 0
    ensures result >= 0
{
    return price - 10
}

fn main() uses io {
    print(discount(5))
}
'''

WONT_COMPILE = '''
fn main() {
    print("no effect declared")
}
'''


def _json_version(path) -> str:
    import json as _j
    return _j.loads(path.read_text(encoding="utf-8"))["version"]


def main() -> int:
    passed = failed = 0

    def skip(label):
        print(f"  skip     {label} (needs the prover)")

    def ok(label, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  ok       {label}")
            passed += 1
        else:
            print(f"  BROKEN   {label}")
            if detail:
                print(f"           {detail}")
            failed += 1

    print("the library")
    print("-" * 62)

    r = velaris.check(PURE)
    ok("check accepts a good program", r.ok, str(r.problems))
    if HAVE_PROVER:
        ok("check reports what was proven", "double" in r.proven,
           str(r.proven))
    else:
        skip("check reports what was proven")

    r = velaris.check(WONT_COMPILE)
    ok("check reports an undeclared effect",
       not r.ok and any(p.code == "E300" for p in r.problems),
       str(r.problems))
    ok("problems carry fixes",
       bool(r.problems and r.problems[0].fixes))

    if HAVE_PROVER:
        r = velaris.check(BROKEN)
        ok("check refutes a false promise",
           not r.ok and any(p.code == "E700" for p in r.problems),
           str(r.problems))
    else:
        skip("check refutes a false promise")
        r = velaris.run(BROKEN, allow={"io"})
        ok("without the prover, the promise breaks while running",
           not r.ok and any(p.code in ("E600", "E601")
                            for p in r.problems), str(r.problems))

    a = velaris.audit(READS_A_FILE)
    ok("audit names every effect", a.effects == ["fs", "io"],
       str(a.effects))
    ok("audit carries a schema version",
       a.schema == "velaris.audit/1" and a.velaris_version)
    ok("audit suggests the safe command", "--allow fs,io" in
       a.safe_command, a.safe_command)

    a = velaris.audit(PURE)
    if HAVE_PROVER:
        ok("audit reports the proven share", a.proven_share == 100.0,
           str(a.proven_share))
    else:
        ok("audit reports a share of nothing proven without the prover",
           a.proven_share == 0.0, str(a.proven_share))

    ffi_src = ('fn main() uses io, ffi {\n'
               '    check py("os", "getcwd", []) {\n'
               '        ok v {\n            print(v)\n        }\n'
               '        fail w {\n            print(w)\n        }\n'
               '    }\n}\n')
    a = velaris.audit(ffi_src)
    ok("audit warns about the ffi cliff", bool(a.warnings),
       str(a.warnings))

    r = velaris.run(PURE, allow={"io"})
    ok("run executes and captures output",
       r.ok and r.output.strip() == "42", repr(r.output))

    r = velaris.run(READS_A_FILE, allow={"io"})
    ok("run REFUSES an effect outside the budget",
       not r.ok and r.refused_effect == "fs", str(r.as_dict()))
    ok("the refused program did not carry on",
       "READ IT" not in r.output, repr(r.output))

    r = velaris.run(READS_A_FILE, allow={"io", "fs"})
    ok("run permits what the budget allows",
       r.ok and "READ IT" in r.output, repr(r.output))

    r = velaris.run(PURE, allow=set())
    ok("a program needing io is refused with no budget",
       not r.ok and r.refused_effect == "io", str(r.as_dict()))

    try:
        velaris.run(PURE, allow={"banana"})
        ok("an unknown effect name is rejected", False)
    except ValueError:
        ok("an unknown effect name is rejected", True)

    r1 = velaris.run(PURE, allow={"io"})
    r2 = velaris.run(READS_A_FILE, allow={"io"})
    r3 = velaris.run(PURE, allow={"io"})
    ok("the budget is restored between runs",
       r1.ok and not r2.ok and r3.ok)

    r = velaris.run('fn main() uses io {\n    print(ask("name:"))\n}\n',
                    allow={"io"}, stdin="gowri\n")
    ok("stdin reaches the program", "gowri" in r.output, repr(r.output))

    r = velaris.run('fn main() uses io {\n    print(args())\n}\n',
                    allow={"io"}, args=["a", "b"])
    ok("args reach the program", "a" in r.output, repr(r.output))

    ok("card returns the language", len(velaris.card()) > 2000)

    FOREVER = ("fn main() uses io {\n    let i = 0\n    while i >= 0 {\n"
               "        i = i + 1\n        if i > 1000000 {\n"
               "            i = 0\n        }\n    }\n    print(1)\n}\n")
    r = velaris.run(FOREVER, allow={"io"}, timeout=2)
    ok("a timeout STOPS a program that never ends",
       r.timed_out and not r.ok
       and any(p.code == "E610" for p in r.problems), str(r.as_dict())[:120])

    DOUBLING = ("fn main() uses io {\n    let s = \"xxxxxxxxxxxxxxxx\"\n"
                "    let i = 0\n    while i < 40 {\n        s = s + s\n"
                "        i = i + 1\n    }\n    print(length(s))\n}\n")
    r = velaris.run(DOUBLING, allow={"io"}, max_memory_mb=150, timeout=60)
    if sys.platform == "win32":
        skip("a memory cap stops a program that eats memory (not on "
             "Windows)")
    else:
        ok("a memory cap STOPS a program that eats memory",
           r.out_of_memory and not r.ok
           and any(p.code == "E611" for p in r.problems),
           str(r.as_dict())[:120])

    r = velaris.run(READS_A_FILE, allow={"io"}, timeout=30)
    ok("the budget still holds inside the bounded child process",
       not r.ok and r.refused_effect == "fs" and "READ IT" not in r.output,
       str(r.as_dict())[:120])

    r = velaris.run(PURE, allow={"io"}, timeout=30)
    ok("an honest program is unaffected by limits",
       r.ok and r.output.strip() == "42", repr(r.output))

    print()
    print("the MCP server")
    print("-" * 62)
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
            "name": "velaris_run",
            "arguments": {"source": READS_A_FILE, "allow": ["io"]}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
            "name": "velaris_audit", "arguments": {"source": PURE}}},
        {"jsonrpc": "2.0", "method": "exit", "params": {}},
    ]
    done = subprocess.run(
        [sys.executable, str(HERE / "velaris_mcp.py")],
        input="\n".join(json.dumps(m) for m in msgs) + "\n",
        capture_output=True, text=True, timeout=600)
    answers = {}
    for line in done.stdout.strip().splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("id") is not None:
            answers[d["id"]] = d

    ok("it announces itself",
       answers.get(1, {}).get("result", {})
       .get("serverInfo", {}).get("name") == "velaris")
    tools = [t["name"] for t in
             answers.get(2, {}).get("result", {}).get("tools", [])]
    ok("it offers all four tools",
       set(tools) == {"velaris_card", "velaris_check", "velaris_audit",
                      "velaris_run"}, str(tools))
    try:
        body = json.loads(answers[3]["result"]["content"][0]["text"])
        ok("run through MCP enforces the budget",
           not body["ok"] and body.get("refused_effect") == "fs",
           str(body)[:120])
        ok("MCP explains the refusal", "note" in body)
    except Exception as e:
        ok("run through MCP enforces the budget", False, str(e))
    try:
        body = json.loads(answers[4]["result"]["content"][0]["text"])
        ok("audit through MCP carries the schema",
           body["schema"] == "velaris.audit/1")
    except Exception as e:
        ok("audit through MCP carries the schema", False, str(e))

    print()
    print("every door, after a real install")
    print("-" * 62)
    import importlib.util
    for module in ("velaris", "velaris_mcp", "velaris_mcp_install",
                   "velaris_magic"):
        ok(f"{module} is importable",
           importlib.util.find_spec(module) is not None,
           "it is missing from the wheel: check pyproject.toml")

    a = velaris.audit(WONT_COMPILE)
    r = velaris.run(WONT_COMPILE, allow={"io"})
    ok("audit and run report problems the same way",
       bool(a.problems) and bool(r.problems)
       and hasattr(a.problems[0], "code")
       and hasattr(r.problems[0], "code"),
       f"audit gave {type(a.problems[0]).__name__}, "
       f"run gave {type(r.problems[0]).__name__}")
    ok("as_dict gives plain data for JSON",
       isinstance(a.as_dict()["problems"][0], dict))

    import subprocess as _sub2
    strict_ok = _sub2.run(
        [sys.executable, str(HERE / "velaris.py"), "check",
         str(HERE / "examples" / "inferred.vel"), "--strict"],
        capture_output=True, text=True, timeout=900)
    strict_no = _sub2.run(
        [sys.executable, str(HERE / "velaris.py"), "check",
         str(HERE / "examples" / "wordcount.vel"), "--strict"],
        capture_output=True, text=True, timeout=900)
    if HAVE_PROVER:
        ok("--strict accepts a file whose promises all prove",
           strict_ok.returncode == 0, strict_ok.stderr[:120])
        ok("--strict REFUSES a promise left to runtime",
           strict_no.returncode == 1 and "could not be proven"
           in strict_no.stderr, strict_no.stderr[:120])
    else:
        ok("--strict refuses rather than pretending, with no prover",
           strict_ok.returncode == 1 and "needs the prover"
           in strict_ok.stderr, strict_ok.stderr[:120])

    npm_pkg = HERE / "npm" / "package.json"
    if npm_pkg.exists():
        ok("the npm package version follows the compiler",
           _json_version(npm_pkg) == velaris.VERSION,
           f"npm says {_json_version(npm_pkg)}, "
           f"compiler says {velaris.VERSION}")
    hooks = HERE / ".pre-commit-hooks.yaml"
    ok("the pre-commit hooks exist", hooks.exists())

    print()
    print("the HTTP door")
    print("-" * 62)
    import json as _json
    import socket
    import subprocess as _sub
    import time
    import urllib.error
    import urllib.request

    with socket.socket() as probe:        # a port nobody else is using
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = _sub.Popen(
        [sys.executable, str(HERE / "velaris.py"), "serve",
         "--port", str(port), "--max-allow", "io,fs"],
        stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
    try:
        for _ in range(60):               # wait for it to answer
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/health", timeout=1).read()
                break
            except Exception:
                time.sleep(0.25)

        def post(path, payload):
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}{path}",
                data=_json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return _json.load(r)
            except urllib.error.HTTPError as e:
                return _json.load(e)

        health = _json.load(urllib.request.urlopen(
            f"http://127.0.0.1:{port}/health", timeout=10))
        ok("it reports its version and ceiling",
           health.get("velaris") == velaris.VERSION
           and health.get("max_allow") == ["fs", "io"], str(health))

        d = post("/audit", {"source": READS_A_FILE})
        ok("audit over HTTP carries the schema",
           d.get("schema") == "velaris.audit/1", str(d)[:100])

        d = post("/run", {"source": READS_A_FILE, "allow": ["io"]})
        ok("HTTP run REFUSES an effect outside the budget",
           not d.get("ok") and d.get("refused_effect") == "fs",
           str(d)[:120])

        d = post("/run", {"source": READS_A_FILE, "allow": ["ffi"]})
        ok("the server refuses what IT does not grant",
           "error" in d and "ffi" in d["error"], str(d)[:120])

        d = post("/run", {"source": PURE, "allow": ["io"]})
        ok("HTTP run works when the budget allows it",
           d.get("ok") and d.get("output", "").strip() == "42",
           str(d)[:120])

        d = post("/check", {"source": WONT_COMPILE})
        ok("check over HTTP reports problems",
           not d.get("ok") and d["problems"][0]["code"] == "E300",
           str(d)[:120])
    finally:
        server.terminate()
        server.wait(timeout=30)

    print("-" * 62)
    print(f"{passed} correct, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
