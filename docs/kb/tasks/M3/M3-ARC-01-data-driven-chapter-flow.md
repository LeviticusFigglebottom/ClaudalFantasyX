---
id: M3-ARC-01
title: Data-driven chapter flow for Act I (generalise HalunaStory and first_playable.json; ADR 0033)
role: architect
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: lead
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). The slice's flow is bespoke: `HalunaStory` and `FirstVerseScene` read hand-named sections of `first_playable.json`. Act I adds six chapters, each with several zones, and they need one shared way to say:
- what plays on arrival, by flag;
- which triggers start which dialogue, battle or scene;
- where a battle returns to;
- how a chapter hands off to the next.

All of it in data, validated, and headless-testable. The slice must keep working unchanged: the Haluna and shrine tests pass, and its shots don't move.

## Acceptance criteria
- [ ] ADR 0033 records the design.
- [ ] A chapter registry and a per-zone story schema under `game/data/flow/`, checked by `validate_data` (flags declared, dialogue ids exist, scenes and spawns exist).
- [ ] A reusable `ZoneStory` node that plays a zone's story from that data, with arrival beats, triggers, battles with victory and escape returns, hand-offs through `FlowRouting`, and night or variant hooks.
- [ ] A test chapter with two zones drives it end to end in an integration test.
- [ ] The prologue's hand-off goes through the registry (to Ch1 once M3-C01-02 lands; until then it stays on Haluna).
- [ ] The slice is unchanged: `test_fp_thread` and the Haluna tests pass.

## Notes

## Review log
