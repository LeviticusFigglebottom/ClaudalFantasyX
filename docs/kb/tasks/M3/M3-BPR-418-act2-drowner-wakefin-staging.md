---
id: M3-BPR-418
title: "Act II battle presentation, next bosses: the Mangrove Drowner (Ch10) and the Wakefin (Ch15)"
role: combat
status: review
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
- [x] Greybox Act II boss arenas (tools/arenas/gen_act2_arenas.py → game/battle/arenas/, arenas.json), each in its
      chapter's grade from color_script.md:
  - `fen_roots_dusk` (Ch10, the Drowner): a mud bar in tannin water under the prop-root cage, overcast dusk;
  - `lowlight_engine_hall` (Ch11, the Lamp Engine): the flooded hall, pillars, conduits in steady bound teal, the
    engine's brass-framed recess;
  - `keth_terrace_wall` (Ch12, the Ram): snow under the Lit Age terrace wall and its cold seep, the pass-cord's red
    knots the only warm note;
  - `night_sea_barge` (Ch15, the Wakefin): the wedding barge at night, no lamp struck, the sea-glow only.
  - Staging rows: the barge 0.6 travel and 0.9 tempo (short runs on a deck); the fen 0.9 (mud).
  - Tests: test_battle_act2_arenas (load, grade, quiet lights, drop into a battle by id), plus test_battle_arena's
    contract (every greybox keeps a Sea).
  - Shots: battle_arena_<id> through `shots/arena_by_id_shot.gd` (`BattleArena.apply_scene`, since there's no
    encounter yet). Render requested. Encounters name them in `arena` once they're written; env-art's kits replace
    them through arenas.json.
- Ask: whoever writes the Act II enemies, keep the ids `mangrove_drowner` and `wakefin`, and the phase id `uprooted`.

## Review log
