---
id: M2-ENV-12
title: "Shell Shrine: build the hall's geometry off the tree on instantiate (as HalunaZone.prebuild), so the warm-up and the router's thread can do it"
role: environment
status: todo
owner_session: ""
reviewer: rendering
depends_on: [M2-RND-17]
milestone: M2
request-from: "rendering"
---
## Goal
From M2-RND-17 (PC GPU). On a cold first launch, the Shell Shrine's first frame takes 1.9 s on every preset and AA:
it compiles 21 surface pipelines plus 7 specializations for the hall's runtime-built geometry.
- `ShellShrineLevel._ready()` calls `_build()`: the spring, basins, channels, pools, door and charm. No SceneState
  lists those meshes, so the zone prewarm can't stage them.
- M2-RND-15's first-run live harvest (`ShaderPrewarm`, registry `first_run_live_scenes`) instances a zone on a worker
  thread and stages the meshes it holds, but it never runs `_ready`.

## Acceptance criteria
- [ ] `ShellShrineLevel` builds the hall's geometry off the tree when it's instanced, like
      `HalunaZone._notification(NOTIFICATION_SCENE_INSTANTIATED)` → `prebuild()`. That's the trial data (`cfg`,
      `trial`, `_g`, `_layout`) and `_build()`. `_ready` then skips what's built: the camera, the signals, `_restore`,
      `_relight` and `bake_gi` stay in `_ready`.
- [ ] Nothing that touches the tree or a node in it runs off the tree.
- [ ] The router's worker-thread instantiate then does the build too, which takes it off the main thread on every
      entry.

## Notes
**Measured** by M2-RND-17 with a throwaway version of exactly this: `_build()` moved to SCENE_INSTANTIATED, plus the
shrine in `first_run_live_scenes`. It ran on `claude/m2-slice` @ 8f74db3a, cold, every cache cleared, Low.
- The shrine's first frame went from **1,918 ms to 188 ms**, and its entry from 2.80 s to 1.18 s.
- The cold first launch's boot grew by about 5 s, under the card.
- M2-RND-17 adds the shrine to `first_run_live_scenes` (rendering's registry). It takes effect once this lands.

- **2026-10-27 (env-art):** already implemented by m2-slice: `ShellShrineLevel._notification` builds on
  `NOTIFICATION_SCENE_INSTANTIATED` off the main thread (`game/levels/ch03/shell_shrine/shell_shrine_level.gd:105`;
  m2-slice's live log, "M2-ENV-12 (the shrine's hall built off the tree)"). Nothing left for env-art. For the Lead:
  close it, or have Rendering check M2-RND-17's measure on hardware.

## Review log
