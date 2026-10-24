---
id: M2-RND-06
title: Rendering nits from review-sweep-Q (battle VFX safety test bounds, Undertow open items, orphan fixture import)
role: rendering
status: doing
owner_session: "worktree-agent-a30d6e9e3e395d6ec"
reviewer: environment
depends_on: [M2-RND-01, M2-RND-03]
milestone: M2
request-from: "lead"
---
## Goal
Small findings from review-sweep-Q on M2-RND-01, M2-RND-03 and M1-RND-23. None of them blocks.

## Acceptance criteria
- [ ] **Battle VFX safety test (RND-03).** `test_battle_vfx.gd::test_flashes_are_capped_and_spaced` accepts `flash_max_alpha <= 0.35` and `flash_min_interval_s >= 0.34`. The documented contract (effects.json `safety.doc`, battle_vfx.md) is **0.3 and 0.5 s**, so a data edit to 0.35 alpha or 0.34 s would pass. Assert the contract values. Also check that every `kind: flash` effect's own `alpha` is within the cap. Read the HUD's layer from `battle_sandbox.tscn`'s `HudLayer` instead of hard-coding `< 1`.
- [ ] **Undertow open items (RND-01).** undertow.md § Compute body still says "a quarter-resolution tier for min-spec (RTX 3060 projection ~7.4 ms on Day High)". That predates High's `body_scale` 0.35, after which the task says 2.0–2.4 ms projected. Correct the line and say which number is current. Keep the two open items, the compute body's own reprojected history and a min-spec quarter-res tier, in undertow.md's open list with this task's id, or measure them.
- [ ] **Orphan import (RND-23).** `tests/fixtures/mote_metrics/.gdignore` stops Godot from importing the fixture, but `glimmer_dusk_signoff_2026-10-23.png.import` is committed again (it came back with bde9795 on the m2-slice merge). Delete it, so the fixture has either a `.gdignore` or an `.import`, not both.

## Review log
