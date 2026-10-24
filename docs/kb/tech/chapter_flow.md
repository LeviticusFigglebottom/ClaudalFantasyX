# Chapter flow and greybox zones (M3-ARC-01, ADR 0033)

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
- **Back-out choices:** a choice that steps Rhen back is `{"if_event": "<event>", "steps": [{"place": "<spawn>"}]}` placed after the `play`.

## Limits
- There are no conditionals beyond `when` and `if_event`. Anything bigger, such as a puzzle or a wave meter, belongs on the zone root (a GreyboxZone subclass), reached with a `zone` step.
- Greybox collision is boxes only and the controller has no step-up, so keep walkable routes flat.
