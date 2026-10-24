---
id: M2-AUD-01
title: Shell Shrine trial audio: the interior cue and the puzzle's sounds
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-FP-16]
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track. The trial (M2-FP-16) has no sound yet. The beat sheet's music cue for B07 is `shell_shrine_interior` (today the sequencer's stand-in is `temple_trial`), and the puzzle needs diegetic feedback (pillar 4: you hear the water go where you sent it).

## Acceptance criteria
- [x] The `shell_shrine_interior` cue (original; the "temple trial ambience" of SPEC's score list), looping under the trial.
- [x] SFX on the trial's signals (`ShellShrineTrial`: `rotated`, `flow_changed`, `side_pool_drained`, `pool_filled`; `ShellShrineLevel.charm_taken`): a stone grind for a basin turn, the water's new route (a pour into a basin, a spill onto a grate, the inner pool filling), the side pool emptying, the door's shell valve sinking, and a small glint for the charm.
- [x] Wired by a listener node, as with the boss VFX hooks (battle_ctb.md). The rules are never touched.

## Notes
- 2026-10-24 audio (claude/audio): delivered.
  - **Cue:** `assets_src/music/shell_shrine_interior.py` -> `assets/audio/music/shell_shrine_interior.ogg`, a 72 s seamless loop in G
    pentatonic (warmer than the M1 temple cue's D minor): a breathing G/D drone, drips whose Minnaert bubbles are
    tuned to the scale (r = 3.26 / f) and ring the shell basins at the same pitch, a far congregation hum (an original
    line; women a fourth above for 30 s), two low breath-horn phrases, two soft kettle gongs. Decoded: −16.0 LUFS,
    −3.3 dBTP, 0 % limited, 0.68 MiB (q 3). Loop tags + sidecar + import synced; `test_audio_loops.gd` covers it.
    music.json's `shell_shrine_interior` now names it (the temple cue stays as `temple_trial`, for A/B).
  - **Puzzle SFX:** `assets_src/sfx/shrine_sfx.py` -> `assets/audio/sfx/shrine/`: stone_turn ×3 (stick-slip grind
    over the 1.2 s turn, a seating knock), pour (the inner pool), spill (a grate), drain (the sluice), side_drain
    (3 s, quickening gurgles, the last suck), door (the shell valve: deep grind, rush, low boom), charm (two tiny
    bars), and `shrine_pool_fill` (a 6 s stereo loop, −24 LUFS). One-shots at −18 LUFS momentary max (mix.md world
    SFX), 0.30 MiB together. `render_all.py --only shrine --determinism`: every file identical.
  - **Wiring:** `game/audio/shrine_audio.gd` (`ShrineAudio`), built by the Audio autoload (ADR 0031) when the level
    enters the tree; data `game/data/audio/shrine_sfx.json` (events) + `sfx_shrine.json` (rows). Positional
    (AudioStreamPlayer3D on the World bus) at the trial's layout points: the turned basin, the path's end (pool,
    sluice, or the last basin's lip for a spill), the door, the side pool. The fill bed runs while the water reaches
    the pool and fades when it's full. Never touches the rules.
  - **Tests:** `tests/integration/test_shrine_audio.gd` (4) on the real level; `--filter=shrine` 33/33 and
    `--filter=audio` 16/16 pass.
  - **For the human (§16 Q3):** listening notes in docs/kb/audio/listening_notes.md, "M2: Shell Shrine".

## Review log
