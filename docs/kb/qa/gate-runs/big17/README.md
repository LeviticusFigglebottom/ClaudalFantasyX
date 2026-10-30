# GATE lead/gate-big17 @ 1a986abf: results (cloud gate session, 2026-10-29/30)

**Stopped early (ADR 0205, the human's 10-30 directive):** the full-manifest capture no longer blocks a batch.
478 of 612 shots were captured; the other 134 (`not_captured.txt`: mostly the slice cutscene shots, ~10 min each
here, plus the late kit rows, crowd lineup and zone dressing shots) were never rendered. big17 itself was merged into
the integration branch at 96222b30 ahead of the shots, at the human's request.

## For the Lead to view: only `part2/` (81 non-PASS shots)
Part 1 (`out/`, `sheets/`, first published at e49c2ecb, 372 shots) has already been viewed: 187 approved at
d987cc6b, drownbell_flood and battle_arena_terrace rejected and routed. **Don't re-view it.**
- `part2/compare.txt`: the 106 shots captured after e49c2ecb: 81 FAIL (43 no baseline + 38 drift), 25 PASS.
- `part2/out/<id>.png`: the 81 non-PASS captures.
- `part2/sheets/new_NN.jpg` (43 shots, 6 to a sheet) and `part2/sheets/drift_NN.jpg` (38, BASE | OUT | DIFF, 3 to
  a sheet, largest RMSE first).
- `compare.txt` (top level) lists all 478 captured shots, both parts.

## Summary
| Step | Result |
|---|---|
| Build | 8 heads merged (gate.md lists them). One fallout fix: 3 stale PROVENANCE rows re-added by the line union. |
| validate_data, taskboard, gdlint, gdformat, audio, manifest | ok (data 0 errors 0 warnings; manifest 612 shots) |
| Tools suite | 182 units, 1914 tests, **4 failing units, all also red on big16**: test_freed_cast_lint, test_npc, test_post_import, test_screenshots |
| Godot import | clean |
| Godot suite | **3241 run, 5 failed + 1 parse error** (`godot_failures.txt`). All but one also red on big16: test_ch04_zones (8 vs 10 Haluna camera volumes), test_iskarra_city (VigilLights), test_zone_cast (the fisher idles), test_cutscene_vfx_hosts.gd (`CutsceneMotes` is gone). **New in big17:** test_dialogue_box, Pell has a model but no portrait (claude/characters' Pell; needs a portrait render). |
| Boot smoke | no ERROR lines |
| Coverage | report only (the full run is skipped: with the suite red, run_coverage reports no numbers). `--filter=battle`, 811 tests: game/battle 96.57%, game/progression 51.78%, partial by construction. |
| Blender | base `lead/gate-big14` (the last Blender-verified gate): **85 jobs, 78 identical, 7 DIFF, all unchanged since big16** (`blender_diffs.txt`): brine_shoals_kit (env-art-b, M3-RND-1315) and 6 crowd bodies (creatures, M3-CRE-659). |
| Screenshots | 478 of 612 captured: 268 FAIL (86 no baseline + 182 drift), 210 PASS. Two slice shots hit the 600 s per-shot hang limit (slow, not hung). |
