# Handoff: character (creatures-b) 2026-10-30 #1

Branch `claude/creatures-b` (lead/gate-big18 fast-forwarded in, then `claude/new-session-mj8c3c` merged). Live log:
`docs/kb/handoffs/live/creatures-b.md`.

## Done
- GPU QA rows 12/35 (Moll): verified on big17; test that every Act I boss encounter seats real bodies. Row 36: the
  Reach's seat [-5.0,0,-2.4] and a lane test. Row 30: later-act arenas, record only. The Spar-wraith turns 45°.
- **M3-CRB-013, the move pass (review):** every Act I boss and Vowbound move has its own clip, a telegraph before
  contact and stays on the floor; the Hullgnaw carries its breach; the Drownbell's feet are planted by IK; the
  Reach's Breach stance stays in frame; all nine viewed from the battle camera. Contacts in the live log.
- **M3-CRB-014 (request to creatures):** review the phase-mapped KO in CreatureActor.
- **M3-CRB-015:** the Act II boss and Vowbound design sheets (docs/kb/plan/act2/bosses/, draft: pre-gate);
  **M4-CRB-001** (the Avalanche Ram's wool swap) filed, blocked by ADR 0203.

## In progress
- None.

## Exact next step
1. When the Lead lands this branch, merge the integration branch back and re-run `--filter=creature`, `boss`,
   `vowbound`, `ch0`; view the gate's drift for the shots listed in the live log's 01:30 entry.
2. When battle-presentation retimes VFX to the new contacts, re-render the boss intros and one choreo shot per boss.
3. At the Act I gate (ADR 0203): start M4-CRB-001, then the Act II bosses from the sheets.

## Known issues
- Pre-existing on big18: test_slice_shots (`slice_dock_night_yes`, a dialogue line); test_ch04_zones's Haluna
  camera (big17, passed on big18 in one run).
- The scratch render fixture (clip sheets at five beats per clip) lives only in the scratchpad; the agents' notes say
  its close-up camera should aim at the head bone, not the bounds.

## Files touched
assets_src/creatures/{bottle_hermit,hullgnaw,drownbell,spar_wraith,cinder_matron,undertows_reach,ilun,virel}/,
assets/creatures/<same>/, assets/ui/portraits/creatures/hullgnaw.png, game/data/creatures/creatures.json (these rows),
game/data/ui/battle_sandbox.json (boss_seats), game/creatures/creature_actor.gd (set_ko, M3-CRB-014),
tests/unit/test_creature_{bosses_act1,ilun_vowbound,actor}.gd, tests/unit/test_battle_boss_seat.gd,
tools/tests/test_creatures.py (HullgnawBreachTest), docs/kb/art/creatures/ sheets for these, docs/kb/plan/act2/bosses/,
docs/kb/tasks/M3/M3-CRB-01{3,4,5}*, docs/kb/tasks/M4/M4-CRB-001*, docs/kb/handoffs/live/creatures-b.md.
