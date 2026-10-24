---
id: M1-QA-10
title: Intermittent lavapipe pipeline-creation error and abort at exit in the asha_face_stylized_compare capture
role: qa
status: done
owner_session: "agent-a2c65f9a3e5a1acdb"
depends_on: []
milestone: M1
request-from: "lead"
---
## Goal
In the Lead's batch-3 full gate (lead/batch3 at 9180bc3+, 2026-10-24), the `asha_face_stylized_compare` capture process:
- logged `Shader vertex input location (0) not provided in vertex input description for pipeline creation` and `Condition "pipeline.is_null()" is true` (scene_shader_forward_clustered.cpp:502);
- still wrote its shot (CAPTURE ok, and it compares at the baseline);
- then printed `Attempted to free invalid ID: 0` and **Aborted** at exit.

That made `capture.sh` exit non-zero, so `ci_local.sh` stopped before the compare. The shot did not fail in the earlier full gates (ci36, batch 2), and two isolated re-runs of the shot passed cleanly. That points to an intermittent fault, but "flake" is not a root cause.

## Acceptance criteria
- [x] Reproduce it: loop the single shot (and the full asha_* block in manifest order) on lavapipe under load, say 20 runs, and record the rate.
- [x] Find the material or mesh whose shader variant lacks vertex input 0. Likely candidates are the M1-RND-24 additive mouth-bounce pass (`character_mouth_bounce.gdshader`, attached by `CharacterShaderTiers.apply_to_tree` to per-instance copies) on the stylized-compare figures, or a material whose mesh has no vertex attributes. Fix the cause; don't suppress the error. *(No material or mesh is involved. The cause is an engine race; the engine fix is requested as M1-ARC-17.)*
- [x] capture.sh: say which shot's process exited non-zero, so a gate failure names it.
- [x] No baseline changes.

## Evidence
- Log: the Lead's scratch `b3-gate/ci/hymn_capture.log`, around the stylized_compare entry. The error came before `CAPTURE ok`, and the abort after it.

## Notes (qa, agent-a2c65f9a3e5a1acdb, 2026-10-24; reviewer: lead)
- **Repro rate:** 0 failures in 90 lavapipe processes, with LP_NUM_THREADS=2, niced, and the load average at 2.5 to 6 while other agents ran. That was 20 runs of the shot with a warm `user://` (shader and PSO cache), 20 with a cold one, and the 10-shot asha block in manifest order 5 times with a fresh `user://` per block (50 processes). The only hit on record is the Lead's batch-3 full gate.
- **Root cause:** a data race in Godot 4.6.3's `RenderingDevice::render_pipeline_create()` (rendering_device.cpp:4165 to 4167). Pipeline compiles on WorkerThreadPool threads read `vertex_formats` outside the RD lock, through `has()` and then the non-const `operator[]`. Meanwhile the render thread's `vertex_format_create()` inserts a new layout under the lock. A lookup during a rehash misses, so `operator[]` default-inserts an empty `VertexDescriptionCache`. Validation then finds no attribute at all, and location 0 is the first one it reports. That waited ubershader pipeline stays `RID()` in `PipelineHashMapRD`, which gives `free invalid ID: 0` at exit. The bogus entry's null driver id makes `vertex_format_free()` crash at RD shutdown, which gives `Aborted`. Upstream 4.7 and master take the lock around `getptr()`; the 4.6 branch doesn't. The mouth-bounce pass, the per-instance copies and the meshes are not involved. The shot is just the most exposed, because two figures create the most new layouts and pipelines in the same frames.
- **Proof:** `tools/dev/rd_vertex_format_race/run.sh forced` uses the Ubuntu debuginfod symbols for the pinned build. It parks the worker after `has()`, runs the main thread into the `vertex_formats` rehash (`_size` = 0), and then resumes the worker. The result is the exact gate message (`i` = 0, empty attribute vector), then SIGSEGV in `RenderingDeviceDriverVulkan::vertex_format_free` at RD shutdown. The same run without the forced interleaving (`plain`) is clean.
- **Fix:** an engine fix is the only real one. M1-ARC-17 (architect) chooses between 4.7, a 4.6.3 backport build and accepting the risk, and writes the ADR. Here, `capture.sh` now names the shot (`CAPTURE PROCESS EXIT <rc>: <id>` and a closing list), and `docs/kb/qa/screenshots.md` ("Engine race") says what a gate does when it hits.
- **Gate:** `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=<the 10 asha_* shots> tools/ci_local.sh` exit 0. validate_data 0/0, tools unittests 495 OK, taskboard OK, gdlint and gdformat clean, Godot tests 1432/0 failed (this covers character_shading and shader_prewarm), coverage OK. The asha RMSEs vs baselines match the Lead's batch-3 gate value for value: front 0.00052, q34 0.00033, profile 0.00057, face_neutral 0.00001, face_smile 0.00001, face_grief 0.00000, sleeve_s0 0.00010, sleeve_s4 0.00010, extreme_pose 0.00029, stylized_compare 0.00003. No shader, scene or asset changed, so no rhen_* shot can move, and none was run.

## Review log
- 2026-10-24 review-sweep-R (lead): **approve-with-fixes.** A rigorous root cause. 90 processes under load gave no hit, and the report doesn't call it a flake. The race is traced to `render_pipeline_create()` reading `vertex_formats` unlocked (`has()` then the non-const `operator[]` default-inserts an empty layout), which accounts for each line of the signature: location 0, `free invalid ID: 0` from the RID() pipeline, and the SIGSEGV in `vertex_format_free` at shutdown. The gdb repro (`tools/dev/rd_vertex_format_race/run.sh forced`, with `.gdignore`'d project, pinned build-id symbols, and scheduler-locked interleaving) reproduces the exact message; `plain` is clean. It shows the race is real and matches; it can't prove the batch-3 hit was this race, but no other cause fits, and the docs say "any other error is not this race". `capture.sh` names the shot and keeps its exit codes. screenshots.md "Engine race" gives a re-run-once rule and says never to re-approve. No baselines changed. **M1-ARC-17:** the Lead's choice (c) in the ADR 0032 update is one of the task's options, and its second criterion applies only to (a)/(b), so ARC-17 is closed with this sweep. **Fix (M2-NIT-04):** in `HYMN_CAPTURE_SHARED=1` mode, capture.sh adds to the closing list but writes no `CAPTURE PROCESS EXIT` log line, so the documented signature is missing from the log in that mode.
