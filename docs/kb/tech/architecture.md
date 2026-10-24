# Runtime Architecture (M0)

## Autoloads (`project.godot`)
| Name | Script | Purpose |
|---|---|---|
| `EventBus` | `game/core/event_bus.gd` | Decoupled signals: battle start/end, flag changes, dialogue events, scene change, save/load. |
| `Game` | `game/core/game.gd` | Owns the live `GameStateData` and the `FlagRegistry`. `get_flag` / `set_flag` reject undeclared flags at runtime, and the validator rejects them in CI. |
| `SaveSystem` | `game/core/save_system.gd` | Versioned JSON saves (`user://saves/slot_NN.json`) with chained migrations; slot 0 = chapter autosave. |
| `SceneRouter` | `game/core/scene_router.gd` | Threaded scene loads behind a fade; `prewarm_requested` hook for the shader-cache warmup (M1-RND-06). Installs `ShaderGlobals` (zone-global reset) and `WeatherClock` (the weather clock, M2-ARC-02) as it starts. |

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
5. **Built-in measurement.** Every swap records `last_swap_stats` (per-phase ms, the four hidden frame times, `max_frame_ms`, and `over_budget`), emits `swap_measured(stats)`, and warns when a frame is over its budget. Since M1-ARC-16 there are two windows with their own budgets (next subsection). Setting `instantiate_on_thread`, `warm_fonts` and `split_swap` to `false` reproduces the M0 behaviour. The probe's `--legacy` flag does exactly that.
6. **Time-sliced prewarm and zone-global reset (M1-RND-15).** `ShaderPrewarm` builds every draw at start but feeds them to its stage `materials_per_frame` at a time (`prewarm_materials.json`; 12), halving the batch after any frame over `slice_budget_ms` (33). While staging, the stage holds its parent's swap through the router's generic `hold_swap(holder)` / `release_swap(holder)` (M1-RND-23; like `SaveSystem.hold_autosave`), and the router waits while `swap_holders()` is non-empty, at most `PREWARM_WAIT_MAX_FRAMES` (120), after the threaded instance and before the unload, and records `prewarm_wait_frames`. On the RX 9070 XT the all-at-once stage cost 121–150 ms in one frame (docs/kb/qa/gpu/2026-10-23-rnd-07.md); the sliced worst frame against SPEC §4.2's 50 ms still needs measuring on the PC GPU (`tools/gpu_bench/run_prewarm.sh`). Just before `change_scene_to_node()` the router emits `scene_swapping(scene_path)`. `ShaderGlobals.install(router)` (in the router's `_ready`) resets `ShaderGlobals.ZONE_GLOBALS` (`hymn_zone_sea_glow`, `hymn_water_level`) to their project.godot defaults on it, so a zone that never writes those globals starts from the defaults, and the router names no system that owns one (M1-RND-23, review-sweep-J S2).

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

### The two measured windows (M1-ARC-16, ADR 0029)
SPEC §4.2 (v1.3) budgets what the player sees, not what the fade hides. The router measures both, each against its own budget, and warns (`push_warning`, naming the budget) when one is over:

| Window | Frames | Stats in `last_swap_stats` | Budget |
|---|---|---|---|
| **Hidden** | the `MEASURE_FRAMES` (4) frames after `change_scene_to_node()`, under the opaque fade: the new scene's `_ready` and first draw | `frame_ms`, `max_frame_ms`, `budget_ms`, `over_budget` | `HIDDEN_FRAME_BUDGET_MS` 1 s a frame |
| **Entry** | `change_scene()` until the fade starts to lift (the fade-out, the load, the prewarm wait, the swap) | `entry_ms`, `entry_budget_ms`, `entry_over_budget` | `ENTRY_BUDGET_MS` 3 s |
| **Visible** | every frame while the fade lifts (`lift_frames` of them), then the first `VISIBLE_MEASURE_FRAMES` (60) after it has lifted | `visible_frame_ms`, `lift_frames`, `max_visible_frame_ms`, `visible_budget_ms`, `visible_over_budget`, `visible_complete` | `SWAP_BUDGET_MS` 50 ms |

- The visible window ends after `change_scene()` returns (about a second at 60 fps). `is_measuring()` is true until then, and `visible_measured(stats)` fires with the same dictionary, now complete. `is_busy()` is unchanged, so nothing waits on the window. A new `change_scene()` cuts it short (`visible_complete` false); a cut window is still judged on the frames it has.
- A frame counts as lifted when the fade rect's alpha is 0 at the frame's end. `SceneRouter.VisibleWindow` takes the timestamps, so tests drive it with an injected clock (`test_scene_router_swap.gd`), the way `frame0_start` is tested.
- `max_frame_ms` and `over_budget` keep their names but are now the **hidden** window, against 1 s: a 60 ms frame under the opaque fade is loading time, not a hitch. `budget_ms` in the stats is 1000.
- The regression test still holds the hidden frames to `perf_budgets.json`'s `test_threshold_ms` (40 ms). That is a tighter guard than ADR 0029 asks for, kept because a regression there shows up first; it also asserts that the probe recorded a complete visible window and an entry time. The probe (`scene_swap_probe.gd`) waits for `is_measuring()` before printing.
- **Which window the benches report.** `tools/gpu_bench/prewarm_bench.gd` has no fade: its `max_ms` is every frame after the scene is added (all visible, judged against 50 ms like the visible window), and its `prewarm_max_ms` and `prewarm_wall_max_ms` are the prewarm stage's frames, which the game runs under the fade (the hidden window, 1 s). `tools/gpu_bench/gpu_bench.gd` reports steady-state frames after its warm-up, neither window. Only the router's own stats measure the game's real transition.

### The boot card: the title shows only once it is warm (M2-ARC-03, ADR 0029)
ADR 0029 counts the boot warm-up as hidden time "under the boot screen before the title". Until M2-ARC-03 the boot
screen *was* the title, so the PC measured 168–265 ms frames on the visible menu
(docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md). Now:

- **The card.** `BootCard` (`game/core/boot_card.gd`) is a CanvasLayer at layer 127, just under the router's fade
  (128) and over every game and debug layer. It is one opaque ColorRect in the renderer's clear colour (the empty
  title's own background) with nothing drawn on it, so its lift reads as the title fading in. It stops the mouse.
- **What boot does** (`boot.gd`, only when boot is the game's scene, `get_tree().current_scene == self`):
  covers the title with a card, turns off the title's `_unhandled_input`, then (deferred) starts the resident
  warm-up (`GraphicsRuntime.warm_resident_shaders`) and the theme font warm-up (`SceneRouter.warm_fonts_now()`,
  the router's `FontWarmer`, once per run) and has the card wait for both (`wait_for_node`, `wait_until(fonts_ready)`).
  When they are done (or after `BootCard.MAX_WAIT_MS`, 10 s, with a warning) the card opens, the title gets its
  keys back, and:
  - **At launch** (no change running) the card lifts over `SceneRouter.FADE_SEC`, and boot calls
    `SceneRouter.measure_reveal(path, card.is_lifted, card_stats)`: ADR 0029's visible window (the lift, then 60
    frames) starts on the lift's first frame. It becomes `last_swap_stats` (`reveal: true`, plus the card's
    `reveal_wait_frames`, `reveal_wait_ms`, `reveal_wait_max_frame_ms`, `reveal_work_done`) and ends with
    `visible_measured`.
  - **Through a change** (the end card, a game over, the slice sweep) the router's opaque fade is already the cover.
    The card holds the router's reveal (`SceneRouter.hold_reveal`) and is cut when it opens; the router keeps its fade
    opaque after the swap while anything holds the reveal (at most `REVEAL_WAIT_MAX_MS`, 10 s), then lifts it and
    starts its own visible window. The wait is recorded as `reveal_wait_frames`, `reveal_wait_ms` and
    `reveal_wait_max_frame_ms`, each frame against the 1 s hidden budget, and is **not** in `entry_ms` (the title is
    not a zone entry; the boot warm-up's 1.3–3.1 s would otherwise read as an entry over 3 s).
- **Not in captures or tests.** Under `tests/screenshots/capture.gd` and the test runner boot is a child, not the
  current scene: no card, and the warm-up starts as before, so `boot_title` is unchanged.
- **The sweep.** `tools/gpu_bench/slice_sweep.gd` counts the frames while the reveal is held as hidden (it
  ended its hidden window at `EventBus.scene_changed`, so the title's warm-up frames used to read as visible).
  Other segments are unchanged: nothing else holds the reveal.
- **Tests.** `tests/unit/test_boot_card.gd` (the card frame by frame through `step(ms)`, the hold, `measure_reveal`,
  `judge_reveal_wait`). `test_scene_router_swap.gd` runs the probe's new `--launch` mode in a child process (the
  launch reveal is complete, starts with the lift, and opened on finished work) and checks that a change to the
  title holds its reveal while no other target does.
- **Reuse (M1-UI-11).** A preset change on the title can use the same card:
  `BootCard.cover(root, SceneRouter.FADE_SEC, SceneRouter.FADE_SEC)`; on `covered`, select the preset and
  `wait_for_node(GraphicsRuntime.current_warm_up())`; `arm()`; on `opened`, give the menu its input back and call
  `SceneRouter.measure_reveal(...)` with `card.is_lifted`. `cancel_visible_window()` ends a window early.

## Saves (M1-ARC-03, architect-stream-4)

SPEC §5.2 (versioned saves, save-point-only, chapter autosave) and §6.6 (shrines: full heal, a save menu, a teleport network later).

**Versions.** The current save is **v6** (`SaveSystem.SAVE_VERSION`). v4 added party vitals, shrines and the respawn point, v5 the bestiary log, and v6 carried Swell (gauges and modes in `party_vitals`, the unlock record in `swell`); each has its own section below, and every older save migrates forward one step at a time.

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

**Done in M1-CMB-08** (`game/battle/scene/battle_vitals.gd`, rules in battle_ctb.md "Carried vitals"): items 1–3 are wired for live battles (`persist_progress` on, no fixture). The live sandbox composes `progress.apply_to` then `Game.vitals_modifier()`. It has no `EquipmentEffects` yet, because the live battle does not build gear effects today, so add `fx.modifier()` between the two when it does. A KO'd or petrified active member trades places with the first living reserve member before `begin()`. With nobody standing at all, the active members get up with 1 HP.

### Location registry (`game/data/world/locations.json`; `LocationRegistry` in `game/world/world_return_registry.gd`)

- `locations[]`: `{id, scene, spawn, name_key}`, plus `default_location`, `new_game: {location_id, spawn}`, and `shrines[]: {id (network id), location_id, spawn}`. Only locations whose scene exists are listed. Today that is `field_test` → the save-shrine copy of the field test zone, spawn `Shrine`.
- `resolve(id, spawn)` returns `{location_id, scene, spawn, fallback}` and falls back to the default for an unknown id.
- `check_locations` in `tools/validate_data.py` (tests in `tools/tests/test_locations_validate.py`) checks that scenes exist, spawns are nodes under the scene's `Spawns`, name keys exist, the default, new-game and shrine rows resolve, every `SaveShrine` instance in any `.tscn` has a registered `location_id` and `network_id`, and the `party_rest.json` rules hold.
- **Open before content lock (M1-ENV-06 review-sweep-L, M1-NIT-02).** The shipped zone `ch02/haluna` (`game/levels/ch02/haluna/haluna.tscn`) instances `game/levels/_tests/haluna_mood/haluna_mood.tscn`, so the playable zone, the `haluna_shrine` it registers and the sea that publishes `hymn_water_level` all live under `_tests/`. An edit made for a mood shot can break the playable zone, and no gate would notice unless `--filter=haluna` or `world_return` happened to cover it. The plan is in **M2-ENV-01**. Promote the mood scene's shared content (dressing, sea, shrine, `WeatheringTide`, sky) to `game/levels/ch02/haluna/`, and leave `haluna_mood.tscn` as a thin test wrapper that instances it with the shot cameras. Do it before content lock, and in a branch that also re-renders the five `haluna_*` shots, so the move is proved byte-identical. Until then, an edit under `_tests/haluna_mood/` is a playable-zone edit: run `--filter=haluna` and `--filter=world_return` for it.

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

## Save robustness (M1-ARC-08, after QA review-sweep-C)

ADR [0018](../decisions/0018-new-game-autosave-policy.md) records the policy decisions.

- **Checked writes.** `save_to_slot` writes `slot_NN.json.tmp` through `_write_checked`. That checks the store result, flushes, checks `get_error()`, closes, and reads the file back to compare it with the text. Only then does it rename over the slot. On any failure it deletes the temp file, pushes a warning, returns the error (`ERR_FILE_CANT_WRITE` when Godot reported none) and emits no `game_saved`, so the slot keeps its previous save. `SaveSystem.store_text: Callable(f: FileAccess, text) -> bool` is the injectable writer. Tests replace it with one that writes half and fails, or writes half and claims success (`tests/unit/test_save_write_check.gd`).
- **Deep shape check.** `SaveShape.problem(state)` (`game/core/save_shape.gd`) checks every present key down to element types: string ids in `party_ids`, `reserve_ids` and `attuned_shrines`; scalar flags; whole, non-negative counts; Lattice travelers; equipment pieces keyed by uid; loadouts; vitals; respawn. The table is in the class comment. JSON loads numbers as floats, so a "whole number" is an int, or a float with no fraction. `state_shape_ok` now delegates to it. Versions must be whole numbers, so 2.7 and `"4"` are corrupt. `load_from_slot`, `deserialize` and `slot_info` share one reader, `_read_save`, so a listing and a load can never disagree. A malformed slot lists as `corrupt`, loads as `null`, and `load_into_game` returns `ERR_FILE_CORRUPT` without touching `Game.state` (`tests/unit/test_save_shape.gd`, including QA's probe slot).
- **Deferred autosave.** `chapter_changed` only calls `request_autosave`. `_process` writes it on a later frame at the first safe point: no hold, `SceneRouter.is_busy()` false, and the tree not paused. **Sequencer rule:** hold the autosave for the whole cutscene (`SaveSystem.hold_autosave(self)` … `release_autosave(self)`). `FieldCameraDirector` also holds it while a scripted shot is held. `new_game_started` (new on `EventBus`, emitted by `Game.new_game()`) and `load_into_game` drop a pending request. Tests use `poll_pending_autosave()`; `autosave()` still writes at once for callers that own their timing (`tests/unit/test_autosave_deferred.gd`, `test_autosave.gd`).
- **New Game over an autosave.** When slot 0 is readable, or from a newer build, the title's New Game asks first. "Go back" is the default, and `ui_cancel` also goes back. "Begin anew" starts the run, and the old autosave stays until the new run's first boundary is written. Manual records are never touched. The loc keys are `TITLE_CONFIRM_NEW_GAME`, `TITLE_CONFIRM_BACK` and `TITLE_CONFIRM_BEGIN` (`tests/unit/test_title_menu.gd`, and the end-to-end flow in `tests/integration/test_save_new_run.gd`).
- **Bounded whole numbers (review-sweep-E S1).** A whole number is at most `SaveShape.MAX_WHOLE` (2^53) in size. Above that a float no longer holds every whole number, and `int()` of a float past the int64 range wraps to -9223372036854775808, so `currency: 1e300` used to load as a negative purse. Game caps (`currency_cap`, `stack_cap`) stay the domain objects' job.
- **Equipment uid integrity (review-sweep-E S2).** `SaveShape` checks the bag as a whole, because `EquipmentBag` trusts it: every `owned` key is a canonical uid (`"5"`, never `"05"` or `"+5"`, which `str(uid)` lookups never reach), `next_uid` is present and greater than every owned uid (else `add_piece` would overwrite a piece), and every loadout uid is `0` (empty) or owned.
- **The camera hold follows the shot (review-sweep-E S3).** `FieldCameraDirector` drops its autosave hold in `_exit_tree` and takes it back in `_enter_tree` while a scripted shot is still held, so a director re-parented mid-cutscene keeps the autosave waiting.
- **Keep the further-along autosave (review-sweep-E S4, ADR 0018 amendment).** When the deferred chapter autosave comes due, `autosave_is_further_along(Game.state)` compares it with slot 0: a later chapter, the same chapter with more play time, or a newer build's save is further along, and the write is skipped (`ERR_ALREADY_EXISTS` on `autosave_finished`, plus a warning). The exception is a run that New Game started (the player confirmed replacing the autosave): until its first autosave is written, it may replace slot 0. A load ends that exception. `autosave()` called directly still writes at once.
- **Downward `set_chapter` (M1-ARC-10).** A chapter move backwards (debug only) requests no autosave and warns, unless `SaveSystem.autosave_on_chapter_regress` is set.
- **Leftover temp files (M1-ARC-10).** A `slot_NN.json.tmp` that is a readable save newer than its slot (by meta `saved_at`), or that sits beside a missing or damaged slot, is *recoverable*. It is never silently discarded: `report_leftover_temps()` logs each one at startup, `leftover_temp_info(slot)` describes it (for a future "recover" prompt), `recover_temp(slot)` renames it over the slot, and the next `save_to_slot` to that slot first moves it to `slot_NN.json.recovered` (with a warning) instead of overwriting it. A torn temp (unreadable) is overwritten, since there is nothing to keep. A failed rename now **keeps** the checked temp file and warns, instead of deleting the new save.
- **Review-sweep-F fixes (M1-ARC-11).**
  - *A temp file never recovers over a newer build's save.* `SaveSystem.temp_is_newer(tmp, main)` decides `recoverable`: an empty or damaged slot is always older; a `STATUS_NEWER` slot (a newer build's save, which this build cannot read) and a slot of a newer save version than the temp file never are. Otherwise the later `saved_at` wins, and in the same second the temp file wins when it has at least the slot's play time (two quick saves, then a failed rename).
  - *Every set-aside is kept.* The next free name is used: `slot_NN.json.recovered`, then `.recovered.2`, `.recovered.3`, … (`recovered_path`, `free_recovered_path`, up to `MAX_RECOVERED`).
  - *Migrations never coerce.* `_migrate_v2_to_v3` (which every v0-v2 save runs through) converts only values that are already whole numbers ≥ 0 and passes anything else through, so the shape check after it reads the save as corrupt. A nested value is no longer a script error, a huge count no longer wraps, and `"7"` is no longer read as 7.
  - *Loadouts must be ones `equip()` could make.* `SaveShape` rejects a piece worn in two slots (by one hero or two). `_read_save` then runs `EquipmentBag.loadout_problem()` on a copy, with the item tables: every worn piece fits its wearer (`equip_error`) and sits in its own slot. A save that fails reads as corrupt in listings and loads.
  - *A reparent mid-move ends the cutscene.* See field_camera.md: when `_exit_tree` pays an owed `blend_finished`, the director also drops its scripted shot, so the autosave hold cannot leak (ADR 0018 Amendment 2).
  - *Continue from an unregistered location* (WorldReturn) warns, goes to the default location, and keeps `Game.state.location_id`, so the next save records the real place and not the stand-in. An empty location uses the default silently, as documented.
- **Review-sweep-G fixes (M1-ARC-11 rework; ADR 0018 Amendment 3).** These supersede two sweep-F bullets above ("Loadouts must be ones `equip()` could make", and "Migrations never coerce" for negative counts).
  - *Table drift is repaired, not corrupt.* `_read_save` no longer runs `loadout_problem()`. After every load `EquipmentBag.repair_loadout()` takes off a worn piece that no longer fits its wearer or slot (it stays in the bag) and drops a piece whose base is unknown, warning for each; `grant_starting` then refills the weapon. `SaveShape` still rejects a piece worn twice and an unowned loadout uid. `loadout_problem()` stays as a diagnostic.
  - *An unreadable slot is never destroyed.* `save_to_slot` (after the checked temp write, before the rename) and `recover_temp` move a non-empty slot that reads as corrupt to the next free `slot_NN.json.corrupt`, `.corrupt.2`, … (`corrupt_path`, `free_corrupt_path`, `MAX_CORRUPT`). If that fails, the write is refused and the slot kept.
  - *Temps worth keeping.* `leftover_temp_info` adds `keep` (`temp_worth_keeping`): recoverable, a newer build's temp, or a readable temp beside a newer build's slot. Those are set aside as `.recovered` before the next write, and `report_leftover_temps` logs them (`kept_leftover_temps`); it still returns only the recoverable slots.
  - *Legacy counts.* A negative whole count in a v0-v2 inventory is dropped with a warning (the frozen v2 → v3 behaviour); from v3 on it is corrupt.
  - *Continue with a stale respawn* tries `location_id` (at the location's own spawn) before the default, and warns.
  - *Locations with no player.* A locations.json row may say `"playable": false` (a mood or art stand-in). `LocationRegistry.can_enter` is false for it, `resolve` falls back to the default (`reason: not_playable`), Continue and `go_to` warn and keep the saved location, and `ShrineNetwork.request_teleport` refuses it. `check_locations` errors on a playable row whose scene has no `Player` under the root and no node in group `"player"`, and on a non-playable `default_location` or `new_game`. `ch02/haluna` is marked until M1-ENV-06 moves it to the playable zone.
  - Tests: test_save_recovery.gd (the B1 probes for the autosave and `recover_temp`, `.corrupt` numbering, newer-build temps), test_save_shape.gd (repair on load, legacy negative counts), test_equipment.gd (`repair_loadout`), test_world_return.gd (stale respawn, not-playable location), test_shrine_network.gd, tools/tests/test_locations_validate.py.
- **Review-sweep-H fixes (M1-ARC-12; ADR 0018 Amendment 4).** These supersede the sweep-G bullet "Table drift is repaired" where it says an unknown base is dropped.
  - *Broken item tables never touch a save.* `ItemDB.load_dir` records each missing or unparseable table in `load_errors`, and `integrity_problem()` is non-empty while any table failed or the equipment table has no equipment, gear types or equip slots. While `SaveSystem.item_tables_problem()` is non-empty, `_post_load` skips the repair and the starting gear (the equipment stays exactly as saved, with a `push_error`), and `save_to_slot` refuses every write with `ERR_UNCONFIGURED` before touching a file.
  - *Unknown pieces are kept.* `repair_loadout` takes a piece of unknown equipment off but never deletes it: base and abilities round-trip untouched, `pieces_for` hides it, and `equip_error` refuses it (`ERR_UNKNOWN_EQUIPMENT`). `unknown_uids()` lists them, and each load warns once.
  - *A newer build's slot is copied.* Before a write replaces a slot that reads `STATUS_NEWER` (the confirmed manual overwrite, a New Game autosave), it is moved to `slot_NN.json.newer`, `.newer.2`, … (`newer_path`, `free_newer_path`).
  - *Locations: instanced players.* `scene_has_player` also finds a node in group `"player"` inside an instanced sub-scene, judges an inherited scene by its base too, and accepts a root script that defines `place_at`.
  - Tests: test_save_item_tables.gd (a broken, missing and hollow equipment.json; unknown pieces round-trip; `.newer` copies), test_equipment.gd, test_save_shape.gd, tools/tests/test_locations_validate.py, tools/tests/test_dlgc.py.
- **Durability limit.** `FileAccess.flush()` is a stdio flush, not an `fsync`: Godot exposes no fsync. On some filesystems a power cut right after the rename can still leave the slot empty or old, even though the write check passed. The read-back check proves the bytes reached the OS, not the disk. The `.tmp` recovery above covers the crash-before-rename case only.
- Tests: `tests/unit/test_save_shape.gd` (bounds, uid integrity), `tests/unit/test_save_recovery.gd` (further-along, New Game exception, downward chapter, temp recovery and set-aside, failed rename), `tests/unit/test_camera_director.gd` (the hold across a reparent).
- **Still open (QA nit):** duplicate or unknown `party_ids` pass the shape check (`["rhen","rhen"]`, `["nobody"]`). That is a semantic check against the character table, not shape.

## Data tables gate (M1-ARC-13, after QA review-sweep-I)

ADR [0018](../decisions/0018-new-game-autosave-policy.md) Amendment 5 records the decision. This section supersedes the sweep-H bullet "Broken item tables never touch a save" where it names `item_tables_problem()` as the gate: that is now one check among several.

- **One gate.** `DataHealth` (`game/core/data_health.gd`) holds one named check per table that saved state is judged against. `SaveSystem.data_health()` builds the standard set (`DataHealth.standard`), and `SaveSystem.data_tables_problem(state)` joins every problem. While it is non-empty, `_post_load` runs no post-load step (the save loads exactly as written, with a `push_error`) and `save_to_slot` refuses every write with `ERR_UNCONFIGURED` before it touches a file. Manual saves, the autosave and the New Game autosave all go through it. `report_data_tables()` logs the problem once at startup (review-sweep-I S2 for ARC-12). A new table that starts to judge saved state gets a check here, not its own flag in SaveSystem.
- **Each check** reports a table that is **torn** (fails to parse), **missing**, or **empty** (parses, but holds none of the rows a save refers to). Every loader records why in `load_error` / `load_errors` and accepts a path, so tests can point it at a broken copy.
- **The Lattice (the MUST).** A broken `lattice_<id>.json` used to read as an empty board, `LatticeProgress.from_dict` dropped every traveler, and the next victory (`battle_rewards.gd`) or F6 cheat wrote that back into `Game.state.lattice`; the next save made it permanent. Now:
  - `LatticeBoard.load_board_from(dir, id)` keeps the id and a `load_error`; `integrity_problem()` is non-empty for a load error, no nodes or no starts. `LatticeRules.integrity_problem()` is non-empty for a load error, no Facets or `move_cost <= 0`.
  - While either is broken, `from_dict` places nobody and **freezes** the saved dict: `to_dict()` returns it unchanged, `add_character` refuses, and `save_into(state)` (the one write-back, used by BattleRewards and the F6 cheat) refuses with a `push_error`.
  - On a sound board nothing is dropped either: an unknown activated node id stays in the set (it grants nothing), a lost position puts the traveler on their start and `LatticeTraveler.saved_position` is written back until they move, a character with no start is kept whole (`kept_characters`), and a saved gate the board lacks is kept (`kept_gates`), in saved order.
  - **Another board's save (M1-ARC-14, review-sweep-J S1).** `from_dict` freezes a save whose `board` field names a board other than the one it is given, exactly as for a broken board, so `to_dict` never rewrites `board` and nobody is re-homed. The writers (`BattleStage.lattice_for`, the F6 cheat's `lattice_target`) load the board the **save** names through `LatticeProgress.board_for(saved, configured)`, and fall back to the configured board only when the save names none. A saved id that is not `[a-z0-9_]+` (`LatticeBoard.is_valid_id`) becomes no path: `board_for` gives the configured board, which then freezes the save, and the `lattice` gate check reports it.
  - **The start on a lost position (review-sweep-J S2).** The start is not added to the saved activations. It counts as activated in play (`LatticeTraveler.implied_start`, `has_activated`), and it joins `activated` on the traveler's first move, as `add_character` would have added it. An untouched save therefore round-trips byte for byte.
  - `is_frozen()` is a flag (`_frozen_flag`), so an empty save on a broken board is frozen too.

### Audit: what in a save refers to which table

| Save field | Table | Failure mode before ARC-13 | Guard now |
|---|---|---|---|
| `lattice` | `progression/lattice_<board>.json`, `progression/facets.json` | **Data loss.** A broken board dropped every traveler, and the next victory and save made it permanent. On a sound board, unknown node ids, start-less characters and unknown gates were dropped silently. | Gate check `lattice` (the board the save names, default `standard`, plus facets.json). `from_dict` freezes or keeps; `save_into` refuses. |
| `lattice.board` vs the configured board | `progression/lattice_<board>.json` (the save's), `ui/battle_sandbox.json` `board` (the config's) | **Latent data loss (ARC-14).** The gate judged the save's board but the writers loaded the config's, and `to_dict` rewrote `board`: a second board or a config typo would have re-homed every traveler. | Writers load the save's board (`LatticeProgress.board_for`); a mismatch freezes; an invalid id is refused by the gate. |
| `equipment` | `items/*.json` | Fixed in ARC-12 (a broken equipment.json wiped the bag). | Gate check `items` (`ItemDB.integrity_problem`). |
| `inventory` | `items/items.json` | No live loss: nothing in game/ prunes the bag. A hollow items.json was not flagged, and `Inventory.normalize()` (unused) would drop every stack. | `ItemDB.items_problem()` (load error, or no items) is now part of the `items` check, and `normalize()` refuses to run while it is non-empty. |
| `party_ids`, `reserve_ids` | `battle/characters.json` | No writer prunes them. Battles cannot build fighters without the table. | Gate check `battle` (`BattleDB.load_dir` / `integrity_problem`: a load error, no characters or no statuses). |
| `party_vitals` | `world/party_rest.json`, `battle/statuses.json` | **Silent change.** With party_rest.json broken, `carried_statuses` was empty, so `Game.record_party` erased every carried status (poison, petrify, zombie) after the next battle. | Gate check `party_rest` (`Game.rest_rules_problem`); `record_party` writes nothing while it is non-empty. Statuses are in the `battle` check. |
| `location_id`, `respawn`, `attuned_shrines` | `world/locations.json` | No loss: WorldReturn keeps `location_id` on a fallback (ARC-11), and nothing prunes `attuned_shrines`. But a save made with no registry is judged against nothing. | Gate check `locations` (`LocationRegistry.load_path` / `integrity_problem`: a load error, no locations, or `default_location` not listed). |
| `flags` | `game/data/flags.tres` | No loss: flags are never pruned, and an undeclared flag only logs. But a story build without its registry is broken. | Gate check `flags` (`FlagRegistry.load_path` / `integrity_problem`: failed to load, or declares no flags). |
| `currency`, `chapter`, `play_time_sec` | none | Not judged against a table. | Shape check only (`SaveShape`). |
| `bestiary` (v5, M1-CMB-03) | `battle/enemies.json` | New field. Nothing prunes it: an id enemies.json no longer lists is kept as saved, and a page reads its stats from the table at display time. | Gate check `bestiary` (`BattleDB.enemies_problem`: enemies.json torn, missing or listing no enemies). Shape: `{String: {read: bool, defeated: whole number}}`. |
| `swell`, and `swell` / `swell_mode` in `party_vitals` (v6, M2-ARC-01) | `battle/swell.json` | New fields. Nothing prunes them: an unlocked mode or rule id swell.json no longer lists is kept as saved (`BattleSwell.load_saved` / `to_saved`). A carried mode that is not choosable falls back to the default mode in battle, and that battle writes the default back (a choice the player can make again, never a gauge). | Gate check `swell` (`BattleSwell.config_problem`: swell.json missing, torn, with no modes, or a default mode it does not list); `Game.record_swell` writes nothing while it is non-empty. Shape: `{unlocked: [String], progress: {String: whole number}}`; vitals `swell` a whole number, `swell_mode` a String. |

- **Not covered.** `recover_temp` is still not behind the gate: it only renames a temp file that an earlier, healthy run wrote and checked, so no table can change what it holds. `report_data_tables` is a log line, not a player-facing message; a boot banner needs a UI task and a loc key.
- Tests: `tests/unit/test_save_data_tables.gd` (each guarded table torn, missing and empty: the gate names it, the save loads exactly as written, manual, empty-slot and auto saves are refused, both slots are byte-identical, and it saves again once mended; the Lattice freeze and refused write-back; unknown Lattice ids through save, load and write-back; `normalize` and `record_party` on broken tables), `tests/unit/test_lattice_save.gd` (in-play behaviour of unknown ids).

## Save v5, the bestiary log (M1-CMB-03, Combat; ADR 0023)

- `SAVE_VERSION = 5`. `GameStateData.bestiary` is `{"<enemy id>": {"read": bool, "defeated": whole number}}`, wrapped in place by `Bestiary` (`game/battle/bestiary.gd`). `from_dict` copies it through `Bestiary.from_saved`, which turns JSON's float counts into ints.
- `_migrate_v4_to_v5` adds an empty log (a v4 save predates Read). The literal is frozen.
- `SaveShape` checks it (`_bestiary`: a Dictionary of records; `read` a bool, `defeated` a whole number >= 0; other keys are ignored). A malformed log reads as corrupt.
- The data-tables gate gained a seventh check, `bestiary` (`DataHealth.bestiary_problem`, from the same cached `battle_db`): enemies.json torn, missing or empty closes saving. A torn or missing enemies.json is also reported by the `battle` check, which joins every battle table's load error.
- Writers: `BattleBestiary` (a Read hit, and one defeat per foe on victory) in live battles only. Rules and glue: docs/kb/design/battle_ctb.md "Read, the bestiary and openings". Tests: `tests/unit/test_bestiary_save.gd`.

## Save v6, carried Swell (M2-ARC-01, Architect; ADR 0018 Amendment 6)

- `SAVE_VERSION = 6`. A `party_vitals` entry may also hold `swell` (gauge points; no value = empty) and `swell_mode` (no value = swell.json's `default_mode`). `GameStateData.swell` is the party's record, `{"unlocked": [mode id], "progress": {"<unlock rule id>": count}}`: modes unlocked through play (starting modes are not listed) and the counts towards the rest. `from_dict` keeps the Swell keys through `_clean_vitals` and turns JSON's float counts into ints (`_clean_swell`).
- `_migrate_v5_to_v6` adds `{"unlocked": [], "progress": {}}` (a v5 save predates carried Swell: empty gauges, default modes, nothing unlocked through play). The literal is frozen. Chained: v4 → v5 → v6.
- `SaveShape` checks `swell` (`_swell`) and the two new vitals keys (`_vital`). A malformed value reads as corrupt.
- The data-tables gate gained an eighth check, `swell` (`DataHealth.swell_problem`; tests set `swell_config` and `swell_loaded`). While swell.json is missing, torn, hollow or names a default mode it does not list, a load changes nothing and saving is refused.
- Writers, live battles only (`persist_progress`, no fixture): `Game.record_party` (gauge and mode, from `EventBus.battle_party_returned`), `Game.record_swell` (the record, from the new `EventBus.battle_swell_returned`), both after a victory or an escape. Out of battle, `BattleSwellCarry.set_mode` (a field mode menu) writes `swell_mode`. `GameStateData.full_heal` (a shrine) keeps both keys.
- Readers: `Game.vitals_modifier()` (gauge, mode) and `BattleSwellCarry.attach` (the record). Rules and glue: docs/kb/design/battle_ctb.md "Carried Swell". Tests: `tests/unit/test_swell_save.gd`.

## The weather clock (M2-ARC-02, Architect)

`WeatherClock` (`game/core/weather_clock.gd`) is the one runtime writer of `hymn_wind_time` (the clock every water,
vegetation and weathering shader runs on) and, in play, of `hymn_wind`.
- **Where it lives.** `SceneRouter._ready` calls `WeatherClock.install(self)`, as it does `ShaderGlobals.install`: the
  owner is the router's `WeatherClock` child, so it survives every swap. `WeatherClock.current()` returns it (the
  first one installed; a second install, such as a test's stand-in router, never replaces it).
- **The clock.** Each frame `_process` → `advance(delta)` adds the frame's delta to `time_s` and writes it through
  `ShaderGlobals.set_value`, so `ShaderGlobals.get_value(&"hymn_wind_time")` is always the live value. It is
  `PROCESS_MODE_PAUSABLE` (explicitly, whatever the router's mode), so it stops while the tree is paused. It is never
  reset: `hymn_wind_time` is not in `ShaderGlobals.ZONE_GLOBALS`. `set_time(s)` scrubs it. It is in
  `ShaderGlobals.FRAME_GLOBALS`, so the per-frame write never calls the ShaderGlobals listeners (one group call over
  every VegetationPlant per frame for nothing); the wind still notifies.
- **Zone wind.** On `SceneRouter.scene_swapping(scene_path)` it writes `hymn_wind` from
  `game/data/world/zone_weather.json`: the `zones` row whose `scene` is the new scene, else `default` (a moderate
  breeze, so a battle or a zone without a row never has a frozen sea). A row is `toward_azimuth_deg` (the downwind
  heading, clockwise from north = -Z, as the water and Haluna rigs use), `wind_m_s` and `gust`.
  `hymn_wind` = (sin(az)·speed, 0, -cos(az)·speed, gust). `hymn_wind` is deliberately **not** a zone global: the owner
  writes it on every swap, so no zone inherits the previous zone's wind, and the two `scene_swapping` handlers never
  depend on their connection order. A scene run on its own (F6, no swap) gets its row on the first running frame, and
  nothing if it has none. `tools/validate_data.py` (`check_zone_weather`) checks every row and that each scene exists.
- **Holds.** `hold(holder)` / `release(holder)` (a freed holder drops out, like `SceneRouter.hold_swap`): while
  anything holds the clock it neither advances nor writes either global. A zone wind that arrives meanwhile is written
  on release, with the clock. A cutscene that scrubs the sea holds it and calls `set_time`.
- **Screenshots stay deterministic.** `tests/screenshots/capture.gd` holds the owner in `_ready` (before any frame)
  for its whole run, so no shot sees the clock or a zone wind, a shot's `setup.globals` and a rig's own writes are the
  only writers, and no baseline moves. The capture setup also re-applies pinned globals after every `_process` and on
  `frame_pre_draw`, so even an unheld owner could not beat a pinned global. The test runner calls every test
  synchronously from its `_ready`, so the owner never ticks during tests; tests call `advance()` directly.
- **One writer.** The Drownbell flood rig (`BattleBossVfx`) no longer runs a clock of its own: it reads the shared
  clock through the global like any `WaterSurface`. Its `flood.weather` breeze still applies only when the wind is
  calm, which in play (the default zone wind) never happens; it remains for the drownbell_flood test rig.
- **Test rigs** (water, haluna_mood, undertow, vegetation, character stages) still write the globals themselves with
  `RenderingServer` for their shots. The rigs that write every frame run after the owner (autoloads process first),
  so they win in the editor too; the vegetation and character stages write once, so the clock moves them in F6 play,
  never under the capture.
- **Precision.** The clock is a float32 in shaders: after 10 h of play its step is about 4 ms, still smooth. A wrap
  would need every periodic term to share a period; revisit only if long sessions show stepping.
- Tests: `tests/unit/test_weather_clock.gd`, `tools/tests/test_zone_weather_validate.py`.
