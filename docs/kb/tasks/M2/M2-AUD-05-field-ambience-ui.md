---
id: M2-AUD-05
title: Field ambience, footsteps, and the new menus' UI sounds
role: audio
status: review
owner_session: "agent-a12c0d49e64ca7b3f"
reviewer: qa
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
The field is silent apart from music. SPEC §9 asks for ambience beds; the new menus (field menu, Vowbound, shop and inn) have no sounds.

## Acceptance criteria
- [x] Ambience beds at −26 LUFS: Haluna by day and by night, surf, the dock, the shrine interior; wind tied to the WeatherClock's zone wind (M2-ARC-02).
- [x] Footsteps by surface (sand, stone, wood) driven by the field motor, listen-only.
- [x] UI SFX for the field menu, the Vowbound menu, and the shop and inn, wired by a data table of menu signals. The shop and inn hooks are pending until M2-UI-06 lands.

## Notes
Implementation by agent-a12c0d49e64ca7b3f, 2026-10-24. Details are in docs/kb/tech/audio_runtime.md ("Ambience", "Footsteps", "Menus").

**Assets.** Everything is synthesized in-repo. `render_all.py --only field_ --determinism` gives identical bytes.
- `assets_src/sfx/field_ambience.py` makes six stereo loops in `assets/audio/ambience/`, each with LOOPSTART/LOOPLENGTH tags and a `.loop.json` sidecar:
  - haluna_day 48 s, haluna_night 44 s, surf 42 s, dock 40 s, shrine_interior 45 s, wind 40 s.
  - All measure −26.0 ± 0.15 LUFS decoded, with true peaks of −8.9 to −14.5 dBTP. Seam flux is 0.48–1.74× the median.
  - Total 2.36 MiB, at Vorbis **q1, not q3**: these noise beds came to 3.1 MiB at q3. `render_all.py` enforces a 2.5 MiB ambience budget and the −26 LUFS / −5 dBTP check.
- `assets_src/sfx/field_sfx.py` makes the mono SFX in `assets/audio/sfx/`, 148 KiB in total:
  - 15 footsteps, `step_{sand,stone,wood}_01..05`: momentary max −18.0 to −19.4 LUFS, true peak ≤ −1.0 dBTP.
  - 7 UI sounds (menu open and close, page, buy, inn rest, error, Vowbound glass tone): −20 LUFS momentary max.
- `render_all.py` gains an `ambience_loop` kind, and its 5 MiB budget now counts M1's jobs only.

**Runtime** (`game/audio/`):
- `ambience.json` adds bed rows and zone beds where music.json names none (no `ambience` key or an empty list). music.json is not edited. Haluna and the shrine are wired. The wind bed's level is `AudioData.wind_db` of `WeatherClock.zone_wind(scene)` (Haluna's 6 m/s gives −9 dB).
- `FootstepAudio` reads only the FieldController's `global_position` and `grounded()`, so no architect request was needed. Stride, surface and pace data are in `footsteps.json`.
- `UiAudio` uses the `ui_sfx.json` hooks (signals, on_enter/on_exit, and per-frame Expression watches with a priority list). It covers CommandMenu (including the Vowbound's own page), FieldMenu, BestiaryMenu, SaveMenu, TitleMenu and GraphicsMenu. The ShopMenu and InnMenu hooks are `pending`: their class and signal names are guesses to fix when M2-UI-06 lands.
- The Audio autoload is now `PROCESS_MODE_ALWAYS`. Without it, the field menu's tree pause paused the music and every menu sound.

**Checks:** `tools/audio/data_check.py` validates ambience.json, footsteps.json, and ui_sfx.json's structure. It checks classes and signals against `game/**/*.gd` and never reads class, signal or expression strings as sfx ids. Tests are in `tools/tests/test_audio_data.py` (+4) and `tests/unit/test_field_audio.gd` (9).

**Left for later:**
- Haluna's dock needs a per-area surface for the wood footsteps. Today the surface is per scene (Haluna is sand). This needs a marker from the Haluna owner.
- To the lead: music.json's shrine row carries `"ambience": []`. ambience.json treats an empty list as "names none", so the shrine bed applies.

## Review log
