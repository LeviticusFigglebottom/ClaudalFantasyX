# Handoff: creatures track (art), 2026-10-27, session 2

Branch `claude/creatures` (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY). Live log: docs/kb/handoffs/live/creatures.md,
section "NEW ACCOUNT (from 2026-10-25)".

## Done
- **Item 1, triage:** the post_import failures were a stale import cache. test_battle_ko_once's primitive-foe test
  fails on the integration branch too, and its fix is in big9.
- **M3-CRE-613, villagers alive:**
  - NpcLook (head attention); FieldNpc glances, look-arounds, chat pairs in bouts, work and storm, and a talk that
    ends when the player gets control back;
  - VillagerLayer (one node per zone; `attach: child` for cutscene actors);
  - zone data for Haluna and haluna_wake;
  - validate_npc, tests, review stages.
- **M3-CRE-615, Act I wildlife data:** M3-CRE-616 adds insects (a worktree agent).
- **M3-CRE-617, hit snap:** hits cut in at 0.1 s, so the hit-stop holds a struck pose, and the four weakest boss
  hits were rebuilt.
- **M3-CRE-618, portrait lights:** camera-relative, with a stronger rim and a kick for the nine darkest creatures.
- **M3-CRE-620:** the Act II roster and every design sheet.
- **M3-CRE-621:** the Mangrove Drowner built (a worktree agent).

## In progress
- M3-CRE-623, the Lamp Engine build (a worktree agent). No renders: its two shots go to the PC.
- RENDER-REQUEST @ b5e05d2f (29 shots) is waiting on the PC.

## Exact next step
1. When the PC posts `RENDERED @ b5e05d2f` (via the Lead), fetch `gpu/render-creatures-*`, view every out and diff
   PNG, and approve npc_wake_feast plus any drift (llvmpipe metadata, never "?").
2. Merge the Lamp Engine worktree branch, then file a RENDER-REQUEST for creature_lamp_engine and _opened.
3. Then the Avalanche Ram, then the Wakefin (the same pattern), and M3-CRE-622 (Drowner polish) after its PC render.
4. When zone owners add the nodes, re-check Haluna (VillagerLayer, WildlifeLayer) with a PC render.

## Known issues
- **battle-presentation (logged for them):** the struck target's clip isn't held during the hit-stop, because
  BattleClips.play resets speed_scale.
- **ui-menus (logged for them):** add the polyps, the flue moth and the oil slug to the bestiary bake's dark list.
- The wildlife_zone_brine_* shots will drift when act1-chapters' Ch6 kit dressing merges.
- The Mangrove Drowner reads spidery when risen (M3-CRE-622).

## Files touched
game/world/npc/*, game/data/world/npc/**, game/levels/_tests/npc/*, game/data/world/wildlife/*,
game/levels/_tests/wildlife/*, game/creatures/creature_actor.gd, game/creatures/creature_portrait.*,
game/data/creatures/creatures.json, assets_src/creatures/{drownbell,cinder_matron,tower_limpet,undertows_reach,
mangrove_drowner}, assets/creatures/*, assets_src/wildlife/insect, assets/wildlife/insect, tools/validate_npc.py,
tools/validate_creatures.py, tools/validate_data.py (one hook), tests/unit/test_{villager_routines,creature_actor}.gd,
tools/tests/test_npc.py, tests/screenshots/{shots.json,baselines/*}, docs/kb/art/{wildlife.md,creatures/**},
docs/kb/tech/field_npc.md, docs/kb/tasks/M3/M3-CRE-613..623.
