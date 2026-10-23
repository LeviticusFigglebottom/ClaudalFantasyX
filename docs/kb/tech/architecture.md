# Runtime Architecture (M0)

## Autoloads (`project.godot`)
| Name | Script | Purpose |
|---|---|---|
| `EventBus` | `game/core/event_bus.gd` | Decoupled signals: battle start/end, flag changes, dialogue events, scene change, save/load. |
| `Game` | `game/core/game.gd` | Owns the live `GameStateData` and the `FlagRegistry`. `get_flag` / `set_flag` reject undeclared flags at runtime, and the validator rejects them in CI. |
| `SaveSystem` | `game/core/save_system.gd` | Versioned JSON saves (`user://saves/slot_NN.json`) with chained migrations; slot 0 = chapter autosave. |
| `SceneRouter` | `game/core/scene_router.gd` | Threaded scene loads behind a fade; `prewarm_requested` hook for the shader-cache warmup (M1-RND-06). |

## State
- `GameStateData` (Resource): flags, party and reserve ids, inventory, currency, play time, location, chapter. `to_dict()` / `from_dict()` are the only serialization path.
- Bump `SaveSystem.SAVE_VERSION` on any schema change, and add a `_migrations[old_version]` step plus a test.

## Planned (M1+)
Built in M1: dialogue runner (`game/narrative/`, DialogueRunner) and text box (`game/ui/dialogue/`, DialogueBox); see tech/dialogue_format.md.

Built in M1 (architect-stream-2): the field controller and camera rails (`game/world/`; see [field_camera.md](field_camera.md)) and the debug overlays F1–F12 (`game/core/debug/`; see "Debug overlays" below).

Still planned: battle scene glue (`game/battle/scene/`, in progress by UI and Combat) and random encounters (M2). The save shrine and save/load menu landed in M1-ARC-03 (see "Saves" below).

## Debug overlays (M1-ARC-02)

- **Where:** `game/core/debug/`. `DebugOverlay` (a CanvasLayer scene) holds the pages, `DebugReadouts` holds the pure page logic, and `DebugHooks` holds discovery and registration. `scene_swap_probe.tscn` is the hitch probe. Data lives in `game/data/debug/`: `debug_overlay.json` has the bindings, pages and cheat amounts, `teleports.json` has the teleport targets, and `perf_budgets.json` has the thresholds.
- **Lifecycle:** this is not an autoload. `boot.gd` instances `debug_overlay.tscn` **by path** under the tree root when `OS.is_debug_build()` returns true, so the overlay survives scene changes. Nothing outside `game/core/debug/` names a debug class, and `test_debug_overlay.gd` enforces that. The folder can therefore be dropped from release exports. **This still needs an export filter**: add `game/core/debug/*, game/data/debug/*` to `exclude_filter` in both `export_presets.cfg` presets (Lead or Systems Architect).
- **Keys** (added to the InputMap at runtime from `debug_overlay.json`; `project.godot` is untouched):

| Key | Page |
|---|---|
| F1 | Help |
| F2 | Turn-order internals |
| F3 | Encounter rate |
| F4 | Flag inspector |
| F5 | Teleport |
| F6 | Lattice cheat |
| F7 | Field camera |
| F9 | Battle sandbox (moved here from `boot.gd`) |
| F12 | Hide |

  Pressing a page's key again closes it. While the overlay is open, `ui_up`, `ui_down` and `ui_accept` move through lists and act on the selection.
- **Hooks** (no coupling: game code joins a *group* and exposes a *method*, both plain strings):
  - Battle: group `debug_battle_engine_source`, `debug_battle_engine() -> BattleEngine`. Without that, the overlay falls back to the first node in the current scene whose `engine` property holds a `BattleEngine`, which already finds `BattleController`.
  - Encounters: group `debug_encounter_provider`, `debug_encounter_state() -> Dictionary`, with the keys in `DebugReadouts.ENCOUNTER_KEYS`. No provider exists until the M2 encounter system lands, so the page says so.
  - Lattice: group `debug_lattice_source`, `debug_lattice() -> LatticeProgress`, and optionally `debug_facets() -> FacetInventory`. Without a source, the cheat rebuilds progress from `Game.state.lattice` and writes it back.
  - Debug-side code and tests can also call `DebugHooks.register_battle_engine`, `register_encounter_provider` and `register_lattice_source`.
- **What each page does:**
  - Turn order shows the clock, the current actor, each fighter's agility, speed multiplier, `Formulas.base_delay`, next time and ticks until their turn, and the same 16-turn prediction the HUD shows.
  - Flags lists every declared flag with its value and description. Enter toggles a bool through `Game.set_flag`.
  - Teleport uses `SceneRouter.change_scene`, then the new root's `place_at(spawn)`.
  - Lattice adds `movement_points` to each party member (or to `fallback_characters`), placing them on their start node, and adds `facets_each` of every Facet type, all through `LatticeProgress` / `FacetInventory`.
- **Text is developer-facing and not localized.** It never ships.

## Scene-swap hitch (M1-RND-06 follow-up, architect-stream-2, 2026-10-22)

**Question.** Rendering measured a 51–71 ms CPU frame on a `SceneRouter.change_scene` with the dummy renderer, which is over the SPEC §4.2 budget of 50 ms.

**Method.** Headless 4.6.3 on the 4-vCPU sandbox, using `Time.get_ticks_usec()` marks around each phase: threaded load, `instantiate()`, `add_child` (including `_ready`), the first frame (deferred calls and first draw), the prewarm spawn, and per-pair font glyph rasterization. Every run is a fresh process, so caches start cold. The sandbox was heavily shared during the measurement (load average 9–11 from other streams' renders), so isolated frames of 50–600 ms appear at random points in any transition, even with the probe at `nice -15`. The numbers below are therefore medians over repeated runs, and the metric is the router's own swap window (`MEASURE_FRAMES` = 4 frames from the swap).

**Findings**
| Phase (cold, battle sandbox) | Cost |
|---|---|
| Threaded load (`battle_sandbox.tscn`) | ~220–260 ms on the loader thread. **No main-thread stall.** Polling costs < 0.05 ms. |
| `instantiate()` | 1–2 ms (0.3 ms warm) |
| `add_child` + `_ready` | 9–21 ms cold, 2–4 ms warm |
| First frame (`BattleController.start_sandbox` deferred, HUD build, first draw) | 27–32 ms cold, ~7 ms warm |
| `ShaderPrewarm` spawn (stage, material load, shader front end) | 6–11 ms, every swap |
| Theme font rasterization, per (font, size) | 2–10 ms. The full theme set (16 pairs) is ~80 ms |
| **Engine fallback font, MSDF** (`gui/theme/default_font_multichannel_signed_distance_field=true`) | **~7 ms per glyph**: 760 ms for ~105 glyphs |

**Root cause.** In the M0 router, the frame that showed a new scene (or the one right after it, since `change_scene_to_packed` adds the scene at the end of the frame) paid for everything at once:
- cold glyph rasterization of every font and size the new UI draws for the first time (the largest single item),
- the new scene's `_ready` and first-frame work,
- the old scene's free,
- the prewarm stage build.

Boot → boot is cheap (7–9 ms), because the boot title's glyphs are already cached from startup. The battle sandbox is the real offender. The 51–71 ms reading came from `ShaderPrewarm`'s six-frame window, which spans the swap frames plus machine noise. There's also a trap waiting: any text that falls back to the engine font is MSDF and costs 7 ms per glyph. A few dozen glyphs of it would blow the budget by itself.

**Fix** (`game/core/scene_router.gd`; public API unchanged):
1. **Font warm-up.** `SceneRouter.FontWarmer` draws every non-MSDF (font, size, outline) of the project theme with a fixed character set, in 16-character units, within a 4 ms per-frame budget. It sits invisibly under the fade, starts with the fade-out, runs once per process, and the swap waits for it.
2. **Prewarm frame.** `prewarm_requested` now fires a frame before the swap, so the stage build has its own frame.
3. **Threaded instance.** `instantiate()` runs on `WorkerThreadPool`. The node isn't in the tree yet, which Godot 4 allows.
4. **Split swap.** `unload_current_scene()` runs a frame before `change_scene_to_node()`, so freeing the old scene and entering the new one never share a frame.
5. **Built-in measurement.** Every swap records `last_swap_stats` (per-phase ms, the four frame times, `max_frame_ms`, and `over_budget`), emits `swap_measured(stats)`, and warns when it's over 50 ms. Setting `instantiate_on_thread`, `warm_fonts` and `split_swap` to `false` reproduces the M0 behaviour. The probe's `--legacy` flag does exactly that.

**Before and after** (`game/core/debug/scene_swap_probe.tscn`, 8 fresh processes each, swap-window max in ms):
| Target | M0 router (`--legacy`): min / median / max | Fixed: min / median / max |
|---|---|---|
| `battle_sandbox.tscn` (from boot) | 30.9 / **42.0** / 122.6 | 19.8 / **27.5** / 60.8 |
| `boot.tscn` (from boot) | 6.9 / 8.8 / 15.1 | 6.9 / 7.0 / 32.2 |

The maxima are contention outliers. What's left of the battle swap frame (about 20 ms on a quiet machine) is the battle scene's own `_ready` and `start_sandbox`: HUD construction, first-time text shaping, and stage spawn. That's content-side work, and splitting it is a request for UI and Combat (see below).

**Regression test.** `tests/unit/test_scene_router_swap.gd` runs the probe in a child process for each target in `game/data/debug/perf_budgets.json`. It passes on the first of up to `attempts` (5) runs under `test_threshold_ms` (40 ms, which leaves 10 ms of headroom under the 50 ms budget). It also asserts the shape of the fix: threaded instance, fonts warmed, unload in its own frame. Each probe run takes about 2.5 s.

**Follow-ups (other owners).**
- *Project settings:* `gui/theme/default_font_multichannel_signed_distance_field=true` makes the engine fallback font MSDF. Either set it to `false`, or make sure no shipped text reaches the fallback. Label3D, debug text and untranslated `RichTextLabel` BBCode fonts are the usual leaks.
- *UI and Combat:* `BattleController.start_sandbox` does about 25–30 ms of cold work in the first frame. Building the HUD rows over two or three frames behind the intro fade would leave a large margin.
- *QA:* measure on a real GPU. Pipeline compiles add to these CPU numbers, and `ShaderPrewarm` exists for exactly that.

## Saves (M1-ARC-03, architect-stream-4)

SPEC §5.2 (versioned saves, save-point-only, chapter autosave) and §6.6 (shrines: full heal, a save menu, a teleport network later).

### Pieces

| Path | What it is |
|---|---|
| `game/core/save_system.gd` | Autoload. Existing format and migrations, plus the APIs below. |
| `game/core/game.gd` | Play-time clock and `set_chapter()`. |
| `game/core/event_bus.gd` | New signals: `chapter_changed(chapter, previous)`, `party_full_heal_requested(source_id)`, `save_shrine_used(shrine_id, location_id)`, `autosave_finished(reason, error)`. |
| `game/world/save_shrine/` | `SaveShrine` (an `Interactable`), `save_shrine.tscn` (primitives + bound glimmer), and `ShrineNetwork` (the teleport network, M1-ARC-06). |
| `game/ui/save/` | `SaveMenu` (view + input, `save_menu.tscn`), `SaveMenuModel` (logic, no nodes), `SaveSlotRow`, `SaveSlotInfo`, and the `TitleSaveEntry` stub. |
| `game/data/ui/save_menu.json` | Slot count (autosave + 6 manual), layout at 1920 × 1080, and motion timings. |
| `game/levels/_tests/save_shrine/` | A copy of the field test zone with a shrine, the capture driver `SaveShrineShot`, and `save_menu_fixtures.json`. |

### SaveSystem APIs

- `save_to_slot(slot, state, reason = &"manual", extra_meta = {})` writes `slot_NN.json.tmp` and renames it over the slot, so a crash mid-write keeps the old save. Slots run 0..`MAX_SLOT` (99).
- **The `meta` block.** A save is `{"version", "state", "meta"}`. `meta` holds `saved_at` (Unix s, from the injectable `clock`), `reason`, `chapter`, `play_time_sec`, `location_id`, `location_key`, and anything from `extra_meta` (the shrine adds `shrine_id`). It is display data only. Loading never reads it, migrations ignore it, and it is not a `GameStateData` field, so it needed no `SAVE_VERSION` bump. Older saves without it list fine, using the file's modified time.
- `slot_info(slot) -> Dictionary` and `list_slots(slots)` return what a menu shows: `status` is `empty`, `ok`, `corrupt` (unparseable, wrong types, or no migration path) or `newer` (saved by a newer build). They **never push errors**, so listing a damaged slot is quiet. `state_shape_ok()` guards both `slot_info` and `load_from_slot` against wrongly typed fields, which would otherwise crash `GameStateData.from_dict`.
- `load_into_game(slot) -> Error` loads the slot into `Game.state` and restarts the play clock. It returns `ERR_FILE_NOT_FOUND` or `ERR_FILE_CORRUPT` and leaves the live game alone on failure.
- `autosave(reason = &"chapter_boundary") -> Error` saves `Game.state` to slot 0 and reports on `EventBus.autosave_finished`. `SaveSystem._ready` connects it to `EventBus.chapter_changed`. `autosave_enabled = false` turns it off for tests and scripted sequences (`ERR_UNAVAILABLE`).
- `save_dir` (default `user://saves`) and `clock` are vars so that tests and captures can use their own folder and fixed timestamps. Restore them afterwards; every test here does.
- `location_name_key(id)`: `"ch02/haluna"` becomes `LOCATION_CH02_HALUNA`. Rows exist for the field test zone, Haluna, the Saltgrass Causeway and the Shell Shrine. A missing key shows "An unnamed shore".

### Chapters and play time (`Game`)

- `Game.set_chapter(n)` is the **only** way story code should change the chapter. It emits `chapter_changed` only on a real change, and that triggers the autosave.
- **Play time.** `advance_play_time(delta)` adds a step clamped to [0, `PLAY_TIME_MAX_STEP_SEC` = 1 s] while `play_clock_running` is true. `_process` calls it, and `Game` runs with `PROCESS_MODE_ALWAYS`, so menus that pause the tree still count. The same deltas always give the same total (tests assert bit-equality). `new_game()` and `load_into_game()` start the clock. **The title screen must call `Game.stop_play_clock()`**, since the clock runs from boot otherwise.

### The shrine

On use (`FieldController.interact()` → `try_interact()`): the base `Interactable` effects run (`uses`, the instance's own `sets_flag`, `used`, and the `field_interacted` bus event). Then `rest()` runs:
1. It sets `save_shrine_used`. Story shrines set their own flag as well; Haluna's sets `ch02_saved_once`.
2. It sets `Game.state.location_id` from its export.
3. It emits `party_full_heal_requested(id)`, and `Game` restores `party_vitals` (M1-ARC-06). It also makes this shrine the respawn point.
4. It emits `save_shrine_used(id, location_id)`.
5. It calls `ShrineNetwork.attune()`, which saves the network id (M1-ARC-06).
6. It opens `SaveMenu` in SAVE mode with `{"shrine_id": id}` and the subtitle "In the shrine's still light, every wound closes."

Shrines are never used up (`once = false`).

The look follows color script rule 2 (bound light). A salt-glass core and a conduit ring are emissive `glimmer_bound` `#4FB3B0`. A `GlimmerField` in **MACHINE** mode holds perfectly still, with `follow_scene_intensity = false` (otherwise it would be invisible in day zones, where `hymn_glimmer.a` = 0) and `follow_global_focus = false` (bound motes never gather). Stone and verdigris primitives complete it, with a fan-shell canopy on two posts. It is a greybox stand-in for the Environment kit.

### The menu

- **Rows.** Slot 0 is the autosave, followed by Records 1–6. A readable row shows the slot name, "Chapter N", the location name, play time (H:MM:SS, tabular) and the save time (local; captures use a 0 bias). A damaged record shows a `ui_danger` status line, and an empty one shows "No record".
- **Rules** (in `SaveMenuModel`, all headless-tested):
  - The cursor visits every row and the help line explains each one.
  - In SAVE mode the autosave row is refused ("written at the end of each chapter").
  - Writing to an empty slot saves at once. A file that is already there (readable, damaged or newer) asks "Write over Record N?", with **"Keep it" as the default**. Saving over a damaged slot repairs it.
  - In LOAD mode only readable rows load, and the cursor starts on the newest record.
  - The result message closes the menu after a successful save. A failure returns to the list.
- **Input.** `ui_up` / `ui_down` move, `ui_left` / `ui_right` also move inside dialogs, `ui_accept` chooses and `ui_cancel` backs out. That covers keyboard and controller through the built-in actions. A mouse click on a row or choice also works. The menu handles `_input` and marks events handled. While open it pauses the tree and restores the pause state on close or free.
- `SaveMenu.open_in(host, mode, extra_meta, subtitle_key)` brings its own `CanvasLayer` (layer 64, under the router fade at 128), which frees itself on close.
- **Title entry.** `TitleSaveEntry.can_continue()`, `continue_slot()` (the newest readable slot, autosave included), `continue_game()` and `open_load_menu(host)`. Since M1-ARC-06 the title menu in `boot.tscn` uses them, and `WorldReturn` moves the player after a load (see below).

### Tests and shots

- **Tests:** `tests/unit/test_save_shrine.gd`, `test_save_menu.gd`, `test_autosave.gd` and `test_play_time.gd`. Each test writes to its own `user://test_*` folder, which it removes. The corrupt fixture is a truncated JSON file in slot 3.
- **Shots** (960 × 540): `save_shrine_field` (the player beside the shrine in the court), `save_menu` (opened through the shrine over fixture slots, with autosave, two records, a damaged one and empties), and `save_menu_overwrite` (the confirm dialog). The driver writes fixtures to `user://shot_saves` and restores everything in `_exit_tree`.

### Open items (other owners)

- ~~Persisted party HP/MP/statuses, attuned shrines, a respawn point, a location registry, title wiring~~: done in M1-ARC-06 (next section).
- **Haluna shrine instance (Environment / Narrative):** `sets_flag = ch02_saved_once`, `location_id = ch02/haluna`, and since M1-ARC-06 `network_id = haluna_shrine`. Environment adds `ch02/haluna` (scene, spawn, `LOCATION_CH02_HALUNA`) to `game/data/world/locations.json` and a `shrines` row for `haluna_shrine` **in the same commit as the scene**: `validate_data.py` fails on a shrine whose `location_id` or `network_id` the registry does not list.

## Save v4, party vitals and return to world (M1-ARC-06 + M1-PRG-03, architect-stream-6)

### Save v4 schema (`GameStateData`, `SAVE_VERSION = 4`)

The v3 fields are unchanged. New in `state`:

| Field | Type | Meaning |
|---|---|---|
| `party_vitals` | `{"<character>": {"hp"?: int, "mp"?: int, "statuses"?: [status id]}}` | HP, MP and **carried** statuses between battles. A member with no entry is at full HP and MP with no statuses. Inside an entry, a missing `hp` or `mp` also means full: a shrine cannot know the maximum (the Lattice and gear set it at battle setup), so it erases the values instead of writing them. Values are clamped to the battle-time maximum. |
| `attuned_shrines` | `[network id]` | Shrines rested at, in attunement order, without duplicates. |
| `respawn` | `{"location_id": String, "spawn": String}` | Where Continue puts the party. An empty `location_id` means `locations.json` `default_location`; an empty `spawn` means the location's own spawn. |

- **v3 → v4 migration** (`_migrate_v3_to_v4`, a frozen literal): `party_vitals = {}` (everyone full, no statuses), `attuned_shrines = []`, and `respawn = {location_id: <the save's location_id, or "">, spawn: ""}`. Fields already present are kept. `state_shape_ok` rejects a non-dictionary `party_vitals` or `respawn` and a non-array `attuned_shrines`, and `from_dict` drops malformed vitals entries, so a damaged save cannot crash battle setup.
- **Post-load step** (M1-PRG-03): `load_from_slot` and `deserialize` run `PartyGoods.ensure_starting_gear(state)`, which calls `EquipmentBag.grant_starting(cid)` for every joined hero (`party_ids` + `reserve_ids`). `grant_starting` is idempotent. A hero with no loadout gets every starting piece once. A hero with a loadout only gets a missing **required** slot (the weapon) filled: with an owned, unworn piece if there is one, otherwise a new starter. Migrated v2 saves therefore load with weapons.
- **`EventBus.game_loaded` moved.** `load_into_game` emits it *after* the save is `Game.state` and the clock runs. A plain `load_from_slot` (menus, tools, tests) only reads and announces nothing.

### Party vitals (`Game`; rules in `game/data/world/party_rest.json`)

- `carried_statuses` (poison, petrify, zombie) outlast a battle; every other status ends with it. They come back at the next setup with `carried_duration` (−1, the engine's "until cured"). `shrine_cures` (the same three) are what a shrine's rest removes. The validator checks the ids exist and that every cure is a carried status.
- `EventBus.party_full_heal_requested` → `Game.heal_party()` → `GameStateData.full_heal(cures)`: full HP and MP for everyone (which lifts KO), and the cures removed. The shrine emits it before its menu opens, so the save holds the healed party.
- `EventBus.battle_party_returned(encounter_id, outcome, party: Array)` (new) → `Game.record_party()` → `GameStateData.record_vitals(...)`: HP and MP (omitted at the maximum) and carried statuses only. A member back at full with nothing carried loses their entry.
- **Battle setup hook.** `Game.vitals_modifier(state = Game.state) -> Callable` is a `BattleEngine.party_modifier` that holds its state. Run it **last**, so it sees the Lattice and gear maximum: `EquipmentEffects.compose([progress.apply_to, fx.modifier(), Game.vitals_modifier()])`. Statuses are added before HP is set, because a KO'd combatant takes none. With no saved vitals it changes nothing, so every existing engine test plays as before (a test asserts this).

### Requests for Combat (the battle scene; no engine-core API is needed)

`game/battle/scene/battle_controller.gd` is outside this stream, so the live sandbox does not use the hooks yet:
1. In `start_battle`, for live battles only (fixtures and captures must stay frozen), set `engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.modifier(), Game.vitals_modifier()])`.
2. When a battle ends in victory or escape (defeat goes to the title), emit `EventBus.battle_party_returned.emit(engine.encounter_id, engine.outcome, engine.party_active + engine.party_reserve)`.
3. Decide what a KO'd active member at battle start does (genre convention: a living reserve swaps in). The engine accepts a combatant built with HP 0; it is simply off the timeline.

### Location registry (`game/data/world/locations.json`; `LocationRegistry` in `game/world/world_return_registry.gd`)

- `locations[]`: `{id, scene, spawn, name_key}`, plus `default_location`, `new_game: {location_id, spawn}`, and `shrines[]: {id (network id), location_id, spawn}`. Only locations whose scene exists are listed. Today that is `field_test` → the save-shrine copy of the field test zone, spawn `Shrine`.
- `resolve(id, spawn)` returns `{location_id, scene, spawn, fallback}` and falls back to the default for an unknown id.
- `check_locations` in `tools/validate_data.py` (tests in `tools/tests/test_locations_validate.py`) checks that scenes exist, spawns are nodes under the scene's `Spawns`, name keys exist, the default, new-game and shrine rows resolve, every `SaveShrine` instance in any `.tscn` has a registered `location_id` and `network_id`, and the `party_rest.json` rules hold.

### Return to world (`WorldReturn`, `game/world/world_return.gd`)

- `SceneRouter.world_return` is a `WorldReturn` child of the router. On `EventBus.game_loaded` it resolves `Game.state`'s respawn (respawn point, then current `location_id`, then the default) and calls `SceneRouter.change_scene(scene, spawn)`.
- **It is off until `boot.gd` arms it** (`arm_world_return()`), so the test runner, captures and tools that load saves never change scene.
- `SceneRouter.change_scene(path, spawn = &"")` takes an optional spawn (API-compatible). Once the new scene is in the tree, still under the opaque fade, `WorldReturn.place_player(root, spawn)` puts the player on `Spawns/<spawn>`: through the zone's own `place_at(spawn, yaw)` when it has one (field zones snap their camera), otherwise by moving the `player` group node or a child named `Player`.
- `go_to(location_id, spawn)` serves New Game and teleports. `change_scene` is an injectable Callable, so tests record swaps; `tests/unit/test_world_return.gd` builds fixture zones at runtime under `user://`.

### Shrine network (`ShrineNetwork`, no longer a stub)

- `attune(shrine)` appends the network id to `Game.state.attuned_shrines` once. `destinations_from(shrine)` lists attuned shrines that have a registry row, minus the shrine itself.
- `request_teleport(shrine, dest)` refuses unless `dest` is one of those destinations and its location resolves. It travels through `SceneRouter.world_return.go_to` (refused while the router is busy) and makes the destination the respawn point. `registry` and `travel` are static vars for tests.
- A rest also makes the shrine the respawn point: the spawn is `SaveShrine.respawn_spawn` (an export), else its registry row's spawn, else the location's spawn.

### Title (`game/ui/title/`, instanced in `boot.tscn`)

- `TitleMenu` (view and input: a `MenuPage` and a help line, using the theme and loc keys only) over `TitleMenuModel` (no nodes). Its layout is in `game/ui/title/title_menu.json` until UI owns a title screen under `game/data/ui/`.
- Continue loads the newest readable record (`TitleSaveEntry.continue_game`). New Game runs `Game.new_game()` and `go_to(new_game)`. Load opens `SaveMenu` in LOAD mode. Without a record, Continue and Load are greyed and the help line says why.
- The title calls `Game.stop_play_clock()`. The `boot_title` baseline was re-approved after looking: the menu is new, and the name label is unchanged.

### M1-PRG-03 notes

- `EquipmentEffects.modifier()` returns a `party_modifier` that owns its `EquipmentEffects`, because a bare `fx.apply_to` Callable does not keep a RefCounted alive. `compose()` now pushes an error for an invalid hook (when composing and when called) instead of skipping it silently.
- **Ember Pot**: the price goes from 110 to **220**, and it stays out of the slice shops (Haluna Market and Forge). Fixed fire damage that ignores defence, at rank 2, beats Rhen's attack on the crab and nearly matches Ysolde's Ember on the eel. At 110 it would undercut the "find the role that answers this foe" lesson. At 220 (the Quickwater tier, about 3½ early fights) it is a deliberate emergency buy. Its description names the Pemakar kilns, so its first shop should be Pemakar's, after the slice. Design: please update the Ember Pot row in `economy.md`'s price curve.

### Tests

`tests/unit/test_save_v4.gd` (schema, migration, `game_loaded` order, post-load gear), `test_save_party_vitals.gd` (rules, write-back, heal, and the setup hook on the real engine), `test_world_return.gd`, `test_shrine_network.gd` and `test_title_menu.gd`, plus additions to `test_save_shrine.gd`, `test_save_system.gd`, `test_equipment.gd` and `test_equipment_effects.gd`.
