#!/usr/bin/env python3
"""Generate playground/index.html with the real velaris.py embedded.

Run after any change to velaris.py:   python build_playground.py
Open playground/index.html in a browser - no install, no server needed.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SRC = (HERE / "velaris.py").read_text(encoding="utf-8")

EXAMPLES = {
    "hello": """fn greet(name: Text) uses io {
    print("hello, " + name)
}

fn main() uses io {
    greet("world")
    print("2 + 2 = " + (2 + 2))
}""",
    "sneaky effect (rejected)": """// This "pure calculator" secretly prints.
// The effect checker refuses to run it.

fn discount(price: Int) -> Int {
    print("leaking: " + price)
    return price - 10
}

fn main() uses io {
    print(discount(200))
}""",
    "broken promise (caught)": """// The promise says the result is never negative.
// (In the browser, promises are checked while running -
// the installed version PROVES this before running, via Z3.)

fn discount(price: Int) -> Int
    ensures result >= 0
{
    return price - 10
}

fn main() uses io {
    print("discount(200) = " + discount(200))
    print("discount(5) = " + discount(5))
}""",
    "records": """record Point {
    x: Int
    y: Int
}

fn shift(p: Point, dx: Int) -> Point {
    return Point(x: p.x + dx, y: p.y)
}

fn main() uses io {
    let p = Point(x: 3, y: 4)
    print(p)
    print(shift(p, 10))
}""",
    "fizzbuzz": """fn fizzbuzz(n: Int) -> Text {
    if n % 15 == 0 {
        return "fizzbuzz"
    } else if n % 3 == 0 {
        return "fizz"
    } else if n % 5 == 0 {
        return "buzz"
    }
    return to_text(n)
}

fn main() uses io {
    let i = 1
    while i <= 15 {
        print(fizzbuzz(i))
        i = i + 1
    }
}""",
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Velaris Playground</title>
<style>
  :root { --paper:#ffffff; --alt:#f6f7f8; --line:#e6e8eb;
          --ink:#0b1215; --mut:#57606a; --brand:#0a7d5a;
          --term:#101418; --term-ink:#e6edf3; --term-mut:#8b949e;
          --err:#e5484d; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family:-apple-system,"Segoe UI",Inter,Roboto,Helvetica,
         Arial,sans-serif; height:100vh; display:flex;
         flex-direction:column; }
  header { padding:12px 20px; display:flex; align-items:center;
           gap:16px; border-bottom:1px solid var(--line);
           flex-wrap:wrap; background:var(--paper); }
  header .brand { font-size:16px; font-weight:700;
    letter-spacing:-.02em; display:flex; gap:8px; align-items:center;
    color:var(--ink); text-decoration:none; }
  .dot { width:8px; height:8px; border-radius:50%;
         background:var(--brand); }
  header .tag { color:var(--mut); font-size:13px; }
  select { background:var(--paper); color:var(--ink);
    border:1px solid var(--line); border-radius:8px; padding:7px 12px;
    font-size:13.5px; }
  button#run { background:var(--ink); color:#fff; border:none;
    border-radius:8px; padding:8px 20px; font-size:14px;
    font-weight:600; cursor:pointer; }
  button#run:hover { background:#22292f; }
  button:disabled { opacity:.45; cursor:wait; }
  header a.gh { margin-left:auto; color:var(--mut); font-size:13px;
    text-decoration:none; }
  header a.gh:hover { color:var(--ink); }
  main { flex:1; display:flex; min-height:0; }
  textarea { flex:1; background:var(--paper); color:var(--ink);
    border:none; resize:none; padding:18px 20px;
    font:13.5px/1.65 ui-monospace,"SF Mono",Consolas,monospace;
    outline:none; }
  #out { flex:1; background:var(--term); color:var(--term-ink);
    margin:0; padding:18px 20px; overflow:auto;
    font:13.5px/1.65 ui-monospace,"SF Mono",Consolas,monospace;
    white-space:pre-wrap; border-left:1px solid var(--line); }
  .err { color:var(--err); } .note { color:var(--term-mut); }
  @media (max-width:800px) { main { flex-direction:column; }
    #out { border-left:none; border-top:1px solid var(--line); } }
</style>
</head>
<body>
<header>
  <a class="brand" href="index.html"><span class="dot"></span>Velaris
  Playground</a>
  <span class="tag">the real compiler, running in your browser</span>
  <select id="examples"></select>
  <button id="run" disabled>loading&hellip;</button>
  <a class="gh"
  href="https://github.com/gowrishankar-infra/velaris-lang">GitHub
  &rarr;</a>
</header>
<main>
  <textarea id="code" spellcheck="false"></textarea>
  <pre id="out"><span class="note">Loading Python runtime (first visit
takes a few seconds)&hellip;

Note: in the browser, promises (requires/ensures/invariant) are checked
while the program runs. The installed version also PROVES them before
running, using the Z3 theorem prover, and compiles hot functions to
native code with LLVM. github.com/gowrishankar-infra/velaris-lang</span></pre>
</main>
<script>
const VELARIS_SRC = __SRC__;
const EXAMPLES = __EXAMPLES__;

const sel = document.getElementById("examples");
const code = document.getElementById("code");
const out = document.getElementById("out");
const runBtn = document.getElementById("run");

for (const name of Object.keys(EXAMPLES)) {
  const o = document.createElement("option");
  o.value = name; o.textContent = name;
  sel.appendChild(o);
}
code.value = EXAMPLES[Object.keys(EXAMPLES)[0]];
sel.onchange = () => { code.value = EXAMPLES[sel.value]; };

let pyodide = null;
async function boot() {
  pyodide = await loadPyodide();
  pyodide.setStdin({ stdin: () => window.prompt("the program asks:") });
  pyodide.FS.writeFile("/velaris.py", VELARIS_SRC);
  runBtn.disabled = false;
  runBtn.textContent = "Run \\u25B6";
  out.innerHTML = '<span class="note">Ready. Pick an example or write ' +
    'your own, then press Run.</span>';
}

async function run() {
  runBtn.disabled = true; runBtn.textContent = "running\\u2026";
  out.textContent = "";
  pyodide.FS.writeFile("/prog.vel", code.value);
  const py = `
import importlib.util, io, json, sys
from contextlib import redirect_stdout, redirect_stderr
spec = importlib.util.spec_from_file_location("velaris", "/velaris.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sys.argv = ["velaris.py", "/prog.vel", "--no-native"]
o, e = io.StringIO(), io.StringIO()
try:
    with redirect_stdout(o), redirect_stderr(e):
        try:
            mod.main()
        except SystemExit:
            pass
except Exception as ex:
    e.write(f"playground error: {ex}")
json.dumps([o.getvalue(), e.getvalue()])
`;
  try {
    const res = JSON.parse(await pyodide.runPythonAsync(py));
    const [stdout, stderr] = res;
    out.textContent = "";
    if (stdout) out.append(stdout);
    if (stderr) {
      for (const ln of stderr.split("\\n")) {
        const s = document.createElement("span");
        s.className = ln.startsWith("note:") ? "note" : "err";
        s.textContent = ln + "\\n";
        out.appendChild(s);
      }
    }
    if (!stdout && !stderr) {
      out.innerHTML = '<span class="note">(no output)</span>';
    }
  } catch (err) {
    out.innerHTML = '<span class="err">playground error: ' + err + '</span>';
  }
  runBtn.disabled = false; runBtn.textContent = "Run \\u25B6";
}
runBtn.onclick = run;
</script>
<script src="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"
        onload="boot()"></script>
</body>
</html>
"""

html = TEMPLATE.replace("__SRC__", json.dumps(SRC)) \
               .replace("__EXAMPLES__", json.dumps(EXAMPLES))
outdir = HERE / "playground"
outdir.mkdir(exist_ok=True)
(outdir / "index.html").write_text(html, encoding="utf-8")
print(f"playground/index.html written ({len(html)//1024} KB)")
