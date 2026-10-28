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
- 2026-10-28, battle-presentation: **M3-HER-1148's five rows** (integration-qa's inventory: Act I bosses with no
  set-piece VFX) are filled.
  - `boss_vfx.json` `bosses` gets kind-`set_piece` rows, played by the new `BattleBossSetPiece`: a gather on each turn
    of a charge, a moment per phase, and the fall.
    - Hullgnaw: coil; ribs breaking; release.
    - The Spar-Wraith: lines; hauled down; release.
    - The Cinder Matron: recrust; the pour; embers settling.
    - The Inquisitor: torching the hulk.
    - The Reach: its gathers; the storm-dark; the Breach.
  - The Drownbell keeps its own rig (`BattleBossVfx.boss_of` skips set-piece rows).
  - The bosses' phase skills (Thrash, Haul, Sea Lash, Slag Pour, Torch the Hulk, the Breach, Recrust, Flood Surge,
    Undertow Surge) got their own effects too. The coverage test now walks phase skills.
  - Tests: `test_battle_boss_set_piece` (each boss plays its moments in order, once; the Drownbell isn't doubled).
- 2026-10-28, battle-presentation: **the Lead's 02:14 item 3, camera choreography on each Act I boss fight.**
  - `choreo.json` `camera.enemy_by_skill`: a boss's big moves get a shot of their own instead of the foes' default push.
    It is checked before `enemy_by_actor`, and the plan now carries `skill`.
    - A heavy single blow (Hood Slam, Gnaw, Thrash, Haul, Ladle Swing, Brine Iron, Crust Slam) plays `boss_blow`, then
      `target`.
    - A move on the whole party (Sea Lash, Shroud Sweep, Slag Pour, Torch the Hulk, Undertow Pull, the Breach) plays
      `boss_sweep`, then holds wide.
  - The heroes' `finisher` and `actor` shots sit on the party's side of the actor, so for a boss every one failed the
    safe frame and fell back to the default. The new `boss_blow` and `boss_sweep` stand behind the boss, on the viewer's
    side (negative `back_m`), so the line is never crossed. Every move passes the safe frame in its own fight.
  - Tests: `test_battle_boss_camera` (each boss's big moves get their lead shot, live in their own fight);
    `tools/validate_choreo.py` checks enemy_by_skill pairs (`EnemyBySkillTests`).
  - Viewing: `tools/vfx/boss_camera_sheet.tscn` renders each move at its lead shot and at the contact.
- 2026-10-28, battle-presentation: **the Lead's item 2, the VFX checked at battle distance on the dressed arenas**
  (env-art and env-art-b merged into a scratch worktree, not pushed; `act1_vfx_sheet --enemy_set`).
  - Most Act I creatures had no stand-in height, so they used the 1.7 m default. Hits floated a metre over the Oil
    Slug and struck the Spar-Wraith's shins. `battle_sandbox.json` `stand_ins` now has a measured `height` row for
    21 Act I creatures (the top of the battle model's bounds; fliers keep their hover). The Reach is left out: its
    model's bounds run 16.5 m tall.
  - On the dark Ch1 tower, Oil Slap (black oil) vanished, so lamp-lit glints now ride on it, and on Smother. Lure Glow
    was a faint fleck on the beaches, so it is larger and brighter.
  - The boss shots were retuned for the real heights (`boss_blow`: strike, back -3.6, side 6.6, up 2.6, fov 56;
    `boss_sweep`: actor, back -4.6, side 6.6, up 2.6, fov 50). A grid probe checked all 13 big moves against the safe
    frame, and the neighbouring settings pass too.
- 2026-10-28, battle-presentation: **the boss-camera sheet, viewed** (`tools/vfx/boss_camera_sheet.tscn`, on the
  dressed arenas).
  - These read well, the boss framing its target from the viewer's side with the party in shot: Hullgnaw's Gnaw and
    Thrash, the Wraith's Haul, Sea Lash and Shroud Sweep, the Matron's Ladle Swing and Slag Pour, the Inquisitor's
    Brine Iron and Torch the Hulk, and the Drownbell's Hood Slam.
  - The Reach failed: from behind its lunge the lens saw only its arm, and the low skyward shot dropped under the
    wall-head.
    - The director now drops a foe's shot when its body, at the strike point, stands across a sight line to its
      targets. A target point inside the body's bounds never counts, since a colossus's rest bounds take in the party
      under its hand.
    - The Reach keeps the default frame, which already shows its hand over the party.
  - Tests: test_battle_boss_camera (+ the body check), camera 53/0, choreo 56/0. The four shots with a foe's action
    (toll, ch08 intercept/counter/withdraw) are unchanged by the check (rmse 0.0000 against the previous capture).
