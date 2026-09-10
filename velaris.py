#!/usr/bin/env python3
"""
Velaris v2.36 — "The language where you can trust code you didn't write."

New in v2.36: examples/linkcheck.vel - a tool worth running, not a
    demonstration - and network failures that say what happened
    instead of quoting the implementation.

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
  velaris <file> --allow io                refuse every other effect
  velaris <file> --deny net,ffi            allow everything but these
  velaris fmt program.vel                  format to the canonical style
  velaris check program.vel                compile only, do not run
  velaris check f.vel --strict             refuse any promise left to runtime
  velaris proofs [path] [--min 80]         how much is proven, not just checked
  velaris proofs . --detail                which functions, one by one
  velaris clean                            forget remembered proofs
  velaris test program.vel                 run every test_ function
  velaris trace program.vel                show every call as it happens
  velaris explain program.vel              walk through what it does
  velaris audit program.vel                what it can touch, before you run it
  velaris card                             the language, for pasting into a model
  velaris mcp-install                      set up the tools in your assistant
  velaris serve [--port 8787]              an HTTP door for any language
  velaris explain <folder>                 a map of every file
  velaris doctor                           check the installation
  velaris new <name>                       start a fresh project
  velaris build program.vel [-o name]      one file anyone can run
  velaris add <url or path> [as name]      vendor a library into lib/
  velaris deps                             what this project depends on
  velaris verify                           are the libraries unchanged?
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

VERSION = "2.60.0"
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
class Closure:
    """A function value that may carry values from around it.

    The function itself was lifted to the top level; this node is what
    the surrounding code evaluates to, and it is where the captured
    values are read - once, at the moment the value is made.
    """
    name: str
    free: list
    line: int


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
class Block:    stmts: list; line: int      # a 'for' unrolled into while
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
    is_lambda: bool = False
    captures: list = field(default_factory=list)   # [(name, type)]


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
    lambda_n = 0

    def __init__(self, tokens: list[Token]):
        self.lifted: list = []
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
        funcs, records, imports = self.lifted, [], []
        while self.peek().kind != "EOF":
            t = self.peek()
            if t.kind == "KEYWORD" and t.text == "import":
                self.next()
                s = self.expect("STRING")
                alias = None
                if self.peek().kind == "IDENT" and self.peek().text == "as":
                    self.next()
                    alias = self.expect("IDENT").text
                imports.append(
                    (unescape(s.text[1:-1], s.line), t.line, alias))
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

    def parse_lambda(self, start: Token):
        """fn(x: Int) -> Bool { return x > 0 } as a value.

        Lifted to a real top-level function with a generated name, so
        every later stage (types, effects, proofs, native codegen) sees
        an ordinary function. Lambdas are pure and cannot capture
        variables from around them - pass what you need as a parameter.
        """
        self.expect("OP", "(")
        params = []
        while self.peek().text != ")":
            pname = self.expect("IDENT").text
            self.expect("OP", ":")
            params.append((pname, self.parse_type()))
            if self.peek().text == ",":
                self.next()
        self.expect("OP", ")")
        if self.peek().text != "->":
            raise VelarisError("E100",
                "a function value needs a result type", start.line,
                fixes=["write: fn(x: Int) -> Bool { return x > 0 }"])
        self.next()
        ret = self.parse_type()
        requires_, ensures_ = [], []      # a function value can promise too
        while (self.peek().kind == "KEYWORD"
               and self.peek().text in ("requires", "ensures")):
            kw = self.next()
            clause = (self.parse_expr(), kw.line)
            (requires_ if kw.text == "requires" else ensures_).append(clause)
        body = self.parse_block()
        Parser.lambda_n += 1
        name = f"fn#{Parser.lambda_n}"
        f = Function(name, params, ret, set(), requires_, ensures_,
                     body, start.line)
        f.can_fail = False
        f.type_vars = []
        f.is_lambda = True
        # names the body reads that it did not bind itself: candidates
        # for capture. Which are really locals is known only once the
        # surrounding function is type checked, so decide there.
        bound = {p for p, _ in params}
        free = []

        def look(node):
            if isinstance(node, Let) or isinstance(node, Assign):
                bound.add(node.name)
            if isinstance(node, Var) and node.name not in bound \
                    and node.name not in free:
                free.append(node.name)
            if isinstance(node, Check):
                bound.add(node.ok_name)
                bound.add(node.fail_name)

        import dataclasses as _dc

        def visit(n):
            if isinstance(n, (list, tuple)):
                for x in n:
                    visit(x)
                return
            if not _dc.is_dataclass(n):
                return
            look(n)
            for fl in _dc.fields(n):
                visit(getattr(n, fl.name))

        visit(body)
        f.free_names = free
        self.lifted.append(f)
        return Closure(name, free, start.line)

    @staticmethod
    def flatten(stmts: list) -> list:
        out = []
        for s in stmts:
            if isinstance(s, Block):
                out.extend(Parser.flatten(s.stmts))
            else:
                out.append(s)
        return out

    def parse_block(self) -> list:
        self.expect("OP", "{")
        stmts = []
        while self.peek().text != "}":
            stmts.append(self.parse_statement())
        self.expect("OP", "}")
        return Parser.flatten(stmts)

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
        if t.kind == "KEYWORD" and t.text == "for":
            self.next()
            name = self.expect("IDENT").text
            inw = self.expect("IDENT")
            if inw.text != "in":
                raise VelarisError("E100", "expected 'in' after the name",
                    inw.line, fixes=["write: for i in 0 to n { ... }",
                                     "or:    for item in xs { ... }"])
            start = self.parse_expr()
            if (self.peek().kind == "IDENT" and self.peek().text == "to"):
                self.next()                       # for i in a to b
                stop = self.parse_expr()
                invs = []
                while (self.peek().kind == "KEYWORD"
                       and self.peek().text == "invariant"):
                    kw = self.next()
                    invs.append((self.parse_expr(), kw.line))
                body = self.parse_block()
                step = Assign(name, BinOp("+", Var(name, t.line),
                                          Num(1), t.line), t.line)
                return Block([
                    Let(name, start, t.line, None),
                    While(BinOp("<", Var(name, t.line), stop, t.line),
                          list(body) + [step], t.line, invs),
                ], t.line)
            Parser.lambda_n += 1                  # for item in xs
            idx = f"for#{Parser.lambda_n}"
            invs = []
            while (self.peek().kind == "KEYWORD"
                   and self.peek().text == "invariant"):
                kw = self.next()
                invs.append((self.parse_expr(), kw.line))
            body = self.parse_block()
            step = Assign(idx, BinOp("+", Var(idx, t.line), Num(1),
                                     t.line), t.line)
            inner = [Let(name, Call("get", [start, Var(idx, t.line)],
                                    t.line), t.line, None)]
            return Block([
                Let(idx, Num(0), t.line, None),
                While(BinOp("<", Var(idx, t.line),
                            Call("length", [start], t.line), t.line),
                      inner + list(body) + [step], t.line, invs),
            ], t.line)
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
            return "List of " + self.parse_type()   # nesting allowed
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
        if t.kind == "KEYWORD" and t.text == "fn":
            return self.parse_lambda(t)
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
            if (self.peek().text == "." and
                    self.toks[self.i + 1].kind == "IDENT" and
                    self.toks[self.i + 2].text == "("):
                self.next()                        # '.'
                fname = self.next().text           # function in namespace
                self.next()                        # '('
                qargs = []
                while self.peek().text != ")":
                    qargs.append(self.parse_expr())
                    if self.peek().text == ",":
                        self.next()
                self.expect("OP", ")")
                return Call(f"{t.text}.{fname}", qargs, t.line)
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


def nice_name(name: str) -> str:
    """Lifted lambdas get generated names; show something readable."""
    if name.startswith("fn#"):
        return "this function value"
    return f"'{name}'"


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
    if isinstance(e, BinOp):
        # keep the meaning: parenthesise operands that bind less tightly,
        # so (result + 1) * count never prints as result + 1 * count
        prec = {"or": 1, "and": 2,
                "==": 3, "!=": 3, "<": 3, ">": 3, "<=": 3, ">=": 3,
                "+": 4, "-": 4, "*": 5, "/": 5, "%": 5}
        here = prec.get(e.op, 6)

        def side(sub, is_right: bool) -> str:
            text = expr_str(sub)
            if isinstance(sub, BinOp):
                there = prec.get(sub.op, 6)
                if there < here or (there == here and is_right):
                    return f"({text})"
            return text
        return f"{side(e.left, False)} {e.op} {side(e.right, True)}"
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

def qualify(fs: list, alias: str) -> None:
    """Rename a library's functions to alias.name, in place.

    References the library makes to its own functions are renamed too,
    so a namespaced import behaves exactly like the flat one from the
    inside - only the importer sees the prefix.
    """
    import dataclasses
    local = {f.name for f in fs}
    new_name = {n: f"{alias}.{n}" for n in local}

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
            return
        if isinstance(node, tuple):
            for x in node:
                walk(x)
            return
        if not dataclasses.is_dataclass(node):
            return
        if isinstance(node, (Call, Var)) and node.name in new_name:
            node.name = new_name[node.name]
        for fld in dataclasses.fields(node):
            if fld.name == "name":
                continue
            walk(getattr(node, fld.name))

    for f in fs:
        walk(f.body)
        walk([e for e, _ in f.requires])
        walk([e for e, _ in f.ensures])
    for f in fs:
        f.name = new_name[f.name]


def unknown_function(name: str, line: int, known) -> VelarisError:
    """One clear message for an unknown name, namespace-aware."""
    if "." in name:
        ns, _, fname = name.partition(".")
        spaces = sorted({n.split(".")[0] for n in known if "." in n})
        if ns in spaces:
            near = sorted(n.split(".", 1)[1] for n in known
                          if n.startswith(ns + "."))
            return VelarisError("E200",
                f"'{ns}' has no function called '{fname}'", line,
                fixes=[f"available in '{ns}': {', '.join(near[:8])}"
                       + (" ..." if len(near) > 8 else ""),
                       "check the spelling of the name"])
        return VelarisError("E200", f"no import is named '{ns}'", line,
            fixes=[f'name an import: import "lib.vel" as {ns}',
                   (f"names in scope: {', '.join(spaces)}" if spaces
                    else "an import only gets a name if you write 'as'")])
    return VelarisError("E200", f"unknown function '{name}'", line,
                        fixes=[f"define 'fn {name}(...)' somewhere",
                               "check the spelling of the name"])


def load_program(entry: str, entry_source: str | None = None):
    funcs, records = [], []
    fn_src, rec_src = {}, {}
    visited = set()

    def load(path: str, importer: str | None, iline: int = 1,
             alias: str | None = None):
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
                    return load(shipped, importer, iline, alias)
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
        for ipath, iline, ialias in imports:   # ialias: don't shadow alias
            load(os.path.join(base, ipath) if base else ipath, path, iline,
                 ialias)
        if alias:
            qualify(fs, alias)
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

FALLIBLE_BUILTINS = {"to_int", "read_file", "fetch", "post",
                     "pop", "slice", "set_at",
                     "add_or_fail", "sub_or_fail", "mul_or_fail",
                     "div_or_fail", "mod_or_fail",
                     "fetch_status", "request", "py", "py_int", "py_float",
                     "py_json", "json_get", "json_int", "json_float",
                     "json_len", "py_new", "py_do", "py_field"}   # + get on maps

PROGRAM_ARGS: list = []    # filled by the CLI: velaris prog.vel a b c

ALL_EFFECTS = ("io", "fs", "net", "clock", "rand", "ffi")
EFFECT_BUDGET: set = set(ALL_EFFECTS)   # everything, unless you say less
FFI_MODULES: set | None = None          # None = any module; a set = only
                                        # these top-level packages


def parse_budget(spec: str) -> tuple:
    """'io,fs,ffi:math,json' -> ({'io','fs','ffi'}, {'math','json'})

    Plain 'ffi' grants every module. 'ffi:a,b' grants the ffi effect for
    those top-level packages only - the one caveat every security review
    of this project raised, made into a precise permission.
    """
    effects: set = set()
    modules: set | None = None
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if item.startswith("ffi:"):
            effects.add("ffi")
            modules = set() if modules is None else modules
            modules.add(item[len("ffi:"):].strip().split(".")[0])
        elif modules is not None and "ffi" in effects and \
                item not in ALL_EFFECTS:
            modules.add(item.split(".")[0])   # continuation of ffi:a,b
        else:
            effects.add(item)
    return effects, modules


def allow_module(module: str, what: str, line: int) -> None:
    """Refuse a Python module this run did not grant."""
    if FFI_MODULES is None:
        return
    top = module.split(".")[0]
    if top in FFI_MODULES:
        return
    raise VelarisError("E311",
        f"'{what}' reaches into Python module '{module}', which this run "
        f"does not allow", line,
        fixes=[f"allow it: --allow ffi:{top}"
               + ("," + ",".join(sorted(FFI_MODULES)) if FFI_MODULES
                  else ""),
               "or use a program that does not need it"])


def spend(effect: str, what: str, line: int) -> None:
    """Refuse an effect the person running this did not allow.

    The compiler checks that a function declares what it does. This is
    the other half: the runtime refuses anything outside the budget
    given on the command line, whatever the source says about itself -
    so you can run a program you have not read.
    """
    if effect in EFFECT_BUDGET:
        return
    raise VelarisError("E310",
        f"'{what}' needs the '{effect}' effect, which this run does not "
        f"allow", line,
        fixes=[f"allow it: velaris <file> --allow {effect}",
               "or use a program that does not need it"])

INT_MIN, INT_MAX = -(2 ** 63), 2 ** 63 - 1

TRACE = {"on": False, "depth": 0, "calls": 0, "limit": 4000}


def trace_enter(name: str, params, args) -> None:
    if not TRACE["on"] or TRACE["calls"] >= TRACE["limit"]:
        return
    TRACE["calls"] += 1
    shown = ", ".join(f"{p}={to_text(a)}" for (p, _), a in
                      zip(params, args))
    print("  " * TRACE["depth"] + f"-> {name}({shown})", file=sys.stderr)
    TRACE["depth"] += 1


def trace_leave(name: str, value, failed: str | None = None) -> None:
    if not TRACE["on"] or TRACE["calls"] > TRACE["limit"]:
        return
    TRACE["depth"] = max(0, TRACE["depth"] - 1)
    if failed is not None:
        print("  " * TRACE["depth"] + f"<- {name} FAILED: {failed}",
              file=sys.stderr)
    elif value is None:
        print("  " * TRACE["depth"] + f"<- {name}", file=sys.stderr)
    else:
        print("  " * TRACE["depth"] + f"<- {name} = {to_text(value)}",
              file=sys.stderr)


def checked_int(value: int, op: str, line: int) -> int:
    """Whole numbers are 64-bit. Outgrowing that is an error, because
    the alternative is native code wrapping while the interpreter keeps
    counting - two engines, two answers, and no way to know which."""
    if isinstance(value, int) and not INT_MIN <= value <= INT_MAX:
        raise VelarisError("E407",
            f"this '{op}' made a number too big to hold "
            f"(whole numbers go from {INT_MIN} to {INT_MAX})", line,
            fixes=["keep the numbers smaller",
                   "or work in smaller units, like cents instead of "
                   "rupees"])
    return value

def _z3_installed() -> bool:
    """Is the prover available, without paying ~350ms to import it?

    importlib.util.find_spec only locates the package; z3 itself is
    imported when a proof actually starts. Programs with no contracts
    - and every run of a cached-proof program - never pay for it.
    """
    try:
        import importlib.util
        return importlib.util.find_spec("z3") is not None
    except Exception:
        return False


HAVE_Z3 = _z3_installed()

BUILTINS = {
    # name          effects needed      argument types        returns
    "log":        {"effects": {"io"},     "types": ["Any"],         "ret": "Unit"},
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
    "code_at":    {"effects": set(),      "types": ["Text", "Int"], "ret": "Int"},
    "py":         {"effects": {"ffi"},    "types": ["Text", "Text", "List of Text"], "ret": "Text"},
    "py_int":     {"effects": {"ffi"},    "types": ["Text", "Text", "List of Text"], "ret": "Int"},
    "py_float":   {"effects": {"ffi"},    "types": ["Text", "Text", "List of Text"], "ret": "Float"},
    "py_json":    {"effects": {"ffi"},    "types": ["Text", "Text", "Text"], "ret": "Text"},
    "py_new":     {"effects": {"ffi"},    "types": ["Text", "Text", "Text"], "ret": "Handle"},
    "py_do":      {"effects": {"ffi"},    "types": ["Handle", "Text", "Text"], "ret": "Text"},
    "py_field":   {"effects": {"ffi"},    "types": ["Handle", "Text"], "ret": "Text"},
    "py_close":   {"effects": {"ffi"},    "types": ["Handle"],       "ret": "Unit"},
    "json_get":   {"effects": set(),      "types": ["Text", "Text"], "ret": "Text"},
    "json_int":   {"effects": set(),      "types": ["Text", "Text"], "ret": "Int"},
    "json_float": {"effects": set(),      "types": ["Text", "Text"], "ret": "Float"},
    "json_len":   {"effects": set(),      "types": ["Text", "Text"], "ret": "Int"},
    "json_has":   {"effects": set(),      "types": ["Text", "Text"], "ret": "Bool"},
    "json_of":    {"effects": set(),      "types": ["Any"],          "ret": "Text"},
    "args":       {"effects": {"io"},     "types": [],              "ret": "List of Text"},
    "env":        {"effects": {"io"},     "types": ["Text", "Text"], "ret": "Text"},
    "exit_with":  {"effects": {"io"},     "types": ["Int"],         "ret": "Unit"},
    "read_line":  {"effects": {"io"},     "types": [],              "ret": "Text"},
    "post":       {"effects": {"net"},    "types": ["Text", "Text"], "ret": "Text"},
    "fetch_status": {"effects": {"net"},  "types": ["Text"],        "ret": "Int"},
    "request":    {"effects": {"net"},    "types": ["Text", "Text", "Text", "Text"], "ret": "Text"},
    "format":     {"effects": set(),      "types": ["Any"],         "ret": "Text"},
    "has":        {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "keys":       {"effects": set(),      "types": ["Any"],         "ret": "Any"},
    "all_of":     {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "any_of":     {"effects": set(),      "types": ["Any", "Any"],  "ret": "Bool"},
    "lower":      {"effects": set(),      "types": ["Text"],        "ret": "Text"},
    "length":     {"effects": set(),      "types": ["Any"],         "ret": "Int"},
    "push":       {"effects": set(),      "types": ["Any", "Any"],  "ret": "Any"},
    "pop":        {"effects": set(),      "types": ["Any"],         "ret": "Any"},
    "slice":      {"effects": set(),      "types": ["Any", "Int", "Int"], "ret": "Any"},
    "set_at":     {"effects": set(),      "types": ["Any", "Int", "Any"], "ret": "Any"},
    "add_or_fail": {"effects": set(),     "types": ["Int", "Int"],  "ret": "Int"},
    "div_or_fail": {"effects": set(),     "types": ["Int", "Int"],  "ret": "Int"},
    "mod_or_fail": {"effects": set(),     "types": ["Int", "Int"],  "ret": "Int"},
    "sub_or_fail": {"effects": set(),     "types": ["Int", "Int"],  "ret": "Int"},
    "mul_or_fail": {"effects": set(),     "types": ["Int", "Int"],  "ret": "Int"},
    "get":        {"effects": set(),      "types": ["Any", "Any"],  "ret": "Any"},
}

KNOWN_TYPES = {"Int", "Text", "Bool", "Float", "Handle"}

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
        raise unknown_function(name, line, table)

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

def check_main(funcs: list, errors: list, *, running: bool = True) -> None:
    """main must exist (when running), take nothing, declare no failure.

    `velaris check library.vel` checks a library as a library - a
    missing main is only an error for the file being run."""
    mains = [f for f in funcs if f.name == "main"]
    if not mains:
        if running:
            errors.append(VelarisError("E400",
                "there is no 'main' - a program needs somewhere to start",
                1, fixes=["add one: fn main() uses io { ... }"]))
        return
    m = mains[0]
    if m.params:
        errors.append(VelarisError("E401",
            f"'main' takes no parameters, but this one asks for "
            f"{len(m.params)}", m.line,
            fixes=["read the command line with args() instead"]))
    if getattr(m, "can_fail", False):
        errors.append(VelarisError("E523",
            "'main' cannot fail - there is nobody above it to catch",
            m.line,
            fixes=["handle failures inside main with check",
                   "or exit_with(1) when something goes wrong"]))


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

    def callee_sig(name: str, line: int = 1) -> tuple[list[str], str]:
        if name in BUILTINS:
            return BUILTINS[name]["types"], BUILTINS[name]["ret"]
        if name not in table:
            raise unknown_function(name, line, table)
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

    NAMESPACES = {n.split(".")[0] for n in table if "." in n}

    def no_shadow(name: str, line: int) -> None:
        if name in NAMESPACES:
            raise VelarisError("E514",
                f"'{name}' is the name of an import, so it cannot also be "
                f"a variable", line,
                fixes=[f"rename the variable",
                       f"or give the import another name: as {name}_lib"])

    lambda_of = {f.name: f for f in funcs if getattr(f, "is_lambda", False)}

    def check_fn(fn: Function) -> None:
        for _pname, _ in fn.params:
            no_shadow(_pname, fn.line)
        env = dict(fn.params)                       # variable -> type
        for cname, ctype in getattr(fn, "captures", []):
            env.setdefault(cname, ctype)            # values carried in
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
            if isinstance(node, Closure):
                lam = lambda_of.get(node.name)
                if lam is None:
                    raise VelarisError("E402",
                        f"unknown function value '{node.name}'", node.line)
                # a name is captured when the surrounding code has it as
                # a local; anything else is a global function or builtin
                caught = []
                for n in node.free:
                    if n in env:
                        caught.append((n, env[n]))
                lam.captures = caught
                check_fn(lam)              # check it where its names mean
                                           # something
                return fmt_fn_type([t for _, t in lam.params],
                                   lam.return_type)
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
                if getattr(fn, "is_lambda", False):
                    raise VelarisError("E402",
                        f"a function value cannot use '{node.name}' from "
                        f"the code around it", node.line,
                        fixes=[f"add it as a parameter: "
                               f"fn(x: T, {node.name}: T) -> ...",
                               "or write a named function that takes it"])
                if node.name in ("break", "continue"):
                    raise VelarisError("E402",
                        f"there is no '{node.name}' in this language",
                        node.line,
                        fixes=["use a condition in the loop test instead",
                               "or keep a flag: "
                               "while going and i < n { ... }"])
                raise VelarisError("E402",
                                  f"unknown variable '{node.name}'",
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
                    "get_or", "pop", "slice", "set_at"):
                n_want = {"length": 1, "keys": 1, "push": 2, "get": 2,
                          "has": 2, "put": 3, "get_or": 3, "pop": 1,
                          "slice": 3, "set_at": 3}[node.name]
                if len(node.args) != n_want:
                    raise VelarisError("E401",
                        f"'{node.name}' expects {n_want} argument(s) "
                        f"but got {len(node.args)}", node.line,
                        fixes=[f"pass exactly {n_want} argument(s)"])
                t0 = infer(node.args[0])
                is_map = t0.startswith("Map of ")
                if is_map:
                    key_t, _, val_t = t0[len("Map of "):].partition(" to ")
                if node.name in ("pop", "slice", "set_at"):
                    if not allow_fail:
                        raise VelarisError("E520",
                            f"'{node.name}' can fail - that cannot be "
                            f"ignored", node.line,
                            fixes=[f"handle it: check {node.name}(...) "
                                   f"{{ ok v {{ ... }} fail why "
                                   f"{{ ... }} }}",
                                   f"or pass it up (inside a fallible "
                                   f"function): try {node.name}(...)"])
                    if not t0.startswith("List of "):
                        raise VelarisError("E501",
                            f"'{node.name}' works on a list, not {t0}",
                            node.line,
                            fixes=[f"pass a list to '{node.name}'"])
                    if node.name == "set_at":
                        want = t0[len("List of "):]
                        got = infer(node.args[2])
                        if got != want and want != "Any":
                            raise VelarisError("E501",
                                f"this list holds {want}, so 'set_at' "
                                f"cannot put {got} in it", node.line,
                                fixes=[f"pass a {want}"])
                    for arg in node.args[1:3 if node.name == "slice" else 2]:
                        if node.name != "pop" and infer(arg) != "Int":
                            raise VelarisError("E501",
                                f"'{node.name}' takes whole-number "
                                f"positions", node.line,
                                fixes=["pass an Int"])
                    return t0
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
                ptypes, ret = callee_sig(node.name, node.line)
                if node.name == "format":          # text, then one value
                    if not node.args:              # per {} placeholder
                        raise VelarisError("E401",
                            "'format' needs the text first", node.line,
                            fixes=['write: format("hi {}", name)'])
                    if infer(node.args[0]) != "Text":
                        raise VelarisError("E501",
                            "'format' needs Text as its first argument",
                            node.line, fixes=['write: format("hi {}", name)'])
                    for a in node.args[1:]:
                        infer(a)
                    if isinstance(node.args[0], Str):   # literal: check now
                        holes = node.args[0].value.count("{}")
                        given = len(node.args) - 1
                        if holes != given:
                            raise VelarisError("E406",
                                f"this text has {holes} placeholder(s) "
                                f"but got {given} value(s)", node.line,
                                fixes=[f"pass exactly {holes} value(s)",
                                       "each {} takes one value"])
                    return "Text"
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
                    if l == r and l in ("Int", "Float", "Text"):
                        return "Bool"   # Text compares alphabetically
                    raise VelarisError("E501",
                        f"'{op}' compares two Ints, two Floats, or two "
                        f"Texts, but this is {l} {op} {r}", node.line,
                        fixes=NUM_FIX)
                if l != r:                             # == and !=
                    raise VelarisError("E501",
                        f"cannot compare {l} with {r}", node.line,
                        fixes=["compare values of the same type"])
                return "Bool"

        def check_stmt(node) -> None:
            if isinstance(node, Let):
                no_shadow(node.name, node.line)
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
        if getattr(fn, "is_lambda", False) and getattr(fn, "free_names", []):
            continue      # checked at its creation site, where the names
                          # it carries actually mean something
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

CACHE_DIR = ".velaris"
CACHE_FILE = os.path.join(CACHE_DIR, "proofs.json")


def proof_key(fn: Function, table: dict, records: list) -> str:
    """What this function's proof actually depends on.

    Its own text, and the *contracts* of everything it calls - because
    a modular proof assumes those. Change a callee's promise and this
    function must be proven again, or the cache would be telling you
    something that is no longer true.
    """
    import hashlib

    def contract_of(f: Function) -> str:
        return "|".join([
            f.name, str(f.params), str(f.return_type),
            ",".join(sorted(f.effects)), str(f.can_fail),
            ";".join(expr_str(e) for e, _ in f.requires),
            ";".join(expr_str(e) for e, _ in f.ensures)])

    called: set = set()

    def walk(node):
        import dataclasses as _dc
        if isinstance(node, (list, tuple)):
            for x in node:
                walk(x)
            return
        if not _dc.is_dataclass(node):
            return
        if isinstance(node, Call):
            called.add(node.name)
        for f in _dc.fields(node):
            walk(getattr(node, f.name))
    walk(fn.body)
    walk([e for e, _ in fn.requires])
    walk([e for e, _ in fn.ensures])

    parts = [VERSION, contract_of(fn), stmt_key(fn.body)]
    for name in sorted(called):
        callee = table.get(name)
        if callee is not None:
            parts.append(contract_of(callee))
    for r in records:
        parts.append(f"{r.name}:{r.fields}")
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def stmt_key(stmts) -> str:
    """A stable text for a function body."""
    import dataclasses as _dc

    def show(node) -> str:
        if isinstance(node, (list, tuple)):
            return "[" + ",".join(show(x) for x in node) + "]"
        if not _dc.is_dataclass(node):
            return repr(node)
        inner = ",".join(f"{f.name}={show(getattr(node, f.name))}"
                         for f in _dc.fields(node) if f.name != "line")
        return f"{type(node).__name__}({inner})"
    return show(stmts)


def _cache_load() -> dict:
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _cache_save(data: dict) -> None:
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass                            # a cache that cannot be written
                                        # is a slowdown, never an error


def check_proofs(funcs: list[Function], records: list,
                 errors: list, proven_out: set | None = None,
                 use_cache: bool = False) -> None:
    # Nothing to prove means nothing to import. Loading z3 costs about
    # 350ms, and most programs - every hello world, every script whose
    # functions carry no promises - were paying it for no work at all.
    # Division, list reads and calls into contracted functions still
    # create obligations, so this asks about those too.
    def needs_proving(fn) -> bool:
        if fn.requires or fn.ensures:
            return True
        found = [False]

        def look(node):
            if isinstance(node, BinOp) and node.op in ("/", "%"):
                found[0] = True
            if isinstance(node, While) and node.invariants:
                found[0] = True
            if isinstance(node, Call):
                if node.name in ("get", "pop", "slice", "set_at"):
                    found[0] = True
                callee = table_all.get(node.name)
                if callee is not None and (callee.requires or callee.ensures):
                    found[0] = True

        import dataclasses as _dc

        def visit(node):
            if isinstance(node, (list, tuple)):
                for x in node:
                    visit(x)
                return
            if not _dc.is_dataclass(node):
                return
            look(node)
            for f in _dc.fields(node):
                visit(getattr(node, f.name))

        visit(fn.body)
        return found[0]

    table_all = {f.name: f for f in funcs}
    if not any(needs_proving(f) for f in funcs):
        if proven_out is not None:
            proven_out.clear()
        return

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
        return all(ft in ("Int", "Bool", "Float", "Text",
                          "List of Int")
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

    class GridVal:
        """A symbolic list of lists: rows, row lengths, and how many."""
        def __init__(self, rows, lens, length):
            self.rows, self.lens, self.length = rows, lens, length

    class MapVal:
        """A symbolic map: values, plus which keys are actually there."""
        def __init__(self, vals, present, key_t, val_t):
            self.vals, self.present = vals, present
            self.key_t, self.val_t = key_t, val_t

    MAP_SORTS = {"Int": lambda: z3.IntSort(), "Bool": lambda: z3.BoolSort(),
                 "Text": lambda: z3.StringSort()}
    CODE_AT = z3.Function("code_at", z3.StringSort(), z3.IntSort(),
                          z3.IntSort())
    SPLIT = z3.Function("split", z3.StringSort(), z3.StringSort(),
                        z3.ArraySort(z3.IntSort(), z3.StringSort()))
    SPLIT_N = z3.Function("split_count", z3.StringSort(),
                          z3.StringSort(), z3.IntSort())
    _st, _ss = z3.String("__split_t"), z3.String("__split_s")
    SPLIT_AXIOMS = [z3.ForAll([_st, _ss], SPLIT_N(_st, _ss) >= 1)]
    UPPER = z3.Function("upper", z3.StringSort(), z3.StringSort())
    LOWER = z3.Function("lower", z3.StringSort(), z3.StringSort())
    _t = z3.String("__case_t")
    CASE_AXIOMS = [                     # changing case keeps the length
        z3.ForAll([_t], z3.Length(UPPER(_t)) == z3.Length(_t)),
        z3.ForAll([_t], z3.Length(LOWER(_t)) == z3.Length(_t)),
    ]

    def map_parts(t: str):
        """('Map of Text to Int') -> ('Text', 'Int') if both are modelable."""
        if not t.startswith("Map of "):
            return None
        key, sep, val = t[len("Map of "):].partition(" to ")
        if not sep or key not in MAP_SORTS or val not in MAP_SORTS:
            return None
        return key, val

    def mk_map(name: str, t: str):
        parts = map_parts(t)
        if parts is None:
            return None
        key_t, val_t = parts
        ks, vs = MAP_SORTS[key_t](), MAP_SORTS[val_t]()
        return MapVal(z3.Array(name, ks, vs),
                      z3.Array(name + "__has", ks, z3.BoolSort()),
                      key_t, val_t)

    def mk(name: str, t: str):
        if t == "Int":
            return z3.Int(name)
        if t == "Float":
            saw_fp[0] = True
            return z3.FP(name, z3.Float64())
        if t == "Text":
            return z3.String(name)
        return z3.Bool(name)

    def mk_rec(prefix: str, rname: str) -> "RecVal":
        out = {}
        for f, ft in rec_fields[rname]:
            if ft in ("Int", "Bool", "Float", "Text"):
                out[f] = mk(f"{prefix}.{f}", ft)
            elif ft == "List of Int":
                arr = z3.Array(f"{prefix}.{f}", z3.IntSort(), z3.IntSort())
                out[f] = ListVal(arr, z3.Int(f"{prefix}.{f}__n"))
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
        if isinstance(e, OpaqueList):
            return has_fresh(e.length)
        if isinstance(e, RecListVal):
            return has_fresh(e.length) or any(
                has_fresh(a) for a in e.arrays.values())
        if isinstance(e, RecElem):
            return has_fresh(e.idx) or has_fresh(e.src.length)
        if isinstance(e, MapVal):
            return has_fresh(e.vals) or has_fresh(e.present)
        if isinstance(e, GridVal):
            return (has_fresh(e.rows) or has_fresh(e.lens)
                    or has_fresh(e.length))
        if z3.is_const(e) and e.decl().name().startswith("__"):
            return True
        return any(has_fresh(c) for c in e.children())

    def show_val(name, v, model):
        if isinstance(v, RecVal):
            def field_text(f, x):
                if isinstance(x, RecVal):
                    return show_val(f, x, model).split(" = ", 1)[-1]
                if isinstance(x, ListVal):
                    n = model.eval(x.length, model_completion=True)
                    return f"{f}: a list of {n}"
                if isinstance(x, MapVal):
                    return f"{f}: a map"
                return f"{f}: {model.eval(x, model_completion=True)}"
            inner = ", ".join(field_text(f, x) for f, x in v.fields.items())
            return f"{name} = {v.rname}({inner})"
        if isinstance(v, ListVal):
            return f"length({name}) = {model.eval(v.length, model_completion=True)}"
        if isinstance(v, MapVal):
            return f"{name} = a map"        # keys are symbolic here
        if isinstance(v, GridVal):
            return (f"length({name}) = "
                    f"{model.eval(v.length, model_completion=True)}")
        return f"{name} = {model.eval(v, model_completion=True)}"

    def bind_params(fnB: Function, args_z3: list) -> dict:
        return {pname: a for (pname, _), a in zip(fnB.params, args_z3)}

    def check_requires_at(fnB, args_z3, ctx, line):
        """Prove the caller always satisfies fnB's requires here (E701)."""
        def names_in(e, out=None):
            if out is None:
                out = set()
            if isinstance(e, Var):
                out.add(e.name)
            import dataclasses as _dc
            if _dc.is_dataclass(e):
                for f in _dc.fields(e):
                    v = getattr(e, f.name)
                    if isinstance(v, (list, tuple)):
                        for x in v:
                            names_in(x, out)
                    else:
                        names_in(v, out)
            return out

        def conjuncts(e):
            """a and b and c -> [a, b, c], so one untranslatable part
            does not throw away the checkable ones. A single length()
            over a record list used to mask a divisor > 0 sitting right
            next to it."""
            if isinstance(e, BinOp) and e.op == "and":
                return conjuncts(e.left) + conjuncts(e.right)
            return [e]

        parts = [p for r_expr, _ in fnB.requires
                 for p in conjuncts(r_expr)]
        bound = bind_params(fnB, [a for a in args_z3])
        for r_expr in parts:
            names = names_in(r_expr)
            involved = [a for (pname, _), a in zip(fnB.params, args_z3)
                        if pname in names]
            if any(a is None for a in involved):
                continue        # this conjunct mentions an unknown
            try:
                need = to_z3(r_expr, bound, None)
            except Unprovable:
                continue
            if any(a is not None and has_fresh(a) for a in involved) or \
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
            return t in ("Int", "Bool", "Float", "Text") or (
                map_parts(t) is not None) or (
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
        if isinstance(node, Str):
            return z3.StringVal(node.value)
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
            if isinstance(obj, RecElem):
                arr = obj.src.arrays.get(node.field)
                if arr is None:
                    raise Unprovable()   # a field the model skipped
                return z3.Select(arr, obj.idx)
            if not isinstance(obj, RecVal):
                raise Unprovable()
            got = obj.fields.get(node.field)
            if got is None:
                raise Unprovable()
            return got
        if isinstance(node, ListLit):
            vals = [to_z3(it, env, ctx) for it in node.items]
            if vals and all(z3.is_string(v) for v in vals):
                arr = z3.K(z3.IntSort(), z3.StringVal(""))
            else:
                arr = z3.K(z3.IntSort(), z3.IntVal(0))
            for idx, v in enumerate(vals):
                if not (z3.is_int(v) or z3.is_string(v)):
                    raise Unprovable()      # lists of lists, records, ...
                if v.sort() != arr.sort().range():
                    raise Unprovable()      # a list cannot mix sorts
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
        if isinstance(node, Call) and node.name == "split":
            t = to_z3(node.args[0], env, ctx)
            sep = to_z3(node.args[1], env, ctx)
            if not (z3.is_string(t) and z3.is_string(sep)):
                raise Unprovable()
            return ListVal(SPLIT(t, sep), SPLIT_N(t, sep))
        if isinstance(node, Call) and node.name in ("upper", "lower"):
            t = to_z3(node.args[0], env, ctx)
            if not z3.is_string(t):
                raise Unprovable()
            return (UPPER if node.name == "upper" else LOWER)(t)
        if isinstance(node, Call) and node.name == "split":
            t = to_z3(node.args[0], env, ctx)
            sep = to_z3(node.args[1], env, ctx)
            if not (z3.is_string(t) and z3.is_string(sep)):
                raise Unprovable()
            # the pieces are unknown, but there is always at least one
            return ListVal(SPLIT(t, sep), SPLIT_N(t, sep))
        if isinstance(node, Call) and node.name == "contains":
            hay = to_z3(node.args[0], env, ctx)
            needle = to_z3(node.args[1], env, ctx)
            if z3.is_string(hay) and z3.is_string(needle):
                return z3.Contains(hay, needle)
            raise Unprovable()
        if isinstance(node, Call) and node.name == "code_at":
            t = to_z3(node.args[0], env, ctx)
            i = to_z3(node.args[1], env, ctx)
            if not (z3.is_string(t) and z3.is_int(i)):
                raise Unprovable()
            # the exact character is unknown to the prover, but it IS a
            # value - enough to reason about the code around it
            return CODE_AT(t, i)
        if isinstance(node, Call) and node.name in ("put", "get_or", "has"):
            base = to_z3(node.args[0], env, ctx)
            if isinstance(base, MapVal):
                k = to_z3(node.args[1], env, ctx)
                if node.name == "has":
                    return z3.Select(base.present, k)
                if node.name == "get_or":
                    d = to_z3(node.args[2], env, ctx)
                    return z3.If(z3.Select(base.present, k),
                                 z3.Select(base.vals, k), d)
                v = to_z3(node.args[2], env, ctx)        # put
                return MapVal(z3.Store(base.vals, k, v),
                              z3.Store(base.present, k, z3.BoolVal(True)),
                              base.key_t, base.val_t)
            if node.name != "put":
                raise Unprovable()
        if isinstance(node, MapLit):
            raise Unprovable()          # literal maps: runtime for now
        if isinstance(node, Call) and node.name in ("length", "get",
                                                    "push"):
            g0 = to_z3(node.args[0], env, ctx) if node.args else None
            if isinstance(g0, GridVal):
                if node.name == "length":
                    return g0.length
                if node.name == "get":
                    idx = to_z3(node.args[1], env, ctx)
                    if ctx is not None:
                        prove_bounds(idx, g0.length, ctx, node.line)
                    return ListVal(z3.Select(g0.rows, idx),
                                   z3.Select(g0.lens, idx))
                row = to_z3(node.args[1], env, ctx)      # push
                if not isinstance(row, ListVal):
                    raise Unprovable()
                return GridVal(
                    z3.Store(g0.rows, g0.length, row.arr),
                    z3.Store(g0.lens, g0.length, row.length),
                    g0.length + 1)
        if isinstance(node, Call) and node.name in ("length", "get", "push"):
            a0 = to_z3(node.args[0], env, ctx)
            if isinstance(a0, OpaqueList):
                if node.name == "length":
                    return a0.length
                raise Unprovable()      # contents are invisible
            if isinstance(a0, RecListVal):
                if node.name == "length":
                    return a0.length
                if node.name == "get":
                    a1 = to_z3(node.args[1], env, ctx)
                    if not hasattr(a1, "sort") or not z3.is_int(a1):
                        raise Unprovable()
                    if ctx is not None:
                        prove_bounds(a1, a0.length, ctx, node.line)
                    return RecElem(a0, a1)
                if node.name == "push":
                    a1 = to_z3(node.args[1], env, ctx)
                    if not isinstance(a1, RecVal) \
                            or a1.rname != a0.rname:
                        raise Unprovable()
                    new_arrays = {}
                    for fname, arr in a0.arrays.items():
                        fv = a1.fields.get(fname)
                        if fv is None or not hasattr(fv, "sort") \
                                or not z3.is_int(fv):
                            raise Unprovable()
                        new_arrays[fname] = z3.Store(arr, a0.length, fv)
                    return RecListVal(a0.rname, new_arrays,
                                      a0.length + 1)
            if not isinstance(a0, ListVal):
                if z3.is_string(a0):
                    return z3.Length(a0)        # characters in the text
                raise Unprovable()
            if node.name == "length":
                return a0.length
            a1 = to_z3(node.args[1], env, ctx)
            # lists are modelled as arrays of Ints; anything else (Text,
            # records, nested lists) stays runtime-checked rather than
            # being forced into a sort it does not fit
            if node.name == "push":
                # a record, a nested list or a map has no Z3 sort at all;
                # ask before assuming, or the translator crashes
                if not hasattr(a1, "sort") or \
                        a1.sort() != a0.arr.sort().range():
                    raise Unprovable()
                return ListVal(z3.Store(a0.arr, a0.length, a1),
                               a0.length + 1)
            if not hasattr(a1, "sort") or not z3.is_int(a1):
                raise Unprovable()          # an index is always an Int
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
            if op in ("/", "%") and not (z3.is_fp(l) or z3.is_fp(r)):
                if ctx is not None:        # divide by zero, proven early
                    prove_nonzero(r, ctx, node.line, op)
                # Velaris divides the way Python does: the result floors
                # toward minus infinity. That matches Z3's integer
                # division only when the divisor is POSITIVE, so that is
                # the only case translated - a negative divisor falls
                # back to a runtime check rather than a formula that
                # would quietly disagree with the interpreter.
                if ctx is None or not provably_positive(r, ctx):
                    raise Unprovable()
                return (l / r) if op == "/" else (l % r)
        raise Unprovable()             # Str, ListLit, floats, anything else

    def provably_positive(divisor, ctx) -> bool:
        """True only if the divisor cannot be zero or negative here."""
        if has_fresh(divisor) or any(has_fresh(c) for c in ctx.conds):
            return False
        solver = z3.Solver()
        solver.set("timeout", solver_budget())
        solver.add(*ctx.param_assum)
        solver.add(*ctx.conds)
        solver.add(divisor <= 0)
        return solver.check() == z3.unsat

    def prove_nonzero(divisor, ctx, line, op: str):
        """Prove the divisor is never zero; only report real violations."""
        if has_fresh(divisor):
            return          # the divisor itself is unknown here; the
                            # runtime check still guards it
        # conditions mentioning havoc'd values stay in the solver rather
        # than cancelling the proof: dropping them would invent
        # counterexamples, and keeping them costs nothing. Without this a
        # loop anywhere before the division hid the check entirely -
        # which is the shape of nearly every average.
        solver = z3.Solver()
        solver.set("timeout", solver_budget())
        solver.add(*ctx.param_assum)
        solver.add(*ctx.conds)
        solver.add(divisor == 0)
        if solver.check() == z3.sat:
            m = solver.model()
            names = sorted({d.name() for d in m.decls()
                            if not d.name().startswith("__")})
            shown = ", ".join(
                f"{n} = {m.eval(z3.Int(n), model_completion=True)}"
                for n in names[:3])
            word = "divide by" if op == "/" else "take the remainder of"
            raise VelarisError("E706",
                f"this can {word} zero"
                + (f": {shown}" if shown else "")
                + " - proven without running the program", line,
                fixes=["guard it: if d != 0 { ... }",
                       "or add a 'requires' that rules out zero"])

    pinned_counter = [False]   # True while checking a real final turn

    def prove_bounds(idx, length, ctx, line):
        """Prove 0 <= idx < length; report only provably-real violations."""
        if not pinned_counter[0] and (
                has_fresh(idx) or has_fresh(length)
                or any(has_fresh(c) for c in ctx.conds)):
            return                       # runtime bounds check still guards
        if has_fresh(length) and not pinned_counter[0]:
            return
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
                    and len(fnB.params) == len(node.args)):
                # translate what translates; an argument the prover
                # cannot see becomes an unknown rather than cancelling
                # the whole check - so 'divisor > 0' is still enforced
                # when it sits beside a record list
                args_z3 = []
                for a, (_, pt) in zip(node.args, fnB.params):
                    try:
                        v = to_z3(a, env, ctx)
                    except Unprovable:
                        if pt.startswith("List of "):
                            counter[0] += 1
                            ln = z3.Int(f"__arg_len_{counter[0]}")
                            v = OpaqueList(ln)
                        else:
                            v = None
                    args_z3.append(v)
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

    def bound_of(s, env, ctx, changed):
        """(counter, its last value in the loop, its starting value).

        Only for the simple shape: one Int compared against something the
        loop does not change, stepping by one.
        """
        if not isinstance(s.cond, BinOp) or s.cond.op not in ("<", "<="):
            return None
        left, right = s.cond.left, s.cond.right
        if not isinstance(left, Var) or left.name not in changed:
            return None
        start = env.get(left.name)
        if start is None or not z3.is_int(start) or has_fresh(start):
            return None
        try:
            limit = to_z3(right, env, None)
        except (Unprovable, KeyError):
            return None
        if not z3.is_int(limit) or has_fresh(limit):
            return None
        steps = [st for st in s.body
                 if isinstance(st, Assign) and st.name == left.name]
        if len(steps) != 1:
            return None                  # not a plain one-step counter
        step = steps[0].value
        if not (isinstance(step, BinOp) and step.op == "+"
                and isinstance(step.left, Var)
                and step.left.name == left.name
                and isinstance(step.right, Num) and step.right.value == 1):
            return None
        last = limit - 1 if s.cond.op == "<" else limit
        return (left.name, last, start)

    current_fn = [None]      # the function being proven, for its ensures

    def quantified_candidates(env, changed):
        """all_of(x, P) in the current ensures becomes a candidate
        invariant over every changed list: everything in it so far
        satisfies P. Entry is vacuous (empty list); preservation asks
        the solver whether each pushed element satisfies P on its path;
        afterward the promise follows directly. This is what lets
        'ensures all_of(result, is_positive)' prove through a loop."""
        fn = current_fn[0]
        if fn is None or not fn.ensures:
            return []
        preds = []
        def harvest(e):
            if isinstance(e, Call) and e.name in ("all_of", "any_of") \
                    and len(e.args) == 2 and isinstance(e.args[1], Var):
                pfn = table.get(e.args[1].name)
                if pfn is not None:
                    preds.append(pfn)
            import dataclasses as _dc
            if _dc.is_dataclass(e):
                for f in _dc.fields(e):
                    v = getattr(e, f.name)
                    if isinstance(v, (list, tuple)):
                        for x in v:
                            if _dc.is_dataclass(x):
                                harvest(x)
                    elif _dc.is_dataclass(v):
                        harvest(v)
        for e_expr, _ in fn.ensures:
            harvest(e_expr)
        if not preds:
            return []
        cands = []
        for n in sorted(changed):
            v = env.get(n)
            if not isinstance(v, ListVal):
                continue
            for pfn in preds:
                def c(e, n=n, pfn=pfn):
                    lv = e[n]
                    if not isinstance(lv, ListVal):
                        raise KeyError(n)
                    counter[0] += 1
                    k = z3.Int(f"__qq{counter[0]}")
                    return z3.ForAll([k], z3.Implies(
                        z3.And(k >= 0, k < lv.length),
                        predicate_formula(pfn, z3.Select(lv.arr, k))))
                cands.append((f"everything in '{n}' satisfies "
                              f"'{pfn.name}'", c))
        return cands

    def infer_invariants(env, changed, s, ctx):
        """Guess the boring invariants so people stop writing them.

        Candidates are simple bounds on the counters a loop moves: each
        changed Int either never goes below or never goes above the
        value it had on entry, and lists keep their length. Everything
        is assumed together, one loop step is explored, and whatever a
        step can break is dropped - repeating until the set is stable.
        (This is the Houdini algorithm, kept deliberately small.)
        """
        snap = {}
        for n in sorted(changed):
            v = env.get(n)
            if v is not None and z3.is_int(v) and not has_fresh(v):
                snap[n] = v
        if not snap:
            return []
        cands = []
        for n, start in snap.items():
            cands.append((f"{n} never goes below its starting value",
                          lambda e, n=n, s0=start: e[n] >= s0))
            cands.append((f"{n} never goes above its starting value",
                          lambda e, n=n, s0=start: e[n] <= s0))

        # A counter walking toward a limit stops AT the limit, not past
        # it. Without this the state after a loop only says i >= limit,
        # so 'the loop ran exactly limit times' can never follow - which
        # is what almost every list-building loop needs.
        bound = None
        if isinstance(s.cond, BinOp) and s.cond.op in ("<", "<=", ">", ">="):
            for side, other, op in ((s.cond.left, s.cond.right, s.cond.op),
                                    (s.cond.right, s.cond.left,
                                     {"<": ">", "<=": ">=", ">": "<",
                                      ">=": "<="}[s.cond.op])):
                if isinstance(side, Var) and side.name in snap:
                    try:
                        limit = to_z3(other, env, None)
                    except (Unprovable, KeyError):
                        continue
                    if not z3.is_int(limit) or has_fresh(limit):
                        continue
                    counter = side.name
                    step = 1 if op in ("<", "<=") else -1
                    # 'while i < E' exits with i at most E; 'while i <= E'
                    # exits with i at most E + 1. Off by one here and the
                    # bound is too weak to pin the counter at exit.
                    edge = (limit if op == "<" else limit + 1) if step > 0 \
                        else (limit if op == ">" else limit - 1)
                    bound = (counter, edge, step)
                    label = (f"{counter} never passes the limit the loop "
                             f"tests against")
                    if step > 0:
                        cands.append((label,
                                      lambda e, n=counter, b=edge: e[n] <= b))
                    else:
                        cands.append((label,
                                      lambda e, n=counter, b=edge: e[n] >= b))
                    break

        try:
            cands.extend(quantified_candidates(env, changed))
        except Unprovable:
            pass

        # A list built one item per turn has exactly as many items as the
        # counter has turns. This is the bridge the prover was missing
        # between a loop and the length of what it produced.
        if bound is not None:
            counter, _, _ = bound
            for n in sorted(changed):
                v = env.get(n)
                if not isinstance(v, ListVal) or has_fresh(v.length):
                    continue
                start_len = v.length
                start_counter = snap.get(counter)
                if start_counter is None:
                    continue
                cands.append((
                    f"'{n}' grows one item for each turn of '{counter}'",
                    lambda e, n=n, c=counter, l0=start_len,
                    c0=start_counter: e[n].length == l0 + (e[c] - c0)))
                cands.append((
                    f"'{n}' never outgrows the turns of '{counter}'",
                    lambda e, n=n, c=counter, l0=start_len,
                    c0=start_counter: e[n].length <= l0 + (e[c] - c0)))
                cands.append((f"'{n}' never shrinks",
                              lambda e, n=n, l0=start_len:
                              e[n].length >= l0))

        for _round in range(3):
            env_h, hfacts = havoc_like(env, changed)
            try:
                facts = list(hfacts) + [c(env_h) for _, c in cands]
                cond_h = to_z3(s.cond, env_h, ctx)
            except (Unprovable, KeyError):
                return []
            ctx_body = Ctx(ctx.conds + facts + [cond_h],
                           list(ctx.assum) + facts + [cond_h],
                           list(ctx.param_assum), ctx.caller)
            try:
                paths = explore(list(s.body), dict(env_h), ctx_body)
            except (Unprovable, VelarisError):
                return []
            if os.environ.get("VELARIS_DEBUG_INV"):
                print("  candidates this round:",
                      [lab for lab, _ in cands], file=sys.stderr)
            keep = []
            for label, c in cands:
                ok = True
                for pctx, ret, penv in paths:
                    if ret is not FELL_OFF:
                        continue
                    try:
                        goal = c(penv)
                    except KeyError:
                        ok = False
                        break
                    solver = z3.Solver()
                    solver.set("timeout", solver_budget())
                    solver.add(*pctx.assum)
                    solver.add(*pctx.conds)
                    solver.add(z3.Not(goal))
                    if solver.check() != z3.unsat:
                        ok = False
                        break
                if ok:
                    keep.append((label, c))
            if len(keep) == len(cands):
                return cands
            cands = keep
            if not cands:
                return []
        return cands

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
            elif old is not None and isinstance(old, GridVal):
                counter[0] += 1
                base = f"__{n}_grid_{counter[0]}"
                inner = z3.ArraySort(z3.IntSort(), z3.IntSort())
                gl = z3.Int(base + "__n")
                out[n] = GridVal(z3.Array(base, z3.IntSort(), inner),
                                 z3.Array(base + "__lens", z3.IntSort(),
                                          z3.IntSort()), gl)
                facts.append(gl >= 0)
            elif old is not None and isinstance(old, RecListVal):
                counter[0] += 1
                arrays = {f: z3.Array(f"__{n}_{f}_{counter[0]}",
                                      z3.IntSort(), z3.IntSort())
                          for f in old.arrays}
                ln = z3.Int(f"__{n}_rlen_{counter[0]}")
                out[n] = RecListVal(old.rname, arrays, ln)
                facts.append(ln >= 0)
            elif old is not None and isinstance(old, OpaqueList):
                counter[0] += 1
                ln = z3.Int(f"__{n}_olen_{counter[0]}")
                out[n] = OpaqueList(ln)
                facts.append(ln >= 0)
            elif old is not None and isinstance(old, MapVal):
                counter[0] += 1
                out[n] = mk_map(f"__{n}_havoc_{counter[0]}",
                                f"Map of {old.key_t} to {old.val_t}")
            elif old is not None and z3.is_string(old):
                out[n] = fresh("Text", n)
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
                changed = assigned_names(s.body, set())
                inferred = infer_invariants(env, changed, s, ctx)
                if not s.invariants and not inferred:
                    raise Unprovable()   # no bridge across this loop
                # 1. ENTRY: every written invariant must hold before the
                #    first spin (inferred ones hold by construction)
                for inv_expr, iline in s.invariants:
                    prove_invariant(inv_expr, iline, env, ctx,
                                    "when the loop starts")
                # 2. PRESERVATION: from ANY state the invariants allow,
                #    one loop step must land back inside the invariants
                env_h, hfacts = havoc_like(env, changed)
                facts = list(hfacts)
                for _, c in inferred:
                    try:
                        facts.append(c(env_h))
                    except KeyError:
                        pass
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
                # 2b. THE LAST TURN. A counter that starts inside the
                #     loop's limit and steps by exactly one takes every
                #     value up to the largest the condition allows - so
                #     that turn really happens, and a read on it is a
                #     real read. Pinning the counter there turns "might
                #     be out of range somewhere" into a fact.
                if bound_of(s, env, ctx, changed) is not None:
                    counter, last, start = bound_of(s, env, ctx, changed)
                    reach = z3.Solver()
                    reach.set("timeout", solver_budget())
                    reach.add(*ctx.param_assum)
                    reach.add(*ctx.conds)
                    reach.add(z3.Not(start <= last))
                    if reach.check() == z3.unsat:      # the turn happens
                        env_last, lfacts = havoc_like(env, changed)
                        env_last[counter] = last
                        ctx_last = Ctx(
                            ctx.conds + lfacts,
                            list(ctx.assum) + lfacts,
                            list(ctx.param_assum), ctx.caller)
                        pinned_counter[0] = True
                        try:
                            explore(list(s.body), dict(env_last), ctx_last)
                        except Unprovable:
                            pass
                        finally:
                            pinned_counter[0] = False

                # 3. AFTERWARD: all we know is invariants hold, cond is false
                env_a, hfacts_a = havoc_like(env, changed)
                facts_a = list(hfacts_a)
                for _, c in inferred:
                    try:
                        facts_a.append(c(env_a))
                    except KeyError:
                        pass
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

    cache = _cache_load() if use_cache else {}
    settled: dict = {}          # what this run confirmed
    for fn in funcs:
        key = proof_key(fn, table, records) if use_cache else None
        if key is not None and key in cache:
            remembered = cache[key]
            settled[key] = remembered
            if remembered.get("proven") and proven_out is not None:
                proven_out.add(fn.name)
            for e in remembered.get("errors", []):
                errors.append(VelarisError(
                    e["code"], e["message"], e["line"],
                    fixes=e.get("fixes", []), file=e.get("file")))
            continue
        before_errors = len(errors)
        current_fn[0] = fn
        saw_fp[0] = False              # FP budget only when FP appears
        env = {}
        list_facts = []
        for pname, ptype in fn.params:
            if ptype in ("Int", "Bool", "Float", "Text"):
                env[pname] = mk(pname, ptype)
            elif ptype == "List of Int":
                arr = z3.Array(pname, z3.IntSort(), z3.IntSort())
                ln = z3.Int(pname + "__n")
                env[pname] = ListVal(arr, ln)
                list_facts.append(ln >= 0)
            elif ptype == "List of Text":
                arr = z3.Array(pname, z3.IntSort(), z3.StringSort())
                ln = z3.Int(pname + "__n")
                env[pname] = ListVal(arr, ln)
                list_facts.append(ln >= 0)
            elif ptype == "List of List of Int":
                inner = z3.ArraySort(z3.IntSort(), z3.IntSort())
                rows = z3.Array(pname, z3.IntSort(), inner)
                lens = z3.Array(pname + "__lens", z3.IntSort(),
                                z3.IntSort())
                ln = z3.Int(pname + "__n")
                env[pname] = GridVal(rows, lens, ln)
                list_facts.append(ln >= 0)
                k0 = z3.Int(pname + "__k")
                list_facts.append(z3.ForAll(
                    [k0], z3.Select(lens, k0) >= 0))
            elif ptype in rec_fields and provable_rec(ptype):
                env[pname] = mk_rec(pname, ptype)
            elif (ptype.startswith("List of ")
                  and ptype[len("List of "):] in rec_fields
                  and provable_rec(ptype[len("List of "):])):
                rname = ptype[len("List of "):]
                arrays = {}
                for fname, ftype in rec_fields[rname]:
                    if ftype == "Int":
                        arrays[fname] = z3.Array(
                            f"{pname}__{fname}", z3.IntSort(),
                            z3.IntSort())
                ln = z3.Int(pname + "__n")
                env[pname] = RecListVal(rname, arrays, ln)
                list_facts.append(ln >= 0)
            elif ptype.startswith("List of "):
                # the contents cannot be modelled, but the LENGTH can -
                # and length is what contracts about lists usually say.
                # Without this, one length(items) in a conjunction threw
                # the whole requires away, checkable parts included.
                ln = z3.Int(pname + "__n")
                env[pname] = OpaqueList(ln)
                list_facts.append(ln >= 0)
            elif ptype.startswith("Map of "):
                mv = mk_map(pname, ptype)
                if mv is not None:
                    env[pname] = mv
        import dataclasses as _dc

        def mentions_case(node) -> bool:
            if isinstance(node, (list, tuple)):
                return any(mentions_case(x) for x in node)
            if not _dc.is_dataclass(node):
                return False
            if isinstance(node, Call) and node.name in ("upper", "lower"):
                return True
            return any(mentions_case(getattr(node, f.name))
                       for f in _dc.fields(node))

        def mentions(node, names) -> bool:
            if isinstance(node, (list, tuple)):
                return any(mentions(x, names) for x in node)
            if not _dc.is_dataclass(node):
                return False
            if isinstance(node, Call) and node.name in names:
                return True
            return any(mentions(getattr(node, f.name), names)
                       for f in _dc.fields(node))

        parts = [fn.body, [e for e, _ in fn.ensures],
                 [e for e, _ in fn.requires]]
        if any(mentions(p, ("upper", "lower")) for p in parts):
            list_facts.extend(CASE_AXIOMS)   # only where they matter
        if any(mentions(p, ("split",)) for p in parts):
            list_facts.extend(SPLIT_AXIOMS)
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
                        elif isinstance(ret, MapVal):
                            rv = "a map"
                        elif isinstance(ret, GridVal):
                            rv = "a list of lists"
                        else:
                            rv = m.eval(ret, model_completion=True)
                        raise VelarisError("E700",
                            f"promise cannot be kept: {nice_name(fn.name)} ensures "
                            f"{expr_str(ens_expr)} - proven without running "
                            f"the program: {vals} gives result = {rv}",
                            cline,
                            fixes=["fix the code so the promise holds for "
                                   "every allowed input",
                                   "or add a 'requires' that rules out "
                                   "such inputs"])
                    if verdict != z3.unsat:
                        raise Unprovable()
            if proven_out is not None and (fn.ensures or fn.requires):
                proven_out.add(fn.name)   # every obligation discharged
            if key is not None:
                settled[key] = {
                    "proven": bool(fn.ensures or fn.requires),
                    "errors": [{"code": e.code, "message": e.message,
                                "line": e.line, "fixes": e.fixes,
                                "file": e.file}
                               for e in errors[before_errors:]]}
        except Unprovable:
            if key is not None:
                settled[key] = {"proven": False, "errors": [
                    {"code": e.code, "message": e.message, "line": e.line,
                     "fixes": e.fixes, "file": e.file}
                    for e in errors[before_errors:]]}
            continue                    # runtime promise checks still guard
        except z3.Z3Exception:
            continue                    # solver hiccup: runtime still guards
        except VelarisError as e:
            errors.append(blame(fn, e))
            if key is not None:         # a refutation is worth remembering
                settled[key] = {"proven": False, "errors": [
                    {"code": x.code, "message": x.message, "line": x.line,
                     "fixes": x.fixes, "file": x.file}
                    for x in errors[before_errors:]]}
            continue

    if use_cache:
        _cache_save(settled)


# ---------------------------------------------------------------------------
# 4d. NATIVE COMPILER (v0.9) — compile pure Int functions to machine code
#     via LLVM. Eligible: params and return are Int; body uses only math,
#     comparisons, and/or/not, if, while, let/assign, and calls to other
#     eligible functions. No effects; contracts are allowed once PROVEN
#     (an unproven promise still needs its runtime check); no '/';
#     lists and text may be READ (bounds-guarded), not built.
# ---------------------------------------------------------------------------

_NATIVE_KEEPALIVE = []          # prevents the JIT engine being garbage-collected


def native_eligible(funcs: list[Function],
                    proven: set = frozenset()) -> set[str]:
    table = {f.name: f for f in funcs}

    def locally_ok(fn: Function):
        if fn.effects or fn.can_fail or fn.type_vars:
            return None
        if (fn.requires or fn.ensures) and fn.name not in proven:
            return None       # unproven promises still need runtime checks
        if fn.return_type not in ("Int", "Float", "Bool"):
            return None      # text results stay interpreted: returning a
                             # struct by value is platform-specific ABI
        if any(pt not in ("Int", "Float", "Bool", "List of Int", "Text")
               for _, pt in fn.params):
            return None
        list_params = {p for p, t in fn.params if t == "List of Int"}
        text_params = {p for p, t in fn.params if t == "Text"}
        calls, ok = set(), [True]
        local_text = set(text_params)

        def text_valued(e) -> bool:
            if isinstance(e, Str):
                return True
            if isinstance(e, Var):
                return e.name in local_text
            if isinstance(e, Call):
                callee = table.get(e.name)
                return callee is not None and callee.return_type == "Text"
            if isinstance(e, BinOp) and e.op == "+":
                return text_valued(e.left)
            return False

        def note_text(stmts):           # locals that hold text
            for s in stmts:
                if isinstance(s, (Let, Assign)) and text_valued(s.value):
                    local_text.add(s.name)
                elif isinstance(s, If):
                    note_text(s.then); note_text(s.other)
                elif isinstance(s, While):
                    note_text(s.body)
        note_text(fn.body)
        note_text(fn.body)              # twice: assignments after use

        def we(e):
            if isinstance(e, Str):
                return                  # text literals are compiled in
            if isinstance(e, (Num, FloatNum, Bool, Var)):
                return
            if (isinstance(e, Call) and e.name in ("length", "get")
                    and e.args and isinstance(e.args[0], Var)
                    and e.args[0].name in list_params):
                for a in e.args[1:]:
                    we(a)
                return
            if (isinstance(e, Call) and e.name in ("length", "code_at")
                    and e.args and text_valued(e.args[0])):
                we(e.args[0])
                for a in e.args[1:]:
                    we(a)
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


def compile_native(funcs: list[Function],
                   proven: set = frozenset()) -> dict:
    """Native code is an optimisation, never a requirement: if anything
    about this machine's backend disagrees with us, the program runs
    interpreted and behaves exactly the same, just slower."""
    try:
        return _compile_native(funcs, proven)
    except Exception:
        return {}


def _compile_native(funcs: list[Function],
                    proven: set = frozenset()) -> dict:
    eligible = native_eligible(funcs, proven)
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
    i64p = ir.PointerType(i64)
    i32 = ir.IntType(32)
    i32p = ir.PointerType(i32)
    TEXT = ir.LiteralStructType([i32p, i64])
    LTY = {"Int": i64, "Bool": i64, "Float": f64, "Text": TEXT}


    def llvm_params(fn):
        out = []
        for _, pt in fn.params:
            if pt == "List of Int":
                out += [i64p, i64]        # data pointer, then length
            elif pt == "Text":
                out += [i32p, i64]        # code points, then length
            else:
                out.append(LTY[pt])
        return out
    module = ir.Module(name="velaris")
    oob = ir.GlobalVariable(module, i64, name="velaris_oob")
    oob.initializer = i64(0)
    oob_idx = ir.GlobalVariable(module, i64, name="velaris_oob_idx")
    oob_idx.initializer = i64(0)
    oob_len = ir.GlobalVariable(module, i64, name="velaris_oob_len")
    oob_len.initializer = i64(0)
    arena = ir.GlobalVariable(module, i32p, name="velaris_arena")
    arena.initializer = ir.Constant(i32p, None)
    arena_cap = ir.GlobalVariable(module, i64, name="velaris_arena_cap")
    arena_cap.initializer = i64(0)
    arena_used = ir.GlobalVariable(module, i64, name="velaris_arena_used")
    arena_used.initializer = i64(0)
    arena_full = ir.GlobalVariable(module, i64, name="velaris_arena_full")
    arena_full.initializer = i64(0)
    overflowed = ir.GlobalVariable(module, i64, name="velaris_overflow")
    overflowed.initializer = i64(0)
    ovf_fns = {}
    for op_name in ("sadd", "ssub", "smul"):
        fty = ir.FunctionType(
            ir.LiteralStructType([i64, ir.IntType(1)]), [i64, i64])
        ovf_fns[op_name] = ir.Function(
            module, fty, name=f"llvm.{op_name}.with.overflow.i64")
    lit_count = [0]
    table = {f.name: f for f in funcs}
    llvm_fns = {}
    for name in eligible:
        fn = table[name]
        fty = ir.FunctionType(LTY[fn.return_type], llvm_params(fn))
        llvm_fns[name] = ir.Function(module, fty, name=name)

    def var_types(fn: Function) -> dict:
        """Sequentially infer each local's Velaris type for typed allocas."""
        tenv = dict(fn.params)

        def te(e) -> str:
            if isinstance(e, Num):
                return "Int"
            if isinstance(e, Str):
                return "Text"
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
                if e.name in ("length", "get", "code_at"):
                    return "Int"        # builtin reads used natively
                return table[e.name].return_type
            if isinstance(e, BinOp):
                if e.op in ("and", "or", "==", "!=", "<", ">", "<=", ">="):
                    return "Bool"
                return te(e.left)      # '+' on Text gives Text
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
        lists = {}                     # name -> (data pointer, length)
        texts = {}                     # name -> (code points, length)
        list_names = {p for p, t in fn.params if t == "List of Int"}
        for n in sorted(names - list_names):
            slots[n] = b.alloca(LTY[tenv.get(n, "Int")], name=n)
        ai = 0
        for pname, ptype in fn.params:
            if ptype == "Text":
                data, ln = lf.args[ai], lf.args[ai + 1]
                data.name, ln.name = pname + "_data", pname + "_len"
                tv = b.insert_value(
                    b.insert_value(ir.Constant(TEXT, ir.Undefined), data, 0),
                    ln, 1)
                slots[pname] = b.alloca(TEXT, name=pname)
                b.store(tv, slots[pname])
                ai += 2
            elif ptype == "List of Int":
                data, ln = lf.args[ai], lf.args[ai + 1]
                data.name, ln.name = pname + "_data", pname + "_len"
                lists[pname] = (data, ln)
                ai += 2
            else:
                lf.args[ai].name = pname
                b.store(lf.args[ai], slots[pname])
                ai += 1

        def txt_ptr(v):
            return b.extract_value(v, 0)

        def txt_len(v):
            return b.extract_value(v, 1)

        def make_text(ptr, ln):
            t = b.insert_value(ir.Constant(TEXT, ir.Undefined), ptr, 0)
            return b.insert_value(t, ln, 1)

        def arena_alloc(n):
            """Bump-allocate n code points; flag (don't crash) if full."""
            used = b.load(arena_used)
            cap = b.load(arena_cap)
            room = b.icmp_signed("<=", b.add(used, n), cap)
            ok_bb = lf.append_basic_block("arena_ok")
            full_bb = lf.append_basic_block("arena_full")
            cont_bb = lf.append_basic_block("arena_done")
            b.cbranch(room, ok_bb, full_bb)
            b.position_at_end(ok_bb)
            base = b.load(arena)
            slot = b.gep(base, [used])
            b.store(b.add(used, n), arena_used)
            b.branch(cont_bb)
            b.position_at_end(full_bb)
            b.store(i64(1), arena_full)      # caller grows and retries
            fallback = b.load(arena)
            b.branch(cont_bb)
            b.position_at_end(cont_bb)
            phi = b.phi(i32p)
            phi.add_incoming(slot, ok_bb)
            phi.add_incoming(fallback, full_bb)
            room_phi = b.phi(ir.IntType(1))
            room_phi.add_incoming(ir.Constant(ir.IntType(1), 1), ok_bb)
            room_phi.add_incoming(ir.Constant(ir.IntType(1), 0), full_bb)
            return phi, room_phi

        def copy_into(dst, src_ptr, n, tag):
            """Copy n code points, one at a time (small texts, no libc)."""
            i_slot = b.alloca(i64, name=tag + "_i")
            b.store(i64(0), i_slot)
            head = lf.append_basic_block(tag + "_head")
            body = lf.append_basic_block(tag + "_body")
            done = lf.append_basic_block(tag + "_done")
            b.branch(head)
            b.position_at_end(head)
            iv = b.load(i_slot)
            b.cbranch(b.icmp_signed("<", iv, n), body, done)
            b.position_at_end(body)
            iv2 = b.load(i_slot)
            b.store(b.load(b.gep(src_ptr, [iv2])), b.gep(dst, [iv2]))
            b.store(b.add(iv2, i64(1)), i_slot)
            b.branch(head)
            b.position_at_end(done)

        def ee(e):                    # emit expression (i64 or double)
            if isinstance(e, Num):
                return i64(e.value)
            if isinstance(e, Str):
                pts = [ord(c) for c in e.value]
                lit_count[0] += 1
                arr_ty = ir.ArrayType(i32, max(len(pts), 1))
                g = ir.GlobalVariable(module, arr_ty,
                                      name=f"text_lit_{lit_count[0]}")
                g.global_constant = True
                g.initializer = ir.Constant(
                    arr_ty, [ir.Constant(i32, p) for p in pts] or
                    [ir.Constant(i32, 0)])
                ptr = b.gep(g, [i64(0), i64(0)])
                return make_text(ptr, i64(len(pts)))
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
            if (isinstance(e, Call) and e.name in ("length", "code_at")
                    and e.args and not (isinstance(e.args[0], Var)
                                        and e.args[0].name in lists)):
                tv = ee(e.args[0])
                if tv.type != TEXT:
                    raise NotImplementedError("length on a non-text value")
                data, ln = txt_ptr(tv), txt_len(tv)
                if e.name == "length":
                    return ln
                idx = ee(e.args[1])
                inside = b.and_(b.icmp_signed(">=", idx, i64(0)),
                                b.icmp_signed("<", idx, ln))
                ok_bb = lf.append_basic_block("char_ok")
                bad_bb = lf.append_basic_block("char_out")
                cont_bb = lf.append_basic_block("char_done")
                b.cbranch(inside, ok_bb, bad_bb)
                b.position_at_end(ok_bb)
                ch = b.zext(b.load(b.gep(data, [idx])), i64)
                b.branch(cont_bb)
                b.position_at_end(bad_bb)
                b.store(i64(1), oob)
                b.store(idx, oob_idx)
                b.store(ln, oob_len)
                b.branch(cont_bb)
                b.position_at_end(cont_bb)
                phi = b.phi(i64)
                phi.add_incoming(ch, ok_bb)
                phi.add_incoming(i64(0), bad_bb)
                return phi
            if (isinstance(e, Call) and e.name in ("length", "get")
                    and e.args and isinstance(e.args[0], Var)
                    and e.args[0].name in lists):
                data, ln = lists[e.args[0].name]
                if e.name == "length":
                    return ln
                idx = ee(e.args[1])
                inside = b.and_(b.icmp_signed(">=", idx, i64(0)),
                                b.icmp_signed("<", idx, ln))
                ok_bb = lf.append_basic_block("read_ok")
                bad_bb = lf.append_basic_block("read_out")
                cont_bb = lf.append_basic_block("read_done")
                b.cbranch(inside, ok_bb, bad_bb)
                b.position_at_end(ok_bb)          # in range: real read
                val = b.load(b.gep(data, [idx]))
                b.branch(cont_bb)
                b.position_at_end(bad_bb)         # out of range: no read,
                b.store(i64(1), oob)              # just record it
                b.store(idx, oob_idx)
                b.store(ln, oob_len)
                b.branch(cont_bb)
                b.position_at_end(cont_bb)
                phi = b.phi(i64)
                phi.add_incoming(val, ok_bb)
                phi.add_incoming(i64(0), bad_bb)
                return phi
            if isinstance(e, Call):
                args_ll = []
                callee = table.get(e.name)
                want = [t for _, t in callee.params] if callee else []
                for pos, a in enumerate(e.args):
                    if pos < len(want) and want[pos] == "Text":
                        tv = ee(a)
                        args_ll += [txt_ptr(tv), txt_len(tv)]
                        continue
                    if isinstance(a, Var) and a.name in lists:
                        args_ll += list(lists[a.name])
                    else:
                        args_ll.append(ee(a))
                return b.call(llvm_fns[e.name], args_ll)
            if isinstance(e, BinOp) and e.op == "+":
                lv = ee(e.left)
                if lv.type == TEXT:
                    rv = ee(e.right)
                    if rv.type != TEXT:
                        raise NotImplementedError
                    ln_l, ln_r = txt_len(lv), txt_len(rv)
                    total = b.add(ln_l, ln_r)
                    dst, had_room = arena_alloc(total)
                    # no room means NO copying: the caller grows the
                    # buffer and runs the whole call again
                    do_bb = lf.append_basic_block("cat_do")
                    skip_bb = lf.append_basic_block("cat_skip")
                    end_bb = lf.append_basic_block("cat_end")
                    b.cbranch(had_room, do_bb, skip_bb)
                    b.position_at_end(do_bb)
                    copy_into(dst, txt_ptr(lv), ln_l, "cpl")
                    copy_into(b.gep(dst, [ln_l]), txt_ptr(rv), ln_r, "cpr")
                    did_bb = b.block          # loops moved us elsewhere
                    b.branch(end_bb)
                    b.position_at_end(skip_bb)
                    skipped_bb = b.block
                    b.branch(end_bb)
                    b.position_at_end(end_bb)
                    ln_phi = b.phi(i64)
                    ln_phi.add_incoming(total, did_bb)
                    ln_phi.add_incoming(i64(0), skipped_bb)
                    return make_text(dst, ln_phi)
            if isinstance(e, BinOp):
                if e.op == "and":
                    return b.and_(ee(e.left), ee(e.right))
                if e.op == "or":
                    return b.or_(ee(e.left), ee(e.right))
                l, r = ee(e.left), ee(e.right)
                flt = l.type == f64

                def checked(kind, value):
                    """Same answer as interpreted: too big is an error."""
                    pair = b.call(ovf_fns[kind], [l, r])
                    bit = b.extract_value(pair, 1)
                    was = b.load(overflowed)
                    b.store(b.select(bit, i64(1), was), overflowed)
                    return b.extract_value(pair, 0)

                if e.op == "+":
                    return b.fadd(l, r) if flt else checked("sadd", None)
                if e.op == "-":
                    return b.fsub(l, r) if flt else checked("ssub", None)
                if e.op == "*":
                    return b.fmul(l, r) if flt else checked("smul", None)
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
    I64P = ctypes.POINTER(ctypes.c_int64)
    I32P = ctypes.POINTER(ctypes.c_uint32)
    oob_addr = engine.get_global_value_address("velaris_oob")
    idx_addr = engine.get_global_value_address("velaris_oob_idx")
    len_addr = engine.get_global_value_address("velaris_oob_len")
    flag = ctypes.cast(oob_addr, I64P)
    ovf_cell = ctypes.cast(
        engine.get_global_value_address("velaris_overflow"), I64P)
    flag_i = ctypes.cast(idx_addr, I64P)
    flag_n = ctypes.cast(len_addr, I64P)

    class CText(ctypes.Structure):
        _fields_ = [("data", ctypes.POINTER(ctypes.c_uint32)),
                    ("length", ctypes.c_int64)]

    arena_state = {"buf": (ctypes.c_uint32 * (1 << 16))(), "cap": 1 << 16}
    arena_ptr_cell = ctypes.cast(
        engine.get_global_value_address("velaris_arena"),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)))
    arena_cap_cell = ctypes.cast(
        engine.get_global_value_address("velaris_arena_cap"), I64P)
    arena_used_cell = ctypes.cast(
        engine.get_global_value_address("velaris_arena_used"), I64P)
    arena_full_cell = ctypes.cast(
        engine.get_global_value_address("velaris_arena_full"), I64P)

    def install_arena():
        arena_ptr_cell[0] = ctypes.cast(
            arena_state["buf"], ctypes.POINTER(ctypes.c_uint32))
        arena_cap_cell[0] = arena_state["cap"]
    install_arena()

    def grow_arena():
        arena_state["cap"] *= 4
        arena_state["buf"] = (ctypes.c_uint32 * arena_state["cap"])()
        install_arena()

    def wrap(fn, raw):
        types = [pt for _, pt in fn.params]
        wants_bool = fn.return_type == "Bool"
        wants_text = fn.return_type == "Text"

        def call(*vals):
            cargs = []
            keep = []                    # keep buffers alive for the call
            for t, v in zip(types, vals):
                if t == "Text":
                    buf = (ctypes.c_uint32 * len(v))(*[ord(c) for c in v])
                    keep.append(buf)
                    cargs += [ctypes.cast(buf, I32P), len(v)]
                elif t == "List of Int":
                    buf = (ctypes.c_int64 * len(v))(*v)
                    keep.append(buf)
                    cargs += [ctypes.cast(buf, I64P), len(v)]
                else:
                    cargs.append(v)
            for _attempt in range(6):
                flag[0] = 0
                ovf_cell[0] = 0
                arena_used_cell[0] = 0
                arena_full_cell[0] = 0
                r = raw(*cargs)
                if ovf_cell[0]:
                    ovf_cell[0] = 0
                    raise VelarisError("E407",
                        "this arithmetic made a number too big to hold "
                        f"(whole numbers go from {INT_MIN} to "
                        f"{INT_MAX})", fn.line,
                        fixes=["keep the numbers smaller",
                               "or work in smaller units, like cents "
                               "instead of rupees"])
                if not arena_full_cell[0]:
                    break
                grow_arena()          # too small: bigger buffer, run again
            else:
                raise VelarisError("E607",
                    "this text grew too large to build", fn.line,
                    fixes=["build shorter pieces of text"])
            if flag[0]:                  # the read was refused, not made
                i, n = flag_i[0], flag_n[0]
                flag[0] = 0
                what = ("text" if any(t == "Text" for t in types)
                        else "list")
                unit = "character" if what == "text" else "item"
                raise VelarisError("E602",
                    f"position {i} is outside the {what} "
                    f"(it has {n} {unit}(s))", fn.line,
                    fixes=["positions go from 0 to length - 1",
                           "check with length(...) before using get"])
            if wants_text:
                return "".join(chr(r.data[i]) for i in range(r.length))
            return bool(r) if wants_bool else r
        return call

    out = {}
    for name in eligible:
        fn = table[name]
        ctypes_args = []
        for _, pt in fn.params:
            if pt == "Text":
                ctypes_args += [I32P, ctypes.c_int64]
            elif pt == "List of Int":
                ctypes_args += [I64P, ctypes.c_int64]
            else:
                ctypes_args.append(CT[pt])
        proto = ctypes.CFUNCTYPE(CT[fn.return_type], *ctypes_args)
        raw = proto(engine.get_function_address(name))
        out[name] = wrap(fn, raw)
    return out


# ---------------------------------------------------------------------------
# 5. INTERPRETER — actually run the program (main() is the entry point)
# ---------------------------------------------------------------------------

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value


class RecElem:
    """rows[i] before a field is chosen: .amount selects from the
    field's array at that index."""
    def __init__(self, src, idx):
        self.src = src
        self.idx = idx


class RecListVal:
    """A list of records, as one array per provable field.

    get(rows, i).amount becomes Select(amount_arr, i) - so bounds are
    checked (the off-by-one over a record list refused before running,
    like the Int-list case) and field arithmetic can prove.
    """
    def __init__(self, rname, arrays, length):
        self.rname = rname          # the record type's name
        self.arrays = arrays        # field name -> z3 Int array
        self.length = length


class OpaqueList:
    """A list whose contents the prover cannot see - only its length.

    Enough for the contracts people actually write about lists of
    records: length(items) > 0, length(result) == length(items), and
    for a divisor to be provably nonzero.
    """
    def __init__(self, length):
        self.length = length


class FailSignal(Exception):
    def __init__(self, reason): self.reason = reason


class HandleValue:
    """A ticket for something living on the Python side of the bridge."""
    __slots__ = ("id", "what")

    def __init__(self, id_: int, what: str):
        self.id, self.what = id_, what

    def __repr__(self):
        return f"<{self.what} #{self.id}>"


PY_OBJECTS: dict = {}
PY_NEXT = [1]


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
    if isinstance(v, HandleValue):
        return f"<{v.what} #{v.id}>"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return "[" + ", ".join(to_text(x) for x in v) + "]"
    return str(v)


# effects per builtin, sorted once instead of on every call
BUILTIN_EFFECTS = {n: tuple(sorted(d.get("effects", ())))
                   for n, d in BUILTINS.items() if d.get("effects")}


def run_builtin(name: str, args: list, line: int):
    # The hot three, before anything else: these are most of the builtin
    # calls in any program and used to sit behind thirty string
    # comparisons and two module imports. None of them has effects, so
    # the budget check does not apply.
    if name == "length":
        a0 = args[0]
        return len(a0) if not isinstance(a0, str) else len(a0)
    if name == "get" and isinstance(args[0], list):
        xs, at = args[0], args[1]
        if not isinstance(at, int) or at < 0 or at >= len(xs):
            raise VelarisError("E602",
                f"this list has {len(xs)} item(s), so there is no "
                f"position {at}", line,
                fixes=["check the length before reading",
                       "or add a 'requires' about the length"])
        return xs[at]
    if name == "push" and isinstance(args[0], list):
        return args[0] + [args[1]]

    import time as _time
    import random as _rand
    for effect in BUILTIN_EFFECTS.get(name, ()):   # precomputed; this
        spend(effect, name, line)                  # ran sorted() on
                                                   # every single call
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
    if name == "pop":
        xs = args[0]
        if not xs:
            raise FailSignal("there is nothing left to take off the end")
        return list(xs[:-1])
    if name == "slice":
        xs, start, stop = args[0], int(args[1]), int(args[2])
        if start < 0 or stop > len(xs) or start > stop:
            raise FailSignal(
                f"a slice from {start} to {stop} does not fit a list of "
                f"{len(xs)}")
        return list(xs[start:stop])
    if name == "set_at":
        xs, at = args[0], int(args[1])
        if at < 0 or at >= len(xs):
            raise FailSignal(
                f"there is no position {at} in a list of {len(xs)}")
        out = list(xs)
        out[at] = args[2]
        return out
    if name in ("div_or_fail", "mod_or_fail"):
        a, b = int(args[0]), int(args[1])
        if b == 0:
            word = "divide" if name == "div_or_fail" else "take a remainder"
            raise FailSignal(f"cannot {word} by zero")
        return a // b if name == "div_or_fail" else a % b
    if name in ("add_or_fail", "sub_or_fail", "mul_or_fail"):
        a, b = int(args[0]), int(args[1])
        answer = (a + b if name == "add_or_fail" else
                  a - b if name == "sub_or_fail" else a * b)
        if not (-(2 ** 63) <= answer <= 2 ** 63 - 1):
            word = {"add_or_fail": "adding", "sub_or_fail": "subtracting",
                    "mul_or_fail": "multiplying"}[name]
            raise FailSignal(
                f"{word} {a} and {b} makes a number too big to hold")
        return answer
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
    if name in ("py_new", "py_do", "py_field", "py_close"):
        import json as _json

        def resolve(module: str, func: str):
            import importlib
            mod, rest = None, ""
            parts = str(module).split(".")
            for cut in range(len(parts), 0, -1):
                try:
                    allow_module(".".join(parts[:cut]), name, line)
                    mod = importlib.import_module(".".join(parts[:cut]))
                    rest = ".".join(parts[cut:])
                    break
                except ImportError:
                    continue
            if mod is None:
                raise FailSignal(f"cannot import '{module}'")
            target = mod
            for part in ([p for p in rest.split(".") if p]
                         + [p for p in str(func).split(".") if p]):
                target = getattr(target, part, None)
                if target is None:
                    raise FailSignal(f"'{module}' has no '{func}'")
            return target

        def split_args(raw):
            """A JSON list of arguments; a trailing object is keywords."""
            try:
                vals = _json.loads(str(raw))
            except Exception as e:
                raise FailSignal(f"the arguments are not valid JSON: {e}")
            if not isinstance(vals, list):
                raise FailSignal("the arguments must be a JSON list")
            kwargs = {}
            if (vals and isinstance(vals[-1], dict)
                    and set(vals[-1]) != {"handle"}):
                kwargs = {str(k): v for k, v in vals[-1].items()}
                vals = vals[:-1]
            return [unwrap(v) for v in vals], {k: unwrap(v)
                                               for k, v in kwargs.items()}

        def unwrap(v):
            """A handle written as {"handle": 3} becomes the object."""
            if isinstance(v, dict) and set(v) == {"handle"}:
                obj = PY_OBJECTS.get(int(v["handle"]))
                if obj is None:
                    raise FailSignal("that handle is closed or unknown")
                return obj
            return v

        def keep(obj) -> "HandleValue":
            PY_NEXT[0] += 1
            PY_OBJECTS[PY_NEXT[0]] = obj
            return HandleValue(PY_NEXT[0], type(obj).__name__)

        def answer(out):
            if isinstance(out, (bytes, bytearray)):
                out = out.decode("utf-8", errors="replace")
            try:
                return _json.dumps(out, ensure_ascii=False)
            except TypeError:                  # not JSON: keep it alive
                return _json.dumps({"handle": keep(out).id})

        if name == "py_close":
            h = args[0]
            if isinstance(h, HandleValue):
                obj = PY_OBJECTS.pop(h.id, None)
                for closer in ("close", "shutdown", "__exit__"):
                    fn_ = getattr(obj, closer, None)
                    if fn_ is not None:
                        try:
                            fn_() if closer != "__exit__" else fn_(
                                None, None, None)
                        except Exception:
                            pass
                        break
            return None

        if name == "py_new":
            target = resolve(args[0], args[1])
            pos, kw = split_args(args[2])
            try:
                return keep(target(*pos, **kw))
            except Exception as e:
                raise FailSignal(f"{args[0]}.{args[1]} failed: {e}")

        h = args[0]
        if not isinstance(h, HandleValue):
            raise FailSignal("this is not a handle")
        obj = PY_OBJECTS.get(h.id)
        if obj is None:
            raise FailSignal("that handle is closed")
        if name == "py_field":
            got = getattr(obj, str(args[1]), None)
            if got is None:
                raise FailSignal(f"no '{args[1]}' on {h.what}")
            return answer(got)
        method = getattr(obj, str(args[1]), None)
        if method is None:
            raise FailSignal(f"{h.what} has no '{args[1]}'")
        pos, kw = split_args(args[2])
        try:
            return answer(method(*pos, **kw))
        except Exception as e:
            raise FailSignal(f"{h.what}.{args[1]} failed: {e}")
    if name.startswith("json_") or name == "py_json":
        import json as _json

        def walk(doc_text, path_text, what):
            try:
                cur = _json.loads(str(doc_text))
            except Exception as e:
                raise FailSignal(f"this is not valid JSON: {e}")
            if str(path_text) == "":
                return cur
            for step in str(path_text).replace("[", ".").replace(
                    "]", "").split("."):
                if step == "":
                    continue
                if isinstance(cur, list):
                    try:
                        idx = int(step)
                    except ValueError:
                        raise FailSignal(
                            f"'{step}' is not a position in a list "
                            f"(while looking for '{path_text}')")
                    if not -len(cur) <= idx < len(cur):
                        raise FailSignal(
                            f"position {idx} is outside this list of "
                            f"{len(cur)} (while looking for "
                            f"'{path_text}')")
                    cur = cur[idx]
                elif isinstance(cur, dict):
                    if step not in cur:
                        raise FailSignal(
                            f"there is no '{step}' here (while looking "
                            f"for '{path_text}')")
                    cur = cur[step]
                else:
                    raise FailSignal(
                        f"cannot look inside {type(cur).__name__} "
                        f"(while looking for '{path_text}')")
            return cur

        if name == "json_of":
            def plain(v):
                if isinstance(v, dict):
                    return {str(k): plain(x) for k, x in v.items()}
                if isinstance(v, list):
                    return [plain(x) for x in v]
                if isinstance(v, RecordValue):
                    return {f: plain(x) for f, x in v.fields.items()}
                return v
            return _json.dumps(plain(args[0]), ensure_ascii=False)

        if name == "json_has":
            try:
                walk(args[0], args[1], "has")
                return True
            except FailSignal:
                return False

        if name == "json_len":
            got = walk(args[0], args[1], "len")
            if isinstance(got, (list, dict, str)):
                return len(got)
            raise FailSignal("this value has no length")

        if name in ("json_get", "json_int", "json_float"):
            got = walk(args[0], args[1], name)
            if name == "json_get":
                if isinstance(got, bool):
                    return "true" if got else "false"
                if isinstance(got, (dict, list)):
                    return _json.dumps(got, ensure_ascii=False)
                return "" if got is None else str(got)
            try:
                return int(got) if name == "json_int" else float(got)
            except (TypeError, ValueError):
                raise FailSignal(
                    f"'{args[1]}' is not a "
                    f"{'whole number' if name == 'json_int' else 'decimal'}")

        # py_json: arguments and answer both travel as JSON, so numbers,
        # lists and nested data survive the trip intact
        module, func, args_json = args[0], args[1], args[2]
        try:
            call_args = _json.loads(str(args_json))
        except Exception as e:
            raise FailSignal(f"the arguments are not valid JSON: {e}")
        if not isinstance(call_args, list):
            raise FailSignal("the arguments must be a JSON list, "
                             'like [1, "two", [3]]')
        def unwrap_handle(v):
            if isinstance(v, dict) and set(v) == {"handle"}:
                obj = PY_OBJECTS.get(int(v["handle"]))
                if obj is None:
                    raise FailSignal("that handle is closed or unknown")
                return obj
            return v

        kwargs = {}
        if (call_args and isinstance(call_args[-1], dict)
                and set(call_args[-1]) != {"handle"}):
            kwargs = {str(k): unwrap_handle(v)
                      for k, v in call_args[-1].items()}
            call_args = call_args[:-1]
        call_args = [unwrap_handle(v) for v in call_args]
        import importlib
        mod, rest = None, ""
        parts = str(module).split(".")
        for cut in range(len(parts), 0, -1):
            try:
                allow_module(".".join(parts[:cut]), name, line)
                mod = importlib.import_module(".".join(parts[:cut]))
                rest = ".".join(parts[cut:])
                break
            except ImportError:
                continue
        if mod is None:
            raise FailSignal(f"cannot import '{module}'")
        target = mod
        for part in ([p for p in rest.split(".") if p]
                     + [p for p in str(func).split(".") if p]):
            target = getattr(target, part, None)
            if target is None:
                raise FailSignal(f"'{module}' has no '{func}'")
        try:
            out = target(*call_args, **kwargs)
        except Exception as e:
            raise FailSignal(f"{module}.{func} failed: {e}")
        if isinstance(out, (bytes, bytearray)):
            out = out.decode("utf-8", errors="replace")
        try:
            return _json.dumps(out, ensure_ascii=False)
        except TypeError:                     # not JSON: keep it alive
            PY_NEXT[0] += 1
            PY_OBJECTS[PY_NEXT[0]] = out
            return _json.dumps({"handle": PY_NEXT[0]})
    if name in ("py", "py_int", "py_float"):
        module, func, call_args = args[0], args[1], args[2]
        import importlib
        mod, rest = None, ""
        parts = str(module).split(".")
        for cut in range(len(parts), 0, -1):     # datetime.date works:
            try:                                  # import what imports,
                allow_module(".".join(parts[:cut]), name, line)
                mod = importlib.import_module(".".join(parts[:cut]))
                rest = ".".join(parts[cut:])      # reach the rest by name
                break
            except ImportError:
                continue
        if mod is None:
            raise FailSignal(f"cannot import '{module}'")
        target = mod
        for part in ([p for p in rest.split(".") if p]
                     + [p for p in str(func).split(".") if p]):
            target = getattr(target, part, None)
            if target is None:
                raise FailSignal(f"'{module}' has no '{func}'")
        def as_number_if_it_is(text):
            """'16' -> 16 and '2.5' -> 2.5, so numeric functions work.

            The arguments arrive as Text (that is the declared type),
            but math.sqrt("16") is a TypeError in Python. A string that
            reads as a number is passed as one; anything else stays
            text. Functions genuinely wanting the text "16" still get
            it via the all-strings retry below.
            """
            s = str(text)
            try:
                return int(s)
            except ValueError:
                pass
            try:
                return float(s)
            except ValueError:
                return s

        attempts = ([as_number_if_it_is(a) for a in call_args],
                    [str(a) for a in call_args],
                    [str(a).encode("utf-8") for a in call_args])
        out, last_err = None, None
        for formed in attempts:
            try:
                out = target(*formed)
                last_err = None
                break
            except TypeError as e:
                last_err = e
                continue                 # the next shape may fit
            except Exception as e:
                raise FailSignal(f"{module}.{func} failed: {e}")
        if last_err is not None:
            raise FailSignal(f"{module}.{func} failed: {last_err}")
        if isinstance(out, (bytes, bytearray)):
            out = out.decode("utf-8", errors="replace")
        try:
            if name == "py_int":
                return int(out)
            if name == "py_float":
                return float(out)
            return str(out)
        except (TypeError, ValueError):
            raise FailSignal(
                f"{module}.{func} gave back something that is not a "
                f"{'whole number' if name == 'py_int' else 'decimal' if name == 'py_float' else 'text'}")
    if name == "code_at":
        t, i = args
        if i < 0 or i >= len(t):
            raise VelarisError("E602",
                f"position {i} is outside the text (it has {len(t)} "
                f"character(s))", line,
                fixes=["positions go from 0 to length - 1",
                       "check with length(...) before using code_at"])
        return ord(t[i])
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
        try:
            with open(str(args[0]), "w", encoding="utf-8") as fh:
                fh.write(to_text(args[1]))
            return None
        except OSError as e:
            raise VelarisError("E608",
                f"could not write '{args[0]}': {e.strerror or e}", line,
                fixes=["check the folder exists and is writable",
                       "or write somewhere else"])

    if name == "request":
        import json as _json
        import urllib.request
        import urllib.error
        method, url, body, headers_json = (str(a) for a in args)
        method = method.upper() or "GET"
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        try:
            headers = _json.loads(headers_json) if headers_json.strip() \
                else {}
        except Exception as e:
            raise FailSignal(f"the headers are not valid JSON: {e}")
        if not isinstance(headers, dict):
            raise FailSignal('the headers must be a JSON object, like '
                             '{"Accept": "application/json"}')
        headers = {str(k): str(v) for k, v in headers.items()}
        headers.setdefault("User-Agent", f"velaris/{VERSION}")
        data = body.encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                answer = {
                    "status": int(resp.status),
                    "body": resp.read(1 << 20).decode("utf-8",
                                                      errors="replace"),
                    "headers": {k: v for k, v in resp.headers.items()}}
        except urllib.error.HTTPError as e:      # a real answer
            answer = {
                "status": int(e.code),
                "body": e.read(1 << 20).decode("utf-8", errors="replace"),
                "headers": {k: v for k, v in (e.headers or {}).items()}}
        except Exception as e:            # say what happened, not how
            reason = "the address did not resolve"
            text = str(e).lower()
            if "timed out" in text or "timeout" in text:
                reason = "it did not answer in time"
            elif "refused" in text:
                reason = "the connection was refused"
            elif "certificate" in text or "ssl" in text:
                reason = "the certificate was not accepted"
            elif "unreachable" in text or "network" in text:
                reason = "the network is unreachable"
            raise FailSignal(f"cannot reach '{url}': {reason}")
        return _json.dumps(answer, ensure_ascii=False)
    if name in ("fetch", "post", "fetch_status"):
        import urllib.request
        import urllib.error
        url = str(args[0])
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        headers = {"User-Agent": f"velaris/{VERSION}"}
        data = None
        if name == "post":
            body = str(args[1])
            data = body.encode("utf-8")
            headers["Content-Type"] = (
                "application/json" if body.lstrip()[:1] in "{["
                else "text/plain; charset=utf-8")
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if name == "fetch_status":
                    return int(resp.status)
                return resp.read(1 << 20).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:      # a real answer, not silence
            if name == "fetch_status":
                return int(e.code)
            raise FailSignal(f"'{url}' answered with status {e.code}")
        except Exception:
            raise FailSignal(f"cannot reach '{url}'")
    if name == "args":
        return list(PROGRAM_ARGS)
    if name == "log":
        print(to_text(args[0]), file=sys.stderr)
        return None
    if name == "env":
        return os.environ.get(str(args[0]), str(args[1]))
    if name == "exit_with":
        code = int(args[0])
        if not 0 <= code <= 255:
            raise VelarisError("E408",
                f"an exit code must be between 0 and 255, not {code}",
                line, fixes=["0 means success; anything else means "
                             "something went wrong"])
        raise SystemExit(code)
    if name == "read_line":
        got = sys.stdin.readline()
        return got.rstrip("\n")
    if name == "format":
        template = str(args[0])
        pieces = template.split("{}")
        holes = len(pieces) - 1
        given = len(args) - 1
        if holes != given:
            raise VelarisError("E406",
                f"format has {holes} placeholder(s) but got {given} "
                f"value(s)", line,
                fixes=[f"pass exactly {holes} value(s) after the text",
                       "each {} in the text takes one value"])
        out = pieces[0]
        for piece, val in zip(pieces[1:], args[1:]):
            out += to_text(val) + piece
        return out
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
        if name in native:                 # machine code, C-like speed
            if TRACE["on"]:                # still visible when tracing
                fnn = table.get(name)
                trace_enter(name + " (native)",
                            fnn.params if fnn else [], args)
                out = native[name](*args)
                trace_leave(name + " (native)", out)
                return out
            return native[name](*args)
        fn = table.get(name)
        if fn is None:
            raise unknown_function(name, line, table)
        return call_function(fn, args, line)

    depth = [0]
    DEPTH_LIMIT = 2000        # deep enough for real recursion, shallow
                              # enough to report before Python's own
                              # stack gives out with a traceback
    # each Velaris frame costs several Python frames, so lift Python's
    # ceiling high enough that OUR limit is the one that fires
    if sys.getrecursionlimit() < DEPTH_LIMIT * 12:
        try:
            sys.setrecursionlimit(DEPTH_LIMIT * 12)
        except Exception:
            pass

    def call_function(fn, args: list, line: int):
        caught = None
        if isinstance(fn, Bound):
            caught, fn = fn.caught, fn.fn
        name = fn.name
        if depth[0] >= DEPTH_LIMIT:
            raise VelarisError("E609",
                f"'{name}' called itself {DEPTH_LIMIT} deep - this looks "
                f"like recursion that never stops", line,
                fixes=["make sure the recursive case moves toward the "
                       "base case",
                       "or rewrite it as a loop"])
        if len(args) != len(fn.params):
            raise VelarisError("E401",
                f"'{name}' expects {len(fn.params)} argument(s) but got {len(args)}",
                line, fixes=[f"pass exactly {len(fn.params)} argument(s)"])
        env = {p[0]: a for p, a in zip(fn.params, args)}
        if caught:
            for cn, cv in caught.items():
                env.setdefault(cn, cv)     # values carried in, read once
                                           # when the value was made
        # the snapshot exists so promises can see entry values; a
        # function with no promises was copying its whole scope on
        # every single call for nothing
        entry = dict(env) if (fn.requires or fn.ensures) else env

        def vals(expr, extra=None):
            scope = dict(entry)
            if extra is not None:
                scope["result"] = extra[0]
            names = sorted(n for n in expr_vars(expr) if n in scope)
            return ", ".join(f"{n} = {scope[n]}" for n in names)

        for expr, cline in fn.requires:
            if not eval_(expr, dict(entry)):
                raise VelarisError("E600",
                    f"broken promise: {nice_name(name)} requires "
                    f"{expr_str(expr)}  ({vals(expr)})", cline,
                    fixes=["check the value before calling this function",
                           "or loosen the promise if it is too strict"])

        retval = None
        trace_enter(name, fn.params, args)
        depth[0] += 1
        try:
            for stmt in fn.body:
                run(stmt, env)
        except ReturnSignal as r:
            retval = r.value
        except FailSignal as f:
            trace_leave(name, None, failed=str(f.reason))
            raise
        except VelarisError as e:
            trace_leave(name, None, failed=f"[{e.code}] {e.message}")
            raise blame(fn, e)
        finally:
            depth[0] -= 1
        trace_leave(name, retval)

        for expr, cline in fn.ensures:
            check_env = dict(entry)
            check_env["result"] = retval
            if not eval_(expr, check_env):
                raise VelarisError("E601",
                    f"broken promise: {nice_name(name)} ensures "
                    f"{expr_str(expr)}  ({vals(expr, (retval,))})", cline,
                    fixes=["the code does not keep this promise - fix the code",
                           "or fix the promise if it is wrong"])
        return retval

    def run(node, env):
        cls = node.__class__
        if cls is Assign:               # the body of every loop
            env[node.name] = eval_(node.value, env)
            return
        if cls is Let:
            env[node.name] = eval_(node.value, env)
            return
        if cls is Let:
            env[node.name] = eval_(node.value, env)
        elif cls is Return:
            raise ReturnSignal(None if node.value is None else eval_(node.value, env))
        elif cls is ExprStmt:
            eval_(node.expr, env)
        elif cls is FailStmt:
            raise FailSignal(eval_(node.value, env))
        elif cls is Check:
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
        elif cls is If:
            branch = node.then if eval_(node.cond, env) else node.other
            for s in branch:
                run(s, env)
        elif cls is While:
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
        elif cls is Assign:
            env[node.name] = eval_(node.value, env)

    _hot = (Num, FloatNum, Str, Bool)

    class Bound:
        """A function value carrying the values it was made with."""
        __slots__ = ("fn", "caught")

        def __init__(self, fn, caught):
            self.fn = fn
            self.caught = caught

    def eval_(node, env):
        cls = node.__class__
        if cls is Closure:
            fn = table[node.name]
            caught = {n: env[n] for n in node.free if n in env}
            return Bound(fn, caught) if caught else fn
        if cls is Var:                  # the commonest node by far
            name = node.name
            if name in env:
                return env[name]
            if name in table:
                return table[name]
            raise VelarisError("E402", f"unknown variable '{name}'",
                               node.line,
                               fixes=[f"declare it first: let {name} = ..."])
        if cls in _hot:                 # literals: the value is the node
            return node.value
        if cls is Num:  return node.value
        if cls is FloatNum: return node.value
        if cls is Neg:  return -eval_(node.value, env)
        if cls is TryExpr:
            return eval_(node.value, env)   # a failure keeps rising
        if cls is Str:  return node.value
        if cls is Bool: return node.value
        if cls is Var:
            if node.name in env:
                return env[node.name]
            if node.name in table:
                return table[node.name]        # a function, as a value
            raise VelarisError("E402", f"unknown variable '{node.name}'", node.line,
                              fixes=[f"declare it first: let {node.name} = ..."])
        if cls is Call:
            if node.name in env and isinstance(env[node.name],
                                               (Function, Bound)):
                return call_function(env[node.name],
                                     [eval_(a, env) for a in node.args],
                                     node.line)
            return call(node.name, [eval_(a, env) for a in node.args], node.line)
        if cls is Not:
            return not eval_(node.value, env)
        if cls is RecordLit:
            return RecordValue(node.name,
                               {f: eval_(v, env) for f, v in node.fields})
        if cls is FieldGet:
            return eval_(node.obj, env).fields[node.field]
        if cls is ListLit:
            return [eval_(i, env) for i in node.items]
        if cls is MapLit:
            return {eval_(k, env): eval_(v, env) for k, v in node.entries}
        if cls is BinOp:
            if node.op == "and":
                return eval_(node.left, env) and eval_(node.right, env)
            if node.op == "or":
                return eval_(node.left, env) or eval_(node.right, env)
            l, r = eval_(node.left, env), eval_(node.right, env)
            if node.op == "+":
                if isinstance(l, str) or isinstance(r, str):
                    return to_text(l) + to_text(r)
                return checked_int(l + r, "+", node.line)
            if node.op == "-":
                return checked_int(l - r, "-", node.line)
            if node.op == "*":
                return checked_int(l * r, "*", node.line)
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


def inspect_source(path: str, source: str | None = None, require_main: bool = False) -> dict:
    """Everything a reader wants to know about a program, as data.

    Used by 'velaris explain' and the browser inspector: for each
    function, what it may do (effects), what it promises, whether the
    promises are proven or left to runtime, and every error in place.
    """
    running = require_main
    report: dict = {"file": path, "functions": [], "errors": [],
                    "proofs": bool(HAVE_Z3), "version": VERSION}
    try:
        funcs, records = load_program(path, source)
    except VelarisError as e:
        report["errors"].append(json.loads(e.machine(path)))
        return report
    errors: list = []
    try:
        check_main(funcs, errors, running=running)
        check_effects(funcs, errors)
        if not errors:
            check_types(funcs, records, errors)
    except VelarisError as e:          # a raise instead of an append is
        errors.append(e)               # still one problem, not a crash
    proved: set = set()
    if not errors:
        try:
            check_proofs(funcs, records, errors, proved,
                         use_cache="--no-cache" not in sys.argv)
        except VelarisError as e:
            errors.append(e)
    seen_e = set()
    for e in errors:                # one problem, one message, everywhere
        key = (e.code, e.file or path, e.line, e.message)
        if key in seen_e:
            continue
        seen_e.add(key)
        report["errors"].append(json.loads(e.machine(path)))
    bad_lines = {e.line for e in errors}
    for f in funcs:
        if f.name.startswith("fn#"):
            continue                     # lifted lambda: shown in place
        report["functions"].append({
            "name": f.name,
            "line": f.line,
            "params": [{"name": n, "type": t} for n, t in f.params],
            "returns": f.return_type or "nothing",
            "effects": sorted(f.effects) or [],
            "can_fail": bool(f.can_fail),
            "generic": list(f.type_vars),
            "requires": [expr_str(e) for e, _ in f.requires],
            "ensures": [expr_str(e) for e, _ in f.ensures],
            "status": ("error" if f.line in bad_lines else
                       "proven" if f.name in proved and HAVE_Z3 else
                       "checked at runtime" if (f.requires or f.ensures)
                       else "no promises"),
            "file": f.src_file or path,
        })
    return report


def editor_answer(method: str, params: dict, text: str, uri: str):
    """Hover, go-to-definition, proof lenses and an outline."""
    import urllib.parse
    path = urllib.parse.unquote(uri.replace("file://", ""))
    if os.name == "nt" and path.startswith("/"):
        path = path[1:]
    try:
        funcs, records = load_program(path, text)
    except VelarisError:
        return None if "codeLens" not in method else []

    proven: set = set()
    if "codeLens" in method:
        errors: list = []
        check_effects(funcs, errors)
        check_types(funcs, records, errors)
        if not errors:
            try:
                check_proofs(funcs, records, errors, proven, use_cache=True)
            except Exception:
                pass

    mine = [f for f in funcs
            if not f.src_file or os.path.abspath(f.src_file)
            == os.path.abspath(path)]

    def signature(f) -> str:
        ps = ", ".join(f"{n}: {t}" for n, t in f.params)
        out = f"fn {f.name}({ps})"
        if f.return_type and f.return_type != "Unit":
            out += f" -> {f.return_type}"
        if f.type_vars:
            out += " for any " + ", ".join(f.type_vars)
        if f.can_fail:
            out += " or fail"
        if f.effects:
            out += " uses " + ", ".join(sorted(f.effects))
        return out

    if method == "textDocument/codeLens":
        lenses = []
        for f in mine:
            if f.name.startswith("fn#"):
                continue
            if f.requires or f.ensures:
                title = ("promises proven before running"
                         if f.name in proven
                         else "promises checked while running")
            elif f.effects:
                title = "may perform: " + ", ".join(sorted(f.effects))
            else:
                title = "pure"
            if f.can_fail:
                title += " - can fail"
            lenses.append({
                "range": {"start": {"line": max(f.line - 1, 0),
                                    "character": 0},
                          "end": {"line": max(f.line - 1, 0),
                                  "character": 1}},
                "command": {"title": title, "command": ""}})
        return lenses

    if method == "textDocument/rename":
        line_no = params["position"]["line"]
        col = params["position"]["character"]
        new_name = params.get("newName", "")
        lines = text.splitlines()
        if line_no >= len(lines) or not new_name:
            return None
        row = lines[line_no]
        start, end = col, col
        while start > 0 and (row[start - 1].isalnum()
                             or row[start - 1] == "_"):
            start -= 1
        while end < len(row) and (row[end].isalnum() or row[end] == "_"):
            end += 1
        old_name = row[start:end]
        if not old_name:
            return None
        here = {f.name for f in funcs
                if not f.src_file
                or os.path.abspath(f.src_file) == os.path.abspath(path)}
        if old_name not in here:
            return None            # only names this file owns
        import re as _re
        pattern = _re.compile(r"\b" + _re.escape(old_name) + r"\b")
        edits = []
        for i, row_text in enumerate(lines):
            code = row_text.split("//")[0]        # leave comments alone
            for m in pattern.finditer(code):
                edits.append({
                    "range": {"start": {"line": i, "character": m.start()},
                              "end": {"line": i, "character": m.end()}},
                    "newText": new_name})
        if not edits:
            return None
        return {"changes": {uri: edits}}

    if method == "textDocument/completion":
        items = []
        for f in funcs:
            if f.name.startswith("fn#"):
                continue
            items.append({"label": f.name, "kind": 3,
                          "detail": signature(f),
                          "documentation": " ".join(
                              [f"requires {expr_str(e)}"
                               for e, _ in f.requires]
                              + [f"ensures {expr_str(e)}"
                                 for e, _ in f.ensures]) or None})
        for name, info in BUILTINS.items():
            eff = ", ".join(sorted(info["effects"])) or "pure"
            fail = " (can fail)" if name in FALLIBLE_BUILTINS else ""
            items.append({"label": name, "kind": 3,
                          "detail": f"builtin -> {info['ret']}{fail}",
                          "documentation": f"effects: {eff}"})
        for word in ("fn", "let", "return", "if", "else", "while", "for",
                     "uses", "requires", "ensures", "invariant", "record",
                     "import", "fail", "check", "try", "or fail",
                     "for any T"):
            items.append({"label": word, "kind": 14})
        return {"isIncomplete": False, "items": items}

    if method == "textDocument/documentSymbol":
        return [{"name": f.name, "kind": 12,
                 "range": {"start": {"line": max(f.line - 1, 0),
                                     "character": 0},
                           "end": {"line": max(f.line - 1, 0),
                                   "character": 80}},
                 "selectionRange": {
                     "start": {"line": max(f.line - 1, 0), "character": 0},
                     "end": {"line": max(f.line - 1, 0), "character": 80}},
                 "detail": signature(f)}
                for f in mine if not f.name.startswith("fn#")]

    # hover and definition both need the word under the cursor
    line_no = params["position"]["line"]
    col = params["position"]["character"]
    lines = text.splitlines()
    if line_no >= len(lines):
        return None
    row = lines[line_no]
    start = col
    while start > 0 and (row[start - 1].isalnum()
                         or row[start - 1] in "_."):
        start -= 1
    end = col
    while end < len(row) and (row[end].isalnum() or row[end] in "_."):
        end += 1
    word = row[start:end]
    if not word:
        return None

    table = {f.name: f for f in funcs}
    found = table.get(word)

    if method == "textDocument/definition":
        if found is None or found.name.startswith("fn#"):
            return None
        target = found.src_file or path
        return {"uri": "file://" + os.path.abspath(target).replace(
                    "\\", "/"),
                "range": {"start": {"line": max(found.line - 1, 0),
                                    "character": 0},
                          "end": {"line": max(found.line - 1, 0),
                                  "character": 1}}}

    if found is not None:
        parts = [signature(found)]
        for e, _ in found.requires:
            parts.append(f"    requires {expr_str(e)}")
        for e, _ in found.ensures:
            parts.append(f"    ensures {expr_str(e)}")
        body = ["```velaris", "\n".join(parts), "```"]
        if found.src_file and os.path.abspath(found.src_file) != \
                os.path.abspath(path):
            body.append(f"from `{os.path.basename(found.src_file)}`")
        return {"contents": {"kind": "markdown",
                             "value": "\n".join(body)}}

    if word in BUILTINS:
        info = BUILTINS[word]
        eff = ", ".join(sorted(info["effects"])) or "pure"
        fail = " (can fail)" if word in FALLIBLE_BUILTINS else ""
        return {"contents": {"kind": "markdown", "value":
                f"**{word}**{fail}\n\n"
                f"takes: {', '.join(info['types']) or 'nothing'}  \n"
                f"gives: {info['ret']}  \n"
                f"effects: {eff}"}}
    return None


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
                "capabilities": {
                    "textDocumentSync": {
                        "openClose": True, "change": 1,
                        "save": {"includeText": True}},
                    "hoverProvider": True,
                    "renameProvider": {"prepareProvider": False},
                    "completionProvider": {
                        "triggerCharacters": [".", " "]},
                    "definitionProvider": True,
                    "codeLensProvider": {"resolveProvider": False},
                    "documentSymbolProvider": True},
                "serverInfo": {"name": "velaris", "version": VERSION}}})
        elif method in ("textDocument/hover", "textDocument/definition",
                        "textDocument/codeLens", "textDocument/completion",
                        "textDocument/rename",
                        "textDocument/documentSymbol"):
            uri = params["textDocument"]["uri"]
            text = docs.get(uri, "")
            result = editor_answer(method, params, text, uri)
            send({"jsonrpc": "2.0", "id": msg["id"], "result": result})
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
            elif (t.text == "(" and prev.kind == "KEYWORD"
                    and prev.text == "fn"):
                space = False              # lambda value: fn(x: Int)
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
        # a contract sits between the signature and the body, where no
        # brace has opened yet - indent it under the signature it belongs
        # to rather than flattening it to the margin
        if line_toks[0].text in ("requires", "ensures", "invariant"):
            d += 1
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


MANIFEST = "velaris.toml"


def _manifest_read() -> list:
    """Every dependency, as (name, source, sha256)."""
    if not os.path.exists(MANIFEST):
        return []
    import re as _re
    text = open(MANIFEST, encoding="utf-8").read()
    return [(m.group(1), m.group(2), m.group(3)) for m in _re.finditer(
        r'^(\w[\w.-]*)\s*=\s*\{\s*source\s*=\s*"([^"]*)"\s*,\s*'
        r'sha256\s*=\s*"([0-9a-f]{64})"\s*\}\s*$', text, _re.M)]


def _manifest_write(deps: list) -> None:
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("# Velaris dependencies. Every library is vendored into\n"
                "# lib/ and recorded here with the exact bytes it had, so\n"
                "# 'velaris verify' can tell you if anything changed.\n\n")
        f.write("[dependencies]\n")
        for name, source, digest in sorted(deps):
            f.write(f'{name} = {{ source = "{source}", '
                    f'sha256 = "{digest}" }}\n')


def packages(argv: list) -> int:
    import hashlib
    cmd = argv[0]
    deps = _manifest_read()

    if cmd == "deps":
        if not deps:
            print("no dependencies yet - add one with: "
                  "velaris add <url or path>")
            return 0
        print(f"{len(deps)} dependenc(ies), vendored in lib/")
        for name, source, digest in deps:
            here = os.path.join("lib", name + ".vel")
            mark = "ok " if os.path.exists(here) else "MISSING"
            print(f"  [{mark}] {name}\n      from {source}"
                  f"\n      {digest[:16]}...")
        return 0

    if cmd == "verify":
        if not deps:
            print("nothing to verify")
            return 0
        bad = 0
        for name, source, digest in deps:
            path = os.path.join("lib", name + ".vel")
            if not os.path.exists(path):
                print(f"  MISSING  {name} (re-add it: velaris add {source})")
                bad += 1
                continue
            now = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if now != digest:
                print(f"  CHANGED  {name} - the file is not what was "
                      f"recorded")
                bad += 1
            else:
                print(f"  ok       {name}")
        if bad:
            print(f"\n{bad} problem(s). A library that changed under you "
                  f"is worth looking at before trusting it.")
            return 1
        print(f"\nall {len(deps)} dependenc(ies) are exactly as recorded")
        return 0

    if len(argv) < 2:                     # add
        print("usage: velaris add <url or path> [as <name>]",
              file=sys.stderr)
        return 1
    source = argv[1]
    name = None
    if len(argv) >= 4 and argv[2] == "as":
        name = argv[3]
    if name is None:
        name = os.path.basename(source)
        if name.endswith(".vel"):
            name = name[:-4]
    if not name or "/" in name or "\\" in name:
        print(f"'{name}' is not a usable library name", file=sys.stderr)
        return 1

    if source.startswith("http://") or source.startswith("https://"):
        import urllib.request
        try:
            with urllib.request.urlopen(source, timeout=20) as resp:
                data = resp.read(4 << 20)
        except Exception as e:
            print(f"could not fetch {source}: {e}", file=sys.stderr)
            return 1
    else:
        if not os.path.exists(source):
            print(f"no such file: {source}", file=sys.stderr)
            return 1
        data = open(source, "rb").read()

    text = data.decode("utf-8", errors="replace")
    os.makedirs("lib", exist_ok=True)
    path = os.path.join("lib", name + ".vel")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    rep_ = inspect_source(path)           # a library must compile
    if rep_["errors"]:
        os.remove(path)
        print(f"'{name}' does not compile, so it was not added:",
              file=sys.stderr)
        for e in rep_["errors"][:3]:
            print(f"  line {e['line']}: [{e['code']}] {e['message']}",
                  file=sys.stderr)
        return 1

    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    deps = [d for d in deps if d[0] != name] + [(name, source, digest)]
    _manifest_write(deps)
    own = [f for f in rep_["functions"]
           if os.path.abspath(f["file"]) == os.path.abspath(path)]
    proven = sum(1 for f in own if f["status"] == "proven")
    effs = sorted({e for f in own for e in f["effects"]})
    print(f"added {name} -> lib/{name}.vel")
    print(f"  {len(own)} function(s), {proven} with proven promises")
    print(f"  performs: {', '.join(effs) if effs else 'nothing'}")
    print(f'  use it with: import "lib/{name}.vel" as {name}')
    return 0


def gather_sources(entry: str) -> dict:
    """The entry file and everything it imports, by relative path."""
    seen: dict = {}
    root = os.path.dirname(os.path.abspath(entry)) or "."

    def walk(path: str) -> None:
        ap = os.path.abspath(path)
        rel = os.path.relpath(ap, root).replace("\\", "/")
        if rel in seen:
            return
        if not os.path.exists(ap):
            return                       # the stdlib is bundled separately
        text = open(ap, encoding="utf-8").read()
        seen[rel] = text
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("import "):
                continue
            piece = line[len("import "):].strip()
            if piece.startswith('"'):
                target = piece[1:piece.index('"', 1)]
                walk(os.path.join(os.path.dirname(ap), target))
    walk(entry)
    return seen


def build_program(argv: list) -> int:
    """Turn a Velaris program into one file anyone can run."""
    if not argv or argv[0].startswith("-"):
        print("usage: velaris build program.vel [-o name]",
              file=sys.stderr)
        return 1
    entry = argv[0]
    if not os.path.exists(entry):
        print(f"no such file: {entry}", file=sys.stderr)
        return 1
    out_name = os.path.splitext(os.path.basename(entry))[0]
    if "-o" in argv:
        out_name = argv[argv.index("-o") + 1]

    report = inspect_source(entry)       # never ship what does not compile
    if report["errors"]:
        print(f"{entry} does not compile, so it was not built:",
              file=sys.stderr)
        for e in report["errors"][:5]:
            print(f"  line {e['line']}: [{e['code']}] {e['message']}",
                  file=sys.stderr)
        return 1

    try:
        import PyInstaller                       # noqa: F401
    except ImportError:
        print("building needs PyInstaller:\n  pip install pyinstaller",
              file=sys.stderr)
        return 1

    import json as _json
    import shutil
    import subprocess
    import tempfile

    sources = gather_sources(entry)
    entry_rel = os.path.relpath(os.path.abspath(entry),
                                os.path.dirname(os.path.abspath(entry)))
    entry_rel = entry_rel.replace("\\", "/")
    work = tempfile.mkdtemp(prefix="velaris-build-")
    launcher = os.path.join(work, f"{out_name}.py")
    with open(launcher, "w", encoding="utf-8") as f:
        f.write("# Generated by velaris build - a Velaris program,\n"
                "# carrying its own compiler.\n"
                "import os, sys, tempfile\n"
                f"SOURCES = {_json.dumps(sources)}\n"
                f"ENTRY = {_json.dumps(entry_rel)}\n"
                "import velaris\n"
                "def main():\n"
                "    here = tempfile.mkdtemp(prefix='velaris-run-')\n"
                "    for rel, text in SOURCES.items():\n"
                "        p = os.path.join(here, rel)\n"
                "        os.makedirs(os.path.dirname(p), exist_ok=True)\n"
                "        open(p, 'w', encoding='utf-8').write(text)\n"
                "    sys.argv = [sys.argv[0], os.path.join(here, ENTRY)]"
                " + sys.argv[1:]\n"
                "    return velaris.main()\n"
                "sys.exit(main())\n")

    here = os.path.dirname(os.path.abspath(__file__))
    sep = ";" if os.name == "nt" else ":"
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile",
           "--name", out_name, "--distpath", os.path.abspath("."),
           "--workpath", os.path.join(work, "build"),
           "--specpath", work, "--noconfirm",
           "--paths", here,
           "--add-data", f"{os.path.join(here, 'stdlib')}{sep}stdlib"]
    for extra in ("z3", "llvmlite"):
        try:
            __import__(extra)
            cmd += ["--collect-all", extra]
        except ImportError:
            pass
    cmd.append(launcher)
    if "--for-everyone" in argv:
        wf = os.path.join(".github", "workflows",
                          f"build-{out_name}.yml")
        os.makedirs(os.path.dirname(wf), exist_ok=True)
        with open(wf, "w", encoding="utf-8") as f:
            f.write(f"""# Built by velaris build --for-everyone.
# One machine cannot build for other machines, so three build for you.
name: build {out_name}

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: windows-latest
            asset: {out_name}-windows.exe
          - os: ubuntu-latest
            asset: {out_name}-linux
          - os: macos-latest
            asset: {out_name}-macos
    runs-on: ${{{{ matrix.os }}}}
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install "velaris-lang[full]" pyinstaller
      - run: velaris build {entry} -o {out_name}
      - shell: bash
        run: |
          for f in {out_name} {out_name}.exe; do
            [ -f "$f" ] && mv "$f" "${{{{ matrix.asset }}}}"
          done
      - uses: softprops/action-gh-release@v2
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: ${{{{ matrix.asset }}}}
""")
        print(f"wrote {wf}")
        print("commit it, then push a tag: three machines will build "
              f"{out_name} for Windows, Linux and macOS")
        return 0

    print(f"building {out_name} from {entry} "
          f"({len(sources)} file(s), this takes a minute)...")
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        print(done.stdout[-2000:], file=sys.stderr)
        print(done.stderr[-2000:], file=sys.stderr)
        print("the build failed - the output above is from PyInstaller",
              file=sys.stderr)
        return 1
    shutil.rmtree(work, ignore_errors=True)
    made = out_name + (".exe" if os.name == "nt" else "")
    size = os.path.getsize(made) / (1024 * 1024) if os.path.exists(made) else 0
    print(f"built ./{made}  ({size:.0f} MB)")
    print("that file is the whole program - no Python, no Velaris, "
          "nothing to install")
    return 0


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
    if argv[:1] in (["add"], ["deps"], ["verify"]):
        return packages(argv)
    if argv[:1] == ["proofs"]:
        target = argv[1] if len(argv) > 1 and not argv[1].startswith("-") \
            else "."
        files = []
        if os.path.isdir(target):
            files = sorted(
                os.path.join(dp, f)
                for dp, _, fns in os.walk(target) for f in fns
                if f.endswith(".vel") and ".velaris" not in dp)
        elif os.path.exists(target):
            files = [target]
        if not files:
            print(f"no .vel files under '{target}'", file=sys.stderr)
            return 1
        rows, totals = [], {"proven": 0, "runtime": 0, "plain": 0,
                            "errors": 0}
        for path in files:
            rep_ = inspect_source(path)
            own = [f for f in rep_["functions"]
                   if os.path.abspath(f["file"]) == os.path.abspath(path)]
            counts = {"proven": 0, "runtime": 0, "plain": 0}
            for f in own:
                if f["status"] == "proven":
                    counts["proven"] += 1
                elif f["status"] == "checked at runtime":
                    counts["runtime"] += 1
                else:
                    counts["plain"] += 1
            for k in counts:
                totals[k] += counts[k]
            totals["errors"] += len(rep_["errors"])
            rows.append({"file": path, **counts,
                         "errors": len(rep_["errors"])})
        promising = totals["proven"] + totals["runtime"]
        share = (100.0 * totals["proven"] / promising) if promising else 0.0
        if "--json" in argv:
            print(json.dumps({"files": rows, "totals": totals,
                              "proven_share": round(share, 1)}, indent=2))
        elif "--detail" in argv:
            print(f"{len(files)} file(s)")
            print("-" * 62)
            for path in files:
                rep_ = inspect_source(path)
                own = [f for f in rep_["functions"]
                       if os.path.abspath(f["file"])
                       == os.path.abspath(path)
                       and (f["requires"] or f["ensures"])]
                if not own:
                    continue
                print(path)
                for f in own:
                    mark = ("proven " if f["status"] == "proven"
                            else "runtime")
                    print(f"    [{mark}] {f['name']}")
                    if f["status"] != "proven":
                        for r in f["requires"]:
                            print(f"                needs    {r}")
                        for e in f["ensures"]:
                            print(f"                promises {e}")
            print("-" * 62)
            print(f"{totals['proven']} of {promising} proven "
                  f"({share:.0f}%)")
        else:
            print(f"{len(files)} file(s)")
            print("-" * 62)
            for r in rows:
                if not (r["proven"] or r["runtime"] or r["errors"]):
                    continue
                mark = "!" if r["errors"] else " "
                print(f"{mark} {r['file']}")
                bits = []
                if r["proven"]:
                    bits.append(f"{r['proven']} proven")
                if r["runtime"]:
                    bits.append(f"{r['runtime']} checked while running")
                if r["errors"]:
                    bits.append(f"{r['errors']} problem(s)")
                print("    " + ", ".join(bits))
            print("-" * 62)
            print(f"{totals['proven']} of {promising} promise-carrying "
                  f"function(s) proven before running "
                  f"({share:.0f}%)")
            if totals["plain"]:
                print(f"{totals['plain']} function(s) make no promises")
            if totals["errors"]:
                print(f"{totals['errors']} problem(s) found")
        if "--min" in argv:
            want = float(argv[argv.index("--min") + 1])
            if share < want:
                print(f"\nproven share {share:.0f}% is below the "
                      f"required {want:.0f}%", file=sys.stderr)
                return 1
        return 1 if totals["errors"] else 0
    if argv[:1] == ["serve"]:
        # A local HTTP door, so a program in ANY language can check,
        # audit and sandbox-run Velaris - not only Python and not only
        # MCP clients. Bound to localhost unless told otherwise, and it
        # says what it will and will not do before it starts.
        import http.server
        import urllib.parse

        port = 8787
        host = "127.0.0.1"
        if "--port" in argv:
            port = int(argv[argv.index("--port") + 1])
        if "--host" in argv:
            host = argv[argv.index("--host") + 1]
        max_allow = set(ALL_EFFECTS)
        if "--max-allow" in argv:
            asked = argv[argv.index("--max-allow") + 1]
            max_allow = {n.strip() for n in asked.split(",") if n.strip()}
            unknown = max_allow - set(ALL_EFFECTS)
            if unknown:
                print(f"not an effect: {', '.join(sorted(unknown))}",
                      file=sys.stderr)
                return 2

        import velaris as _self          # the library half, reused whole

        class Door(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):   # quiet unless something matters
                pass

            def answer(self, code, payload):
                body = json.dumps(payload, indent=2).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path.rstrip("/") in ("", "/health"):
                    return self.answer(200, {
                        "velaris": VERSION, "prover": bool(HAVE_Z3),
                        "max_allow": sorted(max_allow),
                        "endpoints": ["POST /check", "POST /audit",
                                      "POST /run", "GET /card"]})
                if self.path.rstrip("/") == "/card":
                    return self.answer(200, {"card": _self.card()})
                return self.answer(404, {"error": "no such endpoint"})

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                if length > 2_000_000:
                    return self.answer(413, {"error": "that is too large"})
                try:
                    body = json.loads(self.rfile.read(length) or b"{}")
                except json.JSONDecodeError as e:
                    return self.answer(400, {"error": f"bad JSON: {e}"})
                source = body.get("source", "")
                if not isinstance(source, str) or not source.strip():
                    return self.answer(400,
                                       {"error": "send {\"source\": ...}"})
                where = urllib.parse.urlparse(self.path).path.rstrip("/")
                try:
                    if where == "/check":
                        return self.answer(
                            200, _self.check(source).as_dict())
                    if where == "/audit":
                        return self.answer(
                            200, _self.audit(source).as_dict())
                    if where == "/run":
                        asked = set(body.get("allow") or ["io"])
                        refused = asked - max_allow
                        if refused:
                            return self.answer(403, {
                                "error": "this server does not grant "
                                         + ", ".join(sorted(refused)),
                                "max_allow": sorted(max_allow)})
                        out = _self.run(
                            source, allow=asked,
                            stdin=body.get("stdin", ""),
                            args=body.get("args") or [],
                            timeout=float(body.get("timeout") or 30),
                            max_memory_mb=int(body.get("max_memory_mb")
                                              or 512))
                        payload = out.as_dict()
                        payload["allowed"] = sorted(asked)
                        return self.answer(200, payload)
                except Exception as e:
                    return self.answer(500,
                                       {"error": f"{type(e).__name__}: {e}"})
                return self.answer(404, {"error": "no such endpoint"})

        print(f"velaris {VERSION} listening on http://{host}:{port}")
        print(f"  POST /check /audit /run   GET /card /health")
        print(f"  grants at most: {', '.join(sorted(max_allow)) or 'nothing'}"
              f"   (--max-allow io to narrow it)")
        if host not in ("127.0.0.1", "localhost"):
            print("  WARNING: not bound to localhost. This endpoint RUNS "
                  "programs; do not expose it to a network you do not "
                  "control.", file=sys.stderr)
        if "ffi" in max_allow:
            print("  note: ffi is grantable here, which means a caller "
                  "can do anything Python can. --max-allow io,fs is "
                  "safer for a shared machine.")
        try:
            http.server.ThreadingHTTPServer((host, port), Door)\
                .serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
        return 0

    if argv[:1] == ["mcp-install"]:
        here = os.path.dirname(os.path.abspath(__file__))
        for where in (here, os.path.join(here, "..")):
            script = os.path.join(where, "velaris_mcp_install.py")
            if os.path.exists(script):
                sys.path.insert(0, where)
                import velaris_mcp_install
                return velaris_mcp_install.main(argv[1:])
        try:
            import velaris_mcp_install
            return velaris_mcp_install.main(argv[1:])
        except ImportError:
            print("the installer is not alongside this compiler; get it "
                  "from https://github.com/gowrishankar-infra/velaris-lang",
                  file=sys.stderr)
            return 1

    if argv[:1] == ["card"]:
        here = os.path.dirname(os.path.abspath(__file__))
        for where in (os.path.join(here, "LLM.md"),
                      os.path.join(here, "..", "LLM.md")):
            if os.path.exists(where):
                sys.stdout.write(open(where, encoding="utf-8").read())
                return 0
        print("LLM.md is not installed alongside the compiler; read it at "
              "https://github.com/gowrishankar-infra/velaris-lang/blob/"
              "main/LLM.md", file=sys.stderr)
        return 1

    if argv[:1] == ["audit"]:
        if len(argv) < 2:
            print("usage: velaris audit program.vel", file=sys.stderr)
            return 1
        target = argv[1]
        if not os.path.exists(target):
            print(f"no such file: {target}", file=sys.stderr)
            return 1
        report = inspect_source(target)
        own = [f for f in report["functions"]
               if os.path.abspath(f["file"]) == os.path.abspath(target)]
        outside = sorted({e for f in own for e in f["effects"]})
        promising = [f for f in own if f["requires"] or f["ensures"]]
        proven = [f for f in promising if f["status"] == "proven"]
        runtime = [f for f in promising if f["status"] != "proven"]
        reaching = [f for f in own if f["effects"]]
        fallible = [f for f in own if f["can_fail"]]

        if "--json" in argv:
            print(json.dumps({
                "file": target,
                "compiles": not report["errors"],
                "errors": report["errors"],
                "effects": outside,
                "functions": len(own),
                "proven": [f["name"] for f in proven],
                "checked_at_runtime": [f["name"] for f in runtime],
                "reaching_outside": {f["name"]: sorted(f["effects"])
                                     for f in reaching},
                "can_fail": [f["name"] for f in fallible],
                "safe_command": (f"velaris {target} --allow "
                                 + (",".join(outside) or "''")),
            }, indent=2))
            return 1 if report["errors"] else 0

        print(f"AUDIT  {target}")
        print("=" * 62)
        if report["errors"]:
            print(f"This does not compile ({len(report['errors'])} "
                  f"problem(s)). Do not run it.")
            for e in report["errors"][:5]:
                print(f"  line {e['line']}: [{e['code']}] {e['message']}")
            return 1

        print("WHAT IT CAN TOUCH")
        if not outside:
            print("  nothing. This program cannot reach the console, the")
            print("  disk, the network, the clock, randomness or Python.")
        else:
            words = {"io": "the console", "fs": "files",
                     "net": "the network", "clock": "the time",
                     "rand": "randomness", "ffi": "Python, and so "
                                                  "anything Python can do"}
            for e in outside:
                print(f"  {e:<6} {words.get(e, e)}")
            print()
            print("  reached by:")
            for f in reaching:
                print(f"    {f['name']} ({', '.join(sorted(f['effects']))})")
        print()

        print("WHAT IT PROMISES")
        if not promising:
            print("  nothing. No function here carries a contract.")
        else:
            for f in proven:
                print(f"  [proven ] {f['name']}")
                for e in f["ensures"]:
                    print(f"              always: {e}")
            for f in runtime:
                print(f"  [runtime] {f['name']}")
                for e in f["ensures"]:
                    print(f"              claims: {e}")
            share = 100 * len(proven) / len(promising)
            print()
            print(f"  {len(proven)} of {len(promising)} proven before "
                  f"running ({share:.0f}%); the rest are checked while "
                  f"it runs.")
        print()

        if fallible:
            print("WHAT CAN FAIL")
            for f in fallible:
                print(f"  {f['name']}")
            print()

        print("HOW TO RUN IT SAFELY")
        budget = ",".join(outside)
        if budget:
            print(f"  velaris {target} --allow {budget}")
            print("  Anything it did not declare is refused while it runs.")
        else:
            print(f"  velaris {target} --allow ''")
            print("  It needs no permissions at all.")
        if "ffi" in outside:
            print()
            print("  NOTE: this program calls Python, which means it can")
            print("  do anything Python can. An effect budget does not")
            print("  contain that. Read the code before running it.")
        return 0

    if argv[:1] == ["clean"]:
        import shutil
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR, ignore_errors=True)
            print(f"removed {CACHE_DIR}/ - the next run proves everything "
                  f"again")
        else:
            print("nothing to clean")
        return 0
    if argv[:1] == ["build"]:
        return build_program(argv[1:])
    if argv[:1] == ["trace"]:
        if len(argv) < 2:
            print("usage: velaris trace program.vel", file=sys.stderr)
            return 1
        TRACE["on"] = True
        sys.argv = [sys.argv[0]] + argv[1:]      # run it normally
        return main()
    if argv[:1] == ["test"]:
        if len(argv) < 2:
            print("usage: velaris test program.vel", file=sys.stderr)
            return 1
        target = argv[1]
        try:
            funcs, records = load_program(target)
            errs: list = []
            check_effects(funcs, errs)
            check_types(funcs, records, errs)
            if not errs:
                check_proofs(funcs, records, errs)
            if errs:
                for e in errs:
                    print(e.human(target), file=sys.stderr)
                return 1
        except VelarisError as e:
            print(e.human(target), file=sys.stderr)
            return 1
        tests = [f for f in funcs
                 if f.name.startswith("test_") and not f.params
                 and f.src_file == target]
        if not tests:
            print(f"no tests in {target} - name a function test_something "
                  f"and return true when it passes")
            return 1
        native = {} if "--no-native" in argv else compile_native(funcs)
        rt = build_runtime(funcs, native)
        passed = 0
        for t in tests:
            label = t.name[len("test_"):].replace("_", " ")
            try:
                got = rt["call"](t.name, [], t.line)
                if got is True:
                    print(f"  PASS  {label}")
                    passed += 1
                else:
                    print(f"  FAIL  {label}   (returned {to_text(got)})")
            except VelarisError as e:
                print(f"  FAIL  {label}   [{e.code}] {e.message}")
            except FailSignal as e:
                print(f"  FAIL  {label}   failed: {e.reason}")
        print(f"\n{passed}/{len(tests)} passed")
        return 0 if passed == len(tests) else 1
    if argv[:1] == ["check"]:
        if len(argv) < 2:
            print("usage: velaris check program.vel", file=sys.stderr)
            return 1
        bad = 0
        strict = "--strict" in argv
        for target in [a for a in argv[1:] if not a.startswith("-")]:
            rep_ = inspect_source(target)
            if rep_["errors"]:
                bad += 1
                if "--json" in argv:
                    print(json.dumps(rep_["errors"], indent=2))
                else:
                    for e in rep_["errors"]:
                        print(f"{target}:{e['line']}: [{e['code']}] "
                              f"{e['message']}", file=sys.stderr)
            else:
                own = [f for f in rep_["functions"]
                       if os.path.abspath(f["file"])
                       == os.path.abspath(target)]
                proven = sum(1 for f in own if f["status"] == "proven")
                # --strict: "it compiled" should mean "every promise it
                # makes was proven", not "proven or hoped for". Without
                # the flag an unprovable promise degrades to a runtime
                # check, which keeps the language usable with no solver
                # installed - but that is a choice about the DEFAULT,
                # and someone who wants the stronger reading should be
                # able to ask for it.
                if strict:
                    if not rep_["proofs"]:
                        bad += 1
                        print(f"{target}: --strict needs the prover "
                              f"(pip install z3-solver)", file=sys.stderr)
                        continue
                    fell_back = [f for f in own
                                 if (f["requires"] or f["ensures"])
                                 and f["status"] != "proven"]
                    if fell_back:
                        bad += 1
                        print(f"{target}: {len(fell_back)} promise(s) "
                              f"could not be proven, and --strict does "
                              f"not accept runtime checks:",
                              file=sys.stderr)
                        for f in fell_back:
                            print(f"  {f['name']}", file=sys.stderr)
                            for e in f["ensures"]:
                                print(f"      promises {e}",
                                      file=sys.stderr)
                            for r in f["requires"]:
                                print(f"      needs    {r}",
                                      file=sys.stderr)
                        print("  either simplify them until they prove, "
                              "or drop --strict and accept the runtime "
                              "check", file=sys.stderr)
                        continue
                if "--json" not in argv:
                    note = ("" if rep_["proofs"]
                            else "  (no z3: runtime checks)")
                    if strict:
                        note = "  (--strict: every promise proven)"
                    print(f"{target}: ok - {len(own)} function(s), "
                          f"{proven} with proven promises{note}")
        return 1 if bad else 0
    if argv[:1] == ["explain"]:
        if len(argv) < 2:
            print("usage: velaris explain program.vel", file=sys.stderr)
            return 1
        target = argv[1]
        if os.path.isdir(target):
            vels = sorted(
                os.path.join(dp, f)
                for dp, _, fns in os.walk(target) for f in fns
                if f.endswith(".vel"))
            if not vels:
                print(f"no .vel files under '{target}'", file=sys.stderr)
                return 1
            print(f"{len(vels)} file(s) under {target}")
            print("=" * 62)
            worst = 0
            for v in vels:
                r = inspect_source(v)
                own = [f for f in r["functions"]
                       if os.path.abspath(f["file"]) == os.path.abspath(v)]
                proven = sum(1 for f in own if f["status"] == "proven")
                effs = sorted({e for f in own for e in f["effects"]})
                mark = "!" if r["errors"] else " "
                print(f"{mark} {v}")
                print(f"    {len(own)} function(s), {proven} proven"
                      f"   performs: "
                      f"{', '.join(effs) if effs else 'nothing'}")
                for e in r["errors"]:
                    worst = 1
                    print(f"    line {e['line']}: [{e['code']}] "
                          f"{e['message'][:70]}")
            return worst
        rep_ = inspect_source(target)
        if "--json" in argv:
            print(json.dumps(rep_, indent=2))
            return 0 if not rep_["errors"] else 1
        print(f"{rep_['file']}  -  velaris {rep_['version']}")
        print("=" * 62)
        if not rep_["proofs"]:
            print("note: z3-solver is not installed, so promises are "
                  "checked while running\n")
        entry = os.path.abspath(rep_["file"])
        mine, imported = [], {}
        for f in rep_["functions"]:
            if os.path.abspath(f["file"]) == entry:
                mine.append(f)
            else:
                imported.setdefault(f["file"], []).append(f)

        def show(f):
            ps = ", ".join(f"{p['name']}: {p['type']}" for p in f["params"])
            print(f"\nfn {f['name']}({ps}) -> {f['returns']}")
            print(f"  line {f['line']}   [{f['status']}]")
            if f["effects"]:
                print(f"  may perform: {', '.join(f['effects'])}")
            else:
                print("  may perform: nothing (pure)")
            if f["can_fail"]:
                print("  can fail: callers must handle it")
            for r in f["requires"]:
                print(f"  needs:    {r}")
            for e in f["ensures"]:
                print(f"  promises: {e}")

        for f in mine:
            show(f)
        if not mine:
            print("\n(no functions in this file)")
        show_all = "--all" in argv
        for path, fs in imported.items():
            print(f"\n{'-' * 62}")
            if show_all:
                print(f"imported from {path}")
                for f in fs:
                    show(f)
                continue
            proven = sum(1 for f in fs if f["status"] == "proven")
            effs = sorted({e for f in fs for e in f["effects"]})
            print(f"imported from {path}: {len(fs)} function(s), "
                  f"{proven} with proven promises")
            print(f"  performs: {', '.join(effs) if effs else 'nothing'}"
                  f"   (see them with --all)")
        if rep_["errors"]:
            print("\n" + "=" * 62)
            print(f"{len(rep_['errors'])} problem(s):")
            for e in rep_["errors"]:
                print(f"  line {e['line']}: [{e['code']}] {e['message']}")
            return 1
        print("\n" + "=" * 62)
        n_imp = sum(len(v) for v in imported.values())
        print(f"{len(mine)} function(s) in this file"
              + (f", {n_imp} imported" if n_imp else "")
              + ", no problems found.")
        return 0
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
    if "--allow" in sys.argv or "--deny" in sys.argv:
        allowed = set()
        modules = None
        if "--allow" in sys.argv:
            allowed, modules = parse_budget(
                sys.argv[sys.argv.index("--allow") + 1])
            bad = allowed - set(ALL_EFFECTS)
            if bad:
                print(f"'{sorted(bad)[0]}' is not an effect. They are: "
                      f"{', '.join(ALL_EFFECTS)} (or ffi:module,module)",
                      file=sys.stderr)
                return 2
        else:
            allowed = set(ALL_EFFECTS)
        if "--deny" in sys.argv:
            for name in sys.argv[sys.argv.index("--deny") + 1].split(","):
                name = name.strip()
                if name and name not in ALL_EFFECTS:
                    print(f"'{name}' is not an effect. They are: "
                          f"{', '.join(ALL_EFFECTS)}", file=sys.stderr)
                    return 2
                allowed.discard(name)
        EFFECT_BUDGET.clear()
        EFFECT_BUDGET.update(allowed)
        globals()["FFI_MODULES"] = modules
    FLAGS = {"--json", "--no-native", "--time", "--check"}
    PROGRAM_ARGS[:] = [a for a in sys.argv[2:] if a not in FLAGS]
    try:
        funcs, records = load_program(filename)
        errors: list[VelarisError] = []
        check_effects(funcs, errors)  # superpower 1: no hidden effects
        check_types(funcs, records, errors)  # superpower 2: no type surprises
        proven: set = set()
        if not errors:                # proofs assume well-formed code
            check_proofs(funcs, records, errors, proven,
                         use_cache="--no-cache" not in sys.argv)
        if errors:
            seen_err, unique = set(), []
            for e in errors:            # two checkers can spot one problem
                key = (e.code, e.file or filename, e.line, e.message)
                if key not in seen_err:
                    seen_err.add(key)
                    unique.append(e)
            errors[:] = unique
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
        native = ({} if "--no-native" in sys.argv
                  else compile_native(funcs, proven))
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




# ---------------------------------------------------------------------------
# 14. THE LIBRARY — Velaris from inside another program
#
#     An agent framework, an MCP server or an internal tool should not
#     have to shell out to use this. Everything the command line does is
#     available here, with the same guarantees: effects are enforced
#     while the program runs, whatever its source claims.
#
#         import velaris
#         print(velaris.check(src).ok)
#         print(velaris.audit(src).effects)
#         print(velaris.run(src, allow={"io"}).output)
# ---------------------------------------------------------------------------

AUDIT_SCHEMA = "velaris.audit/1"     # the shape of audit().as_dict()


class Problem:
    """One thing wrong, in a form a tool can act on."""

    __slots__ = ("code", "message", "line", "file", "fixes")

    def __init__(self, code, message, line, file, fixes):
        self.code, self.message = code, message
        self.line, self.file, self.fixes = line, file, list(fixes or [])

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message,
                "line": self.line, "file": self.file, "fixes": self.fixes}

    def __repr__(self):
        return f"[{self.code}] line {self.line}: {self.message}"


class CheckResult:
    __slots__ = ("ok", "problems", "proven", "runtime_checked")

    def __init__(self, ok, problems, proven, runtime_checked):
        self.ok = ok
        self.problems = problems
        self.proven = proven                  # names proven before running
        self.runtime_checked = runtime_checked

    def as_dict(self) -> dict:
        return {"ok": self.ok,
                "problems": [p.as_dict() for p in self.problems],
                "proven": list(self.proven),
                "runtime_checked": list(self.runtime_checked)}


class AuditResult:
    """What a program can touch, promise and fail at - before running."""

    __slots__ = ("schema", "velaris_version", "ok", "problems", "effects",
                 "functions", "proven_share", "safe_command", "warnings",
                 "ffi_modules")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def as_dict(self) -> dict:
        out = {k: getattr(self, k) for k in self.__slots__}
        out["problems"] = [p.as_dict() if hasattr(p, "as_dict") else p
                           for p in (out.get("problems") or [])]
        return out


class RunResult:
    __slots__ = ("ok", "output", "logs", "problems", "refused_effect",
                 "exit_code", "timed_out", "out_of_memory")

    def __init__(self, ok, output, logs, problems, refused_effect,
                 exit_code, timed_out=False, out_of_memory=False):
        self.ok, self.output, self.logs = ok, output, logs
        self.problems, self.refused_effect = problems, refused_effect
        self.exit_code = exit_code
        self.timed_out = timed_out
        self.out_of_memory = out_of_memory

    def as_dict(self) -> dict:
        return {"ok": self.ok, "output": self.output, "logs": self.logs,
                "problems": [p.as_dict() for p in self.problems],
                "refused_effect": self.refused_effect,
                "exit_code": self.exit_code,
                "timed_out": self.timed_out,
                "out_of_memory": self.out_of_memory}


def _as_problem(e, where) -> Problem:
    return Problem(getattr(e, "code", "E000"), getattr(e, "message", str(e)),
                   getattr(e, "line", 0), getattr(e, "file", None) or where,
                   getattr(e, "fixes", []))


def _source_to_file(source: str, path: str | None):
    """Velaris resolves imports against a file, so give the text one."""
    import tempfile
    if path is not None:
        return path, None
    tmp = tempfile.NamedTemporaryFile("w", suffix=".vel", delete=False,
                                      encoding="utf-8")
    tmp.write(source)
    tmp.close()
    return tmp.name, tmp.name


def _ffi_modules_named(path: str, source: str | None) -> set:
    """Top-level Python packages a program names in py* calls.

    Only literal module names can be read without running; a module
    built from text at runtime cannot, and the audit says so.
    """
    try:
        funcs, _ = load_program(path, source)
    except Exception:
        return set()
    found: set = set()
    import dataclasses as _dc

    def visit(node):
        if isinstance(node, (list, tuple)):
            for x in node:
                visit(x)
            return
        if not _dc.is_dataclass(node):
            return
        if isinstance(node, Call) and node.name in (
                "py", "py_int", "py_float", "py_json", "py_new") \
                and node.args and isinstance(node.args[0], Str):
            found.add(node.args[0].value.split(".")[0])
        for f in _dc.fields(node):
            visit(getattr(node, f.name))

    for fn in funcs:
        visit(fn.body)
    return found


def check(source: str, *, path: str | None = None,
          prove: bool = True) -> CheckResult:
    """Compile without running. Every problem, plus what was proven."""
    where, temp = _source_to_file(source, path)
    try:
        problems, proven, runtime = [], set(), []
        try:
            funcs, records = load_program(where, source if path else None)
            errors: list = []
            check_main(funcs, errors, running=False)
            check_effects(funcs, errors)
            if not errors:
                check_types(funcs, records, errors)
            if not errors and prove:
                check_proofs(funcs, records, errors, proven, use_cache=False)
            problems = [_as_problem(e, where) for e in errors]
            for f in funcs:
                if (f.requires or f.ensures) and f.name not in proven:
                    runtime.append(f.name)
        except VelarisError as e:
            problems = [_as_problem(e, where)]
        return CheckResult(not problems, problems, sorted(proven),
                           sorted(runtime))
    finally:
        if temp:
            os.unlink(temp)


def audit(source: str, *, path: str | None = None) -> AuditResult:
    """What this program can touch, promise and fail at.

    The same answer `velaris audit` prints, as data, with a schema name
    so a dashboard or an agent can rely on its shape.
    """
    where, temp = _source_to_file(source, path)
    try:
        report = inspect_source(where, source if path else None)
        own = [f for f in report["functions"]
               if os.path.abspath(f["file"]) == os.path.abspath(where)]
        effects = sorted({e for f in own for e in f["effects"]})
        promising = [f for f in own if f["requires"] or f["ensures"]]
        proven = [f["name"] for f in promising if f["status"] == "proven"]
        share = round(100.0 * len(proven) / len(promising), 1) \
            if promising else None
        warnings = []
        modules_named = sorted(_ffi_modules_named(where, source if path
                                                  else None))
        if "ffi" in effects:
            if modules_named:
                warnings.append(
                    "this program calls Python modules "
                    + ", ".join(modules_named)
                    + "; grant exactly those with ffi:"
                    + ",".join(modules_named)
                    + " rather than plain ffi")
            else:
                warnings.append(
                    "this program calls Python through a module name the "
                    "audit cannot read statically; plain ffi grants "
                    "everything Python can do")
        return AuditResult(
            schema=AUDIT_SCHEMA, velaris_version=VERSION,
            ok=not report["errors"],
            # Problem objects, like check() and run() - they carry
            # .as_dict() for anyone who wants plain data. Returning
            # dicts here and objects there made callers handle both.
            problems=[Problem(e.get("code"), e.get("message"),
                              e.get("line"), e.get("file"),
                              e.get("fixes", []))
                      for e in report["errors"]],
            effects=effects,
            functions=[{"name": f["name"], "effects": sorted(f["effects"]),
                        "can_fail": f["can_fail"],
                        "requires": f["requires"], "ensures": f["ensures"],
                        "status": f["status"]} for f in own],
            proven_share=share,
            safe_command=("velaris <file> --allow " + (
                ",".join(
                    [e for e in effects if e != "ffi"]
                    + (["ffi:" + ",".join(modules_named)] if modules_named
                       and "ffi" in effects
                       else ["ffi"] if "ffi" in effects else []))
                or "''")),
            ffi_modules=modules_named,
            warnings=warnings)
    finally:
        if temp:
            os.unlink(temp)


def run(source: str, *, path: str | None = None,
        allow: set | None = None, deny: set | None = None,
        args: list | None = None, stdin: str = "",
        native: bool = True, timeout: float | None = None,
        max_memory_mb: int | None = None) -> RunResult:
    """Run a program under an effect budget and capture what it did.

    allow={"io"} means it cannot read files, reach the network, call
    Python, ask the clock or use randomness - whatever its source says
    about itself. A refused effect stops the program and is reported in
    refused_effect; it cannot be caught by the program.

    timeout (seconds) and max_memory_mb bound the OTHER two things a
    program can do to the machine that runs it: spin forever, or eat
    memory. With either set, the program runs in a separate process
    that is killed on breach, and the result says which limit it hit.
    An agent framework calling this ten thousand times needs both.

    Memory limits use the OS's address-space limit and are enforced on
    Linux and macOS; on Windows the limit is recorded but not enforced,
    and out_of_memory stays False. The timeout is enforced everywhere.
    """
    import io as _io
    import contextlib
    if timeout is not None or max_memory_mb is not None:
        return _run_bounded(source, path=path, allow=allow, deny=deny,
                            args=args, stdin=stdin, native=native,
                            timeout=timeout, max_memory_mb=max_memory_mb)
    where, temp = _source_to_file(source, path)
    if allow is None:
        budget, modules = set(ALL_EFFECTS), None
    else:
        budget, modules = parse_budget(",".join(sorted(allow)))
    for name in (deny or ()):
        budget.discard(name)
    unknown = (budget | set(deny or ())) - set(ALL_EFFECTS)
    if unknown:
        raise ValueError(f"not an effect: {', '.join(sorted(unknown))}; "
                         f"they are {', '.join(ALL_EFFECTS)} "
                         f"(or ffi:module)")

    saved_budget = set(EFFECT_BUDGET)
    saved_modules = FFI_MODULES
    saved_args = list(PROGRAM_ARGS)
    out, err = _io.StringIO(), _io.StringIO()
    problems, refused, code = [], None, 0
    try:
        EFFECT_BUDGET.clear()
        EFFECT_BUDGET.update(budget)
        globals()["FFI_MODULES"] = modules
        PROGRAM_ARGS[:] = list(args or [])
        result = check(source, path=path)
        if not result.ok:
            return RunResult(False, "", "", result.problems, None, 1)
        funcs, records = load_program(where, source if path else None)
        errors: list = []
        proven: set = set()
        check_proofs(funcs, records, errors, proven, use_cache=False)
        compiled = compile_native(funcs, proven) if native else {}
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            old_stdin = sys.stdin
            sys.stdin = _io.StringIO(stdin)
            try:
                interpret(funcs, compiled)
            finally:
                sys.stdin = old_stdin
    except SystemExit as e:
        code = int(e.code or 0)
    except VelarisError as e:
        problems = [_as_problem(e, where)]
        if e.code == "E310":
            refused = e.message.split("'")[3] \
                if e.message.count("'") >= 4 else None
        elif e.code == "E311":
            m = re.search(r"module '([^']+)'", e.message)
            refused = "ffi:" + m.group(1) if m else "ffi"
        code = 1
    except FailSignal as e:
        problems = [Problem("E521", f"a failure escaped: {e.reason}", 0,
                            where, ["handle it with check"])]
        code = 1
    finally:
        EFFECT_BUDGET.clear()
        EFFECT_BUDGET.update(saved_budget)
        globals()["FFI_MODULES"] = saved_modules
        PROGRAM_ARGS[:] = saved_args
        if temp:
            os.unlink(temp)
    return RunResult(code == 0 and not problems, out.getvalue(),
                     err.getvalue(), problems, refused, code)


def _run_bounded(source, *, path, allow, deny, args, stdin, native,
                 timeout, max_memory_mb) -> RunResult:
    """run() in a child process that can be killed."""
    import subprocess
    where, temp = _source_to_file(source, path)
    spec = ",".join(sorted(ALL_EFFECTS)) if allow is None \
        else ",".join(sorted(allow))
    budget, modules = parse_budget(spec)
    for name in (deny or ()):
        budget.discard(name)
    unknown = (budget | set(deny or ())) - set(ALL_EFFECTS)
    if unknown:
        if temp:
            os.unlink(temp)
        raise ValueError(f"not an effect: {', '.join(sorted(unknown))}; "
                         f"they are {', '.join(ALL_EFFECTS)} "
                         f"(or ffi:module)")

    # compile first, in this process: a program that does not compile
    # never needs a child, and the problems come back the normal way
    result = check(source, path=path)
    if not result.ok:
        if temp:
            os.unlink(temp)
        return RunResult(False, "", "", result.problems, None, 1)

    flag = ",".join(sorted(budget - {"ffi"}))
    if "ffi" in budget:
        flag += ("," if flag else "") + (
            "ffi" if modules is None
            else ",".join("ffi:" + m for m in sorted(modules)))
    cmd = [sys.executable, os.path.abspath(__file__), where,
           "--allow", flag or "''"]
    if not native:
        cmd.append("--no-native")
    cmd += list(args or [])

    def limit_memory():                    # runs inside the child
        if max_memory_mb is None:
            return
        try:
            import resource
            cap = int(max_memory_mb) * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        except Exception:
            pass                           # not this platform

    timed_out = False
    out, err, code = "", "", 0
    try:
        done = subprocess.run(
            cmd, input=stdin, capture_output=True, text=True,
            timeout=timeout,
            preexec_fn=limit_memory if os.name != "nt" else None)
        out, err, code = done.stdout, done.stderr, done.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        out = (e.stdout or b"").decode("utf-8", "replace") \
            if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode("utf-8", "replace") \
            if isinstance(e.stderr, bytes) else (e.stderr or "")
        code = 124
    finally:
        if temp:
            os.unlink(temp)

    problems, refused = [], None
    out_of_memory = False
    if timed_out:
        problems.append(Problem(
            "E610", f"the program ran longer than {timeout} second(s) "
                    f"and was stopped", 0, where,
            ["give it more time, or fix the loop that never ends"]))
    elif code != 0:
        text = err.strip()
        m = re.search(r"error\[(E\d{3})\] (.+)", text)
        if m:
            problems.append(Problem(m.group(1), m.group(2).strip(), 0,
                                    where, []))
            if m.group(1) == "E310":
                q = re.search(r"needs the '(\w+)' effect", m.group(2))
                refused = q.group(1) if q else None
            elif m.group(1) == "E311":
                q = re.search(r"module '([^']+)'", m.group(2))
                refused = "ffi:" + q.group(1) if q else "ffi"
        elif "MemoryError" in text or code in (-9, 137) or \
                "Cannot allocate" in text:
            out_of_memory = True
            problems.append(Problem(
                "E611", f"the program used more than {max_memory_mb} MB "
                        f"and was stopped", 0, where,
                ["give it more memory, or find what is growing"]))
        else:
            problems.append(Problem("E000", text.splitlines()[0][:200]
                                    if text else f"exit code {code}",
                                    0, where, []))
    ok = code == 0 and not problems
    return RunResult(ok, out, err if not problems else "", problems,
                     refused, code, timed_out, out_of_memory)


def card() -> str:
    """The language, small enough to paste into a model."""
    here = os.path.dirname(os.path.abspath(__file__))
    for where in (os.path.join(here, "LLM.md"),
                  os.path.join(here, "..", "LLM.md")):
        if os.path.exists(where):
            return open(where, encoding="utf-8").read()
    return ""


if __name__ == "__main__":
    sys.exit(main())
