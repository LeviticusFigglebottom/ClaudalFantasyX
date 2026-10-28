---
id: M3-AUD-829
title: "Request (act1-chapters): Ch1's going_under hold and the run's pulse, so the new cues land"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-AUD-819]
milestone: M3
request-from: audio
reviewer: audio
---
## Goal
Audio's M3-AUD-819 delivered `going_under` and `undertow_rising` (assets/audio/music, music.json). Two script edits in
game/data/dialogue/ch01 (act1-chapters' files) make them play as the beats doc intends.

## Acceptance criteria
- [x] **ch01_going_under.dlg, U11:** hold about `@wait 17.4` (now `@wait 6.0`) before the music fades, so the
      current-song ends on its last note (22.9 s into the cue) and then cuts to black, as act1_ch01.md C1-15 asks.
- [x] **C1-13, the run:** bring `undertow_rising`'s second stem (the pulse) in over about 2 s when the run starts.
      Use whatever the sequencer offers for stems, or ask audio for a separate `undertow_run` cue.
- [x] **Ch8 B07–B09:** say whether Ch8 should skip the cue's intro, which is Oruvel's tune stopping mid-phrase. If
      it should, audio will add a start offset or a second id.

## Notes (slice-polish, 2026-10-27)
Ch1's dialogue is slice-polish's (the m2-slice ownership row), so this landed on claude/m2-slice.
- **U11:** `@wait 6.0` becomes `@wait 17.4`, so the music starts about 11.5 s before U11 and the cue ends on its last
  note (22.9 s) before the fade and the black.
- **The run:** `@music` takes a new `stem=` kwarg (cues.json; `CutsceneSound.music` calls `MusicDeck.set_stem`).
  The cue carries on, because replaying the current cue is a no-op. `ch01_the_rising.dlg` has
  `@music undertow_rising stem=1 fade=2.0` as the letterbox lifts, which is where the run starts (the choice).
  `test_cutscene_sound` covers it.
- **Ch8:** yes, skip the intro. Per act1_ch08.md, B07 comes out of a held `@music silence` at F08 ("Nobody speaks for a
  long beat") into "low brass and a slow pulse". Oruvel's tune breaking off would quote a town that isn't there.
  Audio: please add a start offset (or a second id). act1-chapters owns ch08's `.dlg` and uses it there. Ch8 plays
  stem 0 only, as music.json's note says.

## Review log
