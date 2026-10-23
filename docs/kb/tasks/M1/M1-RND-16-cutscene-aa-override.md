---
id: M1-RND-16
title: Scoped graphics override for storm cutscenes (FSR2 dither workaround)
role: rendering
status: review
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-RND-11]
milestone: M1
reviewer: environment
request-from: "environment"
---
## Goal
M1-RND-11 found that the Undertow body's dither only partly integrates under FSR2 (−36 %, against −85 % under native TAA), because Godot 4.6 has no FSR2 reactive mask for transparent materials (docs/kb/qa/gpu/2026-10-23-rnd-11.md, "Mitigation for storm close-ups on High"). High is the default preset and uses FSR2, and the storm shots are Ch1, Ch8 and Ch20-21. The mitigation is prose only: cinematics needs an API so it does not rediscover this (review-sweep-I on RND-11, S4; filed by M1-RND-15).

## Acceptance criteria
- [x] `GraphicsSettings` scoped override API, e.g. `push_override(owner, {"aa": "taa", "scaling_3d_mode": "fsr1"}) -> handle` / `pop_override(handle)`, applied behind a cut (no mid-shot pipeline switch), restored exactly on pop or when the owner leaves the tree, and never written to the player's settings.cfg
- [x] Nested or overlapping overrides resolve deterministically (last pushed wins; popping restores the one below); tested headless
- [x] Prewarm compiles the override's pipeline variant before the cut (`ShaderPrewarm.match_viewport` sees the overridden state, or the cutscene requests a prewarm for it)
- [x] The Undertow's `temporal_jitter` gate (`UndertowStorm.viewport_is_temporal`) follows the override frame-exactly
- [ ] PC GPU: storm close-up dither crop measured on High with the override (target: within 10 % of native TAA), plus the override's cost
- [x] docs/kb/tech/undertow.md and graphics_settings.md document the API; M2 cinematics tasks reference it

## Notes
- Alternative to weigh: add the storm to an FSR2 reactive mask if a later Godot exposes one (track upstream; ADR if we pin a newer engine).

- 2026-10-23 rendering (worktree-agent-aa764c62452184711), to review (environment):
  - `GraphicsSettings.push_override(owner, values, viewport = null, base = null) -> handle`,
    `pop_override(handle)`, `active_overrides()`, `override_state(extra, base)`. Keys allowed:
    graphics_presets.json `rules.override_keys` (`aa`, `scaling_mode`, `render_scale`, `fsr_sharpness`). The
    override layers on the player's settings (`base`, default user://settings.cfg or the default preset; after
    M1-ARC-15 merges, callers can pass `GraphicsRuntime.settings()`) and is planned like a preset, so the FSR2
    rule still applies. Only viewport properties are written; settings.cfg never is. Applied when pushed: the
    caller pushes at a cut or behind a fade (documented), so no mid-shot switch.
  - Stack: last pushed wins key by key, popping any entry re-applies the rest, the last pop restores a snapshot
    of the viewport exactly, and the owner's `tree_exiting` pops it. A second viewport is refused.
  - Prewarm: `ShaderPrewarm.viewport_state` / `spawn_with_state(scene, parent, GraphicsSettings.override_state(v))`
    makes the stage compile the override's pipeline before the cut; an override pushed before a zone load is seen
    by `match_viewport` already.
  - Undertow: storms join `GraphicsSettings.VIEWPORT_STATE_GROUP`; every push/pop calls
    `on_viewport_state_changed()` -> `_push_dynamic()`, so `temporal_aa` follows in the same frame (tested).
  - tests/unit/test_graphics_override.gd (9 tests). Docs: tech/graphics_settings.md "Scoped overrides",
    tech/undertow.md Gotchas.
  - **Open (PC GPU):** criterion 5, the storm close-up dither crop on High with the override (target within 10 % of
    native TAA) and the override's cost. Needs the RX 9070 XT session (`tools/gpu_bench`, as in RND-11). M2
    cinematics tasks do not exist yet; undertow.md names the Ch1, Ch8 and Ch20-21 shots for them to reference.

## Review log
