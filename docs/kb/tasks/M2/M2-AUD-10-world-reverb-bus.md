---
id: M2-AUD-10
title: A per-area world reverb (WorldVerb) for World and Combat sounds
role: audio
status: review
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
reviewer: qa
depends_on: [M2-AUD-06]
milestone: M2
request-from: lead
---
## Goal
mix.md §4 planned a WorldVerb bus with a preset per area; M2-AUD-06 left it out (world SFX carry their own room).

## Acceptance criteria
- [x] A reverb on the World and Combat buses (Godot buses send to one bus, so an AudioEffectReverb on each with wet/dry from data), presets per area in mix.json (open sea, village lanes, stone shrine, cave), chosen by the zone row.
- [x] Rendered SFX keep a dry enough room that the bus reverb doesn't double it; tests for preset switching on a zone swap.

## Notes
- `game/audio/world_verb.gd` (WorldVerb): an `AudioEffectReverb` on each of mix.json `reverb.buses` (World,
  Combat; reused if already there), both following one preset; every parameter ramps linearly over `ramp_sec`
  (0.5 s); a preset with wet 0 switches the effects off at the end of the ramp.
- `mix.json`: `reverb` (buses, default `dry`, ramp) and `reverb_presets`: dry, open_sea, village_lanes,
  stone_shrine, drowned_cave, battle_beach (all eight parameters + a `_note`).
- `music.json` (only `reverb` keys added): Haluna `village_lanes`, Shell Shrine `stone_shrine`, field battle
  `battle_beach`; title and end card take the default (dry). `AudioDirector.apply_zone` applies the row's preset
  (variants can override), only when it changes.
- **No doubling:** the shrine SFX are rendered in their room (rt60 1.5 s, 22 % wet), so `stone_shrine` is 5 % wet of
  a mid room (enough for the dry footsteps); battle SFX carry 12-30 % of a short room, so `battle_beach` is 5 %.
  `drowned_cave` (28 %) assumes dry-rendered SFX. Documented in audio_runtime.md "Area reverb" and mix.md §7.
- Checks: `data_check.reverb_errors` (buses, default, ranges, zone/variant keys) + 2 tests in test_audio_data.py;
  `tests/unit/test_audio_reverb.gd` (5: repo presets complete, in range and named by zones, shrine wet < cave/2;
  World and Combat carry exactly one reverb; a zone swap ramps both buses halfway then fully; a row without reverb
  goes dry and switches off; an unknown preset changes nothing).

## Review log
