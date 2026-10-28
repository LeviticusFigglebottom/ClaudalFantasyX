# Handoff — art (creatures) — 2026-10-28 #10

The big14 gate fixes. Full detail: the live log docs/kb/handoffs/live/creatures.md, §"big14 gate fixes".

## Done
- Merged `origin/gpu/gate-big14-shots` and the integration branch into `claude/creatures`.
- **Tests:**
  - test_villager_routines and test_crowd_villagers no longer await a frame (the full-suite runner steps none), so the exit crash is gone.
  - The creature and Vowbound tests free what they make.
- **Wake:** the Osu and vendor chat pair is dropped.
- **avalanche_ram:** the build snaps its midline, is byte-identical on every numpy SIMD path, and the rebuilt GLB is committed.
- **cord_moth and nine Act II foes:** they fight on their same-id creatures.json scene (CreatureModels).
- **Portraits:** the six Vowbound and their held forms, with PROVENANCE rows.
- **Haluna:** VillagerLayer builds at once; the shop rows use `attach: child` and `node_name: "Villager"`, so no capsule shows before the first frame and nothing doubles.

## In progress
Nothing.

## Exact next step
1. The Lead merges `claude/creatures` (MERGE-READY in the live log).
2. Then the villager generator continues once M3-CRE-657 (slice-polish: GreyboxZone adds the VillagerLayer) lands.
3. M3-CRE-660 waits on the Lead's answers on pumice_crawler and avalanche_ram scope.

## Known issues
- **kirru_roost.glb (env-art):** request M3-CRE-663.
- **Ossa Fen's `pell` capsule:** Act II, a named person.
- **cord_moth `unravel` has no effect:** battle VFX.
- **Truncated local `.godot/imported` files after a disk-full:** delete them, then re-import.

## Files touched
- Game: game/creatures/creature_models.gd, game/world/npc/villager_layer.gd, game/data/world/npc/zones/ch02_haluna.json.
- Tests:
  - tests/unit/test_creature_{actor,bosses_act1,vfx_anchors,vowbound_held,*_vowbound}.gd
  - tests/unit/test_villager_routines.gd
  - tests/unit/test_crowd_villagers.gd
- Assets: assets_src/creatures/avalanche_ram/build_avalanche_ram.py, assets/creatures/avalanche_ram/avalanche_ram.glb, assets/ui/portraits/creatures/{ilun,kahre,virel,nhoa,hesk,ethren}{,_held}.png, assets/PROVENANCE.md.
- Tasks and logs: docs/kb/tasks/M3/M3-CRE-663-kirru-roost-host-determinism.md, docs/kb/handoffs/live/creatures.md.
