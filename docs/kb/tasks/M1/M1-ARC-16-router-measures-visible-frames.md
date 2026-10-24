---
id: M1-ARC-16
title: SceneRouter measures ADR 0029's two budgets (hidden frames under the fade, the first 60 visible frames)
role: architect
status: todo
owner_session: ""
reviewer: rendering
depends_on: [M1-RND-22]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q accepted ADR 0029, which makes the 50 ms limit apply to visible frames, among them "the first 60 frames after any fade lifts". Hidden frames get a 1 s limit. The ADR says "the router can measure it (its frame_ms after the fade)", but `SceneRouter._swap` measures `MEASURE_FRAMES` (4) frames right after `change_scene_to_node`, while the screen is still opaque (`_fade_to(0.0)` runs after `_swap`). So:
- `swap_measured` / `last_swap_stats` measure hidden frames, and `_record` warns "over the 50 ms budget" for them, which ADR 0029 no longer calls a hitch;
- nothing measures the visible frames the ADR budgets.

## Acceptance criteria
- [ ] Keep the hidden-frame measurement, but judge it against a hidden-frame budget (1 s, as a named constant). Its warning text names that budget.
- [ ] Measure the first `VISIBLE_MEASURE_FRAMES` (60) frames after the fade starts to lift and the first after it ends, against `SWAP_BUDGET_MS` (50). Record them in the stats (for example `visible_frame_ms`, `max_visible_frame_ms`, `visible_over_budget`) and warn over budget.
- [ ] Tests in test_scene_router_swap.gd for both windows, using an injected clock or frame times, the way `frame0_start` is tested.
- [ ] graphics_settings.md or architecture.md documents the two stats. The tools that read `max_frame_ms` (prewarm_bench, gpu_bench) say which window they report.

## Notes
- The SPEC §4.2 wording itself is the Lead's edit (ADR 0029, accepted by sweep-Q), with a SPEC version note.

## Review log
