#!/usr/bin/env python3
"""Generate the Velaris documentation site into docs/.

Pages: index (pitch + quickstart), tutorial (from TUTORIAL.md),
library (parsed from stdlib/std.vel BY THE REAL COMPILER, contracts
included), errors (every E-code scraped from velaris.py), and the
playground. Rebuild with:  python build_docs.py
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import velaris  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "docs"
OUT.mkdir(exist_ok=True)

STYLE = """
:root { --paper:#ffffff; --alt:#f6f7f8; --line:#e6e8eb; --ink:#0b1215;
        --mut:#57606a; --brand:#0a7d5a; --brand2:#075e44;
        --term:#101418; --term-ink:#e6edf3; --term-mut:#8b949e;
        --err:#e5484d; --mint:#7ee2c0; }
* { box-sizing:border-box; margin:0; }
html { scroll-behavior:smooth; }
body { background:var(--paper); color:var(--ink); font:16px/1.65
  -apple-system,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; }
nav { position:sticky; top:0; background:rgba(255,255,255,.86);
  backdrop-filter:blur(10px); border-bottom:1px solid var(--line);
  z-index:10; }
nav .in { max-width:1080px; margin:0 auto; padding:14px 24px;
  display:flex; gap:26px; align-items:center; }
.brand { font-weight:700; font-size:17px; letter-spacing:-.02em;
  color:var(--ink); text-decoration:none; display:flex; gap:8px;
  align-items:center; }
.dot { width:9px; height:9px; border-radius:50%;
  background:var(--brand); display:inline-block; }
nav a { color:var(--mut); text-decoration:none; font-size:14.5px;
  font-weight:500; }
nav a:hover, nav a.here { color:var(--ink); }
nav .ver { margin-left:auto; font-size:12.5px; color:var(--mut);
  border:1px solid var(--line); border-radius:99px; padding:3px 11px; }
main { max-width:760px; margin:0 auto; padding:52px 24px 110px; }
main.wide { max-width:1080px; }
h1 { font-size:clamp(32px,4.6vw,44px); letter-spacing:-.03em;
  line-height:1.12; font-weight:750; }
h2 { font-size:24px; letter-spacing:-.02em; margin:2.2em 0 .7em;
  font-weight:700; }
h3 { font-size:18px; margin:1.6em 0 .5em; font-weight:650; }
p, li { color:#2a3138; }
p { margin:.85em 0; }
.lead { font-size:19px; color:var(--mut); max-width:640px; }
a { color:var(--brand); text-decoration:none; }
a:hover { text-decoration:underline; }
code { background:var(--alt); border:1px solid var(--line);
  padding:1.5px 6px; border-radius:6px;
  font:13px ui-monospace,"SF Mono",Consolas,monospace; }
pre { background:var(--term); color:var(--term-ink); border-radius:12px;
  padding:18px 20px; overflow-x:auto; margin:1.2em 0;
  font:13.5px/1.6 ui-monospace,"SF Mono",Consolas,monospace; }
pre code { background:none; border:none; padding:0; color:inherit;
  font:inherit; }
.k { color:var(--mint); } .e { color:#ff8f8f; } .m { color:var(--term-mut); }
.btns { display:flex; gap:12px; margin:26px 0 8px; flex-wrap:wrap; }
.btn { background:var(--ink); color:#fff; padding:11px 22px;
  border-radius:9px; font-weight:600; font-size:15px; }
.btn:hover { background:#22292f; text-decoration:none; }
.btn.ghost { background:transparent; color:var(--ink);
  border:1px solid var(--line); }
.btn.ghost:hover { border-color:#c7ccd1; }
.hero { padding:74px 0 20px; }
.eyebrow { color:var(--brand); font-weight:650; font-size:13.5px;
  letter-spacing:.06em; text-transform:uppercase; margin-bottom:14px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,
  minmax(230px,1fr)); gap:16px; margin:34px 0; }
.card { border:1px solid var(--line); border-radius:14px;
  padding:20px 22px; background:var(--paper); }
.card b { font-size:15.5px; letter-spacing:-.01em; }
.card p { font-size:14px; color:var(--mut); margin:.5em 0 0; }
.sig { color:var(--ink); font:14px ui-monospace,"SF Mono",Consolas,
  monospace; font-weight:600; }
.contract { color:var(--brand); font:13px ui-monospace,"SF Mono",
  Consolas,monospace; margin:5px 0 0 20px; }
.fnrow { border:1px solid var(--line); border-radius:12px;
  padding:15px 18px; margin:11px 0; }
table { border-collapse:collapse; width:100%; margin:1.2em 0;
  font-size:14.5px; }
td, th { border-bottom:1px solid var(--line); padding:9px 12px;
  text-align:left; vertical-align:top; }
th { color:var(--mut); font-weight:600; font-size:13px;
  text-transform:uppercase; letter-spacing:.05em; }
.ecode { color:var(--err); font-weight:650;
  font-family:ui-monospace,Consolas,monospace; font-size:13px; }
.strip { background:var(--alt); border-top:1px solid var(--line);
  border-bottom:1px solid var(--line); margin:44px -24px;
  padding:34px 24px; }
footer { border-top:1px solid var(--line); color:var(--mut);
  font-size:13.5px; padding:26px 24px; text-align:center; }
"""

PAGES = [("index.html", "Home"), ("tutorial.html", "Tutorial"),
         ("library.html", "Library"), ("errors.html", "Errors"),
         ("playground.html", "Playground")]


def shell(title: str, here: str, body: str, wide: bool = False) -> str:
    links = "".join(
        f'<a href="{p}" class="{"here" if p == here else ""}">{n}</a>'
        for p, n in PAGES)
    fav = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
           " viewBox='0 0 32 32'%3E%3Crect width='32' height='32'"
           " rx='7' fill='%230a7d5a'/%3E%3Ctext x='16' y='22'"
           " font-family='Arial' font-size='18' font-weight='700'"
           " fill='white' text-anchor='middle'%3EV%3C/text%3E%3C/svg%3E")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Velaris - the language where you can
trust code you didn't write. Effects, failure, and Z3-proven contracts,
all in the signature.">
<link rel="icon" href="{fav}">
<title>{html.escape(title)} - Velaris</title>
<style>{STYLE}</style></head><body>
<nav><div class="in"><a class="brand" href="index.html">
<span class="dot"></span>Velaris</a>{links}
<span class="ver">v{velaris.VERSION}</span></div></nav>
<main class="{'wide' if wide else ''}">{body}</main>
<footer>Velaris is MIT-licensed open source &middot;
<a href="https://github.com/gowrishankar-infra/velaris-lang">GitHub</a>
&middot; <a href="https://github.com/gowrishankar-infra/velaris-lang/issues">Issues</a></footer>
</body></html>"""


def md_to_html(md: str) -> str:
    out, in_code = [], False
    for line in md.splitlines():
        if line.startswith("```"):
            out.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        e = html.escape(line)
        e = re.sub(r"`([^`]+)`", r"<code>\1</code>", e)
        e = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", e)
        if e.startswith("### "):
            out.append(f"<h3>{e[4:]}</h3>")
        elif e.startswith("## "):
            out.append(f"<h2>{e[3:]}</h2>")
        elif e.startswith("# "):
            out.append(f"<h1>{e[2:]}</h1>")
        elif e.startswith("- "):
            out.append(f"<li>{e[2:]}</li>")
        elif e.strip() == "":
            out.append("<br>")
        else:
            out.append(f"<p>{e}</p>")
    return "\n".join(out)


def fn_signature(f) -> str:
    ps = ", ".join(f"{n}: {t}" for n, t in f.params)
    sig = f"fn {f.name}({ps})"
    if f.return_type and f.return_type != "Unit":
        sig += f" -> {f.return_type}"
    if f.type_vars:
        sig += " for any " + ", ".join(f.type_vars)
    if f.can_fail:
        sig += " or fail"
    if f.effects:
        sig += " uses " + ", ".join(sorted(f.effects))
    return sig


def library_page() -> str:
    funcs, _ = velaris.load_program(str(HERE / "stdlib" / "std.vel"))
    body = ["<h1>Standard library</h1>",
            '<p class="lead">Every function below is written in '
            "Velaris and parsed onto this page by the real compiler "
            "&mdash; contracts included. A violated "
            "<code>requires</code> is a compile error at your call "
            "site.</p>"]
    for f in funcs:
        body.append('<div class="fnrow">')
        body.append(f'<div class="sig">{html.escape(fn_signature(f))}'
                    '</div>')
        for expr, _ in f.requires:
            body.append(f'<div class="contract">requires '
                        f'{html.escape(velaris.expr_str(expr))}</div>')
        for expr, _ in f.ensures:
            body.append(f'<div class="contract">ensures '
                        f'{html.escape(velaris.expr_str(expr))}</div>')
        body.append("</div>")
    body.append("<h2>Built-in functions</h2><table><tr><th>Name</th>"
                "<th>Effects</th><th>Takes</th><th>Gives</th></tr>")
    for name, info in sorted(velaris.BUILTINS.items()):
        eff = ", ".join(sorted(info["effects"])) or "pure"
        fall = (' <span class="ecode">or fail</span>'
                if name in velaris.FALLIBLE_BUILTINS else "")
        body.append(f"<tr><td><code>{name}</code>{fall}</td>"
                    f"<td>{eff}</td>"
                    f"<td>{html.escape(', '.join(info['types']))}</td>"
                    f"<td>{html.escape(info['ret'])}</td></tr>")
    body.append("</table><p style='font-size:13.5px;color:var(--mut)'>"
                "get on a map can also fail (missing key); get_or "
                "never fails.</p>")
    return "\n".join(body)


def errors_page() -> str:
    src = (HERE / "velaris.py").read_text(encoding="utf-8")
    found: dict[str, str] = {}
    for m in re.finditer(
            r'VelarisError\(\s*"(E\d+)",\s*((?:f?"(?:[^"\\\\]|\\\\.)*"\s*)+)',
            src):
        code = m.group(1)
        msg = " ".join(re.findall(r'f?"((?:[^"\\\\]|\\\\.)*)"', m.group(2)))
        msg = re.sub(r"\s+", " ", msg).strip()
        if code not in found or len(msg) > len(found[code]):
            found[code] = msg
    body = ["<h1>Error reference</h1>",
            '<p class="lead">Every error Velaris can give &mdash; '
            "scraped from the compiler source itself, so this page "
            "cannot go stale. Braces are filled with your "
            "program&rsquo;s names and values; every error also "
            "arrives with numbered fixes, and as JSON with "
            "<code>--json</code>.</p>"
            "<table><tr><th>Code</th><th>Message template</th></tr>"]
    for code in sorted(found):
        body.append(f'<tr><td class="ecode">{code}</td>'
                    f'<td>{html.escape(found[code])}</td></tr>')
    body.append("</table>")
    return "\n".join(body)


def index_page() -> str:
    return f"""
<div class="hero">
<div class="eyebrow">A programming language</div>
<h1>Trust code you didn&rsquo;t write.</h1>
<p class="lead">A Velaris signature tells you everything: the types,
the effects a function may perform, whether it can fail &mdash; and
promises that are <b>mathematically proven before the program
runs</b>.</p>
<div class="btns">
<a class="btn" href="playground.html">Open the playground</a>
<a class="btn ghost"
href="https://github.com/gowrishankar-infra/velaris-lang">View on
GitHub</a>
</div>
</div>

<pre><code><span class="k">fn</span> discount(price: Int) -&gt; Int
    <span class="k">requires</span> price &gt;= 0
    <span class="k">ensures</span> result &gt;= 0
{{
    <span class="k">return</span> price - 10
}}

<span class="e">error[E700]</span> promise cannot be kept: 'discount' ensures result &gt;= 0
<span class="m">  proven without running the program: price = 5 gives result = -5</span></code></pre>

<div class="grid">
<div class="card"><b>Effects are visible</b><p>A function without
<code>uses net</code> can never touch the network &mdash; checked
transitively. Hidden behavior does not compile.</p></div>
<div class="card"><b>Promises are proven</b><p>Contracts are verified
by the Z3 theorem prover for every possible input &mdash; with exact
counterexamples when broken, in genuine IEEE-754 for floats.</p></div>
<div class="card"><b>Failure is unignorable</b><p><code>or fail</code>
in the signature; forgetting the error path is a compile error.
Builtins included.</p></div>
<div class="card"><b>Fast where it&rsquo;s safe</b><p>Pure numeric
functions compile to native code via LLVM, verified identical to the
interpreter.</p></div>
</div>

<div class="strip">
<h2 style="margin-top:0">Install in one line</h2>
<pre style="margin-bottom:8px"><code>pip install "git+https://github.com/gowrishankar-infra/velaris-lang"
velaris doctor
velaris new hello &amp;&amp; cd hello &amp;&amp; velaris main.vel</code></pre>
<p style="font-size:14px;color:var(--mut)">No Python? Download a
standalone executable from the
<a href="https://github.com/gowrishankar-infra/velaris-lang/releases">
latest release</a> &mdash; Windows, Linux, and macOS. Or skip
installing entirely: the <a href="playground.html">playground</a> runs
the real compiler in your browser.</p>
</div>

<h2>The standard library keeps its own promises</h2>
<p><code>sort</code> carries <code>ensures is_sorted(result)</code>
&mdash; and <code>is_sorted</code> is itself a library function,
written in Velaris. Violating a library <code>requires</code> is a
compile error at <i>your</i> call site. Browse the
<a href="library.html">library reference</a>, generated from the real
compiler with contracts included.</p>

<h2>Built for the age of generated code</h2>
<p>Increasingly, the developer reading your compiler&rsquo;s output is
an AI in a fix loop. Every Velaris error has a stable code, a
plain-English message, a location, and numbered fixes &mdash;
available as JSON with <code>--json</code>. All
<a href="errors.html">49 of them are documented</a>, scraped from the
compiler source itself.</p>"""


(OUT / "index.html").write_text(
    shell("Velaris", "index.html", index_page()), encoding="utf-8")
(OUT / "tutorial.html").write_text(
    shell("Tutorial", "tutorial.html",
          md_to_html((HERE / "TUTORIAL.md").read_text(encoding="utf-8"))),
    encoding="utf-8")
(OUT / "library.html").write_text(
    shell("Library", "library.html", library_page()), encoding="utf-8")
(OUT / "errors.html").write_text(
    shell("Errors", "errors.html", errors_page()), encoding="utf-8")
play = (HERE / "playground" / "index.html").read_text(encoding="utf-8")
(OUT / "playground.html").write_text(play, encoding="utf-8")
n_err = errors_page().count('class="ecode"')
print(f"docs/ written: 5 pages, {n_err} error codes documented")
