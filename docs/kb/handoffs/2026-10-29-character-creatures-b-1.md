# Handoff: character (creatures-b) 2026-10-29 #1

Branch `claude/creatures-b`, with integration `claude/new-session-mj8c3c` and `lead/gate-big17` merged in.
Live log: `docs/kb/handoffs/live/creatures-b.md`.

## Done
- GPU QA rows 12/35: Moll verified a real body on big17; new test that every Act I boss encounter seats real bodies.
- GPU QA row 36: the Reach's boss seat moved to [-5.0, 0, -2.4]; test that no clip reaches the party lane.
- Row 30: re-checked, later-act arenas only (record).
- The Spar-wraith turns 45° toward the battle camera (it read edge-on as rigging).

## In progress
- None.

## Exact next step
1. When the Lead lands big17 and this branch, merge the integration branch back and re-run `--filter=boss`.
2. When the PC returns, it re-checks rows 12/35/36 on the real GPU (PC-QUEUE in the live log).

## Known issues
- test_ch04_zones `test_the_wakes_field_camera_is_halunas` fails on big17 (env-art, pre-existing).
- The Reach is dark at the default camera in the storm: lighting is the arena's (env-art-b).

## Files touched
game/data/ui/battle_sandbox.json (boss_seats), game/data/creatures/creatures.json (spar_wraith row),
tests/unit/test_creature_bosses_act1.gd, tests/unit/test_battle_boss_seat.gd,
docs/kb/tasks/M3/M3-CRB-011-boss-seat-at-the-home-camera-request.md, docs/kb/handoffs/live/creatures-b.md.
