---
id: M5-A3P-1808
title: "Ch18: gulls riding the Kite's wake (Act I's gull kind, a flock with a moving, parent-relative centre)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207 (the human's directive, 2026-10-30): Act III production in the creatures lane, from the Act III bestiary
(docs/kb/art/creatures/act3_roster.md, "Reconciled with the Act III beat sheets"). `kite_gulls`: no new mesh: the gull kind in a
flock row whose centre rides a moving parent (the Kite), validated, tested and shot.

## Acceptance criteria
- [x] WildlifeGullFlock with a parent-relative centre, a wildlife row for the Kite.
- [x] Tests (tools test_wildlife; Godot wildlife) and a review shot.

## Review log
- 2026-10-30 creatures: WildlifeGullFlock `follow` (a parent-relative frame set by the layer each step), the Kite's row on review stage kite_gulls.json (the Kite has no zone yet), validator support, tools test_wildlife OK, Godot wildlife 29/0, shot `wildlife_kite_gulls` viewed (birds on the stern rail and wheeling astern). docs/kb/art/wildlife.md "The Kite's gulls".
