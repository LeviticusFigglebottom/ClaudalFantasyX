---
id: M4-A2P-010
title: "Ch10 playable at final quality: story wired, Pell out of Reedhollow, the Drowner's encounter"
role: cinematics
status: doing
owner_session: "act1-chapters → chapters (claude/act1-chapters; ADR 0205)"
depends_on: [M4-C10-01, M4-C10-02, M4-C10-03, M4-A2P-001, M4-A2P-020, M4-A2P-040]
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
Wire Ch10 end to end on env-art's dressing: Ch9's act break hands off to Ch10; the scripts; Pell kept out of Reedhollow by `party` steps; the Mangrove Drowner's enemy row (`model` linked) and encounter on `ossa_fen_roots` with the staged ids (M3-BPR-419: phase `uprooted`); `model` keys on the three regulars' rows; music.json zone and phase rows; NPC and trigger placement; field cameras.

## Acceptance criteria
- [ ] A headless thread test New Game save → Ch10 end, zero SCRIPT ERRORs.
- [ ] The Drowner's boss suite in Act II's boss band (plan §4.7) on the Ch10 loadout (M4-A2P-019).
- [ ] `placeholder_audit.py --act 2` reports zero Ch10 items.
- [ ] The greybox for both zones is retired (M3-ENV-736's swap map).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10. Close M4-AUD-1001 if creature_voices.json's rows are confirmed (the inventory says they exist).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
