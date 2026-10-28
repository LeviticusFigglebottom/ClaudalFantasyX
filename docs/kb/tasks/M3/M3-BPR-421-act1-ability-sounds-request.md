---
id: M3-BPR-421
title: "Request: sounds of their own for the 85 Act I ability effects (they borrow hit/heal/status rows for now)"
role: audio
status: todo
owner_session: ""
depends_on: [M3-BPR-420]
milestone: M3
request-from: combat
---
## Goal
M3-BPR-420 gave every Act I ability its own battle VFX (effects.json; each effect's `note` says what it is). Your
validator rightly needs a sound per effect, so each currently borrows a row in `battle_sfx.json` `vfx`: a damage
skill its element's hit (the repeat plays as your softer layer), a heal or stand-up the heal, the rest status_apply.
These rows were appended by `tools/vfx/gen_act1_ability_vfx.py`, which only fills missing keys and never changes
yours.

## Acceptance criteria
- [ ] Each Act I ability effect gets its own sfx row (or a deliberate share), in your style.
- [ ] test_battle_audio's fire-hit expectation goes back to one play if Ember gets its own sound.

## Review log

## Added 2026-10-28 (M3-BPR-422)
- Two new choreography styles, `swing` (Kerrid's Swell, the weighted swing) and `reel` (Liss's Swell, the reel-stop),
  have stand-in rows at the end of `choreo_sfx.json` `styles`, borrowing the finisher's and the item throw's sounds.
  Each wants its own Swell contact sound, as `swell_rhen` … `swell_ysolde` are for the other four.
- Their effects `swell_weighted_swing` and `swell_reel_stop` borrow `hit_none` and `status_apply` in `battle_sfx.json`.
