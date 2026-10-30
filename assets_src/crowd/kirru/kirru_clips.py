"""The Kirru crowd bodies' shared clip library (assets/crowd/clips/crowd_kirru_clips.tres):

    python3 assets_src/crowd/kirru/kirru_clips.py [--check]

Pell's own field clips (assets/characters/pell/anim/pell_clips.tres, written by hero_clips.py --hero pell: the
wading-bird stand, the long neck's S, his stillness; pell.md section 10) are the Kirru's: `idle`, `talk` and `walk` are
taken out of his library as they are, their tracks re-rooted from his armature onto the crowd's (`crowd_skeleton`, the
node CrowdClipLibrary names on every crowd body), with the library's `hips_rest_y` the idle's first hips height, as
build_crowd writes it, so the crowd import fits the hips track to each Kirru body's own height (a youngster is
shorter). Pure text: a change to Pell's clips reaches the Kirru on the next run.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "assets" / "characters" / "pell" / "anim" / "pell_clips.tres"
OUT = ROOT / "assets" / "crowd" / "clips" / "crowd_kirru_clips.tres"
CLIPS = ("idle", "talk", "walk")
SRC_ARMATURE = "pell_skeleton/"
ARMATURE = "crowd_skeleton/"
HIPS_TRACK = "Skeleton3D:DEF-spine\")"


def build(text: str) -> str:
    blocks = re.split(r"\n(?=\[sub_resource type=\"Animation\")", text.split("\n[resource]")[0])
    anims = {}
    for b in blocks[1:]:
        name = re.search(r'resource_name = &"([^"]+)"', b).group(1)
        anims[name] = b.rstrip("\n")
    out = [f'[gd_resource type="AnimationLibrary" load_steps={len(CLIPS) + 1} format=3]', ""]
    for i, name in enumerate(CLIPS):
        b = re.sub(r'id="clip_\d+"', f'id="clip_{i}"', anims[name], count=1)
        out += [b.replace(SRC_ARMATURE, ARMATURE), ""]
    idle = anims["idle"]
    k = idle.index(HIPS_TRACK)
    keys = re.search(r"keys = PackedFloat32Array\(([^)]*)\)", idle[k:]).group(1).split(",")
    hips_y = float(keys[3])  # (time, transition, x, y, z, ...): the first key's y
    out += ["[resource]", "_data = {"]
    out += [f'&"{n}": SubResource("clip_{i}"){"," if i < len(CLIPS) - 1 else ""}' for i, n in enumerate(CLIPS)]
    out += ["}", f"metadata/hips_rest_y = {hips_y:g}", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = build(SOURCE.read_text(encoding="utf-8"))
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("kirru_clips: up to date" if same else f"kirru_clips: {OUT.relative_to(ROOT)} is stale")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"kirru_clips: wrote {OUT.relative_to(ROOT)} ({', '.join(CLIPS)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
