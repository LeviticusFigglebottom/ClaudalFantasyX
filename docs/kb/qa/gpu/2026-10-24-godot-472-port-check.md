# Godot 4.7.2 port check (2026-10-24)

**Why.** The owner's direction (2026-10-24): the game ships on the latest Godot, not on 4.6.3 (ADR 0001 pins 4.6.3,
so it needs an ADR to supersede it).

**Setup.**
- Engine: `C:\Users\Aaron\Tools\godot-4.7.2\Godot_v4.7.2-stable_win64_console.exe` (official build ed1daf0bf).
- Project: `gpu/m1-rnd-29-first-launch` (integration cd4e425 plus RND-29) in a throwaway worktree, `C:\Users\Aaron\hymn_472`.
  Nothing from it is committed.
- Machine: RX 9070 XT, 2560×1440, High.

## Results

- **Import works.** The first headless import of a fresh worktree logs font and translation load errors, which is
  what any fresh checkout does on its first pass; the second pass logs 0 errors.
- **The re-import adds keys to 45 `.import` files,** all under `assets/`: `array_mesh/deduplicate_surfaces=true`,
  `mesh_library/use_node_names_as_mesh_names=false` and `gltf/texture_map_mode=0` on the .glb imports. Those are
  4.7's new import options at their defaults. Commit them with the engine switch, and check the meshes don't change
  (`deduplicate_surfaces`).
- **The Godot test suite: 1449 run, 0 failed.**
- **The compute storm body, the water, the battles and the boot card all run.** GPU costs match 4.6.3 within 2 %:
  Haluna beach 3.08 ms, Drownbell 1.15, Shell Shrine 0.62.
- **The process `delta` is still capped at ~140 ms on 4.7.2** (a 500 ms stall reports 138.6 ms). Measure hitches
  with `Time.get_ticks_usec`, never `delta`. ShaderPrewarm now does (M1-RND-29); BootCard is M2-ARC-05.

Slice sweep on the editor binary, High (hidden worst / entry; visible worst; ms):

| Segment | 4.7.2, first run (cold) | 4.7.2, second run | 4.6.3, the same machine |
|---|---|---|---|
| Launch (behind the card) | 3681 / 30107; 1155 | 246 / 2094; 0.7 | 290 / 2165; 0.6 |
| Haluna Beach | 2344 / 5176; 5.1 | 525 / **5414**; 5.1 | 280 / 2503 (cold perf build) – 3115 (editor) |
| Tideline battle | 202 / 608; 25.7 | 177 / 744; 11.9 | 121 / 715; 6.4 |
| Shell Shrine | 707 / 1514; 2.4 | 262 / 630; 1.5 | 164 / 525; 1.1 |
| Drownbell battle | 94 / 466; 8.4 | 507 / 1321; 9.0 | 291 / 911; 5.0 |
| The Flood (no RND-07 prebuild on this base) | 1069 | 63 | 58–62 |

**What moves on 4.7.2:**
1. **Haluna's entry nearly doubles,** from 3.1 to 5.4 s. Its worker-thread instance (HalunaZone's prebuild) takes
   3.36 s, against 1.5–1.75 s on 4.6.3. That's M2-ENV-05's item, and it has to be re-measured on 4.7.
2. **The first run on a new engine is cold for everything,** with a 30 s launch and 1.2–3.7 s frames: the engine's
   shader caches are per version, and this is the editor binary, with no baker.
   - **Re-measure with 4.7.2 export templates and the shader baker** (M1-RND-28/29 on 4.7). That's what players get.
   - The 1155 ms visible frame at launch is the card lifting while the first-run warm-up still compiles; re-check
     it on the baked build.

## Next steps for the port

- The ADR, and the SPEC, CLAUDE.md, fetch_godot.py and CI updates. The 4.7.2 export templates need installing
  (official .tpz, SHA-512 checked).
- Re-check the 4.6.3-era workarounds on 4.7:
  - threaded loads crashing Haluna;
  - the `.glsl` include depth and re-import;
  - FSR2 with no reactive mask (M1-RND-26);
  - the `light()` built-ins (M1-RND-24).
- Every lavapipe baseline gets re-approved after the switch.

## Root cause of the "4.7.2 Haluna regression": there isn't one (2026-10-24, the Lead's follow-up)

The 3.36 s against 1.5–1.75 s comparison mixed cache states. Timing each step of `HalunaZone.prebuild()` on the
real router path (the sweep, temporary instrumentation, reverted) shows the two engines are level when the runs are
alike.

**Launch → title → Haluna**, the router's worker-thread `instantiate_ms`, then the prebuild steps:

| Run | 4.6.3 | 4.7.2 |
|---|---|---|
| 1 | 1631 ms: dress 1274, collision 74, actor materials 4 | 1058 ms: dress 724, collision 60, actor materials 4 |
| 2 | 1885 ms: dress 890, collision 60, actor materials 699 | 1742 ms: dress 694, collision 60, actor materials 703 |

**On the main thread** (headless) the same steps cost the same on both engines: dress 360–377, collision 57–62,
actor materials 554–561, water 18–21 ms.

**What does vary, on both engines:**
1. **The cast's materials** (`HalunaActorPose.assign_materials`) take **~0.7 s** unless they're already loaded.
   They're loaded when the first-run warm-up (M1-RND-29) ran in the same launch, because the boot run holds what it
   loads. That's where the swing between runs came from.
2. **Dressing on the worker thread** takes 0.65–1.3 s, against 0.37 s on the main thread: it contends with the
   main thread's fade, font and prewarm work. A high-priority WorkerThreadPool task helped only within noise
   (633–898 ms), so the router keeps the default.

**The fix, for both engines** (`gpu/hero-materials-resident`, 0200d1cd): Asha's 11 material entries are marked
resident, so the boot warm-up holds them.
- **Haluna's entry** goes from 2.94–3.00 s to **2.09–2.33 s** (4.6.3, High), under ADR 0029's 3 s.
- **The cost:** ~245 MB more texture memory from the title on (289 MB against 44). Those are her textures, which
  load anyway whenever she's on screen, so every scene with her already pays it. The boot card also stays up
  0.5 s longer (2.08 s against 1.57 s).
- **Lead's call:** the VRAM trade.
- **The rest of M2-ENV-05** is the worker-thread dressing itself (0.65–1.3 s) on top of that.
