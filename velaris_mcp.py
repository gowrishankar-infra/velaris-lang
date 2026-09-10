#!/usr/bin/env python3
"""Velaris as an MCP server: write, audit, run - inside the assistant.

An assistant that writes code should be able to check it, see what it
can touch, and run it in a box, without leaving the conversation. This
speaks the Model Context Protocol over stdin/stdout, so any MCP client
can offer:

    velaris_card    the whole language, ~2,300 words, for writing it
    velaris_check   compile without running; problems as data
    velaris_audit   what a program touches, promises and can fail at
    velaris_run     run it under an effect budget you choose

Add to an MCP client's config:

    {"mcpServers": {"velaris": {"command": "python",
                                "args": ["-m", "velaris_mcp"]}}}

Nothing here trusts the program's own claims: velaris_run enforces the
budget while the program runs, and a refused effect stops it.
"""
import json
import sys

import os

# the compiler may be: installed (pip), vendored beside this file in an
# .mcpb bundle, or sitting in the repo next door. Try each, in the order
# that keeps a user's own install winning.
_here = os.path.dirname(os.path.abspath(__file__))
for _where in (None, os.path.join(_here, "lib"), _here,
               os.path.dirname(_here)):
    if _where and _where not in sys.path:
        sys.path.insert(0, _where)
    try:
        import velaris
        break
    except ImportError:
        continue
else:                                     # pragma: no cover
    sys.stderr.write("velaris not found: pip install velaris-lang\n")
    raise SystemExit(1)

PROTOCOL = "2024-11-05"

# One pool per distinct budget a caller asks for, made the first time
# that budget is seen and closed when the server stops. An assistant
# calls velaris_run over and over inside one conversation; without this
# each call paid a Python interpreter's startup. The budget still comes
# from the request, and a pool never mixes two of them.
POOLS = None


def pools():
    global POOLS
    if POOLS is None:
        POOLS = velaris.PoolRegistry()
    return POOLS


def close_pools() -> None:
    global POOLS
    registry, POOLS = POOLS, None
    if registry is not None:
        registry.close()


TOOLS = [
    {
        "name": "velaris_card",
        "description": (
            "The Velaris language in about 2,300 words: syntax, the "
            "rules models get wrong, every builtin with its effects and "
            "whether it can fail, full standard-library signatures, and "
            "the error table. Read this before writing Velaris."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "velaris_check",
        "description": (
            "Compile a Velaris program without running it. Returns every "
            "problem with a code, line and suggested fixes, plus which "
            "promises were proven before running and which fall back to "
            "runtime checks. Use this to iterate until a program "
            "compiles."),
        "inputSchema": {
            "type": "object",
            "properties": {"source": {"type": "string",
                                      "description": "the program"}},
            "required": ["source"],
        },
    },
    {
        "name": "velaris_audit",
        "description": (
            "What a program can touch (io, fs, net, clock, rand, ffi), "
            "what each function promises, how much of that is proven "
            "rather than checked while running, what can fail, and the "
            "command to run it safely. Use this before running code you "
            "did not write."),
        "inputSchema": {
            "type": "object",
            "properties": {"source": {"type": "string"}},
            "required": ["source"],
        },
    },
    {
        "name": "velaris_run",
        "description": (
            "Run a Velaris program under an effect budget. Anything "
            "outside the budget is refused while the program runs, "
            "whatever the source claims about itself, and a refusal "
            "cannot be caught by the program. Grant the least you can: "
            "['io'] lets it print and nothing else."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "allow": {
                    "type": "array", "items": {"type": "string"},
                    "description": ("effects to permit: io, env, fs, net, "
                                    "clock, rand, ffi. Default ['io']. "
                                    "Scoped grants: fs:read:./data, "
                                    "fs:write:./out, net:api.example.com"
                                    ":443, net:*.example.com, ffi:math,"
                                    "json, and @N for at most N "
                                    "operations (fs@50, net:host@100). "
                                    "Plain fs, net or ffi grants every "
                                    "path, host or module."),
                },
                "stdin": {"type": "string"},
                "args": {"type": "array", "items": {"type": "string"}},
                "timeout": {
                    "type": "number",
                    "description": ("seconds before the program is "
                                    "stopped. Default 30."),
                },
                "max_memory_mb": {
                    "type": "integer",
                    "description": ("memory cap in MB. Default 512. "
                                    "Enforced on Linux (RLIMIT_AS) and "
                                    "on Windows (a job object); "
                                    "best-effort on macOS. The timeout "
                                    "applies everywhere."),
                },
            },
            "required": ["source"],
        },
    },
]


def as_text(payload) -> dict:
    body = payload if isinstance(payload, str) else json.dumps(payload,
                                                               indent=2)
    return {"content": [{"type": "text", "text": body}]}


def handle_tool(name: str, args: dict) -> dict:
    if name == "velaris_card":
        return as_text(velaris.card())

    source = args.get("source", "")
    if name == "velaris_check":
        return as_text(velaris.check(source).as_dict())

    if name == "velaris_audit":
        return as_text(velaris.audit(source).as_dict())

    if name == "velaris_run":
        allow = set(args.get("allow") or ["io"])
        try:
            result = pools().run(
                source, allow=allow,
                stdin=args.get("stdin", ""),
                args=args.get("args") or [],
                timeout=float(args.get("timeout") or 30),
                max_memory_mb=int(args.get("max_memory_mb") or 512))
        except ValueError as e:
            return as_text({"ok": False, "error": str(e)})
        payload = result.as_dict()
        payload["allowed"] = sorted(allow)
        if result.timed_out:
            payload["note"] = "the program ran too long and was stopped"
        elif result.out_of_memory:
            payload["note"] = "the program used too much memory and was stopped"
        elif result.refused_effect:
            payload["note"] = (
                f"the program tried to use '{result.refused_effect}', "
                f"which this run did not allow")
        return as_text(payload)

    return as_text({"error": f"no tool called '{name}'"})


def reply(msg_id, result=None, error=None) -> None:
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main() -> int:
    try:
        return serve()
    finally:
        close_pools()                     # no worker outlives the server


def serve() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, msg_id = msg.get("method"), msg.get("id")
        params = msg.get("params") or {}

        if method == "initialize":
            reply(msg_id, {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "velaris",
                               "version": velaris.VERSION},
            })
        elif method == "tools/list":
            reply(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            name = params.get("name", "")
            try:
                reply(msg_id, handle_tool(name, params.get("arguments")
                                          or {}))
            except Exception as e:                # never kill the server
                reply(msg_id, as_text({"error": f"{type(e).__name__}: {e}"}))
        elif method in ("notifications/initialized", "initialized"):
            continue                              # no reply expected
        elif method == "shutdown":
            close_pools()
            reply(msg_id, None)
        elif method == "exit":
            close_pools()
            return 0
        elif msg_id is not None:
            reply(msg_id, error={"code": -32601,
                                 "message": f"no method '{method}'"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
