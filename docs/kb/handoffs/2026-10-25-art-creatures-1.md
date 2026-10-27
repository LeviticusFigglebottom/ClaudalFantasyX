# Handoff — art (creatures) — 2026-10-25 #1

Environment `creatures`, branch `claude/creatures` @ 5065b869. Read `docs/kb/handoffs/live/creatures.md` first, from
the section "STATE AT HANDOVER (2026-10-25)" down.

## Done
- 27 Act I creatures, already on the integration branch (big7, big8).
- Since big8, on this branch:
  - M3-CRE-610 villagers alive (FieldNpc, on hero-integration's helpers);
  - M3-CRE-611 ambient wildlife (WildlifeLayer, 4 draw calls, about 0.3 ms);
  - M3-CRE-612 battle polish (hit and idle variety, flier hover so KOs land);
  - the spar_wraith's two phases, phase clip maps and `show_after`;
  - polish passes on the Matron, squall wing and wreck crab;
  - merges of big8 and claude/hero-integration (the Lead's cross-track approval).

## In progress
Nothing running. Triage of four test failures that showed up after the big8 merge has not started.

## Exact next step
Run `godot --headless --path . res://tests/run_tests.tscn -- --filter=post_import` and `-- --filter=battle` on this
branch and on the integration branch (6c6e5514). Fix what is ours; tell the owners about the rest. In the KO-once test,
`wickfry` now has a model. Then capture and compare the creature, battle, npc_stage_field and wildlife_stage shots,
view any change, and write the MERGE-READY line.

## Known issues
- test_post_import (3 LOD tests) and test_battle_ko_once (the primitive foe) fail on the merged tree, not yet triaged.
- Messages to the Lead session were refused (untrusted device); the live log is the channel.
- Minor art: the wreck crab's leg barnacles are faceted; the Matron's yoke cells are even.

## Files touched
assets_src/creatures/**, assets/creatures/**, assets_src/wildlife/**, assets/wildlife/**, game/creatures/**,
game/world/npc/**, game/world/wildlife/**, game/data/creatures/**, game/data/world/{npc,wildlife}/**,
game/data/import/{creatures,wildlife}.json, tools/validate_creatures.py, tools/validate_wildlife.py,
tools/tests/test_creatures.py, tools/tests/test_wildlife.py, tools/dev/creature_lods.gd, tests/unit/test_creature_actor.gd,
tests/unit/test_field_npc.gd, tests/unit/test_wildlife.gd, tests/screenshots/**, assets/PROVENANCE.md,
docs/kb/art/creatures/**, docs/kb/art/wildlife.md, docs/kb/tech/field_npc.md, docs/kb/tasks/M3/M3-CRE-*,
docs/kb/ownership.md, docs/kb/handoffs/live/creatures.md.
