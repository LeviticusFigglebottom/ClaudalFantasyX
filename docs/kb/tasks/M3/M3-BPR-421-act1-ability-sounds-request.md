---
id: M3-BPR-421
title: "Request: sounds of their own for the 85 Act I ability effects (they borrow hit/heal/status rows for now)"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
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
- [x] Each Act I ability effect gets its own sfx row (or a deliberate share), in your style.
      - 73 effects have their own `abl_<effect>` sound (assets_src/sfx/act1_ability_sfx.py, Git LFS), each made from its
        note.
      - The 13 boss and set-piece mechanics share their skill's own row (`skill_<id>`, M3-AUD-861). Inside the 250 ms
        dedupe they play once.
      - The audit's Abilities section (`tools/audio/act1_audio_audit.py`) is 0.
- [x] test_battle_audio: Ember plays `abl_ember`, with the fire hit landing under it as the impact.
- [x] M3-BPR-422's styles:
      - `swing` is whoosh_swing → swell_kerrid.
      - `reel` is reel_whir → swell_liss.
      - Both have crest times in choreo_sfx.json `peaks`.

## Review log

## Added 2026-10-28 (M3-BPR-422)
- Two new choreography styles, `swing` (Kerrid's Swell, the weighted swing) and `reel` (Liss's Swell, the reel-stop),
  have stand-in rows at the end of `choreo_sfx.json` `styles`, borrowing the finisher's and the item throw's sounds.
  Each wants its own Swell contact sound, as `swell_rhen` … `swell_ysolde` are for the other four.
- Their effects `swell_weighted_swing` and `swell_reel_stop` borrow `hit_none` and `status_apply` in `battle_sfx.json`.
