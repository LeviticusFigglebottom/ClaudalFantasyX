# Handoff: characters track, 2026-10-28 (session 1)

Branch `claude/characters`. The MERGE-READY lines in `docs/kb/handoffs/live/characters.md` carry each item's checks.

## Done
- **FAST-TRACK: a grounded run.** Asha, Toma and Rhen share `_RUN` (0a565c4f).
- **The Stillguard soldiers**, M3-CHR-508.
- **The named Act I NPCs**, M3-CHR-526..539 (the villager pipeline), then polished at dialogue range in story order:
  - hair strands, stubble shadows, tight head wraps and headbands, Hobb's knots, Marra's shawl, Garo's burns;
  - Sabe's and Ione's tank tops, feathered hairlines, wiry old brows.
- **Ivo Brannick**, M3-CHR-540: a named Stillguard with his face uncovered.
- **Liss's fringe** in soft clumps, M2-CHR-521.
- **Short hair and beards at dialogue range** (Toma, Kerrid, Moll, netmender), M2-CHR-524, with the soldiers rebuilt on
  the same code.
- **Asha's skirt as cloth.**
  - The pooled skirt drapes onto the floor (M2-CHR-522 follow-up).
  - 16 panels, the even ones derived each frame by HeroSkirtFolds (M2-CHR-542, ADR 0140). The Lead's runtime option
    measured 107 ms per hero, so this is a hybrid at 0.037 ms.
- **Real closed-hand grips**, M2-CHR-544: the prop moves into the fist's hole and the fingers wrap it.
- **big13, big14 and the big14 gate merged in.** `stand_at_pool` is built. big14's test_hero_clips failures are fixed on
  this head.

## In progress
Nothing running.

## Exact next step
Wait for the Lead's merge of `claude/characters` and the GPU renders. These need re-approved baselines:
- every Asha shot (the skirt, the grips);
- Toma's, Moll's and the soldiers' grip shots;
- the villagers' face and front shots;
- the new ivo_* and named-NPC shots.

Then pick from Known issues.

## Known issues
- **M3-CHR-541** (the creatures track): validate_creatures only accepts game/creatures/ models, so
  `stillguard_inquisitor.model` cannot point at `game/characters/foes/moll_battle.tscn` yet.
- **M3-CHR-543** (cinematics / m2-slice): act1_gpu_qa row 31 is staging. Asha kneels with her knees on Rhen; her kneeling
  skirt reaches 0.67 m forward. Re-stage her beside him.
- **Asha's grip** is looser than Toma's: index and ring tips about 38 mm from the staff axis; in walk and run the staff
  turns 21° in her fist to clear the skirt.
- **Leftovers on the NPCs:**
  - Ione's top flares under the arms;
  - a faint edge where each strap lies over the panel;
  - Ione's fringe card tips show as dashes;
  - Toma's crown is faintly mottled close up;
  - Moll's fringe ends in a straight line;
  - toma_lod1 is 1.55 MB.
- **Kerrid's attack** reads as a thrust (M3-CHR-525).
- **Messages to the Lead's session fail** (it needs a trusted device). The live log is the channel.

## Files touched
- `assets_src/characters/asha/{hero_clips,helper_bones}.py`, `game/characters/{hero_helper_bones,hero_skirt_folds}.gd`,
  `game/core/import/characters_post_import.gd`, `game/data/characters/{helper_bones,grips}.json`,
  `tools/dev/{rig_probe.py,rig_checks.json}`, `tests/unit/test_hero_stage.gd`, `docs/kb/decisions/0140-*`.
- `assets_src/characters/{liss,stillguard,villagers,moll,toma}/**` and their outputs, `assets_src/characters/requested_clips.json`.
- Tasks M2-CHR-542 and 544, M3-CHR-541 and 543, and the live log.
