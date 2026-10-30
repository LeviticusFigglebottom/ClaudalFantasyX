# Handoff: creatures, 2026-10-30 (session 11)

**Branch:** claude/creatures (pushed). Integration: claude/new-session-mj8c3c (merged at c789b9a9). Lead: session_01Bg3iP7cPGyjbX4CyniBahc.

## Done
- **The Act I final-quality audit** (the Lead, 10-29 23:10). New tools in tools/creatures/: clip_audit.gd, foot_slip.py, clip_sheet.tscn, wildlife_audit.gd, wildlife_snap.gd and wildlife_apply.py, life_audit.tscn.
  - **Planted feet:** `grounding.pinned` holds planted feet. Applied to the tide crawler, the crab family, the raid hound (its lunge steps its forepaws), the vein sparker, the bottle hermit and the shoal skipper.
  - **KOs:** the vein sparker and the tide crawler now read.
  - **Battle scale:** the ashwing and the sail leech (the leech also hangs lower).
  - **Wildlife:** re-seated on the dressed kits in 10 of 11 zones; fish where the kits brought water; crabs follow the ground (`ground: physics`).
  - Requests: M3-CRE-664 (environment: the causeway's generated file) and M3-CRE-665 (combat: two-foe openings hide the back foe).
- **The big17 test_zone_cast red:** fixed, with a FieldNpc work and storm loop phase.
- **Act II preparation (ADR 0203, docs only):** docs/kb/plan/act2/creatures/ (README plus 15 sheets, `draft: pre-gate`).

## In progress
Nothing.

## Exact next step
1. When the PC reports gpu/act1-qa-3, take the Oil Slug and storm-figure rows first.
2. When `act1-complete` is tagged, work the Act II sheets' "Work at the gate" lists, starting with the ridge lynx's pin and the fen leech, gallery ray and rim crawler reads.

## Known issues
- The battle suite's known three reds.
- Residual slides: the hound's attack 8 cm, the crawler's hit 6 cm, the sparker's hit_b 10 cm.
- Two-foe opening occlusion (M3-CRE-665).

## Files touched
- assets_src/creatures/{common/grounding.py, tide_crawler, reef_crab, raid_hound, vein_sparker, bottle_hermit, shoal_skipper, sail_leech, fen_leech, tower_limpet}/** and their GLBs (plus wallcrab, wreck_crab, root_crab, rim_crawler rebuilt).
- game/creatures/{creature_actor.gd, oil_slug, ashwing, sail_leech}; game/data/creatures/creatures.json.
- game/world/{npc/field_npc.gd, wildlife/wildlife_layer.gd, wildlife/wildlife_crab_beach.gd}; game/data/world/wildlife/*.json; tools/validate_wildlife.py.
- Tests: tests/unit/{test_crowd_villagers, test_creature_actor, test_wildlife, test_zone_cast}.gd; tools/tests/{test_creatures, test_wildlife}.py.
- Docs: docs/kb/art/{creatures/pipeline.md, wildlife.md, creatures/act1/*.md}, docs/kb/plan/act2/creatures/**, the task files M3-CRE-664/665, the live log.
