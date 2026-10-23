---
id: M2-FP-02
title: Playable Haluna zone (player, collision, camera volumes, villagers, shrine, triggers)
role: environment
status: doing
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

## Review log
