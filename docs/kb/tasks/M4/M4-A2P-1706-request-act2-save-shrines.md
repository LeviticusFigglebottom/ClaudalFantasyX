---
id: M4-A2P-1706
title: "Request (ui-menus): place the Act II save shrines (Reedhollow, Lowlight, Quellan, Ansedra); Ch10-Ch13 can't be saved in"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: ui
milestone: M4
request-from: ui
---
## Goal
The Act II save pass (ui-menus, M4-A2P-1707, the Lead's 2026-10-30 ask) found no save shrine or rest point in any
mounted Ch10-Ch13 zone. The player can only autosave there, at a chapter's start; nothing lets them save between.
The plan names one shrine per hub (docs/kb/plan/act2/act2_text_ids.md, "Save-shrine flavour"): `ch10_shrine_reedhollow`,
`ch11_shrine_lowlight`, `ch12_shrine_quellan` and `ch13_shrine_ansedra` (and `ch15_shrine_hollowmere` later). Their
flavour dialogue is done. Act II's shrine rows are the chapters' (same file).

## Ask
For each of Reedhollow, Lowlight, Quellan and Ansedra:
- Place a SaveShrine (or a layout `save_shrine` trigger) in the zone, with a respawn spawn within 8 m.
- Add its row to locations.json `shrines`.
- Ansedra's is an Order shrine: `order: true` (ui/heresy.md; dark after `ch14_declared_heretics`).

## Acceptance criteria
- [ ] test_qa_save_shrines covers them (it walks every zone's shrines) and passes.
- [ ] ui-menus' Continue sweep (test_continue_every_act1_zone, its Act II case) stays green.

## Review log
