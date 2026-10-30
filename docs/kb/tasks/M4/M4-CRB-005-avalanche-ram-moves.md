---
id: M4-CRB-005
title: "The Avalanche Ram's moves at the final bar: a clip per skill, the torn_fleece phase, anchors, the herd-cord"
role: character
status: review
owner_session: creatures-b
depends_on: [M4-A2P-059]
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
The Avalanche Ram (Ch12 boss, docs/kb/plan/act2/bosses/avalanche_ram.md §3–§5) at the Act I final-quality bar
(ADR 0041 §3, ADR 0205), with ADR 0204's `torn_fleece` phase kept. Nothing on it is ice (ADR 0015, M4-A2P-059).

## Acceptance criteria
- [x] Clips: `intro` (2.6 s), `ready`, `idle_b` (authored), `charge_gather`, `attack` (the charge, contact 0.75),
      `cast` retimed as the bellow (contact 0.9), `neck_sweep` (0.75), `fleece_shake` (0.6), `hit`, an authored
      `hit_b`, `ko`; the `torn_fleece` phase: `phase_tear` (the plate tears at 1.0), `idle_torn`, and `_torn`
      versions of attack, cast, charge_gather, neck_sweep, fleece_shake, hit, hit_b, ready and ko through the phase
      `clips` map. Every wind-up ≥ 0.45 s; every clip starts and ends on its phase's idle first frame (the intro's
      start, the KOs' ends and the `ready` loops excepted); hooves planted by the leg solve except where the stamp,
      the paw, the charge's stamp and the rear lift them; nothing under the floor.
- [x] Rig: unweighted `vfx_wound`, `vfx_core`, `vfx_phase`; a `cord` bone on `neck1` (the herd-cord's frayed end
      swings on a damped spring); a `plate` bone on `spine3` for the felted shoulder plate.
- [x] Phase parts: `ShoulderPlate` (hidden after `phase_tear`) and `TornShoulder` (the seep through the tear, shown as
      the phase starts, covered by the plate until it tears). No new material slot; 15,779 triangles (≤ 16k).
- [x] creatures.json: `contact` for every striking clip, `loop`, `vfx_anchors`, the `torn_fleece` phase row; no
      `clip_by_skill` (skills are combat's). The clip map for combat is in both sheets.
- [x] Tests: `test_avalanche_ram_*` in tests/unit/test_creature_bosses_act2.gd, the Ram case in
      test_creature_actor.gd updated for the new bones, tools/tests/test_avalanche_ram.py (the row matches the build).
- [x] Art sheet "As built", design sheet marked built.

## Notes
- **For combat (reviewer):** add the enemy row and skills, then `clip_by_skill`
  `{"ram_charge": "attack", "bellow": "cast", "neck_sweep": "neck_sweep", "fleece_shake": "fleece_shake"}` and the
  enemy's `torn_fleece` phase at 40% HP. The charge's gather is choreo's (`bosses.avalanche_ram.gather`); its clip
  `charge_gather` is there for presentation to play on the gather turn.
- **Why `show` and not `show_after` for `TornShoulder`:** the plate covers it until it tears at 1.0 s of
  `phase_tear`; with `show_after` the seep would come on a second after the tear, at the clip's end.
- Self-rendered and viewed (llvmpipe): every clip at five beats on the keth_seep_terrace preview from the battle
  camera and a closer camera on its line. Baselines not written.

## Review log
