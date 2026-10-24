# Live log: audio (branch `claude/audio`)

Environment: cloud session `session_01FtDSYm5dJHkdC3RqXsDjif`, branch `claude/audio` (from the integration branch
`claude/undertow-lead-handoff-423ixt` at 1023a25). Role: Audio. The Lead reads this file; newest state first.

## State (2026-10-24, updated after M2-AUD-01)
- **Done (pushed):**
  - **M2-AUD-02 runtime** (review pending its last items): the `Audio` autoload (ADR 0031,
    docs/kb/tech/audio_runtime.md): buses from game/data/audio/mix.json, zone music/ambience on
    SceneRouter.scene_swapping, battle music via a listen-only BattleAudio (encounter cue, phase stems), SFX bank
    (sfx.json + per-domain sfx_<domain>.json), listen-only hooks for the cutscene sequencer, DialogueBox (blip ->
    Voice, dialogue duck), battles (ambience duck). `tools/audio/data_check.py` (called by validate_data) +
    tools/tests/test_audio_data.py (also runs tools/audio/tests). Full Godot suite with the autoload live: 1441/0.
  - **M2-AUD-01** -> review (reviewer qa): `shell_shrine_interior` cue (72 s loop, −16.0 LUFS) and the trial's puzzle
    SFX, wired by ShrineAudio. Listening notes added ("M2: Shell Shrine").
- **In progress:** two worktree agents: M2-AUD-04 battle SFX (+ reduced-audio setting) and M2-AUD-05 field
  ambience, footsteps, UI hooks. I merge them into `claude/audio` when they report.
- **Next (me):** M2-AUD-03, the three final cue families (haluna_village/night, battle v2 + drownbell stems, the
  Hush family: hush_first_verse, haluna_dawn, ilun_summon).
- **Request filed:** M2-AUD-07 (cinematics): the sequencer should call `Audio.play_music` / `play_sfx` (its own
  player is routed by listening meanwhile) and drop `music_volume_db` −8.
- **Lead, please note:** the `Audio` autoload line in project.godot (Systems-owned; ADR 0031) and the one
  `check_audio` call appended in tools/validate_data.py (own commit). render_all.py's total budget is now 16 MiB
  (the slice), documented in M2-AUD-06.

## Exact next step
Compose and render `haluna_village` (assets_src/music/haluna_village.py), then the battle and Hush families.

## Un-pushed state
None.
