# Field and cutscene hero hooks, for the hero integration track

m2-slice wrote this on 2026-10-24 for the new **hero integration** track, which owns swapping the capsules for the real Rhen, Asha and Toma models in the field and in battle. It lists every place a hero capsule is made or driven today, so that track can take the swap without duplicating anything. m2-slice owns the zone code named here. **The hero integration track has m2-slice's OK to edit these hook points directly**, or to name the API it wants and m2-slice will wire it.

## Where the hero capsules are built
| Where | What | Node |
|---|---|---|
| Greybox zones (Ch1, Ch3 causeway, Ch4–Ch9): `game/world/zone/greybox_zone.gd` `_build_player()` | The controlled hero: a `FieldController` named `Player`, with a `CapsuleShape3D` and a `CapsuleMesh` from `greybox_defaults.json` `player` | `<zone>/Player` |
| Greybox zones: `greybox_zone.gd` `_build_stage()` | Cutscene and story actors: one `Node3D` per layout `actors` row, named by its speaker id (`rhen`, `asha`, `toma`, …), with a `CapsuleMesh` from `greybox_defaults.json` `actor` | `<zone>/CutsceneStage/Actors/<id>` |
| Haluna (`game/levels/ch02/haluna/haluna.tscn`) | `Player` (`Mesh_rhen`), the cast under the stage (`Mesh_toma`, …) and villager capsules | hand-placed in the `.tscn` |
| Shell Shrine (`game/levels/ch03/shell_shrine/shell_shrine.tscn`), First Verse (`game/levels/ch03/first_verse/first_verse.tscn`) | Player and cast capsules | hand-placed |

Both greybox builders go through `_capsule_mesh(d)`. One seam covers every greybox zone: a hero body scene per id, put on the `Player` (for the party leader) or on the `Actors/<id>` node in place of `_capsule_mesh`, with the capsule kept as the fallback for anyone without a body.

## What drives them
- **Moving and turning:** `CutsceneSequencer` moves and turns the actor's **root node** (`global_position`, `rotation.y`). For a `FieldController` it also sets `motor.facing_yaw`. A body scene must be a child that follows the root; never move the body itself.
- **Clips:** `CutsceneSequencer._play_clip` and `_cue_anim` find the first `AnimationPlayer` under the actor (`find_child("AnimationPlayer")`) and play:
  - `sequencer.json` `clips` by role: idle, talk, walk, run;
  - `@anim <id> <clip>` by name.

  Since M2-FP-29 they cross-fade over `clip_blend_sec` (0.25 s). If the track drives the bodies with an AnimationTree, give the sequencer one entry point instead, such as `play_clip(name, blend)` on the body. Point m2-slice at it and m2-slice will switch the sequencer to it. The walk's start and stop now accelerate and decelerate (`walk_accel_sec` / `walk_decel_sec`), so a locomotion blend driven by speed will look right.
- **Faces:** `sequencer.json` `face_poses` and `lipsync.json`. These are the character track's, already wired.
- **Missing clips:** about 100 Act I clips are requested in `assets_src/characters/requested_clips.json` (M3-CHR-01). Calls to them are skipped until they exist.

## Field walking
`FieldController` (`game/world/field_controller.gd`) and its motor drive the player from input. Field encounters (`FieldEncounters`) and story triggers read only `player.global_position`. Anything that places the player (`place_at`) calls `encounters.reanchor()` (M2-FP-28), so a body swap that re-parents or re-places the player should go through `place_at`.
