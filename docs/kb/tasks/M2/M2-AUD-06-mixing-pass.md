---
id: M2-AUD-06
title: Mixing pass: buses, ducking under dialogue, volume settings, a loudness test
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02, M2-AUD-03, M2-AUD-04, M2-AUD-05]
milestone: M2
request-from: lead
---
## Goal
mix.md §4 is a plan; this item makes it the game's mix.

## Acceptance criteria
- [x] The bus layout as built by the runtime, with ducking under dialogue (Music −4 dB) and ambience under battle.
- [x] Music, SFX, Voice (and master) volume settings in the existing accessibility settings, applied live and saved.
- [x] A loudness check in tools/tests that measures every shipped audio file against its mix.md target and the size budget.

## Notes

## Notes
- 2026-10-24 audio (claude/audio):
  - **Buses and ducks** as built by the Audio autoload from mix.json (M2-AUD-02): Master hard limiter; Music,
    Ambience, SFX (UI, World, Combat), Voice; `dialogue` duck (Music −4, Ambience −2 over 0.25 s) and `battle`
    duck (Ambience −3); the cutscene hold. mix.md §7 documents the mix as built.
  - **Volume settings:** `master_volume`, `music_volume`, `sfx_volume` (SFX + Ambience), `voice_volume` appended
    to accessibility.json (0–100 % in tenths, loc keys appended); `AudioDirector.follow_settings` applies them
    live from `UiSettings.shared()`; mix.json `volume_settings` maps them to buses; data_check verifies both ends.
    The on-screen menu is a request: M2-AUD-08 (ui).
  - **Loudness gate:** `tools/audio/targets.py` (a rule per file family) and `tools/tests/test_audio_loudness.py`
    (decodes every shipped .ogg; integrated or momentary loudness, true peak, 5 MB per file, a 24 MiB total, the
    boss stems as a stack).
  - Tests: `test_audio_runtime.gd::test_volume_settings_scale_their_buses_live`.
  - Not done: a per-area world reverb bus (mix.md's WorldVerb); world SFX carry their own room for now.

## Review log
