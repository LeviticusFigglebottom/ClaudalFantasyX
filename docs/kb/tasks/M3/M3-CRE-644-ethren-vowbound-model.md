---
id: M3-CRE-644
title: "Ethren, the Level Saint (Glimmer, bound Ch13): the Vowbound model (design sheet done; build next)"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: creatures
---
## Goal
Build ethren per its design sheet, docs/kb/art/creatures/vowbound/ethren.md (proposed, 2026-10-27), the way Ilun was built
(M3-CRE-638) and Kahre and Virel are being built (M3-CRE-640/641): the model and clips, the creatures.json
`"vowbound": true` row, a review shot, a portrait manifest row, and the tests, including the summon path.

## Notes
- ethren has no game/data/battle/vowbound.json row yet. The model doesn't need stats, but its clip map (which skill plays
  which clip) waits on Combat's skill ids; until then use the stand-in set.
- The sheet's open questions are for Combat and the Lead, not the human.

## Acceptance criteria
- [x] Design sheet docs/kb/art/creatures/vowbound/ethren.md updated with an "As built" section: every change from the
      proposal (telescoping bells, the two-leaf screen wings, the veil and halo bones, the ring, the rest pose, the
      rig), the gold measured, the framing check, the clips.
- [x] `assets_src/creatures/ethren/build_ethren.py` on the creature kit, built hovering (sole line 0.2 m, hem 0.1 m,
      halo top 3.0 m). **14,406 triangles** (budget 16k): gold 3,304 + veil border 140, seams 1,350, pauldrons 924,
      cuirass 972, breastplate 764, robe 2,112, wings 940, hands 908, arms 672, veil 672, halo 640, head 512, collar
      280, ring 216. 27 bones, 13 clips, GLB 1.53 MB. Seven slots: `lacquer`, `lacquer_red`, `gold`, `seam`, `halo`,
      `veil`, `ring`. The veil is its own mesh (`ethren_veil`) on its own unkeyed bone (`veil`).
- [x] Clips: `idle` 4.0 s loop (1 cm rise and fall, nothing else), `ready` 1.4, `attack` 1.2 (contact 0.55), `cast`
      1.6 (contact 0.8), `hit` 0.5 (peak 0.10, numpy and GLB), `hit_b` (authored), `defend` 1.2, `ko` 1.8, `victory`
      2.2, `rise` 2.6, `dismiss` 1.0, `special` 2.4 (Still Water, contact 1.45), `idle_b` 1.6 (authored: the kit's would
      open the wings). Wings open only in ready, cast, special, victory (tested).
- [x] materials.json and the written .tres: `seam` and `halo` `glimmer_bound` #4FB3B0 at 1.2, no pulse; `veil` 0.2;
      `lacquer`, `lacquer_red`, `gold` (metallic 1.0) and `ring` (rough, never lit) at 0.
- [x] Blender job `creature_ethren` appended; **`verify_blender_builds.py --job creature_ethren`: 8 identical**.
      PROVENANCE rows (own commit). Import rule lists `res://assets/creatures/ethren/`; the `.glb.import` runs the
      creatures post-import script.
- [x] `game/creatures/ethren/ethren_battle.tscn` and the creatures.json row `ethren`: `"vowbound": true`,
      `"vowbound_pending": "M3-CRE-644"`, contacts, `stand_in` yaw −90, height 2.5, radius 0.6, no hover.
      tools/validate_creatures.py accepts a Vowbound row without a vowbound.json row only while `vowbound_pending`
      is set, and errors on the key once the row exists (the Lead's semantics, as on Nhoa's branch; a test in
      tools/tests/test_creatures.py).
- [x] Tests: tests/unit/test_creature_ethren_vowbound.gd (6) and tests/integration/test_ethren_summon_path.gd (2, a
      minimal in-test row: Ilun's under his id, with the skills the fixture holds).
- [x] Shot `creature_ethren` (idle, `three_quarter`, scale bars) and the portrait row `ethren` (defaults: yaw 30°, so
      the veil and the folded wings both read). **Neither rendered.**

## Numeric check (no render)
- Lowest vertex per clip (skinned from the GLB): idle 0.093, ready 0.098, attack 0.066, cast 0.098, hit 0.024, hit_b
  0.008, defend 0.098, ko 0.060, victory 0.098, rise 0.060, dismiss 0.060, special 0.098, idle_b 0.098. No allow-list
  entry; the KO's root does not move (the hips sink 0.45 m inside the telescoping bells).
- **Framing** (every frame of every clip, the camera director's `shot_pose` math, the Vowbound slot, yaw −90):
  default camera, every frame inside the safe frame (rest right 0.027, top 0.074; tightest right 0.005 in rise's start
  and dismiss's end, 0.011 KO). Summon shot: left, right and top inside in every clip; the lower bells are under the
  HUD's bottom band (−0.13 to −0.15), as Kahre's feet are.
- **Gold share** (per-pixel slot coverage from the build's vertices): default camera 0.27% of the frame at rest, max
  0.33%; summon 1.23% at rest, max 1.35% (wings open). Palette limit 5%: holds, no exception needed.
- Preview sheets (numpy/PIL, scratch): `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_views.png`, `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_clips_side.png`,
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_clips_front3q.png`, `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_clips_back.png`, `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_default_camera.png`,
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/ethren_summon.png`; scripts `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/sheet.py` and `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-644/framing.py`.

## Requests
- **Combat:** his vowbound.json row (Glimmer: Slow, Stop, mass wards; Swell `still_water`), then drop
  `vowbound_pending` from his creatures.json row and add `clip_by_skill` (Slow/Stop → `cast`, the ward → `cast` or a
  new clip, Still Water → `special`).
- **UI (battle_sandbox.json):** a `stand_ins.ethren` row if wanted (creatures.json carries height 2.5 and radius 0.6
  until then).
- **battle-presentation (choreo.json):** `first_call_flags.ethren` for his Ch13 first call, and `rise`/`dismiss` as the
  entry and dismissal clips (as for Ilun, M3-CRE-639).
- **battle-vfx:** Still Water's stop at the contact (1.45 s), the field's VFX freezing.
- **characters:** Corran's face under the veil for Ch20 (the veil mesh `ethren_veil` / bone `veil` can be hidden or
  dropped).
- **PC render:** `creature_ethren` (no baseline), his portrait (joins the missing-PNG bake), and a palette-tool gold
  measurement on the summon frame.

## Notes
- For the first render: the lacquer's gloss carrying the light, whether the seams read as light inside the shell, the
  halo's inner face (the default camera sees it at about 14° to its plane, a crescent), the veil's faint glow, and the
  ring on the near hand.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
