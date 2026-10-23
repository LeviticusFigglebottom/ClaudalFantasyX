# PC GPU session: standing queue progress (2026-10-23)

Rules: branch each item from origin/claude/new-session-mj8c3c; one heavy GPU job at a time, < ~85 % sustained,
sweeps < ~30 min without a break (updated by the Lead: cumulative CPU/mem/GPU load ≤ ~75 %, parallel non-benchmark work OK, benchmarks alone); never overwrite baselines; keep the PC awake (keep_display_on helper).
Clone: C:\Users\Aaron\hymn_gpu. Godot: C:\Users\Aaron\godot_463\Godot_v4.6.3-stable_win64_console.exe.

| # | Item | Branch | Status | Next step / summary |
|---|---|---|---|---|
| 1 | M1-CHR-04 rendering + material half | gpu/chr-04-materials | done (task stays doing for the cloud agent) | normal bias 2.5 on the Asha stage key/rim; vest lacquer 0.55/0.16/0.55; report 2026-10-23-chr-04-materials.md |
| 1b | M1-RND-12 Haluna sky perf + tiers (Lead added) | gpu/rnd-12-sky | review | clouds 3.7 → 0.4 ms High 1440p, 2.4 → 0.23 ms Low 1080p; sky_detail tiers; R2–R6 + palette_check; report 2026-10-23-rnd-12-sky.md; all 5 haluna_* shots drift |
| 2 | M2-RND-01 Undertow production start | gpu/m2-rnd-01-undertow | todo | |
| 3 | M1-ENV-03 vegetation follow-ups | gpu/env-03-vegetation | todo | |
| 4 | Perf regression sweep | gpu/perf-sweep | todo | |

## Log

- Item 1 done: CHR-04 face terminator fixed (bias 2.5), vest material set; all 10 asha_* shots drift (listed in the report). Before every push: validate_data + tools/tests (Lead request).
- Item 1b done: RND-12 (branch gpu/rnd-12-sky), status review. Load while benchmarking: CPU 4–5 %, mem 59–60 %, GPU idle ~1 % (benchmarks alone). Next: item 2, M2-RND-01 Undertow production (branch gpu/m2-rnd-01-undertow).
