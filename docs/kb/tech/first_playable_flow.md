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
  4. `hand_off()`: `SceneRouter.world_return.go_to(&"ch02/haluna", &"Beach")` (from the data file),
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

## Tests

`tests/integration/test_fp_field_battle.gd`, `tests/integration/test_fp_prologue.gd`,
`tests/unit/test_fp_end_card.gd` (`-- --filter=test_fp`), and `tools/tests/test_fp_scene_place_at.py`.
The prologue test relies on an `instant` sequencer finishing `play()` without yielding (true of the
stub); if the presentation body ever yields in instant mode, drive it with `await` from a test that the
runner can wait on, or keep instant mode synchronous.
