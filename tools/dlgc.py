#!/usr/bin/env python3
"""dlgc: the .dlg dialogue compiler (ADR 0004, task M1-NAR-03).

Compiles every game/data/dialogue/**/*.dlg (except the compiled/ folder) into
  * game/data/dialogue/compiled/<scene>.json   one file per .dlg, <scene> = file stem = first node title
  * game/data/loc/dialogue.csv                 Godot CSV translation (header `keys,en`, key DLG_<LINE_ID>)

The syntax reference lives in docs/kb/tech/dialogue_format.md. Errors are reported as
`path:line: message` and the exit code is 1 if there are any.

Usage:
  python3 tools/dlgc.py            compile and write outputs
  python3 tools/dlgc.py --check    compile in memory; fail if the committed outputs are stale
  python3 tools/dlgc.py --root PATH
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1
DIALOGUE_DIR = Path("game/data/dialogue")
COMPILED_DIR = DIALOGUE_DIR / "compiled"
LOC_CSV = Path("game/data/loc/dialogue.csv")
SPEAKERS_JSON = DIALOGUE_DIR / "speakers.json"
EMOTIONS_JSON = DIALOGUE_DIR / "emotions.json"

IDENT = r"[a-z][a-z0-9_]*"
LINE_ID_RE = re.compile(r"[a-z0-9_]+")
TITLE_RE = re.compile(r"[a-z][a-z0-9_]*")
HEADER_RE = re.compile(r"^([a-z_]+)\s*:\s*(.*)$")
SPEAKER_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*(?:\[([^\]]*)\])?\s*:\s*(.*)$")
COMMAND_RE = re.compile(r"^<<\s*(.*?)\s*>>$")
OPTION_COND_RE = re.compile(r"<<\s*if\s+(.*?)\s*>>\s*$")
CUE_RE = re.compile(r"^@([a-z][a-z0-9_]*)(?:\s+(.*))?$")
SET_RE = re.compile(r"^\$(" + IDENT + r")\s*=\s*(.+)$")
COMMENT_RE = re.compile(r"(^|\s)//.*$")
CMP_OPS = ("==", "!=", "<=", ">=", "<", ">")


class DlgError(Exception):
    """A compile error at a source line."""

    def __init__(self, line: int, msg: str) -> None:
        super().__init__(msg)
        self.line = line
        self.msg = msg


# ---------------------------------------------------------------- expressions

TOKEN_RE = re.compile(
    r"""\s*(?:
        (?P<num>-?\d+(?:\.\d+)?)
      | (?P<str>"(?:[^"\\]|\\.)*")
      | (?P<flag>\$[a-z][a-z0-9_]*)
      | (?P<op>==|!=|<=|>=|<|>|\(|\))
      | (?P<word>[A-Za-z_][A-Za-z0-9_]*)
    )""",
    re.X,
)


def tokenize(src: str, line: int) -> list[tuple[str, Any]]:
    toks: list[tuple[str, Any]] = []
    pos = 0
    src = src.rstrip()
    while pos < len(src):
        m = TOKEN_RE.match(src, pos)
        if not m or m.end() == pos:
            raise DlgError(line, f"bad expression near '{src[pos:].strip()}'")
        pos = m.end()
        kind = m.lastgroup
        text = m.group(kind)
        if kind == "num":
            toks.append(("lit", float(text) if "." in text else int(text)))
        elif kind == "str":
            toks.append(("lit", json.loads(text)))
        elif kind == "flag":
            toks.append(("flag", text[1:]))
        elif kind == "op":
            toks.append(("op", text))
        elif text in ("true", "false"):
            toks.append(("lit", text == "true"))
        elif text in ("and", "or", "not"):
            toks.append(("op", text))
        else:
            raise DlgError(line, f"unknown word '{text}' in expression (flags need a '$', strings need quotes)")
    return toks


class ExprParser:
    """or := and ('or' and)* ; and := not ('and' not)* ; not := 'not' not | cmp ;
    cmp := atom (CMP atom)? ; atom := literal | $flag | '(' or ')'.
    Output is a prefix array: ["lit", v] | ["flag", name] | ["not", e] | [op, a, b]."""

    def __init__(self, src: str, line: int) -> None:
        self.line = line
        self.src = src
        self.toks = tokenize(src, line)
        self.i = 0

    def parse(self) -> list:
        if not self.toks:
            raise DlgError(self.line, "empty expression")
        e = self._or()
        if self.i != len(self.toks):
            raise DlgError(self.line, f"unexpected '{self.toks[self.i][1]}' in expression '{self.src.strip()}'")
        return e

    def _peek(self) -> tuple[str, Any] | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def _accept(self, op: str) -> bool:
        t = self._peek()
        if t and t[0] == "op" and t[1] == op:
            self.i += 1
            return True
        return False

    def _or(self) -> list:
        e = self._and()
        while self._accept("or"):
            e = ["or", e, self._and()]
        return e

    def _and(self) -> list:
        e = self._not()
        while self._accept("and"):
            e = ["and", e, self._not()]
        return e

    def _not(self) -> list:
        if self._accept("not"):
            return ["not", self._not()]
        return self._cmp()

    def _cmp(self) -> list:
        a = self._atom()
        t = self._peek()
        if t and t[0] == "op" and t[1] in CMP_OPS:
            self.i += 1
            return [t[1], a, self._atom()]
        return a

    def _atom(self) -> list:
        t = self._peek()
        if t is None:
            raise DlgError(self.line, f"expression '{self.src.strip()}' ends too early")
        self.i += 1
        if t[0] in ("lit", "flag"):
            return [t[0], t[1]]
        if t == ("op", "("):
            e = self._or()
            if not self._accept(")"):
                raise DlgError(self.line, "missing ')' in expression")
            return e
        raise DlgError(self.line, f"unexpected '{t[1]}' in expression '{self.src.strip()}'")


def parse_expr(src: str, line: int) -> list:
    return ExprParser(src, line).parse()


# ---------------------------------------------------------------- source model


@dataclass
class SrcLine:
    no: int
    indent: int
    text: str


@dataclass
class Node:
    title: str
    line: int
    headers: dict[str, str]
    body: list[SrcLine]


@dataclass
class CompileResult:
    outputs: dict[str, str] = field(default_factory=dict)  # repo-relative path -> file text
    errors: list[str] = field(default_factory=list)
    loc_rows: list[tuple[str, str]] = field(default_factory=list)


def strip_comment(raw: str) -> str:
    return COMMENT_RE.sub("", raw).rstrip()


def split_nodes(text: str) -> tuple[list[Node], list[DlgError]]:
    """Splits a file into nodes: headers (`title: x`), `---`, body lines, `===`."""
    nodes: list[Node] = []
    errs: list[DlgError] = []
    headers: dict[str, str] = {}
    header_line = 0
    body: list[SrcLine] | None = None
    for no, raw in enumerate(text.splitlines(), 1):
        line = strip_comment(raw)
        if not line.strip():
            continue
        stripped = line.strip()
        if body is None:
            if stripped == "---":
                if "title" not in headers:
                    errs.append(DlgError(no, "'---' without a 'title:' header"))
                body = []
                continue
            m = HEADER_RE.match(stripped)
            if not m:
                errs.append(DlgError(no, f"expected a 'title: <node>' header, got '{stripped}'"))
                continue
            if not header_line:
                header_line = no
            headers[m.group(1)] = m.group(2).strip()
            continue
        if stripped == "===":
            title = headers.get("title", "")
            nodes.append(Node(title, header_line, dict(headers), body))
            headers, header_line, body = {}, 0, None
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            errs.append(DlgError(no, "bad indentation: use spaces, not tabs"))
            continue
        body.append(SrcLine(no, len(line) - len(line.lstrip(" ")), stripped))
    if body is not None:
        errs.append(DlgError(header_line or 1, f"node '{headers.get('title', '?')}' is missing its closing '==='"))
    elif headers:
        errs.append(DlgError(header_line, "headers without a '---' body"))
    return nodes, errs


# ---------------------------------------------------------------- parser (lines -> statement tree)

STOP_WORDS = ("elseif", "else", "endif")


def command_word(text: str) -> str:
    m = COMMAND_RE.match(text)
    if not m:
        return ""
    return m.group(1).split(" ", 1)[0] if m.group(1) else ""


def split_tags(text: str, line: int) -> tuple[str, str, list[str]]:
    """Pops trailing #hashtags. Returns (text, line_id, other_tags)."""
    words = text.split(" ")
    tags: list[str] = []
    while words and words[-1].startswith("#"):
        tags.insert(0, words.pop())
    line_id = ""
    others: list[str] = []
    for t in tags:
        if t.startswith("#line:"):
            lid = t[len("#line:"):]
            if line_id:
                raise DlgError(line, "more than one #line: tag")
            if not LINE_ID_RE.fullmatch(lid):
                raise DlgError(line, f"bad line id '{lid}' (use lowercase letters, digits, underscores)")
            line_id = lid
        else:
            others.append(t[1:])
    body = " ".join(words).strip().replace("\\:", ":").replace("\\#", "#")
    return body, line_id, others


def convert_arg(tok: str) -> Any:
    if tok in ("true", "false"):
        return tok == "true"
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if re.fullmatch(r"-?\d+\.\d+", tok):
        return float(tok)
    return tok


def split_args(src: str, line: int) -> tuple[list[Any], dict[str, Any]]:
    try:
        toks = shlex.split(src or "")
    except ValueError as e:
        raise DlgError(line, f"bad arguments: {e}") from e
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    for t in toks:
        m = re.fullmatch(r"([a-z_][a-z0-9_]*)=(.*)", t)
        if m:
            kwargs[m.group(1)] = convert_arg(m.group(2))
        else:
            if kwargs:
                raise DlgError(line, f"positional argument '{t}' after key=value arguments")
            args.append(convert_arg(t))
    return args, kwargs


class BodyParser:
    """Recursive descent over a node's lines. Indentation is significant for option bodies
    (and optional inside if-branches); every other statement must sit at its block's column."""

    def __init__(self, lines: list[SrcLine], ctx: "FileCtx") -> None:
        self.lines = lines
        self.i = 0
        self.ctx = ctx

    def peek(self) -> SrcLine | None:
        return self.lines[self.i] if self.i < len(self.lines) else None

    def parse(self) -> list[dict]:
        first = self.peek()
        if first is None:
            return []
        if first.indent != 0:
            raise DlgError(first.no, "bad indentation: a node's first line must not be indented")
        return self.block(0, allow_stop=False)

    def block(self, col: int, allow_stop: bool) -> list[dict]:
        stmts: list[dict] = []
        while True:
            ln = self.peek()
            if ln is None or ln.indent < col:
                return stmts
            if ln.indent > col:
                raise DlgError(ln.no, f"bad indentation: expected column {col}, got {ln.indent} "
                                      "(only option bodies and if-branches may be indented)")
            word = command_word(ln.text)
            if word in STOP_WORDS:
                if allow_stop:
                    return stmts
                raise DlgError(ln.no, f"<<{word}>> without a matching <<if>>")
            if ln.text.startswith("->"):
                stmts.append(self.options(col))
            elif word == "if":
                stmts.append(self.if_block(col))
            else:
                self.i += 1
                stmts.append(self.simple(ln))

    def options(self, col: int) -> dict:
        opts: list[dict] = []
        start = self.peek()
        while True:
            ln = self.peek()
            if ln is None or ln.indent != col or not ln.text.startswith("->"):
                break
            self.i += 1
            text = ln.text[2:].strip()
            cond = None
            m = OPTION_COND_RE.search(text)
            if m:
                cond = parse_expr(m.group(1), ln.no)
                text = text[: m.start()].rstrip()
            body_text, line_id, tags = split_tags(text, ln.no)
            if m is None:
                m2 = OPTION_COND_RE.search(body_text)
                if m2:
                    cond = parse_expr(m2.group(1), ln.no)
                    body_text = body_text[: m2.start()].rstrip()
            if not body_text:
                raise DlgError(ln.no, "option has no text")
            if not line_id:
                raise DlgError(ln.no, "option text is missing its #line:<id> tag")
            self.ctx.register_line(line_id, body_text, ln.no)
            nxt = self.peek()
            body: list[dict] = []
            if nxt is not None and nxt.indent > col:
                body = self.block(nxt.indent, allow_stop=False)
            opt: dict[str, Any] = {"id": line_id, "key": dlg_key(line_id), "body": body, "src": ln.no}
            if cond is not None:
                opt["cond"] = cond
            if tags:
                opt["tags"] = tags
            opts.append(opt)
        return {"kind": "options", "options": opts, "src": start.no if start else 0}

    def if_block(self, col: int) -> dict:
        open_ln = self.peek()
        assert open_ln is not None
        branches: list[tuple[list | None, list[dict]]] = []
        cond_src = COMMAND_RE.match(open_ln.text).group(1)[2:]
        cond: list | None = parse_expr(cond_src, open_ln.no)
        self.i += 1
        seen_else = False
        while True:
            nxt = self.peek()
            if nxt is not None and nxt.indent > col:
                body = self.block(nxt.indent, allow_stop=True)
            else:
                body = self.block(col, allow_stop=True)
            branches.append((cond, body))
            ln = self.peek()
            if ln is None or command_word(ln.text) not in STOP_WORDS:
                raise DlgError(open_ln.no, "unbalanced <<if>>: missing <<endif>>")
            if ln.indent != col:
                raise DlgError(ln.no, f"bad indentation: <<{command_word(ln.text)}>> must align with its "
                                      f"<<if>> on line {open_ln.no} (column {col})")
            word = command_word(ln.text)
            inner = COMMAND_RE.match(ln.text).group(1)
            self.i += 1
            if word == "endif":
                if inner != "endif":
                    raise DlgError(ln.no, "<<endif>> takes no arguments")
                return {"kind": "if", "branches": branches, "src": open_ln.no}
            if seen_else:
                raise DlgError(ln.no, f"<<{word}>> after <<else>>")
            if word == "else":
                if inner != "else":
                    raise DlgError(ln.no, "<<else>> takes no condition (use <<elseif>>)")
                seen_else = True
                cond = None
            else:
                cond = parse_expr(inner[len("elseif"):], ln.no)

    def simple(self, ln: SrcLine) -> dict:
        text = ln.text
        if text.startswith("@"):
            m = CUE_RE.match(text)
            if not m:
                raise DlgError(ln.no, f"bad cue '{text}' (cue names are lowercase, e.g. @camera)")
            args, kwargs = split_args(m.group(2) or "", ln.no)
            return {"kind": "cue", "cue": m.group(1), "args": args, "kwargs": kwargs, "src": ln.no}
        cm = COMMAND_RE.match(text)
        if cm:
            return self.command(cm.group(1), ln)
        if text.startswith("<<"):
            raise DlgError(ln.no, "unterminated command (missing '>>')")
        return self.spoken(ln)

    def command(self, inner: str, ln: SrcLine) -> dict:
        word, _, rest = inner.partition(" ")
        rest = rest.strip()
        if word == "set":
            m = SET_RE.match(rest)
            if not m:
                raise DlgError(ln.no, "bad <<set>>: expected <<set $flag = value>>")
            return {"kind": "set", "flag": m.group(1), "value": parse_expr(m.group(2), ln.no), "src": ln.no}
        if word == "jump":
            if not TITLE_RE.fullmatch(rest):
                raise DlgError(ln.no, "bad <<jump>>: expected <<jump node_title>>")
            return {"kind": "jump", "node": rest, "src": ln.no}
        if word == "event":
            if not rest:
                raise DlgError(ln.no, "bad <<event>>: expected <<event name args...>>")
            name, _, arg_src = rest.partition(" ")
            if not TITLE_RE.fullmatch(name):
                raise DlgError(ln.no, f"bad event name '{name}'")
            args, kwargs = split_args(arg_src, ln.no)
            if kwargs:
                raise DlgError(ln.no, "<<event>> takes positional arguments only")
            return {"kind": "event", "name": name, "args": args, "src": ln.no}
        if word == "stop":
            if rest:
                raise DlgError(ln.no, "<<stop>> takes no arguments")
            return {"kind": "stop", "src": ln.no}
        raise DlgError(ln.no, f"unknown command <<{word}>> (known: if, elseif, else, endif, set, jump, event, stop)")

    def spoken(self, ln: SrcLine) -> dict:
        speaker_id = ""
        emotion = ""
        text = ln.text
        m = SPEAKER_RE.match(text)
        if m:
            speaker_id = m.group(1).lower()
            emotion = (m.group(2) or "").strip()
            text = m.group(3)
            if speaker_id not in self.ctx.speakers:
                raise DlgError(ln.no, f"unknown speaker '{m.group(1)}' (add it to {SPEAKERS_JSON.as_posix()}, "
                                      "or write '\\:' for a colon in narration)")
            if m.group(2) is not None and emotion not in self.ctx.emotions:
                raise DlgError(ln.no, f"unknown emotion '[{emotion}]' (allowed: see {EMOTIONS_JSON.as_posix()})")
        body, line_id, tags = split_tags(text, ln.no)
        if not body:
            raise DlgError(ln.no, "line has no text")
        if not line_id:
            raise DlgError(ln.no, "spoken text is missing its #line:<id> tag")
        self.ctx.register_line(line_id, body, ln.no)
        out: dict[str, Any] = {"kind": "line", "id": line_id, "key": dlg_key(line_id), "speaker": speaker_id,
                               "emotion": emotion, "voice": "", "src": ln.no}
        if tags:
            out["tags"] = tags
        return out


# ---------------------------------------------------------------- codegen (statement tree -> ops)


def emit(stmts: list[dict], ops: list[dict], titles: set[str], ctx: "FileCtx") -> None:
    for s in stmts:
        kind = s["kind"]
        if kind == "line":
            op = {"op": "line", **{k: v for k, v in s.items() if k != "kind"}}
            ops.append(op)
        elif kind == "cue":
            ops.append({"op": "cue", "cue": s["cue"], "args": s["args"], "kwargs": s["kwargs"], "src": s["src"]})
        elif kind == "set":
            ops.append({"op": "set", "flag": s["flag"], "value": s["value"], "src": s["src"]})
        elif kind == "event":
            ops.append({"op": "event", "name": s["name"], "args": s["args"], "src": s["src"]})
        elif kind == "stop":
            ops.append({"op": "stop", "src": s["src"]})
        elif kind == "jump":
            if s["node"] not in titles:
                ctx.error(s["src"], f"unknown jump target '{s['node']}' (nodes in this file: {sorted(titles)})")
            ops.append({"op": "jump", "node": s["node"], "src": s["src"]})
        elif kind == "if":
            ends: list[dict] = []
            for cond, body in s["branches"]:
                test = None
                if cond is not None:
                    test = {"op": "if_not", "cond": cond, "to": -1, "src": s["src"]}
                    ops.append(test)
                emit(body, ops, titles, ctx)
                goto = {"op": "goto", "to": -1, "src": s["src"]}
                ops.append(goto)
                ends.append(goto)
                if test is not None:
                    test["to"] = len(ops)
            for g in ends:
                g["to"] = len(ops)
        elif kind == "options":
            choices: list[dict] = []
            menu = {"op": "options", "choices": choices, "src": s["src"]}
            ops.append(menu)
            ends = []
            for o in s["options"]:
                choice: dict[str, Any] = {"id": o["id"], "key": o["key"], "to": len(ops), "src": o["src"]}
                if "cond" in o:
                    choice["cond"] = o["cond"]
                if "tags" in o:
                    choice["tags"] = o["tags"]
                choices.append(choice)
                emit(o["body"], ops, titles, ctx)
                goto = {"op": "goto", "to": -1, "src": o["src"]}
                ops.append(goto)
                ends.append(goto)
            menu["next"] = len(ops)  # where to continue if no option is available
            for g in ends:
                g["to"] = len(ops)


# ---------------------------------------------------------------- project compile


def dlg_key(line_id: str) -> str:
    return "DLG_" + line_id.upper()


class FileCtx:
    def __init__(self, rel: str, speakers: set[str], emotions: set[str], line_ids: dict[str, str],
                 result: CompileResult) -> None:
        self.rel = rel
        self.speakers = speakers
        self.emotions = emotions
        self.line_ids = line_ids
        self.result = result
        self.ok = True

    def error(self, line: int, msg: str) -> None:
        self.ok = False
        self.result.errors.append(f"{self.rel}:{line}: {msg}")

    def register_line(self, line_id: str, text: str, line: int) -> None:
        where = f"{self.rel}:{line}"
        if line_id in self.line_ids:
            raise DlgError(line, f"duplicate line id '{line_id}' (first used at {self.line_ids[line_id]})")
        self.line_ids[line_id] = where
        self.result.loc_rows.append((dlg_key(line_id), text))


def _load_ids(root: Path, rel: Path, table: str, result: CompileResult) -> set[str]:
    p = root / rel
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {str(r["id"]) for r in data[table]}
    except (OSError, ValueError, KeyError, TypeError) as e:
        result.errors.append(f"{rel.as_posix()}: cannot read '{table}' table: {e}")
        return set()


def source_files(root: Path) -> list[Path]:
    base = root / DIALOGUE_DIR
    if not base.exists():
        return []
    compiled = root / COMPILED_DIR
    return sorted(p for p in base.rglob("*.dlg") if compiled not in p.parents)


def compile_file(path: Path, rel: str, ctx: FileCtx) -> dict | None:
    nodes, errs = split_nodes(path.read_text(encoding="utf-8"))
    for e in errs:
        ctx.error(e.line, e.msg)
    if not nodes:
        if not errs:
            ctx.error(1, "no nodes (expected 'title: <name>', '---', body, '===')")
        return None
    titles: set[str] = set()
    for n in nodes:
        if not TITLE_RE.fullmatch(n.title):
            ctx.error(n.line, f"bad node title '{n.title}' (lowercase letters, digits, underscores)")
        if n.title in titles:
            ctx.error(n.line, f"duplicate node title '{n.title}'")
        titles.add(n.title)
    stem = path.stem
    if nodes[0].title != stem:
        ctx.error(nodes[0].line, f"the first node's title '{nodes[0].title}' must match the file name '{stem}'")
    out_nodes: dict[str, Any] = {}
    for n in nodes:
        try:
            tree = BodyParser(n.body, ctx).parse()
        except DlgError as e:
            ctx.error(e.line, e.msg)
            continue
        ops: list[dict] = []
        emit(tree, ops, titles, ctx)
        headers = {k: v for k, v in n.headers.items() if k != "title"}
        out_nodes[n.title] = {"headers": headers, "ops": ops}
    if not ctx.ok:
        return None
    return {"format": FORMAT_VERSION, "scene": stem, "source": rel, "start": nodes[0].title, "nodes": out_nodes}


def render_scene(scene: dict) -> str:
    """Stable JSON with one op per line, so diffs of compiled scenes stay readable."""
    def j(v: Any) -> str:
        return json.dumps(v, ensure_ascii=False)

    out = ["{"]
    for k in ("format", "scene", "source", "start"):
        out.append(f" {j(k)}: {j(scene[k])},")
    out.append(' "nodes": {')
    titles = list(scene["nodes"])
    for ti, title in enumerate(titles):
        node = scene["nodes"][title]
        out.append(f"  {j(title)}: {{")
        out.append(f'   "headers": {j(node["headers"])},')
        out.append('   "ops": [')
        ops = node["ops"]
        out.extend(f"    {j(op)}{',' if i < len(ops) - 1 else ''}" for i, op in enumerate(ops))
        out.append("   ]")
        out.append("  }" + ("," if ti < len(titles) - 1 else ""))
    out.append(" }")
    out.append("}")
    return "\n".join(out) + "\n"


def render_csv(rows: list[tuple[str, str]]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["keys", "en"])
    for k, v in rows:
        w.writerow([k, v])
    return buf.getvalue()


def compile_project(root: Path) -> CompileResult:
    result = CompileResult()
    speakers = _load_ids(root, SPEAKERS_JSON, "speakers", result)
    emotions = _load_ids(root, EMOTIONS_JSON, "emotions", result)
    line_ids: dict[str, str] = {}
    scenes: dict[str, str] = {}
    for path in source_files(root):
        rel = path.relative_to(root).as_posix()
        ctx = FileCtx(rel, speakers, emotions, line_ids, result)
        if path.stem in scenes:
            ctx.error(1, f"scene name '{path.stem}' is already used by {scenes[path.stem]} (compiled names are flat)")
            continue
        scenes[path.stem] = rel
        compiled = compile_file(path, rel, ctx)
        if compiled is not None:
            out = (COMPILED_DIR / f"{path.stem}.json").as_posix()
            result.outputs[out] = render_scene(compiled)
    result.outputs[LOC_CSV.as_posix()] = render_csv(result.loc_rows)
    return result


def stale_outputs(root: Path, result: CompileResult) -> list[str]:
    """Paths whose committed content differs from a fresh compile, plus orphaned compiled files."""
    stale: list[str] = []
    for rel, text in sorted(result.outputs.items()):
        p = root / rel
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            stale.append(rel)
    compiled = root / COMPILED_DIR
    if compiled.exists():
        for p in sorted(compiled.glob("*.json")):
            rel = p.relative_to(root).as_posix()
            if rel not in result.outputs:
                stale.append(rel)
    return stale


def check(root: Path) -> list[str]:
    """Compile errors plus staleness errors; empty means the committed outputs are fresh."""
    result = compile_project(root)
    errors = list(result.errors)
    if errors:
        return errors
    for rel in stale_outputs(root, result):
        errors.append(f"{rel}: dialogue output is stale (run python3 tools/dlgc.py)")
    return errors


def write(root: Path) -> CompileResult:
    result = compile_project(root)
    if result.errors:
        return result
    for rel in stale_outputs(root, result):
        p = root / rel
        if rel in result.outputs:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(result.outputs[rel], encoding="utf-8")
        else:
            p.unlink()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--check", action="store_true", help="fail if committed outputs are stale; write nothing")
    args = ap.parse_args()
    if args.check:
        errors = check(args.root)
        for e in errors:
            print(f"ERROR {e}")
        print(f"dlgc --check: {len(errors)} error(s)")
        return 1 if errors else 0
    result = write(args.root)
    for e in result.errors:
        print(f"ERROR {e}")
    n = len([k for k in result.outputs if k.endswith(".json")])
    print(f"dlgc: {n} scene(s), {len(result.loc_rows)} line(s), {len(result.errors)} error(s)")
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
