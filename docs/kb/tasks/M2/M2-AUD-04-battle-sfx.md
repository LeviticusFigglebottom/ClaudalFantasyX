---
id: M2-AUD-04
title: Battle SFX for the M2-RND-03/04 VFX library
role: audio
status: review
reviewer: qa
owner_session: agent-ae73db10c741bdad2
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
The battle VFX library (battle_vfx.md) is silent. Every effect and boss moment needs a sound, wired listen-only to the same engine and BattleVfx events.

## Acceptance criteria
- [x] Synthesized SFX: element hits (none, fire, ice, lightning, water, holy), Lamp Dive, Shallows Verse, Read, heal, status, KO release, the ambush and preemptive stingers, the Drownbell toll (and its gather), the rim crack and break, polyp rise and mend, Floodnet, the bell's release, the Vowbound call and dismiss.
- [x] A data table (`game/data/audio/battle_sfx.json`: VFX effect id or engine event -> SFX), a `BattleAudio` listener that never writes combat state, and a reduced-audio setting (fewer, softer layers; no stingers' sub-bass).
- [x] Tests: every VFX effect id maps to a sound that exists, the trigger rules, reduced audio, determinism of the renders.

## Notes
- **Sounds:** `assets_src/sfx/battle_sfx.py` (fixed `SEED`, every random draw through `synth.dsp.rng`), registered in
  `tools/audio/render_all.py` JOBS (kind `sfx`). It writes 45 mono Ogg q4 files under `assets/audio/sfx/battle/`,
  plus `assets/audio/sfx/drownbell_toll.ogg`, the far, underwater toll that the cutscene's `@sfx drownbell_toll`
  loads (ch03_the_first_verse). That file used to be a known missing placeholder.
  - Hits have 2–3 variants each (holy has 2). The reduced-audio `_soft` versions of the Flood, the ambush stinger
    and the toll drop the sub-bass.
  - Everything is synthesized, from the music palette: metallophone, gongs, a cast-bell partial model for the
    Drownbell, Minnaert bubbles, and filtered noise. The pitched figures (Shallows Verse, preemptive, victory,
    Vowbound call) are short original pentatonic or open-fifth gestures, as stated in the module docstring.
  - The set totals 0.77 MiB. The largest file is `flood_soft.ogg` at 66 KB.
- **Loudness (decoded):**
  - Combat SFX are within −18 ± 0.9 LUFS momentary max. The peaky ice and rim cracks sit at about −18.5 to −18.9.
  - The stingers, the toll, the bell's release and victory are −16.
  - The quiet textures are lower: Read, toll_gather and polyp_mend −21; status −20; heal, polyp_rise, dismiss and
    escape −19.
  - Every decoded true peak is ≤ −1.1 dBTP, rendered at a −2 dBFS ceiling.
  - `render_all.py --only battle_sfx --determinism` reports all 45 files identical.
- **Tables:**
  - `game/data/audio/sfx_battle.json` holds the rows (Combat bus).
  - `game/data/audio/battle_sfx.json` holds the hooks. `vfx` maps all 21 effects.json ids. `skills.toll`, `events`
    (rim_break, vowbound_call, vowbound_dismiss, vowbound_fell → ko_release), `fields_cleared.flood` → floodnet,
    `phases.flood` → flood, and `openings` and `outcomes` (victory, defeat, escaped → escape) are the fallbacks.
  - `reduced`, `repeat_ms`, `dedupe_ms`, `layer_db` and `reduced_level` are the remaining keys.
  - `data_check.py` now also checks that the keys of `reduced` are real rows (with a test in
    `tools/tests/test_audio_data.py`).
- **BattleAudio** (still listen-only):
  - A fallback hook is dropped when the same sound played within `dedupe_ms`, so the view's flash and the
    engine's opening, toll skill or charge_broken ring once.
  - A vfx repeat within `repeat_ms` (an action's other targets) layers 6 dB softer.
  - **Reduced audio** (a new `reduced_audio` bool appended to `accessibility.json`, with its loc keys appended to
    `strings.csv`) is read live via `UiSettings.shared().changed`. It skips the repeats, swaps the `_soft`
    versions in, and multiplies `SfxBank.level` by 0.7 for the battle. The factor is divided back out on exit,
    so a retry's overlapping listeners compose.
  - `tests/unit/test_ui_settings.gd`'s expected settings list gained the new id (a one-line consequence).
- **Tests:** `tests/unit/test_battle_audio.gd` (10) covers:
  - every effect maps to an importable sound;
  - a fire hit plays a fire variant, and a KO plays ko_release;
  - the Flood surge and Floodnet. The stem check runs only when music.json has a drownbell row; today it has
    none, so the check is skipped;
  - the opening stinger plays once, and the toll plays once from either hook;
  - the Vowbound's call, dismiss and fall;
  - repeats layer;
  - reduced audio (one layer, flood_soft, the bank level live, the level restored on exit);
  - overlapping listeners.
- **Gates:**
  - Pass: validate_data, taskboard --check, gdlint, gdformat --check, unittest (513 tests, OK), Godot
    `--filter=audio` (22/0), `--filter=battle` (421/0), `--filter=ui_settings` (11/0).
  - Not run: no screenshots (no scene or shader touched); no coverage step (game/battle and game/progression
    were not touched).
- **For the reviewer (nobody has listened):**
  - The numbers are proxies.
  - The likeliest weak spots are the lightning crackle (it may read as static) and the Flood's sub-bass on small
    speakers.
  - Retune per sound in `battle_sfx.py` (the `SFX` targets) and re-render with
    `python3 tools/audio/render_all.py --only battle_sfx --determinism`, then
    `godot --headless --path . --import`.

## Review log
