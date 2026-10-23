# PC GPU session: standing queue progress (2026-10-23)

Rules: branch each item from origin/claude/new-session-mj8c3c; one heavy GPU job at a time, < ~85 % sustained,
sweeps < ~30 min without a break (updated by the Lead: cumulative CPU/mem/GPU load ≤ ~75 %, parallel non-benchmark work OK, benchmarks alone); never overwrite baselines; keep the PC awake (keep_display_on helper).
Clone: C:\Users\Aaron\hymn_gpu. Godot: C:\Users\Aaron\godot_463\Godot_v4.6.3-stable_win64_console.exe.

| # | Item | Branch | Status | Next step / summary |
|---|---|---|---|---|
| 1 | M1-CHR-04 rendering + material half | gpu/chr-04-materials | done (task stays doing for the cloud agent) | normal bias 2.5 on the Asha stage key/rim; vest lacquer 0.55/0.16/0.55; report 2026-10-23-chr-04-materials.md |
| 1b | M1-RND-12 Haluna sky perf + tiers (Lead added) | gpu/rnd-12-sky | review | clouds 3.7 → 0.4 ms High 1440p, 2.4 → 0.23 ms Low 1080p; sky_detail tiers; R2–R6 + palette_check; report 2026-10-23-rnd-12-sky.md; all 5 haluna_* shots drift |
| 2 | M2-RND-01 Undertow production start | gpu/m2-rnd-01-undertow | done (task stays doing) | wall foot (skirt, water-dark base, scud, spray over body), sea storm response, joined flanks; Day 4.95 ms High 1440p; report 2026-10-23-m2-rnd-01-start.md |
| 2a | CHR-04 follow-up (Lead): vest values into write_materials.py; Blender gate; judge hair warm brown | gpu/chr-04-materials | todo | |
| 2b | M1-RND-15 criterion 4: prewarm worst frame (Low/High/Ultra, ≤50 ms) + Low TAA foliage ghosting, wind on, 30 fps | gpu/rnd-15-prewarm | todo | |
| 2c | M1-RND-17 dusk released motes: gold and rising | gpu/rnd-17-dusk-motes | todo | |
| 2d | M1-RND-18 SSS crest fade for high cameras (deep within ΔE 0.07) | gpu/rnd-18-sss-crest | todo | |
| 3 | M1-ENV-03 vegetation follow-ups | gpu/env-03-vegetation | todo | |
| 4 | Perf regression sweep | gpu/perf-sweep | todo | |

## Log

- Item 1 done: CHR-04 face terminator fixed (bias 2.5), vest material set; all 10 asha_* shots drift (listed in the report). Before every push: validate_data + tools/tests (Lead request).
- Item 1b done: RND-12 (branch gpu/rnd-12-sky), status review. Load while benchmarking: CPU 4–5 %, mem 59–60 %, GPU idle ~1 % (benchmarks alone). Next: item 2, M2-RND-01 Undertow production (branch gpu/m2-rnd-01-undertow).
- Item 2 done: M2-RND-01 start pushed (gpu/m2-rnd-01-undertow). The capture.tscn rig hung on the Undertow shots (my PIDs killed); I used capture_preset for the drift. Next: 2a (CHR-04 follow-up).
