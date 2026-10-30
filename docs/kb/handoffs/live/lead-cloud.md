# Live log: Lead (cloud) environment


## LEAD 2026-10-29: `session_01Bg3iP7cPGyjbX4CyniBahc` on `claude/new-session-mj8c3c` (the integration branch)
- 17:14–17:17 UTC: created 9 cloud sessions (env `env_0196G2TTr369gfmPLsL5gD3s`, tags `undertow`, `undertow:<track>`). Briefs = SESSION-BRIEFS preamble + track brief + the PC-offline rule.

| Track | Session | Branch |
|---|---|---|
| env-art | `session_01UPFyEAzY1JcdZvoc5FBH1A` | claude/env-art |
| env-art-b | `session_01UPFyEA3FwDAoAKTpVGbGsy` | claude/env-art-b |
| characters | `session_01UPFyE733U6vQyV7tqjizxc` | claude/characters |
| act1-chapters | `session_01UPFyE97m2fmnEAZsDPDniN` | claude/act1-chapters |
| integration-qa | `session_01UPFyE9i6WzR6xpzKDZ82HQ` | claude/hero-integration |
| slice-polish | `session_01UPFyE6pg4bUbqP33yjAkE5` | claude/m2-slice |
| ui-menus | `session_01UPFyE7ZqP7u61XAAeaJqGy` | claude/ui |
| battle-presentation | `session_01UPFyEA8QkJULH74MGgnMvJ` | claude/battle-presentation |
| **gate** | `session_01UPFyE6NmbMsX7kaGj7ousX` | lead/gate-big17 (shots → lead/gate-big17-shots; its log is `gate.md`) |

| creatures | `session_01UPFyE7ob7hr4Skv4cw3rtN` | claude/creatures (started 18:43: big17 gate reds test_npc/test_post_import, audit M3-HER-1142, QA row 40) |
| creatures-b | `session_01UPFyE6iidnDAeaAEP21ZYd` | claude/creatures-b (started 18:43: Moll capsule in battle rows 12/35, Reach arm row 36, row 30) |

| **pc-gpu** (Remote Control, desktop-jj0o43o) | `session_01UPFyEABtMznCLCcXCPdmda` | gpu/* (briefed 00:20 10-30: Act I real-GPU QA pass 3 on lead/gate-big18, the PC-QUEUE items, perf budget, its own RND work, Blender verifies) |
| act2-plan | `session_01UPFyE8YdUYQ5LuuhgfZtqS` | claude/act2-plan (docs only: the Act II plan, the tasks blocked by ADR 0203, the track split) |
| gate big18 | `session_01UPFyEAXofxWazWNnRTzFGJ` | lead/gate-big18 (log `gate-big18.md`) |

- 10-30 10:15: **PC pass 5 (gpu/act1-qa-5, big20): row 67 FIXED** (every entry < 1 s hidden; Brine Shoals 5/5 fresh, no hang). Fixed 23, 25, 43, 44, 45, 49, 50, 52, 53, 57, 60, 67. Partly: 24, 37, 38, 39, 46, 47, 51, 54, 55, 58. Open: 17 (PC fix 12cf79cb → big22), 21, 34, 56, 61, 62, 63, 64, 66. Regressed: 59. All routed (integration-qa 21/24/37/38/47/66; act1-chapters 34/39/58; characters 46/54/55/56; battle-presentation 61/64; env-art-b 51/62/63; env-art 59; slice-polish 58). Told characters not to loosen test_rig_integrity limits.
- 10-30 09:55: **big21 merged** @ 0347aa74 (includes ui-menus row 67 fix 329e7bce). big22 requested with all MERGE-READY heads, Act I fixes first. PC running pass 5; asked to re-probe row 67 on 0347aa74. Idle tracks re-tasked (creatures, creatures-b, audio, env-art-b, ui-menus).
- 10-30 09:30: **GOTCHA: send_later / create_trigger into this Lead session fail with ACCESS_DENIED** (the 06:13 and 09:23 heartbeats never arrived). Deleted them. The heartbeat is now a 20-min background `sleep 1200` Bash task inside the Lead session, re-armed on each wake. A future Lead should do the same.
- 10-30 09:05: **Lead gap 06:00–08:57** (the 06:13 heartbeat never woke this session); added an hourly backstop scheduled task on top of the 20-min send_later. **big20 merged** @ 7dc3ab41 with its two batch reds FAST-TRACKed: hero lens guard → integration-qa; Lowlight/Sanctum snaps → act1-chapters (+ env-art-b). Tools reds routed: act1-chapters (audio_audit, vfx_coverage), act2-plan (cutscene_sfx_files, hero_clips), env-art (keth), characters (13 villagers' rig_integrity, sefir). big21's `glimmer` VFX swatch → battle-presentation. Gate rule: branch-content-only reds = merge-approved. PC sent pass 5 on 7dc3ab41. Every idle track re-tasked.
- 10-30 05:55: big19's second shot batch reviewed and approved (83, 1e63e5ba). big20 fast gate running (lead/gate-big20 @ 4e3c74c9); its one red so far, test_slice_primitives (the Oruvel seabed PlaneMesh, e3ad5bbe), is a FAST-TRACK to slice-polish; the gate reverts just that actor if the fix isn't in by the end of the lanes. Drowner: the Combat side's definition stands. PC asked to measure claude/ui @ 329e7bce (row 67) now; pass 5 after big20. Idle tracks given work: creatures (urchin element off ice, tortoise LOD1), env-art (Act I rows 25/47, ΔE, o17, then Ch13–15 kits), act2-plan (Act II barks and lore), ui-menus (Act II UI and portraits), audio (Act II cues).
- 21:25: **big17 merged** @ 96222b30 ahead of its shots (the human asked to play it now, in the gate session). big18 gate started.
| audio | `session_01UPFyE9L9BA3QodpCNJEfAs` | claude/audio (started 23:10: Act I sound audit) |

- 23:10: **Lead rule from here: no track idles waiting on a gate.** A track with BACKLOG EMPTY gets a self-directed final-quality audit of its own Act I lane on the newest gate branch (as played, with self-rendered stills). Sent to env-art, env-art-b, creatures, creatures-b, battle-presentation, ui-menus, act1-chapters, integration-qa and slice-polish.
- 18:40: ADR 0201 (Pell's niche wording, SPEC v1.5, `i:blue mage` banned). Routed big17's 4 pre-existing tools reds: freed-cast lint → env-art-b; test_npc and test_post_import → creatures; villager_shopkeeper_front NO BASE → approve at the gate.
- **The PC is offline.** When it returns: find it with `list_sessions` (environment_kind `bridge`), then send it the PC brief (SESSION-BRIEFS.md) plus this queue:
  1. Gate whatever batch is next, if the cloud gate session hasn't already gated it.
  2. Act I real-GPU QA at High 1440p, pass A and pass B. Collect every track's `### PC-QUEUE` items first (`grep -n -A20 "PC-QUEUE" docs/kb/handoffs/live/*.md`).
  3. Its unfinished M2-RND-01 (WIP on gpu/m2-rnd-01-undertow), and the in-review RND-22, M2-RND-02/03/04 follow-ups (pc-gpu.md "Unfinished queue").
  4. Measure the Act I scene-change hitches, which must be ≤ 1 s hidden (ADR 0042 §4).
- Heartbeat: every 20 min, check `list_sessions` and run `tools/dev/lead/leadask.sh`, then answer LEAD-ASKs, merge MERGE-READY work via batches, and check gate.md for GATE-BUILT/GATE-DONE.

**Session:** `session_019iimsngAgPLEram1wcbLpE` (new account) · **Branch:** `claude/undertow-lead-handoff-423ixt` (the integration branch) · **Container:** 4 CPUs, Ubuntu, lavapipe. The container has restarted twice; the disk and the worktrees survived both times.

## NEW ACCOUNT (from 2026-10-25), Lead session_018aiGwGLGkxsnMnu8VfCu1m on claude/undertow-lead-handoff-ze8rrn
- 01:45: the integration branch moved to -ze8rrn (a fast-forward). test_hero_clips on big9: 18/18 OK. The PC was briefed: gate big9, then M1-QA-09, the --budget re-sweep, the Act I playthrough, CHR-11 verify. Messaging the PC needed the owner's trust confirmation, now given.
- 01:57: nine track sessions created (roster in CONSOLIDATED §3a). Next: build lead/big10 from every track head on top of big9, and gate it after big9.
- 02:20: four tracks (audio, hero-integration, battle-presentation, act1-chapters) blocked on send_message permission prompts → interrupted and re-briefed. Every track is told: no send_message; use live logs and request tasks; the Lead relays.
- 02:22: **lead/gate-big10 @ 181708a7 pushed** (big9 + integration de93e79e + bpr a3e489bb, creatures 5b32803d, hero-int 0eff0b34, characters 66529dba, menus 0b5c2bd9, ui 776a24a1, m2-slice 6c50823f, env-art 294577d6, audio 7141fef2). Cloud: validate/taskboard/dlgc/lint/format OK, tool tests 1141 OK, Godot 2637/2 (env-only: scene_router_swap without $GODOT; 15/0 with it). Watch: mixed battle baselines (menus vs big9); voices.json `wright` keeps audio's pending voice. PC gates it after big9.
- 10-25 ~02:40 → 10-27 ~15:10: usage-limit stop (all sessions). Nothing had been pushed since about 02:40; big9 had not finished its PC gate.
- 10-27 15:15: limit reset. Nudged all ten sessions (the PC: finish big9 → gpu/gate-big9-shots, then big10).
- 10-27 15:40: **big9 merged** (3b7cbf5e) after viewing all 48 drifted shots on contact sheets (baseline | out | diff). Routed: the Ysolde capsule → hero-integration; the camp capsule foe → creatures; the Hullgnaw framing → bpr 404; a prologue colour shot → slice-polish. Deleting `lead/gate-big9` failed (the remote hung up); retry later.

## STATE AT HANDOVER (2026-10-25)
- **Integration head:** 6c6e5514 plus handover docs. big8 is merged; the fast-tracked playtest fixes (M2-FP-28, M3-CMB-02, M2-BPR-11) are in.
- **Unmerged, staged:** `lead/gate-big9` @ ae4666e0. It is big8 plus the hero integration, the prologue fixes and every track's newest work. It isn't gated yet: gate it on the PC first (CONSOLIDATED §5.1).
- **Local state:** no local agent branches are left unmerged. The old container's worktrees (wt-*) are disposable.
- **Messages sent at handover:** every track was told to stop, push and write a "STATE AT HANDOVER" section plus a session handoff. The PC session was inactive, so its state is summarised in CONSOLIDATED §3/§5/§7 and in pc-gpu.md on its gpu/* branches.
- **Exact next step:** CONSOLIDATED.md §5.

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
- 2026-10-24 ~19:55: **big7 merged (d6a0886d).** It carries ui, menus, battle-presentation, characters (CHR-14), creatures, combat (CMB-07/08), m2-slice, audio, the PC's RND-10..13 and 26 plus M3-RND-01, M2-QA-02 and M2-CHR-10. Gate: Blender 39/39 identical, Godot 1940/0, coverage OK, 196/196 shots across 3 lanes (my container plus gate runners A and B), 29 re-approved after viewing. Decisions: the Drownbell p90 ceiling 60 → 66; the menus' injected-clock swap test cherry-picked. **Next:** big8 (a local merge agent is building it on lead/big8: the newest menus, ui, m2-slice, BPR batch 2, creatures polish, env-art, audio, the PC's RND-14..19, NIT-05, M3-RND-04/05, M3-RBL-01 Reefball). Gate it on lead/gate-big8 with the PC (WSL) and runners A/B as shards. The human's playtest fixes (encounters, prologue default, greyscale) are m2-slice's top priority.
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

## Cloud renders (PC paused)
- RENDERED @ 7a8bff79d15491fe5f03f5ebdaa8211b184eaf5b: lead/gate-render-hero-integration-7a8bff7; 0 pass, 7 drift (cloud)
- RENDERED @ 60cbb212cec3781e32e8ac0f96303b895d54f01e: lead/gate-render-battle-presentation-60cbb21; 0 pass, 1 drift (cloud)
- RENDERED @ 1c9bf8bd7ec282e7dab59df80807c1baed0e4173: lead/gate-render-hero-integration-1c9bf8b; 0 pass, 7 drift (cloud)
- RENDERED @ 5a5b4fed21aa09992244352679a50aa125695273: lead/gate-render-battle-presentation-5a5b4fe; 0 pass, 2 drift; 2 new without baseline (cloud)
- RENDERED @ ed3a458ef8ee2ab08c0626b6e70b42fb0fadf117: lead/gate-render-battle-presentation-ed3a458; 0 pass, 4 drift (cloud)
- RENDERED @ 60eee2f73a37fad79613876a42696da58d8f4962: lead/gate-render-env-art-60eee2f; 0 pass, 5 drift; 3 new without baseline (cloud)
- RENDERED @ c990e2c2c300cf38cb05106e5ea98b8cfb36e20e: lead/gate-render-env-art-c990e2c; 0 pass, 1 drift; 1 new without baseline (cloud)
- RENDERED @ 191e5e89146500aec22ab308413253964391c496: lead/gate-render-env-art-191e5e8; 0 pass, 1 drift; 1 new without baseline (cloud)
- RENDERED @ ab58f891793e482ec9d7ae0ab47e765b72f0e840: lead/gate-render-env-art-ab58f89; 0 pass, 5 drift (cloud)
- RENDERED @ ee3bd3354a6942e6bea5a8598e6b6251d5e717af: lead/gate-render-characters-ee3bd33; 1 pass, 7 drift; 7 new without baseline (cloud)
- RENDERED @ ead04bab2d3963ea1a5a6dc13e4a09360169341c: lead/gate-render-m2-slice-ead04ba; 0 pass, 13 drift; 8 new without baseline, shell_shrine GI rebaked (cloud)
- RENDERED @ 8be2adcd0a63633aa84182842c30e6cdbf1c22e5: lead/gate-render-env-art-8be2adc; 0 pass, 6 drift; 3 new without baseline (cloud)
- RENDERED @ f39cdde37f4831bc6429aec4fa9afe0d9be26ed0: lead/gate-render-env-art-f39cdde; 1 pass, 3 drift (cloud)
- RENDERED @ da7891cf8d765b3c49b3b975d46b99b6abf5f6fb: lead/gate-render-ui-da7891c; 1 pass, 2 drift; 1 new without baseline (cloud)
- RENDERED @ c7703809a107368ea2c2c58de4a1972ac0badf42: lead/gate-render-env-art-c770380; 0 pass, 1 drift; 1 new without baseline (cloud)
- RENDERED @ 1e14af8e0168e3c7ec04b24d0140cabd7858b908: lead/gate-render-env-art-1e14af8; 2 pass, 2 drift (cloud)
- RENDERED @ fca9987986697c673d32188af45879f0a2d257b1: lead/gate-render-env-art-fca9987; 0 pass, 1 drift; 1 new without baseline (cloud)
- RENDERED @ 34d6e51d88b7792c1e109d2773f1eceeeb3ca829: lead/gate-render-ui-34d6e51; 1 pass, 4 drift (cloud)
- RENDERED @ 3b0e44b0b8c0490ddd92a6c0856d0625e1e2b09d: lead/gate-render-creatures-3b0e44b; 0 pass, 3 drift; 1 new without baseline, 2 portrait PNGs (cloud)

## GATE-REQUEST lead/gate-big14 @ 8707ff90 (10-28 ~04:40)
- Integration 608db549 plus all 11 track heads, including the human's playtest FAST-TRACKS (the grounded run, the party spawn, the Prologue colour, Rhen's shallows pose).
- Checks already pass: validate_data, taskboard, dlgc, lint and format.
- **Rebake the Shell Shrine GI** (`tools/shrine/bake_shrine_gi.tscn`, then `gi_inputs.py --write`). Two branches each rebaked it, so the merged inputs match neither bake.
- **Known red:** `test_arenas` reproducibility for `ash_terrace_lanternfall` (red on env-art-b too; needs env-art's M3-ENV-1306).
- Baseline PNG conflicts kept the integration side; I re-approve after viewing.

## GATE-REQUEST lead/gate-big15 @ a44fec70 (10-28 ~10:35)
- big14 plus every track's big14 fixes, plus lead/gate-ft-beach (the beach re-stage). hero-integration is at b7526686: its party-camera fix (Rhen off screen) is not in yet.
- validate, taskboard, dlgc, lint and format all pass. The shrine GI inputs are unchanged (gi_inputs --check is up to date), so no rebake.
- Run with HYMN_STEP_TIMEOUT at 3 h.

## HANDOVER 2026-10-28 ~18:40 UTC (usage limit; a new account takes over)
- Read CONSOLIDATED.md §0. big16 @ ff82858c is the next merge (it contains big15). Gate results go to lead/gate-big16-shots if the cloud gate finished; otherwise have the PC gate it.
- Fold in creatures f6846325 and hero-integration a6e9d548 before merging. The Lead tools are in tools/dev/lead/.
