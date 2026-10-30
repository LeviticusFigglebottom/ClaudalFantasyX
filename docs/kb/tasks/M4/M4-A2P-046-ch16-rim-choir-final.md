---
id: M4-A2P-046
title: "The Pale Rim and the Drowned Choir at final quality (a hero zone)"
role: environment
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
The white shallows, cairns and the waiting ship; the Choir's ring of colossal mouths at moonrise, with bespoke hero meshes (SPEC §7.4). Get `battle_arena_drowned_choir_ring` its first approved render.

## Acceptance criteria
- [ ] As M4-A2P-040, for Ch16.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch16.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- 2026-10-30 chapters (act1-chapters): **a regular-fight arena is missing.** the Rim's shallows (`ch16_rim_skates`, `ch16_rim_crawlers`) have no arena, so they would fight on
  the sandbox's stage. Please add `pale_rim_shallows` (arenas.json) with this zone's kit. chapters then names it on the rows and
  drops them from `ACT2_NO_ARENA_YET` in `tests/integration/test_act1_encounters_resolve.gd` (docs/kb/plan/act2/chapters).

## Review log
