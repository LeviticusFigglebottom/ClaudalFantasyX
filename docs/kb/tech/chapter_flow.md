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
| `encounters` | `{table: [{encounter, weight}], min_m, max_m, when, seed, grace_m, max_step_m}` | `Encounters` (`FieldEncounters`): a random field battle every `min_m`–`max_m` metres walked (seeded; stretched by the party's `encounter_rate_pct`, e.g. Light Step), only while `when` holds and the story is free. It returns to the built-in `Encounter` spawn, where Rhen stood (M2-FP-25). The meter is kept per location across the battle round trip (`FieldEncounters.meters`; a new or loaded game clears it). After each battle `grace_m` must be walked before it runs again, a placement re-anchors the walk, and a frame's jump over `max_step_m` never counts. Both default to `greybox_defaults.json` `encounters` (M2-FP-28) |
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

## Ch5 (M3-C05-02)
Ch5 "Terraces of Ash" follows Ch1's pattern: `game/data/flow/chapters/ch05.json`, two zones under `game/levels/ch05/`, scripts in `game/data/dialogue/ch05/`, loc rows in `game/data/loc/ch05.csv`, and the test `tests/integration/test_ch05_thread.gd`.

**The zone roots.**
- `Ch05Zone` extends `Ch01Zone`, so it keeps `rest`, `give`, `prompt` and `hide_block`/`show_block`. It adds:
  - `give_if(flag, items, lume)`: `give` only while the flag is set. B04's "Not yet" gives the key item `pemakar_leaf_boat` this way, since an `if_event` would end the run.
  - `place_actor(id, mark)`: a cut, not a walk. Kerrid is at the inn gate when the party comes back in B11.
  - The layout's `variants`: rows of `{when, sun, environment, hide, show}`, applied over the layout's own light on `_ready` (and by `apply_variant()`). Pemakar's layout is Lanternfall night; the day after the binding is a variant.
- `Ch05AshcrownZone` is the view of `AshcrownTrial` (`game/levels/ch05/ashcrown/ashcrown_trial.gd`; data `game/data/trials/ashcrown.json`), like ShellShrineLevel and ShellShrineTrial.
  - Its triggers carry `{"trial": catch|turn|stand|release, "id": piece}` payloads. The zone root listens for them itself (ZoneStory ignores them), and only while `ch05_trial_begun` is set and the story is free.
  - It reports the metres the player walks to the trial: the stud ring is a step budget, not a timer.
  - It sets the trial's flags: `ch05_quench_alcove_open` on the sealed vein, `ch05_strike_landed` on the landing.
  - A zone entered after the landing builds the trial solved.

**Entry and exit.**
- **Entry:** `ch05/pemakar` at `Harbour`, which is also the location's own spawn, so Ch5 can be entered directly (F5). Ch4 (M3-C04-02) should hand off with `{"go": {"location": "ch05/pemakar", "spawn": "Harbour"}}`. A party Ch4 leaves is kept. An empty one is filled with Rhen, Asha and Toma, with Ysolde in reserve.
- **Kerrid** joins with a `party` step at the end of B05: active Rhen, Asha and Kerrid; reserve Toma and Ysolde.
- **Exit:** the dawn beat goes to Ch6's `ch06/brine_shoals` at `Entry` (M3-C06-02).

## Ch7 (M3-C07-02)
Ch7 "The Tidecup" is built the same way: `game/data/flow/chapters/ch07.json`, two zones under `game/levels/ch07/`, scripts in `game/data/dialogue/ch07/`, the loc table `game/data/loc/ch07.csv`, and the test `tests/integration/test_ch07_thread.gd`.

**The zones.** `ch07/tamsule` is the port. `ch07/tamsule_bell_galleries` is the story's greybox **stand-in** for the Bell's galleries, catch-pool and moorings. The arena, `ch07/tamsule_bell`, is env-art's and the Reefball agent's. Both zones use `Ch07Zone`, which is `Ch01Zone` (give, rest, hide_block and show_block) plus two calls:
- `checkpoint(spawn)`: B04's autosave before the naming. It moves the respawn point and calls `SaveSystem.request_autosave`.
- `stand(actor, mark)`: puts an actor on a mark with no walk, so Tavi is at his boat when the Bell is entered after B07.

**The Reefball seam.** B05 (`ch07_naming.dlg`) ends on `<<event start_reefball tidecup_opening>>`, declared in `events.json`. The zone's `naming` beat reads it with `{"if_event": "start_reefball", "steps": [{"beat": "reefball_match"}]}`, and `reefball_match` is one `scene` step to `game/levels/ch07/tidecup_match/tidecup_match.tscn` (M3-C07-1206). `TidecupMatch` frames the Reefball engine's story match (data `game/data/flow/ch07_tidecup.json`):
- it plays the match through the Reefball HUD and its controller (M3-UI-01) when they are in the build, loaded by path until the UI track's branch lands; otherwise the engine's AI plays both sides at once (a headless fallback);
- at the end it sets `ch07_tidecup_played` always, and `ch07_tidecup_won` plus the win reward on a win only (a draw counts as a loss for rewards);
- it returns to `ch07/tamsule_bell_galleries` at `CatchPool`.

The zone's first arrival row then plays B07 the same either way. No story `.dlg` and no chapter flow may read `ch07_tidecup_won`. The test enforces it, and its `REWARD_SCRIPTS` lists any script that gives the reward. `test_ch07_tidecup_match` covers the win, loss and draw paths.

**Seams to other chapters.**
- **Entry:** Ch6's dawn (B10) hands off to `ch07/tamsule` at `RiverMouth`; the location row and the F5 teleport reach it directly too.
- **Exit:** B10 hands off to `ch08/corrow` at `Mole` (M3-C08-02).

## Ch4 (M3-C04-02)
Ch4 "The Pilgrim's Wake" is built the same way: `game/data/flow/chapters/ch04.json`, two zones under `game/levels/ch04/`, scripts in `game/data/dialogue/ch04/`, loc rows in `game/data/loc/ch04.csv`, and the test `tests/integration/test_ch04_thread.gd`.

**Haluna's wake night is a stand-in zone, `ch04/haluna_wake`.** HalunaStory owns `ch02/haluna` and isn't data-driven, and ADR 0035 says new chapters use ZoneStory and must not copy HalunaStory. Giving HalunaStory a data hook would put Ch4's night on the slice's code path (test_fp_thread, test_haluna_*). So the night is its own greybox location: Neme's door, the lane, the market and the closed inn, the chapel court, the dock, and the causeway head with the wake-shell wall. When Haluna moves to ZoneStory, the zone block moves to `ch02/haluna` unchanged, and env-art's wake-night dressing (M3-C04-03) lands on the real Haluna.

**The entry.** The wake opens once B11 has sworn Rhen in (`ch03_rhen_sworn_guardian`). In the M2 build the slice's end card still returns to the title; the full game's hand-off from the end card is M3-C04-04. Until then Ch4 is reached at its own location (locations.json, and the F5 debug teleports).

**The exit.** `ch05/pemakar` isn't on this branch, so the ferry's last step is `{"scene": "res://game/flow/end_card.tscn"}` as a stand-in. Repoint it to `{"go": {"location": "ch05/pemakar", "spawn": ...}}` when Ch5 merges (M3-C04-04).

**The zone root.** `Ch04Zone` extends Ch01Zone (rest, give, hide_block / show_block) and adds the layout's `states`: `[{flag, hide, show, place: {actor: mark}}]`, applied in order when the zone is ready and again by a `{"zone": "refresh_states"}` step. A battle reloads the zone, so the dressing and the party's stand-ins (on the ferry, across on the derelict, back aboard) follow the flags. `tools/tests/test_ch04_validate.py` checks the rows' flags, ids and marks, because the shared validator doesn't read `states` yet.

**The ferry is never attacked (ADR 0017 (d)).** There is no walkway between the ferry and the derelict, and the layout's random fights run only while `ch04_boarded_derelict` is set and `ch04_spar_wraith_defeated` isn't. The test walks 500 m on the ferry and asserts that nothing fires.

**Battle prompts in sequence.** An encounter may name a second prompt for one hero's first turn (`turn_prompt_hero`, `turn_prompt_key`; BattleBossHud). The bottle-hermit opens on the swap prompt and shows Read on Ysolde's first turn.

## Ch9 (M3-C09-02)
Ch9 "The Ebbing", the end of Act I, is built the same way: `game/data/flow/chapters/ch09.json`, one zone under `game/levels/ch09/`, scripts in `game/data/dialogue/ch09/`, loc rows in `game/data/loc/ch09.csv`, tunables in `game/data/flow/ch09_field.json`, and the test `tests/integration/test_ch09_thread.gd`. Ch9 has no fight of any kind (act1_ch09.md rule 5): no encounters, no `battle` step, no `sim.py` suite.

**The zone is a stand-in, `ch09/corrow_night`.** The sheet stages Ch9 on the `ch08/corrow` night variant, and Ch8 isn't built (it waits on a combat task). So Ch9 has its own greybox location: the strand of shrouds, the broken wall and the flooded low town, the raft's landing, the Fisher Stair, and the dawn road with its milestone. When Ch8 lands, it either hosts this zone block as its night variant (move the block to `ch08/corrow` and add the layout's pieces) or hands off here with `{"go": {"location": "ch09/corrow_night", "spawn": "Strand"}}`.

**The zone root.** `Ch09Zone` extends `Ch05Zone`, so it keeps the light `variants`, `place_actor`, and Ch01Zone's calls. It adds three things:
- **Variant `place`.** A `variants` row may also stand actors on marks, `{actor: mark}`. The night is the layout's own light. Dawn is a row on `ch09_pell_joined`: the party on the road, Kerrid at the milestone, the stair empty.
- **The layout's `clip_marks`**, for `CutsceneStage.clip_marks`. `@anim asha pole_out` cuts Asha onto the raft mid-harbour until her rig has the clip.
- **The held input**, a `CutsceneHoldGate` on the story's sequencer (see below).

**Two scenes carry most of the chapter, a node per beat.** A `play` step that ends hands the camera back to the field, so beats that must cut into each other share a scene:
- `ch09_the_ebbing`: B03 the gilt line, B04/B05/B07 the three movements, B06 the stair cutaway, and B08 Pell;
- `ch09_the_road_out`: B09, then a **hard cut** to B10, the Iskarra vigil, then B11, the act card.

Flags inside them are set by `<<set>>` at the line that earns them.

**The Ebbing's held input** (act1_ch09.md B04–B07). Each movement sits between `<<event hold_input raise_staff>>` and `<<event hold_input_end>>` (events.json). Inside, `CutsceneHoldGate` runs the scene's time only while the field's interact action is held, and shows "Hold to raise the staff". There is no timing, no score and no fail: letting go pauses the dance, and nothing resets. How long each movement lasts is its own `@wait`s. `test_the_ebbing_cannot_fail` drives the whole scene in real time, waiting two minutes unheld at every gate.

**The Iskarra vigil is staged in the same zone.** The prologue scene is hard-wired to its own cutscene and hand-off, and a scene change fades through the router. So the vigil is a stand-in plaza far east in the zone (x 300), with its own seven stand-ins (`vigil_*`), the burner and shots P02–P04. Env-art decides the real staging (M3-C09-04).

**Seams.**
- **Entry:** Ch8's B18 hands off to `ch09/corrow_night` at `Strand` (M3-C08-02); its own `locations.json` row and the F5 teleport reach it too. The first arrival sets the chapter to 9, and the chapter autosave follows.
- **Ch8's flags.** Ch9 reads three flags that Ch8 must set: `ch08_met_ivo` (the side scene), `ch08_fed_the_beacon` (Fenn's line in B08, else Hobb's) and `ch08_hoist_cut_down` (Liss's bark). They are declared in flags.tres with that note. Ch9 doesn't read `ch08_stair_groups_up`.
- **The night to dawn.** The Ebbing's scene ends on black, and its beat goes to the same zone at `RoadGate`, so the zone reloads in its dawn variant.
- **Exit:** Ch10 (Act II) isn't in M3, so the act break hands off to the end card.

**Pell** has no `characters.json` row, so his joining is the flag `ch09_pell_joined` (and `ch09_pell_named` at B09). He is in no party list and no sim suite; his battle kit is M3-C09-07. The Ch9 party is Rhen, Asha and Toma, with Kerrid and Ysolde in reserve.

## Ch6 (M3-C06-02)
Ch6 "Salt Edict" is built the same way: `game/data/flow/chapters/ch06.json`, one zone under `game/levels/ch06/`, scripts in `game/data/dialogue/ch06/`, loc rows in `game/data/loc/ch06.csv`, and the test `tests/integration/test_ch06_thread.gd`.

**The zone.** `ch06/brine_shoals` holds the whole chapter: the wreck-ridges and the mud-flats (the road), the last ridge and the hold, the burning Saltwright camp, the shoal channel, the ridge camp and the tideline. Its root, `Ch06Zone`, extends Ch04Zone, so the layout's flag-driven `states` keep the raid's cast, the barge, the party and Liss right after the battle or a load. It adds two things:
- the layout's `lights`: rows of `{flag, sun, environment}` applied in order over the layout's own light, on `_ready` and in `refresh_states()`. The ridge camp's dusk uses it.
- `checkpoint(spawn)`: B08's shrine. It moves the respawn point and requests an autosave, as Ch7's does. The shrine beat is `rest` then `checkpoint`.

**Entry and exit.**
- **Entry:** `Entry`, which is also the location's own spawn. Ch5's dawn now hands off with `{"go": {"location": "ch06/brine_shoals", "spawn": "Entry"}}`. Ch5's party is kept (Rhen, Asha and Kerrid; Toma and Ysolde in reserve).
- **Exit:** B10 hands off to `ch07/tamsule` at `RiverMouth`.

**The fight and the barge.** The `raid` beat plays B02 and B03 and ends on the battle step for `ch06_inquisitor`, with Toma, Rhen and Asha on the field and Kerrid and Ysolde in reserve. The battle returns to `CampWaterline` with `ch06_inquisitor_yielded`, and the zone's first arrival row then plays B05 to B08 in one run: the barge, a `party` step that seats Liss in reserve after B06, the lantern, and the ridge camp. A `zone: refresh_states` step follows each scene that sets a flag a state reads.

**Two encounter rules (BossMechanics; battle_ctb.md "Encounter rules: forbidden skills and yielding foes").**
- `forbidden_skills` greys Toma's offensive skills against foes tagged `stillguard` (both the Inquisitor and the hound), and the engine refuses them with `forbidden`. `party_skills` lends him his guard (Stand Fast, Brace, Challenge, Shield Wall) so the fight works without a Lattice.
- `yield_at_hp_pct: 0` makes both foes yield on their feet at 0 HP: nobody dies. The encounter's `victory_key` sets the banner's title: "The Inquisitor yields."

**Random fights.** The layout has one table for the whole road. It runs between `ch06_arrived` and `ch06_sheltered_liss`, so the camp has none. GreyboxZone has a single `encounters` block, so the ridges and the flats share it; separate tables for the flats need a zone-root feature (M3-C06-05).

## Ch8 (M3-C08-02)
Ch8 "The Seawall" is built the same way: `game/data/flow/chapters/ch08.json`, two zones under `game/levels/ch08/`, scripts in `game/data/dialogue/ch08/`, rows in `game/data/loc/ch08.csv`, tunables in `game/data/flow/ch08_field.json`, and the tests `tests/integration/test_ch08_thread.gd` and `tools/tests/test_ch08_flow.py`.

**The zones.**
- `ch08/corrow` is Corrow by day, in the storm and after it: the harbour mole, the wall-head and its Watchers, the Fisher Stair, the low town and the Bastion. The storm and the aftermath are flag-driven `states` and `lights` (from `ch08_beacon_opened` and `ch08_wall_fell`), so a battle's reload or a load comes back right.
- `ch08/coilspire` is the headland path, the keeper's hut, the four tiers of the flue trial, the crown chamber and the beacon gallery.

**The zone roots.** `Ch08Zone` extends `Ch06Zone`, so it keeps the `states`, the `lights`, `checkpoint`, `place_actor` and Ch01Zone's calls. It adds three things:
- the layout's `start_hidden`: blocks built hidden for a state to show (the flood, the breach, the hoist, the storm wall);
- the layout's `states_when`: rows like `states` under a ZoneStory `when`, so every flag must hold. Fenn stands in the gallery only when he fed the beacon and Virel is bound.
- `mend(source)`: between the set piece's fights, every party member's carried HP is raised to at least `mend.hp_pct` of their battle maximum. The maximum is built the way a live battle builds it (Lattice, gear). MP is left alone.

`Ch08CoilspireZone` is the view of `CoilspireTrial` (`game/levels/ch08/coilspire/coilspire_trial.gd`; data in `ch08_field.json` `trial`), as Ashcrown's zone is of its trial.
- Its triggers carry `{"flue": key}`. They answer only after the door (`ch08_entered_coilspire`), while the flame isn't at the crown and the story is free.
- The climb is kept in the numeric flag `ch08_flue_tiers_lit`, so the two placed fights inside don't lose it.
- Tier 3's seized key plays the `stuck_key` beat (Liss and the mark) when Liss is in the party or the reserve, then turns.

**The set piece and the stair meter** (act1_ch08.md §5a; set_piece_battles.md).
- A battle step takes `objective_flag`, a numeric flag. ZoneStory records the flag's value on the request (`BattleRequest.objective_start`).
- After a win or a scripted escape, FieldBattle sets it to that value plus `engine.objective_count`. "Fight again" puts it back to that value.
- Every Ch8 fight carries `ch08_stair_groups_up`. Each fight returns to `WallHead`, and the next arrival row mends the party, plays the scene between and opens the next fight. Wave 1 follows B09's checkpoint, so "Return to last save" goes back to B09.
- The battle parties are the sim suites' (`tools/balance/targets.json` `ch08_*`), so the bands describe what the player plays.

**Seams.**
- **Entry:** Ch7's `leave` beat hands off to `ch08/corrow` at `Mole`, which is also the location's own spawn. B01's party step drops Kerrid: active Rhen, Asha and Toma; reserve Ysolde and Liss.
- **Exit:** B18 writes Kerrid back into the reserve and hands off to `ch09/corrow_night` at `Strand`. Ch9's zone stays its own location; whether it becomes `ch08/corrow`'s night variant is M3-C09-04's call.
- **Ch9's three Ch8 flags** (`ch08_met_ivo`, `ch08_fed_the_beacon`, `ch08_hoist_cut_down`) are set here. Ivo is on the critical path (the wall-gate needs `ch08_met_ivo`).

**Field fights.** The headland's random table and its forced fight are `ch08_headland_gulls` (two stormgulls, Rhen's) and `ch08_headland_crabs` (two wallcrabs, Toma's). The spire's two placed fights are `ch08_flue_moths` (Ysolde's frost). The three enemies are `enemies.json` rows on the creatures track's models (M3-CRE-06), with `sim.py` suites in `tools/balance/targets.json`. Liss's Haul and Virel's kit are still M3-CMB-01's provisional rows.

## Debug chapter select (M3-ARC-02)
F8 in the debug overlay (debug builds only) lists the starts in `game/data/debug/chapter_select.json`: Ch1, then each built chapter. Enter on a start:
1. begins a fresh game;
2. sets that start's `flags` (the story so far);
3. sets its `chapter` and `party`;
4. goes to its `location` at `spawn`. The chapter's zone story takes over from there.

`tools/chapter_flow_check.py` checks the starts: locations, spawns on greybox zones, heroes and declared flags. When a new chapter lands, add its start, and add its completion flags to every later start.

The slice's end card leads on to `end_card.next_location` / `next_spawn` in `first_playable.json` when they are set (M3-C04-04). They are empty for the M2 review build, so the card returns to the title.


## Kit dressing (ADR 0200, act1-chapters)
An Act I zone swaps its greybox look for env-art's kit with a `ZoneKitDressing` child (`game/levels/act1/zone_kit_dressing.gd`, a `HalunaDresser` subclass), instanced in the zone's `.tscn` as `Dressing`, with `Water` (`WaterSurface`) and `Tide` (`WeatheringTide`) beside it when the kit has water. The greybox stays the gameplay: collision, triggers, marks, spawns and `states` are unchanged.
- **The dressing layout** `game/levels/chNN/<zone>/<zone>_dressing.json` is generated by `tools/act1/chNN_<zone>_dressing.py` in the zone's own frame (HalunaDresser's `kit_dir`, `materials_dir`, LOD keys and `pieces`). Never edit the JSON by hand; re-run the generator after a kit merge.
- **Keys:** a piece's `"block": <id>` follows `Greybox/<id>`'s visibility (so `hide_block`/`show_block` and `states` drive it); `"collide": true` gives decor off the route a box collider; `greybox: {hide_all, keep}` hides the block meshes except the story blocks no kit has yet; `fire_lights` (shadowless, fog energy 0, optionally following a block, optionally their own `color`); `multimeshes` (many copies of one kit piece, e.g. Pemakar's leaf-boats) and `far_lights` (camera-facing light quads), both optionally following a block; `"collide": "trimesh"` / `"trimesh_lod0"` for walk surfaces and terrain; `environment` (a copied grade, `.tres` next to the zone); `time_of_day_h`. `KitWalkProbe` reads the kit's box colliders too, and with `check_kit` queries the physics space for the trimesh pieces along a route.
- **Heights:** the floor is still the flat greybox, so pieces sit near y = 0 (a raised hard is sunk). Water the player must not walk on is a new solid block in the zone's layout.
- **Shots:** `game/levels/_tests/act1_zones/<chNN_zone>_shots.tscn` (`Act1ZoneRig`: the zone with its story held, plus `views` built as `Cameras/<name>`).
- **On a kit's heights** (Corrow): the zone takes the kit's own frame, its story points moved once by a relayout script, and `KitCollision` (`game/levels/act1/kit_collision.gd`, used by Ch04Zone and Ch05Zone) adds the layout's `collision_path` file (generated blocks) and its `ramps` (stairs as slabs under 45°, built under `Greybox` so `hide_block` works on them). `tests/integration/kit_walk_probe.gd` (`KitWalkProbe`) walks a zone's routes on its built collision analytically.
- **Casts (M3-CIN-1217):** a stage actor row's `"cast": "<villager>"` puts that villager's actor scene on the actor (`ZoneCast`, a `Cast` node in each Act I zone .tscn), its capsule hidden, idling from its own phase; heroes get their bodies from `HeroFieldActor.attach_stage`.
- **Grades by state:** a Ch06Zone `lights` row or a Ch05Zone `variants` row may carry `environment_res` (a copied kit grade) to swap the zone's Environment (Corrow's fallen wall, Ch9's dawn).
- **Ch6 (M3-C06-1200):** the Brine Shoals kit; `tools/act1/ch06_brine_shoals_dressing.py`. The channel runs north up x = −24 from its silted head at z = −24 (`ChannelWater` keeps Rhen on the banks; the `Channel` spawn is on the east bank). The sun is the colour script's `ch06` frame.
- **Ch8 (M3-C08-1202):** Corrow on the seawall kit's heights (`tools/act1/corrow_frame.py`, `ch08_corrow_relayout.py`, `ch08_corrow_dressing.py`): the walk at y 12, the Fisher Stair on the wall's inner face, the low town at y 1, the Bastion a platform at walk height, the mole's ramp over the parapet; the fall hides the breach segment and the stair's upper flights.
- **Ch9 (M3-C09-1209):** Corrow's night in the same frame, the wall fallen (`tools/act1/ch09_corrow_night.py`, derived from Ch8's files: re-run Ch8's generator first).
- **Ch4 (M3-C04-1204):** the ferry and the Seventh Terrace (`tools/act1/ch04_ferry_dressing.py`): the ship's own frame at (0, 0, 10), the derelict at `bf_terrace.DERELICT_IN_FERRY`, the islet off the starboard gangway.
- **Ch5 (M3-C05-1213):** Pemakar on its kit's ten tiers (`tools/act1/ch05_pemakar_dressing.py`), the kit's frame: the harbour a quay at the shore with the Ch4 ferry alongside, the harbour road up the massif to the first flight, the market and forge on tier 0 by the stair (the smithy trades places with the house there), the inn on tier 2 (moved along its arc to x −6.6), the graves on tier 4, the crown channel on tier 9. The kit's tiers are dressing, not lanes: story points stay on a tier's lane (d 1.6 behind its front) near the stair. The Lanternfall night (lamps, leaf-boats, far and sea lights; ZoneKitDressing `multimeshes`, `far_lights`) follows the `Lamps` block, which the day variant hides; the day uses the kit's dusk grade until M3-ENV-1214.
- **Ch7 (M3-C07-1211):** the Bell's galleries on the Tamsule Bell kit (`tools/act1/ch07_tamsule_bell_dressing.py`), the kit's arena frame: the party's gallery is the west (Oruvel's), the rim trigger is on Oruvel's platform before the prow step where Tavi stands, Ione on Sorrin's prow east; Oruvel's moorings sit at azimuth 325 on the party's run of galleries (the two runs are parted by the boat lanes), a staging behind the posts and a bridge up to the walkway. Ch07Zone adds `KitCollision`. The area map (`zone_maps.json`) follows the moved POIs; it draws kit zones thinly until M3-UI-1212.

## Shared zones (Act III; M5-A3P-1001)
Act III comes back to earlier zones: Ch17 plays at Ch15's `ch17/hollowmere`, and Ch18 revisits Act I's towns. A zone
may have a block in more than one chapter file. `ChapterRegistry.zone()` picks the block from the listed files, in story
order: the first whose `chapter` ("ch17") is the story's current chapter or later, else the first that has the zone.
The current chapter is `Game.state.chapter`, which `ZoneStory` passes in.
- A zone reached on the way out of one chapter belongs to the next. The story is still chapter 16 when Ch16 hands off to
  Hollowmere, and the Ch17 block's arrive row sets chapter 17.
- A zone in a single file behaves as before.
- The layout is shared. Its triggers serve every file's beats, so gate each trigger with the flags of its own chapter
  (`requires_flag`, `blocked_by_flag`). `validate_data` checks a trigger's beat against all the files that have the zone.
- `tests/unit/test_chapter_registry.gd` and `tests/integration/test_ch17_thread.gd` (Ch15 and Ch17 at one zone) cover this.
