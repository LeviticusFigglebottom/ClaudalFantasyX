---
id: M3-BPR-420
title: "Act I at final quality (ADR 0041): every Act I ability plays its own battle VFX, not only the generic hit"
role: combat
status: review
owner_session: claude/battle-presentation
reviewer: rendering
depends_on: [M2-RND-03]
milestone: M3
request-from: lead
---
## Goal
The Lead (01:12, ADR 0041): every Act I enemy ability, party ability, Swell and Vowbound summon has its real VFX (no
stand-in flashes); make the list of every Act I ability whose VFX is generic or missing, and work through it.
Rendering, who owns the battle VFX, is paused with the PC, so this track does it (an ownership row records why).

## The list (2026-10-28)
Before this, `map.skills` named 3 specials (lamp_dive, shallows_verse, read). Every other Act I ability played only
its element's generic hit, and supports, stances, gathers, summons and items played nothing (tools/battle_vfx_coverage.py).

## Done
- `tools/vfx/gen_act1_ability_vfx.py` writes 85 effects into effects.json, each described in its `note`: 77 skills
  (every party kit skill, Ch8's set-piece skills, the 5 other Swells, the 4 Vowbound skills, every Act I creature
  skill and gather) and 8 battle items. Palette swatches only, from 10 motifs: slash, heavy, burst, spray, shards,
  rise, sink, ring, charge and column.
  - Art rules kept: glimmer_lift only for release; spawn wounds sink or move sideways; lamps burn oil; Vowbound light
    is glimmer_bound.
  - Never overwrites rendering's effects (the Drownbell's aimed polyp_mend stays; the polyp's own is `polyp_mend_hit`).
  - `--check` mode.
- Not mapped on purpose: the ward-aimed skills (grip_the_stair, rope_dive, hand_closes). The stair entry has no
  fighter, so an effect would play at the VFX node's origin; their motion is the push reaction (M3-BPR-416). The
  Drownbell's toll and gather stay its boss view's.
- **Sounds:** audio's validator needs a sound per effect. Until audio gives them their own (request **M3-BPR-421**),
  each borrows an existing row: a damage skill its element's hit (a repeat inside repeat_ms is the softer layer), a
  heal or stand-up the heal, the rest the status sound.
- **Battle entry cost:** `BattleVfx.prebuild()` now builds a skill's own effect only if someone in this battle can
  use it (the fighters' skills, the Swells, the Vowbound). Headless, 178 emitters took 66 ms and the sandbox fight
  now builds 72. Rendering's file, a minimal change with its test updated.
- Tests:
  - `test_battle_act1_ability_vfx` (every Act I skill has its own effect; the items; the prebuild filter);
  - `test_battle_vfx` and `test_battle_audio`, with their expectations updated (the skill's own effect first; the
    fire hit's softer repeat);
  - validate_data 0/0.
- Viewed: `tools/vfx/act1_vfx_sheet.tscn` renders every effect on the battle stage, six per sheet, labelled.

## Review log
