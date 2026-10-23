"""GDScript source instrumentation for line coverage (M1-QA-03, ADR 0013).

`instrument(source, first_id)` parses a script with gdtoolkit's Lark parser and returns a copy in
which every executable statement reports to the recorder `HymnCov` (tools/coverage/hymn_cov.gd)
before it runs. Edits never add or remove a line, so Godot error messages and backtraces keep the
original line numbers.

Probe shapes:
  simple statement (var, expression, return, pass, break, continue, const, breakpoint)
      `stmt`             ->  `HymnCov.h(N); stmt`          (works in inline suites and lambdas too)
  if / elif / while condition
      `if cond:`         ->  `if HymnCov.t(N) and (cond):`  (t() returns true; `and` booleanizes
                                                             exactly as the bare `if` would)
  for iterable, match subject
      `for x in e:`      ->  `for x in (e if HymnCov.t(N) else e):`  (same static type, evaluated once)
      `for i in range(a, b):` -> `for i in range((a if HymnCov.t(N) else a), b):` so the analyzer still
                                 types `i` as int (it special-cases a literal `range()` call)

`else:` lines and match patterns are not counted as executable; their bodies are. A multi-line
statement counts once, on its first line. Class-level `var`/`const` initializers are not counted.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from gdtoolkit.parser import parser
from lark import Token, Tree

RECORDER = "HymnCov"

SIMPLE_STMTS = frozenset(
    {
        "pass_stmt",
        "return_stmt",
        "func_var_stmt",
        "break_stmt",
        "breakpoint_stmt",
        "continue_stmt",
        "expr_stmt",
        "const_stmt",
    }
)
# Function-like nodes whose children are statements.
FUNC_NODES = frozenset({"func_def", "property_custom_setter", "property_custom_getter"})


@dataclass
class Probe:
    id: int
    line: int  # 1-based line in the original source
    func: str  # qualified function name ("Inner.f", "hp.set"); lambdas count toward their parent
    kind: str  # "stmt" | "cond" | "iter"


@dataclass
class _Edit:
    start: int
    end: int  # == start for insertions
    kind: str  # "insert" | "cond" | "dup"
    probe: int
    text: str = ""


@dataclass
class Result:
    source: str
    probes: list[Probe] = field(default_factory=list)
    functions: dict[str, int] = field(default_factory=dict)  # qualified name -> header line


class _Walker:
    def __init__(self, first_id: int) -> None:
        self.next_id = first_id
        self.edits: list[_Edit] = []
        self.probes: list[Probe] = []
        self.functions: dict[str, int] = {}

    def _probe(self, line: int, func: str, kind: str) -> int:
        pid = self.next_id
        self.next_id += 1
        self.probes.append(Probe(pid, line, func, kind))
        return pid

    # -- class level ---------------------------------------------------------------------------
    def walk_class(self, node: Tree, prefix: str) -> None:
        last_var = "?"
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            kind = child.data
            if kind in ("class_var_stmt", "static_class_var_stmt"):
                last_var = _var_name(child)
            elif kind == "class_def":
                self.walk_class(child, prefix + _first_name(child) + ".")
            elif kind == "static_func_def":
                self.walk_func(child.children[0], prefix)
            elif kind == "func_def":
                self.walk_func(child, prefix)
            elif kind == "property_body_def":
                for etter in child.children:
                    if isinstance(etter, Tree) and etter.data in FUNC_NODES:
                        suffix = "set" if etter.data == "property_custom_setter" else "get"
                        name = f"{prefix}{last_var}.{suffix}"
                        self.functions.setdefault(name, etter.meta.line)
                        self.walk_body(etter.children, name)

    def walk_func(self, node: Tree, prefix: str) -> None:
        header = node.children[0]
        name = prefix + _first_name(header)
        self.functions.setdefault(name, node.meta.line)
        self.walk_body(node.children[1:], name)

    # -- function level ------------------------------------------------------------------------
    def walk_body(self, children: list, func: str) -> None:
        for child in children:
            if isinstance(child, Tree):
                self.walk_stmt(child, func)

    def walk_stmt(self, node: Tree, func: str) -> None:
        kind = node.data
        if kind in SIMPLE_STMTS:
            pid = self._probe(node.meta.line, func, "stmt")
            self.edits.append(_Edit(node.meta.start_pos, node.meta.start_pos, "insert", pid, f"{RECORDER}.h({pid}); "))
            self.walk_expr(node, func)
        elif kind == "if_stmt":
            for branch in node.children:
                if not isinstance(branch, Tree):
                    continue
                if branch.data in ("if_branch", "elif_branch"):
                    self._wrap_cond(branch.children[0], branch.meta.line, func)
                    self.walk_body(branch.children[1:], func)
                elif branch.data == "else_branch":
                    self.walk_body(branch.children, func)
        elif kind == "while_stmt":
            self._wrap_cond(node.children[0], node.meta.line, func)
            self.walk_body(node.children[1:], func)
        elif kind in ("for_stmt", "for_stmt_typed"):
            idx = next(i for i, c in enumerate(node.children) if isinstance(c, Tree) and c.data == "expr")
            self._wrap_iter(node.children[idx], node.meta.line, func)
            self.walk_body(node.children[idx + 1 :], func)
        elif kind == "match_stmt":
            self._wrap_dup(node.children[0], node.meta.line, func)
            for branch in node.children[1:]:
                if not isinstance(branch, Tree):
                    continue
                # match_branch: pattern, stmts... | guarded_match_branch: pattern, guard expr, stmts...
                skip = 2 if branch.data == "guarded_match_branch" else 1
                if skip == 2:
                    self.walk_expr(branch.children[1], func)
                self.walk_body(branch.children[skip:], func)
        elif kind == "annotation":
            pass  # @warning_ignore etc.: applies to the next statement, carries no runtime code
        # anything else (e.g. a statement kind added in a newer grammar) is left untouched

    def walk_expr(self, node: Tree, func: str) -> None:
        """Instruments the bodies of lambdas found inside an expression (or simple statement)."""
        stack = [c for c in reversed(node.children) if isinstance(c, Tree)]
        while stack:
            cur = stack.pop()
            if cur.data == "lambda":
                self.walk_body(cur.children[1:], func)  # nested lambdas are reached from there
            else:
                stack.extend(c for c in reversed(cur.children) if isinstance(c, Tree))

    # -- wrappers ------------------------------------------------------------------------------
    def _wrap_cond(self, expr: Tree, line: int, func: str) -> None:
        pid = self._probe(line, func, "cond")
        self.edits.append(_Edit(expr.meta.start_pos, expr.meta.end_pos, "cond", pid))
        self.walk_expr(expr, func)

    def _wrap_dup(self, expr: Tree, line: int, func: str) -> None:
        pid = self._probe(line, func, "iter")
        self.edits.append(_Edit(expr.meta.start_pos, expr.meta.end_pos, "dup", pid))
        self.walk_expr(expr, func)

    def _wrap_iter(self, expr: Tree, line: int, func: str) -> None:
        call = _range_call(expr)
        if call is None:
            self._wrap_dup(expr, line, func)
            return
        args = [c for c in call.children[1:] if not (isinstance(c, Tree) and c.data == "trailing_comma")]
        if not args:
            self.walk_expr(expr, func)  # range() with no args is a Godot error anyway
            return
        pid = self._probe(line, func, "iter")
        start, end = _span(args[0])
        self.edits.append(_Edit(start, end, "dup", pid))
        self.walk_expr(expr, func)


def _range_call(expr: Tree) -> Tree | None:
    """The `standalone_call` node if `expr` is exactly `range(...)`."""
    node = expr
    while isinstance(node, Tree) and node.data == "expr" and len(node.children) == 1:
        node = node.children[0]
    if (
        isinstance(node, Tree)
        and node.data == "standalone_call"
        and isinstance(node.children[0], Token)
        and str(node.children[0]) == "range"
    ):
        return node
    return None


def _span(node: Tree | Token) -> tuple[int, int]:
    if isinstance(node, Token):
        return node.start_pos, node.end_pos
    return node.meta.start_pos, node.meta.end_pos


def _first_name(node: Tree) -> str:
    for c in node.children:
        if isinstance(c, Token) and c.type == "NAME":
            return str(c)
    return "?"


def _var_name(node: Tree) -> str:
    for sub in node.iter_subtrees_topdown():
        name = _first_name(sub)
        if name != "?":
            return name
    return "?"


def _render(src: str, edits: list[_Edit], a: int, b: int) -> str:
    """Applies `edits` (sorted by start, outermost first) to src[a:b]; wraps recurse into their span."""
    out: list[str] = []
    cur = a
    for e in edits:
        if e.start < cur or e.end > b or (e.kind == "insert" and e.start >= b):
            continue  # already emitted inside an enclosing wrap, or outside this span
        out.append(src[cur : e.start])
        if e.kind == "insert":
            out.append(e.text)
            cur = e.start
            continue
        inner_edits = [x for x in edits if x is not e and e.start <= x.start and x.end <= e.end]
        inner = _render(src, inner_edits, e.start, e.end)
        if e.kind == "cond":
            out.append(f"{RECORDER}.t({e.probe}) and ({inner})")
        else:
            out.append(f"({inner} if {RECORDER}.t({e.probe}) else {inner})")
        cur = e.end
    out.append(src[cur:b])
    return "".join(out)


def instrument(source: str, first_id: int = 0) -> Result:
    """Returns the instrumented source and its probes (ids first_id, first_id+1, ...)."""
    tree = parser.parse(source, gather_metadata=True)
    walker = _Walker(first_id)
    walker.walk_class(tree, "")
    edits = sorted(walker.edits, key=lambda e: (e.start, -e.end))
    rendered = _render(source, edits, 0, len(source))
    probes = sorted(walker.probes, key=lambda p: p.id)
    return Result(rendered, probes, walker.functions)
