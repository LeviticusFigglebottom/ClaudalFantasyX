---
id: M2-RND-18
title: "Cold first launch: the boot's worst hidden frame (it froze the boot card)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: architect
depends_on: [M2-RND-15]
milestone: M2
request-from: "lead"
---
## Goal
On an empty driver cache, the boot's worst hidden frame was 1.6 s (Low) and 3.0 s (High). A frame that long freezes
the boot card's animation, which reads as a hang. Target: ≤ 1.35 s, the first-launch exception. If a part is truly
irreducible, measure it and write it up for an ADR.

## Acceptance criteria
- [x] Find what the frame is.
- [x] Split or spread it.
- [x] What's irreducible is measured.

## Notes (PC GPU, 2026-10-24)
Traced with `slice_sweep --pipeline-trace` (M2-RND-15), plus a frame dump, on a baked release with every cache
cleared, the driver's included (RX 9070 XT, 2560×1440). The 3.0 s frame was **three costs sharing one frame**:
1. the renderer's own first use, with every feature on;
2. a first-run scene's load: loading its meshes compiles their pipelines;
3. the first material's draw: Haluna's palm frond, 10 surface + 8 specialization + 10 mesh pipelines.

**Changes** (`ShaderPrewarm`, first runs only):
- **The first-run harvest is spread.** `first_run_scenes` are no longer harvested in `start()`. They're harvested one
  at a time, each loaded on a worker thread (as SceneRouter loads a zone) and read on the main thread once it's in.
- **The frame after the bring-up stays empty,** so the renderer's first use doesn't share it with the first draw.
- **`first_run_materials_per_frame` is 1.** Two to a batch put two materials' pipeline sets in one frame.
- **Tried and dropped:** bringing the stage's lights up one per frame, and drawing each batch with the lights hidden
  then lit. Godot compiles a draw's whole surface pipeline set at once, lights or not. Loading the next batch's
  resources a frame early didn't help either: the mesh pipelines belong to the draw.

**Results** (the launch's worst hidden frame):

| | Before | After |
|---|---|---|
| High | 2,970 ms | **1,395–1,434 ms** (4 runs) |
| Low | 1,580–1,606 ms | **1,412–1,678 ms** (3 runs) |

The cold boot takes about 1 s longer (High 32 s, Low 38–41 s). `reveal_wait_end` is `done` in every run. Haluna's
cold first entry stays within budget: 449 ms / 2.0 s (High), 697 ms / 2.3 s (Low).

**What's irreducible.** The worst frame is now **one material's first draw:** Haluna's palm frond, the first
vegetation material, with 10 surface + 8 specialization + 10 mesh pipelines. It measured 1.36–1.68 s over 5 cold
runs. It's a single draw, so its pipeline set compiles synchronously in Godot (4.6.3; 4.7.2 is the same per the port
check), and the project can't split it further. Every other first-run frame is ≤ 1.45 s (most 0.9–1.3 s).

**For an ADR amendment:** the first-launch exception would cover hidden frames up to about **1.7 s**, on a cold
first launch only, with the driver's cache empty, under the card. The worst is one material's synchronous pipeline
compile. Measured on an RX 9070 XT; a min-spec GPU is slower (M3-RND-02 will measure it).

## Review log
