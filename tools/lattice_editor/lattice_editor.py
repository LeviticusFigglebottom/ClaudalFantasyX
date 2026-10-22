#!/usr/bin/env python3
"""Lattice editor (SPEC §6.4): builds, checks, and previews Lattice boards from a compact source.

The committed board JSON (game/data/progression/lattice_<id>.json) is GENERATED from a `.lat` source
in tools/lattice_editor/sections/. Edit the source, then rebuild. Format and design notes live in
docs/kb/design/lattice.md.

Commands:
  build [SRC] [--out JSON]   parse SRC, lay it out, check it, write the board JSON
  check [SRC] [--json JSON]  parse + geometry + data checks, and verify JSON matches the source
  svg   [SRC] [--out SVG]    write an SVG preview (default tools/lattice_editor/out/<board>.svg)
  stats [SRC]                print node counts per region and type

Exit code 1 on any error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

DEFAULT_SRC = HERE / "sections" / "standard.lat"
OUT_DIR = HERE / "out"
DATA_DIR = ROOT / "game" / "data" / "progression"

DIRS: dict[str, tuple[int, int]] = {
    "E": (1, 0), "W": (-1, 0), "N": (0, -1), "S": (0, 1),
    "NE": (1, -1), "NW": (-1, -1), "SE": (1, 1), "SW": (-1, 1),
}
NODE_KEY_ORDER = ["id", "type", "stat", "value", "skill", "gate_level", "character", "x", "y", "region"]
STAT_TOKEN = re.compile(r"^([a-z_]+)\+(\d+)$")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# SVG preview styling (tool-only; not game data).
SVG_SCALE = 34
SVG_MARGIN = 2
SVG_RADIUS = 9
FACET_COLORS = {"power": "#d0574a", "mind": "#4a7fd0", "speed": "#4fae6a", "fortune": "#d9b440"}
TYPE_COLORS = {"ability": "#b07ad8", "gate": "#2b2b33", "empty": "#f4f1ea", "start": "#ffffff"}
REGION_COLORS = {"rhen": "#2f8f8a", "asha": "#3b64b5", "toma": "#b04a3a", "cross": "#777777", "hub": "#a08a2a"}
SHORT_STAT = {"hp": "HP", "mp": "MP", "strength": "STR", "magic": "MAG", "defense": "DEF",
              "magic_defense": "MDF", "agility": "AGI", "accuracy": "ACC", "evasion": "EVA", "luck": "LCK"}


class LatError(Exception):
    pass


@dataclass
class Board:
    id: str = ""
    name_key: str = ""
    nodes: list[dict] = field(default_factory=list)
    edges: list[list[str]] = field(default_factory=list)
    source: str = ""

    def node(self, nid: str) -> dict | None:
        for n in self.nodes:
            if n["id"] == nid:
                return n
        return None

    def to_json_dict(self) -> dict:
        return {
            "board": {"id": self.id, "name_key": self.name_key, "source": self.source},
            "nodes": [{k: n[k] for k in NODE_KEY_ORDER if k in n} for n in self.nodes],
            "edges": self.edges,
        }


def _payload(token: str, where: str) -> dict:
    """Turns one node token into node fields (without id/position)."""
    if token == "_":
        return {"type": "empty"}
    if token.startswith("#"):
        if not token[1:].isdigit():
            raise LatError(f"{where}: gate token must be #<level>, got '{token}'")
        return {"type": "gate", "gate_level": int(token[1:])}
    if token.startswith("@"):
        if not ID_RE.match(token[1:]):
            raise LatError(f"{where}: bad skill id in '{token}'")
        return {"type": "ability", "skill": token[1:]}
    m = STAT_TOKEN.match(token)
    if m:
        return {"type": "stat", "stat": m.group(1), "value": int(m.group(2))}
    raise LatError(f"{where}: unknown token '{token}' (use stat+N, @skill, #level, or _)")


def parse(text: str, source: str = "") -> Board:
    """Parses `.lat` text into a laid-out Board. Raises LatError on syntax errors."""
    b = Board(source=source)
    region = ""
    links: list[tuple[str, str, str]] = []

    def add_node(nid: str, fields: dict, x: int, y: int, where: str) -> None:
        if not ID_RE.match(nid):
            raise LatError(f"{where}: bad node id '{nid}'")
        if b.node(nid) is not None:
            raise LatError(f"{where}: duplicate node id '{nid}'")
        n = {"id": nid, **fields, "x": x, "y": y}
        if region:
            n["region"] = region
        b.nodes.append(n)

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0] if raw.lstrip().startswith("#") else raw
        line = re.sub(r"\s+#\s.*$", "", line).strip()
        if not line:
            continue
        where = f"{source or '<lat>'}:{lineno}"
        words = line.split()
        cmd = words[0]
        if cmd == "board":
            if len(words) < 2:
                raise LatError(f"{where}: board <id> name_key=KEY")
            b.id = words[1]
            for w in words[2:]:
                if w.startswith("name_key="):
                    b.name_key = w.split("=", 1)[1]
        elif cmd == "region":
            if len(words) != 2:
                raise LatError(f"{where}: region <name>")
            region = words[1]
        elif cmd in ("node", "start"):
            # node <id> <token> @ x y     |     start <id> <character> @ x y
            if len(words) != 6 or words[3] != "@":
                raise LatError(f"{where}: {cmd} <id> <{'character' if cmd == 'start' else 'token'}> @ <x> <y>")
            fields = {"type": "start", "character": words[2]} if cmd == "start" else _payload(words[2], where)
            add_node(words[1], fields, int(words[4]), int(words[5]), where)
        elif cmd == "link":
            if len(words) != 3:
                raise LatError(f"{where}: link <a> <b>")
            links.append((words[1], words[2], where))
        elif cmd == "walk":
            _parse_walk(line, where, b, add_node, links)
        else:
            raise LatError(f"{where}: unknown command '{cmd}'")
    for a, c, where in links:
        if b.node(a) is None or b.node(c) is None:
            raise LatError(f"{where}: link to unknown node ({a} -> {c})")
        b.edges.append([a, c])
    if not b.id:
        raise LatError(f"{source}: missing 'board' line")
    return b


def _parse_walk(line: str, where: str, b: Board, add_node, links: list[tuple[str, str, str]]) -> None:
    # walk <name> from <node> <DIR> [step=N]: tokens... [-> <node>]
    head, sep, body = line.partition(":")
    hw = head.split()
    if not sep or len(hw) < 5 or hw[2] != "from" or hw[4] not in DIRS:
        raise LatError(f"{where}: walk <name> from <node> <DIR> [step=N]: tokens... [-> node]")
    name, origin, direction = hw[1], hw[3], DIRS[hw[4]]
    step = 1
    for opt in hw[5:]:
        if opt.startswith("step="):
            step = int(opt.split("=", 1)[1])
        else:
            raise LatError(f"{where}: unknown walk option '{opt}'")
    prev = b.node(origin)
    if prev is None:
        raise LatError(f"{where}: walk starts at unknown node '{origin}'")
    tokens = body.split()
    tail = None
    if "->" in tokens:
        i = tokens.index("->")
        if i != len(tokens) - 2:
            raise LatError(f"{where}: '-> <node>' must end the walk")
        tail = tokens[i + 1]
        tokens = tokens[:i]
    x, y = prev["x"], prev["y"]
    last = origin
    count = 0
    for tok in tokens:
        if tok.startswith(">"):
            if tok[1:] not in DIRS:
                raise LatError(f"{where}: unknown direction '{tok}'")
            direction = DIRS[tok[1:]]
            continue
        count += 1
        nid = f"{name}_{count:02d}"
        if "=" in tok:
            nid, tok = tok.split("=", 1)
        x += direction[0] * step
        y += direction[1] * step
        add_node(nid, _payload(tok, where), x, y, where)
        b.edges.append([last, nid])
        last = nid
    if count == 0:
        raise LatError(f"{where}: walk '{name}' places no nodes")
    if tail:
        links.append((last, tail, where))


def _on_segment(p: tuple[int, int], a: tuple[int, int], c: tuple[int, int]) -> bool:
    cross = (c[0] - a[0]) * (p[1] - a[1]) - (c[1] - a[1]) * (p[0] - a[0])
    if cross != 0:
        return False
    return min(a[0], c[0]) <= p[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= p[1] <= max(a[1], c[1])


def _segments_cross(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int], d: tuple[int, int]) -> bool:
    def orient(p: tuple[int, int], q: tuple[int, int], r: tuple[int, int]) -> int:
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return (v > 0) - (v < 0)
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0


def geometry_report(b: Board) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings): overlapping nodes, nodes sitting on an edge, crossing edges."""
    errs: list[str] = []
    warns: list[str] = []
    pos = {n["id"]: (n["x"], n["y"]) for n in b.nodes}
    seen: dict[tuple[int, int], str] = {}
    for nid, p in pos.items():
        if p in seen:
            errs.append(f"nodes '{seen[p]}' and '{nid}' overlap at {p}")
        seen[p] = nid
    segs = [(e[0], e[1], pos[e[0]], pos[e[1]]) for e in b.edges if e[0] in pos and e[1] in pos]
    for a, c, pa, pc in segs:
        for nid, p in pos.items():
            if nid not in (a, c) and _on_segment(p, pa, pc):
                errs.append(f"node '{nid}' sits on edge [{a}, {c}] (it would read as connected)")
    for i, (a, c, pa, pc) in enumerate(segs):
        for d, e, pd, pe in segs[i + 1:]:
            if {a, c} & {d, e}:
                continue
            if _segments_cross(pa, pc, pd, pe):
                warns.append(f"edges [{a}, {c}] and [{d}, {e}] cross")
    return errs, warns


def data_errors(b: Board, root: Path = ROOT) -> list[str]:
    """Runs the shared validator checks (tools/validate_data.py) against the built board."""
    def load(rel: str) -> dict:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    facets = load(vd.FACETS_FILE)
    skills = {s["id"] for s in load("game/data/battle/skills.json")["skills"]}
    chars = {c["id"] for c in load("game/data/battle/characters.json")["characters"]}
    max_level = facets.get("rules", {}).get("max_gate_level", 0)
    return vd.lattice_errors(b.to_json_dict(), max_level, skills, chars, f"board '{b.id}'")


def dump_json(b: Board) -> str:
    """Stable, diff-friendly JSON: one node and one edge per line."""
    d = b.to_json_dict()
    out = ["{", f'  "board": {json.dumps(d["board"], ensure_ascii=False)},', '  "nodes": [']
    out += [f"    {json.dumps(n, ensure_ascii=False)}," for n in d["nodes"]]
    out[-1] = out[-1].rstrip(",")
    out += ["  ],", '  "edges": [']
    out += [f"    {json.dumps(e)}," for e in d["edges"]]
    out[-1] = out[-1].rstrip(",")
    out += ["  ]", "}"]
    return "\n".join(out) + "\n"


def _facet_of(n: dict, facets: dict) -> str:
    for f in facets.get("facets", []):
        if n["type"] == "stat" and n.get("stat") in f.get("stats", []):
            return f["type"]
    return ""


def to_svg(b: Board, facets: dict) -> str:
    xs = [n["x"] for n in b.nodes]
    ys = [n["y"] for n in b.nodes]
    x0, y0 = min(xs) - SVG_MARGIN, min(ys) - SVG_MARGIN
    w = (max(xs) - x0 + SVG_MARGIN) * SVG_SCALE
    h = (max(ys) - y0 + SVG_MARGIN) * SVG_SCALE

    def px(n: dict) -> tuple[float, float]:
        return (n["x"] - x0) * SVG_SCALE, (n["y"] - y0) * SVG_SCALE

    pos = {n["id"]: px(n) for n in b.nodes}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             f'font-family="sans-serif">',
             f'<rect width="{w}" height="{h}" fill="#101822"/>',
             f'<text x="10" y="20" fill="#e8e4d8" font-size="14">Lattice: {b.id} '
             f'({len(b.nodes)} nodes, {len(b.edges)} edges)</text>']
    for a, c in b.edges:
        (ax, ay), (cx, cy) = pos[a], pos[c]
        parts.append(f'<line x1="{ax}" y1="{ay}" x2="{cx}" y2="{cy}" stroke="#6b7a8c" stroke-width="2"/>')
    for n in b.nodes:
        x, y = pos[n["id"]]
        t = n["type"]
        fill = FACET_COLORS.get(_facet_of(n, facets), TYPE_COLORS.get(t, "#999999"))
        ring = REGION_COLORS.get(n.get("region", ""), "#999999")
        r = SVG_RADIUS * (1.5 if t == "start" else 1)
        shape = (f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" fill="{fill}" '
                 f'stroke="{ring}" stroke-width="3"/>') if t == "gate" else \
                (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{ring}" stroke-width="3"/>')
        parts.append(shape)
        if t == "stat":
            label = f'{SHORT_STAT.get(n["stat"], n["stat"])}+{n["value"]}'
        elif t == "ability":
            label = n["skill"]
        elif t == "gate":
            label = f'L{n["gate_level"]}'
        elif t == "start":
            label = n["character"].upper()
        else:
            label = "empty"
        color = "#ffffff" if t == "gate" else "#e8e4d8"
        dy = 4 if t == "gate" else -SVG_RADIUS - 4
        size = 9 if t == "gate" else 8
        parts.append(f'<text x="{x}" y="{y + dy}" fill="{color}" font-size="{size}" '
                     f'text-anchor="middle">{label}</text>')
    legend = [("Power", FACET_COLORS["power"]), ("Mind", FACET_COLORS["mind"]), ("Speed", FACET_COLORS["speed"]),
              ("Fortune", FACET_COLORS["fortune"]), ("Ability", TYPE_COLORS["ability"]),
              ("Gate", TYPE_COLORS["gate"]), ("Empty", TYPE_COLORS["empty"])]
    for i, (name, col) in enumerate(legend):
        parts.append(f'<circle cx="{16}" cy="{40 + i * 16}" r="5" fill="{col}" stroke="#e8e4d8"/>')
        parts.append(f'<text x="26" y="{44 + i * 16}" fill="#e8e4d8" font-size="11">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def default_json_path(b: Board) -> Path:
    return DATA_DIR / f"lattice_{b.id}.json"


def load_source(src: Path) -> Board:
    rel = src.resolve().relative_to(ROOT).as_posix() if src.resolve().is_relative_to(ROOT) else src.name
    return parse(src.read_text(encoding="utf-8"), rel)


def check_all(b: Board, json_path: Path | None) -> tuple[list[str], list[str]]:
    errs, warns = geometry_report(b)
    errs += data_errors(b)
    if json_path is not None:
        if not json_path.exists():
            errs.append(f"{json_path}: missing (run build)")
        elif json_path.read_text(encoding="utf-8") != dump_json(b):
            errs.append(f"{json_path}: out of date with {b.source} (run build)")
    return errs, warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["build", "check", "svg", "stats"])
    ap.add_argument("src", nargs="?", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--out", type=Path, help="output path (build: JSON, svg: SVG)")
    ap.add_argument("--json", type=Path, help="check: the board JSON to compare against")
    args = ap.parse_args(argv)
    try:
        b = load_source(args.src)
    except LatError as e:
        print(f"ERROR {e}")
        return 1
    if args.command == "stats":
        counts: dict[str, dict[str, int]] = {}
        for n in b.nodes:
            reg = counts.setdefault(n.get("region", "-"), {})
            reg[n["type"]] = reg.get(n["type"], 0) + 1
        for reg, c in counts.items():
            print(f"{reg:6} {sum(c.values()):3}  " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
        print(f"total  {len(b.nodes):3} nodes, {len(b.edges)} edges")
        return 0
    if args.command == "svg":
        facets = json.loads((ROOT / vd.FACETS_FILE).read_text(encoding="utf-8"))
        out = args.out or OUT_DIR / f"lattice_{b.id}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(to_svg(b, facets), encoding="utf-8")
        print(f"wrote {out}")
        return 0
    json_path = args.json or default_json_path(b)
    errs, warns = check_all(b, json_path if args.command == "check" else None)
    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    if errs:
        return 1
    if args.command == "build":
        out = args.out or json_path
        out.write_text(dump_json(b), encoding="utf-8")
        print(f"wrote {out} ({len(b.nodes)} nodes, {len(b.edges)} edges)")
    else:
        print(f"lattice '{b.id}': OK ({len(b.nodes)} nodes, {len(b.edges)} edges, {len(warns)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
