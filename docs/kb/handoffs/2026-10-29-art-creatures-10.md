# Handoff: creatures, 2026-10-29 (session 10)

**Branch:** claude/creatures (pushed). Integration: claude/new-session-mj8c3c. Lead: session_01Bg3iP7cPGyjbX4CyniBahc.

## Done
- Merged the integration branch, plus claude/characters @ 3346484b (the head big17 carries; the crowd generator needs its new villager faces).
- **big17 gate reds:**
  - test_npc: re-ran gen_crowd; crowd_girl_teen was rebuilt.
  - test_post_import (tools): KINDS now includes `crowd`.
  - Both confirmed on lead/gate-big17 in a scratch worktree.
  - villager_shopkeeper_front was self-rendered and viewed (NO BASE: the Lead approves it).
- **M3-HER-1142:** Corrow's storm figure is a crowd body drawn as a cyan silhouette (VillagerLayer `body`/`silhouette`/`tuning` rows, NpcSilhouette), with new shots npc_corrow_storm_figure(_near).
- **GPU QA row 40:** the Oil Slug in battle (flank-on, 1.3×, a lighter back, LampGlow); CreatureActor fades lights on KO; new shot creature_oil_slug_battle.
- **Primitive pass:** the tide crawler and the tower limpet are rebuilt (the rim crawler is rebuilt from the tide crawler). Portraits re-baked.

## In progress
Nothing.

## Exact next step
When the Lead merges this, merge the integration branch back in. Then:
- if slice-polish lands M3-CRE-657, self-render crowd_zone_corrow and npc_corrow_storm_figure in the real game path;
- take any new GPU QA rows for creatures.

## Known issues
- The battle suite's 3 known reds (not ours).
- The Oil Slug's flank stays darkish under its crest on lavapipe: the real-GPU recheck is PC-QUEUE.

## Files touched
- Crowd: assets_src/crowd/params/crowd_girl_teen.json, assets/crowd/crowd_girl_teen/**, assets/crowd/clips/crowd_child_clips.tres.
- NPC: game/world/npc/{field_npc.gd, villager_layer.gd, npc_silhouette.gd, npc_silhouette.gdshader}, game/data/world/npc/zones/ch08_corrow.json, tools/validate_npc.py.
- Creatures: game/creatures/{creature_actor.gd, oil_slug/oil_slug_battle.tscn}, game/data/creatures/creatures.json; assets_src/creatures/{oil_slug, tide_crawler, tower_limpet}/** and their assets/ (plus rim_crawler); assets/ui/portraits/creatures/{oil_slug, tide_crawler, tower_limpet}.png.
- Shots: game/levels/_tests/creatures/shots/battle_oil_slug.tscn, game/levels/_tests/npc/{corrow_storm_figure.tscn, haluna_villagers.gd}, tests/screenshots/shots.json.
- Tests: tests/unit/{test_crowd_villagers.gd, test_creature_actor.gd}, tools/tests/test_post_import.py.
- Docs: docs/kb/tech/field_npc.md, docs/kb/art/creatures/act1/{oil_slug, tower_limpet}.md, the M3-HER-1142 task file, assets/PROVENANCE.md (one stale row dropped).
