---
id: M1-QA-06
title: Capture setup and Blender gate hardening (review-sweep-I)
role: qa
status: done
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
- 2026-10-23 character (review-sweep-J, fresh reviewer): **approve with should-fixes.** No blockers.
  - **What I read:**
    - the task and handoff qa-2;
    - the commits 8ff8162 (capture_setup.gd and its test), f1892f2 (verify_blender_builds.py, blender_builds.json, test_blender_builds.py, blender_builds.md) and 30a12cd (godot_log_check.py, its test, ci_local.sh).
  - **Checks:**
    - `verify_blender_builds.py --coverage-only`: 0 uncovered.
    - Tool tests: 382 OK (test_blender_builds, test_godot_log_check).
    - Godot import ×2 in my own XDG_DATA_HOME, then `godot_log_check.py import`: exit 0.
    - `--filter=capture_setup`: 9 run, 0 failed.
    - Every targeted test log I ran passed `godot_log_check.py tests`.
  - **What passes:**
    - **The hold order.** `frame_pre_draw` comes after SceneTree process, so after Tweens and AnimationPlayers, and the transforms are flushed. The hook is connected only for a shot with a setup (capture_setup.gd:86).
    - **The globals limitation** is documented as a rule.
    - **The signature kinds**, with "NEW failure signature" on anything else.
    - **The coverage check**, which also runs without Blender.
    - **Asha's texture chain** is in the job: 44 files.
    - **Pinned threads**, with a test that a tangent-exporting job runs at 1 thread.
    - **The narrowed Parse Error check.** The import log stays strict.
  - **Should-fix:**
    - **S1 (a mismatch signature that cannot see a regression).** base_body's `expected_failure` is pinned by accessor *names* only (blender_builds.json:17-22; compared at verify_blender_builds.py:383-399). Any further change inside NORMAL, POSITION, TANGENT or indices of those three files still reads KNOWN, even a bb_donor regression that moves the base bodies by centimetres.
      - This matters now: M1-CHR-04 has just edited bb_donor.py and bb_params.py on the claim that "the defaults leave V untouched". This gate could not have caught that claim being false.
      - With `--threads 1` base_body is byte-stable (your own result), so the reason given against hashes is gone. Record each rebuilt file's sha256, or a max-|Δ| bound for POSITION, in `differs`, and fail on a change.
    - **S2 (thread pin is unproven below 4 vCPUs).** "Pinned at 4, so the result never depends on the host's CPU count" is asserted (blender_builds.json `_threads`), but it was verified only on this 4-vCPU box. Run `--job asha` once with `taskset -c 0,1`, or note it as unverified in blender_builds.md.
  - **Nits:**
    - `GD_PATH` (godot_log_check.py:26) would count a torn-`.tres` Parse Error whose message happens to quote a `.gd` path. That is rare and fails safe.
    - `frame_pre_draw` ordering assumes the default rendering thread model. Say so in the CaptureSetup header.
    - `_tracked()` counts untracked, non-ignored `.glb` files, so a developer's WIP export fails the local gate. That is intended, but blender_builds.md should say how to exempt scratch files (or to keep them outside assets/).
- 2026-10-23 lead: closing on review-sweep-J approve; S1/S2 are in M1-NIT-01.
