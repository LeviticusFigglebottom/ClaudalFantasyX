# Handoff — environment — 2026-10-23 #1

## Done
- M1-ENV-01 reworked on the review-sweep-F request-changes. It is now `status: review`, reviewers Rendering + Art Director.
  - **B1 sky:** `env_sky_cumulus` adaptive march, no stipple, no streaks, no rings. The undersides are blue
    and the lit tops reach `cumulus_lit` +1. `background_energy` 1.5 brightens the visible sky only.
  - **S1:** both fogs removed from `haluna_noon_environment.tres`.
  - **S2:** chapel lime-wash (`kit_whitewash`) at the albedo ceiling, on a smooth base.
  - **S3:** H03 reframed, red 16.4% → 5.2%.
  - **S4:** banyan bark gain, so the roots read L 0.23 → 0.42.
  - **S5:** H01 re-staged (120 m, 8 m), plus along-shore shelf variation.
  - **S6:** weathered timber tint, nets turned to the lens, switched to alpha scissor (the sea was drawing
    over the blended net), and given thicker tannin twine.
- New tool `tools/screenshots/palette_check.py` (`coverage`, `region` and `check`) and the checks in
  `tests/screenshots/palette_checks.json`. `tools/tests/test_palette_check.py` runs them on the committed
  baselines.
- Merged `claude/new-session-mj8c3c` (water M1-RND-08, M1-RND-09, the ENV-04 shrine) before approving. The
  five `haluna_h0*` baselines were re-approved once. The before/after table and the reasons are in the task notes.

## In progress
- Nothing. Two haluna.md proposals wait for the Art Director: the H01 re-stage and dropping "backlit" from
  H04. They're in haluna.md Revisions.

## Exact next step
- Reviewers: read the five baselines and the task-note table, then run
  `python3 tools/screenshots/palette_check.py check`. If the AD rejects the H01 re-stage, revert
  `ShotH01` in `haluna_mood.tscn` to (180, 6.15, -5) → (0, 29, -8), re-measure the H01 rects in
  `palette_checks.json`, and re-approve H01.

## Known issues
- The cumulus is a mood-test sky. The cells are soft and a little airbrushed at 960×540; the signature
  sky is Rendering's.
- `kit_canopy_bark` tint values are above 1 (a gain over the shared frangipani bark texture). A proper
  banyan bark texture belongs to the vegetation follow-up (M1-ENV-03).
- The timber tint applies to all kit timber, so H02's eaves and posts are slightly darker too.
- The H01 surf is better but is still a fairly continuous wash. Real breaking-surf variation needs
  water-shader work (Rendering).

## Files touched
- game/shaders/environment/env_sky_cumulus.gdshader
- game/levels/_tests/haluna_mood/{haluna_noon_environment.tres, haluna_mood.tscn, haluna_layout.json, haluna_terrain.gd, README.md}
- assets_src/environments/kits/haluna/{materials.py, kit_textures.py}
- assets/environments/kits/haluna/materials/{kit_whitewash, kit_timber, kit_canopy_bark, kit_net}.tres, textures/net_albedo.png
- tools/screenshots/palette_check.py, tools/tests/test_palette_check.py, tests/screenshots/palette_checks.json
- tests/screenshots/baselines/haluna_h0{1,2,3,4,7}_*.png
- docs/kb/art/environments/{haluna.md (Revisions, appended), haluna_mood_review.md (appended)}, docs/kb/tasks/M1/M1-ENV-01-mood-test.md
