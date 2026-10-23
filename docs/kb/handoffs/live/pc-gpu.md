# Live log: pc-gpu environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a). It is updated on each `gpu/*`
branch after every finished item, and it replaces `docs/kb/qa/gpu/2026-10-23-pc-queue-progress.md` as the canonical
record. The newest copy is on the most recently pushed `gpu/*` branch.

## Environment

- **Machine:** Windows 10, AMD RX 9070 XT, 16 GB RAM.
- **Session:** session_01778wbLbDFnRRLTKjnawv3T.
- **Clone:** `C:\Users\Aaron\hymn_gpu`.
- **Godot:** `C:\Users\Aaron\godot_463\Godot_v4.6.3-stable_win64_console.exe` (4.6.3-stable, Forward+/Vulkan).
- **Keep-awake helper:** `keep_display_on.ps1`, run from the session scratchpad (SetThreadExecutionState). The monitor
  must stay physically on, or Vulkan swapchain creation fails.
- **Rules:**
  - Work on new `gpu/*` branches only, each cut from `origin/claude/new-session-mj8c3c`. Never overwrite lavapipe
    baselines; list the shots that drift.
  - Keep the cumulative CPU, memory and GPU load at or below ~75 %, and run benchmarks and captures one at a time.
  - Gate scope (CLAUDE.md §3): run only the checks a change can break.
- **Gotchas:**
  - After merging the integration branch, run `godot --headless --import` first. A stale class cache fails ~260 battle
    tests.
  - `tests/screenshots/capture.tscn` hung for 100 minutes on the Undertow shots here; use
    `tools/gpu_bench/capture_preset.tscn` with `timeout`.
  - Python generators write CRLF on Windows; normalise to LF before committing.
  - **Asha's materials change only through `assets_src/characters/asha/write_materials.py`**, run with plain
    Python (no Blender). Commit both the script and its outputs. A hand edit to a `.tres` fails the Blender rebuild
    gate (Lead, 6e09360).
  - `tools/tests/test_blender_builds.py::test_python_runs_use_this_interpreter` fails on Windows (path separator
    in `expand`), on the base too.

## Done (branches pushed)

| Item | Branch | Task status | Summary |
|---|---|---|---|
| M1-CHR-04 rendering + material half | gpu/chr-04-materials | review | Face terminator: key/rim `shadow_normal_bias` 2.5. Vest lacquered leather 0.55/0.16/0.55, now in `write_materials.py`. Hair reads warm brown. All `asha_*` drift. Report: `docs/kb/qa/gpu/2026-10-23-chr-04-materials.md` |
| M1-RND-12 Haluna sky tiers | gpu/rnd-12-sky | review | Clouds 3.7 → 0.4 ms (High 1440p) and 2.4 → 0.23 ms (Low 1080p) via baked lattices and `sky_detail` tiers. R2–R6 and palette_check done. All 5 `haluna_*` drift. Report: `docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md` |
| M2-RND-01 start (sweep-G ch08) | gpu/m2-rnd-01-undertow | doing (more criteria remain) | Wall foot (skirt, water-dark base, scud), outer spray over the body, the sea answers the storm, joined flanks. Day 4.95 ms High 1440p, all cameras ≤ 5.43. Undertow shots drift. Report: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md` |
| M1-RND-15 criterion 4 (prewarm, Low-TAA ghosting) | gpu/rnd-15-prewarm | review (measured; 50 ms not met, needs a Lead/Systems decision) | Lazy material loads, batch 2, no halving on the first tick. Worst prewarm frame ~230–310 ms (set-up), up to 0.62 s (Undertow, cold). Ghosting mild. Report: `docs/kb/qa/gpu/2026-10-23-rnd-15-prewarm.md` |
| M1-RND-17 dusk released motes | gpu/rnd-17-dusk-motes | review (character) | Streaks upright (median 37 → 6°) and the upper-sky halo is gold. Horizon and mirror hue targets not met (pale cores; the Art Director's call). New mote_halo/mote_streaks advisory checks. Drift: glimmer_dusk, glimmer_release. Report: `docs/kb/qa/gpu/2026-10-23-rnd-17-dusk-motes.md` |
| Playtest checkout (Lead request) | – (clone of claude/new-session-mj8c3c @ 9508ade) | done | `C:\Users\Aaron\Hymn_Playtest`, imported twice. 60-frame headless smoke boot: exit 0, no errors. **PLAY.bat is at `C:\Users\Aaron\Hymn_Playtest\PLAY.bat`** (EDITOR.bat next to it). Not launched. |
| Earlier (merged by the Lead) | gpu/results-2026-10-23, gpu/rnd-10-undertow-perf, gpu/rnd-09-undertow-shading, gpu/rnd-08-water-glimmer, gpu/rnd-07-presets, gpu/qa-05-asha-gpu, gpu/rnd-11-undertow-params | – | – |

## In progress

Nothing; between items.

## Queue, in order (exact next step first)

1. **M1-RND-18**, the SSS crest fade for high cameras, with deep water within ΔE_ok 0.07 (`gpu/rnd-18-sss-crest`).
   Claim it in the task file.
2. **M1-ENV-03**, the vegetation follow-ups judged on the GPU (`gpu/env-03-vegetation`).
3. **Perf regression sweep** (`gpu/perf-sweep`).
   - Every scene with a camera, at Low/Medium/High/Ultra × 1080p/1440p, with gpu_bench.
   - Output: `docs/kb/qa/gpu/perf_baseline.csv`, plus a report flagging anything over the SPEC §4.2 budgets.
   - Sweeps under ~30 minutes at a stretch.
4. Then write **QUEUE EMPTY** here.

## Local-only state (not in git)

- **`C:\Users\Aaron\Hymn_Playtest`**: a separate clone for the human's playtest, with `PLAY.bat` and `EDITOR.bat`
  (untracked, local only). Delete it freely after the playtest.
- Scratch renders and CSVs under `C:\Users\Aaron\chr04`, `C:\Users\Aaron\rnd12` and `C:\Users\Aaron\m2rnd01`, `C:\Users\Aaron\rnd15` and `C:\Users\Aaron\rnd17`.
  Everything quoted in the reports is reproducible from the commands in them; none of it is needed.
- Edit scripts and the keep-awake helper live in the session scratchpad (temporary).
