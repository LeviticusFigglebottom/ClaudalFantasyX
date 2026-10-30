---
draft: pre-gate
adr: 0203
task: M3-CRB-015
author: creatures-b (docs only)
date: 2026-10-30
---
# Act II boss and Vowbound design sheets (draft: pre-gate)

**Status: draft, pre-gate.** Written under ADR 0203's preparation clause (docs only). Nothing here is built, and no
data, scene, asset or code changed. When the Lead tags `act1-complete`, these sheets become the brief for the Act II
boss and Vowbound tasks ([act2_plan.md](../../act2_plan.md) §2, §4.4, §4.6, §6). Proposed skill and clip ids are
marked *(proposed)*. Combat owns every id that reaches `skills.json`, `enemies.json` or `vowbound.json`.

## The sheets

| Ch | Sheet | Kind | Arena (`arenas.json`) | Model and rig owner | Built today |
|---|---|---|---|---|---|
| 10 | [mangrove_drowner.md](mangrove_drowner.md) | creature boss, 2 phases | `ossa_fen_roots` | creatures-b | mesh, rig, 10 clips, staging (no enemy row) |
| 11 | [lamp_engine.md](lamp_engine.md) | construct boss, 2 phases, with conduit-crawler adds | `lowlight_engine_hall` | creatures-b | engine and crawler models (no rows) |
| 12 | [avalanche_ram.md](avalanche_ram.md) | beast boss, field hazard; **wool swap** ([M4-CRB-001](../../../tasks/M4/M4-CRB-001-avalanche-ram-wool-swap.md)) | `keth_seep_terrace` | creatures-b | model (icy fleece: to swap) |
| 14 | [malcor_venn.md](malcor_venn.md) | people boss, 2 phases, with the flat-engine part | `ansedra_lagoon_escape` | characters (Venn); creatures-b (flat-engine) | flat-engine model only |
| 15 | [wakefin.md](wakefin.md) | creature boss in the dark | `bridal_barge_night` | creatures-b | model, 5 clips, staging |
| 16 | [abiding_guard.md](abiding_guard.md) | people boss (a group), then the storm | `drowned_choir_ring` | characters | nothing |
| 11 | [nhoa.md](nhoa.md) | Vowbound, Ice | (summon) | creatures-b | built (M3-CRE-642) |
| 12 | [hesk.md](hesk.md) | Vowbound, Holy | (summon) | creatures-b | built (M3-CRE-643) |
| 13 | [ethren.md](ethren.md) | Vowbound, Glimmer | (summon) | creatures-b | built (M3-CRE-644) |
| 16 | [kesh.md](kesh.md) | Vowbound, all six in turn | (summon) | creatures-b | **nothing** (this is her first sheet) |

## The standard every sheet holds (Act I's lessons, M3-CRB-013)

1. **Read at the battle camera's distance.** A lone boss is seen from about 12 m with the party in frame. Small or
   edge-on shapes read as props. Every sheet names its one recognisable shape and how it faces the camera.
2. **Every skill has its own clip** (`clip_by_skill`). No generic `attack` or `cast` is shared between skills; the
   generic clips stay only as fallbacks for unmapped skills.
3. **Wind-up at least 0.45 s before contact**, and the wind-up reads before the blow: a shape change you can see at
   12 m, not a twitch.
4. **Phase stances.** Every clip in a phase starts and ends on that phase's idle first frame, through the phase
   `clips` map, so nothing pops back to the phase-1 pose.
5. **Grounding.** Feet planted by IK while grounded, nothing under the floor or the water in any clip (GroundedClipsTest
   with no allow-list), and a breach or prop bone when a clip has to go into the water.
6. **Anchors.** Bosses carry unweighted `vfx_wound`, `vfx_core` and `vfx_phase`. Vowbound carry `vfx_core` and
   `vfx_keepsake`.
7. **The full clip set.** Bosses have `idle`, `idle_b`, `ready`, `intro`, one clip per skill, `hit`, `hit_b`, each phase
   clip with its phase versions, and `ko`. Vowbound have `idle`, `idle_b`, `ready`, `rise`, `dismiss`, one clip per
   skill, `special`, `hit`, `hit_b`, `defend`, `ko`, `victory` (and `release` for Act III's held form, already built
   for the three).

## The Act II rules every sheet checks ([act2_plan.md](../../act2_plan.md) §2a)

- **No ice, frost, rime, glacier or frozen water in any temple or set piece from Ch12 to Ch15** (ADR 0015). Ice
  belongs only to Nhoa, under Sunken Vey (Ch11), and even she has no frozen matter. Keth Pass snow is weather.
- Nothing is revealed about Malcor Venn at the wedding: he fights, bleeds and staggers as a living man.
- No echo of other games' bosses, names or spell tiers. Each sheet ends with an echo check. New names are checked
  against `tools/banned_terms.txt`.
- The bound-light rule: `glimmer_bound` is steady (no flicker, no drift, no shed motes). Only released motes rise
  (`glimmer_lift`), and only where the story says so.

## Balance, at a glance (balance_targets.md, Act II rows)

Boss curve for every sheet: naive ≤ 3%, role_answer 55–80%, smart 70–90%, p90 ≤ 80 actions. The two set pieces (the
Ch14 step-hold and the Ch16 storm) are on the set-piece curve, where `scripted_escape` counts as a win.

## Open questions across the sheets (for the Lead)

Each sheet lists its own questions. The ones that cross sheets:
1. **The Ch12 regulars.** `ridge_lynx` ("ear tufts frosted") and `scree_crawler` ("frost-split scree, a frost counter")
   carry frost in act2_roster.md under ADR 0015's Ch12–Ch15 rule. The rule names temples and set pieces, not the
   pass's wildlife, but the same wool-and-snow reading would be safer. Do we file a creatures task for them too?
2. **People bosses' clip contract.** Malcor Venn and the Abiding guard need the characters pipeline to export a
   battle clip set at boss quality (Act I's Stillguard Inquisitor is the only precedent). Do those clips live in
   creatures.json like a creature, or in a characters table?
3. **Kesh's battle scale.** She is colossal in the bind memory, but she has to fit the Vowbound slot in battle. This
   draft proposes 4.6 m in battle and a cinematic-only colossal scale (kesh.md).
