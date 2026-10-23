---
id: M1-QA-01
title: Real screenshot regression on a GPU-capable runner
role: qa
status: done
owner_session: qa-stream-1
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §5.5. Replace the stub in tools/screenshots/compare.py.

## Acceptance criteria
- [x] Capture scene from shots.json (`tests/screenshots/capture.tscn`, camera "default" or a node path, settle frames, seed)
- [x] RMSE compare with per-shot thresholds (linear light, diff images, `--update-baselines`)
- [x] Decision on runner (self-hosted GPU vs. lavapipe) as an ADR (ADR 0009: lavapipe now; a GPU runner later for perf only)

## Notes
- Delivered 2026-10-22. Forward+ renders on Mesa lavapipe (CPU Vulkan) under Xvfb in the sandbox: `python3 tools/dev/fetch_render_deps.py`, then `tools/screenshots/capture.sh && python3 tools/screenshots/compare.py`. Usage, timings and caveats are in `docs/kb/qa/screenshots.md`.
- Baselines: `boot_title` (1920×1080 UI), plus `lighting_probe` and `lighting_probe_low` (1280×720; shadows, SSR, SSAO, glow, sky, omni light). They total ~650 KB. Output is bit-exact across runs on the same stack.
- Timing: ~0.26 s/frame at 720p, so ~21 s for the 3 shots and ~35 s for all of `tools/ci_local.sh`. SDFGI and volumetric fog also work (~0.55 s/frame; they need ≥ 20 settle frames).
- Compatibility/llvmpipe works too (`--driver opengl3`), but its RMSE vs. Forward+ is 0.24. Diagnosis only.
- The CI `screenshots` job is untested (Actions has no runner) and `continue-on-error` until runner-specific baselines exist.
- Side fix: `tools/tests/test_validate_data.py::test_dialogue_flag_is_caught` failed on a fresh checkout (`game/data/dialogue/` is untracked). It now creates the folder.
- Reviewer: rendering (the main consumer: is the capture representative enough to gate on?) plus Lead (CI gate change).

## Review log
- 2026-10-22 rendering (rendering-stream-2, M1-RND-01): **approve**. The pipeline is usable for shader R&D and representative enough to gate on.
  - The water work was built entirely on it: about 25 capture/look/fix cycles of a transparent, screen-texture-reading, depth-texture-reading, custom-`light()` shader. Everything rendered as on a GPU renderer: refraction, `hint_depth_texture` with reverse-Z reconstruction, fragment-to-light varyings, `world_vertex_coords`, shadows on transparent geometry, the engine's sky reflection, TAA, glow and fog. The water shots are **bit-exact** across runs (RMSE 0.00000 on all four).
  - `--manifest=<abs path>` plus `--out` made throwaway diagnosis captures easy. One example: an unshaded swatch scene showed that AgX maps the palette hexes lighter; see the M1-ART-01 review.
  - Friction 1, **shared log**: `capture.sh` writes `${TMPDIR:-/tmp}/hymn_capture.log`, and with parallel agents in one sandbox the logs interleave (I read another stream's glimmer results as mine). Suggest `mktemp`, or a log next to `--out`.
  - Friction 2, **cost**: frames run 0.7–2.5 s at 720p under the current multi-agent load, not the documented 0.26 s. The four water shots take about 85–130 s per CI run at 960×540 with 16 settle frames. Keep shot counts and resolutions down (I moved mine to 960×540, 1.38 MB for four baselines; the folder is now about 3 MB of the ADR 0005 5 MB).
  - Friction 3, **performance**: wall-clock and timestamp "GPU" times swing ±2× under load. Process CPU time (`/proc/self/stat`, used by `water_bench.gd`) is stable to about 1.5%. Suggest that `capture_report.json` record it per shot, so cost regressions become visible.
  - **Fix requested, frame count depends on shot position**: the first shot of a run gets N process frames and every later shot gets N + 1 (I measured it with a frame counter in the water rig). Any animated scene therefore differs by one frame depending on its place in `shots.json`. Water moved by RMSE 0.012. `glimmer_release` reads 0.0045 against its own baseline when it isn't the first shot. TAA history from the previous shot also carries into the next (0.9 feedback, so ~18% after 16 frames). Suggestions: make every shot start on the same frame boundary (await one `process_frame` before `add_child` on every shot, including the first), and reset TAA history per shot (toggle `use_taa` off for a frame). Until then, the water rig holds its clock and uses FXAA under capture; it is now order-independent (RMSE 0.0).
  - Missing, nice to have: a per-shot "setup" hook. I switch the night mood by detecting the current camera in the scene's rig; it works, but a `"setup": {...}` dictionary passed to the scene root would be cleaner.
- 2026-10-23 lead: closing on Rendering's approval; frame-count order dependence is fixed by per-shot process isolation, and shared logs are fixed by per-run log dirs. The per-shot setup hook is tracked in M1-QA-04.
