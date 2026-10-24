# Chapter flow and greybox zones (M3-ARC-01, ADR 0035)

How an Act I chapter is put together from data. It covers three pieces:
- **zones**: `GreyboxZone`, a scene root built from a layout file;
- **story**: `ZoneStory`, which plays the zone's block of a chapter file;
- **the registry**: `ChapterRegistry` and `game/data/flow/chapters.json`.

The slice (Haluna, the Shell Shrine, the first verse) still runs from `first_playable.json` (first_playable_flow.md).

## Adding a chapter
1. **Dialogue:** write the `.dlg` scripts under `game/data/dialogue/chNN/` and run `python3 tools/dlgc.py` to compile them.
2. **Zone scene:** make one per zone at `game/levels/chNN/<zone>/<zone>.tscn`. It needs only a root:
   ```
   [gd_scene format=3]
   [ext_resource type="Script" path="res://game/world/zone/greybox_zone.gd" id="1_zone"]
   [node name="Oruvel" type="Node3D"]
   script = ExtResource("1_zone")
   location_id = &"ch01/oruvel"
   layout_path = "res://game/levels/ch01/oruvel/oruvel_layout.json"
   ```
3. **Layout:** write the layout file (below), then add the zone to `locations.json`, with a `spawn` from the layout's spawns.
4. **Story:** write the chapter file `game/data/flow/chapters/chNN.json` (below) and append its `res://` path to `chapters.json` `files`.
5. **Flags and encounters:** declare every flag in `flags.tres` and add the encounters to `encounters.json`, with `sim.py` bands.
6. **Test:** write an integration test that drives the chapter headless from entry to exit (see `tests/integration/test_zone_story.gd` for the hooks: `autostart`, `active`, `sequencer.instant`, `hand_off`).
7. **Check:** run `python3 tools/validate_data.py`. It checks the chapter file and its layouts.

## Layout file
Every key is optional. Defaults come from `game/data/world/greybox_defaults.json`.

| Key | Shape | Built as |
|---|---|---|
| `blocks` | `[{id, pos: [x,y,z], size: [x,y,z], yaw, color, solid}]` | `Greybox/<id>`: a box mesh, plus a `StaticBody3D` and box collision unless `solid: false` |
| `spawns` | `{name: [x, y, z, yaw]}` | `Spawns/<name>` (`Marker3D`) |
| `marks` | `{id: [x, y, z, yaw]}` | `CutsceneStage/Marks/<id>` |
| `actors` | `{id: {at: [x,y,z,yaw], color, radius, height, hidden}}` | `CutsceneStage/Actors/<id>`, a capsule stand-in |
| `shots` | `{id: {pos, look_at, fov}}` | `CutsceneStage/Shots/<id>`, a FIXED `CameraShot` |
| `triggers` | `[{id, at, size, yaw, activation: touch\|interact, prompt_key, payload, requires_flag, blocked_by_flag, sets_flag, once}]` | `Triggers/<id>` (`Interactable`); size y 0 uses the default height |
| `camera_volumes` | `[{id, at, size, priority, mode: fixed\|pan_follow\|dolly, pos, look_at, fov, dolly: [[x,y,z]...], track: [[x,y,z]...]}]` | `CameraVolumes/<id>` (`CameraVolume`) with its shot; a dolly's rails go under `Rails/` (M2-FP-25) |
| `encounters` | `{table: [{encounter, weight}], min_m, max_m, when, seed}` | `Encounters` (`FieldEncounters`): a random field battle every `min_m`–`max_m` metres walked (seeded; stretched by the party's `encounter_rate_pct`, e.g. Light Step), only while `when` holds and the story is free. It returns to the built-in `Encounter` spawn, where Rhen stood (M2-FP-25) |
| blocks' `emission`, `emission_energy` | `#rrggbb`, float | an emissive block (a glint) |
| `camera`, `sun`, `environment`, `player`, `actor`, `block_color`, `shot_fov_deg`, `trigger_height` | as in the defaults | override the defaults |

## Chapter file
```json
{"chapter": "ch01", "zones": {"ch01/oruvel": {
  "party": {"party": ["rhen"], "reserve": []},
  "arrive": [{"when": {"unset": ["ch01_surfaced"]}, "steps": [{"place": "Dock"}, {"play": "ch01_surface"}, {"set": "ch01_surfaced"}]}],
  "beats": {"storm": {"when": {"set": ["ch01_kell_wick"]}, "steps": [{"play": "ch01_rising"}, {"battle": "ch01_hullgnaw", "return_spawn": "Raft", "victory_flag": "ch01_hullgnaw_won"}]}},
  "barks": [{"when": {"set": ["ch01_storm_seen"]}, "map": {"ch01_bark_net": "ch01_bark_net_after"}}]
}}}
```
- **Payloads:** a trigger or interactable runs a beat with `{"beat": id}`. `{"dialogue": id}` plays a bark, and adding `"overheard": true` lets Rhen walk on while it plays.
- **Steps:** the class comment in `game/flow/zone_story.gd` is the reference. A `battle`, `go` or `scene` step ends the run and must come last.
- **Battle party:** a battle uses the step's `party` and `reserve` when given, else the current party.
- **Chapters:** `{"chapter": n}` calls `Game.set_chapter(n)`. Put it in a chapter's first arrival, and the chapter autosave follows at the next safe point (M2-FP-27).
- **Back-out choices:** a choice that steps Rhen back is `{"if_event": "<event>", "steps": [{"place": "<spawn>"}]}` placed after the `play`.

## Limits
- There are no conditionals beyond `when` and `if_event`. Anything bigger, such as a puzzle or a wave meter, belongs on the zone root (a GreyboxZone subclass), reached with a `zone` step.
- Greybox collision is boxes only and the controller has no step-up, so keep walkable routes flat.

## Ch1 (M3-C01-02)
Ch1 "Lamp-Diver" is the first chapter built on this flow: `game/data/flow/chapters/ch01.json`, two zones under `game/levels/ch01/`, scripts in `game/data/dialogue/ch01/`, and the test `tests/integration/test_ch01_thread.gd`.

**The zone roots.** Both zones subclass GreyboxZone, so the generic class stays generic:
- `Ch01Zone` adds the story calls Ch1 needs, each reached with a `zone` step:
  - `rest(source)`: a full heal and no save, the request a shrine or an inn makes. Bell-rooms use it, and so does the breath before Hullgnaw.
  - `give(items, lume)`: a negative count takes an item away.
  - `prompt(id)`: a one-time tutorial prompt with a seen-flag, played on a hint sequencer that never holds the player.
  - `hide_block(id)` / `show_block(id)`: the block goes with its collision.
  - The layout's `fog` sets up the zone's fog.
- `Ch01UnderwayZone` adds the lantern and its shutter: a held `field_lantern_shutter`, F or the left face button.
  - Opening it widens the light and reveals the layout's `lantern.reveals` triggers and `lantern.curtains` blocks, for good.
  - `encounter_rate_mult()` exposes the shutter's rate for the field encounters.
- `Ch01OruvelZone` adds the storm variant, the layout's `storm` block:
  - it applies a storm light and the hide and show lists;
  - two lashing flags free the low hull;
  - a zone entered after `ch01_gulls_cried` comes up in the storm.
- Tuning lives in `game/data/flow/ch01_field.json`.

**The checks follow subclasses.** `chapter_flow_check.greybox_layout_path` and `validate_data.scene_has_player` follow a root script's `extends` chain (by path or class_name) to GreyboxZone, so a subclassed zone's layout and spawns are checked.

A battle step's own `party` is not a `party` step.

**Shared pieces still to come, and their placeholders (M2-FP-25, claude/m2-slice):**
- **The chapter step.** C1-01's `Game.set_chapter(1)` waits for the `{"chapter": 1}` step. It goes before `{"set": "ch01_started"}` in the Underway's arrival. Until then, Ch1 writes no chapter autosave.
- **Field random encounters.** The Underway's layout carries `encounters: {table, min_m, max_m}`, which is ignored until they land. Wiring the shutter's `encounter_rate_mult` into it is part of that merge.
- **Camera volumes.** Ch1 uses none yet.

**ZoneStory and fades.** A `play` step followed by a hand-off, with only set, place, party or zone steps between them, doesn't fade back in. A scene that ends on black (the shaft's rise, going under) hands off on black.

**The exit to Haluna.** Ch1 leaves an empty party, so Haluna seats Rhen, Asha and Toma after Cutscene A exactly as it did from a prologue start. Nothing in Ch2 changes.
