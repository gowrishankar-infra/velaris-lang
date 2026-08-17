#!/usr/bin/env python3
"""
Velaris v2.3 — "The language where you can trust code you didn't write."

New in v2.3: launch polish - a professional visual identity for the
    docs site, playground, and README, plus a CI fix for minimal-mode
    proof-only test expectations.

New in v2.2: out-of-the-box readiness.
    velaris doctor          check your setup, with exact fixes
    velaris new myproject   start a project with running code
    Standalone executables (no Python needed) are built for every
    release - download one file and go.

New in v2.1: a documentation site in docs/ (python build_docs.py).
    The library page is parsed from std.vel by this very compiler -
    contracts included - and the error index is scraped from this
    file, so the docs cannot go stale.

v2.0 - THE BUILTINS KEEP THE LANGUAGE'S PROMISE (breaking change):
    to_int, get-on-a-map, read_file, and fetch can now FAIL instead of
    killing the program - and therefore must be called through check
    or try, like any fallible function. The compiler walks you to
    every call that needs updating (error E520). get on a LIST is
    unchanged: list bounds are the prover's job. New: get_or(m, k,
    default) - a total map lookup that never fails.

New in v1.20: sort_by in the standard library (generic sorting by an
    Int key function), and the ledger app gains a 'report' command
    built on it - sorted listing, biggest, smallest, totals.

New in v1.19: a grown-up standard library. stdlib/std.vel now holds
    sixteen functions written in Velaris - including sort, which
    ensures is_sorted(result) using is_sorted, also from the library.
    Violating a library requires is a compile error at your call site.

New in v1.18: FLOAT PROOFS - real IEEE-754, not pretend-math.
    Promises about Float values are proven in Z3's floating-point
    theory, bit-for-bit the arithmetic your machine performs. The
    prover will happily refute x + 0.1 + 0.1 == x + 0.2, because in
    floating point it is false - and Velaris does not pretend.

New in v1.17: FAILURE-AWARE PROOFS. The prover now understands fail,
    check, and try - so promises on 'or fail' functions are proven for
    every path that actually returns. Failing early on bad input makes
    the remaining promise EASIER to prove, and the prover knows it.

New in v1.16: QUANTIFIED LIST PROOFS.
    all_of(xs, p) / any_of(xs, p) ask whether a predicate holds for
    every / some element - and promises using them are PROVEN where Z3
    can settle the quantifier, with runtime checks guarding the rest.
    ensures all_of(result, is_positive)   is now a provable sentence.

New in v1.15: NATIVE Float and Bool. The LLVM backend now compiles pure
    functions over Int, Float, and Bool (division and % stay interpreted
    in both types, so dividing by zero is always a clean error, never a
    silent infinity). Interpreted and native runs are verified to agree.

New in v1.14: RECORD PROOFS. Promises about record fields are now
    proven before running - ensures result.x == p.x + dx is mathematics,
    and a swapped-fields bug is a compile-time counterexample with the
    record values shown. Works for records whose fields are Int, Bool,
    or other such records; lists/Float fields stay runtime-checked.

New in v1.13: the first real app - examples/ledger.vel, an expense
    tracker written in Velaris (records, contracts, or-fail parsing,
    file persistence). Two supporting builtins: chars(text) splits Text
    into single characters (pure), and file_exists(path) checks before
    reading (fs).

New in v1.12: continuous integration + repo hygiene.
    Every push is tested by GitHub Actions on Linux and Windows,
    Python 3.10 and 3.12, WITH and WITHOUT the optional dependencies -
    plus formatter and playground checks. CHANGELOG.md tells the story.

New in v1.11: a LANGUAGE SERVER - errors as you type, in any LSP editor.
    velaris lsp
    Fast checks (effects + types) on every keystroke; the full pipeline
    including Z3 proofs on save. The VS Code extension in editor/vscode
    now launches it automatically (no extra dependencies).

New in v1.10: a formatter - one canonical style for every .vel file.
    velaris fmt program.vel            rewrite in place (if needed)
    velaris fmt program.vel --stdout   print instead of writing
    velaris fmt program.vel --check    exit 1 if not formatted (for CI)

New in v1.9: a REPL - try Velaris line by line.
    velaris repl
    Loose lines run immediately (checked while running); fn / record /
    import definitions get the FULL treatment - effects, types, and
    Z3 proofs - before they are accepted into the session.

New in v1.8: a real install.
    pip install .          (from a clone; add [full] for proofs + native)
    velaris program.vel    (the command, anywhere)
    import "std.vel" now finds the shipped standard library from any
    folder - imports check relative-to-your-file first, then stdlib.

New in v1.7: GENERICS - one function, every type.
    fn first(xs: List of T) -> T for any T
        requires length(xs) > 0
    { return get(xs, 0) }
    T is inferred at each call; conflicting uses are clear errors.
    Plus: examples/std.vel - the first standard library, written in
    Velaris itself.

New in v1.6: FUNCTIONS ARE VALUES - pass them to other functions.
    fn apply(xs: List of Int, f: fn(Int) -> Int) -> List of Int { ... }
    apply(nums, double)
    Only PURE functions (no effects, no fail) can be passed - so a
    passed-in function can never smuggle hidden behavior.

New in v1.5: failure is visible and UNIGNORABLE.
    fn parse(t: Text) -> Int or fail { ... fail "reason" ... }
    Callers must handle it:  check parse(t) { ok v {...} fail why {...} }
    or pass it upward inside another fallible function:  try parse(t)
    Calling a fallible function any other way is a compile error.

New in v1.4: MAPS - lookup tables, written {"alice": 30, "bob": 25}.
    Typed as: Map of Text to Int (keys are Text or Int).
    get(m, key) reads, has(m, key) checks, put(m, key, v) returns a new
    map, keys(m) lists the keys, length(m) counts entries.

New in v1.3: Float - decimal numbers like 3.14.
    Int and Float never mix silently: 1 + 2.5 is a compile error with a
    fix (use to_float(1), or round(2.5) for an Int). Float math is
    runtime-checked; proofs stay Int-only for now.

New in v1.2: a browser playground - open playground/index.html and run
    Velaris with zero install (rebuild it with: python build_playground.py).

New in v1.1: escape sequences in text - \n newline, \t tab, \" quote,
    \\ backslash - plus a VS Code syntax highlighter in editor/vscode.
New in v1.0: the testers' release.
    * Multiple problems are reported in one run (one per function),
      instead of stopping at the first.
    * to_text(x) turns any value into Text.
    * --version prints the version.

Usage:
  velaris program.vel                      run a program (after pip install)
  velaris repl                             interactive session
  velaris fmt program.vel                  format to the canonical style
  velaris doctor                           check the installation
  velaris new <name>                       start a fresh project
  velaris lsp                              language server (for editors)
  velaris version                          print the version
  python velaris.py program.vel            run a program
  python velaris.py program.vel --json     errors as machine-readable JSON
  python velaris.py program.vel --time     show how long the run took
  python velaris.py program.vel --no-native  force the interpreter
  python velaris.py --version

New in v0.16: IMPORTS - programs can span multiple files.
    import "mathlib.vel"
    Paths are relative to the importing file; imports chain and cycles
    are safe; a name defined in two files is a clear error; and error
    messages name the file the problem actually lives in.

New in v0.15: RECORDS - group named fields into one value.
    record Point { x: Int  y: Int }
    let p = Point(x: 3, y: 4)      then      p.x
    Records are immutable: build a new one instead of changing fields.

New in v0.14: the usability pack.
    else if chains, the % remainder operator, and text tools:
    split, contains, upper, lower.

New in v0.13: LIST PROOFS via Z3's theory of arrays.
    Contracts and code over lists (length, get, push) are now provable,
    and every 'get' carries a bounds obligation - reading past the end
    of a list can be proven and rejected before the program runs (E705).

New in v0.12: interactive programs.
    ask("your name?")   reads a line from the keyboard (an io effect)
    to_int(text)        turns text into an Int (pure; clean error if not
                        a whole number)

New in v0.11: fetch(url) is REAL - an actual HTTP GET with a 10-second
    timeout, guarded by 'uses net'. A function without 'uses net' in its
    signature provably cannot touch the network. Failures are clean
    Velaris errors (E606), never tracebacks.

New in v0.10: LOOP INVARIANTS - the prover learned loops.
    while i <= n
        invariant total >= 0
    { ... }
    Velaris proves the invariant holds at loop entry, survives every step,
    and uses it to prove the function's promises. Unproven invariants are
    still checked at runtime on every iteration.

New in v0.9: NATIVE SPEED via LLVM. Pure Int math functions (no effects,
    no contracts, no lists/text) are compiled to real machine code and
    run at C-like speed; everything else stays safely interpreted.
    Flags:  --time       show how long the run took
            --no-native  force the interpreter for everything
    (needs: pip install llvmlite ; without it, everything still runs)

New in v0.8: MODULAR proofs - verification composes across functions.
    When A calls B, the prover uses B's promises to prove A's promises,
    and proves A can never violate B's 'requires' at the call site (E701).
New in v0.7: compile-time PROOFS via the Z3 theorem prover.
    For simple functions, broken promises are now proven false and the
    program is rejected BEFORE it runs - with an exact counterexample.
    Functions Z3 cannot handle (loops, lists, text math) safely fall
    back to runtime promise checks, exactly as in v0.5.
    (needs: pip install z3-solver ; without it, runtime checks still guard)
New in v0.6: negative numbers, and / or / not, and lists.
    let scores = [42, -7, 99]
    fn biggest(xs: List of Int) -> Int requires length(xs) > 0 { ... }
New in v0.5: contracts. Functions make promises; Velaris enforces them.
    fn discount(price: Int) -> Int
        requires price >= 0        <- promise about inputs (caller's duty)
        ensures result >= 0        <- promise about output (function's duty)
Contracts must be pure: a promise cannot print, fetch, or write files.
New in v0.4: while loops and changeable variables.
    while i <= n { total = total + i   i = i + 1 }
New in v0.3: full type checking before the program runs.
    add("hello", 5)   -> rejected at compile time, not a runtime crash
New in v0.2: effects split into io, net, fs, clock, rand.

Pipeline:  source text -> LEXER -> tokens -> PARSER -> AST
           -> EFFECT CHECKER (the special part) -> INTERPRETER

Design rules:
  * Plain English keywords: fn, let, return, if, else, uses
  * A function with no `uses` clause is PURE. Pure functions cannot
    print, touch files, or the network — the compiler proves it.
  * Errors are friendly for humans AND structured (JSON) for AI agents.

Usage:
  python3 velaris.py program.vel          # run a program
  python3 velaris.py program.vel --json   # errors come out as JSON too
"""

import json
import os

VERSION = "2.3.0"
import re
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. LEXER — turn raw text into a list of tokens
# ---------------------------------------------------------------------------

KEYWORDS = {"fn", "let", "return", "if", "else", "uses", "true", "false", "while", "requires", "ensures", "and", "or", "not", "invariant", "record", "import", "fail", "check", "try", "for"}

TOKEN_SPEC = [
    ("COMMENT", r"//[^\n]*"),
    ("NEWLINE", r"\n"),
    ("SKIP",    r"[ \t\r]+"),
    ("ARROW",   r"->"),
    ("FLOAT",   r"\d+\.\d+"),
    ("NUMBER",  r"\d+"),
    ("STRING",  r'"(?:\\.|[^"\\\n])*"'),
    ("IDENT",   r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",      r"==|!=|<=|>=|[+\-*/%<>=(){},:\[\].]"),
]

MASTER_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


@dataclass
class Token:
    kind: str          # NUMBER, STRING, IDENT, KEYWORD, OP, ARROW
    text: str
    line: int


def lex(source: str, keep_trivia: bool = False) -> list[Token]:
    tokens, line = [], 1
    pos = 0
    while pos < len(source):
        m = MASTER_RE.match(source, pos)
        if not m:
            raise VelarisError("E000", f"unexpected character {source[pos]!r}", line,
                              fixes=["remove or replace this character"])
        kind, text = m.lastgroup, m.group()
        pos = m.end()
        if kind == "NEWLINE":
            if keep_trivia:
                tokens.append(Token("NEWLINE", "", line))
            line += 1
        elif kind == "COMMENT":
            if keep_trivia:
                tokens.append(Token("COMMENT", text.rstrip(), line))
        elif kind == "SKIP":
            pass
        elif kind == "IDENT" and text in KEYWORDS:
            tokens.append(Token("KEYWORD", text, line))
        else:
            tokens.append(Token(kind, text, line))
    tokens.append(Token("EOF", "", line))
    return tokens


def fmt_fn_type(param_types: list, ret: str | None) -> str:
    s = "fn(" + ", ".join(param_types) + ")"
    if ret and ret != "Unit":
        s += f" -> {ret}"
    return s


def type_mentions(t: str, tv: str) -> bool:
    if t == tv:
        return True
    if t.startswith("List of "):
        return type_mentions(t[len("List of "):], tv)
    if t.startswith("Map of "):
        key, _, val = t[len("Map of "):].partition(" to ")
        return type_mentions(key, tv) or type_mentions(val, tv)
    sig = fn_sig_parts(t)
    if sig is not None:
        parts, ret = sig
        return any(type_mentions(p, tv) for p in parts) or \
            type_mentions(ret, tv)
    return False


def fn_sig_parts(t: str):
    """Split 'fn(A, B) -> R' into ([A, B], R). None if not a fn type."""
    if not t.startswith("fn("):
        return None
    depth, i, start, parts = 0, 3, 3, []
    while i < len(t):
        c = t[i]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                break
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(t[start:i].strip())
            start = i + 1
        i += 1
    last = t[start:i].strip()
    if last:
        parts.append(last)
    rest = t[i + 1:]
    ret = rest[4:].strip() if rest.startswith(" -> ") else "Unit"
    return parts, ret


ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def unescape(raw: str, line: int) -> str:
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "\\":
            i += 1
            e = raw[i] if i < len(raw) else ""
            if e not in ESCAPES:
                raise VelarisError("E002",
                    f"unknown escape '\\{e}' in text", line,
                    fixes=['known escapes: \\n (newline), \\t (tab), '
                           '\\" (quote), \\\\ (backslash)'])
            out.append(ESCAPES[e])
        else:
            out.append(c)
        i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# 2. AST — the tree shapes the parser produces
# ---------------------------------------------------------------------------

@dataclass
class Num:      value: int
@dataclass
class FloatNum: value: float
@dataclass
class Neg:      value: object; line: int
@dataclass
class Str:      value: str
@dataclass
class Bool:     value: bool
@dataclass
class Var:      name: str; line: int
@dataclass
class BinOp:    op: str; left: object; right: object; line: int
@dataclass
class Call:     name: str; args: list; line: int
@dataclass
class Let:
    name: str; value: object; line: int
    ann: str | None = None             # optional 'let x: Type = ...' 
@dataclass
class Return:   value: object; line: int
@dataclass
class If:       cond: object; then: list; other: list; line: int
@dataclass
class While:
    cond: object; body: list; line: int
    invariants: list = field(default_factory=list)   # [(expr, line)]
@dataclass
class Assign:   name: str; value: object; line: int
@dataclass
class Not:      value: object; line: int
@dataclass
class RecordLit: name: str; fields: list; line: int      # [(fname, expr)]
@dataclass
class FieldGet: obj: object; field: str; line: int
@dataclass
class RecordDef:
    name: str; fields: list; line: int                   # [(fname, type)]
    src_file: str = ""
@dataclass
class ListLit:  items: list; line: int
@dataclass
class MapLit:   entries: list; line: int         # [(key_expr, val_expr)]
@dataclass
class ExprStmt: expr: object; line: int
@dataclass
class FailStmt: value: object; line: int
@dataclass
class TryExpr:  value: object; line: int         # value is a Call
@dataclass
class Check:
    subject: object; line: int                   # subject is a Call
    ok_name: str | None = None; ok_body: list = field(default_factory=list)
    fail_name: str = ""; fail_body: list = field(default_factory=list)

@dataclass
class Function:
    name: str
    params: list[tuple[str, str]]      # (name, type)
    return_type: str | None
    effects: set[str]                  # declared with `uses`
    requires: list                     # [(expr, line)] promises about inputs
    ensures: list                      # [(expr, line)] promises about output
    body: list
    line: int
    src_file: str = ""
    can_fail: bool = False
    type_vars: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Friendly + machine-readable errors
# ---------------------------------------------------------------------------

class VelarisError(Exception):
    def __init__(self, code: str, message: str, line: int,
                 fixes: list[str] | None = None, file: str | None = None):
        self.code, self.message, self.line = code, message, line
        self.fixes = fixes or []
        self.file = file
        super().__init__(message)

    def human(self, filename: str) -> str:
        out = [f"error[{self.code}] {self.message}",
               f"  --> {self.file or filename}, line {self.line}"]
        if self.fixes:
            out.append("  how to fix (pick one):")
            for i, f in enumerate(self.fixes, 1):
                out.append(f"    {i}. {f}")
        return "\n".join(out)

    def machine(self, filename: str) -> str:
        return json.dumps({
            "code": self.code, "message": self.message,
            "file": self.file or filename, "line": self.line,
            "fixes": self.fixes,
        }, indent=2)


# ---------------------------------------------------------------------------
# 3. PARSER — recursive descent, one function per grammar rule
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens: list[Token]):
        self.toks = tokens
        self.i = 0

    def peek(self) -> Token: return self.toks[self.i]
    def next(self) -> Token:
        t = self.toks[self.i]; self.i += 1; return t

    def expect(self, kind: str, text: str | None = None) -> Token:
        t = self.peek()
        if t.kind != kind or (text is not None and t.text != text):
            want = text or kind.lower()
            raise VelarisError("E100", f"expected '{want}' but found '{t.text or 'end of file'}'",
                              t.line, fixes=[f"insert '{want}' here"])
        return self.next()

    def parse_program(self):
        funcs, records, imports = [], [], []
        while self.peek().kind != "EOF":
            t = self.peek()
            if t.kind == "KEYWORD" and t.text == "import":
                self.next()
                s = self.expect("STRING")
                imports.append((unescape(s.text[1:-1], s.line), t.line))
            elif t.kind == "KEYWORD" and t.text == "record":
                records.append(self.parse_record())
            else:
                funcs.append(self.parse_function())
        return funcs, records, imports

    def parse_record(self) -> RecordDef:
        start = self.expect("KEYWORD", "record")
        name = self.expect("IDENT").text
        self.expect("OP", "{")
        fields = []
        while self.peek().text != "}":
            fname = self.expect("IDENT").text
            self.expect("OP", ":")
            fields.append((fname, self.parse_type()))
        self.expect("OP", "}")
        return RecordDef(name, fields, start.line)

    def parse_function(self) -> Function:
        start = self.expect("KEYWORD", "fn")
        name = self.expect("IDENT").text
        self.expect("OP", "(")
        params = []
        while self.peek().text != ")":
            pname = self.expect("IDENT").text
            self.expect("OP", ":")
            ptype = self.parse_type()
            params.append((pname, ptype))
            if self.peek().text == ",":
                self.next()
        self.expect("OP", ")")
        ret = None
        if self.peek().kind == "ARROW":
            self.next()
            ret = self.parse_type()
        effects: set[str] = set()
        type_vars: list[str] = []
        can_fail = False
        while True:                    # uses / for any / or fail, any order
            t2 = self.peek()
            if t2.kind == "KEYWORD" and t2.text == "uses":
                self.next()
                effects.add(self.expect("IDENT").text)
                while self.peek().text == ",":
                    self.next()
                    effects.add(self.expect("IDENT").text)
            elif t2.kind == "KEYWORD" and t2.text == "for":
                self.next()
                anykw = self.expect("IDENT")
                if anykw.text != "any":
                    raise VelarisError("E100", "expected 'any' after 'for'",
                        anykw.line, fixes=["write: for any T"])
                type_vars.append(self.expect("IDENT").text)
                while self.peek().text == ",":
                    self.next()
                    type_vars.append(self.expect("IDENT").text)
            elif (t2.kind == "KEYWORD" and t2.text == "or"
                    and self.toks[self.i + 1].text == "fail"):
                self.next(); self.next()
                can_fail = True
            else:
                break
        requires_, ensures_ = [], []
        while (self.peek().kind == "KEYWORD"
               and self.peek().text in ("requires", "ensures")):
            kw = self.next()
            clause = (self.parse_expr(), kw.line)
            (requires_ if kw.text == "requires" else ensures_).append(clause)
        body = self.parse_block()
        f = Function(name, params, ret, effects, requires_, ensures_,
                     body, start.line)
        f.can_fail = can_fail
        f.type_vars = type_vars
        return f

    def parse_block(self) -> list:
        self.expect("OP", "{")
        stmts = []
        while self.peek().text != "}":
            stmts.append(self.parse_statement())
        self.expect("OP", "}")
        return stmts

    def parse_statement(self):
        t = self.peek()
        if t.kind == "KEYWORD" and t.text == "let":
            self.next()
            name = self.expect("IDENT").text
            ann = None
            if self.peek().text == ":":
                self.next()
                ann = self.parse_type()
            self.expect("OP", "=")
            return Let(name, self.parse_expr(), t.line, ann)
        if t.kind == "KEYWORD" and t.text == "return":
            self.next()
            if self.peek().text == "}":          # bare 'return' with no value
                return Return(None, t.line)
            return Return(self.parse_expr(), t.line)
        if t.kind == "KEYWORD" and t.text == "fail":
            self.next()
            return FailStmt(self.parse_expr(), t.line)
        if t.kind == "KEYWORD" and t.text == "check":
            self.next()
            subject = self.parse_expr()
            if isinstance(subject, TryExpr) or not isinstance(subject, Call):
                raise VelarisError("E100",
                    "'check' needs a call to a function that can fail",
                    t.line, fixes=["write: check f(args) { ok v { ... } "
                                   "fail reason { ... } }"])
            self.expect("OP", "{")
            okkw = self.expect("IDENT")
            if okkw.text != "ok":
                raise VelarisError("E100", "expected 'ok' arm first in check",
                    okkw.line, fixes=["write: ok value { ... }"])
            ok_name = None
            if self.peek().kind == "IDENT":
                ok_name = self.next().text
            ok_body = self.parse_block()
            self.expect("KEYWORD", "fail")
            fail_name = self.expect("IDENT").text
            fail_body = self.parse_block()
            self.expect("OP", "}")
            return Check(subject, t.line, ok_name, ok_body,
                         fail_name, fail_body)
        if t.kind == "KEYWORD" and t.text == "while":
            self.next()
            cond = self.parse_expr()
            invs = []
            while (self.peek().kind == "KEYWORD"
                   and self.peek().text == "invariant"):
                kw = self.next()
                invs.append((self.parse_expr(), kw.line))
            body = self.parse_block()
            return While(cond, body, t.line, invs)
        if t.kind == "IDENT" and self.toks[self.i + 1].text == ".":
            j = self.i + 1                       # looks like p.x(.y)* = ...
            while (self.toks[j].text == "."
                   and self.toks[j + 1].kind == "IDENT"):
                j += 2
            if self.toks[j].text == "=":
                raise VelarisError("E511",
                    "records cannot be changed in place", t.line,
                    fixes=["build a new one: let p2 = "
                           "Point(x: new_value, y: p.y)"])
        if t.kind == "IDENT" and self.toks[self.i + 1].text == "=":
            self.next()
            self.expect("OP", "=")
            return Assign(t.text, self.parse_expr(), t.line)
        if t.kind == "KEYWORD" and t.text == "if":
            self.next()
            cond = self.parse_expr()
            then = self.parse_block()
            other = []
            if self.peek().text == "else":
                self.next()
                if (self.peek().kind == "KEYWORD"
                        and self.peek().text == "if"):
                    other = [self.parse_statement()]   # else if chain
                else:
                    other = self.parse_block()
            return If(cond, then, other, t.line)
        return ExprStmt(self.parse_expr(), t.line)

    def parse_type(self) -> str:
        if self.peek().kind == "KEYWORD" and self.peek().text == "fn":
            self.next()
            self.expect("OP", "(")
            parts = []
            while self.peek().text != ")":
                parts.append(self.parse_type())
                if self.peek().text == ",":
                    self.next()
            self.expect("OP", ")")
            ret = None
            if self.peek().kind == "ARROW":
                self.next()
                ret = self.parse_type()
            return fmt_fn_type(parts, ret)
        t = self.expect("IDENT")
        if t.text == "Map":
            of = self.expect("IDENT")
            if of.text != "of":
                raise VelarisError("E100", "expected 'of' after 'Map'",
                    of.line, fixes=["write map types like: Map of Text to Int"])
            key = self.expect("IDENT").text
            to = self.expect("IDENT")
            if to.text != "to":
                raise VelarisError("E100", "expected 'to' after the key type",
                    to.line, fixes=["write map types like: Map of Text to Int"])
            return f"Map of {key} to " + self.parse_type()
        if t.text == "List":
            of = self.expect("IDENT")
            if of.text != "of":
                raise VelarisError("E100", "expected 'of' after 'List'", of.line,
                                  fixes=["write list types like: List of Int"])
            inner = self.expect("IDENT").text
            return "List of " + inner
        return t.text

    # expressions: or -> and -> not -> comparison -> add/sub -> mul/div -> atoms
    def parse_expr(self):
        left = self.parse_and()
        while self.peek().kind == "KEYWORD" and self.peek().text == "or":
            op = self.next()
            left = BinOp("or", left, self.parse_and(), op.line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek().kind == "KEYWORD" and self.peek().text == "and":
            op = self.next()
            left = BinOp("and", left, self.parse_not(), op.line)
        return left

    def parse_not(self):
        t = self.peek()
        if t.kind == "KEYWORD" and t.text == "not":
            self.next()
            return Not(self.parse_not(), t.line)
        return self.parse_cmp()

    def parse_cmp(self):
        left = self.parse_add()
        while self.peek().text in ("==", "!=", "<", ">", "<=", ">="):
            op = self.next()
            left = BinOp(op.text, left, self.parse_add(), op.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().text in ("+", "-"):
            op = self.next()
            left = BinOp(op.text, left, self.parse_mul(), op.line)
        return left

    def parse_mul(self):
        left = self.parse_postfix()
        while self.peek().text in ("*", "/", "%"):
            op = self.next()
            left = BinOp(op.text, left, self.parse_postfix(), op.line)
        return left

    def parse_postfix(self):
        e = self.parse_atom()
        while self.peek().text == ".":
            dot = self.next()
            fname = self.expect("IDENT").text
            e = FieldGet(e, fname, dot.line)
        return e

    def parse_atom(self):
        t = self.next()
        if t.kind == "KEYWORD" and t.text == "try":
            inner = self.parse_postfix()
            if not isinstance(inner, Call):
                raise VelarisError("E100",
                    "'try' needs a call to a function that can fail",
                    t.line, fixes=["write: try f(args)"])
            return TryExpr(inner, t.line)
        if t.text == "-":                      # negative numbers: -7, -x
            return Neg(self.parse_postfix(), t.line)
        if t.text == "{":                      # map literal: {"a": 1}
            entries = []
            while self.peek().text != "}":
                k = self.parse_expr()
                self.expect("OP", ":")
                entries.append((k, self.parse_expr()))
                if self.peek().text == ",":
                    self.next()
            self.expect("OP", "}")
            return MapLit(entries, t.line)
        if t.text == "[":                      # list literal: [1, 2, 3]
            items = []
            while self.peek().text != "]":
                items.append(self.parse_expr())
                if self.peek().text == ",":
                    self.next()
            self.expect("OP", "]")
            return ListLit(items, t.line)
        if t.kind == "NUMBER":
            return Num(int(t.text))
        if t.kind == "FLOAT":
            return FloatNum(float(t.text))
        if t.kind == "STRING":
            return Str(unescape(t.text[1:-1], t.line))
        if t.kind == "KEYWORD" and t.text in ("true", "false"):
            return Bool(t.text == "true")
        if t.text == "(":
            e = self.parse_expr()
            self.expect("OP", ")")
            return e
        if t.kind == "IDENT":
            if (self.peek().text == "("
                    and self.toks[self.i + 1].kind == "IDENT"
                    and self.toks[self.i + 2].text == ":"):
                self.next()                        # record literal
                fields = []
                while self.peek().text != ")":
                    fname = self.expect("IDENT").text
                    self.expect("OP", ":")
                    fields.append((fname, self.parse_expr()))
                    if self.peek().text == ",":
                        self.next()
                self.expect("OP", ")")
                return RecordLit(t.text, fields, t.line)
            if self.peek().text == "(":            # function call
                self.next()
                args = []
                while self.peek().text != ")":
                    args.append(self.parse_expr())
                    if self.peek().text == ",":
                        self.next()
                self.expect("OP", ")")
                return Call(t.text, args, t.line)
            return Var(t.text, t.line)
        raise VelarisError("E101", f"unexpected '{t.text}'", t.line,
                          fixes=["expected a number, string, variable, or function call"])


def expr_str(e) -> str:
    """Turn an AST expression back into readable source text (for errors)."""
    if isinstance(e, Num):  return str(e.value)
    if isinstance(e, FloatNum): return str(e.value)
    if isinstance(e, Neg):  return f"-{expr_str(e.value)}"
    if isinstance(e, TryExpr): return f"try {expr_str(e.value)}"
    if isinstance(e, Str):  return f'"{e.value}"'
    if isinstance(e, Bool): return "true" if e.value else "false"
    if isinstance(e, Var):  return e.name
    if isinstance(e, Call): return f"{e.name}({', '.join(expr_str(a) for a in e.args)})"
    if isinstance(e, BinOp): return f"{expr_str(e.left)} {e.op} {expr_str(e.right)}"
    if isinstance(e, Not):   return f"not {expr_str(e.value)}"
    if isinstance(e, ListLit): return "[" + ", ".join(expr_str(i) for i in e.items) + "]"
    if isinstance(e, MapLit):
        return "{" + ", ".join(f"{expr_str(k)}: {expr_str(v)}"
                               for k, v in e.entries) + "}"
    if isinstance(e, FieldGet): return f"{expr_str(e.obj)}.{e.field}"
    if isinstance(e, RecordLit):
        return e.name + "(" + ", ".join(f"{f}: {expr_str(v)}" for f, v in e.fields) + ")"
    return "?"


def expr_vars(e) -> set[str]:
    if isinstance(e, Var):   return {e.name}
    if isinstance(e, Not):   return expr_vars(e.value)
    if isinstance(e, Neg):   return expr_vars(e.value)
    if isinstance(e, TryExpr): return expr_vars(e.value)
    if isinstance(e, ListLit):
        out = set()
        for i in e.items:
            out |= expr_vars(i)
        return out
    if isinstance(e, BinOp): return expr_vars(e.left) | expr_vars(e.right)
    if isinstance(e, MapLit):
        out = set()
        for k, v in e.entries:
            out |= expr_vars(k) | expr_vars(v)
        return out
    if isinstance(e, FieldGet): return expr_vars(e.obj)
    if isinstance(e, RecordLit):
        out = set()
        for _, v in e.fields:
            out |= expr_vars(v)
        return out
    if isinstance(e, Call):
        out = set()
        for a in e.args:
            out |= expr_vars(a)
        return out
    return set()


# ---------------------------------------------------------------------------
# 3b. LOADER — resolve imports into one program, remembering which file
#     every function and record came from.
# ---------------------------------------------------------------------------

def load_program(entry: str, entry_source: str | None = None):
    funcs, records = [], []
    fn_src, rec_src = {}, {}
    visited = set()

    def load(path: str, importer: str | None, iline: int = 1):
        ap = os.path.abspath(path)
        if ap in visited:
            return                       # already loaded (diamond or cycle)
        visited.add(ap)
        source = None
        if importer is None and entry_source is not None:
            source = entry_source
        try:
            if source is None:
                source = open(path, encoding="utf-8").read()
        except OSError:
            if importer is not None:
                shipped = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "stdlib", os.path.basename(path))
                if os.path.exists(shipped):
                    visited.discard(ap)
                    return load(shipped, importer, iline)
            if importer is None:
                raise VelarisError("E001", f"cannot find file '{path}'", 1,
                    fixes=["check the file name spelling",
                           "make sure you are in the folder that contains it"])
            raise VelarisError("E512",
                f"cannot find imported file '{path}'", iline,
                fixes=["check the path in the import line",
                       "paths are relative to the importing file"],
                file=importer)
        try:
            tokens = lex(source)
            fs, rs, imports = Parser(tokens).parse_program()
        except VelarisError as e:
            e.file = e.file or path
            raise
        base = os.path.dirname(path)
        for ipath, iline in imports:
            load(os.path.join(base, ipath) if base else ipath, path, iline)
        for f in fs:
            f.src_file = path
            if f.name in fn_src:
                raise VelarisError("E513",
                    f"function '{f.name}' is defined in both "
                    f"'{fn_src[f.name]}' and '{path}'", f.line,
                    fixes=["rename one of them"], file=path)
            fn_src[f.name] = path
            funcs.append(f)
        for r in rs:
            r.src_file = path
            if r.name in rec_src:
                raise VelarisError("E513",
                    f"record '{r.name}' is defined in both "
                    f"'{rec_src[r.name]}' and '{path}'", r.line,
                    fixes=["rename one of them"], file=path)
            rec_src[r.name] = path
            records.append(r)

    load(entry, None)
    return funcs, records


def blame(fn_or_rec, err: VelarisError) -> VelarisError:
    """Attach the true source file to an error, innermost wins."""
    err.file = err.file or fn_or_rec.src_file or None
    return err


# ---------------------------------------------------------------------------
# 4. EFFECT CHECKER — the heart of Velaris
#    Rule: a function may only cause effects it declares with `uses`.
# ---------------------------------------------------------------------------

FALLIBLE_BUILTINS = {"to_int", "read_file", "fetch"}   # + get on maps

BUILTINS = {
    # name          effects needed      argument types        returns
    "print":      {"effects": {"io"},    "types": ["Any"],         "ret": "Unit"},
    "read_file":  {"effects": {"fs"},    "types": ["Text"],        "ret": "Text"},
    "write_file": {"effects": {"fs"},    "types": ["Text", "Any"], "ret": "Unit"},
    "fetch":      {"effects": {"net"},   "types": ["Text"],        "ret": "Text"},
    "now":        {"effects": {"clock"}, "types": [],              "ret": "Int"},
    "random":     {"effects": {"rand"},  "types": ["Int"],         "ret": "Int"},
    "ask":        {"effects": {"io"},     "types": ["Text"],        "ret": "Text"},
    # pure helpers (no effects) - usable everywhere, including promises
    "to_int":     {"effects": set(),      "types": ["Text"],        "ret": "Int"},
    "to_text":    {"effects": set(),      "types": ["Any"],         "ret": "Text"},
    "to_float":   {"effects": set(),      "types": ["Int"],         "ret": "Float"},
    "round":      {"effects": set(),      "types": ["Float"],       "ret": "Int"},
    "contains":   {"effects": set(),      "types": ["Text", "Text"], "ret": "Bool"},
    "split":      {"effects": set(),      "types": ["Text", "Text"], "ret": "List of Text"},
    "upper":      {"effects": set(),      "types": ["Text"],        "ret": "Text"},
    "chars":      {"effects": set(),      "types": ["Text"],        "ret": "List of Text"},
    "file_exists": {"effects": {"fs"},    "types": ["Text"],        "ret": "Bool"},
    "put":        {"effects": set(),      "types": ["Any", "Any", "Any"], "ret": "Any"},
    "get_or":     {"effects": set(),      "types": ["Any", "Any", "Any"], "ret": "Any"},
    "has":        {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "keys":       {"effects": set(),      "types": ["Any"],         "ret": "Any"},
    "all_of":     {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "any_of":     {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "lower":      {"effects": set(),      "types": ["Text"],        "ret": "Text"},
    "length":     {"effects": set(),      "types": ["Any"],         "ret": "Int"},
    "push":       {"effects": set(),      "types": ["Any", "Any"],  "ret": "Any"},
    "get":        {"effects": set(),      "types": ["Any", "Any"],  "ret": "Any"},
}

KNOWN_TYPES = {"Int", "Text", "Bool", "Float"}

def local_names_of(fn: Function) -> set[str]:
    out = {p for p, _ in fn.params}

    def gather(stmts):
        for s in stmts:
            if isinstance(s, (Let, Assign)):
                out.add(s.name)
            elif isinstance(s, If):
                gather(s.then); gather(s.other)
            elif isinstance(s, While):
                gather(s.body)
            elif isinstance(s, Check):
                if s.ok_name:
                    out.add(s.ok_name)
                out.add(s.fail_name)
                gather(s.ok_body); gather(s.fail_body)
    gather(fn.body)
    return out


def check_effects(funcs: list[Function], errors: list) -> None:
    table = {f.name: f for f in funcs}

    def effects_of_callee(name: str, line: int) -> set[str]:
        if name in BUILTINS:
            return BUILTINS[name]["effects"]
        if name in table:
            return table[name].effects
        raise VelarisError("E200", f"unknown function '{name}'", line,
                          fixes=[f"define 'fn {name}(...)' somewhere",
                                 "check the spelling of the name"])

    locals_cache: dict[str, set] = {}

    def walk(node, fn: Function):
        if isinstance(node, Call):
            if fn.name not in locals_cache:
                locals_cache[fn.name] = local_names_of(fn)
            if node.name in locals_cache[fn.name]:
                for a in node.args:          # a passed-in function is pure
                    walk(a, fn)
                return
            needed = effects_of_callee(node.name, node.line)
            missing = needed - fn.effects
            if missing:
                eff = ", ".join(sorted(missing))
                declared = ("declares no effects (it is pure)" if not fn.effects
                            else f"only declares 'uses {', '.join(sorted(fn.effects))}'")
                raise VelarisError(
                    "E300",
                    f"function '{fn.name}' calls '{node.name}' which needs "
                    f"effect '{eff}', but '{fn.name}' {declared}",
                    node.line,
                    fixes=[f"add 'uses {eff}' to the signature of '{fn.name}'",
                           f"remove the call to '{node.name}'"],
                )
            for a in node.args:
                walk(a, fn)
        elif isinstance(node, BinOp):
            walk(node.left, fn); walk(node.right, fn)
        elif isinstance(node, (Let, Return, ExprStmt, FailStmt)):
            inner = node.expr if isinstance(node, ExprStmt) else node.value
            if inner is not None:
                walk(inner, fn)
        elif isinstance(node, TryExpr):
            walk(node.value, fn)
        elif isinstance(node, Check):
            walk(node.subject, fn)
            for s in node.ok_body + node.fail_body:
                walk(s, fn)
        elif isinstance(node, If):
            walk(node.cond, fn)
            for s in node.then + node.other:
                walk(s, fn)
        elif isinstance(node, While):
            walk(node.cond, fn)
            for inv_expr, _ in node.invariants:
                walk_pure(inv_expr, fn, "invariant")
            for s in node.body:
                walk(s, fn)
        elif isinstance(node, Assign):
            walk(node.value, fn)
        elif isinstance(node, (Not, Neg)):
            walk(node.value, fn)
        elif isinstance(node, ListLit):
            for it in node.items:
                walk(it, fn)
        elif isinstance(node, MapLit):
            for k, v in node.entries:
                walk(k, fn); walk(v, fn)
        elif isinstance(node, FieldGet):
            walk(node.obj, fn)
        elif isinstance(node, RecordLit):
            for _, v in node.fields:
                walk(v, fn)

    def walk_pure(node, fn: Function, where: str):
        if isinstance(node, Call):
            if fn.name not in locals_cache:
                locals_cache[fn.name] = local_names_of(fn)
            if node.name in locals_cache[fn.name]:
                for a in node.args:
                    walk_pure(a, fn, where)
                return
            eff = effects_of_callee(node.name, node.line)
            if eff:
                raise VelarisError("E310",
                    f"the '{where}' promise of '{fn.name}' calls "
                    f"'{node.name}' which has effects "
                    f"({', '.join(sorted(eff))}); promises must be pure",
                    node.line,
                    fixes=["only use pure functions and math inside promises"])
            for a in node.args:
                walk_pure(a, fn, where)
        elif isinstance(node, BinOp):
            walk_pure(node.left, fn, where)
            walk_pure(node.right, fn, where)
        elif isinstance(node, (Not, Neg)):
            walk_pure(node.value, fn, where)
        elif isinstance(node, TryExpr):
            raise VelarisError("E310",
                f"the '{where}' promise of '{fn.name}' uses 'try'; "
                f"promises must be simple and pure", node.line,
                fixes=["only use plain values and pure functions in promises"])
        elif isinstance(node, ListLit):
            for it in node.items:
                walk_pure(it, fn, where)
        elif isinstance(node, MapLit):
            for k, v in node.entries:
                walk_pure(k, fn, where); walk_pure(v, fn, where)
        elif isinstance(node, FieldGet):
            walk_pure(node.obj, fn, where)
        elif isinstance(node, RecordLit):
            for _, v in node.fields:
                walk_pure(v, fn, where)

    for fn in funcs:
        try:
            for stmt in fn.body:
                walk(stmt, fn)
            for expr, _ in fn.requires:
                walk_pure(expr, fn, "requires")
            for expr, _ in fn.ensures:
                walk_pure(expr, fn, "ensures")
        except VelarisError as e:
            errors.append(blame(fn, e))


# ---------------------------------------------------------------------------
# 4b. TYPE CHECKER — catch wrong-type bugs before the program ever runs
#     Types: Int, Text, Bool.  "Unit" means "returns nothing".
# ---------------------------------------------------------------------------

def check_types(funcs: list[Function], records: list, errors: list) -> None:
    table = {f.name: f for f in funcs}
    rec = {}
    for r in records:
      try:
        if r.name in rec:
            raise VelarisError("E507", f"record '{r.name}' is defined twice",
                               r.line, fixes=["rename one of them"])
        if r.name in table:
            raise VelarisError("E507",
                f"'{r.name}' is used for both a record and a function",
                r.line, fixes=["rename one of them"])
        seen = set()
        for fname, _ in r.fields:
            if fname in seen:
                raise VelarisError("E507",
                    f"record '{r.name}' has field '{fname}' twice", r.line,
                    fixes=["remove the duplicate field"])
            seen.add(fname)
        rec[r.name] = dict(r.fields)
      except VelarisError as e:
        errors.append(blame(r, e))

    def callee_sig(name: str) -> tuple[list[str], str]:
        if name in BUILTINS:
            return BUILTINS[name]["types"], BUILTINS[name]["ret"]
        f = table[name]
        return [t for _, t in f.params], (f.return_type or "Unit")

    def valid_type(t: str, tvars: frozenset = frozenset()) -> bool:
        if t in KNOWN_TYPES or t in rec or t in tvars:
            return True
        if t.startswith("List of "):
            return valid_type(t[len("List of "):], tvars)
        if t.startswith("Map of "):
            rest = t[len("Map of "):]
            key, sep, val = rest.partition(" to ")
            return sep != "" and key in ("Text", "Int") and \
                valid_type(val, tvars)
        sig = fn_sig_parts(t)
        if sig is not None:
            parts, ret = sig
            return all(valid_type(p, tvars) for p in parts) and (
                ret == "Unit" or valid_type(ret, tvars))
        return False

    TYPE_HINT = ("use Int, Text, Bool, a record name, or "
                 "List of <one of those>")

    for r in records:
        for fname, ftype in r.fields:
            if not valid_type(ftype):
                errors.append(blame(r, VelarisError("E500",
                    f"unknown type '{ftype}' for field '{fname}' of "
                    f"record '{r.name}'", r.line, fixes=[TYPE_HINT])))

    # first: every declared type must be a real type
    for f in funcs:
        tvs = frozenset(f.type_vars)
        for tv in f.type_vars:
            if tv in KNOWN_TYPES or tv in rec:
                errors.append(blame(f, VelarisError("E541",
                    f"type variable '{tv}' shadows a real type", f.line,
                    fixes=["pick a fresh name like T, U, or Item"])))
            elif not any(type_mentions(pt, tv) for _, pt in f.params):
                errors.append(blame(f, VelarisError("E540",
                    f"type variable '{tv}' must appear in at least one "
                    f"parameter (a {tv} only in the return type cannot be "
                    f"inferred)", f.line,
                    fixes=[f"use {tv} in a parameter type"])))
        for pname, ptype in f.params:
            if not valid_type(ptype, tvs):
                raise VelarisError("E500", f"unknown type '{ptype}' for parameter "
                                  f"'{pname}' of '{f.name}'", f.line,
                                  fixes=[TYPE_HINT])
        if f.return_type is not None and not valid_type(f.return_type, tvs):
            raise VelarisError("E500", f"unknown return type '{f.return_type}' "
                              f"for '{f.name}'", f.line,
                              fixes=[TYPE_HINT])

    def builtin_call_fallible(node, infer) -> bool:
        if node.name in FALLIBLE_BUILTINS:
            return True
        if node.name == "get" and node.args:
            try:
                return infer(node.args[0]).startswith("Map of ")
            except VelarisError:
                return False
        return False

    def check_fn(fn: Function) -> None:
        env = dict(fn.params)                       # variable -> type
        declared_ret = fn.return_type or "Unit"

        def infer(node, allow_fail: bool = False) -> str:
            if isinstance(node, TryExpr):
                if not fn.can_fail:
                    raise VelarisError("E521",
                        f"'try' passes failure up, but '{fn.name}' cannot "
                        f"fail", node.line,
                        fixes=[f"add 'or fail' to the signature of "
                               f"'{fn.name}'",
                               "or handle it here with a check block"])
                callee = table.get(node.value.name)
                user_ok = callee is not None and callee.can_fail
                if not user_ok and not builtin_call_fallible(node.value,
                                                             infer):
                    raise VelarisError("E522",
                        f"'{node.value.name}' cannot fail - call it "
                        f"directly without 'try'", node.line,
                        fixes=["remove the 'try'"])
                return infer(node.value, allow_fail=True)
            if isinstance(node, Num):  return "Int"
            if isinstance(node, FloatNum): return "Float"
            if isinstance(node, Neg):
                t = infer(node.value)
                if t not in ("Int", "Float"):
                    raise VelarisError("E501",
                        f"'-' needs a number, but this is {t}", node.line,
                        fixes=["negate an Int or Float value"])
                return t
            if isinstance(node, Str):  return "Text"
            if isinstance(node, Bool): return "Bool"
            if isinstance(node, Var):
                if node.name in env:
                    return env[node.name]
                f2 = table.get(node.name)
                if f2 is not None:
                    if f2.type_vars:
                        raise VelarisError("E543",
                            f"'{f2.name}' is generic - generic functions "
                            f"cannot be passed as values yet", node.line,
                            fixes=["call it directly instead"])
                    if f2.effects:
                        raise VelarisError("E530",
                            f"'{f2.name}' uses effects "
                            f"({', '.join(sorted(f2.effects))}) - only pure "
                            f"functions can be passed as values", node.line,
                            fixes=["pass a function with no 'uses' clause"])
                    if f2.can_fail:
                        raise VelarisError("E530",
                            f"'{f2.name}' can fail - only functions that "
                            f"cannot fail can be passed as values", node.line,
                            fixes=["pass a function without 'or fail'"])
                    return fmt_fn_type([t for _, t in f2.params],
                                       f2.return_type)
                raise VelarisError("E402", f"unknown variable '{node.name}'",
                                  node.line,
                                  fixes=[f"declare it first: let {node.name} = ..."])
            if isinstance(node, Not):
                t = infer(node.value)
                if t != "Bool":
                    raise VelarisError("E501",
                        f"'not' needs a yes/no value (Bool), but this is {t}",
                        node.line, fixes=["use it on a comparison like not (x > 0)"])
                return "Bool"
            if isinstance(node, RecordLit):
                if node.name not in rec:
                    raise VelarisError("E508",
                        f"unknown record '{node.name}'", node.line,
                        fixes=[f"declare it first: record {node.name} {{ ... }}"])
                want = rec[node.name]
                given = {}
                for fname, v in node.fields:
                    if fname not in want:
                        raise VelarisError("E509",
                            f"record '{node.name}' has no field '{fname}'",
                            node.line,
                            fixes=[f"its fields are: {', '.join(want)}"])
                    if fname in given:
                        raise VelarisError("E509",
                            f"field '{fname}' is given twice", node.line,
                            fixes=["give each field exactly once"])
                    given[fname] = infer(v)
                    if given[fname] != want[fname]:
                        raise VelarisError("E501",
                            f"field '{fname}' of '{node.name}' holds "
                            f"{want[fname]}, but this is {given[fname]}",
                            node.line,
                            fixes=[f"give {'an' if want[fname] == 'Int' else 'a'} "
                                   f"{want[fname]} value"])
                missing = [f for f in want if f not in given]
                if missing:
                    raise VelarisError("E509",
                        f"record '{node.name}' is missing field(s): "
                        f"{', '.join(missing)}", node.line,
                        fixes=["give every field a value"])
                return node.name
            if isinstance(node, FieldGet):
                t = infer(node.obj)
                if t not in rec:
                    raise VelarisError("E510",
                        f"{t} has no fields", node.line,
                        fixes=["only records have fields, accessed like p.x"])
                if node.field not in rec[t]:
                    raise VelarisError("E510",
                        f"record '{t}' has no field '{node.field}'",
                        node.line,
                        fixes=[f"its fields are: {', '.join(rec[t])}"])
                return rec[t][node.field]
            if isinstance(node, MapLit):
                if not node.entries:
                    raise VelarisError("E506",
                        "cannot tell what an empty map holds", node.line,
                        fixes=['put at least one entry in it, e.g. {"a": 0}'])
                kt = infer(node.entries[0][0])
                vt = infer(node.entries[0][1])
                if kt not in ("Text", "Int"):
                    raise VelarisError("E501",
                        f"map keys must be Text or Int, but this is {kt}",
                        node.line, fixes=["use Text or Int keys"])
                seen_const = set()
                for k, v in node.entries:
                    if infer(k) != kt:
                        raise VelarisError("E501",
                            f"a map cannot mix {kt} and {infer(k)} keys",
                            node.line, fixes=["keep every key the same type"])
                    if infer(v) != vt:
                        raise VelarisError("E501",
                            f"a map cannot mix {vt} and {infer(v)} values",
                            node.line, fixes=["keep every value the same type"])
                    if isinstance(k, (Str, Num)):
                        if k.value in seen_const:
                            raise VelarisError("E509",
                                f"map key {expr_str(k)} is given twice",
                                node.line, fixes=["give each key once"])
                        seen_const.add(k.value)
                return f"Map of {kt} to {vt}"
            if isinstance(node, ListLit):
                if not node.items:
                    raise VelarisError("E506",
                        "cannot tell what an empty list holds", node.line,
                        fixes=["put at least one item in it, e.g. [0]"])
                t0 = infer(node.items[0])
                for it in node.items[1:]:
                    t = infer(it)
                    if t != t0:
                        raise VelarisError("E501",
                            f"a list cannot mix {t0} and {t}", node.line,
                            fixes=["keep every item in a list the same type"])
                return "List of " + t0
            if isinstance(node, Call) and node.name in (
                    "all_of", "any_of"):
                if len(node.args) != 2:
                    raise VelarisError("E401",
                        f"'{node.name}' expects 2 argument(s) but got "
                        f"{len(node.args)}", node.line,
                        fixes=["pass a list and a predicate function"])
                t0 = infer(node.args[0])
                if not t0.startswith("List of "):
                    raise VelarisError("E501",
                        f"'{node.name}' needs a list first, but this is "
                        f"{t0}", node.line, fixes=["pass a list"])
                elem = t0[len("List of "):]
                want_p = fmt_fn_type([elem], "Bool")
                t1 = infer(node.args[1])
                if t1 != want_p:
                    raise VelarisError("E501",
                        f"'{node.name}' needs a {want_p} predicate, "
                        f"but this is {t1}", node.line,
                        fixes=[f"pass a function taking {elem} and "
                               f"returning Bool"])
                return "Bool"
            if isinstance(node, Call) and node.name in (
                    "length", "push", "get", "put", "has", "keys",
                    "get_or"):
                n_want = {"length": 1, "keys": 1, "push": 2, "get": 2,
                          "has": 2, "put": 3, "get_or": 3}[node.name]
                if len(node.args) != n_want:
                    raise VelarisError("E401",
                        f"'{node.name}' expects {n_want} argument(s) "
                        f"but got {len(node.args)}", node.line,
                        fixes=[f"pass exactly {n_want} argument(s)"])
                t0 = infer(node.args[0])
                is_map = t0.startswith("Map of ")
                if is_map:
                    key_t, _, val_t = t0[len("Map of "):].partition(" to ")
                if node.name == "length":
                    if t0 == "Text" or t0.startswith("List of ") or is_map:
                        return "Int"
                    raise VelarisError("E501",
                        f"'length' works on Text, a list, or a map, "
                        f"but this is {t0}",
                        node.line, fixes=["pass a Text value, list, or map"])
                if node.name == "keys":
                    if not is_map:
                        raise VelarisError("E501",
                            f"'keys' works on a map, but this is {t0}",
                            node.line, fixes=["pass a map"])
                    return "List of " + key_t
                if node.name in ("has", "put"):
                    if not is_map:
                        raise VelarisError("E501",
                            f"'{node.name}' works on a map, but this is {t0}",
                            node.line, fixes=["pass a map as the first argument"])
                    if infer(node.args[1]) != key_t:
                        raise VelarisError("E501",
                            f"this map has {key_t} keys, but this key is "
                            f"{infer(node.args[1])}", node.line,
                            fixes=[f"use {'an' if key_t == 'Int' else 'a'} {key_t} key"])
                    if node.name == "has":
                        return "Bool"
                    if infer(node.args[2]) != val_t:
                        raise VelarisError("E501",
                            f"this map holds {val_t} values, cannot put "
                            f"{infer(node.args[2])}", node.line,
                            fixes=[f"put {'an' if val_t == 'Int' else 'a'} {val_t} value"])
                    return t0
                if node.name == "get_or":
                    if not is_map:
                        raise VelarisError("E501",
                            f"'get_or' works on a map, but this is {t0}",
                            node.line, fixes=["pass a map first"])
                    if infer(node.args[1]) != key_t:
                        raise VelarisError("E501",
                            f"this map has {key_t} keys, but this key is "
                            f"{infer(node.args[1])}", node.line,
                            fixes=[f"use {'an' if key_t == 'Int' else 'a'} "
                                   f"{key_t} key"])
                    if infer(node.args[2]) != val_t:
                        raise VelarisError("E501",
                            f"this map holds {val_t} values, but the "
                            f"default is {infer(node.args[2])}", node.line,
                            fixes=[f"use {'an' if val_t == 'Int' else 'a'} "
                                   f"{val_t} default"])
                    return val_t
                if node.name == "get" and is_map:
                    if not allow_fail:
                        raise VelarisError("E520",
                            "'get' on a map can fail - the key may be "
                            "missing, and that cannot be ignored",
                            node.line,
                            fixes=["handle it: check get(m, key) "
                                   "{ ok v { ... } fail why { ... } }",
                                   "or use get_or(m, key, default) "
                                   "which never fails",
                                   "or pass it up with: try get(m, key)"])
                    if infer(node.args[1]) != key_t:
                        raise VelarisError("E501",
                            f"this map has {key_t} keys, but this key is "
                            f"{infer(node.args[1])}", node.line,
                            fixes=[f"use {'an' if key_t == 'Int' else 'a'} {key_t} key"])
                    return val_t
                if not t0.startswith("List of "):
                    raise VelarisError("E501",
                        f"'{node.name}' needs a list first, but this is {t0}"
                        + (" - use put for maps" if node.name == "push" else ""),
                        node.line, fixes=["pass a list as the first argument"])
                elem = t0[len("List of "):]
                t1 = infer(node.args[1])
                if node.name == "push":
                    if t1 != elem:
                        raise VelarisError("E501",
                            f"this list holds {elem}, cannot push a {t1} into it",
                            node.line, fixes=[f"push {'an' if elem == 'Int' else 'a'} {elem} value"])
                    return t0
                if t1 != "Int":                      # get
                    raise VelarisError("E501",
                        f"'get' needs an Int position, but this is {t1}",
                        node.line, fixes=["positions are numbers, e.g. get(xs, 0)"])
                return elem
            if isinstance(node, Call) and node.name in env \
                    and env[node.name].startswith("fn("):
                parts, ret = fn_sig_parts(env[node.name])
                if len(node.args) != len(parts):
                    raise VelarisError("E401",
                        f"'{node.name}' expects {len(parts)} argument(s) "
                        f"but got {len(node.args)}", node.line,
                        fixes=[f"pass exactly {len(parts)} argument(s)"])
                for i, (a, want) in enumerate(zip(node.args, parts), 1):
                    got = infer(a)
                    if got != want:
                        raise VelarisError("E501",
                            f"'{node.name}' needs {want} for argument {i}, "
                            f"but this is {got}", node.line,
                            fixes=[f"pass a {want} value"])
                return ret
            if isinstance(node, Call) and node.name in FALLIBLE_BUILTINS \
                    and not allow_fail:
                raise VelarisError("E520",
                    f"'{node.name}' can fail - that cannot be ignored",
                    node.line,
                    fixes=[f"handle it: check {node.name}(...) "
                           f"{{ ok v {{ ... }} fail reason {{ ... }} }}",
                           f"or pass it up (inside a fallible function): "
                           f"try {node.name}(...)"])
            if isinstance(node, Call) and (cg := table.get(node.name)) \
                    is not None and cg.type_vars:
                if cg.can_fail and not allow_fail:
                    raise VelarisError("E520",
                        f"'{node.name}' can fail - that cannot be ignored",
                        node.line,
                        fixes=[f"handle it with a check block",
                               f"or pass it up with try {node.name}(...)"])
                ptypes = [t for _, t in cg.params]
                if len(node.args) != len(ptypes):
                    raise VelarisError("E401",
                        f"'{node.name}' expects {len(ptypes)} argument(s) "
                        f"but got {len(node.args)}", node.line,
                        fixes=[f"pass exactly {len(ptypes)} argument(s)"])
                tvset = set(cg.type_vars)
                bind: dict = {}

                def unify(want: str, got: str) -> bool:
                    if want in tvset:
                        if want in bind:
                            return bind[want] == got
                        bind[want] = got
                        return True
                    if want == got:
                        return True
                    if want.startswith("List of ") and \
                            got.startswith("List of "):
                        return unify(want[8:], got[8:])
                    if want.startswith("Map of ") and \
                            got.startswith("Map of "):
                        wk, _, wv = want[7:].partition(" to ")
                        gk, _, gv = got[7:].partition(" to ")
                        return unify(wk, gk) and unify(wv, gv)
                    wf, gf = fn_sig_parts(want), fn_sig_parts(got)
                    if wf is not None and gf is not None:
                        (wp, wr), (gp, gr) = wf, gf
                        return len(wp) == len(gp) and all(
                            unify(a, b) for a, b in zip(wp, gp)) and \
                            unify(wr, gr)
                    return False

                for i, (a, want) in enumerate(zip(node.args, ptypes), 1):
                    got = infer(a)
                    if not unify(want, got):
                        so_far = ", ".join(f"{k} = {v}"
                                           for k, v in bind.items())
                        raise VelarisError("E542",
                            f"'{node.name}' argument {i} should look like "
                            f"{want}, but this is {got}"
                            + (f" (so far: {so_far})" if so_far else ""),
                            node.line,
                            fixes=["make the arguments agree on what "
                                   f"{', '.join(cg.type_vars)} is"])

                def subst(t: str) -> str:
                    if t in bind:
                        return bind[t]
                    if t.startswith("List of "):
                        return "List of " + subst(t[8:])
                    if t.startswith("Map of "):
                        k, _, v = t[7:].partition(" to ")
                        return f"Map of {subst(k)} to {subst(v)}"
                    sig = fn_sig_parts(t)
                    if sig is not None:
                        parts, ret = sig
                        return fmt_fn_type([subst(p) for p in parts],
                                           subst(ret))
                    return t

                return subst(cg.return_type or "Unit")
            if isinstance(node, Call):
                cfn = table.get(node.name)
                if cfn is not None and cfn.can_fail and not allow_fail:
                    raise VelarisError("E520",
                        f"'{node.name}' can fail - that cannot be ignored",
                        node.line,
                        fixes=[f"handle it: check {node.name}(...) "
                               f"{{ ok v {{ ... }} fail reason {{ ... }} }}",
                               f"or pass it up (inside a fallible "
                               f"function): try {node.name}(...)"])
                ptypes, ret = callee_sig(node.name)
                if len(node.args) != len(ptypes):
                    raise VelarisError("E401",
                        f"'{node.name}' expects {len(ptypes)} argument(s) "
                        f"but got {len(node.args)}", node.line,
                        fixes=[f"pass exactly {len(ptypes)} argument(s)"])
                for i, (arg, want) in enumerate(zip(node.args, ptypes), 1):
                    got = infer(arg)
                    if got == "Unit":
                        raise VelarisError("E502",
                            f"argument {i} of '{node.name}' is a call to a "
                            f"function that returns nothing", node.line,
                            fixes=["call a function that returns a value here"])
                    if want != "Any" and got != want:
                        raise VelarisError("E501",
                            f"'{node.name}' needs {want} for argument {i}, "
                            f"but this is {got}", node.line,
                            fixes=[f"pass {'an' if want == 'Int' else 'a'} {want} value instead",
                                   f"or change the parameter type to {got}"])
                return ret
            if isinstance(node, BinOp):
                l, r = infer(node.left), infer(node.right)
                if "Unit" in (l, r):
                    raise VelarisError("E502",
                        "this expression uses a function that returns nothing",
                        node.line, fixes=["only use functions that return a value in math/text"])
                op = node.op
                if op in ("and", "or"):
                    if l == "Bool" and r == "Bool":
                        return "Bool"
                    raise VelarisError("E501",
                        f"'{op}' needs yes/no values (Bool) on both sides, "
                        f"but this is {l} {op} {r}", node.line,
                        fixes=["use comparisons on both sides, like x > 0 and x < 10"])
                NUM_FIX = ["make both sides the same number type",
                           "convert with to_float(x), or round(x) for an Int"]
                if op == "+":
                    if l == "Text" or r == "Text":
                        return "Text"                  # text joining, e.g. "n: " + 5
                    if l == r and l in ("Int", "Float"):
                        return l
                    raise VelarisError("E501", f"cannot add {l} and {r}",
                                       node.line, fixes=NUM_FIX)
                if op == "%":
                    if l == "Int" and r == "Int":
                        return "Int"
                    raise VelarisError("E501",
                        f"'%' needs Int on both sides, but this is {l} % {r}",
                        node.line, fixes=["make both sides Int"])
                if op in ("-", "*", "/"):
                    if l == r and l in ("Int", "Float"):
                        return l
                    raise VelarisError("E501",
                        f"'{op}' needs matching number types, but this is "
                        f"{l} {op} {r}", node.line, fixes=NUM_FIX)
                if op in ("<", ">", "<=", ">="):
                    if l == r and l in ("Int", "Float"):
                        return "Bool"
                    raise VelarisError("E501",
                        f"'{op}' compares matching number types, but this is "
                        f"{l} {op} {r}", node.line, fixes=NUM_FIX)
                if l != r:                             # == and !=
                    raise VelarisError("E501",
                        f"cannot compare {l} with {r}", node.line,
                        fixes=["compare values of the same type"])
                return "Bool"

        def check_stmt(node) -> None:
            if isinstance(node, Let):
                if node.ann is not None:
                    if not valid_type(node.ann, frozenset(fn.type_vars)):
                        raise VelarisError("E500",
                            f"unknown type '{node.ann}'", node.line,
                            fixes=[TYPE_HINT])
                    empty_list = (isinstance(node.value, ListLit)
                                  and not node.value.items)
                    empty_map = (isinstance(node.value, MapLit)
                                 and not node.value.entries)
                    if empty_list or empty_map:
                        want_kind = "List of " if empty_list else "Map of "
                        if not node.ann.startswith(want_kind):
                            raise VelarisError("E501",
                                f"'{node.name}' is declared {node.ann}, "
                                f"but this is an empty "
                                f"{'list' if empty_list else 'map'}",
                                node.line,
                                fixes=["match the declared type and the "
                                       "value"])
                        env[node.name] = node.ann
                        return
                    t = infer(node.value)
                    if t != node.ann:
                        raise VelarisError("E501",
                            f"'{node.name}' is declared {node.ann}, "
                            f"but this is {t}", node.line,
                            fixes=[f"give {'an' if node.ann == 'Int' else 'a'} "
                                   f"{node.ann} value",
                                   "or fix the declared type"])
                    env[node.name] = t
                    return
                t = infer(node.value)
                if t == "Unit":
                    raise VelarisError("E502",
                        f"'{node.name}' would hold nothing: that function "
                        f"returns no value", node.line,
                        fixes=["assign a function that returns a value"])
                env[node.name] = t
            elif isinstance(node, Return):
                if node.value is None:
                    if declared_ret != "Unit":
                        raise VelarisError("E503",
                            f"'{fn.name}' promises to return {declared_ret} "
                            f"but this return gives nothing", node.line,
                            fixes=[f"return a {declared_ret} value"])
                    return
                t = infer(node.value)
                if declared_ret == "Unit":
                    raise VelarisError("E503",
                        f"'{fn.name}' does not declare a return type "
                        f"but returns a {t}", node.line,
                        fixes=[f"add '-> {t}' to the signature of '{fn.name}'",
                               "or remove the returned value"])
                if t != declared_ret:
                    raise VelarisError("E503",
                        f"'{fn.name}' promises to return {declared_ret} "
                        f"but this returns {t}", node.line,
                        fixes=[f"return a {declared_ret} value",
                               f"or change the signature to '-> {t}'"])
            elif isinstance(node, ExprStmt):
                infer(node.expr)
            elif isinstance(node, FailStmt):
                if not fn.can_fail:
                    raise VelarisError("E523",
                        f"'fail' is used, but '{fn.name}' does not declare "
                        f"it can fail", node.line,
                        fixes=[f"add 'or fail' to the signature of "
                               f"'{fn.name}'"])
                t = infer(node.value)
                if t != "Text":
                    raise VelarisError("E501",
                        f"'fail' needs a Text reason, but this is {t}",
                        node.line, fixes=['write a message: fail "why"'])
            elif isinstance(node, Check):
                callee = table.get(node.subject.name)
                user_ok = callee is not None and callee.can_fail
                if not user_ok and not builtin_call_fallible(node.subject,
                                                             infer):
                    raise VelarisError("E522",
                        f"'{node.subject.name}' cannot fail - call it "
                        f"directly, no check needed", node.line,
                        fixes=["remove the check block"])
                rt = infer(node.subject, allow_fail=True)
                if rt == "Unit" and node.ok_name is not None:
                    raise VelarisError("E525",
                        f"'{node.subject.name}' returns nothing - "
                        f"write 'ok {{ ... }}' with no name", node.line,
                        fixes=["remove the name after ok"])
                if rt != "Unit" and node.ok_name is None:
                    raise VelarisError("E525",
                        f"name the result: 'ok value {{ ... }}'", node.line,
                        fixes=["add a name after ok to hold the result"])
                if node.ok_name is not None:
                    env[node.ok_name] = rt
                for s in node.ok_body:
                    check_stmt(s)
                env[node.fail_name] = "Text"
                for s in node.fail_body:
                    check_stmt(s)
            elif isinstance(node, If):
                c = infer(node.cond)
                if c != "Bool":
                    raise VelarisError("E504",
                        f"'if' needs a yes/no condition (Bool), but this is {c}",
                        node.line, fixes=["use a comparison like x > 0"])
                for s in node.then + node.other:
                    check_stmt(s)
            elif isinstance(node, While):
                c = infer(node.cond)
                if c != "Bool":
                    raise VelarisError("E504",
                        f"'while' needs a yes/no condition (Bool), but this is {c}",
                        node.line, fixes=["use a comparison like i < 10"])
                for inv_expr, iline in node.invariants:
                    if infer(inv_expr) != "Bool":
                        raise VelarisError("E505",
                            "'invariant' must be a yes/no promise (Bool)",
                            iline, fixes=["use a comparison like total >= 0"])
                for s in node.body:
                    check_stmt(s)
            elif isinstance(node, Assign):
                if node.name not in env:
                    raise VelarisError("E402",
                        f"unknown variable '{node.name}'", node.line,
                        fixes=[f"declare it first: let {node.name} = ..."])
                t = infer(node.value)
                have = env[node.name]
                if t != have:
                    raise VelarisError("E501",
                        f"'{node.name}' holds {have}, cannot put a {t} in it",
                        node.line,
                        fixes=[f"assign {'an' if have == 'Int' else 'a'} {have} value",
                               f"or make a new variable: let {node.name}2 = ..."])

        # contracts are checked first, while env holds exactly the parameters
        for expr, cline in fn.requires:
            if infer(expr) != "Bool":
                raise VelarisError("E505",
                    f"'requires' must be a yes/no promise (Bool)", cline,
                    fixes=["use a comparison like price >= 0"])
        if fn.ensures:
            if declared_ret != "Unit":
                env["result"] = declared_ret
            for expr, cline in fn.ensures:
                if infer(expr) != "Bool":
                    raise VelarisError("E505",
                        f"'ensures' must be a yes/no promise (Bool)", cline,
                        fixes=["use a comparison like result >= 0"])
            env.pop("result", None)

        for stmt in fn.body:
            check_stmt(stmt)

    m = table.get("main")
    if m is not None and m.can_fail:
        errors.append(blame(m, VelarisError("E524",
            "'main' cannot be 'or fail' - there is no one above it to "
            "handle the failure", m.line,
            fixes=["handle failures inside main with check blocks"])))
    for fn in funcs:
        try:
            check_fn(fn)
        except VelarisError as e:
            errors.append(blame(fn, e))


# ---------------------------------------------------------------------------
# 4c. PROOF CHECKER (v0.8: modular) — proofs now COMPOSE across functions.
#     * When A calls B, the prover uses B's contract as a summary of B:
#       it assumes B's 'ensures' about the result, and PROVES that A always
#       satisfies B's 'requires' at the call site (error E701 if not).
#     * Sound because Velaris has no global state: a call cannot silently
#       change the caller's variables.
#     * Anything unprovable (loops, lists, text math) falls back silently
#       to runtime promise checks.
# ---------------------------------------------------------------------------

def check_proofs(funcs: list[Function], records: list,
                 errors: list) -> None:
    try:
        import z3
    except ImportError:
        print("note: z3-solver is not installed, so promises are checked "
              "while running instead of proven beforehand "
              "(install with: pip install z3-solver)", file=sys.stderr)
        return

    table = {f.name: f for f in funcs}
    rec_fields = {r.name: r.fields for r in records}

    def provable_rec(name: str, seen=frozenset()) -> bool:
        if name in seen:
            return False
        fs = rec_fields.get(name)
        if fs is None:
            return False
        return all(ft in ("Int", "Bool", "Float")
                   or provable_rec(ft, seen | {name})
                   for _, ft in fs)

    class Unprovable(Exception):
        pass

    FELL_OFF = object()
    FAILED = object()
    saw_fp = [False]                   # FP queries earn a bigger budget

    def solver_budget() -> int:
        return 30000 if saw_fp[0] else 3000
    counter = [0]

    class RecVal:
        """A symbolic record: one Z3 value per field."""
        def __init__(self, rname: str, fields: dict):
            self.rname, self.fields = rname, fields

    class ListVal:
        """A symbolic list: a Z3 array of Ints plus a length."""
        def __init__(self, arr, length):
            self.arr, self.length = arr, length

    def mk(name: str, t: str):
        if t == "Int":
            return z3.Int(name)
        if t == "Float":
            saw_fp[0] = True
            return z3.FP(name, z3.Float64())
        return z3.Bool(name)

    def mk_rec(prefix: str, rname: str) -> "RecVal":
        out = {}
        for f, ft in rec_fields[rname]:
            if ft in ("Int", "Bool"):
                out[f] = mk(f"{prefix}.{f}", ft)
            else:
                out[f] = mk_rec(f"{prefix}.{f}", ft)
        return RecVal(rname, out)

    def rec_eq(l: "RecVal", r: "RecVal"):
        parts = []
        for f, ft in rec_fields[l.rname]:
            a, b = l.fields[f], r.fields[f]
            if isinstance(a, RecVal):
                parts.append(rec_eq(a, b))
            else:
                parts.append(a == b)
        return z3.And(*parts) if parts else z3.BoolVal(True)

    def fresh(t: str, base: str):
        counter[0] += 1
        return mk(f"__{base}_result_{counter[0]}", t)

    class Ctx:
        """Per-path proof state: path conditions + facts assumed so far.
        param_assum holds only facts about the caller's own parameters
        (never about summarized call results), so violations proven from
        it alone are guaranteed real - never false alarms."""
        def __init__(self, conds, assum, param_assum, caller):
            self.conds, self.assum = conds, assum
            self.param_assum, self.caller = param_assum, caller

        def fork(self, extra):
            return Ctx(self.conds + [extra], list(self.assum),
                       list(self.param_assum), self.caller)

    def has_fresh(e) -> bool:
        """Does this Z3 expression mention a summarized/havoc value?"""
        if isinstance(e, RecVal):
            return any(has_fresh(v) for v in e.fields.values())
        if isinstance(e, ListVal):
            return has_fresh(e.arr) or has_fresh(e.length)
        if z3.is_const(e) and e.decl().name().startswith("__"):
            return True
        return any(has_fresh(c) for c in e.children())

    def show_val(name, v, model):
        if isinstance(v, RecVal):
            inner = ", ".join(
                show_val(f, x, model).split(" = ", 1)[-1]
                if isinstance(x, RecVal)
                else f"{f}: {model.eval(x, model_completion=True)}"
                for f, x in v.fields.items())
            return f"{name} = {v.rname}({inner})"
        if isinstance(v, ListVal):
            return f"length({name}) = {model.eval(v.length, model_completion=True)}"
        return f"{name} = {model.eval(v, model_completion=True)}"

    def bind_params(fnB: Function, args_z3: list) -> dict:
        return {pname: a for (pname, _), a in zip(fnB.params, args_z3)}

    def check_requires_at(fnB, args_z3, ctx, line):
        """Prove the caller always satisfies fnB's requires here (E701)."""
        for r_expr, _ in fnB.requires:
            try:
                need = to_z3(r_expr, bind_params(fnB, args_z3), None)
            except Unprovable:
                continue
            if any(has_fresh(a) for a in args_z3) or \
                    any(has_fresh(c) for c in ctx.conds):
                continue        # could be a false alarm; runtime will guard
            solver = z3.Solver()
            solver.set("timeout", solver_budget())
            solver.add(*ctx.param_assum)
            solver.add(*ctx.conds)
            solver.add(z3.Not(need))
            if solver.check() == z3.sat:
                m = solver.model()
                vals = ", ".join(
                    show_val(pname, a, m)
                    for (pname, _), a in zip(fnB.params, args_z3))
                raise VelarisError("E701",
                    f"this call can break a promise: '{fnB.name}' requires "
                    f"{expr_str(r_expr)}, but '{ctx.caller}' can call it "
                    f"with {vals} - proven without running the program",
                    line,
                    fixes=["make sure the value meets the promise before "
                           "calling",
                           "or strengthen the caller's own 'requires' to "
                           "rule this out"])

    def predicate_formula(pfn: Function, val):
        """Translate a predicate's body into 'returns true' as a Z3
        formula over val. Only simple pure predicates qualify: one Int
        parameter, Bool result, no loops, no calls, no failure."""
        if (pfn.effects or pfn.can_fail or pfn.type_vars
                or len(pfn.params) != 1 or pfn.params[0][1] != "Int"
                or pfn.return_type != "Bool"):
            raise Unprovable()

        def paths(stmts, penv, conds):
            out = []
            for i, s in enumerate(stmts):
                if isinstance(s, (Let, Assign)):
                    penv = dict(penv)
                    penv[s.name] = to_z3(s.value, penv, None)
                elif isinstance(s, Return):
                    out.append((conds, to_z3(s.value, penv, None)))
                    return out
                elif isinstance(s, If):
                    c = to_z3(s.cond, penv, None)
                    rest = stmts[i + 1:]
                    out += paths(s.then + rest, dict(penv), conds + [c])
                    out += paths(s.other + rest, dict(penv),
                                 conds + [z3.Not(c)])
                    return out
                else:
                    raise Unprovable()  # loops etc.: too clever to inline
            raise Unprovable()          # fell off without returning
        branches = paths(pfn.body, {pfn.params[0][0]: val}, [])
        return z3.Or(*[z3.And(*(cs + [r])) if cs else r
                       for cs, r in branches])

    def summarize_call(node: Call, env, ctx, allow_fail: bool = False):
        """Model a call to a pure user function by its contract."""
        fnB = table.get(node.name)

        def summarizable(t):
            return t in ("Int", "Bool", "Float") or (
                t in rec_fields and provable_rec(t))

        if (fnB is None or fnB.effects or fnB.type_vars
                or (fnB.can_fail and not allow_fail)
                or not summarizable(fnB.return_type or "")
                or any(not summarizable(pt) for _, pt in fnB.params)):
            raise Unprovable()
        args_z3 = [to_z3(a, env, ctx) for a in node.args]
        check_requires_at(fnB, args_z3, ctx, node.line)
        if fnB.return_type in rec_fields:
            counter[0] += 1
            rv = mk_rec(f"__{fnB.name}_result_{counter[0]}",
                        fnB.return_type)
        else:
            rv = fresh(fnB.return_type, fnB.name)
        for ens_expr, _ in fnB.ensures:
            e2 = bind_params(fnB, args_z3)
            e2["result"] = rv
            try:
                ctx.assum.append(to_z3(ens_expr, e2, None))
            except Unprovable:
                pass
        return rv

    def to_z3(node, env, ctx):
        if isinstance(node, Num):  return z3.IntVal(node.value)
        if isinstance(node, FloatNum):
            saw_fp[0] = True
            return z3.FPVal(node.value, z3.Float64())
        if isinstance(node, Bool): return z3.BoolVal(node.value)
        if isinstance(node, Var):
            if node.name not in env:
                raise Unprovable()
            return env[node.name]
        if isinstance(node, Not):
            return z3.Not(to_z3(node.value, env, ctx))
        if isinstance(node, Neg):
            v = to_z3(node.value, env, ctx)
            if isinstance(v, ListVal):
                raise Unprovable()
            return -v
        if isinstance(node, RecordLit):
            if not provable_rec(node.name):
                raise Unprovable()
            vals = {}
            for f, v in node.fields:
                vals[f] = to_z3(v, env, ctx)
            return RecVal(node.name, vals)
        if isinstance(node, FieldGet):
            obj = to_z3(node.obj, env, ctx)
            if not isinstance(obj, RecVal):
                raise Unprovable()
            return obj.fields[node.field]
        if isinstance(node, ListLit):
            arr = z3.K(z3.IntSort(), z3.IntVal(0))
            vals = [to_z3(it, env, ctx) for it in node.items]
            for idx, v in enumerate(vals):
                if isinstance(v, ListVal):
                    raise Unprovable()          # lists of lists: not yet
                arr = z3.Store(arr, z3.IntVal(idx), v)
            return ListVal(arr, z3.IntVal(len(node.items)))
        if isinstance(node, Call) and node.name in ("all_of", "any_of"):
            a0 = to_z3(node.args[0], env, ctx)
            if not isinstance(a0, ListVal):
                raise Unprovable()
            parg = node.args[1]
            if not isinstance(parg, Var):
                raise Unprovable()
            pfn = table.get(parg.name)
            if pfn is None:
                raise Unprovable()      # predicate came through a variable
            counter[0] += 1
            k = z3.Int(f"__q{counter[0]}")
            body = predicate_formula(pfn, z3.Select(a0.arr, k))
            inside = z3.And(k >= 0, k < a0.length)
            if node.name == "all_of":
                return z3.ForAll([k], z3.Implies(inside, body))
            return z3.Exists([k], z3.And(inside, body))
        if isinstance(node, Call) and node.name in ("length", "get", "push"):
            a0 = to_z3(node.args[0], env, ctx)
            if not isinstance(a0, ListVal):
                raise Unprovable()              # length of Text: runtime only
            if node.name == "length":
                return a0.length
            a1 = to_z3(node.args[1], env, ctx)
            if node.name == "push":
                return ListVal(z3.Store(a0.arr, a0.length, a1),
                               a0.length + 1)
            # get: prove the read stays inside the list (E705)
            if ctx is not None:
                prove_bounds(a1, a0.length, ctx, node.line)
            return z3.Select(a0.arr, a1)
        if isinstance(node, Call):
            if ctx is None:            # inside a contract: no call summaries
                raise Unprovable()
            return summarize_call(node, env, ctx)
        if isinstance(node, BinOp):
            op = node.op
            if op == "and":
                return z3.And(to_z3(node.left, env, ctx),
                              to_z3(node.right, env, ctx))
            if op == "or":
                return z3.Or(to_z3(node.left, env, ctx),
                             to_z3(node.right, env, ctx))
            l = to_z3(node.left, env, ctx)
            r = to_z3(node.right, env, ctx)
            if isinstance(l, RecVal) or isinstance(r, RecVal):
                if not (isinstance(l, RecVal) and isinstance(r, RecVal)):
                    raise Unprovable()
                if op == "==":
                    return rec_eq(l, r)
                if op == "!=":
                    return z3.Not(rec_eq(l, r))
                raise Unprovable()
            if isinstance(l, ListVal) or isinstance(r, ListVal):
                if not (isinstance(l, ListVal) and isinstance(r, ListVal)):
                    raise Unprovable()
                if op == "==":
                    return z3.And(l.arr == r.arr, l.length == r.length)
                if op == "!=":
                    return z3.Not(z3.And(l.arr == r.arr,
                                         l.length == r.length))
                raise Unprovable()
            if op == "+":  return l + r
            if op == "-":  return l - r
            if op == "*":  return l * r
            if op == "==":
                if z3.is_fp(l) or z3.is_fp(r):
                    return z3.fpEQ(l, r)     # IEEE: NaN != NaN, +0 == -0
                return l == r
            if op == "!=":
                if z3.is_fp(l) or z3.is_fp(r):
                    return z3.Not(z3.fpEQ(l, r))
                return l != r
            if op == "<":  return l < r
            if op == ">":  return l > r
            if op == "<=": return l <= r
            if op == ">=": return l >= r
        raise Unprovable()             # Str, ListLit, '/', anything else

    def prove_bounds(idx, length, ctx, line):
        """Prove 0 <= idx < length; report only provably-real violations."""
        if has_fresh(idx) or has_fresh(length) or \
                any(has_fresh(c) for c in ctx.conds):
            return                       # runtime bounds check still guards
        solver = z3.Solver()
        solver.set("timeout", solver_budget())
        solver.add(*ctx.param_assum)
        solver.add(*ctx.conds)
        solver.add(z3.Not(z3.And(idx >= 0, idx < length)))
        if solver.check() == z3.sat:
            m = solver.model()
            raise VelarisError("E705",
                f"this 'get' can reach position "
                f"{m.eval(idx, model_completion=True)}, but the list has "
                f"{m.eval(length, model_completion=True)} item(s) - proven "
                f"without running the program", line,
                fixes=["positions go from 0 to length - 1",
                       "guard the read: if i < length(xs) { ... }"])

    def scan_calls(node, env, ctx):
        """Inside expressions we cannot fully model (like text joining),
        still find user-function calls and prove their requires hold,
        and prove every 'get' stays inside its list."""
        if isinstance(node, Call):
            for a in node.args:
                scan_calls(a, env, ctx)
            if node.name == "get" and len(node.args) == 2:
                try:
                    a0 = to_z3(node.args[0], env, ctx)
                    a1 = to_z3(node.args[1], env, ctx)
                    if isinstance(a0, ListVal):
                        prove_bounds(a1, a0.length, ctx, node.line)
                except Unprovable:
                    pass
            fnB = table.get(node.name)
            if (fnB is not None and fnB.requires
                    and len(fnB.params) == len(node.args)
                    and all(pt in ("Int", "Bool", "Float", "List of Int")
                            or (pt in rec_fields and provable_rec(pt))
                            for _, pt in fnB.params)):
                try:
                    args_z3 = [to_z3(a, env, ctx) for a in node.args]
                except Unprovable:
                    return
                check_requires_at(fnB, args_z3, ctx, node.line)
        elif isinstance(node, BinOp):
            scan_calls(node.left, env, ctx)
            scan_calls(node.right, env, ctx)
        elif isinstance(node, (Not, Neg, TryExpr)):
            scan_calls(node.value, env, ctx)
        elif isinstance(node, ListLit):
            for it in node.items:
                scan_calls(it, env, ctx)
        elif isinstance(node, MapLit):
            for k, v in node.entries:
                scan_calls(k, env, ctx); scan_calls(v, env, ctx)
        elif isinstance(node, FieldGet):
            scan_calls(node.obj, env, ctx)
        elif isinstance(node, RecordLit):
            for _, v in node.fields:
                scan_calls(v, env, ctx)

    def assigned_names(stmts, out):
        for s in stmts:
            if isinstance(s, (Let, Assign)):
                out.add(s.name)
            elif isinstance(s, If):
                assigned_names(s.then, out)
                assigned_names(s.other, out)
            elif isinstance(s, While):
                assigned_names(s.body, out)
        return out

    def prove_invariant(inv_expr, iline, env, ctx, where):
        """Prove one invariant under the given state; honest wording only."""
        try:
            goal = to_z3(inv_expr, env, None)
        except Unprovable:
            return                       # can't model it; runtime will check
        solver = z3.Solver()
        solver.set("timeout", solver_budget())
        solver.add(*ctx.assum)
        solver.add(*ctx.conds)
        solver.add(z3.Not(goal))
        verdict = solver.check()
        if verdict == z3.sat:
            m = solver.model()
            names = sorted(n for n in expr_vars(inv_expr) if n in env)
            vals = ", ".join(
                f"{n} = {m.eval(env[n], model_completion=True)}"
                for n in names)
            raise VelarisError("E703",
                f"cannot prove the loop keeps 'invariant "
                f"{expr_str(inv_expr)}' {where} in '{ctx.caller}' - "
                f"the promises allow: {vals}", iline,
                fixes=["fix the loop so the invariant always holds",
                       "or strengthen the invariant(s) to rule this "
                       "state out",
                       "or remove the invariant (it will then be checked "
                       "at runtime instead)"])
        if verdict != z3.unsat:
            raise Unprovable()

    def havoc_like(env, names):
        """Fresh unknowns for every variable the loop can change.
        Returns (new_env, facts) - facts like 'list lengths stay >= 0'."""
        out = dict(env)
        facts = []
        for n in names:
            old = env.get(n)
            if isinstance(old, RecVal):
                counter[0] += 1
                out[n] = mk_rec(f"__{n}_{counter[0]}", old.rname)
            elif isinstance(old, ListVal):
                counter[0] += 1
                arr = z3.Array(f"__{n}_arr_{counter[0]}",
                               z3.IntSort(), z3.IntSort())
                ln = z3.Int(f"__{n}_len_{counter[0]}")
                out[n] = ListVal(arr, ln)
                facts.append(ln >= 0)
            elif old is not None and z3.is_bool(old):
                out[n] = fresh("Bool", n)
            elif old is not None and z3.is_fp(old):
                out[n] = fresh("Float", n)
            else:
                out[n] = fresh("Int", n)
        return out, facts

    def explore(stmts, env, ctx):
        i = 0
        while i < len(stmts):
            s = stmts[i]
            if isinstance(s, FailStmt):
                return [(ctx, FAILED, dict(env))]  # this path never returns
            if isinstance(s, Check):
                rest = stmts[i + 1:]
                rv = summarize_call(s.subject, env, ctx, allow_fail=True)
                env_ok = dict(env)
                if s.ok_name is not None:
                    env_ok[s.ok_name] = rv
                ok_paths = explore(list(s.ok_body) + rest, env_ok, ctx)
                env_fail = dict(env)
                env_fail.pop(s.fail_name, None)   # a Text reason: unmodeled
                fail_paths = explore(list(s.fail_body) + rest, env_fail,
                                     ctx)
                return ok_paths + fail_paths
            if (isinstance(s, (Let, Assign)) and
                    isinstance(s.value, TryExpr)):
                rest = stmts[i + 1:]
                rv = summarize_call(s.value.value, env, ctx,
                                    allow_fail=True)
                env2 = dict(env)
                env2[s.name] = rv
                return (explore(rest, env2, ctx)
                        + [(ctx, FAILED, dict(env))])
            if isinstance(s, Return) and isinstance(s.value, TryExpr):
                rv = summarize_call(s.value.value, env, ctx,
                                    allow_fail=True)
                return [(ctx, rv, dict(env)), (ctx, FAILED, dict(env))]
            if (isinstance(s, ExprStmt)
                    and isinstance(s.expr, TryExpr)):
                rest = stmts[i + 1:]
                summarize_call(s.expr.value, env, ctx, allow_fail=True)
                return (explore(rest, dict(env), ctx)
                        + [(ctx, FAILED, dict(env))])
            if isinstance(s, (Let, Assign)):
                env[s.name] = to_z3(s.value, env, ctx)
            elif isinstance(s, Return):
                r = FELL_OFF if s.value is None else to_z3(s.value, env, ctx)
                return [(ctx, r, dict(env))]
            elif isinstance(s, If):
                c = to_z3(s.cond, env, ctx)
                rest = stmts[i + 1:]
                yes = explore(list(s.then) + rest, dict(env), ctx.fork(c))
                no = explore(list(s.other) + rest, dict(env),
                             ctx.fork(z3.Not(c)))
                return yes + no
            elif isinstance(s, While):
                if not s.invariants:
                    raise Unprovable()   # no bridge across this loop
                # 1. ENTRY: every invariant must hold before the first spin
                for inv_expr, iline in s.invariants:
                    prove_invariant(inv_expr, iline, env, ctx,
                                    "when the loop starts")
                changed = assigned_names(s.body, set())
                # 2. PRESERVATION: from ANY state the invariants allow,
                #    one loop step must land back inside the invariants
                env_h, hfacts = havoc_like(env, changed)
                facts = list(hfacts)
                for inv_expr, _ in s.invariants:
                    try:
                        facts.append(to_z3(inv_expr, env_h, None))
                    except Unprovable:
                        pass
                cond_h = to_z3(s.cond, env_h, ctx)
                ctx_body = Ctx(ctx.conds + facts + [cond_h],
                               list(ctx.assum) + facts + [cond_h],
                               list(ctx.param_assum), ctx.caller)
                exits = []
                for pctx, ret, penv in explore(list(s.body), dict(env_h),
                                               ctx_body):
                    if ret is FELL_OFF:
                        for inv_expr, iline in s.invariants:
                            prove_invariant(inv_expr, iline, penv, pctx,
                                            "after one loop step")
                    else:
                        exits.append((pctx, ret, penv))  # return inside loop
                # 3. AFTERWARD: all we know is invariants hold, cond is false
                env_a, hfacts_a = havoc_like(env, changed)
                facts_a = list(hfacts_a)
                for inv_expr, _ in s.invariants:
                    try:
                        facts_a.append(to_z3(inv_expr, env_a, None))
                    except Unprovable:
                        pass
                cond_a = to_z3(s.cond, env_a, ctx)
                ctx_after = Ctx(ctx.conds + facts_a + [z3.Not(cond_a)],
                                list(ctx.assum) + facts_a + [z3.Not(cond_a)],
                                list(ctx.param_assum), ctx.caller)
                return exits + explore(stmts[i + 1:], env_a, ctx_after)
            elif isinstance(s, ExprStmt):
                try:
                    to_z3(s.expr, env, ctx)
                except Unprovable:
                    scan_calls(s.expr, env, ctx)   # still verify call sites
            else:
                raise Unprovable()
            i += 1
        return [(ctx, FELL_OFF, dict(env))]

    for fn in funcs:
        saw_fp[0] = False              # FP budget only when FP appears
        env = {}
        list_facts = []
        for pname, ptype in fn.params:
            if ptype in ("Int", "Bool", "Float"):
                env[pname] = mk(pname, ptype)
            elif ptype == "List of Int":
                arr = z3.Array(pname, z3.IntSort(), z3.IntSort())
                ln = z3.Int(pname + "__n")
                env[pname] = ListVal(arr, ln)
                list_facts.append(ln >= 0)
            elif ptype in rec_fields and provable_rec(ptype):
                env[pname] = mk_rec(pname, ptype)
        ctx = Ctx([], list(list_facts), list(list_facts), fn.name)
        try:
            for r_expr, _ in fn.requires:
                # If a premise cannot be translated, the whole proof is
                # off: proving with dropped premises would manufacture
                # false counterexamples. Runtime checks still guard.
                fact = to_z3(r_expr, dict(env), None)
                ctx.assum.append(fact)
                ctx.param_assum.append(fact)
            paths = explore(list(fn.body), dict(env), ctx)
            if not fn.ensures:
                continue
            for pctx, ret, _ in paths:
                if ret is FAILED:
                    continue           # ensures speaks only of returns
                if ret is FELL_OFF:
                    raise Unprovable()
                for ens_expr, cline in fn.ensures:
                    e2 = dict(env)
                    e2["result"] = ret
                    goal = to_z3(ens_expr, e2, None)
                    solver = z3.Solver()
                    solver.set("timeout", solver_budget())
                    solver.add(*pctx.assum)
                    solver.add(*pctx.conds)
                    solver.add(z3.Not(goal))
                    verdict = solver.check()
                    if verdict == z3.sat:
                        if has_fresh(ret) or any(has_fresh(c)
                                                 for c in pctx.conds):
                            # counterexample depends on a summarized call:
                            # might be impossible in reality - never claim
                            # "proven"; fall back to runtime checks instead
                            raise Unprovable()
                        m = solver.model()
                        vals = ", ".join(
                            show_val(p, v, m)
                            for p, v in sorted(env.items()))
                        if isinstance(ret, RecVal):
                            rv = show_val("r", ret, m).split(" = ", 1)[-1]
                        elif isinstance(ret, ListVal):
                            rv = "a list"
                        else:
                            rv = m.eval(ret, model_completion=True)
                        raise VelarisError("E700",
                            f"promise cannot be kept: '{fn.name}' ensures "
                            f"{expr_str(ens_expr)} - proven without running "
                            f"the program: {vals} gives result = {rv}",
                            cline,
                            fixes=["fix the code so the promise holds for "
                                   "every allowed input",
                                   "or add a 'requires' that rules out "
                                   "such inputs"])
                    if verdict != z3.unsat:
                        raise Unprovable()
        except Unprovable:
            continue                    # runtime promise checks still guard
        except z3.Z3Exception:
            continue                    # solver hiccup: runtime still guards
        except VelarisError as e:
            errors.append(blame(fn, e))
            continue


# ---------------------------------------------------------------------------
# 4d. NATIVE COMPILER (v0.9) — compile pure Int functions to machine code
#     via LLVM. Eligible: params and return are Int; body uses only math,
#     comparisons, and/or/not, if, while, let/assign, and calls to other
#     eligible functions. No effects, no contracts (those must keep their
#     runtime promise checks), no '/', no Text, no lists.
# ---------------------------------------------------------------------------

_NATIVE_KEEPALIVE = []          # prevents the JIT engine being garbage-collected


def native_eligible(funcs: list[Function]) -> set[str]:
    table = {f.name: f for f in funcs}

    def locally_ok(fn: Function):
        if fn.effects or fn.requires or fn.ensures or fn.can_fail \
                or fn.type_vars:
            return None
        if fn.return_type not in ("Int", "Float", "Bool"):
            return None
        if any(pt not in ("Int", "Float", "Bool") for _, pt in fn.params):
            return None
        calls, ok = set(), [True]

        def we(e):
            if isinstance(e, (Num, FloatNum, Bool, Var)):
                return
            if isinstance(e, (Not, Neg)):
                we(e.value)
            elif isinstance(e, BinOp):
                if e.op in ("/", "%"):
                    ok[0] = False       # backend semantics differ on negatives
                else:
                    we(e.left); we(e.right)
            elif isinstance(e, Call):
                if e.name in BUILTINS or e.name not in table:
                    ok[0] = False
                else:
                    calls.add(e.name)
                    for a in e.args:
                        we(a)
            else:
                ok[0] = False          # Str, ListLit

        def ws(s):
            if isinstance(s, (Let, Assign)):
                we(s.value)
            elif isinstance(s, Return):
                if s.value is None:
                    ok[0] = False
                else:
                    we(s.value)
            elif isinstance(s, If):
                we(s.cond)
                for x in s.then + s.other:
                    ws(x)
            elif isinstance(s, While):
                if s.invariants:
                    ok[0] = False      # invariant checks must not be skipped
                we(s.cond)
                for x in s.body:
                    ws(x)
            elif isinstance(s, ExprStmt):
                we(s.expr)
            else:
                ok[0] = False

        for s in fn.body:
            ws(s)
        return calls if ok[0] else None

    cand = {}
    for f in funcs:
        c = locally_ok(f)
        if c is not None:
            cand[f.name] = c
    changed = True
    while changed:                      # drop anyone calling a non-candidate
        changed = False
        for name in list(cand):
            if not cand[name] <= set(cand):
                del cand[name]
                changed = True
    return set(cand)


def compile_native(funcs: list[Function]) -> dict:
    eligible = native_eligible(funcs)
    if not eligible:
        return {}
    try:
        from llvmlite import ir, binding
    except ImportError:
        print("note: llvmlite is not installed - running fully interpreted "
              "(for native speed: pip install llvmlite)", file=sys.stderr)
        return {}

    i64 = ir.IntType(64)
    f64 = ir.DoubleType()
    LTY = {"Int": i64, "Bool": i64, "Float": f64}
    module = ir.Module(name="velaris")
    table = {f.name: f for f in funcs}
    llvm_fns = {}
    for name in eligible:
        fn = table[name]
        fty = ir.FunctionType(LTY[fn.return_type],
                              [LTY[pt] for _, pt in fn.params])
        llvm_fns[name] = ir.Function(module, fty, name=name)

    def var_types(fn: Function) -> dict:
        """Sequentially infer each local's Velaris type for typed allocas."""
        tenv = dict(fn.params)

        def te(e) -> str:
            if isinstance(e, Num):
                return "Int"
            if isinstance(e, FloatNum):
                return "Float"
            if isinstance(e, Bool):
                return "Bool"
            if isinstance(e, Var):
                return tenv[e.name]
            if isinstance(e, Not):
                return "Bool"
            if isinstance(e, Neg):
                return te(e.value)
            if isinstance(e, Call):
                return table[e.name].return_type
            if isinstance(e, BinOp):
                if e.op in ("and", "or", "==", "!=", "<", ">", "<=", ">="):
                    return "Bool"
                return te(e.left)
            return "Int"

        def ts(stmts):
            for s in stmts:
                if isinstance(s, (Let, Assign)):
                    tenv.setdefault(s.name, te(s.value))
                elif isinstance(s, If):
                    ts(s.then); ts(s.other)
                elif isinstance(s, While):
                    ts(s.body)
        ts(fn.body)
        return tenv

    def collect_names(stmts, out):
        for s in stmts:
            if isinstance(s, (Let, Assign)):
                out.add(s.name)
            elif isinstance(s, If):
                collect_names(s.then, out); collect_names(s.other, out)
            elif isinstance(s, While):
                collect_names(s.body, out)

    CMP = {"==": "==", "!=": "!=", "<": "<", ">": ">", "<=": "<=", ">=": ">="}

    for name in eligible:
        fn = table[name]
        lf = llvm_fns[name]
        entry = lf.append_basic_block("entry")
        b = ir.IRBuilder(entry)
        slots = {}
        tenv = var_types(fn)
        names = {p for p, _ in fn.params}
        collect_names(fn.body, names)
        for n in sorted(names):
            slots[n] = b.alloca(LTY[tenv.get(n, "Int")], name=n)
        for (pname, _), arg in zip(fn.params, lf.args):
            arg.name = pname
            b.store(arg, slots[pname])

        def ee(e):                    # emit expression (i64 or double)
            if isinstance(e, Num):
                return i64(e.value)
            if isinstance(e, FloatNum):
                return ir.Constant(f64, e.value)
            if isinstance(e, Bool):
                return i64(1 if e.value else 0)
            if isinstance(e, Var):
                return b.load(slots[e.name])
            if isinstance(e, Not):
                return b.xor(ee(e.value), i64(1))
            if isinstance(e, Neg):
                v = ee(e.value)
                if v.type == f64:
                    return b.fsub(ir.Constant(f64, 0.0), v)
                return b.sub(i64(0), v)
            if isinstance(e, Call):
                return b.call(llvm_fns[e.name], [ee(a) for a in e.args])
            if isinstance(e, BinOp):
                if e.op == "and":
                    return b.and_(ee(e.left), ee(e.right))
                if e.op == "or":
                    return b.or_(ee(e.left), ee(e.right))
                l, r = ee(e.left), ee(e.right)
                flt = l.type == f64
                if e.op == "+":
                    return b.fadd(l, r) if flt else b.add(l, r)
                if e.op == "-":
                    return b.fsub(l, r) if flt else b.sub(l, r)
                if e.op == "*":
                    return b.fmul(l, r) if flt else b.mul(l, r)
                if flt:
                    return b.zext(b.fcmp_ordered(CMP[e.op], l, r), i64)
                return b.zext(b.icmp_signed(CMP[e.op], l, r), i64)
            raise AssertionError("unreachable")

        def truthy(e):
            return b.icmp_signed("!=", ee(e), i64(0))

        def es(stmts):                              # emit statements
            for s in stmts:
                if b.block.is_terminated:
                    return
                if isinstance(s, (Let, Assign)):
                    b.store(ee(s.value), slots[s.name])
                elif isinstance(s, Return):
                    b.ret(ee(s.value))
                elif isinstance(s, ExprStmt):
                    ee(s.expr)
                elif isinstance(s, If):
                    bb_then = lf.append_basic_block("then")
                    bb_else = lf.append_basic_block("else")
                    bb_cont = lf.append_basic_block("cont")
                    b.cbranch(truthy(s.cond), bb_then, bb_else)
                    b.position_at_end(bb_then)
                    es(s.then)
                    if not b.block.is_terminated:
                        b.branch(bb_cont)
                    b.position_at_end(bb_else)
                    es(s.other)
                    if not b.block.is_terminated:
                        b.branch(bb_cont)
                    b.position_at_end(bb_cont)
                elif isinstance(s, While):
                    bb_cond = lf.append_basic_block("wcond")
                    bb_body = lf.append_basic_block("wbody")
                    bb_end = lf.append_basic_block("wend")
                    b.branch(bb_cond)
                    b.position_at_end(bb_cond)
                    b.cbranch(truthy(s.cond), bb_body, bb_end)
                    b.position_at_end(bb_body)
                    es(s.body)
                    if not b.block.is_terminated:
                        b.branch(bb_cond)
                    b.position_at_end(bb_end)

        es(fn.body)
        if not b.block.is_terminated:
            b.ret(ir.Constant(f64, 0.0)
                  if fn.return_type == "Float" else i64(0))

    for init in ("initialize", "initialize_native_target",
                 "initialize_native_asmprinter"):
        try:                   # each may be required or deprecated,
            getattr(binding, init)()       # depending on llvmlite version
        except (RuntimeError, AttributeError):
            pass
    target = binding.Target.from_default_triple()
    tm = target.create_target_machine(opt=3)
    backing = binding.parse_assembly(str(module))
    backing.verify()
    try:                                    # optimize IR if this API exists
        pto = binding.create_pipeline_tuning_options()
        pto.speed_level = 3
        pb = binding.create_pass_builder(tm, pto)
        pb.getModulePassManager().run(backing, pb)
    except Exception:
        try:
            pmb = binding.PassManagerBuilder()
            pmb.opt_level = 3
            pm = binding.ModulePassManager()
            pmb.populate(pm)
            pm.run(backing)
        except Exception:
            pass                            # unoptimized native is still fast
    engine = binding.create_mcjit_compiler(backing, tm)
    engine.finalize_object()
    _NATIVE_KEEPALIVE.append(engine)

    import ctypes
    CT = {"Int": ctypes.c_int64, "Bool": ctypes.c_int64,
          "Float": ctypes.c_double}
    out = {}
    for name in eligible:
        fn = table[name]
        proto = ctypes.CFUNCTYPE(CT[fn.return_type],
                                 *[CT[pt] for _, pt in fn.params])
        raw = proto(engine.get_function_address(name))
        if fn.return_type == "Bool":
            out[name] = (lambda *a, _raw=raw: bool(_raw(*a)))
        else:
            out[name] = raw
    return out


# ---------------------------------------------------------------------------
# 5. INTERPRETER — actually run the program (main() is the entry point)
# ---------------------------------------------------------------------------

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value


class FailSignal(Exception):
    def __init__(self, reason): self.reason = reason


class RecordValue:
    def __init__(self, rname: str, fields: dict):
        self.rname, self.fields = rname, fields

    def __eq__(self, other):
        return (isinstance(other, RecordValue)
                and self.rname == other.rname
                and self.fields == other.fields)


def to_text(v) -> str:
    if isinstance(v, Function):
        return f"fn {v.name}"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{to_text(k)}: {to_text(x)}"
                               for k, x in v.items()) + "}"
    if isinstance(v, RecordValue):
        inner = ", ".join(f"{k}: {to_text(x)}" for k, x in v.fields.items())
        return f"{v.rname}({inner})"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return "[" + ", ".join(to_text(x) for x in v) + "]"
    return str(v)


def run_builtin(name: str, args: list, line: int):
    import time as _time
    import random as _rand
    if name == "print":
        print(to_text(args[0]))
        return None
    if name == "ask":
        try:
            return input(str(args[0]) + " ")
        except (EOFError, KeyboardInterrupt):
            raise VelarisError("E607", "no input available to read", line,
                               fixes=["run this program in a terminal where "
                                      "you can type an answer"])
    if name == "to_int":
        t = str(args[0]).strip()
        body = t[1:] if t.startswith("-") else t
        if not body.isdigit():
            raise FailSignal(f"'{args[0]}' is not a whole number")
        return int(t)
    if name == "to_text":
        return to_text(args[0])
    if name == "to_float":
        return float(args[0])
    if name == "round":
        return int(round(args[0]))
    if name == "contains":
        return str(args[1]) in str(args[0])
    if name == "split":
        if args[1] == "":
            raise VelarisError("E609", "cannot split by empty text", line,
                               fixes=['use a separator like " " or ","'])
        return str(args[0]).split(str(args[1]))
    if name == "upper":
        return str(args[0]).upper()
    if name == "chars":
        return list(str(args[0]))
    if name == "file_exists":
        return os.path.exists(str(args[0]))
    if name == "lower":
        return str(args[0]).lower()
    if name == "length":
        return len(args[0])
    if name == "push":
        return args[0] + [args[1]]
    if name == "put":
        m, k, v = args
        out = dict(m); out[k] = v
        return out
    if name == "has":
        return args[1] in args[0]
    if name == "keys":
        return list(args[0].keys())
    if name == "get_or":
        m, k, d = args
        return m.get(k, d)
    if name == "get" and isinstance(args[0], dict):
        m, k = args
        if k not in m:
            key_txt = f"'{k}'" if isinstance(k, str) else to_text(k)
            raise FailSignal(f"map has no key {key_txt}")
        return m[k]
    if name == "get":
        xs, i = args
        if i < 0 or i >= len(xs):
            raise VelarisError("E602",
                f"position {i} is outside the list (it has {len(xs)} item(s))",
                line, fixes=["positions go from 0 to length - 1",
                             "check with length(...) before using get"])
        return xs[i]
    if name == "read_file":
        try:
            return open(args[0], encoding="utf-8").read()
        except OSError:
            raise FailSignal(f"cannot read file '{args[0]}'")
    if name == "write_file":
        with open(args[0], "w", encoding="utf-8") as f:
            f.write(str(args[1]))
        return None
    if name == "fetch":
        import urllib.request
        import urllib.error
        url = str(args[0])
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "velaris/0.11"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read(65536).decode("utf-8", errors="replace")
        except Exception:
            raise FailSignal(f"cannot reach '{url}'")
    if name == "now":
        return int(_time.time())
    if name == "random":
        n = args[0]
        if n <= 0:
            raise VelarisError("E405", "random(n) needs n greater than 0", line,
                              fixes=["pass a positive number, e.g. random(6)"])
        return _rand.randrange(n)


def build_runtime(funcs: list[Function], native: dict | None = None):
    native = native or {}
    table = {f.name: f for f in funcs}

    def call(name: str, args: list, line: int):
        if name in ("all_of", "any_of"):
            xs, p = args
            hits = (call_function(p, [v], line) for v in xs)
            return all(hits) if name == "all_of" else any(hits)
        if name in BUILTINS:
            return run_builtin(name, args, line)
        if name in native:
            return native[name](*args)     # machine code, C-like speed
        fn = table.get(name)
        if fn is None:
            raise VelarisError("E200", f"unknown function '{name}'", line,
                               fixes=[f"define 'fn {name}(...)' somewhere",
                                      "check the spelling of the name"])
        return call_function(fn, args, line)

    def call_function(fn: Function, args: list, line: int):
        name = fn.name
        if len(args) != len(fn.params):
            raise VelarisError("E401",
                f"'{name}' expects {len(fn.params)} argument(s) but got {len(args)}",
                line, fixes=[f"pass exactly {len(fn.params)} argument(s)"])
        env = {p[0]: a for p, a in zip(fn.params, args)}
        entry = dict(env)                  # snapshot: promises see entry values

        def vals(expr, extra=None):
            scope = dict(entry)
            if extra is not None:
                scope["result"] = extra[0]
            names = sorted(n for n in expr_vars(expr) if n in scope)
            return ", ".join(f"{n} = {scope[n]}" for n in names)

        for expr, cline in fn.requires:
            if not eval_(expr, dict(entry)):
                raise VelarisError("E600",
                    f"broken promise: '{name}' requires "
                    f"{expr_str(expr)}  ({vals(expr)})", cline,
                    fixes=["check the value before calling this function",
                           "or loosen the promise if it is too strict"])

        retval = None
        try:
            for stmt in fn.body:
                run(stmt, env)
        except ReturnSignal as r:
            retval = r.value
        except VelarisError as e:
            raise blame(fn, e)

        for expr, cline in fn.ensures:
            check_env = dict(entry)
            check_env["result"] = retval
            if not eval_(expr, check_env):
                raise VelarisError("E601",
                    f"broken promise: '{name}' ensures "
                    f"{expr_str(expr)}  ({vals(expr, (retval,))})", cline,
                    fixes=["the code does not keep this promise - fix the code",
                           "or fix the promise if it is wrong"])
        return retval

    def run(node, env):
        if isinstance(node, Let):
            env[node.name] = eval_(node.value, env)
        elif isinstance(node, Return):
            raise ReturnSignal(None if node.value is None else eval_(node.value, env))
        elif isinstance(node, ExprStmt):
            eval_(node.expr, env)
        elif isinstance(node, FailStmt):
            raise FailSignal(eval_(node.value, env))
        elif isinstance(node, Check):
            try:
                val = eval_(node.subject, env)
            except FailSignal as f:
                env[node.fail_name] = f.reason
                for s in node.fail_body:
                    run(s, env)
            else:
                if node.ok_name is not None:
                    env[node.ok_name] = val
                for s in node.ok_body:
                    run(s, env)
        elif isinstance(node, If):
            branch = node.then if eval_(node.cond, env) else node.other
            for s in branch:
                run(s, env)
        elif isinstance(node, While):
            def check_invariants():
                for inv_expr, iline in node.invariants:
                    if not eval_(inv_expr, env):
                        names = sorted(n for n in expr_vars(inv_expr)
                                       if n in env)
                        vals = ", ".join(f"{n} = {to_text(env[n])}"
                                         for n in names)
                        raise VelarisError("E704",
                            f"loop broke its promise: invariant "
                            f"{expr_str(inv_expr)}  ({vals})", iline,
                            fixes=["fix the loop body so the promise holds "
                                   "on every step",
                                   "or fix the invariant if it is wrong"])
            check_invariants()
            while eval_(node.cond, env):
                for s in node.body:
                    run(s, env)
                check_invariants()
        elif isinstance(node, Assign):
            env[node.name] = eval_(node.value, env)

    def eval_(node, env):
        if isinstance(node, Num):  return node.value
        if isinstance(node, FloatNum): return node.value
        if isinstance(node, Neg):  return -eval_(node.value, env)
        if isinstance(node, TryExpr):
            return eval_(node.value, env)   # a failure keeps rising
        if isinstance(node, Str):  return node.value
        if isinstance(node, Bool): return node.value
        if isinstance(node, Var):
            if node.name in env:
                return env[node.name]
            if node.name in table:
                return table[node.name]        # a function, as a value
            raise VelarisError("E402", f"unknown variable '{node.name}'", node.line,
                              fixes=[f"declare it first: let {node.name} = ..."])
        if isinstance(node, Call):
            if node.name in env and isinstance(env[node.name], Function):
                return call_function(env[node.name],
                                     [eval_(a, env) for a in node.args],
                                     node.line)
            return call(node.name, [eval_(a, env) for a in node.args], node.line)
        if isinstance(node, Not):
            return not eval_(node.value, env)
        if isinstance(node, RecordLit):
            return RecordValue(node.name,
                               {f: eval_(v, env) for f, v in node.fields})
        if isinstance(node, FieldGet):
            return eval_(node.obj, env).fields[node.field]
        if isinstance(node, ListLit):
            return [eval_(i, env) for i in node.items]
        if isinstance(node, MapLit):
            return {eval_(k, env): eval_(v, env) for k, v in node.entries}
        if isinstance(node, BinOp):
            if node.op == "and":
                return eval_(node.left, env) and eval_(node.right, env)
            if node.op == "or":
                return eval_(node.left, env) or eval_(node.right, env)
            l, r = eval_(node.left, env), eval_(node.right, env)
            if node.op == "+":
                if isinstance(l, str) or isinstance(r, str):
                    return to_text(l) + to_text(r)
                return l + r
            if node.op == "-":  return l - r
            if node.op == "*":  return l * r
            if node.op == "/":
                if r == 0:
                    raise VelarisError("E403", "division by zero", node.line,
                                      fixes=["check the divisor before dividing"])
                if isinstance(l, float):
                    return l / r
                return l // r
            if node.op == "%":
                if r == 0:
                    raise VelarisError("E403", "remainder by zero", node.line,
                                      fixes=["check the divisor before using %"])
                return l % r
            if node.op == "==":
                return l == r
            if node.op == "!=":
                return l != r
            if node.op == "<":
                return l < r
            if node.op == ">":
                return l > r
            if node.op == "<=":
                return l <= r
            return l >= r

    return {"table": table, "call": call, "run": run, "eval": eval_}


def interpret(funcs: list[Function], native: dict | None = None) -> None:
    rt = build_runtime(funcs, native)
    if "main" not in rt["table"]:
        raise VelarisError("E400", "no 'main' function found", 1,
                          fixes=["add: fn main() uses io { ... }"])
    rt["call"]("main", [], rt["table"]["main"].line)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def lsp_analyze(path: str, text: str, deep: bool) -> list:
    """Run the checkers on an editor buffer; return VelarisErrors."""
    errors: list = []
    try:
        funcs, records = load_program(path, entry_source=text)
    except VelarisError as e:
        return [e]
    check_effects(funcs, errors)
    check_types(funcs, records, errors)
    if deep and not errors:
        check_proofs(funcs, records, errors)
    return errors


def lsp_serve() -> int:
    import urllib.parse

    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    docs: dict[str, str] = {}          # uri -> latest text
    published: set = set()             # uris we have diagnostics on

    def read_message():
        length = None
        while True:
            line = stdin.readline()
            if not line:
                return None
            line = line.strip()
            if not line:
                break
            key, _, val = line.partition(b":")
            if key.lower() == b"content-length":
                length = int(val)
        if length is None:
            return None
        return json.loads(stdin.read(length))

    def send(payload: dict):
        body = json.dumps(payload).encode("utf-8")
        stdout.write(f"Content-Length: {len(body)}\r\n\r\n".encode())
        stdout.write(body)
        stdout.flush()

    def uri_to_path(uri: str) -> str:
        p = urllib.parse.unquote(uri[len("file://"):])
        if len(p) > 2 and p[0] == "/" and p[2] == ":":
            p = p[1:]                   # windows: /C:/... -> C:/...
        return p

    def path_to_uri(p: str) -> str:
        p = os.path.abspath(p).replace("\\", "/")
        if not p.startswith("/"):
            p = "/" + p
        return "file://" + urllib.parse.quote(p)

    def diag_of(e: VelarisError) -> dict:
        msg = f"[{e.code}] {e.message}"
        if e.fixes:
            msg += "".join(f"\nfix: {f}" for f in e.fixes)
        line = max(e.line - 1, 0)
        return {"range": {"start": {"line": line, "character": 0},
                          "end": {"line": line, "character": 500}},
                "severity": 1, "source": "velaris", "message": msg}

    def publish(uri: str, deep: bool):
        path = uri_to_path(uri)
        errors = lsp_analyze(path, docs.get(uri, ""), deep)
        by_file: dict[str, list] = {uri: []}
        for e in errors:
            target = uri if e.file in (None, path) else path_to_uri(e.file)
            by_file.setdefault(target, []).append(diag_of(e))
        for target, ds in by_file.items():
            send({"jsonrpc": "2.0",
                  "method": "textDocument/publishDiagnostics",
                  "params": {"uri": target, "diagnostics": ds}})
            published.add(target)
        for old in list(published):
            if old not in by_file:
                send({"jsonrpc": "2.0",
                      "method": "textDocument/publishDiagnostics",
                      "params": {"uri": old, "diagnostics": []}})
                published.discard(old)

    while True:
        msg = read_message()
        if msg is None:
            return 0
        method = msg.get("method", "")
        params = msg.get("params", {})
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": msg["id"], "result": {
                "capabilities": {"textDocumentSync": {
                    "openClose": True, "change": 1,
                    "save": {"includeText": True}}},
                "serverInfo": {"name": "velaris", "version": VERSION}}})
        elif method == "shutdown":
            send({"jsonrpc": "2.0", "id": msg["id"], "result": None})
        elif method == "exit":
            return 0
        elif method == "textDocument/didOpen":
            uri = params["textDocument"]["uri"]
            docs[uri] = params["textDocument"]["text"]
            publish(uri, deep=True)
        elif method == "textDocument/didChange":
            uri = params["textDocument"]["uri"]
            docs[uri] = params["contentChanges"][0]["text"]
            publish(uri, deep=False)
        elif method == "textDocument/didSave":
            uri = params["textDocument"]["uri"]
            if "text" in params:
                docs[uri] = params["text"]
            publish(uri, deep=True)
        elif method == "textDocument/didClose":
            uri = params["textDocument"]["uri"]
            docs.pop(uri, None)
            send({"jsonrpc": "2.0",
                  "method": "textDocument/publishDiagnostics",
                  "params": {"uri": uri, "diagnostics": []}})
        elif "id" in msg:               # any other request: empty result
            send({"jsonrpc": "2.0", "id": msg["id"], "result": None})


UNARY_BEFORE = {"(", "[", "{", ",", ":", "=", "==", "!=", "<", ">",
                "<=", ">=", "+", "-", "*", "/", "%"}
UNARY_KEYWORDS = {"return", "fail", "and", "or", "not", "requires",
                  "ensures", "invariant", "while", "if"}


def format_source(source: str) -> str:
    toks = lex(source, keep_trivia=True)
    lines, cur = [], []
    for t in toks:
        if t.kind == "NEWLINE":
            lines.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        lines.append(cur)

    def render(line_toks) -> str:
        out = ""
        prev = None
        unary = False
        for t in line_toks:
            if t.kind == "COMMENT":
                body = t.text[2:].strip()
                comment = "// " + body if body else "//"
                out = (out.rstrip() + "  " + comment) if out.strip() \
                    else comment
                prev = t
                continue
            if prev is None or unary:
                space = False
            elif t.text in (")", "]", ",", ".", ":"):
                space = False
            elif prev.text in ("(", "[", "."):
                space = False
            elif t.text == "(" and prev.kind == "IDENT":
                space = False
            else:
                space = True          # includes symmetric { x } spacing
            unary = (t.text == "-" and (
                prev is None or prev.text in UNARY_BEFORE
                or prev.kind == "ARROW"
                or (prev.kind == "KEYWORD" and prev.text in UNARY_KEYWORDS)))
            out += (" " if space else "") + t.text
            prev = t
        return out

    depth = 0
    out_lines: list[str] = []
    blank = False
    for line_toks in lines:
        if not line_toks:
            if out_lines and not blank:
                out_lines.append("")
            blank = True
            continue
        blank = False
        lead = 0
        while lead < len(line_toks) and line_toks[lead].text == "}":
            lead += 1
        d = max(depth - lead, 0)
        text = render(line_toks)
        out_lines.append("    " * d + text if text else "")
        for t in line_toks:
            if t.text == "{":
                depth += 1
            elif t.text == "}":
                depth = max(depth - 1, 0)
    while out_lines and out_lines[-1] == "":
        out_lines.pop()
    return "\n".join(out_lines) + "\n"


def fmt_main(argv: list[str]) -> int:
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print("usage: velaris fmt <file.vel> [--stdout | --check]",
              file=sys.stderr)
        return 1
    status = 0
    for path in files:
        try:
            source = open(path, encoding="utf-8").read()
            formatted = format_source(source)
        except (OSError, VelarisError) as e:
            msg = e.human(path) if isinstance(e, VelarisError) else str(e)
            print(msg, file=sys.stderr)
            status = 1
            continue
        if "--stdout" in argv:
            print(formatted, end="")
        elif "--check" in argv:
            if formatted != source:
                print(f"{path}: needs formatting")
                status = 1
            else:
                print(f"{path}: ok")
        elif formatted != source:
            open(path, "w", encoding="utf-8").write(formatted)
            print(f"formatted {path}")
        else:
            print(f"{path}: already formatted")
    return status


STARTER = """// Welcome to Velaris - the language where you can trust code you
// didn't write. Run me with:   velaris main.vel

import "std.vel"

fn discount(price: Int) -> Int
    requires price >= 0
    ensures result >= 0
{
    if price < 10 {
        return 0
    }
    return price - 10
}

fn main() uses io {
    print("hello from Velaris!")
    print("discount(50) = " + discount(50))
    print("sorted: " + sort([5, 3, 8, 1]))
    check to_int(ask("type a number:")) {
        ok n {
            print("double that is " + (n * 2))
        }
        fail why {
            print("that was not a number - " + why)
        }
    }
}
"""


def doctor() -> int:
    OK, OPT, BAD = "[ ok ]", "[ -- ]", "[FAIL]"
    lines, healthy = [], True
    pv = sys.version_info
    if (pv.major, pv.minor) >= (3, 10):
        lines.append(f"{OK} python {pv.major}.{pv.minor}.{pv.micro}")
    else:
        healthy = False
        lines.append(f"{BAD} python {pv.major}.{pv.minor} - Velaris "
                     f"needs 3.10+ (install from python.org)")
    here = os.path.abspath(__file__)
    lines.append(f"{OK} velaris {VERSION}  ({here})")
    try:
        import z3  # noqa: F401
        lines.append(f"{OK} z3-solver - promises are PROVEN before "
                     f"running")
    except ImportError:
        lines.append(f"{OPT} z3-solver absent - promises checked at "
                     f"runtime instead   fix: pip install z3-solver")
    try:
        import llvmlite  # noqa: F401
        lines.append(f"{OK} llvmlite - pure numeric functions run as "
                     f"machine code")
    except ImportError:
        lines.append(f"{OPT} llvmlite absent - everything runs "
                     f"interpreted   fix: pip install llvmlite")
    std = os.path.join(os.path.dirname(here), "stdlib", "std.vel")
    if os.path.exists(std):
        try:
            fs, _ = load_program(std)
            lines.append(f"{OK} standard library - {len(fs)} functions "
                         f"ready to import")
        except VelarisError:
            healthy = False
            lines.append(f"{BAD} standard library present but broken - "
                         f"reinstall: pip install --force-reinstall "
                         f"velaris-lang")
    else:
        healthy = False
        lines.append(f"{BAD} standard library missing - reinstall: "
                     f"pip install --force-reinstall velaris-lang")
    try:
        toks = lex('fn main() uses io { print(2 + 2) }')
        fs2, rs2, _ = Parser(toks).parse_program()
        errs: list = []
        check_effects(fs2, errs)
        check_types(fs2, rs2, errs)
        if errs:
            raise VelarisError("E999", "self-test failed", 1)
        lines.append(f"{OK} compiler self-test - lex, parse, effects, "
                     f"types all answering")
    except Exception:
        healthy = False
        lines.append(f"{BAD} compiler self-test failed - please report "
                     f"this at github.com/gowrishankar-infra/"
                     f"velaris-lang/issues")
    print(f"velaris doctor - {VERSION}")
    print("-" * 60)
    for ln in lines:
        print(ln)
    print("-" * 60)
    if healthy:
        print("all essential checks passed. "
              "[ -- ] items are optional extras.")
        return 0
    print("something needs fixing - see [FAIL] lines above.")
    return 1


def new_project(name: str) -> int:
    if not name or name.startswith("-"):
        print("usage: velaris new <project-name>", file=sys.stderr)
        return 1
    if os.path.exists(name):
        print(f"'{name}' already exists - pick a fresh name",
              file=sys.stderr)
        return 1
    os.makedirs(name)
    with open(os.path.join(name, "main.vel"), "w",
              encoding="utf-8") as f:
        f.write(STARTER)
    with open(os.path.join(name, "README.md"), "w",
              encoding="utf-8") as f:
        f.write(f"# {name}\n\nA Velaris project.\n\n"
                f"```\ncd {name}\nvelaris main.vel\n```\n\n"
                f"Docs: https://github.com/gowrishankar-infra/"
                f"velaris-lang\n")
    print(f"created {name}/")
    print(f"  {name}/main.vel    - a working program with a proven "
          f"contract")
    print(f"  {name}/README.md")
    print(f"next:  cd {name}  then  velaris main.vel")
    return 0


def repl() -> int:
    print(f"Velaris {VERSION} - interactive session.")
    print("Definitions (fn / record / import) are fully checked before "
          "joining;\nloose lines are checked while running. "
          "Type exit to leave.")
    sess_funcs: list[Function] = []
    sess_recs: list = []
    env: dict = {}
    rt = build_runtime(sess_funcs)

    while True:
        try:
            line = input("velaris> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line.strip() in ("exit", "quit", ":q"):
            return 0
        if not line.strip():
            continue
        depth = line.count("{") - line.count("}")
        while depth > 0:
            try:
                more = input("   ...  ")
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            line += "\n" + more
            depth += more.count("{") - more.count("}")
        try:
            toks = lex(line)
        except VelarisError as e:
            print(e.human("<repl>"))
            continue
        kind = toks[0].text if toks and toks[0].kind == "KEYWORD" else ""
        try:
            if kind in ("fn", "record", "import"):
                fs, rs, imps = Parser(toks).parse_program()
                for ipath, _ in imps:
                    if not os.path.exists(ipath):
                        shipped = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            "stdlib", os.path.basename(ipath))
                        if os.path.exists(shipped):
                            ipath = shipped
                    ifuncs, irecs = load_program(ipath)
                    fs += ifuncs
                    rs += irecs
                cand_f = {f.name: f for f in sess_funcs}
                cand_r = {r.name: r for r in sess_recs}
                for f in fs:
                    if f.name in cand_f:
                        print(f"(replacing fn {f.name})")
                    cand_f[f.name] = f
                for r in rs:
                    if r.name in cand_r:
                        print(f"(replacing record {r.name})")
                    cand_r[r.name] = r
                new_f, new_r = list(cand_f.values()), list(cand_r.values())
                errs: list = []
                check_effects(new_f, errs)
                check_types(new_f, new_r, errs)
                if not errs:
                    check_proofs(new_f, new_r, errs)
                if errs:
                    for e in errs:
                        print(e.human("<repl>"))
                    print("(not accepted)")
                    continue
                sess_funcs[:] = new_f
                sess_recs[:] = new_r
                rt = build_runtime(list(sess_funcs))
                names = [f.name for f in fs] + [r.name for r in rs]
                print("defined: " + ", ".join(names))
            else:
                p = Parser(toks)
                stmts = []
                while p.peek().kind != "EOF":
                    stmts.append(p.parse_statement())
                for s in stmts:
                    if isinstance(s, ExprStmt):
                        v = rt["eval"](s.expr, env)
                        if v is not None:
                            print(to_text(v))
                    else:
                        rt["run"](s, env)
        except FailSignal as f:
            print("failed: " + to_text(f.reason))
        except ReturnSignal:
            print("('return' only works inside a function)")
        except VelarisError as e:
            print(e.human("<repl>"))
        except RecursionError:
            print("(too much recursion)")


def main() -> int:
    argv = sys.argv[1:]
    if argv[:1] == ["repl"]:
        return repl()
    if argv[:1] == ["version"]:
        print(f"Velaris {VERSION}")
        return 0
    if argv[:1] == ["fmt"]:
        return fmt_main(argv[1:])
    if argv[:1] == ["lsp"]:
        return lsp_serve()
    if argv[:1] == ["doctor"]:
        return doctor()
    if argv[:1] == ["new"]:
        return new_project(argv[1] if len(argv) > 1 else "")
    if argv[:1] == ["run"]:
        sys.argv.pop(1)
    if "--version" in sys.argv:
        print(f"Velaris {VERSION}")
        return 0
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    filename = sys.argv[1]
    as_json = "--json" in sys.argv
    try:
        funcs, records = load_program(filename)
        errors: list[VelarisError] = []
        check_effects(funcs, errors)  # superpower 1: no hidden effects
        check_types(funcs, records, errors)  # superpower 2: no type surprises
        if not errors:                # proofs assume well-formed code
            check_proofs(funcs, records, errors)  # promises proven early
        if errors:
            errors.sort(key=lambda e: (e.file or filename, e.line))
            if as_json:
                print(json.dumps(
                    [json.loads(e.machine(filename)) for e in errors],
                    indent=2), file=sys.stderr)
            else:
                print("\n\n".join(e.human(filename) for e in errors),
                      file=sys.stderr)
                if len(errors) > 1:
                    print(f"\nfound {len(errors)} problems", file=sys.stderr)
            return 1
        native = {} if "--no-native" in sys.argv else compile_native(funcs)
        import time as _t
        t0 = _t.perf_counter()
        interpret(funcs, native)
        if "--time" in sys.argv:
            ms = (_t.perf_counter() - t0) * 1000
            mode = "interpreted" if not native else "native+interpreted"
            print(f"[--time] ran in {ms:.1f} ms ({mode})", file=sys.stderr)
        return 0
    except VelarisError as e:
        print(e.machine(filename) if as_json else e.human(filename), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
