---
id: M3-CRE-637
title: "Build the flat-engine (Act II, Ch14 boss part) from its design sheet"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a619fe5cfc69108f9 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The flat-engine (`flat_engine`, docs/kb/art/creatures/act2/flat_engine.md) through the creature pipeline
(docs/kb/art/creatures/pipeline.md), wired the way the Lamp Engine (M3-CRE-623), the other construct, was. It is a
Ch14 boss part: a bound Lit Age engine on Warden Malcor Venn's barge that presses the lagoon flat, not a creature
that strikes. **Its first PC render is pending:** this environment may not render (human directive), so the model
was checked numerically from the GLB instead (below), and its review shot has no baseline yet.

## Acceptance criteria
- [x] `assets_src/creatures/flat_engine/build_flat_engine.py` on the creature kit: a squat 1.8 m drum (radius 0.9 m,
      1.30 m to the lid's crown above the water) of `lacquer_black` iron with two `brass` bands going to
      `bronze_patina` (patina weeping down the black below each band), wet below the splash line; a short iron stack
      with brass collars under a bell-shaped brass cowl on three struts (sooty underneath), to 2.42 m; a salt-glass
      porthole in a brass frame on the party's side (+z) with the bound light behind it (`glimmer_bound`, steady:
      README rule 3); eight 3 m paddles (hinge to tip) fanned flat on the water in a half ring astern and abeam
      (azimuths −87.5° to +87.5°, 25° apart), each an iron-strapped loom down from its hinge onto a long flat blade
      lying on y 0, `timber_weathered` darkened wet; each hinge a brass bracket and a lacquered pin barrel carrying one
      small closed `spawn_wound` mark (6 × 4 cm, the weak point: ADR 0151).
- [x] Two meshes on one rig, the break part's pair: `Engine` (whole) and `EngineBroken` (the drum split along its
      seam with each half tipped 6° apart, the window's glass crazed into facets and dark, the hinge marks dark, and
      the paddles slack: each slewed off the fan by −6..+10° and turned on its pin the least that keeps it on the
      water). The scene hides `EngineBroken`; nothing shows it yet (below).
- [x] 7,620 triangles (budget 8k): `Engine` 3,810 and `EngineBroken` 3,810 (each: iron 2,322, timber 1,072, hinge
      marks 288, window 128). 13 bones: the sheet's drum, chimney and eight paddle hinges, plus `root` and the drum's
      two halves (`half_a`, `half_b`), so the KO splits the whole mesh along the same seam. GLB 0.88 MB.
      Deterministic: `verify_blender_builds.py --job creature_flat_engine` prints identical (5 outputs).
- [x] Clips: `idle` (6 s: the paddles lift and press back in a slow wave round the ring, up to 3.5°, the cowl sways),
      `cast` (the stilling, 1.8 s: every paddle lifts 11° together by 0.6 s and presses down flat at 0.8 s, the
      contact, and holds; the drum rises 3 cm on the lift and settles; the cowl jolts), `attack` (the same clip, by the
      sheet: it does not strike), `hit` (the drum jolts back 3° and paddle 3 kicks up 24°, peak 0.1 s) and an authored
      `hit_b` (the other way, 1.25×, paddle 5), `ko` (2.6 s, the break: a shudder, then the seam splits and each half
      tips 7° outward about its far base edge, opening the seam 0.30 m at the lid, the stack leans 11°, and the paddles
      go slack one by one, slewing off the fan). The kit adds `idle_b` (the stilling at 0.3×).
- [x] materials.json (`iron`, `window`, `timber`, `hinge`) and write_materials.py; the Blender job (appended);
      PROVENANCE rows (their own commit).
- [x] Import rule lists `res://assets/creatures/flat_engine/`; the `.glb.import` runs the creatures post-import script
      (all four slots resolve on both meshes).
- [x] game/creatures/flat_engine/flat_engine_battle.tscn (`EngineBroken` hidden by a property override on the
      instanced GLB) and the creatures.json row: contacts (attack and cast 0.8 s), `ko_fade_sec` 1.2,
      `stand_in.yaw_deg` 90, and a `portrait` row (yaw 30, pitch 24, to show the paddle fan) on the default lights:
      its measured median albedo luminance is 0.338 (sRGB; 0.095 linear), over 0.2, so no dark rim (to be checked on
      the first render: the drum itself is near-black, the paddles carry the median).
- [x] tests/unit/test_creature_actor.gd: the rig, the contacts, no phases, `Engine` shown and `EngineBroken` hidden,
      no break part yet, the stilling lifts every paddle over 8° at 0.6 s and presses each under 1° at 0.8 s, the hit
      kicks paddle 3 over 15° at 0.1 s, and the KO tips both halves 5–9° with every bone on the water.
- [x] Shot `creature_flat_engine` (idle, three-quarter) in tests/screenshots/shots.json with a stage scene like the
      others'. **Not captured; no baseline: it needs the PC render.**
- [x] Bestiary portrait manifest: a `flat_engine` row appended to tools/portraits/portraits.json (default lights).
      `test_creature_portraits` stays red only for the PNGs the PC has not baked; this adds `flat_engine.png` to them.
- [ ] Break part (not this task): see Notes. No enemies.json row (none was invented; the validator allows a creature
      no enemy uses yet).

## Numeric check (no render)
Measured from the exported GLB by skinning every baked frame of every clip (glTF node animation, joint matrices,
linear blend skinning) for each mesh. Clips are on time (M3-CRE-630), so GLB times are the authored ones.

| Clip | Length | Peak (GLB) | `Engine` y (min..max) | `EngineBroken` y (min..max) |
|---|---|---|---|---|
| idle | 6.0 s | 3.0 s (the wave's crest) | 0.000..2.420 | 0.000..2.454 |
| attack | 1.8 s | 0.6 s lifted, 0.8 s pressed (contact) | 0.000..2.443 | 0.000..2.477 |
| cast | 1.8 s | 0.6 s lifted, 0.8 s pressed (contact) | 0.000..2.443 | 0.000..2.477 |
| hit | 0.7 s | 0.100 s | 0.000..2.451 | 0.000..2.506 |
| hit_b | 0.7 s | 0.100 s | 0.000..2.457 | 0.000..2.494 |
| ko | 2.6 s | 1.63 s (the split's overshoot) | 0.000..2.451 | 0.000..2.482 |
| idle_b | 1.3 s | 0.43 s | 0.000..2.427 | 0.000..2.459 |

- Rest: 2.42 m to the cowl's crown, the drum's skirt and every paddle's underside on y 0 (the blades at 0.003), 7.96 m
  across the fan (x ±3.98), z −0.93 (the drum's bow side) to +3.91 (the astern paddle tips).
- Grounding: nothing goes under y 0 in any frame of either mesh (lowest −0.0000), so the engine passes
  GroundedClipsTest without an ALLOW entry. Where the hit's jolt or the KO would press a blade or the drum's skirt
  under, common/grounding.py turns that paddle up on its pin, or lifts the drum, the least it takes.
- Colours: the build's swatches are `lacquer_black` #1D1916, `brass` #B08D57, `bronze_patina` #5F8A78, `salt_glass`
  #BFE6E0, `glimmer_bound` #4FB3B0, `timber_weathered` #7E6A55, `spawn_wound` #3FE0C8, all in palette.json; the
  slots' emission colours are `glimmer_bound` (window, steady) and `spawn_wound` (hinge, the weak-point pulse). Vertex
  albedo luminance (linear) 0.0123..0.5592 on `Engine` and 0.0123..0.2533 on `EngineBroken`, inside the floor
  (0.0101) and the ceiling (0.8014): none below or above. Emissive vertices (mask > 0.5): `Engine` 80 window and 192
  hinge-mark vertices; `EngineBroken` none.

## Notes
- **y 0 is the water, and the drum stops at it.** The sheet has the drum "half sunk through the deck into the
  water". Only what is above the water is modelled: the lagoon hides the rest at night, and a modelled underwater
  half would only show as a too-tall drum on the waterless review stage and in the portrait. So the drum ends at the
  waterline in a wet skirt and the build passes the grounding test instead of being allow-listed. The barge's deck
  is the encounter set's, not this model's.
- **Rest is the pressed pose.** The paddles lie on the water at rest, so "pressing" is authored as lifting them and
  pressing them back down to y 0, never through it (the idle's wave, the stilling).
- **The break part is not wired.** tools/validate_creatures.py requires each `break_parts` key to be an existing
  skill, and skills.json has no charge skill for the engine yet (Liss's, once Ch14's combat kit names it). So the
  creatures.json row lists no part, and the scene hides the broken mesh with a property override. When the skill
  exists, add to the row: `"break_parts": {"<liss_charge_skill>": {"whole": ["Engine"], "broken": ["EngineBroken"]}}`.
  CreatureActor then hides `EngineBroken` itself and swaps the pair on `charge_broken`; the override stays harmless.
- **Until then the KO's window stays lit.** The sheet's KO swaps in the broken mesh (the shader's emission is
  static); without the part, the KO splits the whole mesh's drum, leans the stack and slackens the paddles, but the
  window and the hinge marks keep their light while it fades. The part's swap fixes this; an encounter that breaks the
  engine by KO rather than by charge would want a `ko` hook in CreatureActor (not added: no encounter yet).
- **Not modelled, by the sheet:** the window breathing in the idle and brightening and holding in the stilling (the
  emission is one steady slot: VFX or a shader parameter), the water pulled flat and still round the party (VFX), the
  barge.
- **For the first PC render:** check the read at battle distance (a dark drum with a steady teal window and a fan of
  paddles flat on the water), whether the hinge marks read apart from the window (two teals: `spawn_wound` pulsing,
  `glimmer_bound` steady), the paddles' wet timber on the stage floor, and the portrait on the default lights (rim
  and kick only if the drum reads as a hole).

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
