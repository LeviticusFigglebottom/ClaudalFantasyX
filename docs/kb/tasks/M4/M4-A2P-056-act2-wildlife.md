---
id: M4-A2P-056
title: "Act II wildlife for the new zones"
role: character
status: review
blocked-by: ""
owner_session: claude/creatures
depends_on: []
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
Ambient wildlife (never foes): fen birds and fireflies (Ch10), highland goats or woolbacks (Ch12), rays in the white shallows (Ch16). Ansedra (Ch13–14) has none, by design: "no seabirds" (bible §5.8, ADR 0204 §1). Design sheets: docs/kb/plan/act2/creatures/ (fen_kingfisher, fen_firefly, woolback, rim_ray).

## Acceptance criteria
- [x] Wildlife rows and actors (fireflies, kingfishers, woolbacks, rim rays); placed on the greybox layouts (re-seat with the dressing).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- ADR 0204 §1: Ansedra has **no** wildlife (no seabirds, bible §5.8); the Ch13 row is dropped.
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30, the creatures track (ADR 0205: Act II starts per track; the claim is the Lead's to record on the integration branch): **the fen fireflies are built and placed** (ch10_ossa_fen.json; plan sheet fen_firefly.md, State). **The fen kingfishers are built and placed** (plan sheet fen_kingfisher.md, State). **The woolback herds are built and placed** (plan sheet woolback.md, State). **The rim rays are built and placed** (rim_ray.md, State). All four are built and placed on the greybox; what's left is to re-seat them on the dressed kits (and to move the woolbacks to the Keth troughs) when env-art's kits replace the blocks.

- 2026-10-30 (the Lead, 09:58: build Ch13+ ambient life from the beat sheets): Ch13–14 Ansedra has none (bible §5.8, ADR 0204 §1), and the Ch15 open sea has only the Wakefin and the sea-glow (the sheets). Hollowmere (`ch17/hollowmere`, first visited in Ch15) gets Act I's gulls on the dock piles and a fish shoal, as the flotilla where life comes back after Ansedra (game/data/world/wildlife/ch17_hollowmere.json; shot `wildlife_zone_hollowmere_dock`, viewed). The Ch16 rays are above. Kesh, Ch16's Vowbound, belongs to creatures-b (ownership.md).

## Review log
