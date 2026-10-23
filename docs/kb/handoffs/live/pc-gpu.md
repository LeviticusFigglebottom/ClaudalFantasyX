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
  - `water_look_probe.tscn` needs its `--out` folder to exist, or it errors and hangs.
  - A GDScript test file that fails to parse just drops out of the filtered run (the counts fall). Check the
    `Tests: N run` count, not only `0 failed`.
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
| M1-RND-18 SSS crest fade, high cameras | gpu/rnd-18-sss-crest | review (character) | Crest SSS fades with view steepness for cameras ≥ 10–25 m above the water; even `col_deep` lift. Survey: 0.06 % over 0.03, max 0.050, deep band ΔE 0.019. Low shots bit-identical. Report: `docs/kb/qa/gpu/2026-10-23-rnd-18-sss-crest.md` |
| QA-05b Asha re-check (High, Ultra) | gpu/qa-05b-asha-recheck | done (note in the QA-05 report) | Cheek banding gone; faint smile-fold steps on Ultra only. Hair warm brown (scalp hue 20°, braid 23°), not black. |
| M1-ENV-03 vegetation follow-ups | gpu/env-03-vegetation | review (rendering) | Eave glow removed (shelter auto-probe); FXAA capture + 0.008 threshold; 6 m LOD cross-fade (+0.04 ms); overdraw budget; PLACEHOLDER list; flutter cap. Drift: veg_*, haluna_h02/h03. Report: `docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md` |
| Perf regression sweep | gpu/perf-sweep | done | 31 cameras × 4 presets × 2 res (`docs/kb/qa/gpu/perf_baseline.csv`). Nothing over or at risk against SPEC §4.2; worst High 1440p is Undertow Eye 5.3 ms (12.2–14.9 projected). Report: `docs/kb/qa/gpu/2026-10-23-perf-sweep.md` |
| M1-RND-16 criterion 5 (cutscene AA override) | gpu/rnd-15-prewarm | measured | Override TAA + bilinear: dither −22 % vs native TAA, −0.40 ms. Recommended. Report: `docs/kb/qa/gpu/2026-10-23-rnd-16-aa-override.md` |
| M1-QA-05c Asha §14 final judgement | gpu/qa-05c-asha-final | done | Neutral passes; smile passes after RND-20 (corner terminator); grief fails (mouth interior black, teeth read gold, faceted). Lashes and lid band are asset faults. Report: `docs/kb/qa/gpu/2026-10-23-qa-05c-asha.md` |
| M1-RND-20 smile-corner terminator | gpu/rnd-20-smile-terminator | review (character) | Key and rim bias 2.5 → 4.5: corner clean, nose and contact intact. Shader band rejected (breaks the nose shadow). Drift: all `asha_*`. Report: `docs/kb/qa/gpu/2026-10-23-rnd-20-smile-terminator.md` |
| M2-RND-01 half-res body | gpu/m2-rnd-01-undertow | doing | SubViewport body at tier body_scale (Medium/High 0.5) + proxy composite (tent, capped-cylinder occlusion): High Day 4.94 → 2.27 ms, Eye 5.41 → 2.68. Report: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md` |
| Playtest checkout (Lead request) | – (clone of claude/new-session-mj8c3c, re-pulled to 7f4c76b) | done | `C:\Users\Aaron\Hymn_Playtest`, imported twice. 60-frame headless smoke boot: exit 0, no errors. **PLAY.bat is at `C:\Users\Aaron\Hymn_Playtest\PLAY.bat`** (EDITOR.bat next to it). Not launched. |
| Earlier (merged by the Lead) | gpu/results-2026-10-23, gpu/rnd-10-undertow-perf, gpu/rnd-09-undertow-shading, gpu/rnd-08-water-glimmer, gpu/rnd-07-presets, gpu/qa-05-asha-gpu, gpu/rnd-11-undertow-params | – | – |

## In progress

Nothing; between items.

## Queue, in order (Lead's standing queue of 2026-10-23; integration at 40aa118 and later)

1. **M2-RND-01** (`gpu/m2-rnd-01-undertow`), in progress.
   - Done: the half-res body (High 4.94 → 2.27 ms, glow dither 0.0092).
   - Done: multiple scattering (3 octaves, free).
   - Next: billow surface detail and striation regularity; the compute-pass occlusion inside the volume. Then move on to item 2.
2. **Grief mouth-interior fill** (QA-05c fault 2, rendering side; Asha materials only via write_materials.py). File
   the asset half (black interior, gold teeth) as a character task.
3. **M2-RND-03**, the battle VFX library (claimed for this session). SPEC v1.2 power tiers are lesser, greater and
   grand; no -ra/-ga style suffixes.
4. **M2-RND-02**, underwater rendering (claimed for this session).
5. **M2-RND-04**, Drownbell boss VFX and flood rig. Read the First Playable session's boss data first (branch
   claude/first-playable).
6. **Standing:** GPU checks of shots before the Lead re-approves lavapipe baselines.

Message the Lead (cloud session "New session") when two items are left.

## Local-only state (not in git)

- **`C:\Users\Aaron\Hymn_Playtest`**: a separate clone for the human's playtest, with `PLAY.bat` and `EDITOR.bat`
  (untracked, local only). Delete it freely after the playtest.
- Scratch renders and CSVs under `C:\Users\Aaron\chr04`, `C:\Users\Aaron\rnd12` and `C:\Users\Aaron\m2rnd01`, `C:\Users\Aaron\rnd15`, `C:\Users\Aaron\rnd17`, `C:\Users\Aaron\rnd18`, `C:\Users\Aaron\qa05b` and `C:\Users\Aaron\env03`.
  Everything quoted in the reports is reproducible from the commands in them; none of it is needed.
- Edit scripts and the keep-awake helper live in the session scratchpad (temporary).
