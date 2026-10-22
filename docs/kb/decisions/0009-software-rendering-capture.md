# 0009 — Screenshot capture via software Forward+ (Mesa lavapipe + Xvfb)

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** QA, Rendering, Environment, Character, UI, Lead
- **Author role:** QA

## Context
SPEC §5.5 requires screenshot regression, and ADR 0002 makes the project Forward+ (Vulkan). Headless Godot uses the dummy renderer and draws nothing. The cloud sandbox has no GPU and no display, and GitHub Actions gets no runner (ADR 0008). Without real frames, the whole fidelity track (rendering, environment, character) can't see its own output, and nothing guards it against regressions.

## Options
1. **Self-hosted GPU runner.** Real-hardware fidelity, but no such machine exists, it needs the human, and the agents in the sandbox still can't see frames.
2. **Compatibility renderer on llvmpipe (OpenGL).** Works and runs about 2× faster, but it lacks SSR, SSAO, TAA, SDFGI and volumetrics and has a different colour pipeline. Baselines would not represent the game.
3. **Forward+ on Mesa lavapipe (Vulkan on the CPU) with Xvfb**, fetched from the Ubuntu archive into the ADR 0008 sysroot. It is the same renderer the game ships, it needs no root and no GPU, and it is deterministic.

## Decision
Option 3.
- `tools/dev/fetch_render_deps.py` adds `mesa-vulkan-drivers`, the Mesa/glvnd GL stack, `xvfb` and `vulkan-tools` (88-package closure) to the Godot sysroot. It also writes `godot-render`, a wrapper that sets all the loader/ICD/XKB env vars and starts Xvfb.
- `tests/screenshots/capture.tscn` renders every shot in `shots.json`, and `tools/screenshots/compare.py` compares them by **linear-light RMSE** against committed baselines (thresholds 0.008 for 3D, 0.004 for UI).
- `tools/ci_local.sh` runs capture and compare when the wrapper exists and prints SKIP otherwise. The Actions `screenshots` job (apt Mesa + `xvfb-run`) reports but does not gate.
- Compatibility/llvmpipe is kept for diagnosis only and never produces baselines.
- A self-hosted GPU runner (option 1) is still welcome later, for *performance* and real-hardware fidelity checks. It would get its own baseline set and ADR.

## Consequences
- Every agent can now render a scene to PNG and look at it, which unblocks the fidelity streams.
- Capture is slow: ~0.26 s/frame at 720p, and ~0.55 s/frame with SDFGI and fog. Keep shots few and small (720p), and give GI/fog scenes ≥ 20–30 settle frames.
- Baselines are tied to a software stack (distro Godot 4.6.3+ds-2, Mesa 26.2.4, LLVM 22, `LP_NATIVE_VECTOR_WIDTH=256`). Upgrading Mesa or switching to the official Godot build means re-approving the baselines in a commit that says why.
- lavapipe is not a GPU. Fidelity *judgement* and performance budgets (SPEC §8) still need real hardware.
- The PNG codec is in-repo (numpy + zlib), so no new Python dependency is added.
