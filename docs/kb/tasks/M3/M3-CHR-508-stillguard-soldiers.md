---
id: M3-CHR-508
title: "Stillguard soldiers (six variants) for the Ch6 raid"
role: character
status: review
owner_session: "characters (worktree sg-wt, branch chr-stillguard-wip)"
depends_on: [M2-CHR-01, M1-CHR-14, M3-CHR-507]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
Ch6's Stillguard are capsules in `brine_shoals_layout.json` `actors` (M3-C06-06 #4: six variants if the set is short).
The Order's soldiers: red-lacquered shell armour, round shields, spears (`shield_up`, `level_spear` proposals). Built
as one kit on the base body (Moll's armour language, M3-CHR-507) with six variants by build, face, helm and
weathering.

## Acceptance criteria
- [x] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [x] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours):
      routed through M3-CHR-519 (the level scenes are not ours).
- [x] The Ch6 proposals they perform: `stand_watch_seaward`, `shield_up`, `level_spear` (the spear gripped).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).
- 2026-10-28 (characters): built. One parametric build on Moll's (`assets_src/characters/stillguard/`:
  `build_stillguard.py --variant <v>` on `build_moll.build`, `stillguard_variants.json` with `sg_table.py`, `sg_helm.py`
  for the open-face helm, `sg_textures.py`, `write_materials.py`, `build.sh`). Moll's own outputs are byte-identical
  (verify --job moll). Variants `stillguard_a`..`f` (a, b and c are the level capsules' ids in Ch6 and Ch8; d, e and f
  are crowd extras): heights 1.71-1.84 m, six builds and skin tones, cropped or shaved, the helm on a, c and e,
  weathered atlases (shared, `assets/characters/stillguard/textures/`) on b, c and f. No Inquisitor's sash; Moll's
  round shield on the left forearm; Toma's spear in the right fist on the M2-CHR-515 grip (DEF-spear).
- Budgets: LOD0 39.6k-41.4k tris, LOD1 17.6k-18.5k, GLB 2.33-2.55 MB.
- Clips (hero_clips.py, the Stillguard block; field only, none fights): idle, walk, `stand_watch_seaward`,
  `shield_up`, `level_spear` (one-handed, the shield arm in a low guard).
- Rig probe: the prop guards (spear grip turn and offset, through_garment) and prop_in_body for the Spear and the Shield
  pass with no allowance; the per-variant Costume, Sleeves, Body and max_exposed allowances and their reasons are in
  `tools/dev/rig_checks.json` (`_allowances`).
- Stages, shots (no baselines): `game/levels/_tests/characters/stillguard/` (a, b, c, d stages, two clip scenes and the
  lineup of all six); `stillguard_*` shots in tests/screenshots/shots.json.
- Not covered by this task: the other dialogue cues on these actors (ch06 `walk_torch`, `hold_arm`, `kneel_palms_flat`,
  `let_go`; ch08 `shake_head`) need a clip request.

## Review log
