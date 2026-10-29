---
id: M3-CRE-700
title: "Request: Virel, the Fire Vowbound, as a field body in Coilspire's gallery (the last greybox block on Ch8's path)"
role: character
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
depends_on: [M3-C08-1210]
milestone: M3
reviewer: character
request-from: cinematics
---
## Goal
ADR 0041 (Act I at final quality): Coilspire's gallery still draws Virel, the Fire Vowbound the party binds at the top of
the spire (act1_ch08.md, the binding), as the greybox block `Virel` (2 x 6 x 2 m, glowing, at the gallery's centre;
`game/levels/ch08/coilspire/coilspire_layout.json`). Everything else in the zone is kit dressing now (f90e3df1). For
creatures-b (the Act I bosses and the Vowbound, CONSOLIDATED 2-FOCUS).

## Acceptance criteria
- [x] A Virel model with an idle (and the binding's clips the Ch8 beat sheet names), registered in
      `game/data/creatures/creatures.json` with its PROVENANCE rows.
- [x] act1-chapters casts it on the block's spot (`ZoneCast` `creature:<id>`, or a dressing piece following the
      `Virel` block so the story's show/hide still drives it) and drops `Virel` from `greybox.keep` in
      `tools/act1/ch08_coilspire_dressing.py`.

## Review log
- 2026-10-29 act1-chapters: the model is creatures' (M3-CRE-641, `game/creatures/virel/virel_battle.tscn`, in
  creatures.json). Cast on the `virel` actor at `virel_coil` (`creature:virel`, `cast_still`: held on her idle's first
  frame, no breathing, as F07's "perfectly still"); `Virel` dropped from greybox.keep; she turns side-on to F07 and is
  seen only there (off stage under the fade, hidden with `ch08_virel_bound`). Commits ed235044, 46c9811b; viewed in
  the stills. For character's review: is the battle form (glimmer_bound seams) the right one for the binding's frame,
  or should the field use `virel_held` (glimmer_held)? The beat sheet says the seams read as steady glimmer_bound.
  Renamed from M3-CRE-627 (it shared that id with the Act II regulars file; the Lead, 2026-10-29).
