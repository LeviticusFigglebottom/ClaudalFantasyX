---
id: M3-AUD-06
title: M3 SFX: Reefball, underwater ambience, diving
role: audio
status: done
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
reviewer: qa
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Reefball (SPEC §6.10; the suspended water sphere arena), the underwater world (M2-RND-02) and Rhen's dives need sound.

## Acceptance criteria
- [x] Reefball: ball strikes, the sphere's water (entry, swim, surface), crowd beds and reactions, the whistle, the naming rite.
- [x] Underwater ambience beds (−26 LUFS loops) and diving SFX (entry splash, surfacing, lantern under water, breath).
- [x] sfx_<domain>.json rows, PROVENANCE, loudness targets, tests.

## Notes
- 2026-10-24 audio (worktree agent): built.
  - **Sources:** `assets_src/sfx/reefball_sfx.py` and `assets_src/sfx/underwater_sfx.py`. Everything is synthesized
    in-repo from noise, oscillators and physical models: Minnaert bubbles, stick-slip creaks, formant voices, a
    tower bell and a kettle gong. There are no samples. Each file's docstring describes every sound. Both are
    registered in `render_all.py` JOBS as the new kind `sfx_set` (one-shots and loops in one job: a file listed
    with a `.loop.json` is checked as a loop, and a mono file is measured as mono). `--determinism` gives
    identical bytes for every output.
  - **Reefball** (`assets/audio/sfx/reefball/`, 25 .ogg + 2 sidecars):
    - Ball: kick ×3, push ×2, catch ×2, hard shot ×2, and a score (the float brought up through the surface
      ring).
    - The sphere's water: enter, exit, and swim ×3.
    - Crowd beds, seamless 36 s loops: murmur at −26 LUFS (about 56 far talkers plus a babble floor) and excited
      at −23 (about 80 talkers, swells, calls, claps).
    - Crowd reactions: cheer ×2, groan, gasp.
    - The whistle, an original reed pipe (no pea, no trill): start (a step up a fourth), short, and end (three
      falling notes).
    - The naming rite (12 s): the stands talking, one low bell, the talk thinning, and a hush passing along the
      stands until only the bell is left.
  - **Underwater:**
    - Beds (`assets/audio/ambience/`, −26 LUFS, q1): `underwater_deep` (46 s: a pressure hum, far creaks, slow
      bubble trains) and `drowned_tower` (42 s: stone shaft modes driven by a surging current, ticking stones,
      leaking air, a tower groan).
    - Dive SFX (`assets/audio/sfx/dive/`): entry (the splash, then the muffle closing over), surface (the muffle
      opening, water streaming off, an unvoiced breath out with no gasp), bubble burst, stroke ×4, and the
      lantern hum, a 6 s seamless loop at −24.
  - **Data:**
    - `game/data/audio/sfx_reefball.json` (15 rows: World for the ball and the water, SFX for the crowd's
      reactions, the whistle and the rite).
    - `game/data/audio/sfx_dive.json` (5 rows, World).
    - `ambience.json` gains 4 beds, appended: `underwater_deep`, `drowned_tower`, `reefball_crowd_murmur` and
      `reefball_crowd_excited`, all on Ambience. Their zones aren't assigned yet.
  - **No scenes exist yet** for Reefball, the drowned tower or any dive zone, so the rows and beds are ready to be
    placed. Whoever builds those scenes:
    - adds the `ambience.json` `zones` rows;
    - plays the rows (`Audio.play_sfx_at` for World);
    - stops the crowd beds while `reefball_naming_rite` plays, because it carries its own stands going quiet;
    - stops the returned player of `dive_lantern_hum` when the lantern surfaces.
  - **Targets:** appended to `tools/audio/targets.py` (the crowd beds −26/−23 integrated, the whistle −17, strokes
    −20, other SFX −18 momentary, the hum −24). Noted in `mix.md` §7.
  - **Tests:** `tools/tests/test_audio_data.py` gains `LoopImportTest`: every `.loop.json` in `assets/audio` has an
    `.import` with `loop=true` at the sidecar's offset. `test_audio_loops.gd` covers only the 60–95 s music cues.
  - **Size:** about 2.0 MiB added (beds 0.36–0.38 MiB each, one-shots 9–145 KB).
  - Nobody has listened. The crowd's formant voices are the part most likely to sound synthetic; they are far and
    low-passed on purpose.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
