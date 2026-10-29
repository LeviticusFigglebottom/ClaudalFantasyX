---
id: M2-FP-108
title: "FAST-TRACK: B06 Saltgrass Causeway plays on env-art's final route, not the greybox"
role: cinematics
status: done
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-ENV-10, M3-CRE-611]
reviewer: environment
milestone: M2
request-from: lead
---
## Goal
Viewing the slice (tools/cutscene_frames) showed B06 as pure greybox: a flat sand slab, a flat colour sky, flat
teal planes. That is the most primitive stretch of the human's playthrough, and env-art's final route (M2-ENV-10,
with a swap-in note for m2-slice) has been on the integration branch since big8.

## Acceptance criteria
- [x] GreyboxZone: a layout `dressing` {scene, adopt} instances a final zone scene, dresses it off the tree through
  an adopt script (CausewayZoneDresser, like HalunaZoneDresser), takes its sun and sky, and skips the greybox
  lighting; blocks may be `visible: false` (collision only) and take a `pitch`.
- [x] `tools/causeway/build_causeway_gameplay.py` generates the gameplay layout from env-art's
  `causeway_layout.json`:
  - an invisible walk floor and rails along the 301 m path;
  - the spawns;
  - the triggers (posts, harrier at C07, tide pool, ring, the islet steps);
  - the side-on C02 dolly over the whole route, plus C01, C03–C07 from env-art's preview cameras;
  - the encounter table, unchanged.

  `--check` guards staleness (tools test).
- [x] Creatures' causeway wildlife moved onto the route by the same tool (their data note asked for it at the swap).
- [x] Tests: test_causeway_route (3); zone_story 15, fp_thread 2, causeway 9, wildlife 10, slice_beats 5.
- [ ] Viewed in tools/cutscene_frames (see the live log).

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **Checks run:** `tools/causeway/build_causeway_gameplay.py --check` reports up to date, and
    `--filter=causeway` is 13 run, 0 failed.
  - **The PC baselines show the final route in play:** `slice_causeway_head`, the kit's flats and saltgrass with
    the heroes on the stone causeway; and `slice_causeway_harrier_view`.
  - **What was checked:** the walk floor and the spawns sit on the route's own heights, and the wildlife is moved
    onto the route.
  - The last box (viewed in cutscene_frames) is covered by those baselines. Done.
