#!/usr/bin/env python3
"""Secret of T: a value the type system will not let out (SPEC.md 3.1).

Every case here is a whole program, compiled or run by the real
compiler. The suite covers what an information-flow type has to get
right, and the places a hole would be:

  * every emitting builtin refuses a Secret argument, with E560 naming
    the value and where the secret came from
  * a structure is not a way around it: a record field, a list element
    and a map value each make the whole thing carry the secret
  * a secret cannot be laundered through a helper, through a generic
    function with effects, through a 'fail' reason, or through a
    signature that says it returns a plain value
  * pure computation over a secret keeps the secret, and a comparison
    over one gives an ordinary Bool - the one-bit channel SPEC.md 3.1
    allows on purpose, and says the cost of
  * declassify is refused without the effect declared, refused by the
    budget without the grant, and refused without a reason written in
    the call; with all three it works
  * velaris.audit/1's secrets section reports the sources, whether the
    program declassifies, and each reason
  * the tracer and a broken promise print <secret>, not the value
  * and an honest program that uses a secret correctly still runs

Needs no theorem prover: every rule here is a type rule.

    python check_secret.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
VELARIS = HERE / "velaris.py"
SCRATCH = HERE / "_secret_check.vel"

sys.path.insert(0, str(HERE))
import velaris  # noqa: E402

PASS = [0]
FAIL = [0]


def ok(label: str, good: bool, detail: str = "") -> None:
    if good:
        PASS[0] += 1
        print(f"  ok    {label}")
    else:
        FAIL[0] += 1
        print(f"  WRONG {label}" + (f"\n          {detail}" if detail else ""))


def check(source: str) -> tuple:
    SCRATCH.write_text(source, encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(VELARIS), "check", str(SCRATCH), "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=str(HERE))
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def run(source: str, allow: str) -> tuple:
    SCRATCH.write_text(source, encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(VELARIS), str(SCRATCH), "--allow", allow],
        capture_output=True, text=True, timeout=300, cwd=str(HERE))
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def said(out: str) -> str:
    """What the program printed, without the compiler's notes about what
    is not installed - so a run without the prover compares the same."""
    return "\n".join(ln for ln in out.splitlines()
                     if not ln.startswith("note: ")).strip()


def refused(label: str, source: str, code: str, says=()) -> None:
    """This program must not compile, with this code, saying these."""
    got, out = check(source)
    missing = [s for s in says if s not in out]
    ok(label, got != 0 and code in out and not missing,
       f"expected {code}" + (f" saying {list(says)}" if says else "")
       + ", got: " + " | ".join(out.strip().splitlines()[:2]))


def prints(label: str, source: str, allow: str, want: str) -> None:
    """This program must run and print exactly this."""
    got, out = run(source, allow)
    ok(label, got == 0 and said(out) == want,
       f"wanted {want!r}, got {said(out)!r}")


def audit_of(source: str) -> dict:
    SCRATCH.write_text(source, encoding="utf-8")
    return velaris.audit(source, path=str(SCRATCH)).as_dict()


# every case that starts from a key in the environment starts from this
KEY = 'fn main() uses io, env {\n    let key = env("API_KEY", "")\n'

print("SECRET")
print("-" * 62)
print("a Secret reaches nothing that emits it")
print("-" * 62)

# ---- 1. every builtin that emits refuses a Secret --------------------------
refused("a Secret cannot be printed",
        KEY + "    print(key)\n}\n", "E560",
        says=["Secret of Text", "env(), line 2", "print"])
refused("a Secret cannot be logged",
        KEY + "    log(key)\n}\n", "E560")
refused("a Secret cannot be written to a file",
        'fn main() uses io, env, fs {\n'
        '    write_file("out.txt", env("API_KEY", ""))\n}\n',
        "E560", says=["write_file", "fs"])
refused("a Secret cannot be the path read_file is given",
        'fn go() -> Text uses env, fs or fail {\n'
        '    return try read_file(env("API_KEY", ""))\n'
        '}\n\n'
        'fn main() uses io, env, fs {\n'
        '    check go() {\n'
        '        ok t {\n            print("read")\n        }\n'
        '        fail w {\n            print(w)\n        }\n'
        '    }\n}\n',
        "E560", says=["read_file"])
refused("a Secret cannot be the URL fetch is given",
        'fn go() -> Text uses env, net or fail {\n'
        '    return try fetch(env("API_KEY", ""))\n'
        '}\n\n'
        'fn main() uses io, env, net {\n'
        '    check go() {\n'
        '        ok t {\n            print("got")\n        }\n'
        '        fail w {\n            print(w)\n        }\n'
        '    }\n}\n',
        "E560", says=["fetch", "net"])
refused("a Secret cannot be the body post is given",
        'fn go() -> Text uses env, net or fail {\n'
        '    return try post("https://example.com", env("API_KEY", ""))\n'
        '}\n\n'
        'fn main() uses io, env, net {\n'
        '    check go() {\n'
        '        ok t {\n            print("sent")\n        }\n'
        '        fail w {\n            print(w)\n        }\n'
        '    }\n}\n',
        "E560")
refused("a Secret cannot be passed to Python",
        'fn main() uses io, env, ffi {\n'
        '    check py("os", "getenv", [env("API_KEY", "")]) {\n'
        '        ok v {\n            print("called")\n        }\n'
        '        fail w {\n            print(w)\n        }\n'
        '    }\n}\n',
        "E560", says=["ffi"])
refused("a Secret cannot become an exit code",
        KEY + "    exit_with(length(key))\n}\n", "E560",
        says=["Secret of Int"])
refused("a Secret cannot be the name env() is asked for",
        'fn main() uses io, env {\n'
        '    let which = env("WHICH", "")\n'
        '    let value = env(which, "")\n'
        '    print("done")\n}\n',
        "E560", says=["env"])
refused("a Secret cannot be a failure's reason",
        'fn go() -> Int uses env or fail {\n'
        '    fail env("API_KEY", "")\n'
        '}\n\n'
        'fn main() uses io, env {\n'
        '    check go() {\n'
        '        ok n {\n            print(n)\n        }\n'
        '        fail w {\n            print(w)\n        }\n'
        '    }\n}\n',
        "E560", says=["reason"])

# ---- 2. a structure is not a way around it ---------------------------------
print()
print("nor does a structure carry one past the check")
print("-" * 62)
refused("a record holding a Secret cannot be printed",
        'record Call {\n    url: Text\n    auth: Secret of Text\n}\n\n'
        'fn main() uses io, env {\n'
        '    let c = Call(url: "https://example.com", '
        'auth: env("API_KEY", ""))\n'
        '    print(c)\n}\n',
        "E560", says=["is Call", "env(), line 7"])
refused("nor one that holds it only through another record",
        'record Inner {\n    auth: Secret of Text\n}\n\n'
        'record Outer {\n    name: Text\n    inner: Inner\n}\n\n'
        'fn main() uses io, env {\n'
        '    let o = Outer(name: "x", inner: Inner(auth: env("K", "")))\n'
        '    print(o)\n}\n',
        "E560", says=["is Outer"])
refused("a list of Secrets cannot be printed",
        KEY + "    print([key, key])\n}\n", "E560",
        says=["List of Secret of Text"])
refused("a map whose values are Secrets cannot be printed",
        KEY + '    print({"k": key})\n}\n', "E560",
        says=["Map of Text to Secret of Text"])
refused("a list of records that hold one cannot be printed",
        'record Call {\n    auth: Secret of Text\n}\n\n'
        'fn main() uses io, env {\n'
        '    print([Call(auth: env("API_KEY", ""))])\n}\n',
        "E560", says=["List of Call"])
refused("a field taken out of a record is still a Secret",
        'record Call {\n    auth: Secret of Text\n}\n\n'
        'fn main() uses io, env {\n'
        '    let c = Call(auth: env("API_KEY", ""))\n'
        '    print(c.auth)\n}\n',
        "E560", says=["Secret of Text"])

# ---- 3. it cannot be laundered ---------------------------------------------
print()
print("nor can it be laundered")
print("-" * 62)
refused("a Secret through two helpers is still a Secret",
        'fn one(s: Secret of Text) -> Secret of Text {\n'
        '    return s\n}\n\n'
        'fn two(s: Secret of Text) -> Secret of Text {\n'
        '    return one(s)\n}\n\n'
        'fn main() uses io, env {\n'
        '    print(two(env("API_KEY", "")))\n}\n',
        "E560", says=["env(), line 10"])
refused("a signature that does not say Secret cannot return one",
        'fn load() -> Text uses env {\n'
        '    return env("API_KEY", "")\n}\n\n'
        'fn main() uses io, env {\n    print(load())\n}\n',
        "E503", says=["Secret of Text"])
refused("a generic function with effects takes no Secret",
        'fn show(x: T) uses io for any T {\n    print(x)\n}\n\n'
        'fn main() uses io, env {\n'
        '    show(env("API_KEY", ""))\n}\n',
        "E560", says=["generic", "uses io"])
refused("to_text does not launder one",
        KEY + "    print(to_text(key))\n}\n", "E560")
refused("format does not launder one",
        KEY + '    print(format("key {}", key))\n}\n', "E560")
refused("json_of does not launder one",
        KEY + "    print(json_of(key))\n}\n", "E560")
refused("upper does not launder one",
        KEY + "    print(upper(key))\n}\n", "E560")
refused("joining text to one does not launder it",
        KEY + '    print("key: " + key)\n}\n', "E560")
refused("a Secret cannot be assigned into a plain variable",
        KEY + '    let plain = "x"\n    plain = key\n    print(plain)\n}\n',
        "E501", says=["Secret of Text"])
refused("a Secret cannot be pushed into a plain list",
        KEY + '    let xs = ["a"]\n    print(push(xs, key))\n}\n', "E501")
refused("a Secret of a Secret is not a type",
        'fn f(x: Secret of Secret of Text) -> Int {\n'
        '    return 1\n}\n\n'
        'fn main() uses io {\n    print(f(1))\n}\n',
        "E562")

# ---- 4. pure computation keeps it; a comparison does not -------------------
print()
print("pure computation keeps it, and a comparison is one bit on purpose")
print("-" * 62)
refused("the length of a Secret is a Secret",
        KEY + "    print(length(key))\n}\n", "E560", says=["Secret of Int"])
refused("and-ing a Secret of Bool keeps it secret",
        'fn admin(flag: Secret of Bool) -> Secret of Bool {\n'
        '    return flag and true\n}\n\n'
        'fn main() uses io, env {\n'
        '    print(admin(env("A", "") == ""))\n}\n',
        "E501", says=["Secret of Bool"])
prints("a comparison over a Secret gives an ordinary Bool",
       KEY + '    if key == "" {\n        print("not set")\n'
             '    } else {\n        print("set")\n    }\n}\n',
       "env,io", "not set")
prints("...and so does comparing a Secret of Int with an Int",
       KEY + '    if length(key) < 10 {\n        print("short")\n'
             '    } else {\n        print("long")\n    }\n}\n',
       "env,io", "short")
refused("a Secret of Bool is not a condition",
        'fn admin(flag: Secret of Bool) -> Text {\n'
        '    if flag {\n        return "yes"\n    }\n'
        '    return "no"\n}\n\n'
        'fn main() uses io {\n    print("x")\n}\n',
        "E504", says=["Secret of Bool"])

# ---- 5. declassify ---------------------------------------------------------
print()
print("declassify is the only way out, and says so three times")
print("-" * 62)
DECL = ('fn main() uses io, env, declassify {\n'
        '    let key = env("API_KEY", "none")\n'
        '    print(declassify(key, "REASON"))\n}\n')
refused("declassify without the effect declared is refused",
        DECL.replace("uses io, env, declassify", "uses io, env"),
        "E300", says=["declassify"])
refused("declassify needs a reason written in the call",
        'fn main() uses io, env, declassify {\n'
        '    let key = env("API_KEY", "none")\n'
        '    let why = "built while running"\n'
        '    print(declassify(key, why))\n}\n',
        "E561", says=["written as text"])
refused("declassify refuses an empty reason",
        DECL.replace("REASON", "   "), "E561", says=["empty"])
refused("declassify refuses something that is not a Secret",
        'fn main() uses io, declassify {\n'
        '    print(declassify("plain", "why"))\n}\n',
        "E561", says=["takes a Secret"])
refused("declassify refuses a record that merely holds one",
        'record Call {\n    auth: Secret of Text\n}\n\n'
        'fn main() uses io, env, declassify {\n'
        '    let c = Call(auth: env("API_KEY", ""))\n'
        '    print(declassify(c, "why"))\n}\n',
        "E561", says=["inside it"])
prints("declassify with the effect and the grant lets the value out",
       DECL, "declassify,env,io", "none")
code, out = run(DECL, "env,io")
ok("declassify without the grant is refused while running (E310)",
   code != 0 and "E310" in out and "none" not in said(out),
   said(out)[:140])
prints("what declassify gives back is an ordinary Text",
       'fn main() uses io, env, declassify {\n'
       '    let key = env("API_KEY", "abcd")\n'
       '    let plain = declassify(key, "this demo shows it")\n'
       '    print(upper(plain) + " " + length(plain))\n}\n',
       "declassify,env,io", "ABCD 4")

# ---- 6. read_file_secret ---------------------------------------------------
print()
print("read_file_secret, the other source")
print("-" * 62)
refused("read_file_secret hands back a Secret",
        'fn main() uses io, fs {\n'
        '    check read_file_secret("nothing.txt") {\n'
        '        ok body {\n            print(body)\n        }\n'
        '        fail why {\n            print("could not read it")\n'
        '        }\n    }\n}\n',
        "E560", says=["read_file_secret(), line 2"])
prints("...and a program that keeps it runs",
       'fn main() uses io, fs {\n'
       '    check read_file_secret("nothing.txt") {\n'
       '        ok body {\n            print(length(body) == 0)\n'
       '        }\n'
       '        fail why {\n            print("could not read it")\n'
       '        }\n    }\n}\n',
       "fs:read,io", "could not read it")

# ---- 7. what velaris.audit/1 says ------------------------------------------
print()
print("what velaris.audit/1 says about both (velaris-spec 8.6)")
print("-" * 62)
doc = audit_of(KEY + '    if key == "" {\n        print("x")\n    }\n}\n')
ok("the audit reports env as a source of secrets",
   doc["secrets"]["sources"] == ["env"], str(doc["secrets"]))
ok("...and says the program never declassifies",
   doc["secrets"]["declassifies"] is False
   and doc["secrets"]["declassifications"] == [], str(doc["secrets"]))
ok("...and declassify is not among its effects",
   "declassify" not in doc["effects"], str(doc["effects"]))

doc = audit_of(DECL)
ok("a program that declassifies says so in the audit",
   doc["secrets"]["declassifies"] is True, str(doc["secrets"]))
ok("...with the reason and the function it happened in",
   doc["secrets"]["declassifications"] == [
       {"reason": "REASON", "function": "main", "line": 3}],
   str(doc["secrets"]["declassifications"]))
ok("...and declassify is an effect, so a budget can refuse it",
   "declassify" in doc["effects"] and "declassify" in doc["safe_command"],
   str(doc["effects"]) + " " + doc["safe_command"])

doc = audit_of('fn main() uses io, fs, declassify {\n'
               '    check read_file_secret("k.txt") {\n'
               '        ok body {\n'
               '            print(declassify(body, "printed on purpose"))\n'
               '        }\n'
               '        fail why {\n            print(why)\n        }\n'
               '    }\n}\n')
ok("read_file_secret is reported as a source too",
   doc["secrets"]["sources"] == ["read_file_secret"], str(doc["secrets"]))
ok("...and a program with both sources reports both",
   audit_of('fn main() uses io, env, fs {\n'
            '    let a = env("A", "")\n'
            '    check read_file_secret("k.txt") {\n'
            '        ok body {\n            print(a == body)\n        }\n'
            '        fail why {\n            print(why)\n        }\n'
            '    }\n}\n')["secrets"]["sources"]
   == ["env", "read_file_secret"], "")
ok("a program with no secret at all reports none",
   audit_of("fn main() uses io {\n    print(1)\n}\n")["secrets"]
   == {"sources": [], "declassifies": False, "declassifications": []}, "")

bad = audit_of(KEY + "    print(key)\n}\n")
ok("a program refused for leaking one still names its source",
   bad["ok"] is False
   and any(p["code"] == "E560" for p in bad["problems"])
   and bad["secrets"]["sources"] == ["env"], str(bad["secrets"]))

doc = audit_of('fn a(k: Secret of Text) -> Text uses declassify {\n'
               '    return declassify(k, "first reason")\n}\n\n'
               'fn main() uses io, env, declassify {\n'
               '    let k = env("K", "")\n'
               '    print(a(k))\n'
               '    print(declassify(k, "second reason"))\n}\n')
ok("every declassification is listed, in its own function",
   [(d["function"], d["reason"]) for d in doc["secrets"]
    ["declassifications"]]
   == [("a", "first reason"), ("main", "second reason")],
   str(doc["secrets"]["declassifications"]))

# ---- 8. an honest program -------------------------------------------------
print()
print("and an honest program still runs")
print("-" * 62)
prints("a program that uses a secret correctly runs",
       'record Request {\n    url: Text\n    auth: Secret of Text\n}\n\n'
       'fn build(key: Secret of Text, url: Text) -> Request {\n'
       '    return Request(url: url, auth: "Bearer " + key)\n}\n\n'
       'fn main() uses io, env {\n'
       '    let key = env("API_KEY", "k")\n'
       '    let r = build(key, "https://example.com/v1")\n'
       '    print("GET " + r.url)\n'
       '    if r.auth == "Bearer " {\n'
       '        print("no key was set")\n'
       '    } else {\n'
       '        print("a key was attached, and is not in this output")\n'
       '    }\n}\n',
       "env,io",
       "GET https://example.com/v1\n"
       "a key was attached, and is not in this output")
code, out = run((HERE / "examples" / "secret.vel").read_text(
    encoding="utf-8"), "env,io")
ok("examples/secret.vel runs and prints no key",
   code == 0 and "authorization: Bearer <the key" in out, said(out)[:120])
code, out = run((HERE / "examples" / "secret_bad.vel").read_text(
    encoding="utf-8"), "env,io")
ok("examples/secret_bad.vel is refused with E560 naming env()",
   code != 0 and "E560" in out and "env(), line" in out, said(out)[:160])

# ---- 9. the tracer and a broken promise do not print one -------------------
print()
print("and nothing prints one behind the program's back")
print("-" * 62)
SCRATCH.write_text(
    'fn keep(key: Secret of Text) -> Secret of Text {\n'
    '    return key\n}\n\n'
    'fn main() uses io, env {\n'
    '    let key = env("API_KEY", "sesame")\n'
    '    if keep(key) == "" {\n        print("empty")\n'
    '    } else {\n        print("held")\n    }\n}\n', encoding="utf-8")
done = subprocess.run(
    [sys.executable, str(VELARIS), "trace", str(SCRATCH),
     "--allow", "env,io"],
    capture_output=True, text=True, timeout=300, cwd=str(HERE))
trace = (done.stdout or "") + (done.stderr or "")
ok("velaris trace prints <secret> in place of the value",
   "sesame" not in trace and "<secret>" in trace, trace.strip()[:200])

SCRATCH.write_text(
    'fn keep(key: Secret of Text) -> Secret of Text\n'
    '    requires length(key) > 99\n'
    '{\n    return key\n}\n\n'
    'fn main() uses io, env {\n'
    '    let key = env("API_KEY", "sesame")\n'
    '    if keep(key) == "" {\n        print("empty")\n'
    '    } else {\n        print("held")\n    }\n}\n', encoding="utf-8")
done = subprocess.run(
    [sys.executable, str(VELARIS), str(SCRATCH), "--allow", "env,io"],
    capture_output=True, text=True, timeout=300, cwd=str(HERE))
broke = (done.stdout or "") + (done.stderr or "")
ok("a broken promise about a secret prints <secret>, not the value",
   done.returncode != 0 and "sesame" not in broke and "<secret>" in broke,
   broke.strip()[:200])

SCRATCH.unlink(missing_ok=True)
print("-" * 62)
print(f"{PASS[0]} right, {FAIL[0]} wrong")
sys.exit(1 if FAIL[0] else 0)
