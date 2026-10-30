---
id: M4-A2P-018
title: "Move the Act II greybox and flow generators from tools/act1/ to tools/act2/"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-C14-02]
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
`tools/act1/ch10_greybox.py` … `ch15_16_greybox.py` are Act II's. Move them with `git mv` in one commit, fix the imports and every path that names them (tests, docs, ownership), so Act I's tools stay Act I's.

## Acceptance criteria
- [ ] One commit; validate_data, the tools tests and the ch1x thread tests green.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). act2_tracks.md §5 item 1.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log
