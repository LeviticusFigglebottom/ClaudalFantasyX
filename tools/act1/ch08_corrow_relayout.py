#!/usr/bin/env python3
"""One-time migration (M3-C08-1202, ADR 0200): moves Ch8's flat greybox `ch08/corrow` layout into the Corrow kit's
frame (tools/act1/corrow_frame.py). Run once against the M3-C08-02 greybox; the result is hand-tuned afterwards, so
it is kept for the record (it documents the map), not re-run:

    python3 tools/act1/ch08_corrow_relayout.py  # reads and rewrites game/levels/ch08/corrow/corrow_layout.json

Spawns, marks, actors, shots and triggers go through `to_kit`. The story blocks (props the states show and hide)
are mapped; the geometry blocks (ground, sea, wall, walk, stair, houses, the Bastion's ground) are dropped: the kit
dresses them and tools/act1/ch08_corrow_dressing.py writes their collision (corrow_collision.json).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corrow_frame as cf  # noqa: E402

LAYOUT = cf.ROOT / "game" / "levels" / "ch08" / "corrow" / "corrow_layout.json"
GEOMETRY = {"Ground", "BoundW", "BoundE", "BoundS", "BoundN", "SeaW", "SeaE", "Mole", "Shingle", "SeaWallW",
            "WallSection", "SeaWallE1", "SeaWallE2", "WatchersW", "WatchersSection", "WatchersE", "PaleBlocks",
            "WallHead", "StairHead", "FisherStair", "HandLine", "StairFoot", "LowTown", "HouseA", "HouseB", "HouseC",
            "HouseD", "Bastion", "OuterParapet"}
# Liss's hoist is at the kit's hoist head (s -16.5), 3.5 m east of where the flat map puts it.
HOIST = {"HoistPins", "HoistRope", "Basket", "RopeCoil", "hoist_liss", "hoist_officer", "hoist_toma", "liss_coil",
         "basket_low_a", "basket_low_b", "basket_low_c", "basket_top_a", "basket_top_b", "basket_top_c"}
HOIST_DS = cf.HOIST_S - (-5.0 + cf.S_SHIFT)
# Points the region map can't place: the breach is the kit's (the stair's middle, s -36 .. -24), and the Watchers'
# mouths and Pell's perch are on the parapet. Values: (s, y, wall-frame z, yaw offset).
SPECIAL = {
    "breach_lip": (-23.0, cf.WALK_Y, 1.0, 90.0),
    "watchers_mouths": (-20.0, cf.HEAD_Y + 1.5, cf.HEAD_Z, 0.0),
    "parapet_pell": (-7.0, cf.HEAD_Y, cf.HEAD_Z, 0.0),
    "pell": (-7.0, cf.HEAD_Y, cf.HEAD_Z, 0.0),
    "hobb_after": (-21.0, cf.WALK_Y, -1.0, 0.0),
    "officer_post": (-22.5, cf.WALK_Y, 0.5, 90.0),
}
BREACH_BLOCK = (-30.0, 6.0, 0.0)


def place(name: str, x: float, y: float, z: float, yaw: float = 0.0) -> tuple[float, float, float, float]:
    if name in SPECIAL:
        s, yy, zl, dyaw = SPECIAL[name]
        wx, wy, wz, a = cf.arc(s, yy, zl)
        return wx, wy, wz, yaw + dyaw + a
    if name in HOIST:
        wx, wy, wz, a = cf.to_kit(x, y, z, yaw)
        s = x + cf.S_SHIFT + HOIST_DS
        zl = max(-2.2, min(2.7, (z - cf.GB_WALK_Z) * 0.5))
        bx, by, bz, ba = cf.arc(s, wy, zl)
        return bx, by, bz, yaw + ba
    return cf.to_kit(x, y, z, yaw)


def mark(name: str, p: list) -> list:
    x, y, z, yaw = place(name, p[0], p[1], p[2], p[3] if len(p) > 3 else 0.0)
    return [cf.r3(x), cf.r3(y), cf.r3(z), cf.yaw_norm(yaw)]


def point(name: str, p: list) -> list:
    x, y, z, _yaw = place(name, p[0], p[1], p[2])
    return [cf.r3(x), cf.r3(y), cf.r3(z)]


def main() -> None:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    blocks = []
    for b in g["blocks"]:
        if b["id"] in GEOMETRY:
            continue
        p = b["pos"]
        if b["id"] == "Breach":
            x, y, z, a = cf.arc(*BREACH_BLOCK)
        else:
            x, y, z, a = place(b["id"], p[0], p[1] - b["size"][1] * 0.5, p[2])
            y += b["size"][1] * 0.5
        b = dict(b, pos=[cf.r3(x), cf.r3(y), cf.r3(z)], yaw=cf.yaw_norm(float(b.get("yaw", 0.0)) + a))
        blocks.append(b)
    g["blocks"] = blocks
    g["spawns"] = {k: mark(k, v) for k, v in g["spawns"].items()}
    g["marks"] = {k: mark(k, v) for k, v in g["marks"].items()}
    g["actors"] = {k: dict(v, at=mark(k, v["at"])) for k, v in g["actors"].items()}
    g["shots"] = {k: dict(v, pos=point(k, v["pos"]), look_at=point(k, v["look_at"])) for k, v in g["shots"].items()}
    for t in g["triggers"]:
        x, y, z, a = place(t["id"], t["at"][0], t["at"][1], t["at"][2])
        t["at"] = [cf.r3(x), cf.r3(y), cf.r3(z)]
        t["yaw"] = cf.yaw_norm(float(t.get("yaw", 0.0)) + a)
    g["collision_path"] = "res://game/levels/ch08/corrow/corrow_collision.json"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else LAYOUT  # a dry run writes elsewhere
    out.write_text(dump(g), encoding="utf-8")


def dump(g: dict) -> str:
    """The layout's house style: one key per line at the top, one row per line inside lists and maps."""
    out = ["{"]
    keys = list(g)
    for i, k in enumerate(keys):
        v = g[k]
        end = "," if i < len(keys) - 1 else ""
        if isinstance(v, list) and v and isinstance(v[0], dict):
            rows = [f"    {json.dumps(r, ensure_ascii=False)}" for r in v]
            out.append(f'  "{k}": [\n' + ",\n".join(rows) + f"\n  ]{end}")
        elif isinstance(v, dict) and k in ("spawns", "marks", "actors", "shots"):
            rows = [f'    "{kk}": {json.dumps(vv, ensure_ascii=False)}' for kk, vv in v.items()]
            out.append(f'  "{k}": {{\n' + ",\n".join(rows) + f"\n  }}{end}")
        else:
            out.append(f'  "{k}": {json.dumps(v, ensure_ascii=False)}{end}')
    out.append("}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
