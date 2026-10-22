---
id: M1-QA-01
title: Real screenshot regression on a GPU-capable runner
role: qa
status: review
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
