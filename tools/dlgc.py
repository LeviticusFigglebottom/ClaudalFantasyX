#!/usr/bin/env python3
"""dlgc: the .dlg dialogue compiler (ADR 0004, tasks M1-NAR-03, M1-NAR-04 and M1-NAR-06).

Compiles every game/data/dialogue/**/*.dlg (except the compiled/ folder) into
  * game/data/dialogue/compiled/<scene>.json   one file per .dlg, <scene> = file stem = first node title
  * game/data/loc/dialogue.csv                 Godot CSV translation (header `keys,en`, key DLG_<LINE_ID>)
  * game/data/dialogue/compiled/translator_notes.tsv   #notr / #tn:"..." lines, for translators

Cues are checked against game/data/dialogue/cues.json and <<event>> names against
game/data/dialogue/events.json. The syntax reference lives in docs/kb/tech/dialogue_format.md.
Errors are reported as `path:line: message` and the exit code is 1 if there are any. Warnings
(e.g. a line over 25 words) are printed as WARN and never fail the build.

Usage:
  python3 tools/dlgc.py                     compile and write outputs
  python3 tools/dlgc.py --check             compile in memory; fail if the committed outputs are stale
  python3 tools/dlgc.py --assign-ids FILE   fill in missing #line: ids in FILE (in place), then stop
                        [--prefix PREFIX]   id prefix (default: the file's most common one, else the scene
                                            name's first and last words, e.g. ch02_beach)
  python3 tools/dlgc.py --root PATH
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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
CUES_JSON = DIALOGUE_DIR / "cues.json"
EVENTS_JSON = DIALOGUE_DIR / "events.json"
NOTES_TSV = COMPILED_DIR / "translator_notes.tsv"
TEST_DIR = DIALOGUE_DIR / "test"
# Reserved speaker name for narration with an emotion and an optional voice identity.
NARRATOR = "narrator"
LINE_WORD_LIMIT = 25  # docs/kb/story/voice_guide.md: "about 25 words or fewer"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")
# Tags the compiler gives meaning to (all are also kept in the op's `tags`).
TAG_SUNG = "sung"
TAG_NOTR = "notr"
TAG_LONG = "long"

IDENT = r"[a-z][a-z0-9_]*"
LINE_ID_RE = re.compile(r"[a-z0-9_]+")
TITLE_RE = re.compile(r"[a-z][a-z0-9_]*")
HEADER_RE = re.compile(r"^([a-z_]+)\s*:\s*(.*)$")
# Name, optional (identity), optional as "Alias", optional [emotion], then ':'.
SPEAKER_RE = re.compile(
    r"""^([A-Za-z][A-Za-z0-9_]*)(?:\(\s*([^)]*?)\s*\))?(?:\s+as\s+"((?:[^"\\]|\\.)*)")?"""
    r"""\s*(?:\[([^\]]*)\])?\s*:\s*(.*)$"""
)
TN_RE = re.compile(r"""(?:^|\s)#tn:"((?:[^"\\]|\\.)*)"(?=\s|$)""")
# Near misses of SPEAKER_RE (M1-NAR-06). Each would otherwise compile, silently, to narration.
# `Name [emotion] as "Alias":` (the emotion belongs after the alias)
EMO_BEFORE_ALIAS_RE = re.compile(
    r"""^([A-Za-z][A-Za-z0-9_]*)(\([^)]*\))?\s*\[([^\]]*)\]\s+as\s+"((?:[^"\\]|\\.)*)"\s*:"""
)
# `Name as Alias [emotion]:` (the alias needs double quotes)
UNQUOTED_ALIAS_RE = re.compile(r"""^([A-Za-z][A-Za-z0-9_]*)\s+as\s+([^"\[\]:]*?)\s*(\[[^\]]*\])?\s*:""")
# `[emotion] narration` (narration takes an emotion only through `Narrator [emotion]:`)
EMO_NARRATION_RE = re.compile(r"^\[([^\]]*)\]\s*:?\s*(.*)$")
# The heuristic: up to SPEAKER_LIKE_MAX_WORDS words that start with a capital letter and carry no
# sentence punctuation, then an unescaped colon. Real narration that reads like that takes #narration.
SPEAKER_LIKE_RE = re.compile(r"""^([A-Z][^:.!?;,…—]*?)(?<!\\):""")
SPEAKER_LIKE_MAX_WORDS = 6
TAG_NARRATION = "narration"  # compiler-only: "this is narration, as written"; not kept in the op
ARG_ID_RE = re.compile(r"[A-Za-z0-9_]+")
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
    raw: str = ""  # the source line before the // comment was stripped (for error messages)


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
    warnings: list[str] = field(default_factory=list)
    loc_rows: list[tuple[str, str]] = field(default_factory=list)
    # (key, scene, do_not_translate, note, en) for lines with #notr or #tn:"..."
    note_rows: list[tuple[str, str, bool, str, str]] = field(default_factory=list)
    # every loc key written so far -> where it was first defined (line ids and aliases share the namespace)
    keys: dict[str, str] = field(default_factory=dict)
    alias_text: dict[str, str] = field(default_factory=dict)
    # --assign-ids: (source line, what) of each line or option missing its #line: id, in file order
    missing_ids: list[tuple[int, str]] = field(default_factory=list)


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
        body.append(SrcLine(no, len(line) - len(line.lstrip(" ")), stripped, raw))
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


def split_tags(text: str, line: int, raw: str = "") -> tuple[str, str, list[str], str]:
    """Pops trailing #hashtags and one #tn:"translator note". Returns (text, line_id, other_tags, note).
    `raw` is the source line before comment stripping; it only sharpens the bad-note message."""
    body, line_id, others, note = split_tags_raw(text, line, raw)
    return unescape(body), line_id, others, note


def _clip(text: str, n: int = 40) -> str:
    return text if len(text) <= n else text[: n - 3].rstrip() + "..."


def unescape(body: str) -> str:
    return body.replace("\\:", ":").replace("\\#", "#")


def _note_cut_by_comment(raw: str) -> bool:
    """True if a ` //` comment starts inside a #tn:"..." note on this source line."""
    start = raw.find('#tn:"')
    if start < 0:
        return False
    m = COMMENT_RE.search(raw, start)
    return m is not None


def split_tags_raw(text: str, line: int, raw: str = "") -> tuple[str, str, list[str], str]:
    """split_tags without unescaping `\\:` and `\\#` in the text."""
    note = ""
    notes = list(TN_RE.finditer(text))
    if len(notes) > 1:
        raise DlgError(line, 'more than one #tn:"..." translator note')
    if notes:
        m = notes[0]
        note = json.loads('"' + m.group(1) + '"').strip()
        if not note:
            raise DlgError(line, '#tn:"" is empty (write the note for translators, or drop the tag)')
        text = (text[: m.start()] + " " + text[m.end():]).strip()
    elif re.search(r"(?:^|\s)#tn:", text):
        if _note_cut_by_comment(raw):
            raise DlgError(line, 'translator note cut off: " //" starts a comment, even inside #tn:"..." '
                                 '(reword the note without " //", e.g. use "/" or "or")')
        raise DlgError(line, 'bad translator note: write #tn:"note text" with double quotes')
    words = text.split(" ")
    tags: list[str] = []
    while words and (words[-1] == "" or words[-1].startswith("#")):
        w = words.pop()
        if w:
            tags.insert(0, w)
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
    if TAG_NOTR in others and not note:
        raise DlgError(line, '#notr needs a translator note saying why: #tn:"..."')
    return " ".join(words).strip(), line_id, others, note


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


ARG_TYPES = ("id", "number", "int", "bool", "string", "emotion", "enum")


@dataclass
class Vocab:
    """cues.json and events.json, plus the emotion ids (for the `emotion` arg type)."""

    cues: dict[str, dict] = field(default_factory=dict)
    sets: dict[str, list] = field(default_factory=dict)
    reserved: dict[str, dict] = field(default_factory=dict)
    events: dict[str, dict] = field(default_factory=dict)
    emotions: set[str] = field(default_factory=set)

    def enum_values(self, spec: dict) -> list:
        if "set" in spec:
            return list(self.sets.get(str(spec["set"]), []))
        return list(spec.get("values", []))


def value_error(spec: dict, value: Any, vocab: Vocab) -> str:
    """Why `value` does not fit the arg spec ({"type", "min"?, "max"?, "values"|"set"?}); empty if it fits."""
    kind = spec.get("type", "")
    shown = json.dumps(value) if not isinstance(value, str) else f"'{value}'"
    if kind == "id":
        ok = isinstance(value, str) and ARG_ID_RE.fullmatch(value) is not None
        return "" if ok else f"{shown} is not an id (letters, digits, underscores)"
    if kind == "string":
        return "" if isinstance(value, str) else f"{shown} is not text"
    if kind == "bool":
        return "" if isinstance(value, bool) else f"{shown} is not true/false"
    if kind == "emotion":
        return "" if value in vocab.emotions else f"{shown} is not an emotion in {EMOTIONS_JSON.as_posix()}"
    if kind == "enum":
        allowed = vocab.enum_values(spec)
        if value in allowed:
            return ""
        where = f" (set '{spec['set']}' in {CUES_JSON.as_posix()})" if "set" in spec else ""
        return f"{shown} is not one of {', '.join(str(a) for a in allowed)}{where}"
    if kind in ("number", "int"):
        numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
        if not numeric or (kind == "int" and not isinstance(value, int)):
            return f"{shown} is not {'an integer' if kind == 'int' else 'a number'}"
        if "min" in spec and value < spec["min"]:
            return f"{shown} is below the minimum {spec['min']}"
        if "max" in spec and value > spec["max"]:
            return f"{shown} is above the maximum {spec['max']}"
        return ""
    return f"unknown arg type '{kind}'"


def check_positional(label: str, specs: list[dict], args: list[Any], vocab: Vocab, line: int) -> None:
    required = sum(1 for a in specs if not a.get("optional"))
    names = " ".join(a["name"] if not a.get("optional") else f"[{a['name']}]" for a in specs) or "nothing"
    if not required <= len(args) <= len(specs):
        raise DlgError(line, f"{label} takes {names}; got {len(args)} argument(s)")
    for spec, value in zip(specs, args):
        why = value_error(spec, value, vocab)
        if why:
            raise DlgError(line, f"{label} {spec['name']}: {why}")


def check_cue(cue: str, args: list[Any], kwargs: dict[str, Any], vocab: Vocab, line: int) -> None:
    """Checks a cue against cues.json: known name, positional args, key=value names and values."""
    spec = vocab.cues.get(cue)
    if spec is None:
        raise DlgError(line, f"unknown cue '@{cue}' (known: {', '.join(sorted(vocab.cues))}; "
                             f"new cues go in {CUES_JSON.as_posix()})")
    check_positional(f"@{cue}", spec.get("args", []), args, vocab, line)
    allowed: dict[str, dict] = spec.get("kwargs", {})
    for k, v in kwargs.items():
        if k not in allowed:
            known = ", ".join(f"{a}=" for a in sorted(allowed)) or "none"
            raise DlgError(line, f"@{cue}: unknown key '{k}=' (allowed: {known})")
        why = value_error(allowed[k], v, vocab)
        if why:
            raise DlgError(line, f"@{cue} {k}=: {why}")
    given = {a["name"] for a, _ in zip(spec.get("args", []), args)} | set(kwargs)
    one_of: list[str] = spec.get("one_of", [])
    if one_of and len(given & set(one_of)) != 1:
        raise DlgError(line, f"@{cue} needs exactly one of: {', '.join(one_of)}")
    for k, needed in spec.get("requires", {}).items():
        if k in given and needed not in given:
            raise DlgError(line, f"@{cue}: {k}= only works together with {needed}")


def check_event(name: str, args: list[Any], vocab: Vocab, in_test_dir: bool, line: int) -> None:
    spec = vocab.events.get(name)
    if spec is None or (spec.get("test_only") and not in_test_dir):
        known = sorted(k for k, v in vocab.events.items() if in_test_dir or not v.get("test_only"))
        raise DlgError(line, f"unknown event '{name}' (declared: {', '.join(known)}; "
                             f"declare new ones in {EVENTS_JSON.as_posix()})")
    check_positional(f"<<event {name}>>", spec.get("args", []), args, vocab, line)


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
            body_text, line_id, tags, note = split_tags(text, ln.no, ln.raw)
            if TAG_NARRATION in tags:
                raise DlgError(ln.no, f"#{TAG_NARRATION} marks narration lines; an option is never narration")
            if m is None:
                m2 = OPTION_COND_RE.search(body_text)
                if m2:
                    cond = parse_expr(m2.group(1), ln.no)
                    body_text = body_text[: m2.start()].rstrip()
            if not body_text:
                raise DlgError(ln.no, "option has no text")
            line_id = self.ctx.register_line(line_id, body_text, ln.no, tags, note, "option text")
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
        branches: list[tuple[list | None, list[dict], int]] = []
        cond_src = COMMAND_RE.match(open_ln.text).group(1)[2:]
        cond: list | None = parse_expr(cond_src, open_ln.no)
        self.i += 1
        seen_else = False
        branch_line = open_ln.no
        while True:
            nxt = self.peek()
            if nxt is not None and nxt.indent > col:
                body = self.block(nxt.indent, allow_stop=True)
            else:
                body = self.block(col, allow_stop=True)
            branches.append((cond, body, branch_line))
            ln = self.peek()
            if ln is None or command_word(ln.text) not in STOP_WORDS:
                raise DlgError(open_ln.no, "unbalanced <<if>>: missing <<endif>>")
            if ln.indent != col:
                raise DlgError(ln.no, f"bad indentation: <<{command_word(ln.text)}>> must align with its "
                                      f"<<if>> on line {open_ln.no} (column {col})")
            word = command_word(ln.text)
            inner = COMMAND_RE.match(ln.text).group(1)
            branch_line = ln.no
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
            check_cue(m.group(1), args, kwargs, self.ctx.vocab, ln.no)
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
            check_event(name, args, self.ctx.vocab, self.ctx.in_test_dir, ln.no)
            return {"kind": "event", "name": name, "args": args, "src": ln.no}
        if word == "stop":
            if rest:
                raise DlgError(ln.no, "<<stop>> takes no arguments")
            return {"kind": "stop", "src": ln.no}
        raise DlgError(ln.no, f"unknown command <<{word}>> (known: if, elseif, else, endif, set, jump, event, stop)")

    def spoken(self, ln: SrcLine) -> dict:
        """`Speaker [as "Alias"] [emotion]: text`, `Narrator(identity) [emotion]: text`, or bare narration."""
        speaker_id = ""
        emotion = ""
        narrator = ""
        alias = None
        text = ln.text
        m = SPEAKER_RE.match(text)
        if m:
            name, identity, alias, emo, text = m.groups()
            speaker_id = name.lower()
            emotion = (emo or "").strip()
            if emo is not None and emotion not in self.ctx.emotions:
                raise DlgError(ln.no, f"unknown emotion '[{emotion}]' (allowed: see {EMOTIONS_JSON.as_posix()})")
            if speaker_id == NARRATOR:
                if alias is not None:
                    raise DlgError(ln.no, "narration shows no name, so Narrator takes no 'as \"...\"' alias")
                if identity is not None:
                    if identity.lower() not in self.ctx.speakers:
                        raise DlgError(ln.no, f"unknown narrator identity '{identity}' "
                                              f"(use a speaker id from {SPEAKERS_JSON.as_posix()})")
                    narrator = identity.lower()
                speaker_id = ""
            else:
                if speaker_id not in self.ctx.speakers:
                    raise DlgError(ln.no, f"unknown speaker '{name}' (add it to {SPEAKERS_JSON.as_posix()}, "
                                          "or write '\\:' for a colon in narration)")
                if identity is not None:
                    raise DlgError(ln.no, f"'{name}({identity})': only Narrator takes a voice identity")
            body, line_id, tags, note = split_tags(text, ln.no, ln.raw)
            if TAG_NARRATION in tags:
                raise DlgError(ln.no, f"#{TAG_NARRATION} marks narration that looks like a speaker line; "
                                      f"this line has a speaker ('{name}:')")
        else:
            raw_body, line_id, tags, note = split_tags_raw(text, ln.no, ln.raw)
            if TAG_NARRATION in tags:
                tags.remove(TAG_NARRATION)
            else:
                self.check_near_miss(raw_body, ln.no)
            body = unescape(raw_body)
        if not body:
            raise DlgError(ln.no, "line has no text")
        line_id = self.ctx.register_line(line_id, body, ln.no, tags, note, "spoken text")
        out: dict[str, Any] = {"kind": "line", "id": line_id, "key": dlg_key(line_id), "speaker": speaker_id,
                               "emotion": emotion, "voice": "", "src": ln.no}
        if alias is not None:
            out["name_key"] = self.ctx.register_alias(speaker_id, alias, ln.no)
        if narrator:
            out["narrator"] = narrator
        if tags:
            out["tags"] = tags
        return out

    def check_near_miss(self, body: str, line: int) -> None:
        """M1-NAR-06: a narration line (tags already popped, escapes kept) that nearly matches a speaker
        line is an error, so a typo never ships its raw `Name [emo]:` text. `#narration` skips this."""
        allow = f"tag the line #{TAG_NARRATION} if it really is narration"
        m = EMO_BEFORE_ALIAS_RE.match(body)
        if m:
            name, identity, emo, alias = m.groups()
            fix = f'{name}{identity or ""} as "{alias}" [{emo.strip()}]:'
            raise DlgError(line, f"the emotion goes after the alias: did you mean '{fix}'? "
                                 "(as written, this line would compile as narration)")
        m = UNQUOTED_ALIAS_RE.match(body)
        if m and m.group(1).lower() in self.ctx.speakers and m.group(2):
            name, alias, emo = m.groups()
            fix = f'{name} as "{alias}"' + (f" {emo}" if emo else "") + ":"
            raise DlgError(line, f"an alias needs double quotes: did you mean '{fix}'? "
                                 "(as written, this line would compile as narration)")
        m = EMO_NARRATION_RE.match(body)
        if m:
            emo = m.group(1).strip()
            known = "" if emo in self.ctx.emotions else f"; '{emo}' is not in {EMOTIONS_JSON.as_posix()} either"
            raise DlgError(line, f"narration takes an emotion only through Narrator: did you mean "
                                 f"'Narrator [{emo}]: {_clip(m.group(2))}'? (or 'Narrator(<speaker id>) [{emo}]:' "
                                 f"for a voice-over{known}; {allow})")
        m = SPEAKER_LIKE_RE.match(body)
        if m and len(m.group(1).split()) <= SPEAKER_LIKE_MAX_WORDS:
            prefix = m.group(1).strip()
            first = re.match(r"[A-Za-z0-9_]+", prefix)
            hint = ""
            if first and first.group(0).lower() in self.ctx.speakers | {NARRATOR}:
                hint = f" Did you mean '{first.group(0)}:' or '{first.group(0)} [emotion]:'?"
            raise DlgError(line, f"'{prefix}:' looks like a speaker, but this line would compile as narration "
                                 "(a speaker line is 'Name [emotion]: text' or 'Name as \"Alias\" [emotion]: "
                                 f"text', Name one word from {SPEAKERS_JSON.as_posix()}).{hint} For narration, "
                                 f"write '\\:' for the colon or {allow}")


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
            for cond, body, branch_line in s["branches"]:
                test = None
                if cond is not None:
                    test = {"op": "if_not", "cond": cond, "to": -1, "src": branch_line}
                    ops.append(test)
                emit(body, ops, titles, ctx)
                goto = {"op": "goto", "to": -1, "src": branch_line}
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


def count_words(text: str) -> int:
    """Words as the voice guide counts them: runs of letters and digits (inner ' and - don't split)."""
    return len(WORD_RE.findall(text))


def alias_key(speaker: str, alias: str) -> str:
    """DLG_NAME_<SPEAKER>_<SLUG>; a name with no letters or digits (e.g. "???") gets a short hash."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", alias).strip("_").upper()
    if not slug:
        slug = "X" + hashlib.sha1(alias.encode("utf-8")).hexdigest()[:6].upper()
    return f"DLG_NAME_{speaker.upper()}_{slug}"


class FileCtx:
    def __init__(self, rel: str, speakers: set[str], vocab: Vocab, line_ids: dict[str, str],
                 result: CompileResult, assigning: bool = False) -> None:
        self.rel = rel
        self.scene = Path(rel).stem
        self.speakers = speakers
        self.vocab = vocab
        self.emotions = vocab.emotions
        self.line_ids = line_ids
        self.result = result
        self.assigning = assigning
        self.in_test_dir = rel.startswith(TEST_DIR.as_posix() + "/")
        self.ok = True

    def error(self, line: int, msg: str) -> None:
        self.ok = False
        self.result.errors.append(f"{self.rel}:{line}: {msg}")

    def warn(self, line: int, msg: str) -> None:
        self.result.warnings.append(f"{self.rel}:{line}: {msg}")

    def _claim_key(self, key: str, line: int, what: str) -> None:
        if key in self.result.keys:
            raise DlgError(line, f"{what} maps to loc key {key}, already defined at {self.result.keys[key]}")
        self.result.keys[key] = f"{self.rel}:{line}"

    def register_line(self, line_id: str, text: str, line: int, tags: list[str], note: str, what: str) -> str:
        """Records a line or option's loc row (and translator note). Returns its id. With no id, it is an
        error, except under --assign-ids, where the line is listed and gets a placeholder id."""
        if not line_id:
            if not self.assigning:
                raise DlgError(line, f"{what} is missing its #line:<id> tag")
            self.result.missing_ids.append((line, what))
            return f"missing_{line}"
        where = f"{self.rel}:{line}"
        if line_id in self.line_ids:
            raise DlgError(line, f"duplicate line id '{line_id}' (first used at {self.line_ids[line_id]})")
        self._claim_key(dlg_key(line_id), line, f"line id '{line_id}'")
        self.line_ids[line_id] = where
        self.result.loc_rows.append((dlg_key(line_id), text))
        if note or TAG_NOTR in tags:
            self.result.note_rows.append((dlg_key(line_id), self.scene, TAG_NOTR in tags, note, text))
        words = count_words(text)
        if words > LINE_WORD_LIMIT and TAG_LONG not in tags:
            self.warn(line, f"'{line_id}' has {words} words (voice guide: about {LINE_WORD_LIMIT} or fewer; "
                            f"tag #{TAG_LONG} if the length is earned)")
        return line_id

    def register_alias(self, speaker: str, alias: str, line: int) -> str:
        """Returns the loc key for a speaker's display-name alias, adding its row the first time."""
        try:
            name = json.loads('"' + alias + '"').strip()
        except ValueError as e:
            raise DlgError(line, f"bad alias name: {e}") from e
        if not name:
            raise DlgError(line, 'empty alias name (write as "The girl")')
        key = alias_key(speaker, name)
        if key in self.result.alias_text:
            if self.result.alias_text[key] != name:
                raise DlgError(line, f"alias \"{name}\" and \"{self.result.alias_text[key]}\" both map to {key} "
                                     f"(first at {self.result.keys[key]}); pick distinct names")
            return key
        self._claim_key(key, line, f"alias \"{name}\"")
        self.result.alias_text[key] = name
        self.result.loc_rows.append((key, name))
        return key


def _load_ids(root: Path, rel: Path, table: str, result: CompileResult) -> set[str]:
    p = root / rel
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {str(r["id"]) for r in data[table]}
    except (OSError, ValueError, KeyError, TypeError) as e:
        result.errors.append(f"{rel.as_posix()}: cannot read '{table}' table: {e}")
        return set()


def _load_json(root: Path, rel: Path, result: CompileResult) -> dict:
    try:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        result.errors.append(f"{rel.as_posix()}: cannot read: {e}")
        return {}
    if not isinstance(data, dict):
        result.errors.append(f"{rel.as_posix()}: must be a JSON object")
        return {}
    return data


def load_vocab(root: Path, result: CompileResult) -> Vocab:
    """cues.json + events.json + emotions. Shape errors go to result.errors (validate_data checks deeper)."""
    vocab = Vocab(emotions=_load_ids(root, EMOTIONS_JSON, "emotions", result))
    cues = _load_json(root, CUES_JSON, result)
    for name in ("cues", "sets", "reserved"):
        value = cues.get(name, {})
        if not isinstance(value, dict):
            result.errors.append(f"{CUES_JSON.as_posix()}: '{name}' must be an object")
            value = {}
        setattr(vocab, name, value)
    events = _load_json(root, EVENTS_JSON, result).get("events", [])
    if not isinstance(events, list):
        result.errors.append(f"{EVENTS_JSON.as_posix()}: 'events' must be a list")
        events = []
    vocab.events = {str(e["id"]): e for e in events if isinstance(e, dict) and "id" in e}
    return vocab


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
    grades = ctx.vocab.sets.get("grades", [])
    for n in nodes:
        if "grade" in n.headers and n.headers["grade"] not in grades:
            ctx.error(n.line, f"unknown grade '{n.headers['grade']}' (set 'grades' in {CUES_JSON.as_posix()})")
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


def render_notes(rows: list[tuple[str, str, bool, str, str]]) -> str:
    """Translator notes, tab-separated (a .tsv, so Godot does not import it as a translation)."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(["keys", "scene", "do_not_translate", "note", "en"])
    for key, scene, notr, note, text in rows:
        w.writerow([key, scene, "yes" if notr else "", note, text])
    return buf.getvalue()


def compile_project(root: Path, assign: Path | None = None) -> CompileResult:
    """Compiles every .dlg. With `assign` (a .dlg path), lines missing a #line: id in that file are
    listed in result.missing_ids instead of being errors (see assign_ids)."""
    result = CompileResult()
    speakers = _load_ids(root, SPEAKERS_JSON, "speakers", result)
    vocab = load_vocab(root, result)
    line_ids: dict[str, str] = {}
    scenes: dict[str, str] = {}
    target = assign.resolve() if assign is not None else None
    for path in source_files(root):
        rel = path.relative_to(root).as_posix()
        ctx = FileCtx(rel, speakers, vocab, line_ids, result, assigning=path.resolve() == target)
        if path.stem in scenes:
            ctx.error(1, f"scene name '{path.stem}' is already used by {scenes[path.stem]} (compiled names are flat)")
            continue
        scenes[path.stem] = rel
        compiled = compile_file(path, rel, ctx)
        if compiled is not None:
            out = (COMPILED_DIR / f"{path.stem}.json").as_posix()
            result.outputs[out] = render_scene(compiled)
    result.outputs[LOC_CSV.as_posix()] = render_csv(result.loc_rows)
    result.outputs[NOTES_TSV.as_posix()] = render_notes(result.note_rows)
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


def check_report(root: Path) -> tuple[list[str], list[str]]:
    """(errors, warnings). Errors are compile errors plus stale outputs; empty means fresh."""
    result = compile_project(root)
    errors = list(result.errors)
    if not errors:
        for rel in stale_outputs(root, result):
            errors.append(f"{rel}: dialogue output is stale (run python3 tools/dlgc.py)")
    return errors, list(result.warnings)


def check(root: Path) -> list[str]:
    """Compile errors plus staleness errors; empty means the committed outputs are fresh."""
    return check_report(root)[0]


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


# ---------------------------------------------------------------- --assign-ids

ID_NUM_RE = re.compile(r"^(.*)_(\d+)$")


def short_scene_prefix(scene: str) -> str:
    """The fallback id prefix: the scene name's first and last words (`ch02_girl_on_the_beach` ->
    `ch02_beach`, after the `<chapter>_<scene-short>` convention); a name of one or two words as is."""
    words = [w for w in scene.split("_") if w]
    return f"{words[0]}_{words[-1]}" if len(words) > 2 else scene


def default_prefix(ids: list[str], scene: str) -> str:
    """The most common `<prefix>` of the file's `<prefix>_<NNN>` ids (first seen wins a tie), else the
    scene name shortened by short_scene_prefix."""
    counts: dict[str, int] = {}
    for lid in ids:
        m = ID_NUM_RE.match(lid)
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    if not counts:
        return short_scene_prefix(scene)
    return max(counts, key=lambda k: counts[k])  # dicts keep first-seen order; max keeps the first maximum


@dataclass
class AssignResult:
    text: str | None  # the rewritten file, or None when there are errors
    assigned: list[tuple[int, str]]  # (source line, new id)
    errors: list[str]
    hint: str = ""  # advice to print (e.g. when the prefix fell back to the scene name)


def assign_ids(root: Path, path: Path, prefix: str | None = None) -> AssignResult:
    """Fills each missing #line: id in `path` with `<prefix>_<NNN>`, counting on from the highest number
    the prefix already uses anywhere in the project (zero-padded to 3 digits, or wider if the prefix
    already is). Existing ids are never changed, and an id in use anywhere is skipped. Pure: returns
    the new text; the caller writes it. Running it again on its own output assigns nothing."""
    path = path.resolve()
    try:
        rel = path.relative_to(root.resolve()).as_posix()
    except ValueError:
        return AssignResult(None, [], [f"{path}: not under {root}"])
    if path.suffix != ".dlg" or not path.exists():
        return AssignResult(None, [], [f"{rel}: not a .dlg file"])
    if prefix is not None and not LINE_ID_RE.fullmatch(prefix):
        return AssignResult(None, [], [f"bad --prefix '{prefix}' (lowercase letters, digits, underscores)"])
    result = compile_project(root, assign=path)
    if result.errors:
        return AssignResult(None, [], result.errors)
    text = path.read_text(encoding="utf-8")
    if not result.missing_ids:
        return AssignResult(text, [], [])
    placed = _ids_with_places(result)
    hint = ""
    if prefix is None:
        file_ids = [lid for lid, where in placed if where == rel]
        prefix = default_prefix(file_ids, path.stem)
        if not any(ID_NUM_RE.match(lid) for lid in file_ids):
            hint = (f"no <prefix>_<NNN> ids in this file yet, so the prefix '{prefix}' comes from the scene "
                    "name; pass --prefix <chapter>_<scene-short> to choose another")
    used = {lid for lid, _ in placed}
    numbers = [m for m in (ID_NUM_RE.match(lid) for lid in used) if m and m.group(1) == prefix]
    width = max([3] + [len(m.group(2)) for m in numbers])
    n = max([0] + [int(m.group(2)) for m in numbers])
    lines = text.splitlines(keepends=True)
    assigned: list[tuple[int, str]] = []
    for no, _what in sorted(result.missing_ids):
        n += 1
        while f"{prefix}_{n:0{width}d}" in used:
            n += 1
        new_id = f"{prefix}_{n:0{width}d}"
        used.add(new_id)
        lines[no - 1] = _insert_line_tag(lines[no - 1], new_id)
        assigned.append((no, new_id))
    return AssignResult("".join(lines), assigned, [], hint)


def _ids_with_places(result: CompileResult) -> list[tuple[str, str]]:
    """(line id, repo-relative file) for every registered line id, in registration order."""
    out: list[tuple[str, str]] = []
    for key, where in result.keys.items():
        if key not in result.alias_text:
            out.append((key[len("DLG_"):].lower(), where.rsplit(":", 1)[0]))
    return out


def _insert_line_tag(raw: str, line_id: str) -> str:
    """Appends ` #line:<id>` after the statement's text and tags, before any // comment."""
    body = raw.rstrip("\r\n")
    ending = raw[len(body):]
    m = COMMENT_RE.search(body)
    code = body[: m.start() if m else len(body)].rstrip()
    return f"{code} #line:{line_id}{body[len(code):]}{ending}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--check", action="store_true", help="fail if committed outputs are stale; write nothing")
    ap.add_argument("--assign-ids", type=Path, metavar="FILE", help="fill missing #line: ids in FILE, in place")
    ap.add_argument("--prefix", help="id prefix for --assign-ids")
    args = ap.parse_args(argv)
    if args.assign_ids is not None:
        res = assign_ids(args.root, args.assign_ids, args.prefix)
        for e in res.errors:
            print(f"ERROR {e}")
        if res.text is None:
            return 1
        for no, lid in res.assigned:
            print(f"{args.assign_ids}:{no}: #line:{lid}")
        if res.hint:
            print(f"NOTE  {res.hint}")
        if res.assigned:
            args.assign_ids.write_text(res.text, encoding="utf-8")
        tail = " (now run python3 tools/dlgc.py)" if res.assigned else ""
        print(f"dlgc --assign-ids: {len(res.assigned)} id(s) assigned{tail}")
        return 0
    if args.check:
        errors, warnings = check_report(args.root)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        print(f"dlgc --check: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1 if errors else 0
    result = write(args.root)
    for w in result.warnings:
        print(f"WARN  {w}")
    for e in result.errors:
        print(f"ERROR {e}")
    n = len([k for k in result.outputs if k.endswith(".json")])
    print(f"dlgc: {n} scene(s), {len(result.loc_rows)} line(s), {len(result.errors)} error(s), "
          f"{len(result.warnings)} warning(s)")
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
