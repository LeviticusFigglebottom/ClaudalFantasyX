# Handoff: integration-qa (claude/hero-integration), 2026-10-29, session 1

Lead: `session_01Bg3iP7cPGyjbX4CyniBahc`. Integration branch: `claude/new-session-mj8c3c`. The live log
(`docs/kb/handoffs/live/hero-integration.md`, section "FROM 2026-10-29") has the details.

## Done
- Merged `claude/new-session-mj8c3c` in twice (at 1e87e60d2 and later). pc-gpu.md clashes took integration's side.
- **Trial merges:** two runs, at ~17:40 (big16 prefold) and ~18:45 (big17 prefold). The clashes are logged with
  resolvers.
  - `tools/dev/trial_merge.py` targets the new integration branch and adds `--integration` and `--prefold <ref>`.
  - `tools/dev/merge_union.py` survives a recursive merge's virtual base (stage 1 with conflict markers): it merges
    against the real merge bases.
- **Act I inventory:** re-audited on the big17 trial tree: 9 items, and 5 with Pell's row (integration-qa 0).
- **M3-HER-1149 Pell row:** walk 1.27 and run 3.13 m/s, measured on pell_lod1. Self-rendered: Pell stands on
  the Ch9 rocks. Liss's box is ticked.
- **Moved to review:**
  - M3-HER-1227 (test);
  - M3-C09-09 (grades, act_card, hold_input ruling);
  - M3-ARC-1324 (sphere and smoke tiers);
  - M3-HER-1158 (ui's fix, verified with the probe).
- **big17's tool reds:**
  - test_post_import is fixed;
  - the freed-cast hit is KNOWN, plus M3-HER-1161 (rendering);
  - test_npc is M3-HER-1162 (creatures).
- **Encounter smoke:** green on big17. The guard now returns Haluna's fights to a real spawn and fails on none.

## In progress
- None half-written. qa_encounters is re-running on this branch (the spawn fallback).

## Exact next step
1. Hourly: `python3 tools/dev/trial_merge.py --prefold lead/gate-big17 --keep --dir <scratch>`. Use whatever batch
   the Lead is gating as the prefold; once it's on integration, drop `--prefold`. Log it under "TRIAL MERGE".
2. When big17 lands on integration:
   - merge it;
   - drop Pell's stale KNOWN capsule rows in `tests/integration/qa_known.json` (corrow, corrow_night × 2, ossa_fen);
   - re-run `python3 tools/placeholder_audit.py --write`;
   - tick M3-HER-1149's last box.
3. Then refresh M3-HER-1130's leak list from the gate's full-suite log (`lead/gate-big17` gate.md) rather than
   running the suite again.

## Known issues
- Fresh-`.godot` imports log TideNotchStyleBox parse errors and a missing SourceSans3-Bold.otf. That's
  first-import order noise; the files exist.
- `refresh_bounce_passes` with a freed root (M3-HER-1124, PC rendering) still appears in the encounter run.

## Files touched
tools/dev/trial_merge.py, tools/dev/merge_union.py, tools/freed_cast_lint.py, tools/tests/test_trial_merge.py,
tools/tests/test_merge_union.py, tools/tests/test_post_import.py, tools/tests/test_dlgc.py,
game/core/graphics_runtime.gd, game/data/hero_motion/hero_motion.json, game/data/dialogue/cues.json,
game/data/dialogue/events.json, tests/unit/test_hero_followers.gd, tests/unit/test_hero_field_actor.gd,
tests/unit/test_graphics_runtime_system_tiers.gd, tests/integration/test_qa_encounters.gd,
docs/kb/qa/act1_final_inventory.md; task files M3-HER-1149/1158/1161/1162/1227, M3-C09-09, M3-C09-201,
M3-ARC-1324; the live log.
