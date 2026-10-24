---
id: M1-RND-23
title: Rendering should-fixes left open on RND-15, RND-16, RND-18 and RND-20 (review-sweep-O)
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-15, M1-RND-16, M1-RND-18, M1-RND-20]
milestone: M1
request-from: "lead"
reviewer: environment
---
## Goal
Review-sweep-O closed RND-15, 16, 18 and 20. This task carries the should-fixes from sweeps J, L and N that no task picked up. File:line references are in those tasks' Review logs.

## Acceptance criteria
- [ ] **RND-15, sweep-J S4 (water_surface.gd:77, :102-118):** make `publishes_water_level` a setter that joins and leaves the publisher group. Then a runtime toggle gets the second-publisher warning, and `_exit_tree` clears the global only when the group becomes empty. test_water_surface.gd:131 toggles it at runtime today.
- [ ] **RND-15, sweep-J S2 (Systems signs off):** SceneRouter names `GlimmerField` and `WaterSurface` directly and scans for a `ShaderPrewarm`. Replace that with a `scene_swapping` signal those statics subscribe to, plus a generic hold API, and list the prewarm wait and the global resets in the router's "Public API" header. Coordinate with M1-RND-22, which also edits scene_router.gd.
- [ ] **RND-15, sweep-N S1 and S2:** measure these inside M1-RND-22's GPU run: batch 12 against batch 2 for Undertow-class scenes (one 1.5 s freeze under the fade, against seven 0.1-0.3 s stutters), and `ResourceLoader.load_threaded_request` for the registry entries. Record the choice there.
- [ ] **RND-16, sweep-N S1 and S2:** add the jitter-frozen bilinear control row to docs/kb/qa/gpu/2026-10-23-rnd-16-aa-override.md and report the ratio, so the "22 % under native" figure isn't partly the upscale's blur. Say in undertow.md that the cost column was measured as plain settings, not through the push API.
- [ ] **RND-18, sweep-N S2 and S3:** note in water.md that from a 10-25 m crane the near water already loses its crests (fade 0.10 / 0.28, much steeper than the 25-30° the task suggested), so the M2 crane shots are judged with that in mind. Add `--sss=#hex` to water_look_probe, so the control run no longer edits Art-owned water_looks.json.
- [ ] **RND-20, sweep-N S3:** record the cross-role edit to Character-owned asha_stage.tscn (the key and rim `shadow_normal_bias` 4.5) in ownership.md's notes or a handoff.
- [ ] **Fixture import file:** `godot --import` generates `tests/fixtures/mote_metrics/glimmer_dusk_signoff_2026-10-23.png.import`, which isn't committed (Lead commit 73886df), so every fresh checkout gets an untracked file. Commit it, the way `tests/fixtures/import/import_probe.glb.import` is committed.

## Review log
