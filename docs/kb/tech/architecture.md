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
| `game/world/save_shrine/` | `SaveShrine` (an `Interactable`), `save_shrine.tscn` (primitives + bound glimmer), and the `ShrineNetwork` stub. |
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
3. It emits `party_full_heal_requested(id)`. **There is no persisted party HP yet**: the battle engine builds every fighter at full HP, so today the heal is already true. Whoever owns live party state (the party menu, or persistent HP) restores it when this fires.
4. It emits `save_shrine_used(id, location_id)`.
5. It calls `ShrineNetwork.attune()` (a no-op).
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
- **Title stub.** `TitleSaveEntry.can_continue()`, `continue_slot()` (the newest readable slot, autosave included), `continue_game()` and `open_load_menu(host)`. **After a load nothing moves the player yet**: there is no location → scene registry. Listen to `EventBus.game_loaded`.

### Tests and shots

- **Tests:** `tests/unit/test_save_shrine.gd`, `test_save_menu.gd`, `test_autosave.gd` and `test_play_time.gd`. Each test writes to its own `user://test_*` folder, which it removes. The corrupt fixture is a truncated JSON file in slot 3.
- **Shots** (960 × 540): `save_shrine_field` (the player beside the shrine in the court), `save_menu` (opened through the shrine over fixture slots, with autosave, two records, a damaged one and empties), and `save_menu_overwrite` (the confirm dialog). The driver writes fixtures to `user://shot_saves` and restores everything in `_exit_tree`.

### Open items (other owners)

- **Persisted state still needed** (not added here: each needs a new `GameStateData` field and SAVE_VERSION 4):
  - party HP/MP/statuses, for a real heal and for persistence between battles;
  - the attuned shrine network ids, for the teleport network;
  - a respawn point (`scene` + `spawn`), so a load can put the player back at the shrine. `meta.shrine_id` is recorded already, but it is display-only.
- A location registry (`location_id` → scene, spawn, name key) under `game/data/world/`, used by load routing and by `ShrineNetwork`.
- The title screen (UI) wires `TitleSaveEntry` and calls `Game.stop_play_clock()`.
- The Haluna shrine instance sets `sets_flag = ch02_saved_once` and `location_id = ch02/haluna` (Environment / Narrative).
