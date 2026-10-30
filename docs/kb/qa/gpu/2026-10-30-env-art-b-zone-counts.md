# env-art-b's zones: render counts and dressing cost (2026-10-30)

The Lead asked for a performance check on env-art-b's heaviest zones: Pemakar, Brine Shoals, Corrow (Ch8 and Ch9) and
Ch13–Ch16. Each was measured at its hero shots on the cloud box: lavapipe (Vulkan on llvmpipe), 1280×720, through the
shot rigs and their capture setup. Frame time on lavapipe only compares zones against each other, so this report uses
counts.
- **Per frame:** draw calls, objects and primitives in view, averaged over 8 frames after 30 settle frames, plus the
  shadow pass's draw calls.
- **Per scene:** the meshes, multimeshes and lights, and the most repeated meshes.
- **Probe:** `_scratch_eab/perf.gd` (scratch, not committed). The numbers are from build 944f7d2c plus the ambient-life
  commits.

## Counts at the hero shots

| Shot | Draws (shadow) | Objects | Primitives | Meshes (surfaces) | MultiMeshes | Lights |
|---|---:|---:|---:|---:|---:|---:|
| ch05_pemakar_harbour | 311 (862) | 2,526 | 1.76 M | 1,347 (3,026) | 7 | 394 |
| ch05_pemakar_crown | 439 (873) | 1,946 | 1.90 M | 1,347 (3,026) | 7 | 394 |
| ch06_brine_road | 410 (632) | 504 | 0.46 M | 255 (446) | 3 | 6 |
| ch06_brine_camp | 341 (944) | 369 | 0.45 M | 255 (446) | 3 | 6 |
| ch08_corrow_arrival | 313 (826) | 463 | 0.89 M | 503 (878) | 4 | 2 |
| ch08_corrow_stair | 371 (1,052) | 666 | 0.85 M | 503 (878) | 4 | 2 |
| ch09_corrow_strand | 524 (1,101) | 1,010 | 0.88 M | 657 (1,305) | 0 | 33 |
| ch09_corrow_road | 221 (228) | 441 | 0.71 M | 555 (1,095) | 0 | 2 |
| ch13_ansedra_arrival | 140 (381) | 299 | 0.34 M | 120 (290) | 0 | 1 |
| ch13_ansedra_causeway | 116 (409) | 257 | 0.30 M | 120 (290) | 0 | 1 |
| ch13_sanctum_basin | 70 (169) | 80 | 0.06 M | 44 (59) | 0 | 7 |
| ch13_archive_door | 21 (183) | 65 | 0.02 M | 26 (79) | 0 | 1 |
| ch14_court_ceremony | 43 (242) | 89 | 0.24 M | 53 (167) | 0 | 9 |
| ch15_hollowmere_dock | 114 (366) | 201 | 0.30 M | 128 (348) | 3 | 12 |
| ch15_sea_deck | 24 (43) | 24 | 0.24 M | 10 (22) | 0 | 1 |
| ch16_rim_wade | 13 (36) | 31 | 0.24 M | 23 (56) | 1 | 1 |

**The draw calls are low everywhere.** Godot batches the kit's repeated pieces itself. Pemakar shows 2,526 objects in
view but only 311 draws, because its 203 channel pieces, 196 steles and 192 wall pieces share their meshes and
materials. The worst frame, Corrow's strand at night, is about 1,600 draws with the shadow pass.

Making the repeated props MultiMeshes would not cut the draws. It would cut the node count and the CPU's culling.
- **Pemakar** is the only zone with a large node count: 1,347 meshes.
- **Its graves** (335) **and terrace pieces** (about 600) carry box colliders and trimesh walk surfaces. Turning them
  into MultiMeshes means rebuilding their collision on its own.
- **Not done:** no zone is over the budget proposed below, and the zones' meshes and collision are already proved by
  their tests and walks.

**Triangles:**
- **Pemakar is the heavy one:** 1.8–1.9 M in view. The crown view sees the whole town inside its 120 m LOD1 range.
- **The rest are under 0.9 M.**
- **On the PC tier:** the recommended tier (RTX 3060 class) handles this. On the minimum tier (GTX 1060, Low preset)
  it is the first thing to watch, and the PC GPU queue's `gpu_bench` on `ch05_pemakar_crown` is the measure that
  counts.

**Lights:**
- **Pemakar:** 393 lamp omnis, every one on the Lamps block. This is under Forward+'s 512 clustered elements per view,
  but the crown view sees 388 of them within 90 m.
- **What changed:** the lamps now fade out from 70 m over 20 m (`fire_light_fade`, below). The far lamps' glow is
  already the `far_lights` quads. The harbour and crown shots are unchanged by eye before and after.

## Where a zone entry's time goes

SPEC §4.2 budgets 3 s for a zone entry. The "add" step instances the zone and runs its `_ready` and its dressing. It
measured 11–24 s on this box for Pemakar, Brine Shoals and Corrow, and 1.5–3.5 s for Ch13–Ch16.

A node-by-node timing (the gaps between `node_added` events) shows the dressing is the smaller share:
- **The heroes.** Each cutscene hero's body and AnimationTree (asha, toma, ysolde, kerrid, liss) and the HeroParty
  take 1.6–2.7 s each. That's 9–11 s of Pemakar's and Corrow's 14 s.
  - **Why the probe sees it:** the probe adds the zone outside SceneRouter, so ADR 0111's ResidentLoads never warmed
    the hero scenes.
  - **In the game:** the router's resident loads take this out of the swap frame.
- **The first UI label.** About 1.2–1.9 s, which is font and theme setup on first use.
- **ZoneKitDressing**, timed per step (instrumented, not committed):
  - **Pemakar** (cached): pieces 0.65 s, the leaf-boat MultiMesh 0.75–1.2 s, the edge walls 0.06 s and the greybox
    hide 0.05 s, about 2.0 s in all.
  - **Corrow:** pieces 0.28 s and the storm 0.26 s, about 0.55 s in all.
  - **On a desktop CPU:** expect a third to a fifth of these.

The environment's own entry cost is therefore at most about 2 s on this box, at Pemakar. Nothing in env-art-b's
dressing breaks the 3 s budget on the PC.

## Changes in this pass
- **ZoneKitDressing `fire_light_fade`:** `[begin_m, length_m]` at the layout's top level. Every fire light fades out
  with distance, so the omnis beyond leave the clustered list. Test: `test_zone_ambient_life.gd`,
  `test_a_zone_fire_fade_reaches_every_lamp`.
- **Pemakar:** `LAMP_FADE_M = (70, 20)` in `tools/act1/ch05_pemakar_dressing.py`. Viewed at ch05_pemakar_harbour,
  _crown and _weir, the same by eye.

## Proposed per-zone budget (LEAD-ASK in env-art-b.md)
No per-zone draw or instance budget is written in `docs/kb/tech` or in ADR 0111. env-art-b proposes these for field
zones at a hero view, measured as above, to be tightened by the PC's `gpu_bench`:
- **Draws:** ≤ 800 visible and ≤ 2,000 counting shadows.
- **Objects:** ≤ 3,000 in view.
- **Triangles:** ≤ 2 M in view.
- **Lights:** ≤ 400 omnis in the zone, which leaves room under Forward+'s 512 clustered elements per view for decals
  and probes. Lamps a town shows far off take `fire_light_fade` and `far_lights`.
- **Entry:** ZoneKitDressing ≤ 0.5 s on a desktop CPU, which is about 2 s on the cloud box.

Every zone above is within these, with Pemakar near the triangle and light lines.
