---
id: M3-AUD-16
title: Act I zone ambience beds: the Tidecup (Tamsule Bell), Brine Shoals, Terraces of Ash, the Seawall
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
env-art's M3 kits are merged on claude/env-art and claude/m2-slice; their zones need beds.

## Acceptance criteria
- [x] Seamless −26 LUFS beds per zone (crowd-less Bell interior, shoal mud and smoke, terrace channels and lantern boats, the seawall's wind and waves), ambience.json rows and zone entries for scenes that exist.

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/sfx/act1_ambience.py` (built on field_ambience.py's periodic blocks):
  tamsule_port, tamsule_bell, brine_shoals, pemakar_terraces, ashcrown, corrow_seawall; 40–46 s seamless loops at
  −26.0 LUFS, q1, 2.32 MiB together (its own 3.0 MiB budget in render_all). Each bed's layers set from measured bus
  loudness (plans commented in GAINS). `render_all --only act1_ambience --determinism`: identical.
- ambience.json rows for all six; zone entries for the four scenes on claude/m2-slice (Tamsule, the Bell galleries,
  Pemakar, Ashcrown) marked `"pending": true` (data_check skips the scene-exists check for them; they go live when the
  scenes merge). Brine Shoals and Corrow have kit previews only (claude/env-art): their zone entries wait for the
  zone scenes.
- Known: `tamsule_bell`'s wrap has a small decoded step from the Vorbis encoder (float seam clean; spectral flux 0.98x,
  under the gate); flagged in listening_notes.md.
- Also fixed: render_all's music loudness check matched ambience beds by name prefix (tamsule, corrow_seawall,
  brine_shoals); it now applies to music files only.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
