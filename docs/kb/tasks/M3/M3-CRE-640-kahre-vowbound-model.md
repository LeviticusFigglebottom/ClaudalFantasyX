---
id: M3-CRE-640
title: "Kahre, the Forge-Crowned (Lightning, bound Ch5): a Vowbound creature model in place of the battle placeholder"
role: character
status: review
owner_session: "creatures (worktree agent-aff95178e46e68414, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue (2026-10-27, item 5 "more creatures") and the Ilun precedent (M3-CRE-638). kahre is in
game/data/battle/vowbound.json and callable once its bound flag is set, but it has no model, so a call shows a
primitive placeholder. Build it per docs/kb/story/vowbound.md §2, the same way Ilun was built: a design sheet
(docs/kb/art/creatures/vowbound/kahre.md), the model and clips (the stand-in set plus rise, dismiss and special),
the creatures.json `"vowbound": true` row (CreatureModels attaches it), a review shot, and a portrait manifest row.

**His first PC render is pending:** this environment may not render, so he was checked numerically and on
silhouette sheets drawn from the build's own vertices (below), and his review shot has no baseline yet.

## Acceptance criteria
- [x] Design sheet `docs/kb/art/creatures/vowbound/kahre.md`: the idea (an upright hornbill-headed smith-beast), size
      (3.37 m, justified against Ilun, the heroes and the summon frame), palette swatches (volcanic_stone, ash,
      brass, bone, iron; no red, no orange), the bound light (`glimmer_bound` 1.2, steady, no particles), the anvil
      chest, the spark mane, the hammer, the clips and timings, the rig, the budget, and **the framing check**. No
      weak point (ADR 0151 is for foes).
- [x] `assets_src/creatures/kahre/build_kahre.py` on the creature kit: knuckle-walking forearms and three-toed hind
      feet; an anvil chest plate (face, horn, waist) with a bound-light struck star on each flank (raised boss and
      seven crack ribbons, slot `strike`); a mane of 25 zig-zag bolts in three rows, flat double-faced blades skinned
      to the neck chain (slot `mane`; geometry, not particles, moving only with the neck); a ground hornbill's bill,
      jaw and brass casque; the smith's cross-peen hammer fused upright into the casque (slot `hammer`, unlit, iron
      and ash wood with a sand_cloth wrap); five hanging tail feathers.
- [x] **Grounded by construction:** `solve_legs` keys every leg at every baked frame with a two-bone solve in the
      leg's own plane (in the parent's rest frame, matching creature_kit's export) and a level foot, blended with an
      authored free pose where a foot leaves the ground (the Last Strike's rear). `hit_b` and `idle_b` are authored,
      because the kit's scaled copies would push the solved feet through the water.
- [x] **14,080 triangles** (budget 16k): feet and fists 3,440, limbs 2,128, torso 1,904, bill and casque 1,656, anvil
      1,272, neck 1,040, hammer 1,008, mane 500, skull 360, strike 352, eyes 240, tail 180. 7,986 vertices, 22 bones,
      GLB 1.37 MB. Seven slots: `body`, `anvil`, `strike`, `mane`, `beak`, `eye`, `hammer`.
- [x] Clips (13): `idle` 4.0 s loop, `ready` 1.4 s (a stamp of the left fist), `attack` 1.2 s (contact 0.55 s: the
      casque strike, the hammer's face meeting the foe at 1.4 m, 2.1 m out), `cast` 1.6 s (contact 0.8 s: Forge
      Bolt), `hit` 0.5 s (peak 0.10 s), authored `hit_b` (peak 0.10 s, the other side, 1.35×), `defend` 1.2 s,
      `ko` 2.0 s (he lies down, held from 1.6 s), `victory` 2.2 s, `rise` 2.6 s (from a crouch, left fist, right fist,
      up), `dismiss` 1.0 s (ends bowed), `special` 2.8 s (contact 1.55 s: Last Strike, the hammer's face the lowest
      point of him, 3 cm over the water, 1.6 m in front), authored `idle_b` 1.2 s.
- [x] materials.json (write_materials.py); every emissive slot `glimmer_bound` #4FB3B0 at 1.2 with no pulse; the
      hammer, anvil and beak are not lit. The Blender job `creature_kahre` (appended). PROVENANCE rows (their own
      commit). **`verify_blender_builds.py --job creature_kahre`: 8 identical.**
- [x] Import rule lists `res://assets/creatures/kahre/`; the `.glb.import` runs the creatures post-import script.
- [x] `game/creatures/kahre/kahre_battle.tscn` and the creatures.json row `kahre`: `"vowbound": true`,
      `clip_by_skill` (`forge_bolt` → `cast`, `last_strike` → `special`), contacts, `stand_in` `yaw_deg` −90 plus
      **`height` 3.3 and `radius` 0.75**: Kahre has no battle_sandbox.json row (UI's), so without them the VFX
      anchors would sit on a 1 m fighter and the ring would be 0.42 m. tools/validate_creatures.py now allows
      `height` and `radius` in `stand_in` (numbers > 0), with a test in tools/tests/test_creatures.py. No code
      change: `CreatureModels.stand_in_overrides` already answers for any `vowbound` row (M3-CRE-638).
- [x] Godot tests `tests/unit/test_creature_kahre_vowbound.gd` (matched by `creature`, `vowbound` and `kahre`): the
      stand-in resolves (scene, yaw −90, height, radius, no hover); the scene loads headless with all 13 clips, the
      skill mapping and the contacts; FighterStandIn plays `ready` and `ko` and hands it the KO; the feet stay
      planted in the idle, the casque strike drives the head down and forward, the rise starts crouched, the KO lies
      him down, Last Strike brings the head 2.4 m down from the rear to the water.
- [x] `tests/integration/test_kahre_summon_path.gd` (Ilun's precedent): the battle sandbox with the
      choreo_vowbound_rise fixture, Kahre bound from the live tables in the test (no fixture names him;
      battle_fixtures.json is UI's), Asha calls him, and his stand-in shows the actor, with and without the
      first-call cinematic forced.
- [x] Shot `creature_kahre` (idle, three-quarter, scale bars) appended to tests/screenshots/shots.json with a stage
      scene. Portrait manifest row `kahre` appended to tools/portraits/portraits.json (as the Lead did for Ilun).
      **Neither captured nor baked: they need the PC render.**

## Framing check (no render)
Every vertex of every baked frame projected with the camera director's own math (`shot_pose`; the battle axis is
the default camera's flat −x) on the Vowbound slot (party Slot1, x 3.0, z −1.1), turned by `yaw_deg` −90, 16:9.
- **Default battle camera.** His length runs along the battle axis, across the screen, and the slot's mark sits at
  u 0.765, so only about 0.85 m behind it is inside the safe frame's right edge (u 0.85). The first build (3.6 m long,
  centred, the tail out behind) reached u 0.92, Ilun's failure. Rebuilt upright and compact (hips at z −0.42, rump at
  −0.89, the tail feathers hanging), every frame of every clip keeps **u ≤ 0.851** (idle 0.848, hit_b's peak 0.851,
  KO 0.843, Last Strike 0.846). At rest the top is at v 0.110, inside; the raised head in `cast` (v 0.011) and one
  frame of the Last Strike's rear (v −0.001) pass the HUD's top margin, which is fine during an action (the director
  plays the action's lead shot).
- **Summon shot.** x 0.37–0.62, top v 0.16–0.23 (idle, ready, rise's end): inside. His feet are under the HUD's
  bottom band (v 0.90), as any grounded fighter's are from that low camera looking 1.6 m up.

| Clip | Length | Lowest vertex y (GLB, skinned) | Highest |
|---|---|---|---|
| idle | 4.0 s | 0.000 (a sole) | 3.43 |
| ready | 1.4 s | 0.000 | 3.65 |
| attack | 1.2 s | 0.000 | 3.88 |
| cast | 1.6 s | 0.000 | 4.04 |
| hit / hit_b | 0.5 s | 0.000 | 3.65 / 3.70 |
| defend | 1.2 s | 0.000 | 3.37 |
| ko | 2.0 s | 0.000 | 3.63 |
| victory | 2.2 s | 0.000 | 3.84 |
| rise | 2.6 s | 0.000 | 3.60 |
| dismiss | 1.0 s | 0.000 | 3.52 |
| special | 2.8 s | 0.000 | 4.11 |
| idle_b | 1.2 s | 0.000 | 3.46 |

No GroundedClipsTest allow-list entry. Rest: x ±0.85, y 0 to 3.37, z −0.89 to +1.96.

**Preview sheets** (numpy and PIL from the build's vertices, painter's algorithm, no Godot), scratch, not committed:
`/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-640/kahre_views.png`
(six rest views), `.../kahre_clips.png` (21 key poses), `.../kahre_default_camera.png` and `.../kahre_summon.png`
(the two framings with the HUD safe frame drawn); the scripts `sheet.py`, `diag.py` (per-clip lows and screen
extents), `hammer.py` and `blow.py` (the Last Strike contact search) are beside them.

## Requests
- **battle-presentation (choreo.json):** the M3-CRE-638 request (`vowbound.entry.clip` and `summon_cinematic.entry.clip`
  `rise`, `vowbound.dismiss.clip` `dismiss`) fits Kahre too: his `rise` is 2.6 s from a crouch with two steps up, and
  his `dismiss` 1.0 s ends bowed. `summon_cinematic.first_call_flags` has no `kahre` entry, so his first call never
  plays the cinematic; if it should, add `"kahre": "<a seen-flag>"` (a flag in flags.tres; story's call).
- **UI (battle_fixtures.json, optional):** a fixture that binds `kahre` (with his vowbound row and his skills in its
  frozen tables) would let a Vowbound shot show him; the integration test binds him itself until then.
- **menus:** the Ilun request stands (portrait test vs. Vowbound rows); the `kahre` manifest row was appended like
  Ilun's, so it adds `kahre.png` to the PNGs the PC has to bake.

## Notes
- **The light.** The hide's inner glow is lower than Ilun's (mask 0.05, not 0.08–0.10): he is dark stone with light
  held in it, and the mane and the struck star carry the bound light. Check on the render that the hide does not read
  teal; if it does, lower GLOW (assets_src/creatures/kahre/build_kahre.py) further.
- **The anvil** is metallic 0.8 (dark iron, brass at the face's edges): check it reads as iron and not as a black
  hole on the default camera's side view.
- **For the first PC render:** `creature_kahre`, and a Vowbound battle shot with him called (none exists yet).

## Review log
