# Shell Shrine salvage (not built)

env-art's parallel Shell Shrine kit (M2-ENV-03) was superseded by m2-slice's kit
(`assets_src/environments/kits/haluna/shrine_interior.py`, the Art Director's verdict in M2-ENV-03's
Review log). These four pure-numpy geometry modules are kept as **source only** for M2-ENV-09, which
salvages pieces from them into the adopted kit. No Blender job builds them, nothing under `assets/`
comes from them, and nothing imports them. Delete this folder when M2-ENV-09 is done.

| Module | Worth salvaging |
|---|---|
| `ss_water.py` | `channel_bend` (0.6 m radius, turns +X, leaves at (0.6, 0, -0.6)) and `channel_t` (1.4 m, branch to +X at z = -0.7): 0.4 m wide, 0.25 m deep inside, rim at 0.3 m, nacre bands, VC weathering, LOD0 + LOD1 (~550 / ~460 tris). Also the sluice and spillway sump. |
| `ss_props.py` | `leaf_boat` (0.28 m folded leaf with a frangipani flower, 389 / 48 tris; uses `kit_garland` + `kit_garland_throat`), `offering_shelf` (fan-shell back, nacre strip, front +X), `sea_stones` (9 stepping stones + 16 boulders along +X, for a waterline 1.8 m under the floor). |
| `ss_architecture.py` | The whorl column, the conch niche, and `ceiling_layout` / `build_ceiling`: a smooth vault fitted under Haluna's tiered `roof_fan_shell`, with the oculus offset to where a 75° south sun actually lands. |
| `ss_common.py` | The kit metrics table and helpers (revolved profiles, coursed stone walls, collision proxies) the others import. |

They import the Haluna kit's `kit_common` and `shrine` (read-only). The whole WIP (materials, dressing,
preview scene, a 9-test GDScript suite) was commit d0749489 in env-art's container; it was never pushed.

Lessons from it, for the adopted kit: the water shader culls back faces, and Godot front faces are
clockwise seen from above, so a strip wound the other way doesn't render; a ReflectionProbe on its default
ambient blacks out exterior faces inside its box, and on auto ambient it washes the room warm (set an
explicit ambient colour).
