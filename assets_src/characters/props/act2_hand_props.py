"""Act II hand props (M4-A2P-052/050; act2_ch14.md, act2_ch15.md). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/props/act2_hand_props.py [-- --out-dir DIR]
    # -> assets/characters/props/act2/{dock_hook,salt_glass_housing,wedding_cord}.glb and materials/*.tres

Wick.py's mesh helpers (its `Mesh`, `tube`, `ring`, `make_object`, `export`, `write_material`) with this file's
material table. Each prop's origin is its grip, so a `BoneAttachment3D` on the holding hand's bone places it:

* `dock_hook.glb`: Aldous Varrow's dock-hook (act2_ch15.md H05 "a dock-hook in his belt", H13 he pushes the raft off
  with it): a 0.62 m ash haft, a tarred cord grip, an iron collar and a J hook with a blunt point. Origin at the grip,
  the haft along +Y.
* `salt_glass_housing.glb`: the salt-glass lamp-housing he raises for Tobin's motes (H14): a glass cylinder between
  two brass rims, a brass cap and a bail. The glass is `housing_glass` (salt_glass); its emission (the bound glow,
  glimmer_bound) is off by default, a scene parameter. Origin at the bottom of the bail's loop (held from above).
* `wedding_cord.glb`: the knotted cord Tobin and Merel pass hand to hand (act2_ch14.md W05) with the ring Liss carried
  threaded on it: a 0.5 m cord in lacquer red with three overhand knots and a gold ring. Origin at its middle.

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
OUT_DIR = ROOT / "assets" / "characters" / "props" / "act2"
MATERIALS = {  # name: (hex, roughness, metallic)
    "hook_wood": ("#8C6E4E", 0.7, 0.0),  # oiled ash, darker with handling
    "hook_cord": ("#2A2622", 0.85, 0.0),  # tarred cord
    "hook_iron": ("#3A3836", 0.45, 1.0),
    "housing_glass": ("#BFE6E0", 0.12, 0.0),  # salt_glass
    "housing_brass": ("#B08D57", 0.38, 1.0),  # brass
    "wedding_cord": ("#B3261E", 0.8, 0.0),  # lacquer_red (both families' colour: the Warden's red)
    "wedding_ring": ("#D4A437", 0.25, 1.0),  # gold_leaf
}
W.MATERIALS = MATERIALS
HAFT_LEN = 0.62
HAFT_R = 0.014
SEG = 14


def log(msg: str) -> None:
    print(f"[act2_props] {msg}", flush=True)


def line(a, b, n: int) -> np.ndarray:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return np.array([a + (b - a) * t for t in np.linspace(0.0, 1.0, n)])


def dock_hook() -> W.Mesh:
    m = W.Mesh()
    up = np.array([0.0, 0.0, 1.0])
    m.extend(W.tube(line((0, 0, -0.18), (0, 0, HAFT_LEN - 0.18), 18), lambda t, th: HAFT_R * (1.0 - 0.08 * t), SEG,
                    mat="hook_wood"))
    m.extend(W.tube(line((0, 0, -0.08), (0, 0, 0.08), 8), lambda t, th: HAFT_R * 1.12, SEG, mat="hook_cord"))
    top = HAFT_LEN - 0.18
    m.extend(W.tube(line(up * (top - 0.05), up * (top + 0.01), 4), lambda t, th: HAFT_R * 1.2, SEG, mat="hook_iron"))
    # the J: up from the collar, over, and back down to a blunt point
    pts = []
    for t in np.linspace(0.0, 1.0, 18):
        if t < 0.35:
            pts.append((0.0, 0.0, top + 0.2 * t / 0.35))
        else:
            a = math.pi * (t - 0.35) / 0.65 * 1.15
            pts.append((0.045 - 0.045 * math.cos(a), 0.0, top + 0.2 + 0.045 * math.sin(a)))
    m.extend(W.tube(np.array(pts), lambda t, th: 0.0075 * (1.0 - 0.55 * t), 10, mat="hook_iron"))
    return m


def salt_glass_housing() -> W.Mesh:
    m = W.Mesh()
    r, h = 0.045, 0.11
    z0 = -0.03 - h  # the bail's loop at the origin, the housing below it
    m.extend(W.tube(line((0, 0, z0), (0, 0, z0 + h), 6), lambda t, th: r, 24, mat="housing_glass"))
    for z in (z0, z0 + h):
        m.extend(W.ring(np.array([0.0, 0.0, z]), np.array([0.0, 0.0, 1.0]), r + 0.002, 0.004, "housing_brass", seg=28))
    cap = [(0.0, 0.0, z0 + h + 0.025 * s) for s in np.linspace(0.0, 1.0, 5)]
    m.extend(W.tube(np.array(cap), lambda t, th: (r + 0.003) * (1.0 - 0.75 * t), 24, mat="housing_brass"))
    base = [(0.0, 0.0, z0 - 0.012 * s) for s in np.linspace(0.0, 1.0, 3)]
    m.extend(W.tube(np.array(base), lambda t, th: (r + 0.003) * (1.0 - 0.2 * t), 24, mat="housing_brass"))
    bail = [(0.032 * math.cos(a), 0.0, -0.03 + 0.032 * math.sin(a) + 0.0) for a in np.linspace(0.0, math.pi, 16)]
    m.extend(W.tube(np.array(bail), lambda t, th: 0.0022, 8, mat="housing_brass"))
    return m


def wedding_cord() -> W.Mesh:
    m = W.Mesh()
    L = 0.5
    path = np.array([(x, 0.0, -0.06 * (1.0 - (2.0 * x / L) ** 2)) for x in np.linspace(-L / 2, L / 2, 60)])
    knots = (-0.15, 0.0, 0.15)

    def radius(t, th):
        x = -L / 2 + L * t
        bump = max(math.exp(-((x - k) / 0.008) ** 2) for k in knots)
        return 0.003 * (1.0 + 1.6 * bump)

    m.extend(W.tube(path, radius, 10, mat="wedding_cord"))
    ring_at = np.array([0.075, 0.0, -0.06 * (1.0 - (2.0 * 0.075 / L) ** 2)])
    m.extend(W.ring(ring_at, np.array([1.0, 0.0, 0.0]), 0.011, 0.0022, "wedding_ring", seg=24))
    return m


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="act2_hand_props.py")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    out = Path(args.out_dir).resolve() if args.out_dir else OUT_DIR
    (out / "materials").mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name, build in (("dock_hook", dock_hook), ("salt_glass_housing", salt_glass_housing),
                        ("wedding_cord", wedding_cord)):
        m = build()
        ob = W.make_object(name.title().replace("_", ""), m)
        path = out / f"{name}.glb"
        W.export(ob, path)
        log(f"{path.name}: {m.tris()} tris, {path.stat().st_size} bytes")
    for name in MATERIALS:
        W.write_material(out / "materials", name)
    # the housing's bound glow (H14): emission off by default, glimmer_bound, a scene parameter
    p = out / "materials" / "housing_glass.tres"
    p.write_text(p.read_text(encoding="utf-8") + "emission_enabled = true\nemission = Color(0.310, 0.702, 0.690, 1)\n"
                 "emission_energy_multiplier = 0.0\n", encoding="utf-8")
    log(f"wrote {len(MATERIALS)} materials")
    return 0


if __name__ == "__main__":
    sys.exit(main())
