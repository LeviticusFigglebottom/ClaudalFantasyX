# Handoff — art (creatures) — 2026-10-28 #3

Session summary for the creatures track's main session (the coordinator, merging worktree agents' branches into
`claude/creatures`). The live log is docs/kb/handoffs/live/creatures.md.

## Done
- **The Vowbound, all on the creature pipeline and attached through CreatureModels (`"vowbound": true` rows):**
  - Ilun (M3-CRE-638), with an integration test of the real summon path;
  - Kahre (640) and Virel (641), the Act I Vowbound;
  - Nhoa (642), Hesk (643) and Ethren (644), Act II's, with the `vowbound_pending` validator key until Combat adds
    their vowbound.json rows;
  - their Act III foe forms (647): held material sets, `release` clips, and `<id>_held` scenes and rows.
- **The Mangrove Drowner redesign (M3-CRE-622):** no longer a spider; approved on the cloud render 3b0e44b; done.
- **The flat-engine (M3-CRE-637):** approved; its portrait and the Drowner's are committed.
- **M3-CRE-645:** the gallery ray, glass skate and ridge lynx polished (the primitive audit).
- **M3-CRE-100 (cinematics' request):** Haluna's shop villagers moved into VillagerLayer rows with an `actor`
  override. A layer added in its zone's `_ready` builds deferred, so it adopts the shim's villagers and nothing
  doubles.
- **M3-C05-05:** the Cinder Matron's skills play her clips. Notes added that the Ch4–Ch6 creatures are seated.
- **Renders:** the PC render fce2e82 was reviewed and 28 shots approved (battle shots stale after big12, not
  approved). The cloud render 3b0e44b was approved.
- **Act III roster proposal (M3-CRE-646)**, plus design sheets for the Act II Vowbound.
- **Merges:** big12, the integration's docs merges, and Git LFS enabled locally (nothing of ours is over 5 MB).

## In progress
- M3-CRE-648, a worktree agent writing Act III sheets: the Cage frame, wick_crawler, chain_lamp, spire_moth,
  held_shoal and drowned_lantern.

## Exact next step
1. When M3-CRE-648 reports: review the sheets, merge, and push.
2. When the one open RENDER-REQUEST is served (lead/gate-render-creatures-*): view every out, diff and portrait;
   approve with llvmpipe metadata; commit the 26 portraits with PROVENANCE rows, which turns
   test_creature_portraits green.
3. After the Lead confirms the Act III ids: build in act3_roster.md's order (the Cage frame next, with the
   characters track for the founders).

## Known issues
- test_creature_portraits stays red until the portrait bake lands (only unbaked PNGs; the manifest is complete).
- Requests waiting on other tracks:
  - Combat: vowbound.json rows for nhoa, hesk and ethren, and the Ch20 enemies rows;
  - battle-presentation: M3-CRE-639 (the rise and dismiss clips) and the first-call flags;
  - ui: M3-CRE-634, and optional sandbox rows;
  - audio: M3-CRE-633;
  - characters: Moll (M3-CRE-625), the villager clips (M3-CRE-614), and Corran's face under Ethren's veil.
- The rest of the old 101-shot render set is deferred until the PC returns.

## Files touched
assets_src/creatures/{ilun,kahre,virel,nhoa,hesk,ethren,mangrove_drowner,flat_engine,gallery_ray,glass_skate,ridge_lynx,common}/,
assets/creatures/…, game/creatures/…, game/creatures/creature_models.gd, game/creatures/creature_actor.gd,
game/data/creatures/creatures.json, game/data/world/npc/zones/ch02_haluna.json, game/world/npc/villager_layer.gd,
tools/validate_creatures.py, tools/validate_npc.py, tools/portraits/portraits.json, tests/…, docs/kb/art/creatures/…,
docs/kb/tasks/M3/M3-CRE-6{38..48}*, docs/kb/handoffs/live/creatures.md.
