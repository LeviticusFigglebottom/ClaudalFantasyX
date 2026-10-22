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

Still planned: dialogue runner (`game/narrative/`), battle scene glue (`game/battle/scene/`), Lattice (`game/progression/`), UI theme (`game/ui/`), and debug overlays F1–F12 (SPEC §5.4, task M1-ARC-02).

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
