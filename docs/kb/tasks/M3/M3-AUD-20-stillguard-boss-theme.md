---
id: M3-AUD-20
title: Ch6 boss theme: the Stillguard Inquisitor and the raid-hound (the Order's own)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agent)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Ch6's boss is the first fight against the Order's people; Toma refuses to strike to kill. It needs a battle theme that is not a monster's.

## Acceptance criteria
- [x] An original battle loop at -16 LUFS, a music.json battle row for its encounter (pending until the encounter exists), loop tests, PROVENANCE.

## Notes
- `assets_src/music/stillguard_inquisitor.py` -> `assets/audio/music/stillguard_inquisitor.ogg` + `.loop.json`
  (+ `.ogg.import`, loop=true, loop_offset 4.615 s). A minor, 4/4 at 104 BPM, a march. 2-bar intro (a copy of bars
  31-32) + a 32-bar loop (73.85 s); 78.46 s in all, 0.89 MiB (q3.5). Form: 1-4 the line forms | 5-12 A, the edict
  (piano octaves) | 13-20 B, the people (the flute's lament, women's hum) | 21-24 the hound (running drill, Bb) |
  25-32 A'' (the edict an octave down, the flute's counterline), shield fill into the wrap.
- -16.05 LUFS integrated, -1.58 dBTP (decoded); limiter at most 0.2 dB on 2 % of samples. Seam: flux x0.64, jump
  x1.26; intro splice residual -71 dB. Every event sits a sixteenth late (`downbeat_offset_s` in the sidecar).
  `render_all.py --only stillguard_inquisitor --determinism`: identical.
- Bus balance from measured bus loudness (second render on plan): piano edict and flute 0 LU, drums -5, big drum -8,
  march -8, bass -7, shields -9, men's hum -9, women's hum -11, gong -14.
- Wiring: render_all JOBS row + M2_CUES; music.json cue `stillguard_inquisitor`; LOOPING_CUES. **No battle row:** no
  Stillguard or Inquisitor encounter exists in game/data/battle/encounters.json yet. The intended mapping is in the
  cue's `_note` (`battle.encounters stillguard_inquisitor -> stillguard_inquisitor`). Add it when the fight lands.
- Listening notes: docs/kb/audio/listening_notes.md, "the Ch6 boss".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
