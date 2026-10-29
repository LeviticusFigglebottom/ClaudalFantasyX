---
id: M3-AUD-14
title: Creature voices and movement SFX (reef crab, lantern eel, gull harrier, spawn polyp, the Drownbell, the Act I bestiary)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
The creatures track (claude/creatures) models the slice's foes and the Act I bestiary. Each needs a voice (idle, hurt, attack, death) and movement (skitter, slither, wingbeats).

## Acceptance criteria
- [x] A per-creature voice table (data) and synthesized sets; hooks to the creature models' clip/phase signals listen-only by name; tests; PROVENANCE; loudness targets.

## Notes
- **Sounds:** `assets_src/sfx/creature_sfx.py` renders 194 files to `assets/audio/sfx/creatures/`. 23 creatures have
  their own set: the slice's five, with idle 1, attack 2, hurt 3, death 1 and move 3, and 18 Act I foes, with idle 1,
  attack 2, hurt 2, death 1 and move 2. The four palette variants (wreck_crab, wallcrab, wall_polyp, stormgull) reuse
  their parent's set at another pitch.
  - Levels: voices −18 LUFS momentary, idles −20, movement −21. Decoded true peaks are all ≤ −1.48 dBTP.
  - The set is 3.0 MiB. `render_all.py --only creature_sfx --determinism` gives byte-identical files.
  - The sounds are physical and formant models, not recordings (listening_notes.md has a section on them).
- **Data:** the rows are in `game/data/audio/sfx_creatures.json` (115 rows, Combat bus), and
  `game/data/audio/creature_voices.json` maps each base id to its events. `tools/audio/data_check.py` has
  `creature_voice_errors`: every enemies.json enemy needs a row or `"silent"`, and the events, rows, pitch, clips and
  delays are checked. The targets.py rules are appended, specific before generic.
- **Runtime:** `game/audio/creature_audio.gd` (`CreatureAudio`) is a child of BattleAudio, which got one small
  `_attach_creatures` block. It only listens:
  - **attack** on the creature's own action_resolved;
  - **hurt** (once per kind per action) and **death** (a hit, or poison on turn_ended, once). Both play −3 dB and
    70/110 ms behind the hit and KO sounds, layered under them;
  - **idle** when the battle opens or creatures join;
  - **move** from the model's AnimationPlayer `animation_started`, found by script class name (`CreatureActor`,
    property `creature_id`) with has_signal guards, or with the attack while no model is heard.
- **Tests:** `tests/unit/test_creature_audio.gd` (8 tests) and `tools/tests/test_audio_data.py` (`CreatureVoiceDataTest`,
  4 tests). Gates run: validate_data, taskboard --check, gdlint and gdformat, test_audio_data, Godot
  `--filter=audio` (60/60) and `--filter=battle` (423/423), and the loudness test.
- **Once claude/creatures merges, verify:**
  - the CreatureActors enter under the BattleController, so they are found;
  - `models` counts them, and the move plays once per action, from the clip;
  - whether `delays_ms.attack` should follow `contact_time` if hits get timed to the contact.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
