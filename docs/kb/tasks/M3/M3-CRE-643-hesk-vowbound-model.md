---
id: M3-CRE-643
title: "Hesk, the Cord-Keeper (Holy, bound Ch12): the Vowbound model (design sheet done; build next)"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree-agent-adff7ba4a64aa18db, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: creatures
---
## Goal
Build hesk per its design sheet, docs/kb/art/creatures/vowbound/hesk.md (proposed, 2026-10-27), the way Ilun was built
(M3-CRE-638) and Kahre and Virel are being built (M3-CRE-640/641): the model and clips, the creatures.json
`"vowbound": true` row, a review shot, a portrait manifest row, and the tests, including the summon path.

## Notes
- hesk has no game/data/battle/vowbound.json row yet. The model doesn't need stats, but its clip map (which skill plays
  which clip) waits on Combat's skill ids; until then use the stand-in set.
- The sheet's open questions are for Combat and the Lead, not the human.

## Acceptance criteria
- [x] Design sheet docs/kb/art/creatures/vowbound/hesk.md updated to "built": the keth convention and her ledger
      numbers, "As built" (size, triangles, rig, clips), the changes from the proposal and why, the framing check,
      the light.
- [x] `assets_src/creatures/hesk/build_hesk.py` on the creature kit: a great condor perched on the water, wings
      half-folded and mantled (2.45 m across at rest), eight **knotted cord primaries** per wing built as geometry
      (twisted gauze_white rope with a sand_cloth strand; beads, long knots and figure-eights as keth, the leading
      cords reading 47 and 7), a ruff of soft cords, a bare bone head, the planted right talon solved onto the water
      every frame, the keth bundle in the drawn-up left talon hanging to 0.1 m over the water.
- [x] **13,602 triangles** (budget 14k): knots 4,056, cords 3,680, ruff 1,104, feet 936, wing plumage 800, body 792,
      bundle 710, legs 512, head 452, neck 336, eyes 160, tail 64. 7,782 vertices, 25 bones, GLB 1.58 MB.
- [x] Clips (13): `idle` 4.0 s loop, `ready` 1.4, `attack` 1.2 (contact 0.55), `cast` 1.6 (contact 0.8), `hit` 0.5
      (peak 0.10), `hit_b` 0.5 (authored), `defend` 1.2, `ko` 1.8, `victory` 2.2, `rise` 2.6, `dismiss` 1.0,
      `special` 2.4 (Pass-Cord, contact 1.45), `idle_b` 1.2.
- [x] materials.json (six slots) → write_materials.py. `cord`, `ruff`, `eye` glimmer_bound #4FB3B0 at 1.2, steady;
      the mask is 1.0 at the knots, 0.2 along the cords and ruff, 0.55 on the eyes. `plumage`, `head`, `bundle` unlit:
      **the keth bundle never glows**. The Blender job `creature_hesk` (appended); **verify: 7 identical**.
      PROVENANCE rows (their own commit). Import rule lists `res://assets/creatures/hesk/`; the `.glb.import` runs the
      creatures post-import script.
- [x] `game/creatures/hesk/hesk_battle.tscn`; creatures.json row `hesk`: `"vowbound": true`, `"vowbound_pending":
      "M3-CRE-643"`, contacts, `stand_in` yaw −90 with `height` 2.4 and `radius` 0.6 (no battle_sandbox.json row, as
      Kahre). No `clip_by_skill` (no skill ids yet): the stand-in set plays.
- [x] **No vowbound.json row:** tools/validate_creatures.py rejected a `vowbound` row without one. It now takes the
      coordinator's shared key `vowbound_pending` (Nhoa's semantics: allows the missing row, an error once the row
      exists), with a test in tools/tests/test_creatures.py. Keep Nhoa's version on merge if they differ.
- [x] Godot tests: tests/unit/test_creature_hesk_vowbound.gd (6: the stand-in resolves with her height and radius;
      the scene loads with all 13 clips and the contacts; FighterStandIn plays `ready` and `ko` on her; the planted
      talon stays on the water in every clip; the clips follow the sheet; only the cords and eyes carry the light) and
      tests/integration/test_hesk_summon_path.gd (2: the sandbox calls her from choreo_vowbound_rise with a minimal
      in-test row, Ilun's live row under her id, with and without the first-call cinematic forced).
- [x] Shot `creature_hesk` (idle, three_quarter, scale bars) appended to tests/screenshots/shots.json with a stage
      scene; portrait manifest row `hesk` appended (default yaw 30, pitch 14). **Neither captured nor baked.**

## Numeric check (no render)
| Clip | Lowest y | Widest span (x) |
|---|---|---|
| idle | 0.005 | 2.57 |
| ready | 0.005 | 3.53 |
| attack | 0.005 | 3.63 |
| cast | 0.005 | 4.03 |
| hit / hit_b | 0.005 | 2.45 |
| defend | 0.005 | 2.45 |
| ko | 0.000 | 4.35 (falling; lies at 3.83) |
| victory | 0.005 | 4.24 |
| rise | 0.000 | 3.39 |
| dismiss | 0.000 | 2.45 |
| special | 0.000 | 4.39 (downstroke; holds 4.13–4.19 spread) |
| idle_b | 0.005 | 2.86 |

GroundedClipsTest (from the GLB) passes with no allow-list entry.

**Framing** (every frame of every clip, the camera director's math, Vowbound slot x 3.0 z −1.1, yaw −90, 16:9,
choreo.json safe frame; `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/framing.py`):
- Default battle camera: every clip inside on every side. At rest left 0.65, right 0.015, top 0.17, bottom 0.13; the
  tightest are the KO's fall (right +0.001) and victory (right +0.003). The first build crossed the right edge in
  ready, attack, cast, KO, victory and special (worst −0.049); the open wings now cup forward (see the sheet).
- Summon shot: left, right and top inside in every clip; her feet sit under the bottom band (−0.15), as Kahre's do.

**Preview sheets** (numpy and PIL from the build's vertices, no Godot), scratch, not committed:
`/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/hesk_views.png` (six rest views), `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/hesk_clips.png` (16 key poses), `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/hesk_cords.png` (the knots close up),
`/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/hesk_default_camera.png` and `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-643/hesk_summon.png` (the two framings with the safe frame). Scripts beside them:
`sheet.py`, `framing.py`, `edge.py`, `diag.py`, `span.py`, `ko.py`, `try_poses.py`.

## Requests
- **Combat (game/data/battle/vowbound.json):** her row (stats, skills, the Holy affinities, `swell.technique`
  Pass-Cord), the skills, and a `VOWBOUND_HESK` loc key. Then creatures.json gets `clip_by_skill` (cleanse → `cast`,
  Pass-Cord → `special`) and drops `vowbound_pending` (the validator will insist).
- **battle-presentation (choreo.json):** `first_call_flags.hesk` if her Ch12 call plays the cinematic, and the
  standing `rise` / `dismiss` entry-clip ask (M3-CRE-639); she has both.
- **battle-vfx:** Pass-Cord's line of shining knots runs from her contact (1.45 s; her head comes 0.8 m forward and
  the wings sweep down to 0.36 m over the water).
- **Lead / art:** the open question stands: holy light as `glimmer_bound` (built) or a palette ADR.
- **PC render:** `creature_hesk` (new, no baseline) and her portrait (joins the PNG bake).

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
