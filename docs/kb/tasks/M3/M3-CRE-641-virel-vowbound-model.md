---
id: M3-CRE-641
title: "Virel, the Kite-Serpent (Fire, bound Ch8): a Vowbound creature model in place of the battle placeholder"
role: character
status: review
owner_session: "creatures (worktree-agent-ab22a89553400c234, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-638]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue (2026-10-27, item 5 "more creatures") and the Ilun precedent (M3-CRE-638). virel is in
game/data/battle/vowbound.json and callable once its bound flag is set, but it has no model, so a call shows a
primitive placeholder. Build it per docs/kb/story/vowbound.md §3, the same way Ilun was built: a design sheet
(docs/kb/art/creatures/vowbound/virel.md), the model and clips (the stand-in set plus rise, dismiss and special),
the creatures.json `"vowbound": true` row (CreatureModels attaches it), a review shot, and a portrait manifest row.
**Her first PC render is pending:** this environment may not render, so she was checked numerically and on silhouette
sheets drawn from the build's own vertices (below), and her review shot and portrait have no image yet.

## Acceptance criteria
- [x] Design sheet `docs/kb/art/creatures/vowbound/virel.md`: silhouette and size, the coil and why, the framing
      check on both cameras, palette swatches, the fire-versus-bound-light choice, the kite (panels, seams, frame,
      bridle, streamers), the key, the clips and their timings, the rig, the budget. No weak point (ADR 0151 is for
      foes).
- [x] `assets_src/creatures/virel/build_virel.py` on the creature kit: a ribbon-serpent of sailcloth panels, 6.25 m
      long (a 0.75 m kite head and a 5.5 m body) coiled once round an upright oval loop (1.2 by 1.36 m, centre 1.7 m
      over the water) in a plane turned 22° off the battle axis, the tail's pass 0.55 m deeper than the neck's; 14
      scalloped panels with every hem and cross-seam a band of bound light (geometry, skinned with the cloth: no
      particles); a timber frame (spine spar, a batten per panel, the bowed crest-spar) on the cloth's outer face; a
      three-line bridle meeting 0.38 m under her throat, where the brass tuning key hangs on a 10 cm cord; two tail
      streamers. Built **hovering** (no stand-in `hover`). 16 bones, weighted by arc length (the coil passes close
      to itself).
- [x] **12,158 triangles** (budget 16k): seams 4,620, sail 3,888, spars 2,538, eyes 448, key 352, cord 168, streamers
      144. 6,279 vertices. GLB 1.05 MB. Five slots: `sail`, `seam`, `spar`, `cord`, `key`.
- [x] Clips (13): `idle` 4.0 s loop, `ready` 1.4 s, `attack` 1.2 s (contact 0.5 s), `cast` 1.6 s (Kite Flare, contact
      0.6 s, then jabs at 0.88 and 1.15 s), `hit` 0.5 s (peak 0.10 s, numpy and GLB), `defend` 1.2 s, `ko` 1.8 s,
      `victory` 2.2 s, `rise` 2.6 s, `dismiss` 1.0 s, `special` 2.4 s (Flare Line, contact 1.4 s), and the kit's
      `hit_b` and `idle_b`. The key counter-turns 0.9 of the head's turn, 0.12 s behind it.
- [x] materials.json and write_materials.py; every emissive slot `glimmer_bound` #4FB3B0 at 1.2 with no pulse; the
      frame, cord and key are not lit. The Blender job `creature_virel` (appended). PROVENANCE rows (their own
      commit). **`verify_blender_builds.py --job creature_virel`: 6 identical.**
- [x] Import rule lists `res://assets/creatures/virel/`; the `.glb.import` runs the creatures post-import script.
- [x] `game/creatures/virel/virel_battle.tscn` and the creatures.json row `virel`: `"vowbound": true`,
      `clip_by_skill` (`kite_flare` → `cast`, `flare_line` → `special`), contacts, `stand_in.yaw_deg` −90, no `hover`,
      `portrait` yaw 72° (square to her sails). CreatureModels already attaches a `vowbound` row (M3-CRE-638): no code
      changed.
- [x] Godot tests `tests/unit/test_creature_virel_vowbound.gd` (matched by `--filter=creature`, `--filter=vowbound`
      and `--filter=virel`): the stand-in resolves to the model (scene, yaw −90, no hover; she is no enemy); the scene
      loads headless with all 13 clips, the skill mapping and the contacts; FighterStandIn plays `ready` and `ko` on
      her and hands her the KO; the idle undulates, the rise starts furled, the KO droops her head with the key still
      hanging, the attack lashes forward and down, Flare Line winds in and then pulls her into a line over 5 m.
- [x] `tests/integration/test_virel_summon_path.gd` (`--filter=virel`): the battle sandbox calls her (the Vowbound
      fixture `choreo_vowbound_rise` with Virel bound instead of Ilun; her vowbound.json row and her skills join the
      fixture's frozen tables, which hold only Ilun's) and her stand-in shows the actor, after the call and with the
      first-call cinematic forced.
- [x] Shot `creature_virel` (idle, `flank_high`, with the heroes' scale bars) appended to tests/screenshots/shots.json
      with a stage scene like Ilun's. **Not captured; no baseline: it needs the PC render.**
- [x] Portrait manifest row `virel` appended to tools/portraits/portraits.json (as the Lead added Ilun's). **Not
      baked: the PNG and its PROVENANCE row come from the PC's bake**, so test_creature_portraits now lists 18 missing
      PNGs (the 17 already requested and hers).

## Numeric check (no render)
Measured from the exported GLB by skinning every baked frame of every clip (tools/tests/test_creatures.py
`skinned_lowest`); the numpy report (`python3 assets_src/creatures/virel/build_virel.py --report`) gives the same.

| Clip | Length | Lowest vertex y | Notes |
|---|---|---|---|
| idle | 4.0 s | 0.722 | a wave nose to tail, 0.9° bend and 4° luff per bone, body ±4 cm, streamers twice a cycle |
| ready | 1.4 s | 0.761 | gathered and reared at 0.5 s, taut at 0.95 s |
| attack | 1.2 s | 0.731 | reared at 0.3 s; the head lashes 0.43 m forward and 0.68 m down by the contact (0.5 s) |
| cast | 1.6 s | 0.761 | the flare by 0.35 s, jabs at 0.6 (contact), 0.88 and 1.15 s |
| hit | 0.5 s | 0.761 | peak 0.10 s |
| hit_b | 0.5 s | 0.760 | peak 0.10 s |
| defend | 1.2 s | 0.761 | wound tight, held 0.3–0.85 s |
| ko | 1.8 s | 0.561 | head droops 0.49 m, root settles 0.2 m, held from 1.45 s; the key hangs (down axis y −0.997) |
| victory | 2.2 s | 0.760 | climbs 0.18 m by 0.8 s |
| rise | 2.6 s | 0.760 | starts furled (head 0.82 m below rest), open by 1.5 s |
| dismiss | 1.0 s | 0.761 | ends furled |
| special | 2.4 s | 0.353 | wound at 1.0 s (head to tail 1.9 m); the line at 1.4 s, 5.4 m end to end, tail 1.07 m up, head 2.65 m up and 4.8 m ahead; highest frame 3.48 m (the release) |
| idle_b | 1.14 s | 0.761 | the kit's fidget |

- Rest: x −0.92 to +0.61, y 0.76 (the loop's lowest hem) to 2.94 (the crest-spar), z −0.58 to +1.51.
- **No clip goes under the water**, so no GroundedClipsTest allow-list entry. The KO test's grounded branch holds
  (the root drops 0.2 m).
- **Framing** (every frame of every clip projected through the default battle camera on the Vowbound slot and the
  `summon` shot; margin to the HUD safe frame, choreo.json `camera.safe_frame`, as a fraction of the screen):
  default camera at rest left 0.61, right 0.05, top 0.09, bottom 0.24; every clip inside, the tightest right 0.011
  (victory) and top 0.016 (attack's rear), except Flare Line's release, which touches the right edge for a frame
  (−0.002, under 3 px at 1280). Summon shot at rest left 0.32, right 0.21, top 0.15, bottom 0.04; `ready`, `rise`
  and `idle` (what it plays) inside; the KO (−0.008) and Flare Line's line (−0.057) leave it at the bottom, and
  neither plays on it. **Her tail stays inside the right edge** (the lesson of Ilun's): she is coiled, her head
  toward the foes.
- Colours: `sand_cloth` #C9B48E, `faded_teal_cloth` #5E9A96, `gauze_white` #EBE7DF, `timber_weathered` #7E6A55,
  `brass` #B08D57, `deep_teal_shadow` #0E4A55 (albedo) and `glimmer_bound` #4FB3B0 (emission), all palette.json
  swatches, inside the albedo floor and ceiling. No `ember_orange` on her form (palette.json: flame and horizon only,
  the Fire VFX base; act1_ch08.md F07 and §5 Light: her seams read as steady `glimmer_bound`, and the fire element is
  her battle VFX's). The sheet has the reasoning.
- **Silhouette sheets** (numpy and PIL from the build's vertices, painter's algorithm, no Godot):
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-641/virel_views.png`
  (six rest views, including the review shot's `flank_high`),
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-641/virel_clips.png`
  (16 key poses),
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-641/virel_summon.png`
  (the summon shot with the HUD safe frame) and
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-641/virel_default_camera.png`
  (the default battle camera on the Vowbound slot: idle 0 and 1 s, Flare Line's contact, Kite Flare's contact). The
  per-frame margins come from `.../M3-CRE-641/framing.py`. Scratch, not committed.

## Requests
- **UI (game/data/ui/battle_sandbox.json `stand_ins`): add a `virel` row.** Ilun has one (height 2.3); Virel has
  none, so her stand-in spec has no `height`: FighterStandIn uses 1.0 m (damage numbers and markers at 1.0 m, under
  her head at 2.6 m) and BattleVfx uses 1.7 m for its anchors (chest 1.02 m, the bottom of her loop). Suggested:
  `"virel": {"shape": "capsule", "color": "#C9B48E", "radius": 0.5, "height": 2.6, "tint": "#C9B48E", "emission":
  "#4FB3B0", "emission_energy": 0.45}` (chest 1.56 m, the loop's middle; head 2.6 m, her head). The model needs no
  change for it.
- **battle-presentation (choreo.json): Virel's first call and her entry clips.** (a) `summon_cinematic.first_call_flags`
  lists only `ilun`, so Virel's first call (act1_ch08.md B16: "the full Virel summon cinematic plays on the first
  call") needs `"virel": "ch08_virel_first_call_seen"` and that flag declared in flags.tres. (b) The same ask as Ilun's
  (M3-CRE-639): `rise` for the entry and `dismiss` for the dismissal; Virel has both (2.6 s and 1.0 s, in place).
  Until then `ready` plays on both and reads acceptably (a gather and a snap taut).
- **battle-vfx (effects.json): her fire.** Kite Flare (`kite_flare`) and Flare Line (`flare_line`) carry the fire
  colour (`ember_orange` and the flame swatches): her own seams are `glimmer_bound` and never change colour, so the
  warm light of the Flare Line frame (act1_ch08.md §5: "the one warm, bright frame of the set-piece. It is fire light,
  not glimmer") must come from the effect. Flare Line's line runs from her tail (1.05 m up, 0.4 m behind her mark) to
  her head (2.65 m up, 4.8 m ahead) at the contact (1.4 s); an effect laid along that line would burn the whole
  kite-string at once.
- **PC render:** `creature_virel` (new, no baseline), her portrait (tools/portraits/portraits.json `virel`, joins the
  bake already requested for the 17 missing PNGs), and the first render of a Virel call (no shot calls her yet).

## Notes
- **Why not laid out long.** A 6 m serpent laid along the battle axis would cross the default camera's right safe
  edge by metres (the Vowbound slot is 1.1 m from it), and laid across it would face the default camera end-on.
  Coiled once, she is a kite flown in a loop: the shape keeps the length (6.25 m of cloth) in a 2.1 m by 2.2 m figure.
- **Flare Line leaves her mark.** The special's line reaches 4.8 m toward the foes over the field (by design: the
  whole kite-string burning at once over the wall-head, act1_ch08.md B16). `special` is not in the kit's
  IN_PLACE_CLIPS, and its root never moves horizontally (the body bone's offset does it), so the sequencer's
  placement is unaffected.
- **For the first PC render:** the seams' brightness against the cloth, whether the cloth reads lit through from the
  seams, the frame on the cloth, the key on the summon frame, and above all whether the still teal seams read as fire
  held still (the point) or simply as teal.

## Review log
