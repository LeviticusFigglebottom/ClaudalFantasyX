# CONSOLIDATED HANDOFF: start here

**Rewritten:** 2026-10-24 by the Lead, cloud session `session_019iimsngAgPLEram1wcbLpE` (new account). It replaces the old account's handoff; that version is in git history at a504072. Each environment's detail is in this folder (`lead-cloud.md`, `pc-gpu.md`, and `m2-slice.md` / `characters.md` on those tracks' branches). **Fetch every branch first: the newest per-environment log is on that environment's own branch.**

## 0. Read these, in this order
1. [`CLAUDE.md`](../../../CLAUDE.md): the operating rules for every agent. They include "Gate scope", §7a live logs, and §8a shared-machine and scratch rules.
2. [`SPEC.md`](../../../SPEC.md) v1.2: the brief. Only the Lead edits it, and every change needs an ADR plus a version note.
3. [`docs/kb/STATUS.md`](../../STATUS.md): milestone, risks, and questions for the human.
4. This file, then `python3 tools/taskboard.py` for the live task board (about 91 of 121 done).
5. ADRs 0001–0024 in [`docs/kb/decisions/`](../../decisions/), skimming the titles.

## 1. What the project is and where it stands
- *Hymn of the Undertow* is an original, cinematic, turn-based RPG in Godot **4.6.3** (Forward+, typed GDScript, data-driven JSON, a headless and deterministic battle engine).
- **IP guardrail:** it is inspired in tone only by a classic 2001 JRPG. Many story re-stagings removed echoes of it: ADRs 0015, 0016, 0017, 0020 and 0022, plus SPEC v1.1 and v1.2. Keep that strictness. For example, never use the inspiring game's -ra/-ga spell-tier suffixes.
- **Milestone M1 (tech and look prototypes):** nearly done.
  - **Exit criteria met:** CTB battle, water, glimmer, the Undertow prototype (perf solved), and the five-shot mood test.
  - **Remaining exit criterion:** "one hero at final fidelity". Asha has been through rounds CHR-02 to CHR-11, plus RND-20 and RND-21 (all merged). Round 7 is M1-CHR-12, on the characters track.
    - Latest GPU verdict (docs/kb/qa/gpu/2026-10-24-qa-08-asha.md): neutral passes; smile passes on shading but reads as a smirk at 1x; grief fails, closely, on a lip-edge black rim and peg teeth.
    - Still open: the lid band (R:B 3.7 against 2.0–2.5), the crown and hairline, the smile's eyes, and lashes that read spiky.
    - The fallback is ADR 0019, stronger stylisation, which needs the human's call.
  - **Then:** M1-LEAD-01, the M1 review. It also waits on the human listening to the music (AUD-02).
- **Already into M2 (vertical slice):**
  - A **playable first-minutes thread** (title → prologue → beach cutscene → playable Haluna → villagers → first battle → shrine save → Ch3 cutscene → end card). See [`docs/PLAYTEST.md`](../../../PLAYTEST.md).
  - Save **v6**: party vitals, bestiary, Swell carry.
  - Swell gauges with a unique input for each of the four heroes. Shallows Verse heals every ally except Asha: "the Cantor's song is for the others".
  - Read, bestiary and preemptive/ambush openings.
  - The Read panel, the bestiary menu and the Swell mode menu.
  - Post-import scripts, and fully byte-reproducible Blender builds.
- **The M2 vertical-slice review is a BLOCKING human review** (SPEC §16 Q7).

## 2. Branches (all on `LeviticusFigglebottom/ClaudalFantasyX`)
| Branch | Status |
|---|---|
| `claude/undertow-lead-handoff-423ixt` | **The integration branch, standing in for `main`** (CLAUDE.md §4: the Lead's session branch). Every merge lands here. |
| `claude/new-session-mj8c3c` | The old integration branch. **Frozen at a504072**; don't merge into it. |
| `claude/m2-slice` | The M2 vertical-slice track (from `claude/first-playable` 67984ce). |
| `claude/characters` | The Characters track (from the integration branch). |
| `claude/first-playable` | The old First Playable branch, stopped at 67984ce. Being merged in (see §5). |
| `gpu/*` | The PC GPU session's branches, one per item. Merged: rnd-21-mouth-fill, qa-07, qa-08-asha-recheck. **Don't merge:** qa-05d-asha-recheck (superseded by qa-08), chr-04-materials and qa-05b-asha-recheck (overtaken by later rounds). **WIP:** m2-rnd-01-undertow (54b5f33 is a mergeable checkpoint; the 5 undertow shots get re-approved when the task reaches review), m2-rnd-01b-undertow-compute. |
| `lead/test`, `lead/fp`, `worktree-agent-*` | Local to the Lead's container. Lost on a restart; anything unmerged is redone from its task file. |

## 3. Environments (live)
1. **Lead:** cloud `session_019iimsngAgPLEram1wcbLpE`, 4 CPUs. It orchestrates, merges, reviews and runs the gates, with up to ~3 local subagents in worktrees (Character, Combat, UI, Reviewer). An **hourly check-in routine** (`trig_01LJyLo42xCq3WVmAza3BMhe`, :54 each hour) checks every environment, merges what's ready and refreshes these logs.
2. **pc-gpu:** Remote Control `session_01UFcBRsk9M9EKtxJKdBU2mB` (desktop-jj0o43o) on the human's PC (RX 9070 XT, Windows, official Godot 4.6.3). It **can message the Lead**.
   - **Queue:** M2-RND-01 Undertow production (with the compute-pass occlusion) → M1-RND-22 prewarm floor → M2-RND-03 battle VFX → M2-RND-02 underwater → M2-RND-04 Drownbell VFX and flood rig. GPU checks before any lavapipe re-approval jump the queue.
   - **The human's rules:** total CPU, memory and GPU load ≤ 75%; one GPU benchmark at a time (a CPU-light subagent alongside is fine); new `gpu/*` branches only; never overwrite baselines; Asha's materials change only via write_materials.py; keep pc-gpu.md current; message the Lead when two items remain.
3. **m2-slice:** cloud `session_01DQ9tdk8Uatb8Jr6raAkXiC`, branch `claude/m2-slice`, Auto mode, 2–3 subagents allowed. Queue: M2-FP-10 dialogue key light → M2-FP-11 (undo FP-09's zone-sun bias 3.0; two waiting router callers) → Drownbell follow-ups (its boss status strip is being renumbered from a colliding FP-11 to FP-12) → FP-05/ARC-15 follow-ups → Haluna at slice quality → Shell Shrine trial → first Vowbound, Cutscene A/B faces. Log: `m2-slice.md` on its branch.
4. **characters:** cloud `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch `claude/characters`, Auto mode, 2–3 subagents allowed. Queue: **M1-CHR-12 Asha round 7 first** (grief lip-edge rim and peg teeth, lid band, smile eyes, crown; from QA-08), with M2-CHR-01 Rhen and Toma in parallel (parked WIP in assets_src/characters/rhen/, see WIP.md) → Asha's clips (M2-FP-07) → M1-ART-06. Log: `characters.md` on its branch.
- **Permissions:** `.claude/settings.json` allow-lists the read-only checks and cross-session messaging (the human's directive). Sessions pick it up after merging the integration branch.

## 4. Process that works (keep it)
- **Standing queues:** never one task at a time; ask each environment to message when it's two items from the end.
- **Review sweeps:** after each merge batch, a fresh reviewer agent covers every `status: review` task. On approve or approve-with-fixes, close the task and file the fixes as new tasks. On request-changes, reopen it.
- **Gate scope** (CLAUDE.md): agents run only checks their change can break. The Lead runs the full `tools/ci_local.sh` (about 60–90 min on 4 CPUs) after a batch of code or render merges, in a separate `lead/integration` worktree.
- **NEVER merge a `gpu/*` branch before running its affected shots on lavapipe.** Test-merge in a scratch worktree (for example `lead/test`), run `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=<ids> HYMN_LOG_DIR=$(mktemp -d) tools/ci_local.sh`, view every drift side by side, then copy `tests/screenshots/out/<id>.png` to `baselines/` and merge. Two PC merges had to be reverted for skipping this.
- **Merging:**
  - Append-only conflicts go through `python3 tools/dev/merge_union.py <file>`. Check for duplicate loc keys with `cut -d, -f1 game/data/loc/strings.csv | sort | uniq -d`.
  - Never commit conflict markers; check with `git grep -n '^<<<<<<< '`.
  - Run `timeout 900 python3 -m unittest discover -s tools/tests`, which takes about 4 minutes; a 280 s timeout cuts it off silently.
- **Number collisions:** at handoff, the integration branch's task files were renumbered to match `claude/first-playable`: FP-05 is polish and FP-06 the Drownbell boss on that branch; thread hardening is FP-09 and the dialogue key light FP-10. Parallel agents collide on task ids, ADR numbers and handoff numbers, so check every merge. Valid task roles are listed by `taskboard.py --check`; use `character` for art.
- **Coverage baseline:** ratchet it up after test-adding merges with `python3 tools/coverage/run_coverage.py --update-baseline`. Currently battle 99.93% and progression 96.52%.

## 5. Exact next steps for the Lead
1. **Merge `claude/first-playable`.** The trial merge is in `lead/fp` (`../wt-fp`):
   - The .uid conflict took ours.
   - The Drownbell ADR was **renumbered 0024 → 0026**, because 0024 is the Asha hair ADR.
   - `sim.py --check` passes every suite (Drownbell role_answer 77.6%, smart 85.2%).
   - The scoped gate (battle and title shots, Blender skipped) is re-running. The first run stopped on the Rhen build.sh test failure, since fixed by parking build.sh.wip.
   - When it's green, merge it and tell m2-slice to merge the integration branch.
2. **Merge the local subagents as they report:** Combat (the battle_engine.gd split, then one slice combat item) and UI (M2-UI-04). Merge each cloud track's review-ready work after a scoped gate on a test merge.
3. **Re-approve** the undertow shots when M2-RND-01 reaches review (GPU drift: eye 0.072, night 0.043, dusk 0.029, day_ch08 0.023, low 0.020). **View each one on lavapipe first.**
4. **Full gate** (`tools/ci_local.sh`, every shot, Blender required) in a `lead/integration` worktree after this merge batch.
5. **The next review sweep (P)** over the review column: M1-CHR-08, M1-QA-08, and whatever the tracks hand in.
6. **When CHR-12 lands:** a PC GPU re-check of grief and smile (as QA-08 did), then M1-LEAD-01 once the human has listened to the music.
7. **Also open:** a jagged stair-step dark shape on Asha's vest shoulder (QA-08 item F) needs Rendering triage. Fold it into M1-RND-23.

## 6. Open questions for the human (also in STATUS.md)
- **Playtest** the first minutes (docs/PLAYTEST.md; a ready copy may be at `C:\Users\Aaron\Hymn_Playtest\PLAY.bat`). Is Asha's close-up face acceptable as a direction, or should we take ADR 0019's stronger stylisation?
- **Music:** listen to the three cues (docs/kb/audio/listening_notes.md, §16 Q3). This blocks AUD-02 and M1-LEAD-01.
- **Git LFS?** The 5 MB file cap binds Asha's GLB and textures.
- **GitHub Actions:** runs never leave `queued`; check the repo settings.
- **Reefball arena form:** default is to keep it.

## 7. Toolchain and gotchas
**Getting the tools:**
- Godot 4.6.3 and Blender 5.0.1 come from the Ubuntu archive via `tools/dev/fetch_*.py`; GitHub release downloads are blocked in the cloud.
- **Baselines are lavapipe** (software Forward+, ADR 0009). Never approve GPU captures as baselines.

**Shared-machine safety:**
- Never kill processes by pattern; kill only your own PIDs (CLAUDE.md §8a).
- Give every run a unique `HYMN_LOG_DIR` and `XDG_DATA_HOME`.
- Put scratch files in a per-task subfolder.

**Blender gate:**
- `tools/dev/verify_blender_builds.py`; thread counts are pinned per job.
- The known-failure list is EMPTY: every Blender output rebuilds byte-identically.
- With no `main` ref, set `HYMN_BLENDER_BASE=<sha>`, or it rebuilds every job (about 6 minutes).

**Assets:** Asha's materials come from `write_materials.py` (pure Python); hand-editing a `.tres` breaks the gate.

**Line caps and RNG:**
- `battle_controller.gd` is at about 994 of gdlint's 1000-line cap. Put new logic in helper classes.
- Live battles draw one opening roll (preemptive or ambush). Story encounters set `"opening": "normal"`.

**Things that didn't work in the old account:**
- `send_later` scheduled check-ins failed with ACCESS_DENIED.
- Background subagents die on a container restart; only what they committed in their worktree survives.

## 8. Where things are
- **Story:** docs/kb/story/; ADRs 0015–0017, 0020, 0022.
- **Art:** docs/kb/art/ (palette.json, color_script.md, characters/asha*.md).
- **Tech:** docs/kb/tech/ (architecture: save v6 and DataHealth; field_camera; dialogue_format; battle_ctb; ui; water; glimmer; undertow; character_shading; asset_import).
- **Design:** docs/kb/design/ (formulas, balance_report, economy).
- **GPU reports:** docs/kb/qa/gpu/.
- **Per-task handoffs:** docs/kb/handoffs/2026-10-23-*.md.
