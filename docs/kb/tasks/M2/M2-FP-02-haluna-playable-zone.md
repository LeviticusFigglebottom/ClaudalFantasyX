---
id: M2-FP-02
title: Playable Haluna zone (player, collision, camera volumes, villagers, shrine, triggers)
role: environment
status: done
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ENV-01, M1-ARC-06]
milestone: M2
request-from: lead
---
## Goal
`game/levels/ch02/haluna/haluna.tscn`: the Environment-owned mood scene instanced (not edited) with a player, terrain and building collision, camera volumes, spawns, 3 talkable villagers, the save shrine, a scripted battle trigger and the causeway-head trigger, plus a CutsceneStage for Cutscene A.

## Acceptance criteria
- [x] Rhen (placeholder) walks the beach, lanes and court with collision, under authored camera volumes.
- [x] Spawns: Beach, Shrine, Village, BattleReturn, CausewayHead. `locations.json` row `ch02/haluna` points at the new scene and is playable.
- [x] Three villagers with short bark scenes (the B03 "Cantor" fragments).
- [x] Tests: the zone loads, the player stands on ground at every spawn, interactables fire their payloads.

## Notes (environment worktree, 2026-10-23)
- Built: `game/levels/ch02/haluna/` (`haluna.tscn`, `HalunaZone`, `HalunaCollision`, `HalunaActorPose`,
  README with every node path and position). The mood scene is instanced, never edited; its five shot
  cameras are released at runtime and the zone's `FieldCamera` is made current.
- Collision is built at runtime from the mood scene (~100 ms, ~550 shapes): heightmap ground over the
  walkable core, oriented boxes / trunk cylinders per kit piece (lane gates open), the dock as trimesh +
  deck floor, rails and a ramp, and a sea wall 5 m past the waterline.
- Camera: composed pan-follow volumes for the beach (two), H02 lane, H09 market, H04 dock, H07 chapel
  court and the shrine; a whole-zone hub `ORBIT` fallback (`hub_orbit_enabled`, Q/R).
- Villagers `npc_market` / `npc_chapel` / `npc_dock` with `ch02_bark_{market,chapel,dock}.dlg` (new
  speakers `vendor`, `reed`, `netmender`, `fisher`); prompt key `FIELD_PROMPT_LISTEN`.
- Triggers `tideline_battle` (a strip seaward of the beach-head tide wall covering every lane gate) and
  `causeway_head`, authored only: no code reacts to them here. `ch02_tideline_won` declared.
- `CutsceneStage` for Cutscene A: Shots H05/H06/H01, Actors asha (asha.glb, still kneeling pose) and toma
  (capsule + spear), Marks kneel_beside_rhen / beach_path / rhen_shallows / rhen_lantern. The test walks
  every cue of `ch02_girl_on_the_beach` and checks each target resolves.
- **M1-ENV-06:** this completes its intent. `ch02/haluna` now points at `haluna.tscn` (no `playable:
  false`, no `_note`); `test_haluna_shrine.gd` and `test_world_return.gd` are updated. One deviation:
  the SaveShrine stays inside `haluna_mood.tscn` (Environment-owned, not edited here) and reaches the
  playable zone through the instance; `check_locations` passes. M1-ENV-06 can be closed by its owner.
- Tests: `tests/integration/test_haluna_zone.gd` (`-- --filter=haluna`).

## Notes (handoff)
- Ready for review by **art** / **environment**. Known: loading the zone costs one ~1.5 s frame under the router fade (mood dressing + collision); the hub orbit fallback can clip roofs (no camera collision).

## Review log
- 2026-10-23 environment (review-sweep-K, fresh reviewer): **approve with should-fixes.** No blockers.
  - **What I read:** the task, handoff first-playable-1, `git diff 2ddca3f^1 2ddca3f -- game/levels/ch02 tests/integration/test_haluna_zone.gd tests/unit/test_haluna_shrine.gd tests/unit/test_world_return.gd`, the zone README, and the trigger and spawn blocks of haluna.tscn (:440-455, :567-612).
  - **Checks:** Godot `--filter=haluna` 7/0 failed, `world_return` 17/0, `fp_` 15/0 (test_fp_thread walks the zone). `validate_data` 0/0 (check_locations passes).
  - **What passes:**
    - The mood scene is instanced and never edited.
    - Triggers are gated by data: `requires_flag ch02_met_asha` and `blocked_by_flag ch02_tideline_won` (haluna.tscn:571-572).
    - BattleReturn (−24, 6.5) is about 2.3 m inland of strip 2 (x ≈ −20.4 ± 1.75), so the return never lands inside the trigger.
  - **Should-fix:**
    - **S1: Asha's face lighting.** haluna_mood.tscn:83 sets `shadow_normal_bias = 1.0` on the Sun, and that sun lights Asha at dialogue range in Cutscene A. character_shading.md:184 (M1-QA-05) says lights that key a face need 2.5–3.0, or the cheek terminator banding comes back. The mood scene is Environment-owned, so open a request task, or override the bias in `HalunaZone._ready` for the cutscene.
    - **S2: duplicated flag.** haluna_zone.gd:31 hard-codes `&"ch02_met_asha"`. first_playable.json `haluna.intro_flag` already names it, so read it through FirstPlayableConfig, or the two will drift.
    - **S3: no test proves the strip can't be bypassed.** README:63 says "any way up from the beach to the village crosses it", but no test checks that. test_fp_thread only walks straight −X from Beach. The causeway head is on the beach side (README:35), so this is what forces the fight (see M2-FP-04 B1). A small test should walk from BattleReturn to CausewayHead along the lanes and assert the trigger fires.
    - **S4: the 1.5 s load frame (known).** File a task to bake or time-slice HalunaCollision (~550 shapes at load). The router logs it over budget, and SPEC §4.2's 50 ms transition limit applies once prewarm is sliced (M1-RND-15).
- 2026-10-23 lead: closing on review-sweep-K approve; the should-fixes are in M2-FP-05 (FP), M1-ARC-15 (graphics settings never applied) or the PC queue (QA-05 re-run).
