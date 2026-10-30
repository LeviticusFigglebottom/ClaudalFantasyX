"""Edge walls for a greybox zone's walkways (the human's playtest, 2026-10-30: "you can easily fall off and start
walking in the water"). Pure Python, from the zone's greybox layout.

The walk surfaces are the blocks whose top is at the deck level (|top - DECK_Y| <= DECK_TOL_M), the sea and the
lagoons' water and beds excepted. Each walk block's four edges are walked in the block's own frame every STEP_M: a
point PROBE_M outside the edge that no other walk covers, and that no block standing taller than the deck covers (a
stall, a hull or a rail is already a wall), is open. Each run of open points becomes one wall along that edge, WALL_T_M
thick, standing just outside it (the walk keeps its full width), WALL_H_M tall, turned with the block. A run whose
points only a hideable walk covers (one the story hides or shows: the storm's lost bridge) carries that block's id as
"while_hidden": the dresser turns it on only while that block is hidden.

    walls(layout, hideable) -> [{"pos": [x, y, z], "size": [x, y, z], "yaw": deg, "while_hidden"?: id}]
"""

from __future__ import annotations

import math

STEP_M = 0.25
PROBE_M = 0.15
WALL_T_M = 0.12
WALL_H_M = 1.6
DECK_Y = 0.0
DECK_TOL_M = 0.3
SEA_IDS = ("Sea", "Water", "Bed", "Waterline")  # the sea, the lagoons and their beds: never a walk


def _top(b: dict) -> float:
    return b["pos"][1] + b["size"][1] / 2


def _covers(b: dict, x: float, z: float) -> bool:
    a = math.radians(float(b.get("yaw", 0.0)))
    dx, dz = x - b["pos"][0], z - b["pos"][2]
    lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
    return abs(lx) <= b["size"][0] / 2 and abs(lz) <= b["size"][2] / 2


def _to_world(b: dict, lx: float, lz: float) -> tuple[float, float]:
    """A point in the block's frame (Godot's rotation_degrees.y = yaw) to the zone's."""
    a = math.radians(float(b.get("yaw", 0.0)))
    return (b["pos"][0] + lx * math.cos(a) + lz * math.sin(a), b["pos"][2] - lx * math.sin(a) + lz * math.cos(a))


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
            and b["pos"][1] - b["size"][1] / 2 <= DECK_Y + 0.5 and b["id"] not in hideable]

    def state(own: dict, x: float, z: float) -> str | None:
        """'' when the point is closed (a walk always there, or a wall), the hideable walk's id when only one covers
        it, None when it is open water."""
        if any(_covers(b, x, z) for b in tall):
            return ""
        over = [b["id"] for b in walks if b is not own and _covers(b, x, z)]
        if any(i not in hideable for i in over):
            return ""
        return sorted(over)[0] if over else None

    out: list[dict] = []
    for b in walks:
        hx, hz = b["size"][0] / 2, b["size"][2] / 2
        yaw = float(b.get("yaw", 0.0))
        # The four edges: (along-axis half length, the edge's fixed local coordinate, axis, outward sign).
        for axis, half, fixed, sign in (("x", hx, hz, 1), ("x", hx, hz, -1), ("z", hz, hx, 1), ("z", hz, hx, -1)):
            n = max(1, int(round(2 * half / STEP_M)))
            step = 2 * half / n
            tags = []
            for i in range(n):
                t = -half + (i + 0.5) * step
                lx, lz = (t, sign * (fixed + PROBE_M)) if axis == "x" else (sign * (fixed + PROBE_M), t)
                tags.append(state(b, *_to_world(b, lx, lz)))
            i = 0
            while i < n:
                tag = tags[i]
                j = i
                while j + 1 < n and tags[j + 1] == tag:
                    j += 1
                if tag != "":
                    a, c = -half + i * step, -half + (j + 1) * step
                    mid, length = (a + c) / 2, c - a
                    off = sign * (fixed + WALL_T_M / 2)
                    lx, lz = (mid, off) if axis == "x" else (off, mid)
                    x, z = _to_world(b, lx, lz)
                    size = [length, WALL_H_M, WALL_T_M] if axis == "x" else [WALL_T_M, WALL_H_M, length]
                    row = {"pos": [round(x, 3), DECK_Y + WALL_H_M / 2, round(z, 3)],
                           "size": [round(v, 3) for v in size], "yaw": round(yaw, 3)}
                    if tag:
                        row["while_hidden"] = tag
                    out.append(row)
                i = j + 1
    return out
