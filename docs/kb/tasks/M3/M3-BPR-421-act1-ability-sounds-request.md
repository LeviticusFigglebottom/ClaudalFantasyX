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
