---
id: M3-MNU-201
title: "Lattice page: the pseudo-loc walk fails after the overview button (M3-MNU-04) met M2-UI-28"
role: ui
status: todo
owner_session: ""
depends_on: [M3-MNU-04]
milestone: M3
request-from: ui
---
## Goal
With the big8 gate (claude/menus' M3-MNU-04 Lattice overview) merged into claude/ui (M2-UI-28's
pseudo-localisation walk), `tests/unit/test_pseudo_loc_screens.gd` `test_party_pages_fit` fails on
`lattice_menu` and `lattice_menu_activate`, at 100% and 130%:

```
lattice_menu @100%: overflows: @Control/@Label 345x41 needs (123, 88)-(468, 129),
its box is (741, 81)-(1116, 129): [Ţĥé Ļáţţîçé ····]
```

TextFitProbe measures the page's header label against a box at (741..1116, 81..129), which is where the
overview button's new `PanelSmall` frame sits (`lattice_menu.json` overview.button). Likely fix: the frame
or the header moves so the probe no longer pairs them, or the header gets its own panel. Not root-caused. Found while merging for M3-UI-01; not
touched there.

## Acceptance criteria
- [ ] `test_pseudo_loc_screens.gd` `test_party_pages_fit` passes with the overview button in place.
- [ ] `lattice_menu` / `lattice_menu_activate` / `lattice_overview` shots re-approved if they move.

## Review log
