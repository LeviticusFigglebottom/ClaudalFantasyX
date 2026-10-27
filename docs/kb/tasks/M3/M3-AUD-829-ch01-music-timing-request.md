---
id: M3-AUD-829
title: "Request (act1-chapters): Ch1's going_under hold and the run's pulse, so the new cues land"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-AUD-819]
milestone: M3
request-from: audio
---
## Goal
Audio's M3-AUD-819 delivered `going_under` and `undertow_rising` (assets/audio/music, music.json). Two script edits in
game/data/dialogue/ch01 (act1-chapters' files) make them play as the beats doc intends.

## Acceptance criteria
- [ ] **ch01_going_under.dlg, U11:** hold about `@wait 17.4` (now `@wait 6.0`) before the music fades, so the
      current-song ends on its last note (22.9 s into the cue) and then cuts to black, as act1_ch01.md C1-15 asks.
- [ ] **C1-13, the run:** bring `undertow_rising`'s second stem (the pulse) in over about 2 s when the run starts.
      Use whatever the sequencer offers for stems, or ask audio for a separate `undertow_run` cue.
- [ ] **Ch8 B07–B09:** say whether Ch8 should skip the cue's intro, which is Oruvel's tune stopping mid-phrase. If
      it should, audio will add a start offset or a second id.

## Review log
