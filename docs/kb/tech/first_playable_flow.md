# First-playable flow (M2-FP-03)

How the first playable strings its pieces together: **New Game → prologue → Haluna beach**, field
battles that open the CTB battle and come back, and the **end card** that returns to the title.
Code lives in `game/flow/` and `game/levels/prologue/`; tunables in
[`game/data/flow/first_playable.json`](../../../game/data/flow/first_playable.json)
(`FirstPlayableConfig.section(&"field_battle" | &"prologue" | &"end_card")`).

## New Game and the prologue

- `locations.json` lists `prologue` first and `new_game` is `{"location_id": "prologue", "spawn": "Start"}`.
  The title's `start_new_game()` does `Game.new_game()` then `WorldReturn.go_to(new_game)`, so nothing
  in the title changed.
- `game/levels/prologue/prologue.tscn` (`PrologueScene`) is a placeholder dead city at dusk built from
  primitives (white towers, one standing and one fallen arch, dead lamp-columns, seven vigil silhouettes
  on a terrace above drowned water; key, fill, sky and fog from color script `prologue_iskarra_dusk`).
  It has one `Camera3D` under a `FieldCameraDirector` (no player, `initial_shot` = P01), a
  `CutsceneStage` with `Shots/P01` (a FIXED `CameraShot`), and `Spawns/Start`.
- The root defines `place_at(spawn, yaw_deg := 0.0) -> bool` (returns true): `WorldReturn.place_player`
  calls it after the swap, and the location registry and `tools/validate_data.py` count the scene as
  playable. (M2-FP-03 fixed the validator to read the root's `script = ExtResource(..)` property line,
  which is how Godot saves it; before, only a header attribute counted.)
- When it is the current scene and `autoplay` is on, it runs `play()`:
  1. `Game.set_flag(&"prologue_seen")`;
  2. `await sequencer.play(&"prologue_dead_city", stage)` (a `CutsceneSequencer` child made on demand;
     tests inject an `instant` one);
  3. waits until `SceneRouter.is_busy()` is false (a short cutscene can end while the router is still
     finishing its own swap, and the router drops a change made meanwhile);
  4. `hand_off()`: `SceneRouter.world_return.go_to(&"ch01/oruvel_underway", &"Drop")` (from the data file; it was `ch02/haluna` `Beach` until M3-C01-02, and Ch1's own end now goes there),
     emitting `handed_off(location_id, spawn)`. It happens once.
- Injection points: `autoplay` (export), `sequencer`, `travel: Callable(location_id, spawn) -> bool`.
- The script is `game/data/dialogue/prologue/prologue_dead_city.dlg`: letterbox, `@camera P01`, fade in,
  a held wait, the SPEC §3.5 line as `Narrator(rhen) [tender]: ... #vo`, a held wait, fade out. No other
  story is added.
- While `ch02/haluna` is still the not-playable mood stand-in, `go_to` falls back to the default
  location (warned, as for Continue). Once the playable zone row lands with a `Beach` spawn, the
  hand-off goes there with no code change.

## Field battles: `BattleRequest` and `FieldBattle`

```gdscript
# from a zone, an interactable, or after a cutscene's <<event start_battle ...>>:
BattleRequest.start(&"ch02_tideline", &"ch02/haluna", &"Beach", &"some_declared_flag")
```

`BattleRequest` (`game/flow/battle_request.gd`, RefCounted):

| API | Meaning |
|---|---|
| `static start(encounter, return_location, return_spawn, victory_flag := &"", escape_at := &"") -> BattleRequest` | `make()` + `submit()`: records the request and opens the field battle scene through `SceneRouter.change_scene`. Returns the request (adjust `active`/`reserve`/`rng_seed` at once if needed). |
| `static make(...) -> BattleRequest` | Builds one with the data file's party (`active` [rhen, asha], `reserve` [toma]) and `seed`; records nothing. |
| `static submit(r)` | Records `r` and opens `field_battle.scene`. |
| `static pending()`, `take()`, `clear()` | The one waiting request; `take()` returns and forgets it. |
| `static change_scene: Callable(path)` | Test hook; unset = the router. |
| fields | `encounter`, `active`, `reserve`, `rng_seed`, `return_location`, `return_spawn`, `victory_flag`, `escape_spawn` (M2-FP-05; empty = `return_spawn`) |

`FieldBattle` (`game/flow/field_battle.gd`, `extends BattleController`) and `field_battle.tscn`, an
**inherited scene** of `battle_sandbox.tscn` whose root uses the script; no Combat or UI file is edited.

- **Start:** `start_sandbox()` (what the sandbox's `_ready` calls, staged behind the router's fade) takes
  the pending request and calls `start_request(r, rng_seed := -1, staged := false)`. The fight is live:
  `persist_progress` stays on, so `BattleVitals` carries HP/MP in and out, items come from the real
  inventory and Lattice gains are saved. With no request pending it is the plain sandbox fight.
- **Result panel:** after a victory or an escape it is re-shown with **Return only** (a story fight is not
  replayed). After a defeat (M2-FP-05) it offers **Fight again** (same start; `BattleVitals` records
  nothing on a defeat) and **Return to last save** (`CHOICE_LAST_SAVE`, `FLOW_RESULT_LAST_SAVE`; it reads
  **Return to title**, `FLOW_RESULT_TITLE`, when there is no save record).
- **Return** → `return_to_field() -> bool`: sets `victory_flag` with `Game.set_flag` on a victory only,
  then `SceneRouter.world_return.go_to(return_location, spawn)`, where `spawn` is `return_spawn`, or
  `escape_spawn` after an escape when the request names one. It runs once, and never after a defeat, so
  a field trigger cannot be walked past by losing.
- **Return to last save** → `return_to_last_save() -> Error` (defeat only, once): loads the newest
  readable record, autosave included, with `TitleSaveEntry.continue_game` (the title's Continue). In the
  game `WorldReturn` is armed and routes on `EventBus.game_loaded`; when it is not (a scene opened on its
  own, tests) FieldBattle travels to `WorldReturn.resolve(Game.state)` itself. With no record it opens
  the title (`RETURN_SCENE`, `res://game/core/boot.tscn`).
- **Haluna:** the story passes `first_playable.json` `haluna.battle_escape_spawn` (`BeforeBattle`, on the
  beach 5 m seaward of the trigger strip, facing it) as the escape spawn, so the party reaches
  `BattleReturn`, past the strip, only by winning. Known gap: a save record made in Haluna before the
  win with no respawn (a chapter autosave; none is written in the first playable today) would continue at
  the location's own spawn, `Shrine`, past the strip.
- Injection points: `request`, `travel: Callable(location_id, spawn) -> bool`, `open_title: Callable(path)`,
  `save_system` (null = the autoload), plus the controller's own
  `auto_start` / `pacing_scale`.
- `WorldReturn.go_to` does not need `enabled` (that only gates the return on load), so field travel works
  in the game and is recorded in tests.

### `ch02_tideline`

`encounters.json` row `ch02_tideline` (reef_crab + lantern_eel, `scripted: false` so it can be fled,
name `ENC_CH02_TIDELINE`). BattleSim, 500 seeds, rhen + asha with toma in reserve, new-game strength
(bare and `m1_starting` gave the same picture): every policy wins 100%; mean 9.6 to 10.6 turns, p90 12;
plain attacking (`naive`) loses a party member in about 1 fight in 5 (mean party KO 0.19), `smart` never
does. Comfortable, not free: a first field fight before the Ch3 boss bands.

## End card

`EndCard` (`game/flow/end_card.gd`, `end_card.tscn`): black screen, `FLOW_END_CARD_TITLE`
(`BannerLabel`), `FLOW_END_CARD_LINE` (`BodyLabel`) and `FLOW_END_CARD_PROMPT` (`HelpLabel`), fading in
over `fade_in_sec`. After `min_hold_sec`, the prompt shows and `ui_accept` calls `accept()`, which
emits `returning(scene_path)` and changes scene to `return_scene` (`res://game/core/boot.tscn`, the
title) once.

- Show it: `EndCard.open()` or `SceneRouter.change_scene(EndCard.SCENE)`.
- Test hooks: `change_scene: Callable(path)`, `advance(delta)`, `handle_input(event)`, `prompt_shown()`.

## Haluna's slice beats (M2-FP-13)

`HalunaStory` plays three more beats from the vertical-slice beat sheet, all in-engine (no letterbox, no camera cues), with their data in `first_playable.json` `haluna`:
- **B02, Neme's table** (`after_battle_scene_id` `ch02_nemes_table`). It plays from `begin()` on the first arrival after the tideline victory (`battle_victory_flag`), while `after_battle_flag` (`ch02_ate_at_nemes`, which the scene sets) is still unset. Rhen is placed at `after_battle_spawn` (Village, by Neme's stand-in). The scene opens black (`@fade in`), so the move is never seen.
  - The beach path is closed until the fight is won, so this keeps the order dawn → walk up → fight → noon at Neme's.
- **B03, the four "Cantor" fragments.** Each is a one-shot TOUCH trigger (`Triggers/Overhear*`, payload `{"dialogue": ..., "overheard": true}`, after `ch02_met_asha`) around the market, chapel, dock and lane villagers.
  - They play on a second sequencer, `HalunaStory.overhear`, with `hold_player = false` and `auto_advance` (lines hold `overheard_hold_sec`). Rhen walks on, `busy` stays false, and nothing is blocked.
  - Anything else that starts (a villager bark, the battle, the causeway) cuts it off with `_hush()`.
  - Talking to the villager still plays the bark. The lane child (`ch02_bark_lane`) is new.
- **B05, Low tide** (`before_ending_scene_id` `ch02_low_tide`). The causeway-head trigger plays it, then hands off to Cutscene B.
  - **M2-FP-21:** B05 opens on Asha's question and a "Go now" / "Not yet" choice. "Not yet" plays her reply and `<<event departure_declined>>` (`haluna.ending_decline_event`); `HalunaStory._end()` then puts Rhen at `ending_decline_spawn` (`CausewayHead`, short of the box), clears `busy` and hands nothing off. The trigger is not `once`, so the next walk-in asks again. "Go now" runs B05 to its end and hands off as before (tests take it by default: `auto_choice = 0`).
  - **M2-FP-20:** before the first save, `Triggers/CausewayHeadUnsaved` (the same box, blocked by `ch02_saved_once`) plays the overheard `ch02_bark_causeway_unsaved` (Toma and Asha point Rhen to the town shrine). It is not `once`: it plays on every walk-in until the save, but never over itself (the overhear sequencer must be idle).

New speakers: `neme`, `child`. Tests: `tests/integration/test_haluna_slice_beats.gd`.

## The Shell Shrine trial and the dock at night (M2-FP-16, M2-FP-15)

The thread's end now runs: the causeway head → B05 → **the Shell Shrine trial** (`haluna.ending_scene`; game/levels/ch03/shell_shrine/README.md) → through its door, Cutscene B (`shell_shrine.next_scene`) → the Drownbell → **Haluna's dock at night** → the end card.
- After the Drownbell, `first_verse.after_location` / `after_spawn` send the party back to `ch02/haluna` at `DockNight` instead of opening the end card. (`after_scene` is now used only on the no-battle path.)
- On that arrival, `HalunaStory.begin()` plays B11, because `night_flag` (`ch03_drownbell_defeated`) is set and `sworn_flag` (`ch03_rhen_sworn_guardian`) isn't:
  - `HalunaZone.set_night(haluna.night, haluna.night_hide)` puts up the **stand-in night** until M2-ENV-02. The mood sun is dimmed and turned moonlight blue. A *copy* of the mood's Environment gets a darker sky and less ambient light, so the shared `.tres` is never touched. Warm lamps go up, and the dock villagers are gone home.
  - `place_cast(night_cast, night_marks)` sits Asha at the end of the dock and puts Toma at the landward end, with the mark he walks to.
  - `ch03_dock_at_night` plays in-engine; Toma's `@mark` walk is his arrival. The scene sets the sworn flag, and the story hands off to `night_end_scene` (the end card).
- Once sworn, the villagers' barks (and the overheard fragments) play their `night_barks` blessings.

## Tests

`tests/integration/test_fp_field_battle.gd`, `tests/integration/test_fp_prologue.gd`,
`tests/unit/test_fp_end_card.gd` (`-- --filter=test_fp`), and `tools/tests/test_fp_scene_place_at.py`.
The prologue test relies on an `instant` sequencer finishing `play()` without yielding (true of the
stub); if the presentation body ever yields in instant mode, drive it with `await` from a test that the
runner can wait on, or keep instant mode synchronous.

## Hand-offs never get lost (M2-FP-09, review-sweep-K)

`SceneRouter.change_scene` ignores a request made while another swap is running (it warns and returns), and `WorldReturn.go_to` can't tell. A flow step that set its "done" latch before such a call could strand the player. So every first-playable hand-off goes through **`FlowRouting`** (`game/flow/flow_routing.gd`):
- `when_free(change)` waits a frame at a time until the router is idle, then makes the change exactly once.
- `change_scene(path)` and `go_to(location, spawn)` are its two forms.

The callers are `FieldBattle` (return to the field, the last save, the title or the end card), `EndCard`, `BattleRequest.submit`, `HalunaStory` and `FirstVerseScene`. `tests/unit/test_flow_routing.gd` drives a busy router by hand, and fails if any of these files calls `SceneRouter.change_scene` directly. Test hooks: `busy`, `next_frame` and `record`.

Also in M2-FP-09:
- `HalunaZone` reads the arrival flag from `first_playable.json` (`haluna.intro_flag`).
- The zone sun follows the close-up lighting rule (`face_key_shadow_normal_bias` 3.0 on the zone root; character_shading.md "Shadows on characters"), and so does the first-verse set's sun.
- `tests/integration/test_fp_thread.gd` now covers the full loop on real data:
  - it drives the story's real trigger and request;
  - it loses twice, using Fight again between, then Return to last save;
  - it wins, then saves at the shrine and loads the record back;
  - it calls the Drownbell and reaches the end card.
- `test_the_battle_strip_cannot_be_walked_around` checks that every line from the beach to the shrine crosses the strip, and that walking inland from the causeway head is stopped.
