"""Edge walls for a greybox zone's walkways (the human's playtest, 2026-10-30: "you can easily fall off and start
walking in the water"). Pure Python, from the zone's greybox layout.

The walk surfaces are the blocks whose top is at the deck level (|top - DECK_Y| <= DECK_TOL_M), the sea excepted.
On a WALL_CELL_M grid, every side of a walk cell that borders a cell no walk covers (and no block standing taller
than the deck covers: a stall or a hull is already a wall) gets a wall. Runs along a grid line merge into one box,
WALL_T_M thick, standing just outside the edge so the walk keeps its full width, WALL_H_M tall. A wall at an opening
a hideable block fills (one the story hides or shows: the storm's lost bridge) carries that block's id as
"while_hidden": the dresser turns it on only while that block is hidden.

    walls(layout, hideable) -> [{"pos": [x, y, z], "size": [x, y, z], "yaw": 0, "while_hidden"?: id}]

Blocks with a yaw are rasterised in their own frame; the walls are axis-aligned on the grid (a yawed walk gets a
stepped edge, WALL_CELL_M fine).
"""

from __future__ import annotations

import math

WALL_CELL_M = 0.25
WALL_T_M = 0.12
WALL_H_M = 1.6
DECK_Y = 0.0
DECK_TOL_M = 0.3
SEA_IDS = ("Sea",)


def _top(b: dict) -> float:
    return b["pos"][1] + b["size"][1] / 2


def _covers(b: dict, x: float, z: float) -> bool:
    a = math.radians(float(b.get("yaw", 0.0)))
    dx, dz = x - b["pos"][0], z - b["pos"][2]
    lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
    return abs(lx) <= b["size"][0] / 2 and abs(lz) <= b["size"][2] / 2


def _bounds(blocks: list[dict]) -> tuple[float, float, float, float]:
    xs, zs = [], []
    for b in blocks:
        r = math.hypot(b["size"][0], b["size"][2]) / 2
        xs += [b["pos"][0] - r, b["pos"][0] + r]
        zs += [b["pos"][2] - r, b["pos"][2] + r]
    return min(xs) - 1.0, max(xs) + 1.0, min(zs) - 1.0, max(zs) + 1.0


def hideable_ids(layout: dict, extra: tuple = ()) -> set[str]:
    """Every block id the layout names outside its block list (a storm's hide/show rows, a lashing's frees), plus
    `extra` (ids a chapter flow's hide_block / show_block steps name)."""
    ids = {b["id"] for b in layout["blocks"]}
    found: set[str] = set(i for i in extra if i in ids)

    def walk(o) -> None:
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and o in ids:
            found.add(o)

    for k, v in layout.items():
        if k != "blocks":
            walk(v)
    return found


def walls(layout: dict, hideable: set[str]) -> list[dict]:
    blocks = layout["blocks"]
    walks = [b for b in blocks if b["id"] not in SEA_IDS and abs(_top(b) - DECK_Y) <= DECK_TOL_M]
    tall = [b for b in blocks if b["id"] not in SEA_IDS and _top(b) > DECK_Y + DECK_TOL_M
            and b["pos"][1] - b["size"][1] / 2 <= DECK_Y + 0.5]
    x0, x1, z0, z1 = _bounds(walks)
    n = WALL_CELL_M
    x0, z0 = math.floor(x0 / n) * n, math.floor(z0 / n) * n  # cell lines on the blocks' edges
    nx, nz = int((x1 - x0) / n) + 1, int((z1 - z0) / n) + 1

    def owners(i: int, k: int) -> frozenset:
        x, z = x0 + (i + 0.5) * n, z0 + (k + 0.5) * n
        return frozenset(b["id"] for b in walks if _covers(b, x, z))

    def blocked(i: int, k: int) -> bool:
        x, z = x0 + (i + 0.5) * n, z0 + (k + 0.5) * n
        return any(_covers(b, x, z) and b["id"] not in hideable for b in tall)

    cell = {(i, k): owners(i, k) for i in range(nx) for k in range(nz)}
    # Edges: (axis, line index, run index, side, tag). axis "x": a wall along X at z line k (between rows k-1, k).
    edges: dict[tuple, str | None] = {}
    for (i, k), own in cell.items():
        if not own:
            continue
        for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = cell.get((i + di, k + dk), frozenset())
            here_always = own - hideable
            tag: str | None
            if not nb:
                if blocked(i + di, k + dk):
                    continue
                tag = None  # (a hideable walk's own rim goes with it: harmless over the water once it's gone)
            elif nb - hideable:
                continue  # walk on both sides, always
            elif here_always:
                tag = sorted(nb)[0]  # the far side is a hideable walk: a wall while it's hidden
            else:
                continue
            if di:
                edges[("z", i + (1 if di > 0 else 0), k, di, tag)] = tag
            else:
                edges[("x", k + (1 if dk > 0 else 0), i, dk, tag)] = tag
    out = []
    keys = sorted(edges, key=lambda e: (e[0], e[1], e[3], str(e[4]), e[2]))
    run: list = []

    def flush() -> None:
        if not run:
            return
        axis, line, _r, side, tag = run[0]
        a, b = run[0][2], run[-1][2] + 1
        length = (b - a) * n
        if axis == "x":
            z = z0 + line * n + side * WALL_T_M / 2
            x = x0 + (a + b) / 2 * n
            row = {"pos": [round(x, 3), DECK_Y + WALL_H_M / 2, round(z, 3)], "size": [round(length, 3), WALL_H_M, WALL_T_M]}
        else:
            x = x0 + line * n + side * WALL_T_M / 2
            z = z0 + (a + b) / 2 * n
            row = {"pos": [round(x, 3), DECK_Y + WALL_H_M / 2, round(z, 3)], "size": [WALL_T_M, WALL_H_M, round(length, 3)]}
        row["yaw"] = 0.0
        if tag:
            row["while_hidden"] = tag
        out.append(row)
        run.clear()

    for e in keys:
        if run and (e[0], e[1], e[3], e[4]) == (run[-1][0], run[-1][1], run[-1][3], run[-1][4]) and e[2] == run[-1][2] + 1:
            run.append(e)
        else:
            flush()
            run.append(e)
    flush()
    return out
