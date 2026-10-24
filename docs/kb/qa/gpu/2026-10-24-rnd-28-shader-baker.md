# M1-RND-28: the export shader baker on a Windows release build (2026-10-24)

Machine: RX 9070 XT, Windows 10, Godot 4.6.3. Branch `gpu/m1-rnd-28-shader-baker`, from `gpu/slice-perf-sweep`.
This is ADR 0029 follow-up 1, which the Lead approved (2026-10-24).

## Templates

- **Downloaded:** `Godot_v4.6.3-stable_export_templates.tpz` from the official GitHub release
  (`github.com/godotengine/godot/releases/download/4.6.3-stable/`), 1,255,918,323 bytes.
- **SHA-512:**
  `da606b61c10157844f8300172df374472665f95015495cb1a7cd132c40ede404faa96cc1016a4b9662db9909ddea69632c4948b2cd11163438dad4808881fb68`.
  It matches the release's `SHA512-SUMS.txt` (`sha512sum -c`: OK).
- **Installed** in Godot's standard folder, `%APPDATA%/Godot/export_templates/4.6.3.stable/` (`version.txt`:
  4.6.3.stable). The archive was deleted afterwards, and nothing is committed.

## Export presets

- **`Windows Desktop`:** `shader_baker/enabled=true`. A release export takes 24 s and bakes 1262 shader steps.
- **New `Windows Perf` preset** (`runnable=false`, feature `perf_build`): the same build, but it keeps
  `tools/gpu_bench` and `game/levels/_tests` (see the blocker below). Its main scene is the slice sweep, through
  project.godot's `run/main_scene.perf_build`. Release binaries refuse a scene path on the command line, and the
  override applies only to builds with that feature.
- **Run it:** `build/windows_perf/hymn_of_the_undertow.exe --audio-driver Dummy -- --preset=high --res=2560x1440`.

## Blocker found: a release build of the shipping game is broken

`Windows Desktop` excludes `game/levels/_tests/*` (since bba1f6d), but shipped code depends on it:
- `HalunaZone`, `haluna_collision.gd` and `GraphicsRuntime` use `HalunaDresser`, `HalunaTerrain` and
  `WeatheringTide` from `_tests/haluna_mood/`.
- `haluna.tscn` instances `haluna_mood.tscn`.
- `VegetationPlant` lives in `_tests/vegetation/`.
- `gerstner_waves.gd`, `locations.json` and `sequencer.json` reference `_tests` paths.

In that build `scene_router.gd` fails to compile (a depended script), and Haluna can't load. Filed **M2-ARC-04**
(architect).

A side note: the export logs "Failed loading resource: res://game/data/loc/dialogue.csv" (and `strings.csv`). That
happens editor-side only; the exported game's translations load (no runtime error).

## Measured: the slice sweep in the release build (High, 2560×1440, 6 s dwell; ms)

"Cold" is a fresh install: this project's `shader_cache` and `vulkan` caches cleared. "Warm" is the second launch.

| Segment | Release + baker, cold | Release + baker, warm | Release, no baker, cold | Editor binary, cold |
|---|---|---|---|---|
| Title: hidden worst / visible worst | 1009 / **1240** | 255 / 160 | 1188 / 1218 | 513 / 217 |
| Haluna Beach: hidden worst / whole entry | **1978 / 8045** | 572 / **2550** | 2836 / 11380 | 512 / 3057 |
| Haluna Beach: visible worst | 4.5 | 5.6 | 4.4 | 4.6 |
| Tideline battle: hidden worst / entry / visible worst | 138 / 787 / 7.9 | 102 / 635 / 6.8 | – | 136 / 734 / 8.1 |
| Shell Shrine: hidden worst / entry / visible worst | 167 / 528 / 1.1 | 136 / 495 / 1.2 | – | 167 / 527 / 1.7 |
| Drownbell battle: hidden worst / entry / visible worst | 292 / 913 / 6.0 | 291 / 921 / 5.0 | 481 / 1607 / 30.4 | 297 / 925 / 7.3 |
| The Flood, mid-battle: visible worst | **79** | 42 | **1024** | 60 |
| GPU median, Haluna Beach / Drownbell | 3.09 / 1.15 | 3.10 / 1.15 | 3.11 / 1.14 | 3.10 / 1.15 |

**The baker pays:**
- A cold Haluna entry falls from 11.4 s to 8.0 s, and its worst hidden frame from 2.8 s to 2.0 s.
- The Flood's first cold frame falls from 1024 ms to 79 ms.
- The cold Drownbell entry falls from 1.6 s to 0.9 s.

**A fresh install still fails ADR 0029 / SPEC v1.3 §4.2:**
- hidden frames up to 2.0 s, against 1 s;
- Haluna's entry at 8 s, against 3 s;
- the title visible at 1.2 s;
- the Flood at 79 ms, against 50.

What's left cold is pipeline creation on the driver; the baker removes shader compilation, not pipelines. The second
launch passes on everything but the title (M2-ARC-03) and the Flood's 42 ms (M2-RND-07). Haluna's release-build entry
is 2.55 s warm, inside 3 s, where the editor binary takes 3.1 s. Filed **M1-RND-29** for the first launch.

**The editor binary's cold run is far better than the release build's** (Haluna 3.1 s, title 217 ms). It doesn't
recompile what the release build does. It likely holds a cache outside `user://`, so editor-binary measurements
understate a player's first launch. Use the perf build for cold numbers.

**Visible frames** here are the sweep's own window. `SceneRouter.last_swap_stats["max_visible_frame_ms"]` (M1-ARC-16)
isn't merged yet; re-run once it is.

## Checks

- Godot `--export-release` for both presets.
- validate_data and `taskboard --check`.
- No game code changed. The only changes are export_presets.cfg and the `run/main_scene.perf_build` feature override
  in project.godot, which shipped builds never see. So no Godot tests and no screenshots.
