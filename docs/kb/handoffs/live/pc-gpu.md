# Live log: pc-gpu environment

Seeded by the Lead on 2026-10-23. **This environment owns this file** (CLAUDE.md §7a). It's updated on each `gpu/*`
branch after every finished item, and it replaces `docs/kb/qa/gpu/2026-10-23-pc-queue-progress.md` as the canonical
record. The newest copy is on the most recently pushed `gpu/*` branch.

> **Current session (from 2026-10-29 ~20:20 EDT):** a new Remote Control session on this PC. The Lead is
> `session_01Bg3iP7cPGyjbX4CyniBahc`; the integration branch is **`claude/new-session-mj8c3c`**.
> **This copy, on `gpu/act1-qa-3`, is the newest.**

## BACK ONLINE @ 2026-10-29 ~20:20 EDT: the Lead's pass-3 queue

- **LFS: this PC reaches lfs.github.com** (HTTP 302 from Git Bash). `git lfs pull` fetched all 197 LFS objects
  into the big18 worktree. The PC can push LFS objects on request.
- **GPU-QA-DONE pass3 @ gpu/act1-qa-3.** Rows and the pass-3 summary are in `docs/kb/qa/act1_gpu_qa.md`; contact
  sheets are in `docs/kb/qa/gpu/act1/pass3/`.
  - Pass A: 618 of 619 shots. field_hud_over_haluna_wake hangs on a missing scene (row 43).
  - Pass B: the walk, 141 segments.
  - Open rows: 14 fixed (4, 6, 12, 15, 18, 19, 26, 27, 28, 32, 33, 35, 36, 40). Still open: 17, 21, 23, 24, 25, 31, 34,
    37, 38, 39.
  - New rows 43–63, with owners.
  - Every track's PC-QUEUE answer is in the summary. One example: hero-integration's `material is null` comes from
    the Corrow storm figure (row 44, creatures).
  - Pass B's budget (the walk with stills): hidden-frame entries are mostly < 1 s now. Still OVER: Ch5 1707,
    Pemakar 1625, Ch6 1640, Ch8 1804, Ch9 1529 and Corrow-night 1279 ms. The clean, still-free numbers are item 3.
- **Items 2 and 3 are done** (the PC-QUEUE, and the hitches as a quick confirm per ADR 0205). Results are in
  act1_gpu_qa.md under "Pass 3 hitches" and "Pass 3 costs"; the per-zone rows are `act1_big18:*` in perf_baseline.csv.
  - Clean High walk: every hidden frame is ≤ 1.82 s, so all pass the 2 s bar.
  - Fresh-process GPU swap sweep: Corrow 2151 ms and Pemakar 2016 ms, just over 2 s.
  - Row 64: fights show a visible frame over 50 ms after the fade (tideline 79, causeway 123, Drownbell 98, Hermit
    108–121, Matron 142, Moll 55–70 ms). Owner battle-presentation / tech.
  - Row 65: M3-RND-21's smoke is 0.31 ms for 3 columns, and M3-RND-26's drop is 0.36–0.43 ms, both over 0.3 ms. The
    fires cost 0.03 ms.
  - The Spar-wraith's 45° turn is still open: it needs a capture in motion.
  - Low and Ultra were not run (the Lead's quick-confirm call).
  - New tool options: `--hide=<glob>` in gpu_bench and capture_preset.
- **Row 17 (Undertow eye), the Lead's ask: MERGE-READY `gpu/row17-undertow-eye-rings` @ 12cf79cb (M3-RND-29, in
  review).**
  - The sea shader only: the spiral patterns are anti-aliased, the throat streaks redirected, and the normal is now
    computed per pixel.
  - `--filter=undertow` 53/0. Cost +0.02–0.10 ms at High 1440p.
  - Lavapipe: the undertow_* shots that see the storm's sea will drift; re-approve them after viewing.
- **Item 5 (Blender verifies): skipped**, per the Lead (ADR 0205: non-blocking).
- **Item 4 (my RND work):** every RND branch named (M2-RND-01/02/03/04, M1-RND-22) is already merged and `done`.
  Taking the rendering request tasks instead:
  - **MERGE-READY `gpu/m3-her-1152-1124-freed-casts` @ ef078a10**, which fixes M3-HER-1152 (the RevenantTells cast)
    and M3-HER-1124 (the UnderwaterRig deferred root). Both tasks are in review (qa).
    - Checks: `--filter=_thread` 40/0 with no deferred-call error; revenant 8/0; underwater 8/0; lint and format clean.
    - test_freed_cast_lint's one remaining hit is env-art-b's ebbing_motes (fixed on their branch).
  - M3-RND-28 (the Ch8 storm figure) should be met by creatures' storm figure (M3-HER-1142, MERGE-READY on
    claude/creatures); I'll check it in pass 4. Still for rendering: M3-RND-28 (the Ch8 storm figure's capsule over the water) and M3-HER-1161 (EbbingMotes, fixed by
    env-art-b on their branch).
- **Item 1 (the plan as started), Act I real-GPU QA pass 3:** on `gpu/act1-qa-3`. That's origin/lead/gate-big18 @ 37a90b4c,
  plus integration cf03aa8d (4 commits ahead), plus gpu/act1-qa-2, which held act1_gpu_qa.md and had never been merged.
  The worktree is C:/Users/Aaron/hymn_qa3.
  - The walk gains the three Act I zones it lacked: ch04/haluna_wake, ch05/pemakar and ch09/corrow_night.
  - Pass A (619 shots, High ×2.667, `--setup`), then pass B (the walk), then the swap sweep (`act1_swap_sweep.py`
    run windowed on the GPU), then re-checks of the rows.
- Items 2–5 follow, in the Lead's order.
- **Audio's PC-QUEUE (listening on real speakers) needs the human: skipped.**

## RESUMED @ 2026-10-27 ~23:30 EDT (the Lead: ADR 0041, Act I final quality first)

The paused 13-request render queue is **retired** (the cloud tracks self-render now). The new priorities, in order:
1. **Gates from big14 on**: the full suite, coverage, Blender for the touched jobs, the full manifest on lavapipe, contact sheets, results on gpu/gate-bigN-shots. No GATE-REQUEST yet (lead/gate-big13 was gated by the cloud).
2. **Act I real-GPU QA** (between gates): `docs/kb/qa/act1_gpu_qa.md`, contact sheets on gpu/act1-qa-<n>.
   - Pass A: every manifest shot at High 2560×1440 (capture_preset). Running.
   - Pass B: the walk. slice_sweep gained `--walk`, `--stills` and a hitches_33ms column; `tools/gpu_bench/act1_walk.json` covers the title, the Prologue, Ch1–Ch9 by chapter start, every spawn, one battle per arena and every boss. It also gives the per-zone frame-time budget (the --budget re-sweep, now over all of Act I).
3. **Heavy builds**: Blender verify of claude/characters, creatures and creatures-b vs the integration branch, in WSL clone /root/hymn_heavy. Running.
4. M3-RND-02 (the GPU clock cap) stays parked for the human.

Windows import note: on Windows, Godot 4.6.3's `--import` segfaults part-way (exit 139) on a fresh .godot; the second try completes. The QA scripts retry until exit 0 and the DONE line.

<details><summary>The pause (2026-10-27 17:29), kept for the record</summary>

## PAUSED @ 2026-10-27 17:29 EDT (the Lead's instruction, from the human)

No job of this session is running. WSL `hymn` is idle: the batch (PIDs 302 and 20150, both mine) was stopped after creatures fce2e82b finished, and `PAUSED` is the last line of /root/renders/batch.log. No gate, benchmark or Blender job is running.

**Done since the session began (all pushed):**
- The big11 gate.
- The big12 gate (`gpu/gate-big12-shots`, merged as e930595c).
- The Shell Shrine GI rebake on big12 (`gpu/shrine-gi-big12`).
- M2-NIT-904, the import exit-code and DONE check (`gpu/m2-nit-904-import-exit-check`; /root/gate.sh and /root/render_batch.sh are installed with it).
- M3-RND-03, implemented and checked on lavapipe (`gpu/m3-rnd-03-sefir-tells` @ c3fd1eb4; the 4 revenant_tells_* baselines are to be approved after viewing).
- M1-QA-09 on hardware (`gpu/m1-qa-09-heroes`).
- The M2-CHR-11 verify.
- Render queues 2–4 up to creatures fce2e82b, all listed as RENDERED below.

**Interrupted:** nothing mid-capture. The rest of queue 4 never started.

**Open render requests (unrendered, oldest first; the FAST-TRACK first):**
- the rest of queue 4: battle-presentation 5a5b4fed, env-art 60eee2f7, characters ee3bd335, env-art 29ddd021;
- queue 5 (new at the 17:00 scan): **hero-integration 7a8bff79 (FAST-TRACK)**, act1-chapters 9ccd51b2, env-art c990e2c2,
  m2-slice ca7c8ede, creatures db3c9507, ui da7891cf, battle-presentation ed3a458e, env-art 191e5e89, env-art ab58f891.
- Skipped as answered: 44a7d65c and 3fddb67b (both ancestors of big12, so its gate rendered them) and 12 older requests whose
  shots a later request covers (5a3f9a37, faa61872, 24bf927a, fa67bfee, f21fba5f, ba49617a, 05f6abc9, 9ba01356, dcc68922,
  32f33a75, b35e17c1, 5ff54f27). The audio and ze8rrn rows in render_scan's output mirror other tracks' lines.

**Hardware queue, not started:**
- The slice `--budget` re-sweep (ADR 0029/0037) is ready. The worktree is C:/Users/Aaron/hymn_budget, detached at integration 7f355a8f. It runs cold launches at High and Low with `--export` through tools/gpu_bench/run_cold_launch.sh, then the whole thread warm at High with `--budget`. The script is budget.sh in the session scratchpad.
- Then the Act I playthrough (F8 chapter select; Ch1 and Ch4–Ch9; findings as tasks 900–999).

**Exact next step on resume:**
1. `git fetch`, then re-run render_scan.py (requests may have arrived while paused).
2. Render the hero-integration 7a8bff79 fast-track first, then the open list above, oldest first, with /root/render_batch.sh.
3. Publish with render_publish.sh.
4. Then the budget re-sweep on the integration head of that day (re-point hymn_budget), and then the Act I playthrough.

</details>

## Renders for the tracks (RENDERED lines, newest first)

- RENDERED @ fce2e82b: gpu/render-creatures-fce2e82; 41 pass, 60 drift
- RENDERED @ 43492e80: gpu/render-env-art-43492e8; 0 pass, 1 drift
- RENDERED @ 121362b3: gpu/render-ui-121362b; 1 pass, 1 drift
- RENDERED @ 854e6a95: gpu/render-env-art-854e6a9; 1 pass, 4 drift
- RENDERED @ db0819b2: gpu/render-battle-presentation-db0819b; 18 pass, 27 drift
- RENDERED @ a195cd39: gpu/render-ui-a195cd3; 0 pass, 1 drift
- RENDERED @ 95be6118: gpu/render-env-art-95be611; 0 pass, 1 drift
- RENDERED @ 17b0601f: gpu/render-m2-slice-17b0601; 0 pass, 7 drift
- RENDERED @ 94fe8f77: gpu/render-env-art-94fe8f7; 0 pass, 3 drift
- RENDERED @ 26755f97: gpu/render-ui-26755f9; 2 pass, 0 drift
- RENDERED @ fd630bb8: gpu/render-env-art-fd630bb; 1 pass, 2 drift
- RENDERED @ 17325e00: gpu/render-ui-17325e0; 8 pass, 4 drift
- RENDERED @ 7f56d643: gpu/render-characters-7f56d64; 0 pass, 5 drift
- RENDERED @ 599b2418: gpu/render-env-art-599b241; 0 pass, 5 drift
- RENDERED @ c0ee5230: gpu/render-act1-chapters-c0ee523; 5 pass, 9 drift
- RENDERED @ d4430397: gpu/render-hero-integration-d443039; 0 pass, 6 drift
- RENDERED @ c1d1e3e6: gpu/render-battle-presentation-c1d1e3e; 2 pass, 4 drift
- **Shell Shrine GI rebaked on lead/gate-big12 @ 8a28be17** (the Lead's ask; test_shrine_gi_bake failed there): gpu/shrine-gi-big12,
  both states OK (1.56 s each, ~930 KB), gi_inputs.py --write; test_shrine_gi_bake passes. A first attempt ran on a silently
  aborted import (150 KB bake): the import retry now checks the exit code and the final DONE line (M2-NIT-904).
- RENDERED @ eeaf91bf: gpu/render-act1-chapters-eeaf91b; 0 pass, 2 drift
- RENDERED @ 44080e1e: gpu/render-creatures-44080e1; 0 pass, 4 drift
- RENDERED @ 8b25b3b4: gpu/render-m2-slice-8b25b3b; 1 pass, 7 drift
- RENDERED @ 99623a0c: gpu/render-ui-99623a0; 4 pass, 1 drift (portraits via render.sh: hullgnaw, scuttler, tide_crawler, undertows_reach
  byte-identical to the cloud PNGs; squall_wing 0.0083, wing glints only)
- RENDERED @ 8daa0c63: gpu/render-act1-chapters-8daa0c6; 0 pass, 2 drift
- RENDERED @ 8770a067: gpu/render-env-art-8770a06; 1 pass, 10 drift
- RENDERED @ 60b62678: gpu/render-battle-presentation-60b6267; 0 pass, 2 drift
- RENDERED @ 1b84b89c: gpu/render-hero-integration-1b84b89; 11 pass, 0 drift
- RENDERED @ 4ce8a48a: gpu/render-m2-slice-4ce8a48; 4 pass, 4 drift. **The Shell Shrine's GI rebaked on lavapipe** (both states,
  16 s; shrine_gi_{open,closed}.res and shrine_gi_inputs.json are on the branch, so test_shrine_gi_bake passes). slice_haluna_villagers_village:
  no capture at this sha (the PackedStringArray `flags` bug that 3fddb67b fixes).
- RENDERED @ b99be560: gpu/render-creatures-b99be56; 0 pass, 1 drift
- RENDERED @ 680cd88e: gpu/render-battle-presentation-680cd88; 0 pass, 4 drift
- RENDERED @ 21125780: gpu/render-creatures-2112578; 0 pass, 1 drift
- RENDERED @ 038d5651: gpu/render-characters-038d565; 10 pass, 9 drift
- RENDERED @ 5112837a: gpu/render-act1-chapters-5112837; 0 pass, 2 drift
- RENDERED @ 10f21a17: gpu/render-creatures-10f21a1; 0 pass, 2 drift
- RENDERED @ 179069de: gpu/render-env-art-179069d; 0 pass, 1 drift
- RENDERED @ b30c2cf2: gpu/render-act1-chapters-b30c2cf; 0 pass, 2 drift
- RENDERED @ ba16d48b: gpu/render-env-art-ba16d48; 2 pass, 2 drift
- RENDERED @ 6454c06c: gpu/render-ui-6454c06; 2 pass, 1 drift
- RENDERED @ 1a422476: gpu/render-env-art-1a42247; 3 pass, 0 drift
- RENDERED @ 22a5de11: gpu/render-env-art-22a5de1; 3 pass, 0 drift
- RENDERED @ 25dcea24: gpu/render-battle-presentation-25dcea2; 2 pass, 4 drift
- RENDERED @ 77a6a777: gpu/render-act1-chapters-77a6a77; 3 pass, 3 drift
- RENDERED @ 71f19fbc: gpu/render-env-art-71f19fb; 0 pass, 3 drift
- RENDERED @ b2453cfd: gpu/render-hero-integration-b2453cf; 3 pass, 7 drift
- RENDERED @ b5e05d2f: gpu/render-creatures-b5e05d2; 28 pass, 1 drift
- RENDERED @ fdec3cc6: gpu/render-m2-slice-fdec3cc; 12 pass, 9 drift
- RENDERED @ a0d2549f: gpu/render-env-art-a0d2549; 10 pass, 5 drift
- RENDERED @ 180510e1: gpu/render-act1-chapters-180510e; 0 pass, 2 drift
- RENDERED @ dc93a5de: gpu/render-characters-dc93a5d; 16 pass, 29 drift
- RENDERED @ 5317c0e6: gpu/render-ui-5317c0e; 51 pass, 25 drift (not in shots.json at this sha: portraits:hullgnaw,scuttler,squall_wing,tide_crawler,undertows_reach)

## Gate results (newest first)

- **GATE lead/gate-big14@8707ff90 (+ the shrine GI rebake 8f6fd29f): FAIL (Lead to view).** The suite and the manifest finished at 2026-10-28 ~04:30. Coverage (3 h limit, 2809 s): FAIL with no numbers, "suite did not pass under instrumentation (exit -6)": the 15 failures plus the crash at exit.
  - Shrine GI rebaked first; test_shrine_gi_bake passes.
  - Tools: 6 failing units: test_arenas (known), test_screenshots, test_pemakar_kit, test_zone_dressing_ch01, test_zone_map_pois, test_hero_clips.
  - Godot: 3161 run, 15 failed. Then a **segfault at exit** in test_villager_routines.gd:489 (creatures), which stops ci_local's pipefail on its own.
  - The suite now takes ~45 min. ci_local's default 600 s step and run_coverage's 600 s both time out; HYMN_STEP_TIMEOUT has to be raised.
  - Boot smoke ok. Coverage re-running with 3 h.
  - Blender: 77 changed jobs, 2 DIFF (kirru_roost.glb, avalanche_ram.glb).
  - Shots: 523 compared, 302 failed (121 new + 181 drift), no shutdown SCRIPT ERROR.
  - The human's four FAST-TRACKS on the GPU:
    - the Prologue colour: yes;
    - the run: grounded in the stills;
    - the beach: Rhen not in frame, and 4 lines on empty sky;
    - the party start: Asha and Toma walk ahead, but Rhen is not on screen.
  - Every scene change is over the 1000 ms hidden-frame budget (New Game 3.0 s, Ch2 2.0 s, the first fight 1.7 s, Ch1 1.3 s).
  - On lead/gate-ft-beach @ 93d0741e the beach works: Rhen in the shallows, Asha kneeling beside him. Still open there: Asha's skirt passes through him, two lines are framed on his waist, and the field camera starts underwater.
  - `docs/kb/qa/gate-runs/big14/` on `gpu/gate-big14-shots`.
  - **`gpu/ci-step-timeout-3h` @ 75e14190: MERGE-READY.** HYMN_STEP_TIMEOUT now defaults to 3 h in ci_local.sh, run_coverage.py and gate.sh.
- **GATE lead/gate-big12@8a28be17: FAIL (2 Godot failures = the cloud's, 3 tools failures, drift + 31 new shots; Lead to view).**
  Godot 2820/2: test_creature_portraits (the 4 new creatures "have a portrait in the manifest") and
  test_footsteps_slice_zones causeway tidepool (water expected, stone got). Coverage and boot not reached (ci_local stops
  there). Tools: test_screenshots (31 shots without baselines, not 41), test_iskarra (3 vigils on the paving, want >= 7),
  test_shrine_gi_bake (rebaked: gpu/shrine-gi-big12). Blender: 28/28 identical (asha, rhen, toma, sefir, ysolde, 9 villagers,
  kits, creatures). Shots: 341 compared, 111 failed = 31 no baseline + 57 newly failing (Asha/Toma/Rhen clips and views,
  the battle UI shots, strips, creature_portraits, shrine_s01, haluna h01/h04, vigil_line/voice_over) + 23 repeats
  (arenas camp/shoals re-dressed ~0.1, choreo, inquisitor intro 0.164); 20 of big11's failures pass now. The shutdown
  `Trying to cast a freed object` (life_audio.gd:124) now follows 19 shots. `docs/kb/qa/gate-runs/big12/` on `gpu/gate-big12-shots`.
- **GATE lead/gate-big11@23ea8c6f: FAIL (expected drift + a new shutdown script error; Lead to view).** Godot 2738/0,
  coverage and boot ok. Tools: the known test_shrine_gi_bake failure (lane A re-run with it non-fatal). Blender: 13/13
  identical (base ze8rrn). Shots: 303 compared, 43 failed: 7 new shots, 5 Haluna-villager field/dialogue shots,
  and 31 repeats of big10's (boss intros, choreo, arenas). New: `Trying to cast a freed object` at shutdown after
  11 villager/wildlife/Ch6 shots (capture.sh exits 1). `docs/kb/qa/gate-runs/big11/` on `gpu/gate-big11-shots`.
- **GATE lead/gate-big9@ae4666e0: FAIL (expected drift; Lead to view).** Godot 2561/0, coverage ok, boot smoke ok,
  lint/data/unittests ok. Blender: 51 changed jobs (base ze8rrn), 40 identical, 11 DIFF, all M2-CHR-11 (rhen, toma,
  9 villagers). Shots: 281 compared, 48 failed (battle hero rigs, arenas, boss intros, flood, save_shrine_field,
  field_tip_card, settings_accessibility, formation_menu, creature_portraits). PNGs, compare.txt and the README with
  the groups: `docs/kb/qa/gate-runs/big9/` on `gpu/gate-big9-shots`. Wall 37 min + an 18 min lane A rerun (the
  Blender DIFF stops lane A before the Godot suite, so the PC now runs Blender after the suite: see big10).
- **GATE lead/gate-big10@181708a7: FAIL (expected drift; Lead to view).** Godot 2637/0, coverage ok, boot smoke ok,
  lint/data/unittests ok. Blender: 22 changed jobs (base lead/gate-big9), 20 identical, 2 DIFF (rhen, toma: M2-CHR-11).
  Shots: 292 compared, 51 failed = 37 identical repeats of big9's (already approved), 8 repeats that changed again
  (Hullgnaw intro reframed 0.266, drownbell/matron intros, choreo hit/melee/toll/ko, creature_portraits), 6 new
  (boss intros hermit/inquisitor/wraith, field_hero_party/rhen_walk/gait_strip). `docs/kb/qa/gate-runs/big10/`.
  The gate now runs Blender after the suite (HYMN_SKIP_BLENDER=1 in ci_local, then verify_blender_builds.py).
- big9: merged by the Lead (integration 3b7cbf5e).

## Hardware queue results (newest first)

- **Heavy builds (2026-10-28 ~00:30, Blender 5.0.1 on the i9 (AVX2), changed jobs vs integration 608db549):**
  - characters @ 68ca13c9: 18/18 identical.
  - creatures @ cabcf669: 49 jobs, 1 DIFF. creatures-b @ 2b2efdf7: 53 jobs, the same 1 DIFF.
  - The DIFF: `assets/creatures/avalanche_ram/avalanche_ram.glb` (committed 6549c8a9… vs rebuilt 8d990e15…; POSITION data). The rebuild is the same on both branches, so the committed .glb no longer matches its source; it may have been built on a CPU without AVX2 (as in M2-CHR-11). Owner: creatures. Rebuild it from source, or say which machine built it.
- **M3-RND-03 lavapipe check (2026-10-27):** gpu/m3-rnd-03-sefir-tells @ 02d1fa52, 4 shots without baselines,
  `docs/kb/qa/gpu/2026-10-27-m3-rnd-03-lavapipe/`. With the tells on, Sefir's shadow edges are crisper and a tighter contact
  line runs along his hem. There's no double lighting and no black shadow. His reflection holds its outline (subtle with this
  test wave). Asha is unchanged. Rendering, env-art and art should view the shots and approve the baselines.
- **M2-CHR-11 verify (2026-10-27):** claude/characters @ 3723f3eb (incl. 20773234), AVX2 i9-12900K: base_body, rhen, toma
  and 9 villagers 12/12 identical (664 s). Reported to the Lead and characters.
- **Act I real-GPU QA, passes A and B and the budget (2026-10-28):** `docs/kb/qa/act1_gpu_qa.md` on `gpu/act1-qa-2`, 41 rows with owners, plus sheets under docs/kb/qa/gpu/act1/.
  - Pass B walked Act I on lead/gate-ft-beach: 122 segments, 401 stills.
  - New in pass B:
    - the BattleResultPanel freed-object error (506×);
    - ch06_ridge_skippers fought on the test stage;
    - Moll still a capsule in battle;
    - the Reach's arm fills the frame;
    - followers between the camera and Rhen (Ch3);
    - the camera against the Coilspire wall;
    - Ch9 without Asha and Toma.
  - **Budget:** every scene entry and battle start is OVER the 1000 ms hidden-frame budget. It grows from ~1.2 s (Ch1) to 4.1–4.5 s (Ch5–Ch9) as video memory climbs, so it may be accumulation. Visible frames are all within 50 ms, and GPU p99 is ≤ 3.6 ms everywhere. Owner: tech / ui (loading).
- **The human's four FAST-TRACKS on big15 (lead/gate-big15 @ 6466a6f5), RX 9070 XT, High 1440p (2026-10-28 ~09:30):** sheets in `docs/kb/qa/gpu/act1/playtest_big15/`.
  1. **The Prologue colour: yes.** Domes, blue bands and banners are in colour.
  2. **The beach: yes.** Rhen lies in the shallows with Asha kneeling beside him, both faces in frame. He then sits up and stands. Still open: Asha's skirt passes through him (row 31), and two lines are framed on his waist when he stands (row 32).
  3. **The party start: partly.** **Rhen is now on screen** at the start, with his lantern, walking beside Asha up the beach (start15.jpg). But the camera opens ~15 m back over the shallows, Toma isn't in frame, and when the camera turns in the village lane it swings into the stone walls with Rhen hidden.
  4. **The run: grounded** (the Ch1 filmstrip at 0.12 s).
- **Act I re-check on big15:** 15 of the open rows fixed, 12 still open (act1_gpu_qa.md, gpu/act1-qa-2).
- **Load: over 75% today.** While lane B ran, the big15 Windows import peaked at 94% total CPU for ~74 s, and the 48-shot re-check ran at a median of 85% (max 100%). The playtest walk ran during Blender at a median of 40% (max 67%). From now on, GPU work waits for the gate's single-process steps, or the gate drops to 1 shard.
- **big15 gate (running), lead/gate-big15 @ 6466a6f5** (restarted 06:35 when big15 moved from a44fec70):
  - Lane B done: 593 compared, 375 failed, wall 7538 s.
  - Blender running, then the lane-A suite (3 h limit) and coverage. Results to gpu/gate-big15-shots.
- **M1-QA-09 on hardware (heroes, 2026-10-27):** 49 shots at High 2× and Ultra on ze8rrn@f580e756, `gpu/m1-qa-09-heroes`
  `docs/kb/qa/gpu/2026-10-27-m1-qa-09-heroes/`. Asha's staff and Toma's spear aren't gripped (open hands; they float upright
  in run/walk_cycle/offer_hand). The staff goes through the skirt when kneeling. Asha's underskirt is a rigid tube in
  offer_hand, with the shin through it. The extreme_pose skirt stretches. Toma's beard edge is blotchy. Rhen's limbs and
  clothing, and Asha's braid, are clean. Identical at High and Ultra (asset or rig, not preset). Owners: characters
  (hero-integration for the prop attach).

## PC setup for a new session

- **Machine:** Windows 10 Home, AMD RX 9070 XT, 16 GB RAM, user `Aaron`.
  - Shells: PowerShell 5.1 and Git Bash.
  - Python 3.14 on PATH as `python`, with gdtoolkit (`python -m gdtoolkit.linter` / `.formatter`).
- **Clone:** `C:\Users\Aaron\hymn_gpu` (origin github.com/LeviticusFigglebottom/ClaudalFantasyX).
- **Godot:** `C:\Users\Aaron\godot_463\Godot_v4.6.3-stable_win64_console.exe` (4.6.3-stable official, Forward+/Vulkan).
  It isn't on PATH; set `G=/c/Users/Aaron/godot_463/Godot_v4.6.3-stable_win64_console.exe` in Git Bash.
- **The monitor must stay physically ON.** If the display is off or asleep, Vulkan swapchain creation fails, and every
  windowed run (gpu_bench, capture_preset) errors out.
  - Run `powershell -ExecutionPolicy Bypass -File tools/dev/keep_display_on.ps1 -Hours 10` in the background. It calls
    SetThreadExecutionState.
  - It stops sleep, not a human pressing the monitor's power button.
- **Load cap:** keep the cumulative CPU, memory and GPU load at or below ~75 %. Run benchmarks and captures one at a
  time, never in parallel. Kill only PIDs you started (CLAUDE.md §8a).

### Commands

```bash
# after any merge of the integration branch: re-import first (a stale class cache fails ~260 tests)
$G --headless --path . --import
# tests, filtered to the area you touched (check the "Tests: N run" count: a file that fails to parse just drops out)
$G --headless --path . res://tests/run_tests.tscn -- --filter=<area>
python tools/validate_data.py; python tools/taskboard.py --check
python -m gdtoolkit.linter game tests; python -m gdtoolkit.formatter -l 120 --check game tests

# GPU frame time (windowed, never --headless). Full option list at the top of tools/gpu_bench/gpu_bench.gd.
$G --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/gpu_bench.tscn -- \
  --scene=res://game/levels/_tests/undertow/undertow_test.tscn --camera=<path> \
  --presets=high --res=2560x1440 --csv=C:/abs/out.csv [--png-dir=C:/abs/dir --hold-storm --undertow-half=0.5]

# GPU screenshots of manifest shots at a preset (use this, not tests/screenshots/capture.tscn, for Undertow shots)
$G --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync res://tools/gpu_bench/capture_preset.tscn -- \
  --shots=id1,id2 --preset=high --out=C:/abs/dir [--scale=2 --hold-storm \
  --manifest=res://docs/kb/qa/gpu/2026-10-23-rnd-09-pending-shots.json \
  --light-set=prop=value,... --mat-set=uniform=value|#rrggbb,... --push-override=key=value]

# drift between two captures: linear-light RMSE, the same as the lavapipe gate
python -c "import sys; sys.path.insert(0,'tools/screenshots'); import compare, pngio; \
  print(compare.rmse_linear(pngio.read(sys.argv[1]), pngio.read(sys.argv[2])))" before.png after.png
```

- **Base vs branch drift:** capture both in a detached worktree of the base
  (`git worktree add --detach <dir> origin/claude/undertow-lead-handoff-423ixt`, then import it), and remove the
  worktree afterwards. For a drift that covers only uncommitted work: `git stash`, capture, `git stash pop`.
- **Metrics in `tools/`:** `mote_metrics.py` (glimmer halos/streaks), `aa_shimmer.py --ghost`, `sss_probe_metrics.py`,
  `perf_budget.py`, plus `tools/gpu_bench/eave_glow.tscn` and `lod_pop.tscn`.
- **GPU → min-spec projection:** RTX 3060 about 2.3–2.8× this card (the Lead uses ~3× for the Undertow); GTX 1060
  4.2–5.0×.

### Rules (from the Lead)

- **Branches:** work on new `gpu/*` branches only, one per item, cut from
  `origin/claude/undertow-lead-handoff-423ixt`. That's the integration branch from 2026-10-23; it replaces
  `claude/new-session-mj8c3c`, which is frozen at a504072. Never push to someone else's branch.
- **Baselines:** never overwrite lavapipe baselines; list the shots that drift. The Lead re-approves on lavapipe.
- **Gate scope** (CLAUDE.md §3): run only the checks a change can break, and say in the report what was skipped.
- **Tasks:** claim a task in its file (`status: doing`, `owner_session`) in the first commit, and set `status:
  review` at the end.
- **Asha's materials change only through `assets_src/characters/asha/write_materials.py`.** Run it with plain Python,
  normalise CRLF to LF, and commit the script and its outputs together. A hand edit to a `.tres` fails the Blender
  rebuild gate.
- **Commit trailers:** messages end with the Co-Authored-By and Claude-Session lines the harness gives.
- **Queue:** message the Lead when two queue items remain. Keep this file current after every item.
- **Reports to the Lead:** after each pushed item, send the branch, the commit and the shots that drift.
- **Standing interrupt:** GPU checks before a lavapipe re-approval (captures at High and Ultra, compared against the
  base). These jump the queue.
- **Gate before every push:** validate_data, the tools unittests, lint and format, and Godot tests filtered to the
  area.

### Gotchas

- `tests/screenshots/capture.tscn` hung for 100 minutes on the Undertow shots here. Use `capture_preset.tscn` with
  `timeout`.
- **Line endings:** Python generators and gdformat write CRLF on Windows. Normalise to LF before committing.
- `water_look_probe.tscn` needs its `--out` folder to exist, or it errors and hangs.
- **The compute body's Godot traps** (undertow.md, "Gotchas"):
  - A `.glsl` file expands one include level, and re-imports only when it changes itself, so run
    `tools/rendering/gen_undertow_compute.py`.
  - `get_cam_projection()` is already corrected.
  - Set `Texture2DRD` RIDs on the main thread.
  - Detach textures before freeing them.
- **New capture options:** `--add-box=x,y,z,sx,sy,sz` (a test box) and `--node-set=Path:prop=value` (e.g.
  `Storm:half_res_compute=false` for the SubViewport A/B).
- **`capture_preset --mat-set` doesn't reach the Undertow body.** The body renders in the half-res SubViewport.
  Edit undertow.json for the run instead, and restore it afterwards.
- **The capture size:** `capture_preset` writes 960×540 by default and 1920×1080 with `--scale=2`. Compare like with
  like.
- **Shell traps:**
  - Don't run `cat > file` without input; it blocks on stdin.
  - Inline heredoc Python with Windows backslashes or `\n` escapes breaks. Write a `.py` file instead.
- **Godot behaviours:**
  - Transparent materials write no motion vectors.
  - TAA destroys a transparent SubViewport's alpha.
  - `VISIBILITY_RANGE_FADE_SELF` alpha-blends the instance (it isn't a dither).
  - `RenderingServer.global_shader_parameter_get` and `shader_get_parameter_default` don't work at runtime or headless.
    Use `ShaderGlobals` (game/core/shader_globals.gd) for the globals.
  - A shader uniform default must be a literal.
  - `shadow_normal_bias` is in shadow texels, not metres.
- The Undertow half-res body uses visual layer 20; don't use it for anything else in a storm scene.
- **Known Windows-only failure:** `tools/tests/test_blender_builds.py::test_python_runs_use_this_interpreter`, filed
  as M1-QA-07.

## Branches (all pushed)

| Branch | State | Content |
|---|---|---|
| gpu/gate-big11-shots | big11 gate result (for the Lead to view) | 43 failing shots (out + diff PNGs), compare.txt, blender_diffs.txt, README. |
| gpu/m3-rnd-03-sefir-tells | **M3-RND-03 in review** (reviewer Art; env-art's M3-ENV-1000 waits on it) | RevenantTells: Sefir's reflection never ripples (still-actor capsule globals, flat SSR on his hits), his shadow faintly too sharp (keys stop casting him; a cancelling spot pair re-casts it crisper). 4 shots (on/off), 7 tests. Lavapipe no-drift check of the water shots queued. |
| gpu/m1-qa-09-heroes | **M1-QA-09 on hardware** (report) | 49 hero shots at High 2x and Ultra; staff/spear not gripped, skirt and underskirt clipping (characters). |
| gpu/m2-nit-903-runner-renders | **M2-NIT-903** (runner, for the Lead) | tools/dev/pc_gate: gaterun.sh (Blender after the suite), the import-crash retry in gate.sh, render_scan.py / render_batch.sh / render_publish.sh for track RENDER-REQUESTs; NIT-902's fresh-.godot sync.sh; gate_runner.md section. |
| gpu/gate-big9-shots | big9 gate result (for the Lead to view) | 48 failing shots (out + diff PNGs), compare.txt, blender_diffs.txt, README with groups. |
| gpu/m2-nit-902-gate-runner-fresh-import | **M2-NIT-902** (runner fix) | sync.sh never keeps .godot (a stale import failed test_post_import); runbook: 10 GB WSL cap, 2 shards, the shots-branch practice. |
| gpu/gate-big8-shots | big8's 29 failing shots (out + diff PNGs, clean cache) | for the Lead to view; README groups them. |
| gpu/m2-nit-901-audio-check-windows | **M2-NIT-901** (accepted, in big8) | data_check keys sfx_*.json by POSIX path (399 false errors on Windows). |
| gpu/m2-rnd-910-quit-mid-warmup | **M2-RND-910** (accepted, in big8) | Quit during a first-run warm-up hung (predelete waited on RND-18's worker-thread load()). Loads now via ResourceLoader threaded requests; predelete never waits on a load. boot_title first-run capture exits in 5 s (was killed); new test. |
| gpu/m2-gate-runner | **Gate runner** (for the Lead) | WSL2 `hymn` + tools/dev/pc_gate/ + tools/dev/gate_runner.md. Parity proved (196/196 on d6a0886d). Filed M2-CHR-11 (Blender AVX2 DIFFs) and M2-ARC-12 (stall tests' clock margin). |
| gpu/m2-rnd-16-release-exit-leak | **M2-RND-16 in review** (reviewer Architect) | The exit leak (130 in use): a Godot 4.6.3 GDScript compiler bug: a function naming HalunaDresser then HalunaZoneDresser (its subclass) pins the class graph. Not release-only. Fix: haluna_zone.gd names the subclass first; 0 in use (editor and release). New tool: slice_sweep --leak-probe. |
| gpu/m3-rnd-05-reefball-night | **M3-RND-05 in review** (reviewer Art) | The night match: the ball's water column carries the rule-3 sea-glow (on/off 1.56-5.0x, stone <= 2.36x the sea), lamp-keyed players; arena lamps need light_volumetric_fog_energy 0 (they lit the god-ray fog green). +0.01-0.08 ms. Stacked on RND-04. Two new pending shots. |
| gpu/m2-nit-05-blender-test-windows | **M2-NIT-05** (accepted) | test_blender_builds on Windows: the expectation uses the scratch Path's own spelling. With NIT-04 merged, all tools tests are green on Windows (498, 6 skipped). |
| gpu/m3-rnd-04-reefball-caustics | **M3-RND-04 in review** (reviewer Character) | Caustics on the Reefball players: the ocean's caustic web in the sphere's multiply pass, projected along the sun, sun-facing faces only; every tier (<= 0.013 ms at 1440p). Stacked on M3-RND-01. The four reefball shots change: re-approve on lavapipe with RND-01's. |
| gpu/m2-rnd-19-cold-sweep-budget | **M2-RND-19** (accepted) | ADR 0037's gate: `slice_sweep --budget` (1.7 s behind the first-run cue, 1 s other hidden, 50 ms visible; exit 1 if over) + `tools/gpu_bench/run_cold_launch.sh`. Cold High 1379 ms / Low 1405 ms, all ok. Stacked on RND-18, with the integration branch and NIT-04 merged. |
| gpu/m2-rnd-18-cold-boot-frame | **M2-RND-18** (accepted; ADR 0037) | Cold boot's worst hidden frame: High 2970 -> 1395-1434 ms, Low 1580 -> 1412-1678 (harvest spread on a worker thread, an empty frame after bring-up, 1 material per first-run batch). Irreducible: one material's synchronous pipeline set (palm frond, 1.36-1.68 s) -> ADR amendment ~1.7 s. Stacked on RND-17 (with RND-14 merged). |
| gpu/m2-rnd-17-zone-stage-gi | **M2-RND-17 in review** | The shrine's cold first frame is its runtime-built hall: first_run_live_scenes + M2-ENV-12 (m2-slice builds it off the tree): 1918 -> 188 ms. |
| gpu/m2-rnd-14-advanced-group | **M2-RND-14** (accepted) | Boot turns Forward+'s advanced shader group on (a frame of TAA) for TAA-off players: the 4.6.3 deadlock's trigger off the shrine. |
| gpu/m2-nit-04-capture-test-windows | fix (accepted) | test_capture_sh on Windows: Git Bash + POSIX paths. |
| gpu/m2-rnd-15-cold-first-entry | **M2-RND-15 in review** (reviewer Environment) | Cold first launch: the first run also instances Haluna live (worker thread) and stages its runtime-built surfaces; Haluna's cold first entry 637/2312 ms Low, 407/2045 High (was 1771/4426, 1607/3767). The '825 ms visible' frame was the sweep timing out under the card (fixed: LAUNCH_TIMEOUT_S, SLICE_TIMEOUT); new --pipeline-trace. |
| gpu/m3-rnd-01-reefball | **M3-RND-01 in review** (reviewer Art/character) | Reefball water sphere prototype (WaterSphereRig): refraction + Fresnel outside, Snell window/TIR inside, god rays, a clean crossing; +0.1-0.5 ms. Key frames docs/kb/qa/gpu/reefball/. |
| gpu/arc-08-first-launch | report (Lead request) | ARC-08 re-measure, every cache cleared (the driver's too): the wait ends done in all runs, the cue shows; cold-driver frames still over ADR 0029 (Low 825 ms visible just after the lift, Haluna 1.6-1.7 s first entry). |
| gpu/shrine-gi-hang-probe | report (Lead request) | Shrine load + GI bake: no hang in 25 GPU loads; the bake's 4.2-5.6 s hidden frame breaks ADR 0029 (routed to m2-slice). |
| gpu/m2-rnd-13-set3-error | **M2-RND-13** (merged into lead/gpu6) | The set-3 Vulkan error: old targets freed before the Texture2DRDs got the new RIDs; retired now. 0 error lines. |
| gpu/m2-rnd-12-ultra-storm | **M2-RND-12** (merged into lead/gpu6) | Ultra storm <= 4 ms at 1440p: compute body 0.5 / 56 steps (3.47/2.55/3.69 ms). |
| gpu/m3-rnd-tasks | tasks | Filed M3-RND-01/02/03 and M2-QA-01 (capture_preset ignores a shot's setup). |
| gpu/godot-472-port | **long-lived, not to merge until the Lead calls it** | 4.7.2 port prep: fetch_godot.py --official (SHA-512), the import churn (45 .import), templates installed and verified, suite 1451/0 on 4.7.2, baked 4.7.2 level with 4.6.3; workaround re-checks in docs/kb/qa/gpu/2026-10-24-godot-472-port-prep.md. Worktree C:/Users/Aaron/hymn_472port. |
| gpu/m1-rnd-26-bounce-gate | **M1-RND-26 in review** (reviewer Character) | Option (a): the mouth bounce pass draws only while an omni/spot light reaches the mouth (CharacterShaderTiers.refresh_bounce_passes). High, directional: the mouth matches no-pass within capture noise (was up to 74/255); a shadowed spot keeps the bounce. |
| gpu/m2-rnd-11-sweep-r | **M2-RND-11 in review** (reviewer Environment) | First-run tests; warm compute pipelines freed at exit (0 leaks); named literals; Ultra reflects the real body via a full-res compute body (also ~1 ms faster; Ultra's storm is 15-18 ms at 1440p: budget call); M2-ENV-05 lead: Haluna + character entries resident -> second-launch entry 1.6/1.9 s. |
| gpu/m2-rnd-10-storm-art | **M2-RND-10 in review** (reviewer Art/character) | Storm Art fixes: full-res rent cores and lips in the composite (12-23:1 slits on High), sheet curtains, softer rain (landfall 11.6%), landfall near-night slate-teal (OkL 0.211; sea C 0.018 just short), Letting gold at wound 0.9, rise_ratio 2.0, per-chapter flash/bolts, no rain underwater. +0.07-0.12 ms High. Lavapipe drift: all undertow_* shots. |
| gpu/m2-rnd-09-underwater-art | **M2-RND-09 in review** (reviewer Art/character) | Underwater Art fixes: lagoon swatches + night_sea look, TIR off sea_glow, night sea-glow in the column (on/off 2.2×), the lantern halo moved into the post (warm: h 72-75°, 0 green px), glimmer compensation (and the field's own absorption off underwater), the waterline camera and an antialiased meniscus. Lavapipe drift: underwater_below/window/waterline. |
| gpu/rnd-29-headless-fix | **gate fix, ready** (Lead-urgent) | CI boot smoke (headless, fresh user://, --quit-after 60) was 225 resources still in use: headless ran the first-launch warm-up every boot, and residents sat in a static. Now headless skips it and residents live on a ShaderPrewarmResident root node. Smoke: 0 ERROR lines × 5, also merged into gpu/hero-materials-resident (conflicts resolved there, 1452/0). |
| gpu/hero-materials-resident | **ready to merge after RND-29** (Lead-approved) | Asha's 11 materials resident from boot, per preset via `resident_presets` (ShaderPrewarm.entry_resident). Haluna's entry High 2.9-3.0 → 2.1-2.3 s; Low 3.5-3.6 → 2.3-2.8 s (so resident on Low too); ~245 MB texture memory (Low 285 vs 39). Now merged with the gate fix (conflicts resolved). |
| gpu/godot-472-port-check | **done** (owner's direction: ship on the latest Godot) | 4.7.2 port check in a throwaway worktree (`C:/Users/Aaron/hymn_472`, not committed): imports, 1449/0 tests, GPU costs within 2 %. Haluna root-caused: no 4.7 regression (cache states differed); holding Asha's materials resident (`gpu/hero-materials-resident`) cuts Haluna's entry to 2.1-2.3 s on both engines. First run on a new engine is fully cold; re-measure with 4.7.2 templates + baker. Report: `docs/kb/qa/gpu/2026-10-24-godot-472-port-check.md` |
| gpu/m1-rnd-29-first-launch | **M1-RND-29 in review** (reviewer Environment) | First-run pipeline warm-up behind the boot card (marker `user://pipeline_warm.cfg`); fresh-install zone entries 0.46-1.33 s (Haluna was 2.5-4.3 s), hidden ≤ 221 ms, visible ≤ 23 ms. One frame left: Low's first 3D frame 1.35 s on the first launch only. ShaderPrewarm measures wall time (Godot caps delta at ~150 ms; BootCard filed M2-ARC-05). |
| gpu/arc-03-remeasure | **done** (Lead request) | M2-ARC-03 re-measured on hardware, recorded in its Review log: title visible worst 0.6-0.8 ms on Low/High/Ultra (was 168-265); a real perf-build launch reports reveal true, max_visible_frame_ms 7.95 cold / 2.11 warm, reveal wait 1.7-1.9 s (worst frame 148-150 ms). The slice sweep gains a `launch` segment and prints the router's last_swap_stats. |
| gpu/m2-rnd-08-low-storm-cost | **M2-RND-08 in review** (reviewer Environment) | Low's storm shells read the baked lattice (shared `undertow_lattice.gdshaderinc`) and skip wounds off the wall band: Low storm cost 1.32-1.65 → 0.31-0.66 ms at 1440p, under High's. `undertow_horizon_low` drifts 0.025 (re-approve). |
| gpu/m2-rnd-07-flood-hitch | **M2-RND-07 in review** (reviewer Combat) | The Drownbell Flood's mid-battle hitch was the first turbulent particle emitter (31-32 ms of main-thread build) of polyp_rise. `BattleVfx.prebuild()` at attach builds every effect layer's emitter under the fade. Flood 1.7-1.8 ms on Low/High/Ultra, warm and fresh install (was 39-44, 79 cold); battle entries' hidden worst frame 0.35-0.6 s. Report: `docs/kb/qa/gpu/2026-10-24-rnd-07-flood-hitch.md` |
| gpu/m1-rnd-28-shader-baker | **M1-RND-28 in review** (reviewer Environment) | Official 4.6.3 export templates installed (SHA-512 verified). shader_baker on for Windows Desktop; a `Windows Perf` preset runs the slice sweep as its main scene. Release + baker, fresh install: Haluna 8.0 s (no baker 11.4), hidden worst 2.0 s, title 1.2 s, Flood 79 ms (no baker 1024): filed M1-RND-29. Second launch passes (Haluna 2.55 s). **Blocker filed M2-ARC-04:** release exports exclude game/levels/_tests, which shipped code depends on (SceneRouter fails). Report: `docs/kb/qa/gpu/2026-10-24-rnd-28-shader-baker.md` |
| gpu/slice-perf-sweep | **done** (queue item 5) | First-playable thread end to end at Low/High/Ultra 1440p (`tools/gpu_bench/slice_sweep.tscn`): title, Haluna x3 spawns, tideline battle, Shell Shrine, Drownbell battle and its Flood. GPU well inside budget (worst: Haluna beach 3.1 ms High, 5.7 Ultra). Over or at risk, filed: Haluna entry 3.1-3.5 s > 3 s (M2-ENV-05); the title visible during the boot warm-up, 168-265 ms (M2-ARC-03); the Drownbell Flood 39-61 ms mid-battle (M2-RND-07). 24 rows in perf_baseline.csv. Report: `docs/kb/qa/gpu/2026-10-24-slice-perf-sweep.md` |
| gpu/adr-0029-prewarm-followups | **M1-RND-27 in review** (reviewer Environment) | ADR 0029 follow-ups. Boot warm-up worst frame **0.86-0.89 s cold / 0.47-0.66 s warm** (was 1.06-1.20 / ~0.75): a plain-first stage bring-up, residents loaded in their batch, and the Undertow body's compute twin warmed instead of the never-drawn spatial shader on Medium/High. The SceneState harvest and primitive-mesh materials read unbuilt take Haluna's start() from 664 to 353 ms cold. materials_per_frame 2 is kept (measured). The export baker needs export templates (not installed). Report: `docs/kb/qa/gpu/2026-10-24-rnd-27-prewarm.md` |
| gpu/m2-rnd-05-undertow-events | **M2-RND-05 in review** (reviewer Environment; Art's sign-off is M2-ART-03) | The Undertow as an event: torn rents (dark lip, halo), curtains of held light off the wounds, cloud-to-sea bolts on the camera's half plus a capped 2.0x/2-frame exposure flash, camera rain, the zone shadow, the storm in the sea's reflection (the half-res body's own pixels), six chapter presets and `unbinding` (the Ch21 Letting). Storm cost at High 1440p **0.59-0.84 ms** (was 0.55-0.76). All 4 `undertow_*` baselines drift by design; 3 pending shots in `docs/kb/qa/gpu/2026-10-24-rnd-05-pending-shots.json`. Report: `docs/kb/qa/gpu/2026-10-24-rnd-05-undertow-events.md` |
| gpu/m1-env-09-lod-check | **done** (queue item 2; the review entry is in the ENV-09 task, whose status stays review for the shelter-against-Haluna criterion) | M1-ENV-09 GPU check of the `visibility_parent` LOD chain. `lod_sweep_probe` gives LOD_SWEEP PASS on Vulkan. The real palm, stepped and with a moving camera at 5 m/s, in and out: no pop, no hole, an opaque trunk; one LOD outside 118.5–122 m and LOD1 plus the fading LOD2 inside. The band costs +0.07/0.09/0.11 ms at Low/High/Ultra 1440p for 40 palms (about 2 µs each). `lod_pop.tscn` gains `--direction`, `--solo`, draw counts, `--png-every`, `--hide-lod` and `--bench --clones`. Report: `docs/kb/qa/gpu/2026-10-24-env-09-lod-check.md` |
| gpu/m1-rnd-24-gpu-check | **done** (queue item 1 of the 2026-10-24 top-up; the RND-24 task stays in review with its owner) | M1-RND-24 criterion 2 on the GPU. A shadowed spot key: the grief interior median goes from fallback 0.0145 to pass 0.0194 at High (from 0.0144 to 0.0185 at Low); the share below 0.01 goes 0.16 → 0.10 at High and 0.19 → 0.07 at Low; this matches the key-shadow-off control. Closed mouths: RMSE ≤ 0.0001. QA-08 fault A doesn't change (it's RND-25's). Cost: none measurable (< 0.005 ms at 1440p). **Finding: M1-RND-26**, where under FSR2 (High) the pass softens the mouth's edges even with no positional light; lavapipe isn't affected. New tool `tools/gpu_bench/mouth_bounce_probe.tscn`. Report: `docs/kb/qa/gpu/2026-10-24-rnd-24-bounce-gpu.md` |
| gpu/m2-rnd-04-drownbell-vfx | **M2-RND-04 in review** (reviewer Environment; contains gpu/m2-rnd-03-battle-vfx, so merge that first) | The Drownbell's set piece: `BattleBossVfx`, attached through BattleVfx (no controller edit), playing every battle_ctb.md hook point. That's the toll telegraph and shockwave, rim sparks and the break, polyp lights and mend streams, Ilun's Floodnet, and the bell's seaward release. **The flood rig** is a WaterSurface (the lagoon_low_sun look) that rises −0.7 → +0.6 m over 8 s; it's the battle's one `hymn_water_level` publisher, and the key light and sea-glow follow it. **High 1440p, worst frame 2.0 ms** (Ultra 3.4). Reduced motion is covered. Also fixes RND-03's retry leaving the old view. **Finding:** nothing shipped drives the weather clock `hymn_wind_time` (only test rigs do); the rig runs it in the boss battle. One pending shot: `docs/kb/qa/gpu/2026-10-24-rnd-04-pending-shots.json`. Docs: battle_vfx.md "The Drownbell" |
| gpu/m2-rnd-02-underwater | **M2-RND-02 in review** (reviewer Environment) | Underwater look: `UnderwaterRig` (`game/world/water/underwater/`) gives a per-pixel absorption and scatter post with a wave-following waterline (a meniscus, no pop at the crossing); the underside (the Snell window with the refracted sun, and TIR); volumetric god rays on High and Ultra; marine snow; Rhen's oil-lamp lantern. The light level follows the scene's sun, so night dives are dark. Tiers: `tiers.underwater` in graphics_presets.json. **The rig costs +0.32 ms at High 1440p; the whole frame is 1.1–1.5 ms.** On Low: +0.14 ms. gpu_bench and capture_preset now apply every system tier (`GraphicsRuntime.apply_system_tiers`), so their Low, Medium and Ultra captures of water scenes can change. Three new pending shots: `docs/kb/qa/gpu/2026-10-24-rnd-02-pending-shots.json`. Art sign-off is **M2-ART-02**. Docs: `docs/kb/tech/underwater.md` |
| gpu/fp-10-keylight-check | pushed (from origin/claude/m2-slice 0408806; Lead request) | M2-FP-10 GPU check. No artefacts; cost ≤ 0.03 ms; Haluna sun at bias 1.0, no face regression. H05's 74° sun leaves the face in brow and nose shadow, so set `key_pitch_deg` 30 on H05 and H06. **Layer 20 conflict** between the key light and the Undertow half-res body. New tool `tools/gpu_bench/keylight_probe.tscn`. Report: `docs/kb/qa/gpu/2026-10-24-fp-10-keylight.md` |
| gpu/m2-rnd-03-battle-vfx | **M2-RND-03 in review** (reviewer Environment) | Battle VFX library: `BattleVfx`, listen-only (one controller line). The data (`effects.json`) holds 14 effects: element hits, Lamp Dive, Shallows Verse, Read, heal, status, KO into released glimmer, and the opening flashes. Flashes are photosensitivity-capped and below the HUD; reduced motion is supported. The worst 3v3 burst costs +0.04 ms at High 1440p. Battle shots move ≤ 0.0022 on the GPU (under the gate). Docs: `docs/kb/tech/battle_vfx.md` |
| gpu/m1-rnd-22-prewarm | **M1-RND-22 in review** (reviewer Environment) | Prewarm hitch floor. Battle transitions now 34–46 ms on every preset (before 308–371). The floor was a test material in every transition, other presets' tier variants, and variant compiles on first draw. Fixes: the `preset_tier` filter, a boot warm-up of resident shaders, the FSR2 stage size (no more FFX error spam), and the router frame-0 timing. Zone and storm entries are 142–312 ms behind the fade: ADR 0029 (proposed). Threaded loads and harvest were tried and crash Godot, so they were reverted. Report: `docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md` |
| gpu/m2-rnd-01b-undertow-compute | **M2-RND-01 in review** (contains gpu/m2-rnd-01-undertow; merge that first) | Compute body (ADR 0028): exact occlusion; High body_scale 0.35 (motion-checked). The storm's own cost is 0.58–0.80 ms at High 1440p. All 5 Undertow shots drift. Follow-up task M2-RND-05. Report: m2-rnd-01-start.md, the last two sections |
| gpu/m2-rnd-01-undertow | **WIP, not merged** (task `doing`) | M2-RND-01. Earlier: the wall foot, the sea's storm response, joined flanks, the half-res body and 3-octave multiple scattering. This session: noise-warped striations, fringe billows with sun-ward shading, softer sea streaks, and the wound-stipple fix (skin step refinement). High 1440p: Day 2.56, Eye 3.11 ms. All 5 Undertow shots drift. Integration branch merged in (a504072). Report: `docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md` |
| gpu/qa-08-asha-recheck | task `review` (reviewer: character) | M1-QA-08: Asha GPU recheck at 2× High and Ultra (96a6585 / 9a133ee). Neutral passes; smile passes on shading but reads as a smirk at 1×; grief still fails on two Character mouth faults (black rim, peg teeth). CHR-12: crown, lid band (R:B 3.7 against 2.0–2.5) and smile eyes fail; lip bow and skin pass. ADR 0024 check 2 confirmed. Report: `docs/kb/qa/gpu/2026-10-24-qa-08-asha.md` |
| gpu/qa-05d-asha-recheck | superseded by qa-08 | The first cut of the same recheck, before the task file existed. Don't merge. |
| gpu/rnd-21-mouth-fill | merged (96a6585) | M1-RND-21: the `mouth` shader family's cavity bounce. Report: `docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md` |
| gpu/rnd-18-20-followups | in review; Lead's lavapipe check ci35 | RND-18 S1: deep lift gated by SSS (no drift). RND-20 S1: measured, Haluna stays at 1.0 (bias is in texels); rule in character_shading.md. Filed M1-ENV-08. Report: `docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md` |
| gpu/qa-07-windows-interpreter-test | new, not merged | Files M1-QA-07 (the Windows-only test failure), Lead request |
| gpu/env-03-vegetation-v2, gpu/rnd-17-dusk-motes-v2 | merged + lavapipe-approved (c940d77) | ENV-03 v2 (final-cut-only LOD fade, Shelter enum/mask, ShaderGlobals); RND-17 v2 |
| gpu/chr-04-materials, gpu/qa-05b-asha-recheck | pushed; not ancestors of the integration branch (the Lead took their content earlier, per the queue log; check before deleting) | CHR-04 material half; QA-05b note |
| gpu/env-03-vegetation, gpu/rnd-17-dusk-motes, gpu/perf-sweep, gpu/qa-05-asha-gpu, gpu/qa-05c-asha-final, gpu/results-2026-10-23, gpu/rnd-07-presets, gpu/rnd-08-water-glimmer, gpu/rnd-09-undertow-shading, gpu/rnd-10-undertow-perf, gpu/rnd-11-undertow-params, gpu/rnd-12-sky, gpu/rnd-15-prewarm, gpu/rnd-18-sss-crest, gpu/rnd-20-smile-terminator | merged | Earlier items; reports under `docs/kb/qa/gpu/` |
| gpu/grief-mouth-fill | **local only, abandoned** | An empty branch plus `stash@{0}` (a stage FillLight); superseded by the RND-21 shader family. Safe to delete. |

## Unfinished queue, in order (exact next step first)

**Queue from the new Lead (session_018aiGwG..., 2026-10-24/27):**
1. GATE lead/gate-big9: **done**, pushed to `gpu/gate-big9-shots`.
2. GATE lead/gate-big10 @ 181708a7: **done**, pushed to `gpu/gate-big10-shots`. Any later
   `lead/gate-*` pre-empts items 3-6 at the next safe point (never during a benchmark).
**Standing (2026-10-27): the PC does ALL rendering** (TRACK-RULES "RENDERING GOES TO THE PC"): poll the
`origin/claude/*` live logs for `RENDER-REQUEST @ <sha>` lines after each item and every ~30 min; answer with
`RENDERED @ <sha>: gpu/render-<track>-<sha7>; n pass, m drift` below. Priority: gates > fast-track renders > other
renders (oldest first) > the hardware queue.
3. M1-QA-09 on hardware (on integration 3b7cbf5e, all three heroes; NEXT): Asha braid/clothing/staff clipping and limbs, then the other heroes (screenshots on a gpu/ branch).
4. Slice `--budget` re-sweep (ADR 0029/0037) on the integration head after big9 merges.
5. Act I playthrough on hardware (F8 chapter select: Ch1, Ch4-Ch9); file findings as M?-*-9xx tasks.
6. M2-CHR-11: when characters pushes the AVX2 SIMD snaps, `verify_blender_builds.py --all` on it.
Later: M3-RND-02 (needs the owner's OK to cap GPU clocks); RND-16; `gpu/godot-472-port` stays parked.

**Earlier queue (kept for the record):**

**Queue (the Lead's top-up of 2026-10-24).** Base each item on the integration branch once the Lead's batch merge
lands; until then, base on the current head (a514c06, then 54425e2).
- **1. M1-RND-24 criterion 2 (GPU): done** on `gpu/m1-rnd-24-gpu-check`.
- **2. M1-ENV-09 GPU check: done** on `gpu/m1-env-09-lod-check`: it passes.
- **3. M2-RND-05: in review** on `gpu/m2-rnd-05-undertow-events` (Art: M2-ART-03).
- **4. ADR 0029 follow-ups: in review** as M1-RND-27 on `gpu/adr-0029-prewarm-followups` (export baker waiting on export templates).
- **5. Slice perf sweep: done** on `gpu/slice-perf-sweep`; filed M2-ENV-05, M2-ARC-03 and M2-RND-07.
- **5b. M1-RND-28: in review** on `gpu/m1-rnd-28-shader-baker`; filed M2-ARC-04 (a release-build blocker) and M1-RND-29.
- **Lead's queue after it (2026-10-24):** M2-RND-07 (in review on `gpu/m2-rnd-07-flood-hitch`), then the Low-preset storm cost (M2-RND-08, in review), then the M2-ARC-03 re-measure (done), then M1-RND-29 (in review); the owner's direction (2026-10-24): the game ships on the latest Godot (4.7.2 at C:/Users/Aaron/Tools/godot-4.7.2); a port check in a worktree is next (file and fix), then M1-RND-29 (first-launch pipelines), then M1-QA-09 when the Lead says M1-CHR-14 has landed (check the braid attachment, clipping and limb seams across the clips).
- **6. M1-QA-09:** only after M1-CHR-12 merges (the Lead will say).

Merge notes from the previous queue:
- RND-03 goes before RND-04.
- The RND-02 and RND-04 branches each add an ownership.md row after the same line (a trivial conflict).
- RND-22 and RND-04 both touch prewarm_materials.json.

**Previous queue (all in review):**

1. **M2-RND-01: in review** (reviewer Environment), on `gpu/m2-rnd-01b-undertow-compute`; merge
   `gpu/m2-rnd-01-undertow` first.
   - High `body_scale` is 0.35 (motion-checked); Medium stays at 0.5.
   - The storm's own cost is 0.58–0.80 ms at High 1440p, ~2–2.4 ms projected on an RTX 3060.
   - All 5 Undertow shots drift: re-approve them on lavapipe.
   - The storm-event criteria moved to **M2-RND-05** (todo).
2. **M1-RND-22: in review** (`gpu/m1-rnd-22-prewarm`). Battle transitions are in budget. Follow-ups are in ADR 0029: the
   export shader baker (needs export templates on the PC), a SceneState harvest for big zones, and slicing the
   boot warm-up.
3. **M2-RND-03: in review** (`gpu/m2-rnd-03-battle-vfx`). Next passes are in battle_vfx.md: an art pass for the pale effects, and contact-frame timing once body clips exist.
4. **M2-RND-02: in review** (`gpu/m2-rnd-02-underwater`). The Lead adds the 3 pending shots on lavapipe. Open:
   - the glimmer-motes boost underwater (Art's call, in M2-ART-02);
   - caustics on characters;
   - a splash at the crossing.
5. **M2-RND-04: in review** (`gpu/m2-rnd-04-drownbell-vfx`). Next passes are in battle_vfx.md: the arena's sunset grade, sinking the bell, rim crack decals, and re-measuring battle transitions once M1-RND-22 merges. Originally: Drownbell boss VFX and flood rig. Read the First Playable boss data first (session
   session_01ELR13ohWMPrprcpcgLa7UR, branch `claude/first-playable`).
- **Standing:** GPU checks of shots before the Lead re-approves lavapipe baselines.
- **Open findings to route** (filed or noted, not this queue):
  - M1-ENV-08: the vegetation LOD hysteresis hole.
  - The M2 dialogue key light: a few metres of shadow range, bias 4.5 (character_shading.md).
  - Teeth albedo: M1-CHR-11.
  - M1-RND-26: under FSR2 the mouth bounce pass softens the mouth (filed 2026-10-24).

## Local-only state (not in git)

- **This session's scratch:** captures, CSVs and the helper scripts `bench.sh`, `cap.sh`, `cap5.sh`, `capd.sh` and `jset.py`.
  It's in `C:/Users/Aaron/AppData/Local/Temp/claude/C--Users-Aaron/d3383506-5a83-49e1-8dcf-15422406b087/scratchpad/m2rnd01` and `.../rnd02`. Temporary.

None of it is needed: everything quoted in the reports can be reproduced from the commands in them.
- **`C:\Users\Aaron\Hymn_Playtest`:** a separate clone for the human's playtest, with untracked `PLAY.bat` and
  `EDITOR.bat`. Delete it after the playtest.
- **`C:\Users\Aaron\hymn_shots_gpu`:** 87 GPU screenshots (base body, Asha and others) from early QA passes.
  Scratch.
- **Scratch renders and CSVs:** `C:\Users\Aaron\chr04`, `rnd12`, `m2rnd01` (including `cur/undertow_day_ch08.png`, the
  2× capture that shows the two defects above), `rnd15`, `rnd17`, `rnd18`, `qa05b` and `env03`, plus the old
  session's scratchpad (temporary).
- **`stash@{0}`** and the local branch `gpu/grief-mouth-fill` in `C:\Users\Aaron\hymn_gpu`: abandoned (see above).

## Queue (Lead, 2026-10-24 deep queue)
1. M2-RND-09 underwater Art fixes: **review** (`gpu/m2-rnd-09-underwater-art`).
2. M2-RND-10 storm Art fixes: **review** (`gpu/m2-rnd-10-storm-art`).
2a. M2-RND-11 (review sweep R follow-ups): **review** (`gpu/m2-rnd-11-sweep-r`).
3. M1-RND-26: **review** (`gpu/m1-rnd-26-bounce-gate`).
4. Next: M3-RND-02 (min-spec proxy, waiting on the owner's OK for a GPU clock/power limit); M1-QA-09 and the slice re-sweep when the characters merge; M3-RND-03 when the zones are named.
3. M1-RND-26 the mouth-bounce pass's FSR2 softening at High.
4. M1-QA-09 Asha on hardware: starts on the Lead's "characters merged".
5. The 4.7.2 port prep on the long-lived `gpu/godot-472-port` (not merged until the Lead calls it).
6. The slice perf re-sweep, once the characters and creatures land.
7. M3 R&D: the Reefball arena look, a minimum-spec proxy, and Act I look-dev support.

## Gate runner results (WSL2 distro `hymn`; tools/dev/gate_runner.md)
- **GATE d6a0886d@d6a0886d: FAIL (host-only), wall 16.3 min.** Lane A: data, unittests, audio, taskboard, lint,
  format and manifest ok. Godot **1940 run, 2 failed**: `test_frame_clock::test_a_real_stall_reads_past_the_cap` and
  `test_boot_card::test_a_real_stall_under_the_card_reads_at_least_its_length`, a WSL2 clock skew under load. They pass
  3/3 idle; **M2-ARC-12**. Coverage and smoke didn't run (the gate stops at the first failure). Lane B: **196/196 shots
  pass** (parity with the container). Blender `--all`: **41 jobs, 31 identical, 10 DIFF** (base_body, rhen, toma and
  seven villagers: an AVX2 host without M1-CHR-14's snaps; **M2-CHR-11**).
- **GATE lead/gate-big7@ab048d51: FAIL, wall 18.2 min** (cross-check). Blender, 39 changed jobs: 9 DIFF, the same
  M2-CHR-11 set. Shots: 196 compared, 2 failed: `save_shrine_field` 0.07021 and `settings_accessibility` 0.04817, the two
  the Lead re-approved after viewing in d0e0c5a3 and a7350535. So the container and the runner agree.
- Parity proof on 81651b7e: 75/75 shots; llvmpipe "LLVM 22.1.8, 256 bits"; drifts identical to the container's
  (water_horizon 0.00507, water_night 0.00306, haluna_h01 0.00189); output independent of LP_NUM_THREADS.
- **GATE lead/gate-cmb02@7c424c3b: FAIL (shots only), wall 15.8 min.** Lane A green: Godot 1948/0 (M2-ARC-12's margin
  holds under WSL load), coverage OK, smoke OK, Blender 0 changed jobs. Shots: 196 compared, 24 failed, all the
  timeline order. In 22 of them 100% of the changed pixels lie in the timeline column. battle_hud_preview also has the
  "acts again in 4 -> 5 turns" hint; battle_swell_ring also has the Lamp Dive ring state ("Perfect"), which the Lead
  is viewing. The 061b0361 run was stopped at the Lead's request.
- **GATE lead/gate-big8@aa55b77e: FAIL (expected-kind drifts plus the known Blender set), wall 27.4 min.** Lane A
  (fresh import): Godot **2324 run, 0 failed**; coverage OK; smoke OK; data, lint and tools tests OK. Blender, 44
  changed jobs: 35 identical, **9 DIFF** (exactly the M2-CHR-11 set: rhen, toma and seven villagers). Lane B: **238
  compared, 29 failed**: 16 battle_arena_*, 6 battle_boss_intro_*, drownbell_flood, creature_portraits, and 5 not on
  the Lead's list (field_area_title, field_interact_prompt, field_objective_line, field_tip_card, dialogue_continue:
  UI unchanged, the Haluna stone and sand behind it differ). settings_hub, settings_accessibility and
  shrine_s01–s05 pass. PNGs: gpu/gate-big8-shots (docs/kb/qa/gate-runs/big8/).
- **Runner bug, fixed (M2-NIT-902):** the first big8 attempt kept a stale .godot. It failed 3 test_post_import tests
  (stale LOD ranges; 21/21 fresh) and moved two tideline arena shots; the rerun's PNGs are the clean ones. Claude Code
  also reaped one attempt for low system memory; with the owner's OK WSL now caps at 10 GB with 2 shards.

