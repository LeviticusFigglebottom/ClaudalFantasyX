---
id: M4-A2P-092
title: "Boss stems for Malcor Venn and the Abiding guard, and the battle phase rows for all six bosses"
role: audio
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
Two stems each (Venn: the still water slows, then he boards; the guard: stem 2 is the storm waking), and the `battle.encounters` and `battle.phases` rows for the four creature bosses (`uprooted`, `opened`, `ram_rage`, `wakefin_breaching`) once their encounters exist.

## Acceptance criteria
- [ ] Sources, renders, rows; the phase rows match the encounters.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch14, Ch16.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- 2026-10-30 (audio): malcor_venn and abiding_guard rendered (2 stems each, 80 s, assets/audio/act2/music/); their cue rows name the intended phase rows. Still to do: the encounter and phase rows once combat adds the fights, `court_steps`, and the six boss-intro stings (keyed by encounter id).

## Review log
