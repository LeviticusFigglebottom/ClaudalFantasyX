---
id: M2-RND-17
title: "Shell Shrine's cold first frame (1.9 s): warm the variants its first draw compiles in the zone's prewarm stage"
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M2-RND-15]
milestone: M2
request-from: "lead"
---
## Goal
Found by M2-RND-14. On every cold path, TAA on or off, the Shell Shrine's first frame is 1.9 s (21 surface pipelines
plus 7 specializations), over ADR 0029's 1 s hidden frame. The zone's prewarm stages its 32 registry materials, but
the hall's first real frame still compiles 21 new pipeline variants. Find which, and warm them in the stage. The
Lead's first lead is VoxelGI. Coordinate with m2-slice, which is moving the hall's GI bake to one state per frame.

## Acceptance criteria
- [x] Find which variants the shrine's first frame compiles.
- [x] Warm them in the zone stage. The shrine's cold first frame is ≤ 1 s on Low and High.

## Notes (PC GPU, 2026-10-24)
**It isn't VoxelGI.** Low has GI off (VoxelGI hidden), and cold Low still had the 1.9 s frame with 21 surfaces plus 7
specializations. Those pipelines are the hall's **runtime-built geometry**: `ShellShrineLevel._ready()` →
`_build()` makes the spring, basins, channels, pools, door and charm. No SceneState lists them, so neither the zone
prewarm nor the first-run harvest staged them. It's Haluna's case again (M2-RND-15).

**Fix:**
1. The shrine joins the registry's `first_run_live_scenes` (this branch, stacked on M2-RND-15).
2. **M2-ENV-12** (filed for m2-slice): ShellShrineLevel builds the hall off the tree on instantiate, as
   HalunaZone.prebuild does, so the live harvest (which never runs `_ready`) sees it. As a bonus, the router's worker
   thread does the build on every entry.

**Measured** with a throwaway version of both on `claude/m2-slice` @ 8f74db3a (cold, every cache cleared, Low):

| | Before | After |
|---|---|---|
| Shrine's first frame | 1,918 ms (21 + 7) | **188 ms** |
| Shrine entry | 2.80 s | 1.18 s |
| Cold boot (under the card) | 34.4 s | 39.9 s |

No VoxelGI node in the stage is needed on these presets: Medium's VoxelGI variants, if any remain, would show up as
a residual once M2-ENV-12 lands. Re-measure on Medium then.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **Part 1 is in:** the shrine is in `prewarm_materials.json`'s `first_run_live_scenes` (line 961), and
    `ShaderPrewarm` stages it off the tree.
  - **The diagnosis matches the kit:** the hall's spring, basins, channels, pools, door and charm are built at
    runtime by `ShellShrineLevel._build()` from the kit's pieces, so no SceneState lists them.
  - **Part 2 (M2-ENV-12)** is the shrine's off-tree build. Its re-measure on Medium follows that. Done.
