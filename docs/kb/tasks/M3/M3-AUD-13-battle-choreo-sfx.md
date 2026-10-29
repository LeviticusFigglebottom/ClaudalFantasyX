---
id: M3-AUD-13
title: Battle SFX for the battle-presentation choreography (M2-BPR-01..08)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
claude/battle-presentation adds BattleChoreo (approach, strike, contact, recover, return beats), the boss and Vowbound choreographies, KO collapse and entries (docs/kb/tech/battle_presentation.md on that branch). BattleVfx already fires on `contact` there, so the M2-AUD-04 sounds follow the blow.

## Acceptance criteria
- [x] Contact hits per weapon/style, strike whooshes, approach/return footfalls on sand, the KO collapse, Swell finisher accents, the Drownbell's toll wave and flood beats, the Vowbound call, rise and fall.
- [x] Listen-only hooks keyed by class and signal names in data (they must load without the battle-presentation classes present on claude/audio), tests with stand-in nodes, PROVENANCE, loudness targets.

## Notes
- 2026-10-24 audio: done on claude/audio (worktree), not pushed. 55 sounds in `assets/audio/sfx/choreo/` from
  `assets_src/sfx/choreo_sfx.py` (render_all `--only choreo_sfx --determinism`: all identical): whooshes (melee,
  heavy, cast, throw, guard; -20 LUFS M max), weapon accents (Rhen's hooks + lantern glass, Asha's staff, Toma's spear
  and shield, Ysolde's book and focus, Kerrid's anchor-cleaver, claws, teeth, the bell's hood; -21, a layer under the
  -18 hit), sand footfalls (4, -21), KO collapse (2, -18), Swell accents (4, -19), toll wave, flood surge (-18), flood
  brace (2, -21), Vowbound beckon (-19), rise, rise_long, fall (-18), sink (-20). Rows in `sfx_choreo.json`
  (Combat), rules in targets.py, PROVENANCE rows.
- Hook: `game/data/audio/choreo_sfx.json` + `game/audio/choreo_audio.gd`; the director attaches it when a node whose
  script's global class name is `BattleChoreo` enters the tree (two lines in `_on_node_added`). Signals by name:
  `beat(kind, actor_id)`, `contact(result)`; methods `current`, `style_id_for`, `entering`, `leaving`, `animating`,
  `after_sequence`, property `speed`. BattleBossChoreo / BattleVowboundChoreo are RefCounted (never enter the
  tree), so the call / departure / Flood come from the engine and the rise / sink / fall / step-off / walk-in from
  BattleChoreo.entering / leaving. Docs: audio_runtime.md "Choreography layers"; listening_notes.md.
- The hook row is `pending` until the class merges; validate_data then checks its signals (simulated against
  origin/claude/battle-presentation's choreo.json and signal list: clean, all 13 styles covered).
- Gates: validate_data, taskboard --check, gdlint/gdformat, test_audio_data.py (31), godot --filter=audio (67, incl.
  15 in test_choreo_audio.gd), loudness test.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
