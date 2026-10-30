---
id: M3-AUD-10
title: Ch1 Oruvel raft-town theme and the Ch4 living funeral
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-03]
milestone: M3
request-from: lead
---
## Goal
Ch1: Oruvel, a raft-town of divers and salvage, the community about to die (Rhen haggles and jokes). Ch4: Haluna holds Asha's living funeral; Rhen leaves the feast angry.

## Acceptance criteria
- [x] Oruvel: an original town loop (a different town from Haluna: rafts, rope, trade, jokes). The living funeral: a through-composed or looping cue (a feast that is a funeral). −16 LUFS, cue rows, listening notes.

## Notes
- Done in a worktree agent (claude/audio). Both are seamless loops (LoopMixer), −16 LUFS, with tags, sidecars,
  render_all jobs and `M2_CUES` entries, `music.json` cues (`resume: true`, no zone rows), `LOOPING_CUES`,
  PROVENANCE rows, synced `.import` files, and the listening notes in "M3: Oruvel, the living funeral, the causeway
  beds". `--determinism`: identical.
- `music/oruvel.ogg` (`assets_src/music/oruvel.py`), a 73.8 s loop: G mixolydian, 4/4 swung at 104 BPM. A new
  synthesized free-reed squeezebox carries the tune: two reeds a few cents apart, with brightness that follows the
  bellows pressure. Under it are its own oom-pah left hand, a salvage cittern (paired wire courses) and a
  block-and-tackle knock, plus a frame drum, claps, a rope creak and a ship's bell. Form: intro, A, A′, an E minor B
  (the town looks away), and a cittern tag. It has no flute and no bars, and it lands home, unlike Haluna. Levels vs
  the tune (measured): left hand −7, bass −10, cittern chop −10, tag −2, drum −9, block −11, claps −13, bell −12,
  rope −18. Decoded −16.03 LUFS, TP −1.96 dBTP, 0.79 MiB (q3). The limiter takes up to 3.1 dB on 0.15 % of samples.
  Seam flux ×1.75.
- `music/pilgrims_wake.ogg` (`assets_src/music/pilgrims_wake.py`), an 83.5 s loop: a feast and a funeral at two
  tempos. The funeral is a C minor hymn in half notes over a descending ground (Cm Bb Ab G | Fm Cm/Eb Dø G7), played
  by the grand piano with a constant pedal (so its body is time-invariant in the loop), then hummed by the village,
  with a dark funeral bell once a round. The feast is a 3+3+2 harp and frame-drum dance in sixteenths, with claps and
  jingles. Round 3 thins and leaves two bare bars. Levels vs the hymn (piano top voice and hum both 0 LU): piano
  ground −4, harp −7, drums −7, claps −12, bell −11, gongs −14. Here the piano's raw level is about 20 dB under the
  hum. The file starts a sixteenth early (`downbeat_offset_s`), because with the downbeat on the seam the flux was
  ×4.66, against ×0.13 now. Decoded −16.03 LUFS, TP −1.78 dBTP, 0.87 MiB (q3.5). The limiter takes up to 2.9 dB on
  0.6 % of samples.
- **The budget:** these cues and the M2-AUD-13 beds take all shipped audio to about 24.7 MiB, so
  `tools/audio/targets.py` `TOTAL_BUDGET` goes from 24 to 32 MiB (in its own commit, with a mix.md §7 note). The Lead
  should reconcile this with the parallel boss-cue workers, who will hit the same line.
- Not done: a stinger for Rhen leaving the feast angry. The cue doesn't play his anger; if the scene wants one, it is
  a separate cue.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
