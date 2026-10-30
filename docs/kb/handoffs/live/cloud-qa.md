# Live log: cloud-qa (lavapipe stand-in for the PC)

This environment owns this file (CLAUDE.md §7a). Branch `qa/cloud-pass6`. The Lead is `session_01Bg3iP7cPGyjbX4CyniBahc`;
the integration branch is `claude/new-session-mj8c3c`.

**What it is:** the PC (pc-gpu) is offline, so this cloud session runs its QA passes headless and on Mesa lavapipe
(llvmpipe, 4 vCPU, no GPU). Lavapipe's lighting, shadows and shading differ from the RX 9070 XT, so every pass-6 note
judges only what lavapipe can show: framing, geometry, cameras, presence and motion. Timings are CPU-side and on a
contended 4-vCPU box: compare them with each other and across merges, not with the PC's numbers.

**Methods and tools (all on this branch):**
- The PC's QA doc and walk tools were brought over from `gpu/act1-qa-5` (tools only): `docs/kb/qa/act1_gpu_qa.md`,
  `tools/gpu_bench/slice_sweep.gd`, `act1_walk*.json`, `capture_preset.gd`.
- Manifest shots: `tools/screenshots/capture.sh --shots <ids> --out <dir>` (one process per shot, lavapipe).
- Row walk: `godot-render ... res://tools/gpu_bench/slice_sweep.tscn -- --walk=res://tools/gpu_bench/act1_walk_pass6.json
  --preset=high --res=960x540 --stills=<dir>`.
- Playtest probes (new, headless):
  - (a) `tools/gpu_bench/return_probe.tscn`: the victory exit → field timing;
  - (b) `tools/gpu_bench/dock_probe.tscn` + `dock_overlaps.py`: Oruvel's boat/dock AABBs and every deck edge walked;
  - (c) `tools/gpu_bench/run_cycle_probe.tscn` (lavapipe): a clip at even phases from the stage's cameras;
  - (d) `tools/gpu_bench/encounter_gap_probe.tscn`: each zone's live FieldEncounters meter, its gaps and the run speed.
- Stills: `docs/kb/qa/cloud/pass6/` (small JPG sheets).

## PASS 6 @ 2026-10-30 (big22, integration @ 19e7f01c)

(in progress; see the sections below)
