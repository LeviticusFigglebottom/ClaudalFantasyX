#!/usr/bin/env python3
"""Body clips for the Haluna villagers (M2-CHR-03), as Godot AnimationLibrary text resources.

    python3 assets_src/characters/villagers/villager_clips.py [npc ...]   # default: every params file
    # -> assets/characters/villagers/<npc>/anim/<npc>_clips.tres

The heroes' clip generator (assets_src/characters/asha/hero_clips.py, M2-FP-07) used as a library: the skeleton
rest read from the villager's committed GLB, the same keyed body bones, the same pose functions (`idle`, `talk`,
`walk`), with a persona per villager from `_persona` in params/<npc>.json (sway, a forward lean, how far the arms
hang). Without these an instanced villager would stand in the bind A-pose. The `characters` import rule
(game/data/import/characters.json `animations`) puts the library on an AnimationPlayer at the asset root, so the
field can play `idle` (and `talk` during a bark). Pure Python, deterministic; tools/tests/test_villagers.py rebuilds
every library and compares it byte for byte, so rerun this after any rebuild that moves a skeleton.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "asha"))

import hero_clips as hc  # noqa: E402

PARAMS_DIR = HERE / "params"
CLIPS = ["idle", "talk", "walk"]
DEFAULT_PERSONA = {"sway": 1.0, "lean": 0.0, "staff": False, "arms_down": 41.0}


def persona(npc: str) -> dict:
    extra = json.loads((PARAMS_DIR / f"{npc}.json").read_text(encoding="utf-8"))
    return {**DEFAULT_PERSONA, **extra.get("_persona", {}), "staff": False}


def glb_path(npc: str) -> Path:
    return ROOT / "assets" / "characters" / "villagers" / npc / f"{npc}.glb"


def out_path(npc: str) -> Path:
    return ROOT / "assets" / "characters" / "villagers" / npc / "anim" / f"{npc}_clips.tres"


def build(npc: str) -> str:
    """hero_clips.build's resource layout for a villager's skeleton and persona."""
    pers = persona(npc)
    sk = hc.Skeleton(glb_path(npc))
    base = f"{sk.root_name}/Skeleton3D:"
    subs = []
    for ci, clip in enumerate(CLIPS):
        length = hc.LENGTHS[clip]
        loop = clip in hc.LOOPS
        n = int(round(length * hc.FPS))
        times = [i / hc.FPS for i in range(n + 1)]
        keys_q = {b: [] for b in hc.BONES}
        keys_p = []
        for t in times:
            tt = (t % length) if loop else t
            pose = hc.pose_at(clip, tt, length, sk, pers)
            turns = {b: hc.qeuler(v) for b, v in pose.items() if b != "hips"}
            local = sk.local_pose(turns)
            for b in hc.BONES:
                keys_q[b].append((t, local[b]))
            keys_p.append((t, sk.rest_t[hc.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)))
        lines = [f'[sub_resource type="Animation" id="clip_{ci}"]', f'resource_name = &"{clip}"',
                 f"length = {hc.fmt(length)}", f"loop_mode = {1 if loop else 0}", f"step = {hc.fmt(1.0 / hc.FPS)}"]
        tracks = [("position_3d", hc.HIPS, [(t, list(p)) for t, p in keys_p])]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in keys_q[b]]) for b in hc.BONES]
        for ti, (kind, bone, keys) in enumerate(tracks):
            vals = []
            for t, v in keys:
                vals += [hc.fmt(t), "1"] + [hc.fmt(x) for x in v]
            lines += [f'tracks/{ti}/type = "{kind}"', f"tracks/{ti}/imported = false", f"tracks/{ti}/enabled = true",
                      f'tracks/{ti}/path = NodePath("{base}{bone}")', f"tracks/{ti}/interp = 1",
                      f"tracks/{ti}/loop_wrap = true", f"tracks/{ti}/keys = PackedFloat32Array({', '.join(vals)})"]
        subs.append("\n".join(lines))
    data = ",\n".join(f'&"{c}": SubResource("clip_{i}")' for i, c in enumerate(CLIPS))
    head = f'[gd_resource type="AnimationLibrary" load_steps={len(CLIPS) + 1} format=3]\n\n'
    return head + "\n\n".join(subs) + f"\n\n[resource]\n_data = {{\n{data}\n}}\n"


def main(argv: list[str]) -> int:
    npcs = argv or sorted(p.stem for p in PARAMS_DIR.glob("*.json"))
    for npc in npcs:
        p = out_path(npc)
        p.parent.mkdir(parents=True, exist_ok=True)
        text = build(npc)
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)} ({len(text) / 1e6:.2f} MB, {len(CLIPS)} clips)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
