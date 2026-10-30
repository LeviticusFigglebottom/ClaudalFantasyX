# Handoff — art (creatures) — 2026-10-28 #8

Worktree agent for M3-CRE-662, the crowd follow-up to M3-CRE-659 (ADR 0152): cloth never near skin, and a smaller
crowd. Branched from `claude/creatures`; not pushed. The task is at status review (reviewer: art), with the details in
its Notes.

## Done
- **Cloth versus skin.** `skin_delta_e` (`tools/validate_npc.py`) is shared by the generator and the validator.
  - The metric is CIE76 on CIELAB split into lightness, chroma and hue, with k_l 0.3 and k_h 0.5.
  - The floor is 18.5, calibrated in `ranges.json` `skin_clearance` against the palette, the crowd's skin range and
    the tops the renders showed reading as skin: lowest pass 20.6 (order_marble on the lightest skin; greys 25.4 or
    more), highest fail 16.7.
  - The fail tops are the review's two pale tops (found in a re-render of M3-CRE-659's crowd_lineup_a), plus the
    lighter cream that a first pass at k 0.75 / floor 24 gave man_heavy_b, which still read as skin.
  - Consequence: creams and beiges fail near any crowd skin.
  - `draw_cloth` widens instead of keeping a miss: own mixes, then other sets, then a darker or lighter mix, then an
    error naming the person or body.
  - It applies to the bodies' default `_tints` and to every person's tints. Against M3-CRE-659's data, 12 defaults
    and 23 person tints were under the floor; none are now.
  - Changed: 35 of 66 default cloth tints (17 bodies' materials) and 88 of 168 person cloth tints (42 people); 31
    hair tints moved as a side effect of the seeded stream.
- **Shared clips.**
  - Four AnimationLibraries in `assets/crowd/clips/` (adult, elder, child, child_small) replace 22 per-body
    libraries.
  - The import (`CrowdClipLibrary`, `game/world/npc/crowd_clip_library.gd`, run by `crowd_post_import.gd`) renames
    every body's armature to `crowd_skeleton` and sets `Skeleton3D.motion_scale` so the hips track fits the body.
  - The groups come from sampling bone positions: within 1.0 cm (feet 0.4 cm) of each body's own clips.
  - Clips went from 12.00 to 2.84 MB, and assets/crowd from 42.85 to 33.69 MB (tracked files).
- **Rebuild:** all 22 bodies. GLBs, maps and actors are byte-identical; the cloth materials and clips changed.
  `verify_blender_builds` prints identical for all 22 `crowd_*` jobs.
- **Tests:**
  - tools: `SkinClearance` (5) and `SharedClips` (3) in `tools/tests/test_npc.py`.
  - Godot: `test_every_crowd_body_shares_its_groups_clips_at_its_own_height`.
- **Docs and data:** `docs/kb/art/creatures/crowd.md` (§3, new §5), PROVENANCE (22 clip rows out, 4 in), and the
  crowd job outputs in `tools/dev/blender_builds.json`.

## Gates
- `unittest tools.tests.test_npc tools.tests.test_blender_builds`: 55 OK.
- `validate_data`: 0 errors. The one warning is the existing haluna `shrine_offering`.
- `taskboard --check`: OK. `gen_crowd.py --check`: clean. `gdlint` and `gdformat`: clean.
- Godot `--filter=crowd` 6/0, `villager` 33/0, `field_npc` 10/0.
- The crowd shots were rendered and viewed (see the task's review notes). No baselines were written.

## Known issues
- A body's own `_persona` now only feeds its group's mean persona, about 1 cm at the hands.
- Changing the post-import does not re-import unchanged GLBs. A worktree with an old `.godot` cache must delete the
  `crowd_*.glb-*` files in `.godot/imported` (or reimport them) to pick up the shared libraries.
- From #7, still open: the life_audio freed-cast at capture teardown (audio), M3-CRE-657 (slice-polish), and no
  baselines for the crowd shots.

## Exact next step
1. Merge into `claude/creatures`. After the merge, reimport the crowd GLBs (see Known issues).
2. Render the 14 `crowd_*` shots and write their baselines.
3. Art review of M3-CRE-662.

## Files touched
assets_src/crowd/{gen_crowd.py,build_crowd.py,ranges.json,params/*.json}, assets/crowd/** (clips/ new, per-body
anim/ removed, cloth materials), game/data/world/npc/crowd.json, game/data/import/crowd.json,
game/core/import/crowd_post_import.gd, game/world/npc/crowd_clip_library.gd(.uid), tests/unit/test_crowd_villagers.gd,
tools/validate_npc.py, tools/tests/test_npc.py, tools/dev/blender_builds.json, assets/PROVENANCE.md,
docs/kb/art/creatures/crowd.md, docs/kb/tasks/M3/M3-CRE-662-crowd-cloth-and-size.md.
