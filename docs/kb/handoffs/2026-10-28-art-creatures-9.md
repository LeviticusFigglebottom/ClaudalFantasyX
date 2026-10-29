# Handoff — art (creatures) — 2026-10-28 #9

The coordinator session's summary since #3 (the ADR 0041 refocus). Live log: docs/kb/handoffs/live/creatures.md.

## Done
- **ADR 0041 refocus:** the Act II and later creature tasks are blocked (their work kept); the render queue retired; self-rendering adopted.
- **The 20 Act I regular enemies are final in review:**
  - weak points for the flue moth, raid hound and vein sparker (M3-CRE-650);
  - spawn and death VFX anchors, `CreatureActor.vfx_anchor` (M3-CRE-651);
  - all 20 self-rendered and viewed, plus their portraits (M3-CRE-652);
  - the shoal skipper, slag tortoise, sail leech and oil slug rebuilt (M3-CRE-654);
  - the raid hound rebuilt (M3-CRE-655);
  - portraits re-baked and committed.
- **M3-HER-1142's rows:**
  - a creature can stand on a greybox stage (CreatureActor.play_clip takes HeroMotion's blend);
  - the hound's layout line is requested from act1-chapters (M3-CRE-658);
  - the inquisitor is Moll, characters' (M3-CRE-625).
- **Villager runtime:** VillagerLayer adopts a greybox stage actor's model (M3-CRE-656: Kell in Oruvel).
- **Crowd villagers (ADR 0152):**
  - M3-CRE-659: 22 bodies, 56 people in 10 zones.
  - M3-CRE-662: the perceptual skin-clearance metric, and shared clip libraries (34 MB).
- **Merges:** big13, the integration's docs, Git LFS.

## In progress
Nothing running.

## Exact next step
1. When slice-polish lands **M3-CRE-657** (GreyboxZone adds the VillagerLayer):
   - merge it;
   - clear `.godot/imported/crowd_*.glb-*` and re-import;
   - self-render the zone crowd shots and view them;
   - run tools/placeholder_audit.py (on the integration branch) to confirm the generic villagers leave the inventory.
2. When the Lead answers M3-CRE-660 ("pumice_crawler" = scree_crawler?; avalanche_ram in scope?), do that pass and
   re-check the raid hound and slag tortoise on the Lead's re-render.
3. When characters lands M3-CRE-661: regenerate the wrights with line-marks and the brand, and drop the crowd's LOD0
   workaround.

## Known issues
- test_creature_portraits stays red for the paused Act II/III portraits (ui's M3-CRE-634 would limit the test to
  enemies).
- Audio's shutdown cast (life_audio.gd:124) makes capture.sh exit 1 even when every shot is ok.
- Baselines to re-render (the Lead):
  - creature_flue_moth, creature_raid_hound, creature_vein_sparker, creature_shoal_skipper, creature_slag_tortoise,
    creature_sail_leech, creature_oil_slug;
  - battle_boss_intro_inquisitor;
  - the 14 crowd_* shots.

## Files touched
assets_src/creatures/{flue_moth,raid_hound,vein_sparker,shoal_skipper,slag_tortoise,sail_leech,oil_slug,…},
assets_src/crowd/**, assets/crowd/**, game/creatures/creature_actor.gd, game/world/npc/**,
game/data/creatures/creatures.json, game/data/world/npc/{crowd.json,zones/*}, tools/validate_{creatures,npc}.py,
tools/tests/test_{creatures,npc}.py, tests/unit/test_{creature_vfx_anchors,villager_routines}.gd,
assets/ui/portraits/creatures/*, docs/kb/decisions/0152-crowd-villagers.md, docs/kb/tasks/M3/M3-CRE-65*–66*.
