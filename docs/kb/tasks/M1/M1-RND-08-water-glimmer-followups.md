---
id: M1-RND-08
title: Water and glimmer follow-ups (review-sweep-B)
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-08-water-glimmer; water items first)
depends_on: [M1-RND-01, M1-RND-02, M1-RND-03, M1-ENV-01]
milestone: M1
request-from: "environment"
---
## Goal
Environment-side findings on water and glimmer, scheduled after the Undertow and mood-test streams that consume both have merged.

## Acceptance criteria
- [x] Global tide/water-level uniform (stone weathering, Drownbell flood)
- [x] Zone-level hymn_sea_glow global decoupled from mote energy (water + glimmer)
- [x] Caustics: less uniform Voronoi web, no visible tiling; pattern exposed as material param (Shell Shrine nets)
- [x] Glimmer: fixed-count non-respawning field mode (H06 needs exactly 9 on every preset)
- [x] Glimmer: local-space option so bound fields follow moving hosts
- [x] glimmer_bound baseline; spiral rate vs lifetime; .dlg cue args mapped to field params
- [x] Dusk released motes: warmer halo, density gradient; held motes spawn low over water
- [x] Water: NaN at the anti-solar pixel (sun about 5° up, behind the camera; suspect normalize(L+V)) blooms into a white disc (found by the Undertow stream)
- [x] Water: SSS paints saturated green bands across open sea with a low sun behind the camera
- [x] Water: SSS crests read as large pale patches from high cameras at noon (Art, M1-ART-04)

## Notes
- 2026-10-23 PC GPU session claims this task and starts with the three water items (NaN at the anti-solar pixel, SSS green bands, SSS crest patches), which need a real GPU to see. Glimmer and caustics items stay open unless noted below.
- 2026-10-23 water items done (NaN guard, view-dependent SSS wrap; pale crest patches reduced, Art to confirm). Report: docs/kb/qa/gpu/2026-10-23-rnd-08.md. Lavapipe re-approvals: water_shallows, water_lagoon, water_horizon, haluna_h01_village_from_sea, haluna_h04_dock (haluna_h03 optional). Remaining items open.

- 2026-10-23 all items done; report docs/kb/qa/gpu/2026-10-23-rnd-08.md (parts 1 and 2). Lavapipe re-approvals: water_shallows, water_lagoon, water_horizon, glimmer_dusk, glimmer_night_held, haluna_h01_village_from_sea, haluna_h04_dock; new glimmer_bound from the pending manifest. Art to confirm caustics look, halo_chroma_gain and the noon crest patches.
- 2026-10-23 rendering (M1-RND-15, worktree-agent-a94256e372f018240): **B1 closed.** `glimmer_bound` moved from the pending manifest into tests/screenshots/shots.json after `glimmer_release` (ShotCamera, 960×540, 30 settle frames; no capture setup needed: the stage moves the carrier with `delta`, which `--fixed-fps 60` makes deterministic). Rendered on lavapipe (Forward+, llvmpipe LLVM 22.1.8) and inspected before approval: after 0.5 s the cage has travelled 0.75 m right of the figure and its teal field is still inside it, so the local-space field follows its host. About a dozen distinct motes resolve inside the 0.5 m cage at this framing; the rest of the 24 overlap or sit behind the posts (`fixed_count` 24 is unit-tested). The brightest core is #6AA9AB against glimmer_bound's on-screen 0 level #66A7A6, the halos' median is #3A7D84 (near the −1 level #3B8280, hue 205°), there is no gold or red in the cage (palette_check coverage), and the night sea and sky are unchanged from the night shots. Approved with `compare.py --update-baselines glimmer_bound` (PASS rmse 0.00000 on re-compare). The pending-shots manifest is now empty. Back to **review** (environment); S1-S4 and the nit are in M1-RND-15, S5 (Art sign-off) stays open for M1-ART-04.
- 2026-10-23 rendering (M1-RND-15): **NaN fix confirmed on lavapipe**, the driver where the Undertow stream saw the white disc. `tools/gpu_bench/water_probe.tscn -- --scene=undertow --camera=Cameras/Horizon --sun-elev=5 --sun-rel-az=180 --set=use_sss=true --res=960x540 --frames=60` (llvmpipe, Forward+, High): anti-solar pixel (480, 453), disc peak 0.192 and mean 0.109 (the GPU measured 0.102 after the fix), and no white disc in the frame.

## Review log
- 2026-10-23 environment (review-sweep-I, fresh reviewer): **request-changes** (one AC not met in tree; everything else approve-with-fixes).
  - **What I read:** the task, docs/kb/qa/gpu/2026-10-23-rnd-08.md (parts 1 and 2) and the pending-shots manifest, `git log -p` for 844574c, 170bca4, 86ce66b and 246b2dc, and the Lead's re-approvals 146375d and cb318dc. I viewed the `water_lagoon` and `glimmer_dusk` baselines.
  - **Checks:** Godot `--filter=glimmer` 34 run, 0 failed. `--filter=water` 23 run, 0 failed. `validate_data` 0/0. Tool tests 359 OK.
  - **What passes:**
    - **SSS fix.** The view-dependent wrap term (`toward_light`, water_surface_body.gdshaderinc:563-564) is the right root cause for both the green bands and the noon crest patches. The numbers back it: the anti-solar disc drops 0.305 → 0.102, the same as with SSS off, and back-lit views change by RMSE 0.0007.
    - **NaN guard.** `vdh` is clamped to 0..1, and `hv` is normalised by `inversesqrt(max(dot, ε))` (:570).
    - **Fixed-count, local-space and cue mapping** are tested (9 motes on every preset, a moving and rotating parent, every `cues.json` value mapped).
    - **The Ending exception.** The sea-glow floor is now 0.04, so E4 0.07 and E5 0.06 render as authored, and `ending_dock` reaches 0 through the `zone_energy <= 0` branch.
    - **The lavapipe re-approvals** in cb318dc cover the listed shots.
  - **Blocker:**
    - **B1. AC "glimmer_bound baseline" is ticked but not in the tree.** `glimmer_bound` is not in tests/screenshots/shots.json, and there is no `baselines/glimmer_bound.png`. It still sits in docs/kb/qa/gpu/2026-10-23-rnd-08-pending-shots.json. Lead: move the entry into shots.json after `glimmer_release`, render it on lavapipe, **open the image** (the cage must be visibly carrying its 24 motes), and approve it. Then this AC is met. The NaN fix also still awaits the lavapipe confirmation the report asks for. Note it in the same commit.
  - **Should-fix:**
    - **S1 (the Ending's dark sea can be overridden).** glimmer.gdshaderinc:77-79: `hymn_sea_glow_zone` lets any material with `sea_glow_energy > 0` override the zone, so a zone global of 0 cannot force the sea dark. SPEC §3.5's final image ("the whole sea dark for the first time in a thousand years") depends on *every* water material in `ending_dock` being 0. All defaults are 0 today, so this is latent. Either treat the zone's off scenes as a hard 0 (a negative sentinel, or an `hymn_zone_sea_glow_off` flag), or make `sea_glow_violation`, or a validator, check the materials of off scenes.
    - **S2 (globals outlive their zone).** `hymn_zone_sea_glow` and `hymn_water_level` are global shader parameters that are written but never reset. A night zone followed by a zone that never calls `set_scene_sea_glow`, or one with no publishing sea, inherits the previous zone's glow or tide line. Reset both on zone exit (WaterSurface `_exit_tree`, or SceneRouter), or require every zone to write them, and add that to M1-ENV-05.
    - **S3 (one publisher).** water_surface.gd:73: `publishes_water_level` defaults to **true**, so every river or pool WaterSurface also writes the zone level each frame, and the last one to process wins. Default it to false and turn it on for the zone sea. Or warn when two publishers are in the tree.
    - **S4 (stale comments).** water_surface_body.gdshaderinc:234 and :521, and glimmer_sea_glow_overlay.gdshader:4, still say the glow is "gated by hymn_glimmer.a" or "on when hymn_glimmer.a > 0". It no longer is.
    - **S5 (Art confirmations outstanding).** Caustics look, `halo_chroma_gain` and the noon crest patches are all "Art to confirm". From the lavapipe baselines:
      - `water_lagoon`: the near-field web is less uniform, and the far tiling is gone.
      - `glimmer_dusk`: the released motes still read near-white against the dusk sky, not gold, and the `center_bias` 1.8 clustering is hard to see at this framing.
      Please get Art (M1-ART-04) to sign off, or open an Art task, before this goes to done.
  - **Nits:** the `local_space` field converts through `field_to_world` in the process shader. Record in glimmer.md which inputs stay world-space (attractors, the release wave, water), so Environment knows what follows a moving host.
- 2026-10-23 lead: reopened on review-sweep-I request-changes: the glimmer_bound shot and baseline are missing; the should-fixes move into M1-RND-15 alongside it.
