---
id: M3-ENV-1329
title: "Brine Shoals: hard wet/dry seams where the channel tiles meet the mudflat tiles"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
env-art-b's player-height walk of Ch6 (on big21 merged) shows a hard straight line across the sand wherever a
`channel_straight_a/b` tile meets a `mudflat_patch_a/b` tile. Those edges are the channel column's x −36 and −12,
z < −24. It's most visible:
- at the `CampWaterline` spawn looking north or south: the frame splits down the middle, one half glossy-wet and
  the other dry ripples;
- at the `Channel` spawn looking east: a horizontal line 5 m ahead.

Turning the shader's wetness off in a test render removes every seam. Variation and LOD made no difference. The
cause is the baked VC.B wetness in `assets_src/environments/kits/brine_shoals/bs_ground.py`:
- `_mud_channels` (the mudflat) floors wetness at 0.75 ("the whole flat is damp").
- `build_channel`'s `wet()` gives `1 − smoothstep(−0.25, 0.14, Y) × 0.75`, about 0.5 at y 0 on the tile edge and
  0.27 on the bank tops.

So the two sides of every channel-column edge differ by 0.25–0.5 in wetness.

## The proposed patch (kit code, so env-art's)
```python
        def wet(X, Z, Y):  # the banks as damp as the flat around them (_mud_channels' 0.75 floor)
            return np.maximum(1.0 - kc.smoothstep(-0.25, 0.14, Y) * 0.75, 0.75)
```
Then rebuild `channel_straight_a/b`. The kit manifest's bytes change; the tris don't.

## Acceptance criteria
- [ ] No straight wet/dry line at the channel column's edges in env-art-b's walk stills (the `CampWaterline` and
      `Channel` spawns).
- [ ] env-art-b re-renders `ch06_brine_camp` and `ch06_brine_road` and the walk.

## Review log
