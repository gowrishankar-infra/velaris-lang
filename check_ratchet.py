#!/usr/bin/env python3
"""The capability ratchet: a widening must never pass, and a change that
does not widen must never fail.

`velaris capabilities check` holds a tree to the surface declared in
velaris.capabilities. The point of it is gradual change - capability
assembled across many commits, each of which looks fine on its own -
and that is only caught if every commit is compared with the declared
baseline, never with the commit before it. So this suite does not
assert that the check catches a widening in one diff; it builds real
git histories and asserts what the check says at every commit of them,
and it holds a previous-commit comparison beside it to show where that
one goes blind.

Every case runs the command line in a scratch directory. Nothing here
needs the prover or the network.

    python check_ratchet.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
VELARIS = HERE / "velaris.py"
sys.path.insert(0, str(HERE))
import velaris  # noqa: E402

try:
    from jsonschema import Draft4Validator
except ImportError:                        # the SARIF case says it skipped
    Draft4Validator = None

HAVE_GIT = shutil.which("git") is not None


class Tree:
    """A scratch directory of .vel files, optionally a git repository."""

    def __init__(self, files: dict, git: bool = False):
        self.root = Path(tempfile.mkdtemp(prefix="velaris-ratchet-"))
        self.git_repo = git
        if git:
            self.git("init", "-q")
            for key, value in (("user.name", "ratchet"),
                               ("user.email", "ratchet@example.invalid"),
                               ("commit.gpgsign", "false"),
                               ("core.autocrlf", "false")):
                self.git("config", key, value)
        self.write(files)

    def write(self, files: dict) -> None:
        for name, text in files.items():
            path = self.root / name
            if text is None:
                path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")

    def velaris(self, *words):
        return subprocess.run([sys.executable, str(VELARIS), *words],
                              cwd=str(self.root), capture_output=True,
                              text=True, encoding="utf-8", timeout=600)

    def init(self, *more):
        return self.velaris("capabilities", "init", ".", *more)

    def check(self):
        """(exit code, the JSON result, or {})"""
        done = self.velaris("capabilities", "check", ".", "--json")
        try:
            return done.returncode, json.loads(done.stdout)
        except ValueError:
            return done.returncode, {"_stdout": done.stdout,
                                     "_stderr": done.stderr}

    def review(self, ref):
        done = self.velaris("review", "--against", ref, "--json")
        try:
            return json.loads(done.stdout)
        except ValueError:
            return {"_stderr": done.stderr, "_stdout": done.stdout}

    def git(self, *words):
        return subprocess.run(["git", *words], cwd=str(self.root),
                              capture_output=True, text=True, timeout=120)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def baseline(self) -> dict:
        return json.loads((self.root / "velaris.capabilities")
                          .read_text(encoding="utf-8"))

    def set_baseline(self, doc: dict) -> None:
        (self.root / "velaris.capabilities").write_text(
            velaris.capabilities_text(doc), encoding="utf-8", newline="\n")

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


def kinds(result: dict) -> list:
    return sorted((f["kind"], f.get("grant") or f.get("effect")
                   or f.get("function")) for f in result.get("findings", []))


def grant_finding(result: dict, grant: str) -> dict:
    return next((f for f in result.get("findings", [])
                 if f["kind"] == "grant" and f["grant"] == grant), {})


# ---- the programs the cases are built from ---------------------------------

GREETER = '''import "lib/text.vel"

fn main() uses io {
    print(greeting("world"))
}
'''

TEXT_LIB = '''fn greeting(who: Text) -> Text {
    return "hello, " + who
}
'''

PINGER = '''fn ping() -> Int uses net or fail {
    return try fetch_status("https://api.example.com/ping")
}

fn main() uses io, net {
    for i in 0 to {N} {
        check ping() {
            ok code {
                print(to_text(code))
            }
            fail why {
                print(why)
            }
        }
    }
}
'''


def pinger(n, host="api.example.com", note="") -> str:
    return (PINGER.replace("{N}", str(n))
            .replace("api.example.com", host)
            .replace("fn main() uses io, net {",
                     "fn main() uses io, net {" + (
                         f'\n    print("{note}")' if note else "")))


READER = '''fn main() uses io, fs {
    check read_file("{PATH}") {
        ok text {
            print(text)
        }
        fail why {
            print(why)
        }
    }
}
'''


def reader(path: str) -> str:
    return READER.replace("{PATH}", path)


def main() -> int:
    passed = failed = 0
    trees = []

    def ok(label, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  ok       {label}")
            passed += 1
        else:
            print(f"  BROKEN   {label}")
            if detail:
                print(f"           {str(detail)[:600]}")
            failed += 1

    def skip(label, why):
        print(f"  skip     {label} ({why})")

    def tree(files, git=False):
        t = Tree(files, git)
        trees.append(t)
        return t

    try:
        # ------------------------------------------------------------------
        print("a gradual widening: six commits, each innocent on its own")
        print("-" * 62)
        if not HAVE_GIT:
            skip("the six-commit history", "git is not installed")
        else:
            t = tree({"app.vel": GREETER, "lib/text.vel": TEXT_LIB}, git=True)
            t.init()
            t.commit("0: a greeter, and its declared surface")
            steps = [
                ("1: a text helper, pure", {
                    "lib/tidy.vel": 'fn tidy(t: Text) -> Text {\n'
                                    '    return lower(t)\n}\n'}),
                ("2: the greeting uses it", {
                    "lib/text.vel": 'import "tidy.vel"\n\n'
                                    'fn greeting(who: Text) -> Text {\n'
                                    '    return "hello, " + tidy(who)\n}\n'}),
                ("3: a summary of lines, pure", {
                    "lib/summary.vel": 'fn summary(lines: List of Text) '
                                       '-> Text {\n'
                                       '    return to_text(length(lines)) + " lines"\n}\n'}),
                ("4: main prints a summary", {
                    "app.vel": 'import "lib/text.vel"\n'
                               'import "lib/summary.vel"\n\n'
                               'fn main() uses io {\n'
                               '    print(greeting("world"))\n'
                               '    print(summary(["a", "b"]))\n}\n'}),
                ("5: an address, as text", {
                    "lib/summary.vel": 'fn summary(lines: List of Text) '
                                       '-> Text {\n'
                                       '    return to_text(length(lines)) + " lines"\n}\n\n'
                                       'fn endpoint() -> Text {\n'
                                       '    return "https://collector.'
                                       'example.net/v1"\n}\n'}),
                ("6: the summary is delivered, three calls down", {
                    "lib/deliver.vel": 'fn send(body: Text) -> Text '
                                       'uses net or fail {\n'
                                       '    return try post("https://'
                                       'collector.example.net/v1", body)\n'
                                       '}\n\n'
                                       'fn deliver(body: Text) -> Text '
                                       'uses net {\n'
                                       '    check send(body) {\n'
                                       '        ok r {\n'
                                       '            return r\n'
                                       '        }\n'
                                       '        fail why {\n'
                                       '            return why\n'
                                       '        }\n'
                                       '    }\n}\n',
                    "lib/summary.vel": 'import "deliver.vel"\n\n'
                                       'fn summary(lines: List of Text) '
                                       '-> Text uses net {\n'
                                       '    return deliver(to_text(length(lines)))\n}\n\n'
                                       'fn endpoint() -> Text {\n'
                                       '    return "https://collector.'
                                       'example.net/v1"\n}\n',
                    "app.vel": 'import "lib/text.vel"\n'
                               'import "lib/summary.vel"\n\n'
                               'fn main() uses io, net {\n'
                               '    print(greeting("world"))\n'
                               '    print(summary(["a", "b"]))\n}\n'}),
            ]
            codes, reviews = [], []
            for message, files in steps:
                t.write(files)
                t.commit(message)
                code, result = t.check()
                codes.append((message, code, result))
                reviews.append(t.review("HEAD~1").get("risk"))
            ok("commits 1 to 5 each pass against the baseline: nothing in "
               "them widens the surface",
               [c for _, c, _ in codes[:5]] == [0] * 5,
               [(m, c, kinds(r)) for m, c, r in codes[:5]])
            code6, r6 = codes[5][1], codes[5][2]
            net = grant_finding(r6, "net:collector.example.net")
            ok("commit 6 FAILS against the baseline", code6 == 1, kinds(r6))
            ok("...naming what widened: net, a new effect, to "
               "collector.example.net",
               net.get("new_effect") is True
               and net.get("outside_surface") is True, net)
            prog = next((q for q in net.get("programs", [])
                         if q["file"] == "app.vel"), {})
            origin = (prog.get("origins") or [{}])[0]
            ok("...and the file, function and line that introduced it, and "
               "the three calls from main that reach it",
               origin.get("file") == "lib/deliver.vel"
               and origin.get("function") == "send"
               and origin.get("line") == 2 and origin.get("call") == "post"
               and prog.get("reached_from")
               == ["main", "summary", "deliver", "send"], prog)
            gained = [f for f in r6.get("findings", [])
                      if f["kind"] == "function"]
            ok("...and that main, which the baseline recorded, gained net",
               [(f["file"], f["function"], f["gained"]) for f in gained]
               == [("app.vel", "main", ["net"])], gained)
            ok("a review of each commit against the one before it calls "
               "1 to 5 low and 6 high",
               reviews == ["low"] * 5 + ["high"], reviews)
            ok("the check read no history: it passes again once the "
               "baseline is widened in a commit of its own",
               t.init("--force").returncode == 0 and t.check()[0] == 0)

        # ------------------------------------------------------------------
        print()
        print("against the declared baseline, never the previous commit")
        print("-" * 62)
        if not HAVE_GIT:
            skip("the history of small steps", "git is not installed")
        else:
            t = tree({"poll.vel": pinger(10)}, git=True)
            t.init()
            t.commit("a poller, ten requests a run, declared")
            t.write({"poll.vel": pinger(20)})
            t.commit("twenty")
            code_a, ra = t.check()
            risk_a = t.review("HEAD~1").get("risk")
            t.write({"poll.vel": pinger(20, note="polling")})
            t.commit("an unrelated change after the widening was merged")
            code_b, rb = t.check()
            rev_b = t.review("HEAD~1")
            ok("a widening that is merged anyway goes on failing against "
               "the baseline at every later commit",
               code_a == 1 and code_b == 1 and kinds(rb)
               == [("count", "net")], kinds(rb))
            ok("...while a comparison with the previous commit sees nothing "
               "the moment it is one commit old",
               risk_a == "high" and rev_b.get("risk") == "low"
               and not rev_b.get("surface", {}).get("widened"), rev_b)
            for n in (40, 80, 160, 320, 640, 1000):
                t.write({"poll.vel": pinger(n)})
                t.commit(f"{n}")
            code_c, rc = t.check()
            rev_c = t.review("HEAD~1")
            count = next((f for f in rc.get("findings", [])
                          if f["kind"] == "count"), {})
            step = next((f for f in rev_c.get("surface", {})
                         .get("widened", []) if f["kind"] == "count"), {})
            ok("seven small steps are as visible as one: the check reports "
               "1000 against the declared 10",
               code_c == 1 and count.get("current") == 1000
               and count.get("surface_allows") == 10, count)
            ok("...where the previous commit shows one step, 640 to 1000",
               step.get("current") == 1000
               and step.get("surface_allows") == 640, step)
            doc = t.baseline()
            doc["surface"]["counts"] = {"net": 1000}
            doc["programs"][0]["counts"] = {"net": 1000}
            t.set_baseline(doc)
            t.commit("accept 1000 requests a run")
            rev = t.review("HEAD~1")
            ok("accepting it is an edit to the baseline, and a review names "
               "that edit and calls it high",
               t.check()[0] == 0 and rev.get("risk") == "high"
               and rev.get("declared", {}).get("widened")
               == ["net count 10 -> 1000"], rev.get("declared"))
            (t.root / "velaris.capabilities").unlink()
            t.commit("no baseline, no ratchet")
            rev = t.review("HEAD~1")
            ok("removing the baseline turns the ratchet off, and a review "
               "says so and calls it high",
               rev.get("risk") == "high"
               and rev.get("declared", {}).get("removed") is True,
               rev.get("declared"))

            # The working directory's path and the one git reports for the
            # repository can be spelled differently - a Windows short name
            # (RUNNER~1 on CI), a junction, a symbolic link (macOS's /var
            # is /private/var). 4.0.0 compared the two as text and read the
            # ref's files from the wrong place; review must ask git.
            t = tree({"sub/app.vel": GREETER, "sub/lib/text.vel": TEXT_LIB},
                     git=True)
            t.commit("a tree under a subdirectory")
            # uncommitted: the working tree now needs net, the ref does not,
            # so only a review that really reads the ref's files sees a
            # widening
            t.write({"sub/app.vel": GREETER.replace(
                "fn main() uses io {",
                "fn main() uses io, net {\n"
                '    check fetch_status("https://x.example.org") {\n'
                "        ok s {\n"
                "            print(to_text(s))\n"
                "        }\n"
                "        fail w {\n"
                "            print(w)\n"
                "        }\n"
                "    }")})
            link = Path(tempfile.mkdtemp(prefix="velaris-link-")) / "repo"
            made = False
            try:
                if os.name == "nt":
                    made = subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(link),
                         str(t.root)], capture_output=True).returncode == 0
                else:
                    os.symlink(t.root, link, target_is_directory=True)
                    made = True
            except OSError:
                made = False
            if not made:
                skip("review from a path spelled unlike git's",
                     "cannot make a junction or link here")
            else:
                done = subprocess.run(
                    [sys.executable, str(VELARIS), "review", "--against",
                     "HEAD", ".", "--json"], cwd=str(link / "sub"),
                    capture_output=True, text=True, encoding="utf-8",
                    timeout=600)
                try:
                    rev = json.loads(done.stdout)
                except ValueError:
                    rev = {"_stderr": done.stderr}
                ok("review from a path spelled unlike git's own reads the "
                   "ref's files, not the working tree: io before, net "
                   "after, high",
                   rev.get("risk") == "high"
                   and rev.get("surface", {}).get("before", {})
                   .get("grants") == ["io"]
                   and "net:x.example.org" in rev.get("surface", {})
                   .get("after", {}).get("grants", []), rev)
                if os.name == "nt":
                    os.rmdir(link)             # the junction, not its target
                else:
                    link.unlink()

        # ------------------------------------------------------------------
        print()
        print("widenings, each by another route")
        print("-" * 62)
        store = ('fn save(line: Text) uses fs {\n'
                 '    write_file("out/log.txt", line)\n}\n')
        t = tree({"app.vel": GREETER, "lib/text.vel": TEXT_LIB,
                  "lib/store.vel": store})
        t.init()
        t.write({"app.vel": 'import "lib/text.vel"\n'
                            'import "lib/store.vel"\n\n'
                            'fn main() uses io, fs {\n'
                            '    let g = greeting("world")\n'
                            '    save(g)\n'
                            '    print(g)\n}\n'})
        code, r = t.check()
        g = grant_finding(r, "fs:write:out/log.txt")
        ok("through an import: app.vel now writes through lib/store.vel - "
           "the repository's surface already had that write, app.vel's "
           "entry did not, and it FAILS (W3, not W1)",
           code == 1 and g.get("outside_surface") is False
           and g.get("rules") == ["W3"]
           and [q["file"] for q in g.get("programs", [])
                if q["outside_entry"]] == ["app.vel"], r.get("findings"))
        ok("...and main is named as the function that gained fs",
           ("function", "main") in kinds(r), kinds(r))

        t = tree({"app.vel": GREETER, "lib/text.vel": TEXT_LIB})
        t.init()
        t.write({"app.vel": 'import "lib/text.vel"\n'
                            'import "http.vel" as http\n\n'
                            'fn main() uses io, net {\n'
                            '    check http.get("https://api.example.com") {\n'
                            '        ok body {\n'
                            '            print(body)\n'
                            '        }\n'
                            '        fail why {\n'
                            '            print(greeting(why))\n'
                            '        }\n'
                            '    }\n}\n'})
        code, r = t.check()
        g = grant_finding(r, "net")
        origins = [s["file"] for q in g.get("programs", [])
                   for s in q["origins"]]
        ok("through a standard-library module: http.vel brings net, "
           "unscoped because its URL is a parameter, and it FAILS",
           code == 1 and g.get("new_effect") is True
           and any(o.startswith("<stdlib>/http.vel") for o in origins),
           g)

        t = tree({"peek.vel": 'fn main() uses io, fs {\n'
                              '    print(to_text(file_exists("./data")))\n}\n'})
        t.init()
        t.write({"peek.vel": 'fn main() uses io, fs {\n'
                             '    print(to_text(file_exists("./")))\n}\n'})
        code, r = t.check()
        ok("a path prefix widened from ./data to ./ FAILS, naming fs:read:./",
           code == 1 and grant_finding(r, "fs:read:./").get(
               "outside_surface") is True, kinds(r))

        t = tree({"poll.vel": pinger(10)})
        t.init()
        t.write({"poll.vel": pinger(1000)})
        code, r = t.check()
        c = next((f for f in r.get("findings", []) if f["kind"] == "count"),
                 {})
        ok("a count raised from 10 to 1000 FAILS (W2, W4), naming the loop",
           code == 1 and c.get("current") == 1000
           and c.get("surface_allows") == 10
           and c.get("rules") == ["W2", "W4"]
           and "turns at most 1000" in (c.get("why") or ""), c)

        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"poll.vel": pinger(3, host="*.example.com")})
        code, r = t.check()
        ok("a host changed from api.example.com to *.example.com FAILS: a "
           "star in a URL is taken as any host",
           code == 1 and grant_finding(r, "net").get("outside_surface"),
           kinds(r))
        cov = velaris._covers
        gp = velaris._grant_parts
        ok("...and as grants, net:*.example.com is not inside "
           "net:api.example.com, while the reverse is",
           not cov(gp("net:api.example.com"), gp("net:*.example.com"))
           and cov(gp("net:*.example.com"), gp("net:api.example.com")))

        unbounded_reader = (
            'fn load(path: Text) -> Text uses fs or fail {\n'
            '    return try read_file(path)\n}\n\n'
            'fn show(line: Text) -> Text {\n'
            '    return "> " + line\n}\n\n'
            'fn main() uses io, fs {\n'
            '    for a in args() {\n'
            '        check load(a) {\n'
            '            ok text {\n'
            '                print(show(text))\n'
            '            }\n'
            '            fail why {\n'
            '                print(why)\n'
            '            }\n'
            '        }\n'
            '    }\n}\n')
        t = tree({"cat.vel": unbounded_reader})
        t.init()
        t.write({"cat.vel": unbounded_reader.replace(
            'fn show(line: Text) -> Text {\n'
            '    return "> " + line\n}\n',
            'fn show(line: Text) -> Text uses fs {\n'
            '    if file_exists(line) {\n'
            '        return "> " + line\n'
            '    }\n'
            '    return line\n}\n')})
        code, r = t.check()
        ok("an effect added to a function that had none, while the "
           "program's grants and counts stay exactly as they were, is "
           "still REPORTED",
           code == 1 and kinds(r) == [("function", "show")]
           and r["findings"][0]["gained"] == ["fs"], r.get("findings"))

        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"poll.vel": PINGER.replace("{N}", "3").replace(
            '"https://api.example.com/ping"',
            'lower("HTTPS://API.EXAMPLE.COM/PING")')})
        code, r = t.check()
        ok("a URL built while running makes net unscoped, and it FAILS "
           "against a baseline naming the host",
           code == 1 and grant_finding(r, "net").get("outside_surface"),
           kinds(r))

        t = tree({"read.vel": reader("data/in.csv")})
        t.init()
        t.write({"read.vel": reader("data/in.csv").replace(
            'check read_file("data/in.csv")',
            'check read_file(lower("DATA/IN.CSV"))')})
        code, r = t.check()
        ok("a path built while running makes fs:read unscoped, and it FAILS",
           code == 1 and grant_finding(r, "fs:read").get("outside_surface"),
           kinds(r))

        t = tree({"read.vel": reader("data/in.csv")})
        t.init()
        t.write({"read.vel": reader("data/in.csv").replace(
            "fn main() uses io, fs {",
            "fn main() uses io, fs {\n    write_file(\"data/in.csv\", \"x\")")})
        code, r = t.check()
        ok("a write added to a path that was only read FAILS, naming "
           "fs:write:data/in.csv",
           code == 1 and grant_finding(r, "fs:write:data/in.csv")
           .get("new_effect") is False, kinds(r))

        py_prog = ('fn root(n: Text) -> Text uses ffi or fail {\n'
                   '    let args = [n]\n'
                   '    return try py("{MOD}", "sqrt", args)\n}\n\n'
                   'fn main() uses io, ffi {\n'
                   '    check root("16") {\n'
                   '        ok v {\n'
                   '            print(v)\n'
                   '        }\n'
                   '        fail why {\n'
                   '            print(why)\n'
                   '        }\n'
                   '    }\n}\n')
        t = tree({"root.vel": py_prog.replace("{MOD}", "math")})
        t.init()
        t.write({"root.vel": py_prog.replace("{MOD}", "cmath")})
        code, r = t.check()
        ok("a new Python module FAILS, naming ffi:cmath",
           code == 1 and bool(grant_finding(r, "ffi:cmath")), kinds(r))
        computed = py_prog.replace('py("{MOD}"', 'py(lower("MATH")')
        t.write({"root.vel": computed})
        code, r = t.check()
        ok("a module named by a value built while running makes ffi "
           "unscoped, and it FAILS - the audit now says so too (ffi_any)",
           code == 1 and bool(grant_finding(r, "ffi"))
           and velaris.audit(computed).ffi_any is True, kinds(r))

        t = tree({"a.vel": pinger(3), "b.vel": pinger(3, host="cdn.example.org")})
        t.init()
        t.write({"b.vel": pinger(3, host="api.example.com")})
        code, r = t.check()
        g = grant_finding(r, "net:api.example.com")
        ok("a recorded program reaching a host another program already "
           "had FAILS - the surface is unchanged, its own entry is not",
           code == 1 and g.get("outside_surface") is False
           and [q["file"] for q in g.get("programs", [])] == ["b.vel"],
           r.get("findings"))

        looping = pinger(3).replace("for i in 0 to 3 {",
                                    "for h in args() {")
        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"poll.vel": looping})
        code, r = t.check()
        c = next((f for f in r.get("findings", []) if f["kind"] == "count"),
                 {})
        ok("a loop with no fixed number of turns has no bound, and FAILS "
           "against a count of 3, saying which loop",
           code == 1 and c.get("current") is None
           and "no fixed number of turns" in (c.get("why") or ""), c)

        recursive = ('fn poll(n: Int) -> Int uses net {\n'
                     '    if n <= 0 {\n'
                     '        return 0\n'
                     '    }\n'
                     '    check fetch_status("https://api.example.com") {\n'
                     '        ok s {\n'
                     '            return poll(n - 1)\n'
                     '        }\n'
                     '        fail why {\n'
                     '            return 0\n'
                     '        }\n'
                     '    }\n}\n\n'
                     'fn main() uses io, net {\n'
                     '    print(to_text(poll(5)))\n}\n')
        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"poll.vel": recursive})
        code, r = t.check()
        c = next((f for f in r.get("findings", []) if f["kind"] == "count"),
                 {})
        ok("recursion has no bound either, and the finding says recursion",
           code == 1 and c.get("current") is None
           and "call itself" in (c.get("why") or ""), c)

        t = tree({"repo/run.vel": 'import "../ext/app.vel"\n',
                  "ext/app.vel": 'fn main() uses io {\n'
                                 '    print("hi")\n}\n'})
        t.velaris("capabilities", "init", "repo")
        t.write({"ext/app.vel": 'fn main() uses io, net {\n'
                                '    check fetch("https://x.example.org") {\n'
                                '        ok b {\n'
                                '            print(b)\n'
                                '        }\n'
                                '        fail w {\n'
                                '            print(w)\n'
                                '        }\n'
                                '    }\n}\n'})
        done = t.velaris("capabilities", "check", "repo", "--json")
        r = json.loads(done.stdout or "{}")
        ok("a program whose main is imported from outside the checked tree "
           "needs what that main does, and it FAILS when that widens",
           done.returncode == 1
           and bool(grant_finding(r, "net:x.example.org")), kinds(r))

        t = tree({".ci/deploy.vel": 'fn main() uses io {\n'
                                    '    print("deploy")\n}\n'})
        t.init()
        t.write({".ci/deploy.vel": pinger(1)})
        code, r = t.check()
        ok("a program in a hidden directory is part of the repository, and "
           "its widening FAILS", code == 1 and ("grant", "net:api.example"
                                                ".com") in kinds(r),
           kinds(r))

        t = tree({"read.vel": reader("data/in.csv")})
        t.init()
        doc = t.baseline()
        doc["surface"]["grants"] = ["fs:read:data", "io"]
        doc["programs"][0]["grants"] = ["fs:read:data", "io"]
        t.set_baseline(doc)
        t.write({"read.vel": reader("data/..\\\\..\\\\secret.txt")})
        code, r = t.check()
        ok("a path that climbs out with backslashes is not taken as inside "
           "a prefix: on Windows data/..\\..\\x leaves data, so it FAILS",
           code == 1 and r.get("widened"), kinds(r))

        # ------------------------------------------------------------------
        print()
        print("changes that do not widen must pass")
        print("-" * 62)
        t = tree({"poll.vel": pinger(3), "read.vel": reader("data/in.csv")})
        t.init()
        t.write({"poll.vel": pinger(3).replace(
            'return try fetch_status("https://api.example.com/ping")',
            'let base = "https://api.example.com"\n'
            '    let url = base + "/ping"\n'
            '    return try fetch_status(url)'),
            "read.vel": reader("data/in.csv").replace(
                'check read_file("data/in.csv")',
                'let where = "data/in.csv"\n'
                '    check read_file(where)')})
        code, r = t.check()
        ok("a literal URL or path moved into a variable bound once passes: "
           "it is still a fixed host and path, not one built while running",
           code == 0 and not r.get("findings"), r)
        t.write({"poll.vel": pinger(3).replace(
            "for i in 0 to 3 {", 'let hosts = ["a", "b", "c"]\n'
                                 '    for h in hosts {')})
        code, r = t.check()
        ok("...and a loop over a list held in a variable keeps its bound of "
           "3", code == 0 and not r.get("findings"), r)
        t = tree({"poll.vel": pinger(1000), "read.vel": reader("data/in.csv"),
                  "b.vel": pinger(3, host="cdn.example.org")})
        t.init()
        t.write({"poll.vel": pinger(10),
                 "read.vel": 'fn main() uses io {\n    print("no file")\n}\n',
                 "b.vel": None})
        code, r = t.check()
        ok("narrowing - a lower count, an effect dropped, a program "
           "removed - passes, and is reported as narrowing",
           code == 0 and not r.get("findings") and r.get("narrowed")
           and any("no longer needed" in n for n in r["narrowed"]),
           r)

        multi = ('import "lib/text.vel"\n'
                 'import "lib/store.vel"\n\n'
                 'fn helper(n: Int) -> Int {\n'
                 '    return n + 1\n}\n\n'
                 'fn main() uses io, fs {\n'
                 '    let total = helper(1)\n'
                 '    let g = greeting("x")\n'
                 '    save(g)\n'
                 '    for i in 0 to 4 {\n'
                 '        print(to_text(file_exists("data/in.csv")))\n'
                 '    }\n'
                 '    print(to_text(total))\n}\n')
        t = tree({"app.vel": multi, "lib/text.vel": TEXT_LIB,
                  "lib/store.vel": store})
        t.init()
        before = t.baseline()
        shuffled = ('// the same program, rearranged\n'
                    'import "lib/store.vel"\n'
                    'import "lib/text.vel"\n\n\n'
                    'fn main() uses fs, io {\n'
                    '    let g   =   greeting("x")\n'
                    '    let sum = helper(1)      // renamed local\n'
                    '    for i in 0 to 4 {\n'
                    '        print(to_text(file_exists("data/in.csv")))\n'
                    '    }\n'
                    '    save(g)\n'
                    '    print(to_text(sum))\n}\n\n'
                    'fn helper(n: Int) -> Int {\n'
                    '    return n + 1\n}\n')
        t.write({"app.vel": shuffled})
        code, r = t.check()
        ok("reordering functions, imports, uses clauses and statements, "
           "renaming locals and reformatting pass with nothing reported",
           code == 0 and not r.get("findings") and not r.get("narrowed"),
           r)
        t.init("--force")
        after = t.baseline()
        ok("...and the baseline written from the rearranged tree is the "
           "same, bar the date",
           dict(before, date=None) == dict(after, date=None))
        fmt = t.velaris("fmt", "app.vel")
        code, r = t.check()
        ok("velaris fmt on it changes nothing either", fmt.returncode == 0
           and code == 0 and not r.get("findings"), fmt.stderr or r)

        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"lib/math.vel": 'fn twice(n: Int) -> Int {\n'
                                 '    return n * 2\n}\n'})
        code, r = t.check()
        ok("a file added with no effects passes", code == 0
           and not r.get("findings"), r)
        t.write({"other.vel": pinger(2)})
        code, r = t.check()
        ok("a new program that stays inside the declared surface - the "
           "same host, no more requests a run - passes too",
           code == 0 and not r.get("findings"), r)

        counter = ('fn main() uses io, fs {\n'
                   '    let i = 0\n'
                   '    while i < 4 {\n'
                   '        print(to_text(file_exists("data/in.csv")))\n'
                   '        i = i + 1\n'
                   '    }\n}\n')
        t = tree({"count.vel": counter})
        t.init()
        t.write({"count.vel": counter.replace(
            "    let i = 0\n",
            "    let i = 0\n"
            "    let noise = 2 * 3\n"
            '    print("starting")\n'
            "    print(to_text(noise))\n")})
        code, r = t.check()
        ok("statements added between a counter's start and its loop keep "
           "the bound of 4, so no count is reported",
           code == 0 and not r.get("findings")
           and t.baseline()["surface"]["counts"] == {"fs": 4}, r)
        t = tree({"app.vel": multi, "lib/text.vel": TEXT_LIB,
                  "lib/store.vel": store})
        t.init()
        t.write({"app.vel": multi.replace("helper", "plus_one")})
        code, r = t.check()
        ok("a function renamed, effects unchanged, passes", code == 0
           and not r.get("findings"), r)
        t.write({"app.vel": multi.replace(
            "fn helper(n: Int) -> Int {\n    return n + 1\n}\n\n", "")
            .replace('import "lib/text.vel"\n',
                     'import "lib/text.vel"\nimport "lib/helper.vel"\n'),
            "lib/helper.vel": 'fn helper(n: Int) -> Int {\n'
                              '    return n + 1\n}\n'})
        code, r = t.check()
        ok("a function moved to another file passes", code == 0
           and not r.get("findings"), r)
        t.write({"app.vel": multi.replace("fn main() uses io, fs {",
                                          "fn main() uses io {")})
        code, r = t.check()
        ok("a program that stops compiling passes, with a note: it cannot "
           "run, so it adds nothing until it compiles again",
           code == 0 and any("does not compile" in n
                             for n in r.get("notes", [])), r)

        # ------------------------------------------------------------------
        print()
        print("the declared surface is the operator's to widen")
        print("-" * 62)
        t = tree({"read.vel": reader("data/sub/x.csv")})
        t.init()
        doc = t.baseline()
        doc["surface"]["grants"] = ["fs:read:data", "io"]
        doc["programs"][0]["grants"] = ["fs:read:data", "io"]
        t.set_baseline(doc)
        t.write({"read.vel": reader("data/other/y.csv")})
        code_in, _ = t.check()
        t.write({"read.vel": reader("config.csv")})
        code_out, r_out = t.check()
        ok("a hand-written prefix covers any path under it, and nothing "
           "outside it", code_in == 0 and code_out == 1
           and bool(grant_finding(r_out, "fs:read:config.csv")),
           kinds(r_out))

        t = tree({"poll.vel": pinger(3)})
        t.init()
        doc = t.baseline()
        doc["surface"]["grants"] = ["io", "net:*.example.com"]
        doc["programs"][0]["grants"] = ["io", "net:*.example.com"]
        t.set_baseline(doc)
        t.write({"poll.vel": pinger(3, host="cdn.example.com")})
        code_w, _ = t.check()
        t.write({"poll.vel": pinger(3, host="example.com")})
        code_parent, _ = t.check()
        ok("a declared wildcard covers one label under it, not the domain "
           "itself", code_w == 0 and code_parent == 1)
        doc["surface"]["grants"] = ["io", "net:api.example.com:443"]
        doc["programs"][0]["grants"] = ["io", "net:api.example.com:443"]
        t.set_baseline(doc)
        t.write({"poll.vel": pinger(3)})
        code_noport, _ = t.check()
        t.write({"poll.vel": pinger(3, host="api.example.com:443")})
        code_port, _ = t.check()
        ok("a grant with a port covers a URL that writes that port, and "
           "not one that writes none", code_noport == 1 and code_port == 0)

        # ------------------------------------------------------------------
        print()
        print("versions, and baselines that cannot be read")
        print("-" * 62)
        t = tree({"poll.vel": pinger(3)})
        t.init()
        doc = t.baseline()
        doc["velaris_version"] = "1.0.0"
        t.set_baseline(doc)
        code, r = t.check()
        ok("a baseline from an older Velaris WARNS and does not fail",
           code == 0 and any("older" in w for w in r.get("warnings", [])),
           r.get("warnings"))
        doc["velaris_version"] = "99.0.0"
        t.set_baseline(doc)
        code, r = t.check()
        ok("...and one from another version warns the same way",
           code == 0 and r.get("warnings"), r.get("warnings"))
        doc["velaris_version"] = "1.0.0"
        t.set_baseline(doc)
        t.write({"poll.vel": pinger(4)})
        code, r = t.check()
        ok("...but the warning never hides a widening", code == 1
           and r.get("warnings"), kinds(r))

        t = tree({"poll.vel": pinger(3)})
        first = t.init()
        text = (t.root / "velaris.capabilities").read_text(encoding="utf-8")
        again = t.init()
        ok("init will not replace a baseline without --force",
           first.returncode == 0 and again.returncode == 1
           and (t.root / "velaris.capabilities").read_text(
               encoding="utf-8") == text, again.stderr)
        ok("...and --force records it again", t.init("--force").returncode
           == 0)
        (t.root / "velaris.capabilities").unlink()
        none = t.velaris("capabilities", "check", ".")
        ok("check with no baseline exits 2, and says how to write one",
           none.returncode == 2 and "capabilities init" in none.stderr,
           none.stderr)
        for label, body in [
                ("the provisional /0 form",
                 '{"schema": "velaris.capabilities/0", "programs": []}'),
                ("text that is not JSON", "{ not json"),
                ("a count written into a grant",
                 json.dumps({"schema": velaris.CAPABILITIES_SCHEMA,
                             "velaris_version": velaris.VERSION,
                             "date": "2026-09-11",
                             "surface": {"grants": ["net:h.example@3"],
                                         "counts": {}},
                             "programs": []}))]:
            (t.root / "velaris.capabilities").write_text(body,
                                                         encoding="utf-8")
            bad = t.velaris("capabilities", "check", ".")
            ok(f"a baseline holding {label} exits 2 rather than passing",
               bad.returncode == 2, bad.stderr)

        # ------------------------------------------------------------------
        print()
        print("what the check hands to tools")
        print("-" * 62)
        t = tree({"poll.vel": pinger(3)})
        t.init()
        t.write({"poll.vel": pinger(3, host="evil.example.net")})
        code, r = t.check()
        g = grant_finding(r, "net:evil.example.net")
        ok("--json is velaris.capabilities-check/1, naming the rules each "
           "widening fails and the edit that would accept it",
           r.get("schema") == "velaris.capabilities-check/1"
           and r.get("widened") is True and g.get("rules") == ["W1", "W3"]
           and 'add "net:evil.example.net" to surface.grants'
           in g.get("accept", []), g)
        sarif = t.velaris("capabilities", "check", ".", "--sarif")
        try:
            log = json.loads(sarif.stdout)
        except ValueError:
            log = {}
        results = (log.get("runs") or [{}])[0].get("results", [])
        hit = next((x for x in results
                    if x["ruleId"] == "capability-widened"), {})
        region = (hit.get("locations") or [{}])[0].get(
            "physicalLocation", {})
        ok("--sarif lands each widening as an error at the line that "
           "introduced it",
           sarif.returncode == 1 and hit.get("level") == "error"
           and region.get("artifactLocation", {}).get("uri", "")
           .endswith("poll.vel")
           and region.get("region", {}).get("startLine") == 2, hit)
        if Draft4Validator is None:
            skip("...and the log validates against SARIF 2.1.0",
                 "jsonschema is not installed")
        else:
            schema = json.loads((HERE / "tests" / "sarif-schema-2.1.0.json")
                                .read_text(encoding="utf-8"))
            errs = list(Draft4Validator(schema).iter_errors(log))
            ok("...and the log validates against SARIF 2.1.0", log
               and not errs, [e.message for e in errs[:2]])

        # ------------------------------------------------------------------
        print()
        print("the rules underneath")
        print("-" * 62)
        table = [
            ("fs:read:data", "fs:read:data/x.csv", True),
            ("fs:read:./data/", "fs:read:data", True),
            ("fs:read:data", "fs:read:database", False),
            ("fs:read:data", "fs:read:data/../secret", False),
            ("fs:read:.", "fs:read:../x", False),
            ("fs:read:.", "fs:read:x/y", True),
            ("fs:read", "fs:read:/etc/passwd", True),
            ("fs:read", "fs:write:x", False),
            ("fs", "fs:write:x", True),
            ("fs:write:out", "fs:write", False),
            ("net", "net:a.example.com", True),
            ("net:a.example.com", "net", False),
            ("net:*.example.com", "net:a.example.com", True),
            ("net:*.example.com", "net:a.b.example.com", False),
            ("net:*.example.com", "net:*.b.example.com", False),
            ("net:h.example:443", "net:h.example", False),
            ("net:h.example", "net:h.example:443", True),
            ("net:[::1]", "net:[::1]:8080", True),
            ("ffi", "ffi:os", True),
            ("ffi:math", "ffi:os", False),
            ("ffi:math", "ffi", False),
            ("io", "io", True),
            ("env", "io", False),
        ]
        wrong = [(b, c, want) for b, c, want in table
                 if velaris._covers(gp(b), gp(c)) != want]
        ok(f"{len(table)} covering cases: paths by whole components, "
           f"wildcards one label deep, ports, modules", not wrong, wrong)
        ok("a reduced grant list keeps one spelling of a path and drops "
           "what another grant covers",
           velaris._reduce_grants(["fs:read:./data/", "fs:read:data",
                                   "fs:read:data/x", "io", "io"])
           == ["fs:read:./data/", "io"])

        def bound(source):
            funcs, _ = velaris.load_program("_bound.vel", source)
            b, _ = velaris._operation_bounds(funcs)
            return {k: velaris._as_count(v) for k, v in b["main"].items()}

        counted = [
            ("nested loops multiply", 'fn main() uses fs {\n'
             '    for i in 0 to 3 {\n'
             '        for j in 1 to 5 {\n'
             '            let e = file_exists("x")\n'
             '        }\n    }\n}\n', {"fs": 12, "net": 0}),
            ("the larger branch of an if counts", 'fn main() uses fs {\n'
             '    if file_exists("a") {\n'
             '        let x = file_exists("b")\n'
             '        let y = file_exists("c")\n'
             '    } else {\n'
             '        let z = file_exists("d")\n'
             '    }\n}\n', {"fs": 3, "net": 0}),
            ("a loop over a list literal turns once per item",
             'fn main() uses fs {\n'
             '    for p in ["a", "b", "c"] {\n'
             '        let e = file_exists(p)\n'
             '    }\n}\n', {"fs": 3, "net": 0}),
            ("a hand-written counter, started by a let",
             'fn main() uses fs {\n'
             '    let i = 2\n'
             '    while i <= 6 {\n'
             '        let e = file_exists("x")\n'
             '        i = i + 1\n'
             '    }\n}\n', {"fs": 5, "net": 0}),
            ("a function called twice counts twice",
             'fn one() -> Bool uses fs {\n'
             '    return file_exists("x")\n}\n\n'
             'fn main() uses fs {\n'
             '    let a = one()\n'
             '    let b = one()\n}\n', {"fs": 2, "net": 0}),
            ("a counter that a loop body changes is not a fixed start",
             'fn main() uses fs {\n'
             '    let i = 0\n'
             '    while i < 3 {\n'
             '        i = i + 1\n'
             '    }\n'
             '    while i < 5 {\n'
             '        let e = file_exists("x")\n'
             '        i = i + 1\n'
             '    }\n}\n', {"fs": None, "net": 0}),
        ]
        wrong = []
        for label, source, want in counted:
            try:
                got = bound(source)
            except velaris.VelarisError as e:
                got = f"does not compile: {e.message}"
            if got != want:
                wrong.append((label, got, want))
        ok(f"{len(counted)} bounds on the operations of a run: nested "
           f"loops, branches, list literals, counters, calls - and no "
           f"bound where the text does not fix one", not wrong, wrong)
    finally:
        for t in trees:
            t.close()

    print("-" * 62)
    print(f"{passed} correct, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
