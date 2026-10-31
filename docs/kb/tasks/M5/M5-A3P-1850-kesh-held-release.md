---
id: M5-A3P-1850
title: "Kesh's held form and her release (Ch21 H03), as the Ch20 six"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
reviewer: qa
depends_on: []
milestone: M5
---
## Goal
act3_ending H03 (act3_threads T-01, accepted): Asha calls Kesh out one last time and she is released as the Ch20 six
were. "She lifts and doesn't look at him", her light rising out of the top of the frame. The six held forms exist
(M3-CRE-647); Kesh had none.

## Done (2026-10-30)
- `assets_src/creatures/kesh/materials.json` `held` block -> `assets/creatures/kesh/materials_held/` (glimmer_bound
  -> glimmer_held at the same energy, steady); `game/creatures/kesh/kesh_held_battle.tscn` (same GLB, `material_dir`
  the held set); creatures.json `kesh_held` (her clip map and contacts, `ko` = `release`, `phases.release` held,
  stand_in yaw 90, 4.2 m).
- `release` (3.5 s, build_kesh.py `build_release`): the arms open low and wide, palms out; the robe's mouths open;
  the face lifts and turns from her resting gaze the other way (keyed over the idle's head turn); the column carries
  her up 2.2 m, out of the battle frame.
- The `kesh_held` portrait (tools/portraits/portraits.json; rendered, viewed) and PROVENANCE rows.
- tests/unit/test_creature_kesh_held.gd: the row (release KO, held phase, not a Vowbound), the held light on every lit
  surface, the release's rise (at least 1.5 m) and turn (at least 15°).
- Checks: Blender creature_kesh 7 identical; Godot kesh_held 3/0, vowbound 118/0, creature_portraits 4/0,
  creature_actor 31/0; tools test_creatures and test_blender_builds OK; validate_data 0/0. Clip sheet viewed.
- **Open, for others:** Combat's enemies.json row (`model` = the held scene) and Ch21's encounter; the release's
  glimmer_lift swap and rising motes are battle VFX's (as for the six).

## Review log
