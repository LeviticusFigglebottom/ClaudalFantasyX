---
id: M4-A2P-060
title: "Act II battle VFX in effects.json: every new skill, boss and set piece"
role: combat
status: doing
owner_session: claude/battle-presentation (session_01UPFyEA8QkJULH74MGgnMvJ; ADR 0205: Act II starts for battle-presentation)
depends_on: [M4-A2P-058]
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
A generator `tools/vfx/gen_act2_ability_vfx.py` (as Act I's) for every Act II skill and the people bosses, plus the intros for Malcor Venn and the Abiding guard and the boss-intro shots M3-BPR-408/418 wait on.

## Acceptance criteria
- [ ] Entries generated; `BattleVfx.prebuild` covers them; shots viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.4, §4.6.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
