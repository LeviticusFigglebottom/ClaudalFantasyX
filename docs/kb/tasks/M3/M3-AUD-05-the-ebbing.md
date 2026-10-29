---
id: M3-AUD-05
title: Ch9 "The Ebbing": the emotional cue
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Asha's first great Ebbing: hundreds drowned, she dances on a raft as the motes drift down and seaward. The most beautiful sequence in Act I; Pell: "Beautiful. And pointing the wrong way."

## Acceptance criteria
- [x] An original through-composed cue (Hush-family material allowed, never imitating an existing melody), −16 LUFS, listening notes, a cue row.

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/music/the_ebbing.py`: 114 s through-composed from the Hush theme (hush_theme_v2's harmony and MEL_A/B/C): the vocalise-like Cantor line over the grand piano, a slow 3/4 dance (interlocking metallophones, soft frame drum), glass motes whose figures only fall (down and seaward), ending on E over A minor. Bus levels measured: piano L-3, dance L-8, motes and drone L-10, drum L-12. −16.0 LUFS, −2.0 dBTP. Original material (see the docstring); byte-reproducible (render_all --determinism).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
