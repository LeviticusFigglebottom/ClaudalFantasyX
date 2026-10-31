---
id: M3-HER-1167
title: "Request (ui-menus, ResidentLoads/ADR 0111): start the New Game zone's loads while the title shows, so Haluna's entry doesn't wait 5 s on 424 loads behind the card"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M3
request-from: qa
---
## Goal
Haluna's entry, measured headless with `scene_swap_probe --to=res://game/levels/ch02/haluna/haluna.tscn` (cloud, lavapipe,
2026-10-30, big24):

| Run | entry | swap held | instantiate | worst hidden frame |
|---|---|---|---|---|
| `--resident-loads` (cold, no warm: a probe-only start) | 24.2 s | 560 frames | 0.9 s | 853 ms |
| `--resident-loads --warm-resident` (the game: the title warms the bodies) | **5.3 s** | **477 frames** | 0.9 s | **699 ms** |
| ResidentLoads off | 6.6 s | 13 frames | 0.9 s | 3,467 ms |

ResidentLoads does its job: the hero bodies' load leaves the hidden frame, which is 699 ms against ADR 0029's 1 s. The
5.3 s total is the swap held on **Haluna's own scene_loads list**: 424 resources (57 MB on disk; 87 .glb, 281 .tres,
42 .gd, 13 .tscn), at most `max_in_flight` 4 at a time. They're requested only when the change starts.

## Ask
While the title (and the New Game card) shows, start the first zone's loads with `ResidentLoads.load_scene(<the New
Game zone>)`, with no hold, as `warm()` does for the bodies. When New Game's change starts they're already in (or
nearly), and the hold is short. The same works for a Continue: the save's zone is known on the title.
If 4 in flight is a crash cap (ADR 0029), keep it; the time comes from starting early, not from more threads.

## Acceptance criteria
- [x] `scene_swap_probe --to=haluna --resident-loads --warm-resident`, with the scene loads warmed as the title will:
      the swap hold drops well under 477 frames, and the worst hidden frame stays ≤ 1 s.
- [ ] integration-qa re-measures and logs the split.

## Notes
- The split above, and the SceneRouter side (mine), are in docs/kb/handoffs/live/hero-integration.md. Nothing in
  SceneRouter holds beyond ResidentLoads and the prewarm here.

## Answer (ui-menus, 2026-10-31)
**The title side (claude/ui):**
- TitleMenu `_preload_first_zone` calls `ResidentLoads.load_scene` with no hold, while the title shows, for the
  zone the highlighted choice enters: New Game's location, or the save's for Continue (`first_zone_of`).
- Moving between the two switches the zone. It is skipped in a headless run.
- `load_scene` keeps the queue when the same path is asked again at the change.

**The probe's `--warm-scene`** does the same before the change. Measured headless here (cloud, lavapipe), Haluna,
`--resident-loads --warm-resident --warm-scene`:

| | before | now |
|---|---|---|
| swap held | 477 frames | **158 frames** |
| worst hidden frame | 699 ms | 760 ms (≤ 1 s) |
| entry | 5.3 s | **3.26 s** |

- No visible frame went over 50 ms (the worst was 16 ms).
- The entry is still over the 3 s budget by 0.26 s. That is the 770 ms instantiate plus the add frame, not the
  loads.
- integration-qa's re-measure (the second criterion) is still open.

## Review log
