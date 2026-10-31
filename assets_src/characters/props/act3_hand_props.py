"""Act III hand props (M5-A3P-1982; act3_ch19.md section 5). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/props/act3_hand_props.py [-- --out-dir DIR]
    # -> assets/characters/props/act3/{watch_roll,stylus}.glb and materials/*.tres

Wick.py's mesh helpers (its `Mesh`, `tube`, `make_object`, `export`, `write_material`) with this file's material table,
as act2_hand_props.py does. Each prop's origin is its grip, so a `BoneAttachment3D` on the holding hand places it:

* `watch_roll.glb`: Ilsabet Rue's watch roll, the Warden's four hundred years of watches: two dark wooden rollers
  0.26 m long with turned brass ends, and between them a 0.22 m span of the roll's pale vellum, half open, sagging a
  little. Held in the left hand by the near roller's middle: origin there, the rollers along +X, the open span along +Y.
* `stylus.glb`: her stylus, a 0.15 m bone shaft with a brass collar and a fine iron nib. Origin at the grip, a third of
  the way from the nib; the nib along -Z.

Everything is generated here; nothing is downloaded. Deterministic (no randomness, fixed tessellation).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wick as W  # noqa: E402  (the mesh helpers; its MATERIALS table is swapped for ours below)

ROOT = HERE.parents[2]
OUT_DIR = ROOT / "assets" / "characters" / "props" / "act3"
MATERIALS = {  # name: (hex, roughness, metallic)
    "roll_wood": ("#3A2A20", 0.6, 0.0),  # dark oiled roller wood
    "roll_brass": ("#B08D57", 0.38, 1.0),  # brass
    "roll_vellum": ("#E4DCC8", 0.8, 0.0),  # pale vellum, a little warm
    "stylus_bone": ("#E4DED3", 0.55, 0.0),  # bone, order_marble's tone
    "stylus_iron": ("#3A3836", 0.45, 1.0),
}
W.MATERIALS = MATERIALS
ROLL_LEN = 0.26  # m: the rollers
ROLL_R = 0.011
ROLL_SPAN = 0.22  # m: the open vellum between the rollers
ROLL_SAG = 0.012  # m: how far the open span sags
SEG = 14


def log(msg: str) -> None:
    print(f"[act3_props] {msg}", flush=True)


def line(a, b, n: int) -> np.ndarray:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return np.array([a + (b - a) * t for t in np.linspace(0.0, 1.0, n)])


def _roller(y: float) -> W.Mesh:
    m = W.Mesh()
    h = ROLL_LEN / 2
    m.extend(W.tube(line((-h, y, 0.0), (h, y, 0.0), 10), lambda t, th: ROLL_R, SEG, mat="roll_wood"))
    for sx in (-1.0, 1.0):  # the turned brass ends
        knob = line((sx * h, y, 0.0), (sx * (h + 0.016), y, 0.0), 5)
        m.extend(W.tube(knob, lambda t, th: ROLL_R * (1.25 - 0.55 * t), SEG, mat="roll_brass"))
    return m


def watch_roll() -> W.Mesh:
    m = W.Mesh()
    m.extend(_roller(0.0))
    m.extend(_roller(ROLL_SPAN))
    # the open span: a sheet from the top of one roller to the top of the other, sagging a little in the middle
    cols, rows = 2, 12
    xs = np.linspace(-ROLL_LEN / 2 + 0.01, ROLL_LEN / 2 - 0.01, cols)
    P = np.zeros((rows, cols, 3))
    for j, v in enumerate(np.linspace(0.0, 1.0, rows)):
        y = v * ROLL_SPAN
        z = ROLL_R - ROLL_SAG * math.sin(math.pi * v)
        for i, x in enumerate(xs):
            P[j, i] = (x, y, z)
    sheet = W.Mesh()
    sheet.grid(P, "roll_vellum", closed=False)
    back = W.Mesh()  # the sheet's underside, so it reads from below too
    back.grid(P[:, ::-1] - np.array([0.0, 0.0, 0.0008]), "roll_vellum", closed=False)
    m.extend(sheet)
    m.extend(back)
    return m


def stylus() -> W.Mesh:
    m = W.Mesh()
    L = 0.15
    z0, z1 = -L / 3, 2 * L / 3  # the nib end below the grip, the butt above
    m.extend(W.tube(line((0, 0, z0 + 0.012), (0, 0, z1), 12), lambda t, th: 0.0035 * (1.0 - 0.25 * t), 10,
                    mat="stylus_bone"))
    m.extend(W.tube(line((0, 0, z0 + 0.010), (0, 0, z0 + 0.018), 3), lambda t, th: 0.0042, 10, mat="roll_brass"))
    m.extend(W.tube(line((0, 0, z0), (0, 0, z0 + 0.012), 4), lambda t, th: 0.0028 * t + 0.0003, 8, mat="stylus_iron"))
    return m


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="act3_hand_props.py")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    out = Path(args.out_dir).resolve() if args.out_dir else OUT_DIR
    (out / "materials").mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name, build in (("watch_roll", watch_roll), ("stylus", stylus)):
        m = build()
        ob = W.make_object(name.title().replace("_", ""), m)
        path = out / f"{name}.glb"
        W.export(ob, path)
        log(f"{path.name}: {m.tris()} tris, {path.stat().st_size} bytes")
    for name in MATERIALS:
        W.write_material(out / "materials", name)
    log(f"wrote {len(MATERIALS)} materials")
    return 0


if __name__ == "__main__":
    sys.exit(main())
