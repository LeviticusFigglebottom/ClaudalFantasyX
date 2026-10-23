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
- 2026-10-23 environment (review-sweep-L, fresh reviewer): **interim approve of the API; stays in `review` until criterion 5 (the PC GPU measurement) lands.** No blockers in the code.
  - **What I read:** `git show` a2a947b: graphics_settings.gd:362-497, shader_prewarm.gd, undertow_storm.gd, graphics_presets.json `rules.override_keys`, and test_graphics_override.gd.
  - **Checks:** Godot `--filter=graphics_override` 9/0 failed and `--filter=graphics_settings` 24/0.
  - **Criteria 1–4 and 6 hold:**
    - The stack is last-wins key by key, and popping any entry re-plans the rest.
    - The last pop restores a snapshot of the six viewport properties.
    - The owner's `tree_exiting` pops its own entry, and a second viewport is refused.
    - settings.cfg is never written.
    - Storm listeners are told in the same call, so `temporal_aa` follows frame-exactly.
  - **Should-fix:**
    - **S1: `_override_settings` is replaced by every push** (graphics_settings.gd:401). A second push with a different `base` re-bases the overrides already active, so the first owner's layer changes silently. Keep the first push's base for the stack's lifetime, or refuse a different one, and test it.
    - **S2: `tree_exiting` fires on a reparent too**, not only on free. An owner moved under a new parent mid-cutscene loses its override at once. Document that the owner must be a node that stays put (the sequencer), or listen to `tree_exited` plus `is_queued_for_deletion`.
    - **S3: `override_state()` with no base reads user://settings.cfg from disk on every call** (:472-477), including every pop and push. That's cheap, but pass `GraphicsRuntime.settings()` once M1-ARC-15 is in, as the handoff says. Track it on the M2 cinematics task.
  - **Still open:** criterion 5, the storm close-up dither crop on High with `{aa: taa, scaling_mode: fsr}` against native TAA (target within 10%), plus the override's cost, on the RX 9070 XT. Until that's measured, the workaround is unproven on the hardware it exists for.
