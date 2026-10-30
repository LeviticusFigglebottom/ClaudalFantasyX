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

(in progress: the row walk on lavapipe, row 64 and the suite reds are still running; the playtest checks are done on
19e7f01c and re-run on big23.)

### HUMAN PLAYTEST checks (2026-10-30), headless

**(a) Victory exit → field (owner integration-qa; target ≤ 1 s of black).** `return_probe`: the F8 chapter start, the
location, the fight asked for as the zone asks it, foes held at 1 HP, Return pressed 1 s after the result panel shows (t0).
From t0 it holds the stick and records the router's fade. CPU-side, on a 4-vCPU box with a lavapipe job beside it, so the
absolute numbers run slower than a PC; they are for comparing merges. Milliseconds from t0, 19e7f01c → big23 (8fe3644b):

| Fight → return | black (fade ≥ 0.99) | field scene in | fade clear | hero moves | input live | instantiate | worst hidden frame |
|---|---|---|---|---|---|---|---|
| tideline → Haluna BattleReturn | 5905 → 6130 | 5375 → 5310 | 6601 → 6679 | 5574 → 5520 | 18417 → 18524 (the post-fight lines) | 1815 → 1883 | 3100 → 2944 |
| causeway shore → Encounter | 4046 → 3744 | 4356 → 4067 | 4737 → 4432 | 4380 → 4081 | 4737 → 4438 | 90 → 106 | 3881 → 3569 |
| the Drownbell → Haluna DockNight | 17012 → 14752 (B11, the chapter card, Ch4 inside the 60 s) | 5815 → 4371 | 6791 → 5638 | 6271 → 4829 | never in 60 s (B11 → Ch4) | — | — |
| Oruvel scuttlers → AfterScuttlers | 2797 → 2795 | 3102 → 3085 | 3495 → 3471 | 3115 → 3103 | 3495 → 3471 | 1277 → 1198 | 1444 → 1498 |
| Ch4 ferry (derelict leeches) → Encounter | 5554 → 5497 | 5557 → 5471 | 6223 → 6158 | 5832 → 5767 | 6229 → 6162 | 909 → 817 | 4252 → 4268 |
| Ch6 ridge skippers → Encounter | 11263 → 11354 | 10893 → 10841 | 11815 → 11907 | 11150 → 11114 | 11834 → 11914 | 3815 → 2677 | 6683 → 7769 |

- **Every return is far over 1 s of black, and big23 doesn't change it.** The black is the zone's whole reload under the
  fade: one hidden frame of 1.4–7.8 s (the zone's instance and first draw), then the reveal wait. The battle has freed the
  field, so each return is a cold zone entry.
- **The hero takes the stick 0.3–1.1 s before the fade clears** (moves < fade clear on every return): he can walk blind.
- The tideline's post-fight lines hold input until ~18.5 s (story, by design). The Drownbell goes on through B11 and the
  chapter card into Ch4.
- **Suggestion for integration-qa:** start the return zone's threaded load when the victory shows (the result panel is
  ≥ 1 s of reading), or keep the field zone resident under the battle, so Return only fades.

**(b) Oruvel moorings (owner env-art; the guard integration-qa).** `dock_probe` + `dock_overlaps.py`.
- **Boats vs docks (mesh AABBs overlapping > 5 cm on every axis):** 19e7f01c 13 pairs → **big23 10 pairs** (7fbb9319
  moved the cookboat clear). Still overlapping on big23:
  - scale_hull × the raft deck under it: 1.93 × 2.08 × 7.27 m;
  - keel_hull × two tucked raft decks: 10.45 × 2.17 × 0.43 m each;
  - terrace_hull × a tucked raft deck: 0.25 × 2.14 × 10.50 m;
  - hull_outrigger × a small tucked deck: 0.59 × 1.14 × 0.34 m; the second outrigger × two plank bridges: 0.61 and
    2.76 m wide;
  - dive_raft × two plank bridges and the gull post (likely intended: the bridges land on the raft, the post stands on it).
  AABBs only flag candidates: view them in the GPU stills before acting.
- **Dock edges:** every walkable deck box's edges, every 2 m, the hero driven straight off with the field controller.
  - **19e7f01c: 215 of 260 pushes walk off into the water**, onto the solid Sea block at y = −1.0, and the hero **can't
    climb back** (216 of 216 tries stuck 1 m below the deck): a soft-lock at every open edge of every mooring, bridge and
    plank.
  - **big23: 0 of 260** (28b005ad's edge walls). Fixed.

**(c) Rhen's default run (owner characters).** `run_cycle_probe`, rhen_stage at 12 even phases of the `run` clip
(0.667 s), side and front, on lavapipe: `docs/kb/qa/cloud/pass6/playtest_c_rhen_run_side_front.jpg`.
- Side: a full alternating stride, the feet plant, the torso upright: grounded.
- **Front: the hands swing up to shoulder and face height with open, splayed fingers** (left hand at t0–t1, right at
  t5–t8). It reads as a wave, not a run's arm swing. The forearms stay folded up through the whole cycle.

**(d) Breather between field encounters (owner act1-chapters; target 30–45 s).** `encounter_gap_probe` reads each zone's
live meter and draws its first 8 gaps with the zone's own `_draw()`, plus the grace, at the 3.6 m/s run (the measured push
reaches 3.59–3.66 m/s on open ground).

| Zone | 19e7f01c gaps (s) | big23 gaps (s) |
|---|---|---|
| Ch1 Underway | 6.5–11.6 | 31.0–48.7 |
| Ch3 causeway (after the harrier) | 25.4–29.6 | 39.0–52.0 |
| Ch4 derelict | 8.2–13.7 | 32.3–50.1 |
| Ch5 Ashcrown stair | 11.7–17.1 | 35.4–52.0 |
| Ch6 Brine Shoals | 10.0–13.2 | 38.4–48.3 |
| Ch8 Coilspire path | 9.5–14.5 | 33.6–50.9 |

- **big23 fixes it** (a1e49de9, b7d03f81: a 95–145 m gap, grace 15 m and 12 s). About a third of the draws land 46–52 s,
  a little over the 45 s target: fine for a breather; say if 45 s is a hard cap.
- Oruvel, Haluna, the Shell Shrine, the wake, Pemakar, Tamsule and Corrow have no random encounters, only scripted fights.
- With the longer gaps, the main routes (straight-line spawn-to-spawn: 13–197 m) now hold 0–1 random fights each. The
  Coilspire path (102 m) and the derelict (13 m) hold none.
