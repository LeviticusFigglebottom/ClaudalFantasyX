---
id: M3-CRE-642
title: "Nhoa, the Rootlight (Ice, bound Ch11): the Vowbound model"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree-agent-a68ca47506828c52d, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: creatures
---
## Goal
Build nhoa per its design sheet, docs/kb/art/creatures/vowbound/nhoa.md (proposed, 2026-10-27), the way Ilun was built
(M3-CRE-638) and Kahre and Virel are being built (M3-CRE-640/641): the model and clips, the creatures.json
`"vowbound": true` row, a review shot, a portrait manifest row, and the tests, including the summon path.
**Her first PC render is pending.** This environment may not render, so she was checked numerically and on silhouette
sheets drawn from the build's own vertices (below). Her review shot and portrait have no image yet.

## Acceptance criteria
- [x] The design sheet is updated with an **As built** section: the counts, the rig, the softened bow, and a
      correction to its summon-framing claim.
- [x] `assets_src/creatures/nhoa/build_nhoa.py` on the creature kit. A tall, slight Kirru-like figure, 3.19 m to the
      antler tips: a heron's S-neck (four bones) carrying a small otter-like head at 2.45 m, two crowns of knuckled
      mangrove root (timber paling to bone, glowing faintly at the tips only), long arms with webbed four-fingered
      hands, and a robe that thins at the hem (0.75 m) into 18 hanging strands of motes.
- [x] **The motes are geometry, not particles:** 1,623 flattened beads skinned to her bones. They are seeded
      (`default_rng`), scattered 0 to 6 cm out from a dark `abyss_navy` inner body, densest on the core, and strung
      down the strands, with three short trails from each hand. Each bead is steady `glimmer_bound` at 1.2 with a
      0.4–1.0 mask. Nothing drifts and nothing is frozen (ADR 0015).
- [x] **Built hovering:** the strands' lowest ends are 0.15 m over the water at rest, with no stand-in `hover`. Across
      every frame of every clip the lowest vertex is 0.05 m (the KO), so no clip goes under the water and
      GroundedClipsTest needs no allow-list entry.
- [x] **14,820 triangles** (budget 16k): motes 9,738, body 2,980, antlers 1,272, shell 420, cord 250, eyes 160.
      10,861 vertices, 28 bones, GLB 1.77 MB. Five slots: `body`, `motes`, `antler`, `eye`, `shell`.
- [x] **The name-shell never glows:** the `shell` slot (the shell and its cord) has emission energy 0 and no mask, and
      no mote covers it. A Godot test checks the material.
- [x] Clips (13): `idle` 4.0 s loop, `ready` 1.4 s, `attack` 1.2 s (contact 0.55 s), `cast` 1.6 s (contact 0.8 s),
      `hit` 0.5 s (peak 0.10 s), `hit_b` (authored, rolled to the other side, peak 0.10 s), `defend` 1.2 s, `ko`
      1.8 s, `victory` 2.2 s, `rise` 2.6 s, `dismiss` 1.0 s, `special` 2.4 s (Farewell-Tide, contact 1.45 s: arms
      high and the strands drawn up 0.77 m into a column), and the kit's `idle_b`.
- [x] materials.json and write_materials.py. The Blender job `creature_nhoa` is appended, and PROVENANCE rows are in
      their own commit. **`verify_blender_builds.py --job creature_nhoa`: 6 identical.**
- [x] The import rule lists `res://assets/creatures/nhoa/`, and the `.glb.import` runs the creatures post-import
      script.
- [x] `game/creatures/nhoa/nhoa_battle.tscn` and the creatures.json row `nhoa`: `"vowbound": true`, contacts,
      `stand_in` yaw −90, height 3.2 and radius 0.5 (as Kahre's: no battle_sandbox.json row), and no `hover`. It also
      has **`vowbound_pending`**, a new key in validate_creatures.py with a tools test. Her vowbound.json row is
      Combat's, and the validator required it. The key names the task, allows the missing row, and becomes an error
      once the row exists. There is no `clip_by_skill` until her skills exist.
- [x] Godot tests `tests/unit/test_creature_nhoa_vowbound.gd` (5; `--filter=creature`, `vowbound` and `nhoa`):
      - the stand-in resolves to the model (scene, yaw, height, radius, no hover; she is no enemy);
      - the scene loads headless with all 13 clips and their contacts, with her head over 2.3 m and her strands over
        the water;
      - the shell and body materials are unlit;
      - FighterStandIn plays `ready` and `ko`;
      - the clips match the sheet: the strands sway, the strike sweeps forward, the cast pushes both hands out, the
        hit snaps her head back, defend crosses her arms, the rise and dismissal are bowed, the KO bows her, and
        Farewell-Tide lifts her wrists over her head and draws all three strand chains up.
- [x] `tests/integration/test_nhoa_summon_path.gd` (2, `--filter=nhoa`): the battle sandbox calls her and her
      stand-in shows the actor, both after the call and with the first-call cinematic forced. She has no vowbound.json
      row, so the test binds her into `choreo_vowbound_rise` with Ilun's live row copied under her id, using existing
      skills and nothing written to Combat's tables.
- [x] Shot `creature_nhoa` (idle, `flank_high`, with scale bars) and its stage scene are appended to shots.json.
      **Not captured, no baseline.**
- [x] The portrait manifest row `nhoa` is appended to tools/portraits/portraits.json. **Not baked: no PNG.**

## Framing check (no render)
Every vertex of every baked frame was projected with the camera director's math (`shot_pose`, choreo.json
`camera.safe_frame` left 0.04, right 0.15, top 0.10, bottom 0.26), on the Vowbound slot (x 3.0, z −1.1), turned by
yaw −90, at 16:9.
- **Default battle camera: inside in every frame of every clip.** At rest the margins are left 0.70, right 0.05, top
  0.05 and bottom 0.14. The tightest frames are hit_b's right edge (+0.008), cast's (+0.010), and Farewell-Tide's and
  attack's (+0.014). The top stays at +0.039 or more. Her narrow vertical build keeps the crowded right edge clear,
  which was Ilun's failure.
- **Summon shot** (4.2 m back, 2.6 m aside, 0.35 m up, looking 1.6 m above her mark, 46°). At rest the margins are left
  0.40, right 0.30, top 0.04 and bottom −0.11. On her mark the bottom safe line is at about 0.6 m, so the lower 0.45 m
  of the strands sit under the HUD's bottom band in every clip, as Kahre's feet do. Fitting all 3.05 m of her inside
  would need the shot's ±2.1 m hold to grow, or a shorter model than the sheet's 3.2 m. The top stays inside in `idle`
  (+0.037), `ready` (+0.023) and `rise` (+0.018), which are what the shot plays. Only hit_b's peak (−0.003) and
  Farewell-Tide's raised arms (−0.006) touch it, and neither plays on that shot. The sheet's earlier claim that the
  hold "fits her" is corrected there.

**Preview sheets** (numpy and PIL from the build's vertices, painter's algorithm, no Godot; scratch, not committed):
- `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-642/nhoa_views.png`:
  six rest views, including the review shot's `flank_high`.
- `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-642/nhoa_clips.png`:
  16 key poses.
- `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-642/nhoa_closeups.png`:
  the head and the name-shell.
- `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-642/nhoa_summon.png`:
  the summon shot with the HUD safe frame.
- `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-642/nhoa_default_camera.png`:
  the default camera.

The scripts are beside them: `framing.py` (per-frame margins, with output in `framing.txt`), `sheet.py`, `diag.py` and
`bones.py` (the bone positions the Godot test thresholds come from).

## Requests
- **Combat (game/data/battle/vowbound.json):** her row (the sheet's open question). The row needs her skills, the copy
  skill (an echo of the last enemy action) and the Swell finisher `farewell_tide`. Once it lands, in one commit,
  creatures: drop `vowbound_pending` from her creatures.json row (the validator will demand it), add `clip_by_skill`
  (`farewell_tide` → `special`, her ice skill → `cast`), and let the summon-path test use her own row. If the copy
  skill wants its own `echo` clip (sheet, optional), ask creatures for it; `attack` serves until then.
- **battle-presentation (choreo.json):** (a) `summon_cinematic.first_call_flags` needs an `nhoa` entry for her Ch11
  first call, with its flag declared in flags.tres. (b) Use `rise` for her entry and `dismiss` for her dismissal, as
  for Ilun, Kahre and Virel (M3-CRE-639). She has both, in place.
- **Rendering and battle-vfx:** Farewell-Tide's rising column is the one bound-light exception (vowbound.md §5) and
  needs color_script.md's sanction. It is the effect's job, not the model's. At the contact (1.45 s) her wrists are at
  2.53 m and the strand ends are drawn up to about 1.1 m, round her at a 0.25–0.5 m radius, so a column rising from
  there takes over from the model.
- **UI (optional):** a `stand_ins.nhoa` row in battle_sandbox.json is not needed, since her creatures.json `stand_in`
  carries height 3.2 and radius 0.5 (Kahre's route).
- **PC render:** `creature_nhoa` (new, no baseline), her portrait (it joins the missing-PNG bake), and a first render
  of a Nhoa call.

## Notes
- **For the first PC render:**
  - Whether 1,623 small beads read as one grainy, light-held figure at battle distance (about 110 px tall) or as
    noise. If they read as noise, enlarge `MOTE_R`. If she reads too solid, lower the count.
  - The dark inner body between the beads.
  - The antler tips' faint glow.
  - That the name-shell stays the one solid, unlit object at her throat.
  - The cold reading through colour alone (`salt_glass` over `abyss_navy`) with nothing frozen.
- **Parallel builds:** Hesk (M3-CRE-643) and Ethren (M3-CRE-644) append to the same shared files (creatures.json,
  blender_builds.json, PROVENANCE.md, shots.json, portraits.json, the import rule's list). Every edit here is an append
  or an alphabetical insert. If either Vowbound also lacks a vowbound.json row, it can use `vowbound_pending` rather
  than another validator change. A same-named change on their branches would conflict in validate_creatures.py, and
  the Lead keeps one.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
