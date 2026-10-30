---
id: M3-ENV-1391
title: "Oruvel: three moored hulls and an outrigger still clip their decks or planks (request from cloud QA, playtest row 75)"
role: environment
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
reviewer: qa
priority: high
---
## Goal
The human's playtest: boats clip the Oruvel docks. 7fbb9319 (big23) fixed the cookboat, but on big25 (4b198810) 10
boat/dock mesh-AABB overlaps remain. Cloud QA rendered each one (lavapipe:
`docs/kb/qa/cloud/pass6/row75_oruvel_overlap_views_big25.jpg`, made with `tools/gpu_bench/spawn_stills.tscn --views`).
The real clips are below; the dive raft's bridges and gull post are intended.

## Acceptance criteria
- [ ] `scale_hull` vs the raft deck at its side: the deck's edge cuts through the hull (AABB overlap 1.93 × 2.08 ×
      7.27 m). Move the hull clear of the deck, or cut the deck back.
- [ ] `keel_hull` vs the two tucked raft decks at its side (z ≈ −33.5): the decks run 0.43 m into the hull.
- [ ] `terrace_hull` vs the tucked raft deck at x ≈ −33.9: the deck corner runs 0.25 m into the hull.
- [ ] The second `hull_outrigger` (x ≈ 37.5–40.3, z ≈ −20.4 to −13.6) lies under the two plank bridges at z ≈ −17.7 to
      −16.3: the planks pass through the canoe (overlap 0.61 and 2.76 m wide).
- [ ] The first `hull_outrigger` vs the small tucked deck (0.59 × 1.14 × 0.34 m): its outrigger boom rests on the deck
      edge. Check this one; it may read as moored.
- [ ] `python3 tools/gpu_bench/dock_overlaps.py <meshes.json>` from
      `tools/gpu_bench/dock_probe.tscn -- --out=<dir>` lists only the dive raft's intended pairs.

## Notes
Owner: env-art (the Prologue to Ch4 zones, ADR 0041). See act1_gpu_qa.md row 75 on `qa/cloud-pass6`.

## Review log
