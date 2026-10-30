"""The Ch6 camp arenas' smoke as Rendering's volumetric columns (env-art-b, M3-RND-21). env-art's arena tables
(`arena_scenes.py`, read-only) place the kit's `smoke_plume` shells, and `write_arena` writes .glb instances only. So
after a wrapper writes its arena, this swaps each plume instance for a SmokeColumn node (`game/vfx/smoke/
smoke_column.gd`, the "camp" profile) with the same transform. The column uses the shell's frame: +X downwind, the
same yaw and scale, foot at the origin. Each plume gets its own billow seed, in order."""

from __future__ import annotations

import re
from pathlib import Path

PLUME = "res://assets/environments/kits/brine_shoals/smoke_plume.glb"
SCRIPT = "res://game/vfx/smoke/smoke_column.gd"
PROFILE = "camp"
SEED_STEP = 0.37


def swap(path: Path) -> int:
    """Rewrites the arena scene at `path` in place; returns the number of plumes swapped."""
    text = path.read_text(encoding="utf-8")
    m = re.search(rf'^\[ext_resource type="PackedScene" path="{re.escape(PLUME)}" id="([^"]+)"\]$', text, flags=re.M)
    if m is None:
        return 0
    rid = m.group(1)
    text = text.replace(m.group(0), f'[ext_resource type="Script" path="{SCRIPT}" id="{rid}"]')
    count = 0

    def node(mm: re.Match) -> str:
        nonlocal count
        seed = round(SEED_STEP * count, 2)
        count += 1
        return (f'[node name="{mm.group(1)}" type="Node3D" parent="{mm.group(2)}"]\n{mm.group(3)}\n'
                f'script = ExtResource("{rid}")\nprofile = "{PROFILE}"\nseed = {seed}\n')

    text = re.sub(rf'^\[node name="([^"]+)" parent="([^"]+)" instance=ExtResource\("{re.escape(rid)}"\)\]\n'
                  r'(transform = [^\n]+)\n', node, text, flags=re.M)
    path.write_text(text, encoding="utf-8")
    return count
