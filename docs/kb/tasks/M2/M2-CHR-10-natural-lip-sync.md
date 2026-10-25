---
id: M2-CHR-10
title: Natural text-driven lip sync for cutscene faces (graphemes, co-articulation, reveal timing)
role: character
status: review
owner_session: "character lip-sync worktree (agent-a7e15e97d1022d9ca, session_019iimsngAgPLEram1wcbLpE)"
depends_on: [M2-FP-18]
milestone: M2
request-from: lead
reviewer: lead
---
## Goal
The human's note: the characters' mouthing of their lines in cutscenes looks unnatural. M2-FP-18's flap snapped one vowel shape open on every vowel and shut after it. At the box's 40 characters a second that is a chatter of hard open/close pops, with `vis_aa` 0.55 plus an extra `jaw_open` 0.18 (about 0.45 of the jaw's range) on every syllable. Replace it with a natural approach. There is no voice (no TTS or audio generation, SPEC §16 Q5).

## Acceptance criteria
- [x] Grapheme-to-viseme pass with English digraphs (th, sh, ch, ph, ee, oo, ou, ...), silent letters, and word-start and word-end rules, onto the rig's 10 visemes (`FaceVisemes.segments`).
- [x] Co-articulation: neighbouring visemes blend by dominance, with separate anticipation and carry-over spreads. Bilabials p/b/m (and f/v) always close the lips, lip rounding is anticipated before o/u, nothing snaps per letter, and the jaw's speed is capped per shape (`LipSync`).
- [x] Timing locked to the DialogueBox reveal (its own `chars_per_sec`). Punctuation closes the mouth to rest, the line's end returns to rest smoothly, and a skipped reveal releases at a capped rate.
- [x] Intensity follows the line's `[emotion]` tag, subtle by default; natural speech stays well inside the extremes. A small asymmetric idle drift runs while a line plays.
- [x] Every curve constant is in data: `game/data/cutscene/lipsync.json` (sequencer.json's `visemes` block is gone).
- [x] Tests: grapheme mapping, bilabial closure, punctuation rest, the per-frame cap, emotion intensity, idle, timing against a reveal speed and against a real DialogueBox, plus the rig and the sequencer.
- [x] Frame strips of Asha's lines rendered on lavapipe, viewed, and the constants iterated.

## Notes (character, 2026-10-24)
- **Approach.** `FaceVisemes.segments(text)` gives viseme segments in character units. `LipSync.start(text, cps, emotion, seed)` blends them (a Cohen–Massaro-style dominance average plus a lip-closure pull) at 120 Hz, scales them by the emotion's intensity, and slew-limits each shape with a look-ahead limiter: every low point is reached on time, and the closure shapes are limited the other way round so they are never cut short. `CutsceneFace.say(text, cps, seed)`, `end_line(grace)`, and `emotion` (set by the sequencer's `_set_face`). The sequencer passes `overlay.box.settings.chars_per_sec`, releases the rig when the box stops revealing early, and passes cps 0 under `instant` and skip. Docs: `docs/kb/tech/cutscenes.md`, "Faces".
- **Constants** (lipsync.json, after three rounds on lavapipe):
  - **Shapes at intensity 1:** aa 0.6, e 0.5, i 0.48, o 0.55, u 0.58, mbp 0.6, fv 0.55, l 0.42, st 0.45. No extra `jaw_open`, because the vis_* shapes carry their own jaw.
  - **Intensity:** default 0.85, from exhausted 0.6 up to laugh and surprised 1.0.
  - **Dominance a / ahead / behind:** vowels 1.0 / 0.03 / 0.03 s; o 1.0 / 0.08 / 0.04; u 1.2 / 0.09 / 0.04; mbp 2.5 / 0.02 / 0.015; fv 2.0 / 0.02 / 0.015; l and st 0.8 / 0.02 / 0.02; rest 4.0 / 0.03 / 0.03. base_rest is 0.15.
  - **Closures:** mbp 1.0 and fv 0.7, with closure_tau 0.012 s.
  - **Caps:** 6/s (mbp 9, fv 7), so `vis_aa` changes by at most 0.1 per 60 fps frame.
  - **Ends:** tail_s 0.3, release_per_s 2.0.
  - **Idle:** dimple_L 0.05 @ 0.41 Hz, stretch_R 0.04 @ 0.29, lip_lower_down 0.04 @ 0.53, press 0.03 @ 0.23, faded in and out over 0.25 s.
- **Frames viewed** (lavapipe, `asha_stage.tscn` `Cameras/Face`, driven through CutsceneFace + LipSync at 40 cps). All are crops of the mouth.
  - **Round 1** (ch02_beach_002 "There you are. No, don't sit up yet. You've swallowed half the bay.", soft_smile; every 4th frame): far too subtle. Jaw peaks were about 0.05, so it read as a murmur.
  - **Round 2** (higher rows and caps; every 2nd frame): the mouth visibly shaped the words, but the p of "up" and the b of "bay" stayed parted with teeth showing.
  - **Round 3** (the closure pull and peak-preserving limiter; every 2nd frame, 60 frames): the lips meet on "up" and "bay" and tuck for the v of "You've" and the f of "half". Openings on "are", "swallowed" and "half" are modest and vary by vowel, transitions are smooth with no per-letter pops, and the mouth eases to the soft_smile rest within tail_s (0.3 s) of the last character.
  - **Sad line** (ch02_beach_020 "Some of them came in with you. I heard them on the water.", every 3rd frame): smaller openings, closures on the m's, and a rest at the full stop.
  - Judged against the human's note, the mouth reads as quiet, natural speech, not flapping. Strips are not committed. They come from a scratch driver (CutsceneFace on the stage's Asha) in the session's scratchpad.
- **No baseline moves.** No screenshot in `tests/screenshots/shots.json` plays a line: `asha_face_*` are static poses from AshaStage, which never builds a CutsceneFace. So no face_* baseline was re-approved, and no shot gate was run.
- **Ownership.** `game/cutscene/**` is m2-slice's (M2-FP-18). This task edits `cutscene_face.gd`, `cutscene_sequencer.gd` (only the `_line` lip-sync call, `_set_face` setting `rig.emotion`, `_face_of` passing lipsync.json, and `advance` releasing on a skip) and `face_visemes.gd` (rewritten), and it adds `lip_sync.gd`. It removes sequencer.json's `visemes` block and adds `game/data/cutscene/lipsync.json`. The Lead asked for these edits for this task. The face rigs are the characters track's. No rig, shape key or Blender source changed: lip sync only drives Asha's existing `vis_*` shapes (asha.md §6.2), stays within §6.2's 0.6 cap, and drives four existing expression shapes for the idle. `game/ui/dialogue/` (UI) is untouched: the reveal speed is read from `box.settings`.
- **Known limit.** The box reveals at 40 characters a second, about 2.7 times a speaking pace, and the mouth is locked to it. So syllables are short, and the speed cap keeps their openings modest. At the player's slower settings (min 5 cps) the same curves open fully to the rows. The reveal itself has no punctuation pauses (UI's file), so a comma's rest lasts as long as the comma and the spaces after it reveal. If UI ever adds reveal pauses, the timeline should take them from the box (one function: char index → time).

## Notes (ui, 2026-10-24): timing follows the reveal's punctuation pauses (M2-UI-27)
- `LipSync.start(text, cps, emotion, seed, reveal_times)` and `CutsceneFace.say(..., reveal_times)` take the box's `DialogueBox.reveal_times()`.
  - `LipSync.starts_for` maps each character position to the moment it starts speaking: the 1 / cps before the box shows it. Inside a character it runs at 1 / cps (`_at`), so the pause the reveal holds after a mark lies outside every segment that ends there, and the mouth relaxes to rest.
  - The speech end is the last reveal.
  - With no reveal times it is x / cps, exactly as before.
- `CutsceneSequencer._line` passes `overlay.box.reveal_times()`. This is a UI edit in `game/cutscene/` (m2-slice's), assigned by the Lead.
- **Test:** `test_lip_sync.gd::test_the_mouth_rests_while_the_reveal_lingers_at_a_comma`. "Mama, wait." with the box's real timing: the mouth opens on "Mama", is under 35% of that mid-pause, and ends with the box.

## Review log
