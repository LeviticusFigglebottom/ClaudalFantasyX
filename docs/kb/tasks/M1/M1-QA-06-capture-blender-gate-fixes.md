---
id: M1-QA-06
title: Capture setup and Blender gate hardening (review-sweep-I)
role: qa
status: review
owner_session: "worktree-agent-ae77f8e225d2b48a3"
depends_on: [M1-QA-04, M1-QA-02]
milestone: M1
request-from: "character"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [x] Held capture values win over Tweens (apply after the tween step, or pause tweens) (capture_setup.gd ~:103-120)
- [x] Globals restore to the previous live value where possible, or the limitation is documented in the shot schema
- [x] A known-failure job still fails on a NEW failure signature (verify_blender_builds.py ~:371-386)
- [x] A new .glb or Blender script not covered by any job fails the gate
- [x] Asha's texture chain is covered or explicitly listed as out of scope
- [x] (Lead, added 2026-10-23) The vegetation job's TANGENT nondeterminism (palm_coconut_b.glb failed in another agent's full run with no asset change) is investigated under load, and the tangents are made deterministic or the tangent tolerance is applied consistently to every job, with the choice documented
- [x] (Lead, added 2026-10-23) ci_local.sh's "Parse Error" check matches only real GDScript parse errors (not Godot's message for a deliberately torn text .tres in a test), with a test

## Notes
- **Reviewer: character** (the Blender jobs are character's assets; the capture half was rendering's ask in QA-04).
- **Capture, S1 (hold order).** `CaptureSetup.pre_draw()` runs on `RenderingServer.frame_pre_draw`, after the SceneTree's Tweens, timers, physics and every AnimationPlayer callback mode, and re-applies the hold there. For each held node it also calls `Node3D.force_update_transform()` on the node and its subtree: the SceneTree would otherwise push a held transform to the renderer only next frame, after that frame's Tween wrote over it again. The `_process` hold stays. The hook is connected only while a shot with a non-empty setup runs, and `end()` disconnects it, so the 58 setup-free shots run exactly as before.
- **Capture, S2 (globals).** Godot cannot read a live global outside the editor, so restoring "the previous live value" is not possible. The limitation and the rule ("a capture scene must not rely on a global inherited from an earlier shot; set it in `_ready` or in `setup.globals`") are in the CaptureSetup header (the schema) and in qa/screenshots.md "Restore".
- **Capture nits:** the unsupported value types are listed (Transform3D, Basis, Rect2...: set components instead), and `time_scale: 0` freezes physics time is documented.
- **Blender, S1 (signatures).** `expected_failure` now needs a `kind`:
  - `build_error` + `log_contains`: shader_test's must hold `ValueError: the value returned by the 'key' function is not a number`.
  - `mismatch` + `differs` {path: [accessors]}: base_body's three `.glb` must differ in exactly `NORMAL`, `POSITION`, `TANGENT` and `indices`. The new `glb_differences` lists every differing accessor, not only the first kind as `compare_glb` does. The old report said POSITION only; the full diff shows all four.
  - Any other failure (a crash of a mismatch job, a timeout, a new file or accessor, one that stopped differing) prints `NEW failure signature` and fails. Hashes would not work as a signature: before threads were pinned (Lead addition 1, below), base_body's rebuild hash changed run to run, and this session's runs show it (athletic `cbcee8…`, then `4523ba…`).
- **Blender, S2 (coverage).** `coverage_errors()` runs before any build and needs no Blender. Every `.glb` under assets/ that is tracked (or untracked and not ignored) must match a job's outputs, and every `assets_src/**/*.py` that imports `bpy`, `bmesh` or `mathutils` must match a job's sources, unless `coverage_exempt` lists it with a why (empty today). It fails as `BLENDER UNCOVERED`, even when Blender is missing (exit 1, not the SKIP code 3). `--coverage-only` runs just this check, and `CoverageTest` runs it on the repo in the tool tests.
- **Blender, S3 (Asha's texture chain): covered.** Runs can now start with `{python}`. The asha job is now Blender `build_asha.py --bake-dir {scratch}/asha_bake`, then `asha_textures.py --bake-dir {scratch}/asha_bake`, then `write_materials.py`, and it verifies 44 files: 2 `.glb`, 23 `textures/*.png`, 19 `materials/*.tres`. **All are byte-identical.** The cost: asha takes ~227 s instead of 45 s, and only when its (or base_body's, or the donor's) sources or outputs change. Still out of scope, as listed in blender_builds.md: the non-Blender texture scripts of the kit, vegetation and shader test, the Undertow bake, and audio.
- **Blender nits:** `HYMN_BLENDER_REQUIRED=1` makes ci_local fail instead of SKIP (for the Lead's merge run). The `copy_into_sandbox` = assets_src limit is documented. I did not edit handoff qa-1's "RND-12": handoffs are history.
- **Not touched:** `assets_src/characters/asha/` (another worktree is rebuilding Asha). Heads-up for that work: the asha job now also verifies the textures and materials, so a rebuild must commit them together with the `.glb`.
- **Lead addition 1: tangent nondeterminism. Decision: deterministic builds (pinned threads), not tolerance.**
  - *Could not reproduce the vegetation flake:* 38 rebuilds at default threads were all `7 identical`: 6 at once, then 4 rounds of 8 at once (load up to ~13 on 4 CPUs).
  - *base_body shows the mechanism:* at default (4) threads its rebuild hash changed run to run (athletic `cbcee8…`/`4523ba…`, heavy `58142e…`/`06cf15…`). At `--threads 1`, 3 concurrent runs (and 3 more later) were byte-identical. This was the "tangent wobble" the 1e-3 TANGENT tolerance hid. Vegetation exports tangents the same way (`export_tangents=True` in veg_common.py), so the palm failure is most likely the same race. The Haluna kit already stopped exporting tangents for this reason (kit_common.py:512).
  - *But a global `--threads 1` is wrong:* Asha at 1 thread differs in 3 files (`asha_body_normal`, `_orm`, `_skinmask`; her bake depends on the thread count, stable at a fixed count), and her committed files match 4 threads.
  - *So:* every Blender run gets `--threads N`. It is `"threads": 1` for the jobs that export tangents (base_body, vegetation) and `default_threads: 4` for the rest, so the result never depends on the host's CPU count (a 2- or 8-vCPU runner). base_body's TANGENT tolerance is removed, and no job has one. Tests enforce both rules: a tangent-exporting job must run at 1 thread, and no job may carry a tolerance.
  - *Verified:* `--all` with pinned threads gives 5 jobs, 0 failed, 0 uncovered, 292 s, with 3 concurrent base_body + vegetation rebuilds alongside it. All 4 base_body/vegetation rebuilds were byte-identical to each other, and vegetation matches its committed files.
  - *Owners:* requests **M1-ENV-07** (vegetation: `--threads 1`, or drop exported tangents) and **M1-CHR-06** (base_body `--threads 1`, Asha `--threads 4` in their build scripts). Docs: blender_builds.md "Threads are pinned".
- **Lead addition 2: the "Parse Error" check.** Godot 4.6.3's own output, from a probe project in the scratchpad:
  - A torn text resource prints `ERROR: res://torn.tres:6 - Parse Error: Expected ','.`
  - A GDScript error prints `SCRIPT ERROR: Parse Error: …`, then `at: GDScript::reload (res://….gd:3)`, then `ERROR: Failed to load script "res://….gd" with error "Parse error".`
  - New `tools/dev/godot_log_check.py`. In `tests` mode it counts `SCRIPT ERROR`, `Failed to load script`, and a `Parse Error` on a line that names a `.gd` file (not `.gdshader`). In `import` mode it is as strict as before, because a torn resource in the repository is a real import error.
  - ci_local.sh uses it for both logs. Tests: `tools/tests/test_godot_log_check.py` (7, using the captured lines). On the real probe logs, the torn `.tres` alone exits 0, and torn `.tres` + broken `.gd` exits 1.
- Tests: `tools/tests/test_blender_builds.py` 12 → 24; `tests/unit/test_capture_setup.gd` +2 (a Tween stepped after the hold, then `pre_draw`; hook lifetime).
- Docs: qa/blender_builds.md, qa/screenshots.md "Per-shot setup".

## Review log
