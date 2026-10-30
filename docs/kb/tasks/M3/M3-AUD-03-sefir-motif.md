---
id: M3-AUD-03
title: Sefir's motif (first heard at the end of Ch6)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
High Warden Sefir Aurane's first appearance (Ch6): a white barge that leaves no wake; gentle, correct, terrible. The motif recurs through the game.

## Acceptance criteria
- [x] An original motif plus its first full statement (the barge, Ch6), with variants for later use documented; listening notes; cue rows.

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/music/sefir_theme.py`: the motif G4 C5 D5 E5 D5 C#5 (rises to D, slips to a held C# over F major) and its first statement, a 71 s loop in C major: congregation hum (the Order hums), a glass harmonica with no attack, the harmony drifting C→Ab→F, the congregation humming the motif, a cold F# over C at the end. Variants for later chapters (glass alone, hummed only, a 5/4 bell ostinato for his fight) documented in the docstring. −16.0 LUFS, −4.1 dBTP. Original material (see the docstring); byte-reproducible (render_all --determinism).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
