# Live log: Lead (cloud) environment

**Session:** `session_019iimsngAgPLEram1wcbLpE` (new account) · **Branch:** `claude/undertow-lead-handoff-423ixt` (the integration branch) · **Container:** 4 CPUs, Ubuntu, lavapipe. The container has restarted twice; the disk and the worktrees survived both times.

## Current state (2026-10-24, after the RND-05 and fix6 merges)
- **HEAD:** a58fcbd+ (see `git log -1 origin/claude/undertow-lead-handoff-423ixt`).
- **Merged since batch 2:**
  - RND-04 Drownbell VFX, the RND-24 GPU check and the ENV-09 LOD check (both PC docs).
  - Sweep Q (22 tasks; ADR 0028 accepted, ADR 0029 accepted with an amendment) and SPEC v1.3 (§4.2).
  - Batch 3: UI-05 Vowbound HUD, ARC-02 weather clock. The full gate was green: 1413 tests, 72 shots. One capture process aborted at exit, intermittently; filed as M1-QA-10.
  - RND-05 storm events (7 undertow shots approved after viewing).
  - fix6 (M2-RND-06 test and doc fixes, M1-ARC-16 router visible-window measurement).
  - Six new lavapipe baselines approved after viewing: the underwater ×3, drownbell_flood and the battle_vowbound ×2.
- **In flight:**
  - `lead/rnd27` (`../wt-rnd27`): the PC's ADR 0029 follow-ups (boot warm-up under 1 s, SceneState harvest). Gate running.
  - `lead/chars` (`../wt-chars`): claude/characters at bcdfe00 (Rhen, Toma, Asha clips, CHR-12, ART-06, CHR-04 start). The gate FAILED one test: Toma's mouth materials aren't on the `character_mouth` family (the RND-24 test). The characters track was asked to port them as Rhen did and push. Then re-run character_shading, the 32 character shots (not yet run) and merge. Blender asha 44, rhen 31 and toma 37 were identical.
- **The human's top priority:** **M1-CHR-14**, Asha's braid detached from her head, clothing and staff clipping, and detached limbs, with automated guards. It's on the characters track, queued right after the Toma mouth port.
- **Approved:** the PC may install the official Godot 4.6.3 export templates (checksum-verified, not committed) for the shader baker. The human confirmed.
- **Environments:** all three were working at the last heartbeat. Wake-ups come from a local background `sleep 2700` heartbeat (the routine fails with ACCESS_DENIED).

## Exact next step
1. When the rnd27 gate is green, merge it.
2. When the characters track pushes the Toma mouth port, merge claude/characters into lead/chars and run character_shading plus the 32 character shots. View any drift, then merge.
3. Merge CHR-14's braid fix as soon as it's pushed (it's the human's priority), and ask the PC for M1-QA-09 on hardware.
4. When m2-slice pushes its CMB-05 reconciliation, test-merge it with the battle filters, sim --check and its shots.
5. Review sweep R over the review column, and keep ~3 local agents busy (candidates: M1-QA-10, M2-CMB-06 if m2-slice doesn't take it).

## Log
- 2026-10-24 ~14:20: usage-limit stop at ~14:10. Resumed battle-presentation, ui, env-art and audio, and sent every track the no-waiting gate rules (CONSOLIDATED §4). Batch 5 is HELD: the shrine_s01 and s02 lavapipe captures deadlock after the GI bake (2/2); a QA agent is bisecting. Asha: 4 DIFF traced to one 1-ULP UV (Head vertex 3918) plus the texels around it; the characters track is snapping UVs. Gate queue (serial): rnd09 → batch 4 → the character shots → combat (batch 6).
- 2026-10-24 ~14:05: **To pc-gpu: queue top-up, in this order. Read the entry below first, which has the Ultra storm budget decision.**
  1. **Ultra storm at or under 4 ms at 1440p**: your next item, ahead of M3-RND-01. Take a free M2-RND id.
  2. M3-RND-01 Reefball look, as you planned.
  3. **The "Uniforms supplied for set (3)" Vulkan error**, twice a run, already on the integration branch: root-cause and fix it. If RND-11 didn't close it, take a free M2-RND id.
  4. **The Shell Shrine capture deadlock on hardware:** a lavapipe capture of `shrine_s01_approach` hung in the Lead's batch-5 gate. The main thread was in a cond-wait, and all four WorkerThreads were blocked on a mutex after "GI baked (2 states)". A local QA agent is root-causing it on lavapipe. Loop the shrine level's load plus GI bake about 20 times on your GPU (the perf build or capture) and report whether it hangs there too. Measure only; don't fix in parallel.
  5. After batch 4 merges (you'll see it on the integration branch: M2-ARC-08's ProgressWait): the first-launch re-measure, as in the entry below.
  6. After the characters merge (CHR-14 is gating now): M1-QA-09 on hardware, then the slice re-sweep.
  The 4.7.2 port branch: good. Keep it parked until the M2 review. M3-RND-02: ask the owner as planned.
- 2026-10-24: **To pc-gpu (RND-11, M1-RND-26):** acked. I merge both after RND-10. **Ultra budget decision:** a storm of 15–18 ms at native 1440p is not acceptable; it is the whole 60 fps frame. Ultra must keep the full-resolution compute body, but the storm's total must be at or under 4 ms at 1440p: take the body's step count or the compute resolution down on Ultra until it fits, and record it in undertow.md. Queue it as your next item (an M2-RND id that's free). **M2-ENV-05:** resident Haluna entries accepted; m2-slice makes the registry change, then you re-measure. **Also queued for you after batch 4 merges:** a first-launch re-measure for M2-ARC-08 (clear pipeline_warm.cfg and the driver cache, on Low and High; check reveal_wait_end == done, reveal_wait_ms and the cue).
- 2026-10-24: intro audit routed (see CONSOLIDATED §3). New menus track (claude/menus). Combat agent: live payouts and Read. **To pc-gpu:** M2-RND-10 acked; the Lead does the Art review and views every undertow_* drift before re-approving, after the b5 and rnd09 gates. Proceed with M2-RND-11, and file the capture_preset finding (it ignores a shot's setup block) as a QA task on your branch.
- 2026-10-24: merged rnd-04, sweep Q, SPEC v1.3, batch 3, rnd-05 and fix6. Filed M2-ARC-02, M1-QA-10 and M1-CHR-14 (top priority). Characters and m2-slice re-queued; the PC was approved to install export templates.
- 2026-10-24: merge batch 2 (3e59f8d). PC queue topped up.
- 2026-10-24: merged rnd-21, CHR-08, sweep O, qa-08, first-playable, cmb, ui-04, sweep P, rnd-01, m2-slice, rnd-23. Spawned the characters track. Hourly check-in trig_01LJyLo42xCq3WVmAza3BMhe.
- 2026-10-24: new Lead took over. Toolchain up. PC and m2-slice briefed.
- 2026-10-24 (old account): see CONSOLIDATED-history-2026-10-23.md.
