---
id: M1-ARC-17
title: Engine fix for the Godot 4.6.3 RenderingDevice vertex-format race (gate abort, M1-QA-10)
role: architect
status: done
owner_session: ""
depends_on: [M1-QA-10]
milestone: M1
request-from: "qa"
---
## Goal
M1-QA-10 traced the intermittent `asha_face_stylized_compare` gate failure to a data race inside the pinned engine. No project code can remove it. Pick and land an engine-side fix, and write the ADR it needs (ADR 0001/0011 pin the engine).

**The race** (Godot 4.6.3-stable, `servers/rendering/rendering_device.cpp`):
- `render_pipeline_create()` runs on WorkerThreadPool threads (background and ubershader pipeline compiles). It takes the RD lock only around the framebuffer-format lookup. It then reads `vertex_formats` **outside the lock** with `has()` and the **non-const `operator[]`** (lines 4165 to 4167).
- `vertex_format_create()` runs on the render thread whenever a surface needs a new vertex layout. It inserts into the same `HashMap` under the lock, but the reader doesn't hold it.
- If the insert rehashes (or robin-hood-shifts) the table between the reader's `has()` and its `operator[]`, the lookup misses. `operator[]` then **inserts a default `VertexDescriptionCache`** with no attributes and `driver_id` 0. Validation finds no attribute at all, so the first missing location is 0: `Shader vertex input location (0) not provided in vertex input description for pipeline creation`. The render thread had waited on that ubershader pipeline, so `PipelineHashMapRD::get_pipeline` stores `RID()` for it, and at exit `clear_pipelines()` frees it: `Attempted to free invalid ID: 0`. The bogus entry stays in the map, and at RD shutdown `vertex_format_free()` dereferences its null driver id (SIGSEGV in `RenderingDeviceDriverVulkan::vertex_format_free`). That is the `Aborted`.
- Upstream `4.7` and `master` take `_THREAD_SAFE_METHOD_` around a `vertex_formats.getptr()` lookup (no default insert). The `4.6` branch and `4.6.3-stable` don't have that change.

## Acceptance criteria
- [ ] Choose one, in an ADR: (a) move to 4.7.x once a build is reachable by the gate (ADR 0011's condition); (b) build 4.6.3 locally with the one-hunk backport below (a reproducible patch under `tools/dev/`, the same Debian source, and re-approved baselines only if pixels move); or (c) accept the risk and treat a named `CAPTURE PROCESS EXIT` on a shot whose PNG compares clean as a re-run (`docs/kb/qa/screenshots.md`, "Engine race").
- [ ] Whichever you pick (other than c), `tools/dev/rd_vertex_format_race/run.sh forced` reports "race NOT reproduced" on the new engine build. Its breakpoint line numbers are 4.6.3's, so update them for a patched or newer source.

## Notes
- Backport hunk (upstream form):
  ```cpp
  const VertexDescriptionCache *vd;
  {
      _THREAD_SAFE_METHOD_
      vd = vertex_formats.getptr(p_vertex_format);
  }
  ERR_FAIL_NULL_V(vd, RID());
  driver_vertex_format = vd->driver_id;
  // ... then validate against vd->vertex_formats
  ```
- Rate seen by QA-10 on lavapipe: 1 failure in the Lead's batch-3 gate (stylized_compare after the whole manifest), and 0 in 90 asha processes under load (45 of them stylized_compare). The window is a few hundred nanoseconds per pipeline. The stylized compare is the most exposed shot because its two figures create the most vertex layouts and pipelines in the same frames.
- It isn't specific to lavapipe or to capture. Any 4.6.3 build can hit it on real GPUs at the first sight of a material/mesh pairing, so the game can also hit it.

## Review log
- 2026-10-24 review-sweep-R (lead): **done (decision recorded).** Criterion 1: the ADR 0032 update (aeb0875) chooses option (c): accept the rare risk until the 4.7 port, re-run a named `CAPTURE PROCESS EXIT` shot once, and never re-approve its baseline. That matches screenshots.md "Engine race". Criterion 2 applies only to (a) or (b), so it doesn't apply here. The port task should re-run `tools/dev/rd_vertex_format_race/run.sh forced` on 4.7.x (with its line numbers updated) as proof that the fix landed.
