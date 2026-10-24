# M2-RND-14: boot turns on Forward+'s advanced shader group (2026-10-24)

**Why** (the Lead's root cause of the Shell Shrine lavapipe hang, M2-QA-02). This is a Godot 4.6.3 deadlock, and
master has the same code:
- `version_get_shader()` holds a shader's version mutex while it waits for that shader's compile tasks.
- Pipeline-compile tasks for the same shader fill every worker, each waiting on that mutex, so the compiles never
  start.
- The trigger is Forward+ turning its advanced variants on (motion vectors, VoxelGI, SSS, lightmaps) lazily, on the
  first frame that needs them. With TAA off, that's the shrine's first post-bake frame, with the whole hall loaded.
- 4.7.2 doesn't fix it, so the mitigation is permanent.

**Fix** (`ShaderPrewarm._begin_bring_up`). When the game has no motion vectors (TAA off and no FSR2), every boot's
stage bring-up gets one extra frame with TAA on, right after the plain first frame and before anything stages, then
TAA off again. The group comes on under the card, while the scene is tiny, and everything staged after it compiles
with the group on. With TAA or FSR2, which every preset ships with, the game already has motion vectors, so nothing
is added.

**Measured** (RX 9070 XT, Low with `aa=fxaa`, so TAA is off; `claude/m2-slice` @ 8f74db3a plus this change, with
every cache cleared, the driver's included; `slice_sweep --override=aa=fxaa --pipeline-trace`):

| | TAA off, before | TAA off, after | Default Low (TAA on), after |
|---|---|---|---|
| Cold boot (`launch` hidden total) | 21.3 s | 33.2 s | 34.4 s |
| Boot's surface pipelines | 100 | 164 | 160 |
| Shell Shrine's first frame: worst hidden / entry | 913–926 / 1,360 ms | 1,874–1,896 / 2,742–2,799 | 1,918 / 2,801 |
| Shrine's first-frame pipelines | 16 surfaces + 7 spec | 21 + 7 | 21 + 7 |

- **Before,** a TAA-off boot compiled no advanced variants (100 surfaces), and the shrine's first frame switched
  the group on: the deadlock's trigger.
- **After,** a TAA-off boot compiles the advanced variants under the card (164 surfaces, as a default TAA-on boot's
  160), and the shrine's first frame matches the default path exactly (21 + 7). Nothing switches the group on at the
  shrine.
- The cost: a cold TAA-off boot gets as long as everyone's (+12 s cold, under the card). A warm boot adds one frame.
- The deadlock can't be reproduced on the GPU itself; it's lavapipe's. This shows the trigger is gone. The Lead's QA
  agent can re-run the lavapipe capture.

**Also found (not this task).** On every cold path, TAA on or off, the shrine's first frame is 1.9 s, over ADR 0029's
1 s. The shrine's zone prewarm stage has no VoxelGI, so the GI variants of its materials compile at first draw. A
VoxelGI node in the stage, for zones whose registry entries need it, would warm them (rendering, a follow-up).

**Tools.** `slice_sweep --override=key=value,...` applies GraphicsSettings overrides on top of `--preset`. The test
is `test_a_taa_off_boot_turns_the_advanced_shader_group_on_before_staging` (prewarm 18/0).
