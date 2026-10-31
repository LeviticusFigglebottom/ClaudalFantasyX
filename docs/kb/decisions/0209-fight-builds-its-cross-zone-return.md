# 0209 — A fight builds its cross-zone return scene while it runs (ReturnPark)

- **Status:** accepted
- **Date:** 2026-10-31
- **Roles affected:** tech (SceneRouter), ui-menus (the victory-panel preload, ResidentLoads), creatures (VillagerLayer), qa / pc-gpu
- **Author role:** tech (integration-qa, hero-integration track)

## Context
This is the human's playtest #1 open item. On the PC (pass 7 row 74, big33), the Drownbell → Haluna return was 8.2–8.6 s of covered black. Same-zone returns were 0.9–1.0 s.
- ADR 0205's resident field covers only a fight that returns to the zone it left.
- A scripted fight that ends somewhere new reloaded and re-instantiated the destination behind the fade.
- The victory panel's preload (ResidentLoads.prepare_return) only had the panel's second or two.
- The destination is known when the fight starts (its BattleRequest).

## Options
1. A longer victory panel or a loading screen. This breaks the "≤ 1 s black" bar the Lead set and hides the cost.
2. Keep every likely destination resident. That costs memory for every zone, and most fights return home.
3. **Build the one known destination off the tree while the fight runs, then swap it in on Return.**

## Decision
Option 3.
- When `SceneRouter` enters a fight (the change that keeps the field resident) and the fight's return is not that resident field, `ReturnPark.start` runs once the battle is in. It does three things:
  - threaded-loads the return scene;
  - starts its zone runtime loads (`ResidentLoads.prepare_return`, the victory panel's own call, now made earlier);
  - waits for them, then instantiates the scene on a worker thread (the zone's prebuild runs there; ShaderGlobals writes are held meanwhile, M3-HER-1151) and parks the root off the tree.
- The change to that scene takes the parked root: no load, no instantiate.
- If the build is still in flight when Return comes, the change waits for it. That's still earlier than starting it then.
- Any other change (except a retry into the battle), or a loaded game, frees the park.
- `SceneRouter.park_return` switches it off; the probe uses `--no-park` to compare.

## Consequences
- Headless (causeway fight → Haluna, injected clock): the Haluna entry falls from 3.23 s (instantiate 2.05 s) to 1.18 s (instantiate 0).
- `return_probe --cases=drownbell` (headless, real flow): field in at 1.05–1.09 s, down from 3.39 s. The covered time is 2.5 s, down from 4.1 s.
- What is left under the fade is the add-to-tree frame and the zone's reveal holds (VillagerLayer): slice-polish's and creatures' levers.
- A fight with a cross-zone return holds a second zone in memory (the parked root) beside the resident field.
- The arena's wind and shimmer globals pause while the worker instantiates (about 1 s on the PC). That's the price of the M3-HER-1151 hold.
- ui-menus' victory-panel preload stays. It now finds its loads already in and costs nothing, so it's harmless and the fallback if the park is off.
- Watch: one headless parked run in five logged an engine `Parameter "t" is null` error (no backtrace). It may be a worker/main renderer race in the dummy renderer. The PC should watch for it.

## Amendment 1 (2026-10-31): PC pass 7 re-measure, rows 74 and 68
On the real GPU, the park took the Drownbell → Haluna return from 8.2–8.6 s to 2.87–3.03 s. What was left was the swap-in waiting on the shader prewarm (175 frames). A Drownbell fight start and a Ch6 entry also segfaulted (row 68), once next to a duplicate threaded load of one model.
- **The prewarm runs during the fight.** Once the park is built, the router emits `prewarm_requested` for it, and ShaderPrewarm stages its pipelines then. The swap-in of a prewarmed parked scene requests no second prewarm. If Return comes before the stage finishes, its swap hold makes the swap wait, as before.
  - Watch: pipeline compiles now happen during the battle, where they can be visible hitches. ShaderPrewarm's time slicing (`materials_per_frame`, `slice_budget_ms`) still applies. The PC should measure battle frames during a cross-zone fight.
- **One family of loads at a time.**
  - With the park on, the router no longer requests the return scene beside the battle's own threaded instantiate (`_prewarm_return`).
  - ReturnPark loads the scene, then the zone's runtime loads (ResidentLoads), then instantiates. Nothing overlaps the battle's entry, or the scene load.
- **The add frame is lighter.** `FieldCameraDirector.warm_triangles` builds big meshes' occlusion triangles on the instantiate worker. Haluna's root `_ready` went from 322 to 21 ms headless.
