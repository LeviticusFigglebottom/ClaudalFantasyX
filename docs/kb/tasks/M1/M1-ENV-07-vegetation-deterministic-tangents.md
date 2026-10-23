---
id: M1-ENV-07
title: Vegetation builds with deterministic tangents (single-threaded, or no exported tangents)
role: environment
status: review
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-06]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-06 found that Blender's threaded tangent export races. At 4 threads, base_body's rebuild hash changed from run to run, and at `--threads 1` it was byte-stable. Another agent's full gate run failed `vegetation` on palm_coconut_b.glb TANGENT data with no asset change, which fits the same race. The gate now rebuilds vegetation at `--threads 1` (blender_builds.json `"threads": 1`), and the committed files match that build. But `assets_src/environments/vegetation/build.py`, run by hand, still uses Blender's default thread count, so a future rebuild can commit a variant the gate rejects.

## Acceptance criteria
- [x] The vegetation build is deterministic whoever runs it. Either document and use `blender --threads 1` for it (a header line in build.py and the PROVENANCE build column), or stop exporting tangents (`export_tangents=False` in veg_common.py, as kit_common.py does; Godot's `ensure_tangents` import setting already generates them), then regenerate and re-approve the affected screenshots.
- [x] `python3 tools/dev/verify_blender_builds.py --job vegetation`, run three times at once, reports `7 identical` every time.
- [x] If tangents are no longer exported, the job's `"threads": 1` in tools/dev/blender_builds.json may go back to the default (the unit test in tools/tests/test_blender_builds.py only requires 1 thread for jobs that export tangents).

## Notes
- Measured in M1-QA-06 (docs/kb/qa/blender_builds.md, "Threads are pinned"). 38 default-thread vegetation rebuilds were all identical here, so the race is rare for these meshes, but base_body shows it is real.
- 2026-10-23 (worktree-agent-a361fe4924e35dfcf):
  - **Choice:** I stopped exporting the tangents, the second route. `veg_common.export_glb` has `export_tangents=False`, and all seven `.glb.import` already carry `meshes/ensure_tangents=true` (import_settings.py), so Godot generates MikkTSpace tangents on import. This removes the race, where a thread flag would only avoid it. The job's `"threads": 1` is removed, so it runs at the default 4.
  - **What changed:** every mesh keeps the same POSITION, NORMAL, UVs, COLOR_0 and indices, and only the TANGENT accessor is gone. beach_vine_patch has fewer vertices (996→914, 606→516) because the exporter no longer splits vertices by tangent, but its triangles are the same. The files are 19–31% smaller (frangipani_a 1.67→1.29 MB).
  - **Determinism:** a build at 1 thread and three concurrent `--job vegetation` runs at 4 threads gave the same 7 hashes, and the job reports `7 identical`.
  - **Shots:** `veg_backlit_fronds` 0.00373, `veg_frangipani_close` 0.00472, `veg_beach_wide` 0.00089 (limit 0.018), plus the Haluna mood shots that place the vegetation (h01 0.00176, h02 0.00160, h03 0.00105, h04 0.00000, h07 0.00075; limit 0.008): **all pass, no re-approval needed**. The Godot suite (1001 tests, including the prewarm tests that load palm/frangipani meshes) passes.
  - **Tests:** test_vegetation now asserts that the committed `.glb` have *no* TANGENT and that every import ensures tangents.
  - Review: rendering (SPEC §12.3, Rendering ↔ Environment).

## Review log
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve.** No blockers.
  - **Checks:** `python3 tools/dev/verify_blender_builds.py --job vegetation`, run 3 times in a row at the default 4 threads: **`7 identical`** every time, rc 0. test_vegetation (part of the 411 tool tests) asserts no TANGENT in the .glb files and `ensure_tangents=true` on every import.
  - **Is dropping tangents safe? Yes, confirmed in Godot.** A headless script loaded each imported vegetation .glb from this worktree's fresh `--import`. **Every surface has `ARRAY_FORMAT_TANGENT`:** beach_vine_patch 2/2, frangipani_a/b 6/6, palm_coconut_a/b/c 6/6 and saltgrass_clumps 4/4. All seven `.glb.import` files have `meshes/ensure_tangents=true`. No game code loads these .glb files at runtime through GLTFDocument (grep), so every use goes through the importer. Godot's MikkTSpace pass is deterministic, so the in-game tangents are stable too.
  - The authors' shot numbers (`veg_*` ≤ 0.0047 against a limit of 0.018, `haluna_*` ≤ 0.0018) are consistent with the attributes being unchanged apart from TANGENT. I did not re-render, because the Lead's full gate covers it.
  - **Nit:** `beach_vine_patch` lost 82 vertices that had been split only by tangent. If any future script indexes those vertices (wind weights by index), it must not assume the old count. Nothing does today.
