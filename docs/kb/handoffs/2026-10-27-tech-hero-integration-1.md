# Handoff — tech (hero-integration) — 2026-10-27 #1

Session `session_01PzF7Jc4XVQdTWcaYUyCjPB`, branch `claude/hero-integration`. Live log: `docs/kb/handoffs/live/hero-integration.md`
("NEW ACCOUNT" section).

## Done
- Merged the integration branch twice (c6a960ab, then big9 @ 5c5b9292).
- **M2-HER-1110, the no-snapping guards** (ADR 0192): `HeroMotionGuard` plus limits in `motion_guard.json`, and four tests:
  - battle pops on every hero (26 clip changes each);
  - field snaps over 13 zones;
  - cutscene snaps over 27 scenes (the prologue plus the slice and Act I);
  - Haluna's villagers (duck-typed on creatures' VillagerLayer).
- **Fixed by the guards:**
  - followers dropping 2 m through the Brightwater Ferry's pier edge (feet now take a floor within a step of Rhen's
    trail height, eased);
  - Ysolde's placeholder KO standing up in one frame (the wrapper installs placeholders and then tunes their blends);
  - a crash installing placeholder clips under a playing AnimationPlayer (the wrapper now installs on a stopped player).
- **Ysolde:** a battle wrapper (`ysolde_battle_actor.tscn`) and a field and cutscene body (hero_motion.json; walk 1.02
  and run 2.11 m/s measured). Her cutscene whip turns are gone.
- **M2-HER-1116:**
  - followers turn to face whoever Rhen talks to;
  - stairs and slopes ease;
  - `HeroFootIK` on every field and cutscene hero body (flat ground untouched; a 1 cm continuous dead zone).
- M2-HER-1103: revive blend rows for characters' coming revive clip.
- The battle_heroes_* shot rig is applied (scenes in `game/levels/_tests/hero_motion/`). Its shots.json rows are at
  b2453cfd for the PC render only (see Known issues).

## In progress
- Requests out (task files; the Lead relays them, since send_message is off):
  - 1108 (ui-menus): repoint the battle stand_ins at the wrappers, Ysolde too;
  - 1111 (QA & Tools): the runner hides parse errors;
  - 1112 (slice-polish): put the VillagerLayer in Haluna;
  - 1113 (slice-polish): `cutscene_no_snap.patch`, verified on claude/m2-slice;
  - 1114 (battle-presentation): the placeholder crash fix (`stop()` before the library swap) and the finisher arm
    flip;
  - 1115 (characters): Ysolde's battle clips;
  - M3-HER-1117 (creatures): villagers' foot IK.
- Render request @ b2453cfd: battle_heroes_* plus the field hero shots. Waiting on the PC.

## Exact next step
1. When the PC posts `RENDERED @ b2453cfd`:
   - fetch `gpu/render-hero-integration-b2453cf` and view every out and diff PNG;
   - copy the approved battle_heroes_* outs into baselines with the lavapipe metadata;
   - re-add the 7 shots.json rows in the same commit.
2. As each request lands, empty its KNOWN entry:
   - test_hero_cutscene_snaps (1113);
   - test_hero_battle_pops (1114).
3. After 1108 lands, re-run test_hero_battle_pops and the battle filter on the integration branch.
4. Then write the fold-into-characters handoff (standing queue item 7).

## Known issues
- The battle_heroes_* rows are held out of shots.json until their baselines are approved (the tools manifest test
  needs a baseline per row).
- In tests, a StaticBody3D moved after entering the tree, or freed, only updates the physics space on a physics step
  (see test_hero_foot_ik's per-test sites).
- `tests/run_tests.gd` reports a test file with a parse error as "0 failed" (M2-HER-1111).
- Rhen peaks at 5.85 m/s on Pemakar (step push-ups; FieldController is slice-polish's), under the 6 m/s limit.

## Files touched
- `game/hero_motion/`:
  - hero_motion_guard.gd, hero_foot_ik.gd (new);
  - hero_field_party.gd, hero_field_actor.gd, hero_battle_actor.gd, hero_motion.gd;
  - battle/ysolde_battle_actor.tscn (new).
- `game/data/hero_motion/`: motion_guard.json, foot_ik.json (new); hero_motion.json, battle_hero.json.
- tests:
  - `tests/unit/`: test_hero_battle_pops, test_hero_field_snaps, test_villager_snaps, test_hero_foot_ik (new);
    test_hero_battle_actor, test_hero_followers;
  - `tests/integration/test_hero_cutscene_snaps.gd` (new).
- `game/levels/_tests/hero_motion/battle_heroes_*` (from hero_battle_shots.patch).
- `docs/kb/`: tasks M2-HER-1103, 1108–1116 and M3-HER-1117; decisions/0192;
  tech/cutscene_no_snap.patch; the live log.
