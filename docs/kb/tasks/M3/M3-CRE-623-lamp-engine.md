---
id: M3-CRE-623
title: "Build the Lamp Engine (Act II, Ch11 boss) from its design sheet"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-af5577379119314f8 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The second Act II build from M3-CRE-620's sheets: the Lamp Engine (`lamp_engine`,
docs/kb/art/creatures/act2/lamp_engine.md) through the creature pipeline (docs/kb/art/creatures/pipeline.md), the
way the Mangrove Drowner (M3-CRE-621) was built. **Its first PC render is pending:** this environment may not render
(human directive), so the model was checked numerically from the GLB instead (below), and its two review shots have
no baselines yet.

## Acceptance criteria
- [x] `assets_src/creatures/lamp_engine/build_lamp_engine.py` on the creature kit: a 3.4 m bell-hooded brass tower on
      four short jointed legs (lacquered hip and knee balls, three-clawed lamp-stand feet); a lantern housing of
      three gimballed rings (tiers) of four petal plates round a central column, each petal carrying its quarter of
      a polished hoop and one salt-glass lamp on a gimbal fork (twelve lamps); two long trimming arms off the hood's
      rim with scissor heads (a fixed and a moving blade); a cracked salt-glass core globe threaded on the column
      inside the housing. Rule 3 (a Lit Age construct): the lamps' light and the core are `glimmer_bound`, steady
      (no pulse); the gimbal hubs (24, two per lamp) are the `spawn_wound` weak points. `brass` going to
      `bronze_patina` and wet below the waterline (its knees, y 0.85) with verdigris runs, `lacquer_black` joints
      and petal ribs, a sooty inside to the petals and the hood, `sea_glow` drips down the glass. Every colour is a
      palette.json swatch.
- [x] 18,488 triangles (budget 20k), 50 bones, GLB 2.6 MB. Deterministic: `verify_blender_builds.py --job
      creature_lamp_engine` prints identical (5 outputs).
- [x] Clips: `idle` (6 s: the rings turn against each other ±12–16°, the lamps sway, each arm's shears tick),
      `attack` (the trim: the right arm winds up with its shears open and snips forward, contact 0.6 s of 1.3 s),
      `cast` (the gathering: the lamps swing one by one toward the target through their gimbals and lift, the arms
      rise, a held breath at 1.0 s), `hit` (the rings jolt and a lamp swings loose on its gimbal, peak 0.1 s) and
      an authored `hit_b` (the other way, another lamp), `ko` (from the open pose: the rings sag, the lamps hang,
      the arms drop into the water and the frame kneels 0.55 m, its feet kept flat), `phase_change` (`opened`,
      2.0 s), `idle_opened`, and the strikes from the open pose (`attack_opened`, `cast_opened`, `hit_opened`, the
      pose composed exactly with each key's rotation). The kit adds `idle_b`.
- [x] materials.json (`frame`, `hub`, `glass`, `core`) and write_materials.py; the Blender job; PROVENANCE rows.
- [x] game/creatures/lamp_engine/lamp_engine_battle.tscn and the creatures.json row: phase `opened` (clip,
      `idle_opened`, the open strike map; nothing hidden: the closed housing hides the core), contacts (attack and
      attack_opened 0.6 s, cast and cast_opened 1.0 s), loops, `stand_in.yaw_deg` 90, `ko_fade_sec` 1.2, and a
      `portrait` row on the default lights (mid-tone brass, not a dark row; to be checked on the first render).
- [x] Import rule lists the folder; the `.glb.import` runs the creatures post-import script.
- [x] tests/unit/test_creature_actor.gd: the engine opens (phase clip first, then `idle_opened`, which loops), its
      middle ring stands folded back in the open idle (60–76° off rest), it trims from the open pose with its
      contact, and its open hit wins over the variants.
- [x] Shots `creature_lamp_engine` (idle) and `creature_lamp_engine_opened` (phase `opened`) in
      tests/screenshots/shots.json with stage scenes like the Drowner's. **Not captured; no baselines: they need
      the PC render.**
- [ ] Encounter (not this task): an enemies.json row with `model` and a phase `opened` at 50% HP when the Ch11
      encounter is designed. No enemy row was invented; the validator allows a creature no enemy uses yet.

## Numeric check (no render)
Measured from the exported GLB by evaluating every clip frame by frame (glTF node animation, joint matrices, linear
blend skinning). The exporter writes every clip one frame (1/30 s) late, as for every creature, so GLB times read
0.033 s after the authored ones (the hit peaks at 0.10 s authored, 0.13 s in the GLB).

| Clip | Length | Peak (GLB) | Height (min..max y) | Feet lowest | Lamp clearance |
|---|---|---|---|---|---|
| idle | 6.0 s | 1.53 s | 0.000..3.412 | 0.000 | 0.072 m |
| attack | 1.3 s | 0.63 s (contact 0.6) | 0.000..3.400 | 0.000 | 0.082 m |
| cast | 1.8 s | 1.03 s | 0.000..3.458 (arms raised) | 0.000 | 0.074 m |
| hit | 0.7 s | 0.13 s | 0.000..3.407 | 0.000 | 0.063 m |
| hit_b | 0.7 s | 0.13 s | 0.000..3.409 | 0.000 | 0.040 m |
| ko | 3.0 s | 3.03 s (end) | -0.007..3.417 (kneels to 2.85) | -0.007 | 0.034 m |
| phase_change | 2.0 s | 1.43 s | 0.000..3.468 (arms spread) | 0.000 | 0.050 m |
| idle_opened | 5.0 s | 1.30 s | 0.000..3.412 | 0.000 | 0.042 m |
| attack_opened | 1.3 s | 0.63 s | 0.000..3.515 (wind-up) | 0.000 | 0.055 m |
| cast_opened | 1.8 s | 1.03 s | 0.000..3.458 | 0.000 | 0.052 m |
| hit_opened | 0.7 s | 0.13 s | 0.000..3.407 | 0.000 | 0.039 m |
| idle_b | 1.3 s | 0.77 s | 0.000..3.412 | 0.000 | 0.079 m |

- Rest: 3.400 m to the finial, feet at y 0, 3.6 m across the arms (x ±1.79), z ±1.14.
- Lamps: each lamp's bounding sphere (r 0.213 m round its vertices' centroid) holds no vertex of any other part in
  any frame of any clip (its own gimbal fork and hubs left out; its own petal and hoop checked by vertex distance).
  "Lamp clearance" is the nearest frame vertex to any lamp vertex; the nearest lamp-to-lamp sphere gap is 0.094 m
  (cast). The KO's feet sink 7 mm between its 0.1 s leg keys.
- The core is hidden closed and shows open: rays from a camera 9 m out at 15° elevation, from eight azimuths, reach
  1.3% of the core's front-facing vertices closed (a sliver through the 1.2° petal seams at 0° and 180°) and 48%
  open.
- Colours: the build's swatches are `brass` #B08D57, `bronze_patina` #5F8A78, `lacquer_black` #1D1916,
  `salt_glass` #BFE6E0, `glimmer_bound` #4FB3B0, `spawn_wound` #3FE0C8, `sea_glow` #1C6B78, all in palette.json;
  the slots' emission colours are `spawn_wound` (hub) and `glimmer_bound` (glass, core). Vertex albedo luminance
  0.0123..0.6829, inside the floor (0.0101) and ceiling (0.8014): none below or above.

## Notes
- **Break parts (the sheet's proposal, one per ring):** not wired. The validator requires `break_parts` to be keyed
  by an existing charge skill, and skills.json has none for the rings. They also need geometry: a ring's petals
  are in the one body mesh now, so each ring would need `Ring0..2` / `Ring0..2Broken` meshes (dark lamps, a
  broken hoop) as the Drownbell's `Rim` has. A task for the encounter's designers once the Ch11 encounter exists.
- **Not modelled, by the sheet:** the cast's lamps brightening in sequence (the glass emission is one steady slot:
  VFX or a per-lamp shader parameter), the KO's core going dark and the `glimmer_lift` motes rising from it (VFX),
  and the water drips (VFX; the glass carries sea_glow drip streaks).
- **The KO starts open.** CreatureActor plays the row's `ko` without the phase `clips` map, and a boss falls in
  phase 2, so the KO is authored from the open pose; a KO in phase 1 (an overkill past 50%) opens the rings in the
  0.12 s blend.
- Lamps don't stay dead level as their petals fold: the middle and top rings' lamps tip out 30° and 20° (`LEVEL`),
  because a level lamp in a petal folded 68° stands through its own hoop. The cast swings each lamp toward the
  target through its gimbal (out about its hubs, sideways about its outward axis), never inward.
- **For the first PC render:** check the read at battle distance (a ringed tower of steady lights, not the Cinder
  Matron's squat body), the portrait on the default lights (rim and kick only if it reads dark), the closed core's
  seam glow, and whether the hubs read apart from the glass (two teals: `spawn_wound` pulsing, `glimmer_bound`
  steady).

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
