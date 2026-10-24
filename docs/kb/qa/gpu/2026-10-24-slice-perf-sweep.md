# Slice perf sweep: the first-playable thread end to end (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3, 2560×1440. Branch `gpu/slice-perf-sweep`, cut from the integration branch at
a2e1d4b. This is queue item 5. New tool: `tools/gpu_bench/slice_sweep.tscn`.

**Method.** The sweep boots as the game does: the preset goes through GraphicsRuntime (never saved), then boot.tscn
through SceneRouter, so the boot warm-up, the prewarm, the fade and the graphics hook are all real. It then walks the
thread in the game's order.
- **Title** (boot.tscn).
- **Haluna**, at three spawns: Beach, Village and CausewayHead.
- **The tideline field battle.**
- **Shell Shrine.**
- **The Drownbell field battle,** then its Flood phase, forced (bell HP to 40 %).

**Setup.**
- The story flags that would start a cutscene are set, so each view is the playable one.
- Autosaves are held.
- Each view dwells 8 s, one process per preset, with the shader caches warm.

**Per segment** (as ADR 0029 / SPEC v1.3 §4.2 define them):
- **Hidden:** the frames under the fade, from the request until the scene is in. Each frame must be under 1 s,
  and the whole entry under 3 s.
- **Visible:** from then until 60 frames after the fade lifts, each under 50 ms.
- **Dwell:** GPU and wall time.

All 24 rows are in `docs/kb/qa/gpu/perf_baseline.csv` (`scene` = `slice:<segment>`), with new optional columns:
`gpu_mean_ms`, `frame_max_ms`, `hidden_max_ms`, `hidden_total_ms` and `visible_max_ms`.

## Results

Per zone and preset: GPU median (mean) over the dwell, and the dwell's worst frame. Then the transition: worst
hidden frame / whole hidden entry, and the worst visible frame. All in ms.

| Segment | Low GPU | High GPU | Ultra GPU | Dwell worst (L/H/U) | Hidden worst / total (H) | Visible worst (L/H/U) |
|---|---:|---:|---:|---|---|---|
| Title | 0.03 | 0.03 | 0.03 | 0.9 / 0.7 / 0.8 | 330 / 1016 | **188 / 168 / 265** |
| Haluna, Beach | 1.69 (1.68) | 3.09 (3.08) | 5.67 (5.60) | 3.2 / 4.0 / 6.5 | 499 / **3115** (Low 3513, Ultra 3078) | 5.9 / 4.7 / 7.3 |
| Haluna, Village | 1.67 | 2.81 | 4.37 | 3.5 / 3.8 / 5.0 | – | 3.6 / 4.8 / 6.1 |
| Haluna, CausewayHead | 1.09 | 1.97 | 2.91 | 1.9 / 2.6 / 3.8 | – | 5.3 / 6.2 / 7.1 |
| Tideline battle | 0.58 | 0.88 | 0.83 | 1.4 / 2.2 / 1.5 | 108 / 652 | 7.6 / 8.2 / 8.4 |
| Shell Shrine | 0.39 | 0.62 | 0.58 | 1.1 / 1.3 / 1.1 | 135 / 498 | 1.5 / 1.9 / 1.5 |
| Drownbell battle | 0.74 | 1.16 | 1.30 | 1.5 / 1.7 / 2.0 | 301 / 938 | 6.2 / 9.1 / 8.2 |
| Drownbell, the Flood (mid-battle) | 0.89 (1.01) | 1.33 (1.59) | 1.45 (2.14) | 1.8 / 2.8 / 3.9 | – | **39 / 44 / 41** (a trial run: 61) |

**Frame budget: well inside.**
- The heaviest view is Haluna's beach: 3.1 ms at High 1440p, 7.1–8.7 ms projected on an RTX 3060, against
  16.7 ms (`perf_budget.py`: all "ok").
- Ultra's beach is 5.7 ms.
- Battles and the shrine are under 1.4 ms. The Flood adds about 0.2–0.4 ms on average.

## Over budget, or at risk: filed

1. **Haluna's zone entry takes 3.1–3.5 s, against the 3 s limit.** Its worst hidden frame is 0.5 s, which is fine.
   - SceneRouter's stats: the zone's instance on the worker thread takes 1.57–2.05 s (HalunaZone's prebuild runs
     in it), and the prewarm 0.47–0.49 s, on top of the threaded load.
   - Filed **M2-ENV-05** (environment, request-from rendering).
2. **The title's first visible frames hitch: 168–265 ms.**
   - The boot screen *is* the bootstrap title. The swap frame, the font warm-up (186 ms) and the resident shader
     warm-up (RND-27) all run while the menu shows.
   - ADR 0029 counts the boot warm-up as hidden, which assumes a boot screen *before* the title.
   - Filed **M2-ARC-03** (architect): keep the title behind a loading card or the fade until the warm-up ends.
3. **At risk: the Drownbell's Flood phase,** 39–44 ms mid-battle in the dwell runs, and 61 ms in a trial run (its
   first Flood in that process).
   - It's visible, it's mid-battle, and it's close to the 50 ms limit.
   - Likely cause: the polyps joining (their models' first draw) and the flood rig's first rise. That's my own
     RND-04 rig, so it's filed under rendering as **M2-RND-07**.

## Not covered

- **Cutscenes.** Cutscene A (the girl on the beach), B02, B05 and the First Verse were skipped by their flags; their
  cameras and characters are another load.
- **The prologue,** which isn't in the item's thread.
- **The 1080p minimum-spec rows.** The item asked for 1440p.
- **Visible frames** are measured by the sweep itself. SceneRouter's own `max_visible_frame_ms` comes with M1-ARC-16;
  re-run then. The CLI is the same.

## Checks

- **Run:**
  - gdlint and gdformat on the tool.
  - `perf_budget.py`, merged.
  - The tools unittests (`perf_budget.py` changed), validate_data and `taskboard --check`.
- **Skipped:** the Godot tests (no game code changed; the tool lives in `tools/`) and screenshots.
