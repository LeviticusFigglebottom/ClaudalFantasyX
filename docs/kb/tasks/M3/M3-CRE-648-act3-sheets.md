---
id: M3-CRE-648
title: "Act III design sheets: the Cage frame, the Lamp Spire's three, the Undertow layers' two"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "creatures (worktree agent)"
reviewer: lead
depends_on: [M3-CRE-646]
milestone: M3
request-from: creatures
---
## Goal
Write the design sheets for six of the Act III creatures proposed in docs/kb/art/creatures/act3_roster.md
(M3-CRE-646), each before its build, in docs/kb/art/creatures/act3/:
- `the_cage`: the Ch20 boss frame only. The four bound founders' figures are the characters track's; the sheet seats
  them and gives their bones and cues.
- `wick_crawler`, `chain_lamp` and `spire_moth` (a flue moth variant): Ch19, the Iskarra Lamp Spire.
- `held_shoal` and `drowned_lantern`: Ch20, the Undertow layers, in held light.

## Acceptance criteria
- [x] Six sheets on the README rules. Each covers what it is, silhouette and size against the battle camera and the
  enemy marks, colour by palette swatch, the weak point (ADR 0151), clips with lengths and contact seconds (hits peak
  at 0.10 s), rig, triangle budget, grounding or hover, and open questions for Combat and the chapter designer.
- [x] The held-light pair moves only sideways or down (color_script.md rule 1), built as skinned geometry, not
  particles (as Nhoa). Each sheet names a build check for it.
- [x] The constructs' bound light stays steady (rule 2). The chain lamp's beat is its louvres, not its light.
- [x] act3_roster.md has a "Sheets" line.
- [ ] The Lead reviews. The chapter designer and Combat answer the open questions; then builds in the roster's order.

## Notes
- Docs only. Gates: `validate_data.py`, `taskboard.py --check`, a banned-terms scan of the new files. No Godot run and
  no tools tests (no code or tools touched).
- The Cage is proposed as **one combatant** with phases at 75/50/25% and the KO breaking the last quarter. The board
  has three enemy marks, so four founders plus a frame cannot each stand on one.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
