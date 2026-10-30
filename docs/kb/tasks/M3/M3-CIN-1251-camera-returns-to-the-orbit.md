---
id: M3-CIN-1251
title: "Request (the field camera's owner, game/world/**): leaving every camera volume never returns to the hub orbit; the camera stays parked on the last volume"
role: architect
status: review
owner_session: claude/hero-integration (integration-qa, the field camera; Lead fast-track 10-30)
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
`game/world/field_camera_director.gd` picks the best containing volume in `update()` and `snap()`. When the leader is in
**no** volume (`_pick_volume()` returns null), neither one does anything: the last volume's shot stays active. So in
play, walking out of any pan-follow volume (Act I has dozens: POI volumes, Pemakar's harbour, Coilspire, Corrow) leaves
the camera parked at that volume's position while Rhen walks away from it. The hub orbit (`initial_shot`) only comes up
at a zone load with no volume active.

Found by act1-chapters on 2026-10-30 (GPU QA row 49):
- A probe put the leader at Pemakar's Weir spawn (inside a new Weir volume), then at InnGate. That gave `inside=[]`,
  `active=Weir`.
- `test_qa_field_camera` failed for InnGate and FromAshcrown under whichever volume was last. It passes today only by
  luck: the spawn order and where the stale camera happens to point.

## Proposed fix
In `update()` and `snap()`, when no scripted shot is held and `_pick_volume()` is null while `active_volume` isn't, return
to `initial_shot`. `update()` blends (the volume's own blend rules); `snap()` cuts.

```gdscript
var best := _pick_volume()
if best != null and best != active_volume:
    _enter(best, false)
elif best == null and active_volume != null and initial_shot != null:
    _activate(initial_shot, null, false, float(data.get("default_blend_sec", 0.0)))  # snap(): cut (true, 0.0)
```

## Acceptance criteria
- [x] Walking out of every volume blends back to the hub orbit; a teleport out of every volume cuts to it.
- [x] `--filter=camera` and `--filter=qa_field_camera` green, including Pemakar's spawns with a Weir volume present.
- [ ] Then act1-chapters re-applies GPU QA row 49's camera side: Pemakar's Harbour volume landward
      (pos [1.43, 3.33, 18.32] → look [0.0, 1.9, 24.5], fov 50), plus a Weir volume (at [13.6, 2.0, 25.2], size [6, 5, 6],
      pos [7.64, 3.37, 23.06] → look [13.6, 1.9, 25.2], fov 50). Both were viewed in poi_views and held back because of this bug.

## Review log
- **integration-qa (claude/hero-integration), 10-30: done, review: cinematics / act1-chapters.**
  - `update()`: outside every volume with a volume still active and a hub shot set, it blends to `initial_shot` (its
    own blend_sec, else default_blend_sec; its hard_cut honoured). `snap()`: cuts to it. A zone with no hub shot
    keeps the last volume's shot, as before (test_leaving_every_volume_keeps_the_shot still holds).
  - Test: test_leaving_every_volume_returns_to_the_hub_shot (walk out blends, walk back in takes the volume, teleport
    out cuts). `--filter=camera` 67/0; `--filter=qa_field_camera` 2/0 **with c9da92f3f's Harbour and Weir volumes
    applied** on top, so act1-chapters can re-apply row 49's camera side.
