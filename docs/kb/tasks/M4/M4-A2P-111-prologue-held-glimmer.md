---
id: M4-A2P-111
title: "The Prologue's motes drift, never rise: switch prologue_dead_city's glimmer_lift to glimmer_held and re-baseline its shot"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
The Lead accepted act3_threads T-07 on 2026-10-30. The Prologue's vigil is Ch19's dusk, and nothing is released before
H09, so the motes around Rhen are held: they drift sideways and seaward and never rise. act_outline's Prologue line is
updated. The script still has `@vfx glimmer_lift at=by_asha count=12`
(`game/data/dialogue/prologue/prologue_dead_city.dlg`, after `prologue_dead_city_001`), and its header comment says
"glimmer rises around him".

## Acceptance criteria
- [ ] The cue becomes `@vfx glimmer_held at=by_asha count=12` (it sinks seaward by default; add a sideways drift if
      the cue vocabulary gains one). The header comment is updated to match.
- [ ] `HYMN_SHOTS=slice_prologue_vigil_line` is re-rendered and its baseline updated if the motes show in frame.
- [ ] Godot `--filter=cutscene` and `fp_prologue` green; dlgc --check clean.

## Notes
Narrative didn't change the cue itself, because the change moves a rendered baseline that is Cinematics' to own.

## Review log
