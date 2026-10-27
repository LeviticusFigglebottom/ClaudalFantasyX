---
id: M3-AUD-830
title: "Request (act1-chapters): Ch5's doubled thunder and the inn gate's festival, for the new cues"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-AUD-821]
milestone: M3
request-from: audio
---
## Acceptance criteria
- [ ] **ch05_kahre.dlg:** remove the `@sfx plume_thunder` after ch05_kahre_017. `hush_second_verse` carries its own
      thunder on *mir* (32.59 s into the cue), so the line doubles it. Time the plume flash to 31.54 s.
- [ ] **ch05_inn_gate.dlg** replays `lanternfall` from the start, so the "distant" festival plays at full size. Say
      whether a far variant is wanted (audio can make `lanternfall_far`), or play it at a lower `vol=`.

## Review log
