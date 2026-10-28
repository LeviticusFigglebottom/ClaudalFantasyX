---
id: M3-BPR-418
title: "Act II battle presentation, next bosses: the Mangrove Drowner (Ch10) and the Wakefin (Ch15)"
role: combat
status: blocked
blocked-by: ADR 0041
owner_session: claude/battle-presentation
reviewer: lead
depends_on: [M3-BPR-408]
milestone: M3
request-from: lead
---
## Goal
TRACK-RULES self-directed backlog step 5 (the next act in this area). After M3-BPR-408 (the Lamp Engine, the
Avalanche Ram), stage the other Act II bosses whose creature scenes exist (claude/creatures, in big12), from
docs/kb/art/creatures/act2_roster.md and act_outline.md. Their enemies and encounters aren't written yet, so
everything is keyed by enemy id, as 408 was.

## Done (2026-10-27)
- **Boss intros by enemy id** (choreo.json `boss_intro.by_enemy`), with the M3-BPR-404 fit, the card clearance and
  the party rule:
  - the Mangrove Drowner: `boss_tall` (the root cage stands tall), "The Mangrove Drowner / It grew into the roots and
    would not let go";
  - the Wakefin: `boss` (low in the water), "The Wakefin / It followed the first wake out of Ansedra".
  - Loc keys BOSS_TITLE_/BOSS_EPITHET_MANGROVE_DROWNER and _WAKEFIN appended to strings.csv.
  - Test: `test_an_act_two_boss_gets_its_intro_wherever_it_appears` now covers all four Act II bosses.
- **The Drowner tears free** (choreo.json `bosses.mangrove_drowner.phases.uprooted`, the phase id from its
  creatures.json row): its root lifts and rocks while its own `phase_change` clip plays, and the party braces in
  turn. Test: `test_the_drowner_tears_free_with_a_moment`.
- **The Wakefin's telegraph** (choreo.json `bosses.wakefin`, `camera.pressure.by_enemy.wakefin`): it fights in the dark,
  so any charge it gathers sinks its blade under the water and holds it there (no light added), and the camera closes
  in a step a turn. Sound and sea-glow are audio's and rendering's. Test `test_the_wakefin_sinks_its_blade_and_the_dark_closes_in`.
- Request M3-BPR-419 to act1-chapters: the Act II boss encounters use these enemy, phase and arena ids.

## Next (when their rows exist)
- [ ] Shots: battle_boss_intro_drowner, battle_boss_intro_wakefin, and a freeze-frame of the Drowner tearing free.
      Then render requests.
- [x] ~~Greybox Act II boss arenas~~ **withdrawn 2026-10-28.** Env-art has built the final kits (claude/env-art:
      `ossa_fen_roots` M3-ENV-718, `lowlight_engine_hall`, `keth_seep_terrace` M3-ENV-717, `bridal_barge_night`), and
      the Lead's gate has rendered them. The greyboxes duplicated them, and one id (`lowlight_engine_hall`) and its shot
      would have collided at merge. They're removed, generator and shots included. Request M3-BPR-419 names env-art's
      ids.
- Ask: whoever writes the Act II enemies, keep the ids `mangrove_drowner` and `wakefin`, and the phase id `uprooted`.

## Review log
