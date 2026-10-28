---
id: M3-CHR-507
title: "Inquisitor Hadric Moll, the Ch6 boss (stillguard_inquisitor): design sheet, model and battle clips"
role: character
status: review
owner_session: "characters (branch claude/characters)"
depends_on: [M2-CHR-01, M1-CHR-14]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The Act I boss `stillguard_inquisitor` (encounter `ch06_inquisitor`) has no `model` in `game/data/battle/enemies.json`
and is a white capsule in `battle_boss_intro_inquisitor` and `battle_arena_camp`. He is a person, so the character track
builds him (act1_ch06.md §9 #12, M3-C06-06 #3): **Inquisitor Hadric Moll**, forties, "a tired officer who still
believes the Edict"; red-lacquered shell armour with an Inquisitor's white sash, a round shield, a long-hafted
brine-iron held upright like a standard. Silhouette: the standard Stillguard plus the long iron. In order: design sheet
(`docs/kb/art/characters/hadric_moll.md`) → model on the base body (the human-foe path) → battle clips → shots.

## Acceptance criteria
- [ ] Design sheet reviewed by Rendering and the Art Director (swatches proposed; no FF/SE terms).
- [ ] Built from source under `assets_src/characters/` on the base-body path, host snaps opted in (M2-CHR-11), a
      `tools/dev/blender_builds.json` job verified on the three numpy paths, PROVENANCE rows, GLB < 5 MiB.
- [ ] Replaces the capsule in every scene listed in the goal (a request task to the scene's owner if it is not ours).
- [ ] Battle clips `idle`, `attack`, `hit`, `ko` (and `yield`, his scripted end: `HUD_CH06_INQUISITOR_YIELDS`), the
      brine-iron gripped by the M2-CHR-515 prop grip (it never floats), rig-probe clean.
- [ ] `stillguard_inquisitor.model` set in enemies.json (request to Combat if the battle scene is theirs).

## Notes
- Filed 2026-10-27 by the characters track from the Lead's Act I capsule audit (the Act I encounter, boss and level tables).

- 2026-10-28 (worktree chr-moll-wip): built on the hero path (`assets_src/characters/moll/`, job `moll`). Decisions
  where the sheet could not be met as written, within the §7 budgets:
  - **Sleeves:** the tunic's long sleeves are offset shells of the shipped arm skin (Liss's work-sleeve method), so
    they ride the arm exactly; the bare torso skin under the arm, between the jack's dropped armhole (M1-CHR-14) and
    the arm, is cut (it passed through the sleeves as the arm came down). The tunic otherwise shows as its skirt.
  - **The yield (`ko`):** the iron is planted before him on the midline, not at his right knee: with the 0.62 m
    shield on his left forearm, the left hand could only reach a haft at his right side with the shield through his
    chest. Both hands are on the haft (the left 12 cm over the right), the shield clear of his body, the haft 13 cm
    clear of his legs (arm turns searched numerically on his skeleton). `yield` is the same clip under its own name.
  - **Attack:** "two-handed" is read as the right fist driving the levelled iron with the shield arm swinging back
    (the sheet's own note); the fist's grip (the haft across the palm) cannot level a 2.1 m haft at shoulder height,
    so the thrust carries the head to chest height (1.3 m) from a fist at the hip, rising 15 degrees.
  - **Finisher:** the iron's lift stops at the wrist's reach (raised diagonally over his head, not head-forward).
  - **No revive** (optional in the contract): he is a foe. The battle clip tests skip it for him and check the yield
    kneeling on the haft instead of lying down (KO_OWN).
  - **Combat:** `stillguard_inquisitor.model` is not set here (ownership). Point it at a battle actor that instances
    `res://assets/characters/moll/moll_lod1.glb` (it shares `moll_clips.tres` through the import rule's
    `strip_suffixes`), e.g. `game/characters/heroes/moll_battle.tscn` built like the heroes' `<hero>_battle.tscn`
    (M2-CHR-06); the actor plays `ko` for 0 HP (the yield) and `yield` for HUD_CH06_INQUISITOR_YIELDS.

## Review log
