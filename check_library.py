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
import os
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

    def skip(label, why="needs the prover"):
        print(f"  skip     {label} ({why})")

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
    # the read goes through a path built at runtime, so the audit can
    # narrow it to a direction but not to a path
    ok("audit suggests the safe command", "--allow fs:read,io" in
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
    # The cap is RLIMIT_AS on POSIX and a job object on Windows (3.1).
    # Linux honours RLIMIT_AS; macOS treats it as best-effort and the
    # program ran to the 60 s timeout there (E610, not E611) on every
    # macos-latest leg since 2.62. The assertion holds where the
    # mechanism holds, and velaris says which that is rather than the
    # suite guessing from the platform name.
    if velaris.memory_cap_is_enforced():
        r = velaris.run(DOUBLING, allow={"io"}, max_memory_mb=150,
                        timeout=60)
        ok("a memory cap STOPS a program that eats memory",
           r.out_of_memory and not r.ok
           and any(p.code == "E611" for p in r.problems),
           str(r.as_dict())[:120])
        ok("...and it is Linux's RLIMIT_AS or a Windows job object that "
           "did it",
           sys.platform == "linux" or os.name == "nt", sys.platform)
    elif sys.platform == "darwin":
        skip("a memory cap stops a program that eats memory",
             "RLIMIT_AS is best-effort on macOS")
    else:
        skip("a memory cap stops a program that eats memory",
             "no job object could be made on this Windows")

    r = velaris.run(READS_A_FILE, allow={"io"}, timeout=30)
    ok("the budget still holds inside the bounded child process",
       not r.ok and r.refused_effect == "fs" and "READ IT" not in r.output,
       str(r.as_dict())[:120])

    r = velaris.run(PURE, allow={"io"}, timeout=30)
    ok("an honest program is unaffected by limits",
       r.ok and r.output.strip() == "42", repr(r.output))

    print()
    print("scoped grants through the library (3.0)")
    print("-" * 62)
    import os as _os
    import shutil as _shutil
    import threading as _threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    box = HERE / "_library_box"
    for sub in ("data", "out"):
        (box / sub).mkdir(parents=True, exist_ok=True)
    inside = box / "data" / "a.txt"
    inside.write_text("inside\n", encoding="utf-8")
    outside = HERE / "_library_outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    data, out = (box / "data").as_posix(), (box / "out").as_posix()

    ports = {}

    class Local(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/go"):
                self.send_response(302)
                self.send_header(
                    "Location", f"http://localhost:{ports['other']}/x")
                self.end_headers()
                return
            body = b"hello"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv_a = HTTPServer(("127.0.0.1", 0), Local)
    srv_b = HTTPServer(("127.0.0.1", 0), Local)
    ports["granted"], ports["other"] = (srv_a.server_address[1],
                                        srv_b.server_address[1])
    for srv in (srv_a, srv_b):
        _threading.Thread(target=srv.serve_forever, daemon=True).start()
    gp, op = ports["granted"], ports["other"]

    def reads(path):
        return ("fn main() uses io, fs {\n"
                f'    check read_file("{path}") {{\n'
                "        ok t { print(\"READ \" + t) }\n"
                "        fail w { print(\"failed\") }\n    }\n}\n")

    def writes(path):
        return ("fn main() uses io, fs {\n"
                f'    write_file("{path}", "x")\n    print("WROTE")\n}}\n')

    def fetches(url):
        return ("fn main() uses io, net {\n"
                f'    check fetch("{url}") {{\n'
                "        ok b { print(\"GOT \" + b) }\n"
                "        fail w { print(\"caught: \" + w) }\n    }\n}\n")

    def refused(label, source, allow, code, effect_prefix):
        r = velaris.run(source, allow=set(allow))
        ok(label, not r.ok and any(p.code == code for p in r.problems)
           and (r.refused_effect or "").startswith(effect_prefix),
           str(r.as_dict())[:120])

    refused("run REFUSES a read outside the prefix (E313)",
            reads(outside.as_posix()), ["io", f"fs:read:{data}"],
            "E313", "fs:")
    refused("run REFUSES a write with only read granted (E313)",
            writes((box / "data" / "new.txt").as_posix()),
            ["io", f"fs:read:{data}"],
            "E313", "fs:")
    refused("run REFUSES a .. escape (E313)",
            reads((box / "data" / ".." / ".." / outside.name).as_posix()),
            ["io", f"fs:read:{data}"], "E313", "fs:")
    if _os.name != "nt":
        link = box / "data" / "link.txt"
        try:
            link.symlink_to(outside)
            refused("run REFUSES a symlink escape (E313)",
                    reads(link.as_posix()), ["io", f"fs:read:{data}"],
                    "E313", "fs:")
        except OSError:
            skip("run REFUSES a symlink escape", "no symlinks on this file system")
    else:
        skip("run REFUSES a symlink escape", "POSIX only")
    refused("run REFUSES a host not in the list (E314)",
            fetches(f"http://localhost:{gp}/"), ["io", f"net:127.0.0.1:{gp}"],
            "E314", "net:")
    refused("a wildcard does NOT match the parent domain (E314)",
            fetches("http://example.com/"), ["io", "net:*.example.com"],
            "E314", "net:")
    refused("run REFUSES a port not in the list (E314)",
            fetches(f"http://127.0.0.1:{op}/"), ["io", f"net:127.0.0.1:{gp}"],
            "E314", "net:")
    count_fs = ("fn main() uses io, fs {\n    let i = 0\n"
                "    while i < 3 {\n"
                f'        if file_exists("{inside.as_posix()}") {{ print("looked") }}\n'
                "        i = i + 1\n    }\n}\n")
    refused("run STOPS at the file operation count (E315)",
            count_fs, ["io", f"fs:read:{data}@2"], "E315", "fs")
    count_net = ("fn main() uses io, net {\n    let i = 0\n"
                 "    while i < 3 {\n"
                 f'        check fetch_status("http://127.0.0.1:{gp}/") {{\n'
                 "            ok c { print(c) }\n            fail w { print(w) }\n"
                 "        }\n        i = i + 1\n    }\n}\n")
    refused("run STOPS at the network operation count (E315)",
            count_net, ["io", f"net:127.0.0.1:{gp}@2"], "E315", "net")
    env_prog = ('fn main() uses io, env {\n'
                '    print(length(env("PATH", "")) > 0)\n}\n')
    refused("run REFUSES env() with only io granted (E310)",
            env_prog, ["io"], "E310", "env")
    c = velaris.check('fn main() uses io {\n    print(env("PATH", ""))\n}\n')
    ok("check says exactly what changed for env()",
       not c.ok and c.problems[0].code == "E300"
       and c.problems[0].message == "env() now needs 'uses env'",
       str(c.as_dict())[:120])

    r = velaris.run(fetches(f"http://127.0.0.1:{gp}/go"),
                    allow={"io", f"net:127.0.0.1:{gp}"})
    ok("a redirect to an ungranted host is a failure the program catches",
       r.ok and "caught:" in r.output and "redirected to" in r.output,
       str(r.as_dict())[:120])
    r = velaris.run(fetches(f"http://127.0.0.1:{gp}/go"),
                    allow={"io", f"net:127.0.0.1:{gp}", f"net:localhost:{op}"})
    ok("a redirect to a granted host is followed",
       r.ok and r.output.strip() == "GOT hello", str(r.as_dict())[:120])
    honest = ("fn main() uses io, env, fs, net {\n"
              f'    check read_file("{inside.as_posix()}") {{\n'
              "        ok t {\n"
              f'            write_file("{(box / "out" / "copy.txt").as_posix()}", t)\n'
              f'            check fetch_status("http://127.0.0.1:{gp}/") {{\n'
              '                ok c { print(format("ok {} {}", c, length(env("PATH", "")) > 0)) }\n'
              "                fail w { print(w) }\n            }\n        }\n"
              "        fail w { print(w) }\n    }\n}\n")
    r = velaris.run(honest, allow={"io", "env", f"fs:read:{data}",
                                   f"fs:write:{out}@5", f"net:127.0.0.1:{gp}@5"})
    ok("an honest program using exactly its grants runs",
       r.ok and r.output.strip() == "ok 200 true", str(r.as_dict())[:120])
    r = velaris.run(reads(outside.as_posix()), allow={"io", f"fs:read:{data}"},
                    timeout=20)
    ok("the bounded child enforces the same prefix (E313)",
       not r.ok and any(p.code == "E313" for p in r.problems),
       str(r.as_dict())[:120])
    a = velaris.audit(reads(inside.as_posix()) + fetches("https://api.example.com/v1").replace("fn main", "fn other"))
    ok("audit names the paths and hosts a program reads",
       a.fs_paths["read"] == [inside.as_posix()]
       and a.net_hosts["hosts"] == ["api.example.com"]
       and "fs:read:" in a.safe_command and "net:api.example.com" in a.safe_command,
       a.safe_command)
    _shutil.rmtree(box, ignore_errors=True)
    outside.unlink(missing_ok=True)
    scoped_ports = (gp, op)
    scoped_servers = (srv_a, srv_b)
    scoped_data = data

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
    print("velaris.lock (3.1)")
    print("-" * 62)
    import shutil as _sh
    import tempfile as _tf
    lockbox = Path(_tf.mkdtemp(prefix="velaris-lock-"))
    try:
        upstream = lockbox / "greet.vel"
        upstream.write_text(
            "fn greet(who: Text) -> Text\n"
            "    ensures length(result) >= 1\n"
            "{\n"
            '    return "hi " + who\n'
            "}\n", encoding="utf-8")
        work = lockbox / "project"
        work.mkdir()

        def velaris_in(where, *words):
            env = dict(os.environ)
            env["PYTHONPATH"] = str(HERE)
            return subprocess.run(
                [sys.executable, str(HERE / "velaris.py"), *words],
                cwd=str(where), capture_output=True, text=True, env=env,
                timeout=300)

        added = velaris_in(work, "add", str(upstream), "as", "greet")
        lock = work / "velaris.lock"
        ok("velaris add writes velaris.lock",
           added.returncode == 0 and lock.exists(),
           (added.stdout + added.stderr)[:160])
        recorded = json.loads(lock.read_text(encoding="utf-8"))
        entry = (recorded.get("libraries") or [{}])[0]
        ok("the lock records source, sha256 and the Velaris that added it",
           recorded.get("lockfile") == "velaris.lock/1"
           and entry.get("name") == "greet"
           and len(entry.get("sha256", "")) == 64
           and entry.get("added_by") == velaris.VERSION,
           str(recorded)[:200])
        ok("the locked digest is the digest of the bytes that arrived",
           entry.get("sha256") == __import__("hashlib").sha256(
               upstream.read_bytes()).hexdigest(),
           str(entry.get("sha256")))

        clean = velaris_in(work, "deps", "--verify")
        ok("deps --verify passes on a clean tree",
           clean.returncode == 0 and "exactly as locked" in clean.stdout,
           (clean.stdout + clean.stderr)[:200])

        vendored = work / "lib" / "greet.vel"
        kept = vendored.read_bytes()
        vendored.write_bytes(kept + b"\n// tampered with\n")
        tampered = velaris_in(work, "deps", "--verify")
        ok("deps --verify FAILS on a tampered file",
           tampered.returncode == 1 and "CHANGED" in tampered.stdout,
           (tampered.stdout + tampered.stderr)[:200])

        vendored.unlink()
        missing = velaris_in(work, "deps", "--verify")
        ok("deps --verify FAILS on a library that is not there",
           missing.returncode == 1 and "MISSING" in missing.stdout,
           (missing.stdout + missing.stderr)[:200])

        vendored.write_bytes(kept)
        upstream.write_text(
            upstream.read_text(encoding="utf-8") + "\n// a new version\n",
            encoding="utf-8")
        refused = velaris_in(work, "add", str(upstream), "as", "greet")
        ok("velaris add REFUSES to overwrite different bytes",
           refused.returncode == 1
           and "different file" in refused.stderr
           and vendored.read_bytes() == kept,
           (refused.stdout + refused.stderr)[:200])
        forced = velaris_in(work, "add", str(upstream), "as", "greet",
                            "--force")
        ok("...and --force replaces it and relocks it",
           forced.returncode == 0
           and vendored.read_bytes() != kept
           and velaris_in(work, "deps", "--verify").returncode == 0,
           (forced.stdout + forced.stderr)[:200])
    finally:
        _sh.rmtree(lockbox, ignore_errors=True)

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

    print()
    print("the HTTP door with a scoped ceiling (3.0)")
    print("-" * 62)
    gp, op = scoped_ports
    box2 = HERE / "_door_box"
    (box2 / "data" / "sub").mkdir(parents=True, exist_ok=True)
    (box2 / "data" / "sub" / "a.txt").write_text("inside\n", encoding="utf-8")
    data2 = (box2 / "data").as_posix()
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port2 = probe.getsockname()[1]
    server = _sub.Popen(
        [sys.executable, str(HERE / "velaris.py"), "serve",
         "--port", str(port2), "--max-allow",
         f"io,fs:read:{data2},net:127.0.0.1:{gp}@5"],
        stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port2}/health", timeout=1).read()
                break
            except Exception:
                time.sleep(0.25)

        def post2(path, payload):
            req = urllib.request.Request(
                f"http://127.0.0.1:{port2}{path}",
                data=_json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.status, _json.load(r)
            except urllib.error.HTTPError as e:
                return e.code, _json.load(e)

        prog = ("fn main() uses io, fs {\n"
                f'    check read_file("{(box2 / "data" / "sub" / "a.txt").as_posix()}") {{\n'
                "        ok t { print(\"READ \" + t) }\n"
                "        fail w { print(\"failed\") }\n    }\n}\n")
        code, d = post2("/run", {"source": prog, "allow": ["io", "fs:read"]})
        ok("the door refuses an unscoped ask against a scoped ceiling (403)",
           code == 403 and "fs:read" in d.get("error", ""), str(d)[:120])
        code, d = post2("/run", {"source": prog,
                                 "allow": ["io", f"fs:read:{box2.as_posix()}"]})
        ok("the door refuses a wider path prefix than it grants (403)",
           code == 403, str(d)[:120])
        code, d = post2("/run", {"source": prog,
                                 "allow": ["io", f"fs:read:{data2}/sub"]})
        ok("the door accepts a narrower prefix and the program runs",
           code == 200 and d.get("ok") and d.get("output", "").strip() == "READ inside",
           str(d)[:120])
        code, d = post2("/run", {"source": prog,
                                 "allow": ["io", f"net:localhost:{gp}"]})
        ok("the door refuses a host it does not grant (403)",
           code == 403, str(d)[:120])
        code, d = post2("/run", {"source": prog,
                                 "allow": ["io", f"net:127.0.0.1:{gp}@10"]})
        ok("the door refuses a count above its own (403)",
           code == 403 and "at most 5" in d.get("error", ""), str(d)[:120])
        code, d = post2("/run", {"source": prog, "allow": ["io", "fs:peek:x"]})
        ok("the door rejects a budget that does not parse (400)",
           code == 400, str(d)[:120])
    finally:
        server.terminate()
        server.wait(timeout=30)
        _shutil.rmtree(box2, ignore_errors=True)
        for srv in scoped_servers:
            srv.shutdown()

    print()
    print("safe_command round-trips (3.3)")
    print("-" * 62)
    # A grant that names an awkward path or host must survive being
    # written to a budget and read back unchanged: parse it, write the
    # canonical text a safe_command is built from, parse that, and get
    # the same budget. This is the escaping rule of spec v0.2 - IPv6 in
    # brackets, and `, @ [ ] %` percent-encoded in a path or host - and
    # it is a property of the budget objects, not a string comparison.
    def budget_shape(b):
        return (sorted(b.effects),
                None if b.modules is None else sorted(b.modules),
                None if b.fs is None else sorted(b.fs),
                None if b.net is None else sorted(b.net),
                dict(b.limits))

    awkward = [
        "net:[::1]", "net:[::1]:443", "net:[2001:db8::1]:8080",
        "net:[fe80::1%25eth0]", "net:[::1]@3",
        "fs:read:./a%2Cb.txt", "fs:write:./mail%40host",
        "fs:read:./with a space", "fs:read:./café",
        "fs:read:./data/", "fs:read:../up", "fs:read:./100%25.txt",
        "fs:read:./a%40b%2Cc", "fs:write:./out@5",
        "net:host%2Cname", "net:user%40host", "net:%25pct",
        "net:api.example.com:443", "net:*.example.com",
        "io,fs:read:./x%2Cy,net:[::1]:8443,ffi:math",
        "fs:read:./tab\tsep", "net:[2001:db8::dead:beef]",
    ]
    rt_bad = [g for g in awkward
              if budget_shape(velaris.Budget.parse(g))
              != budget_shape(velaris.Budget.parse(
                  velaris.Budget.parse(g).spec()))]
    ok(f"{len(awkward)} awkward grants round-trip through the canonical "
       "budget text", not rt_bad, f"did not round-trip: {rt_bad}")

    # the same, reached through the artifact that had the bug: a program
    # naming an IPv6 host and a comma path, whose audit.safe_command must
    # parse back to those exact grants (spec v0.2, Q5 resolved).
    awk_prog = ('fn grab() uses fs, net or fail {\n'
                '    let a = try read_file("data,cache.txt")\n'
                '    let b = try fetch("http://[2001:db8::1]:8080/x")\n'
                '}\n'
                'fn main() uses io { print("ok") }\n')
    sc = velaris.audit(awk_prog).safe_command
    b = velaris.Budget.parse(sc.split("--allow ", 1)[1])
    ok("audit safe_command with an IPv6 host and a comma path parses back",
       ("2001:db8::1", 8080) in (b.net or [])
       and any((p or "").endswith("data,cache.txt") for _, p in (b.fs or [])),
       sc)

    print()
    print("malformed budgets fail cleanly (3.3)")
    print("-" * 62)
    # Every malformed budget must be a clean budget error, never an
    # unhandled traceback (spec Q6). `fs@²` used to stop the parser
    # with a ValueError from int(); an unknown effect, a doubled colon,
    # a stray bracket, a count on ffi, a scope on io - each must raise a
    # readable BudgetError and nothing else.
    def malformed_budgets():
        out = []
        out += ["fs::", "fs:::", "net::", "net:::1", "net:::", "fs:read:",
                "fs:write:", ":", "@5", "net:[]", "net:[]:80"]
        for d in ["²", "³", "٣", "⁵", "۲", "５"]:
            out += [f"fs@{d}", f"net@{d}", f"fs:read:x@{d}", f"net:h@{d}"]
        for t in ["x", "1x", "-1", "1.5", "0x1", "1_000", "1e9", "", "  ",
                  "one", "+3", "1,2", "9x", "0o7", "3.0", "٤",
                  "₂", " 5", "0b1", "1'0"]:
            out += [f"fs@{t}", f"net@{t}", f"fs:write:x@{t}"]
        out += ["fs@-1", "net@-5", "fs:read:x@-2", "net:h:80@-1"]
        for p in ["0", "65536", "70000", "99999", "100000", "-1", "x", "8o",
                  "66000", "123456", "1e3", "80.0", " 80", "0x50"]:
            out += [f"net:h:{p}", f"net:[::1]:{p}"]
        out += ["net:", "net:h:x", "net:[::1", "net:[a]b", "net:[a][b]",
                "net:[", "net:h/path", "net:a:b:c", "net:h:1:2"]
        out += ["fs:read:a@b@c", "net:h@1@2", "fs@1@2", "net@3@4"]
        out += ["ffi@5", "ffi@1", "ffi:@5", "ffi:", "ffi:math@5",
                "ffi:math@", "ffi:.@2", "ffi:@", "ffi:a@9", "ffi@2", "ffi@0"]
        for e in ["io", "env", "clock", "rand"]:
            out += [f"{e}:x", f"{e}@1", f"{e}:", f"{e}@0", f"{e}:read",
                    f"{e}@2", f"{e}:scope"]
        out += ["IO", "Fs", "NET", "Ffi", "banana", "io2", "fss", "nett",
                "clockk", "randd", "envv", "xyz", "fs1", "net1",
                "fs:reed:x", "net:*.com", "net:*", "net:*.*",
                "fs:read:x,,net:*.com,ffi@2", "net:*.", "net:*.1.2.3",
                "net:a*b.com", "net:*a.com", "Io", "ENV", "Clock", "RAND",
                "http", "web", "sql", "exec", "shell", "sys", "net2",
                "fs_", "ff", "f", "n", "e", "io.", "io-x", "read",
                "write", "path", "host", "port", "module", "count"]
        return sorted(set(out))

    fuzz = malformed_budgets()
    fuzz_wrong = []
    for g in fuzz:
        try:
            velaris.Budget.parse(g)
            fuzz_wrong.append(("parsed cleanly", g))
        except ValueError as e:            # BudgetError is a ValueError
            if not str(e):
                fuzz_wrong.append(("no message", g))
        except Exception as e:             # a traceback: the bug we fix
            fuzz_wrong.append((type(e).__name__, g))
    ok(f"{len(fuzz)} malformed budgets each raise a readable budget error "
       "(>= 200)", len(fuzz) >= 200 and not fuzz_wrong,
       f"{fuzz_wrong[:5]}")
    # allow= in the library raises ValueError too, not a traceback
    try:
        velaris.run(PURE, allow={"fs@²"})
        ok("a bad grant through the library is a ValueError", False)
    except ValueError:
        ok("a bad grant through the library is a ValueError", True)
    except Exception as e:
        ok("a bad grant through the library is a ValueError", False,
           type(e).__name__)

    print()
    print("the CLI's audit --json is velaris.audit/1 (3.3)")
    print("-" * 62)
    # The command line was the one door that did not emit velaris.audit/1
    # (spec Q3). It now prints audit().as_dict(), the same shape as the
    # library, MCP server, HTTP door, npm package, CrewAI tool and Action.
    cli = subprocess.run(
        [sys.executable, str(HERE / "velaris.py"), "audit",
         str(HERE / "examples" / "json_ffi.vel"), "--json"],
        capture_output=True, text=True, timeout=300)
    try:
        doc = json.loads(cli.stdout)
    except Exception as e:
        doc = None
        ok("the CLI's audit --json is valid JSON", False,
           f"{e}: {cli.stdout[:120]}")
    if doc is not None:
        ok("the CLI's audit --json carries the velaris.audit/1 schema",
           doc.get("schema") == "velaris.audit/1", str(doc)[:120])
        ok("the CLI's safe_command scopes ffi to the module named "
           "(ffi:math,io, not ffi,io)",
           doc.get("safe_command") == "velaris <file> --allow ffi:math,io",
           doc.get("safe_command"))
        schema_path = (HERE.parent / "velaris-spec" / "schemas"
                       / "velaris.audit.1.schema.json")
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            skip("the CLI's audit --json validates against the spec schema",
                 "jsonschema is not installed")
        else:
            if not schema_path.exists():
                skip("the CLI's audit --json validates against the spec "
                     "schema", f"{schema_path} is not present")
            else:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                errs = sorted(Draft202012Validator(schema).iter_errors(doc),
                              key=lambda e: list(e.absolute_path))
                ok("the CLI's audit --json validates against the v0.2 "
                   "velaris.audit/1 schema in velaris-spec",
                   not errs, "; ".join(e.message for e in errs[:3]))

    print("-" * 62)
    print(f"{passed} correct, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
