# CONSOLIDATED HANDOFF: start here (new account)

**Written:** 2026-10-24 by the outgoing Lead (cloud session `session_01Bg3iP7cPGyjbX4CyniBahc`), at the account handoff. Every session of the old account was told to stop, push and update its live log. Each environment's own detail is in this folder: [`lead-cloud.md`](lead-cloud.md), [`pc-gpu.md`](pc-gpu.md) and [`first-playable.md`](first-playable.md). **Fetch every branch first; the newest copy of each per-environment log may be on that environment's own branch** (see §2). The old running log is [`CONSOLIDATED-history-2026-10-23.md`](CONSOLIDATED-history-2026-10-23.md).

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
  - **Remaining exit criterion:** "one hero at final fidelity". Asha has been through six rounds (CHR-02, 03, 04, 07, 09, 10, with 11 in flight).
    - Latest GPU verdict (docs/kb/qa/gpu/*qa-05c*): neutral and smile pass; grief fails because of the teeth and mouth interior.
    - Still open: the lash comb, the lid band and the brow notch.
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
| `claude/new-session-mj8c3c` | **The integration branch, standing in for `main`.** Every merge lands here. Last full gate green at fc3940c (ci30). Scoped gates were green afterwards: ci32 at 2ce7045, ci33 lavapipe-approved merges at c940d77. See §5 for what is pending. |
| `claude/first-playable` | The First Playable session's branch. It's ahead of the integration branch with unmerged work (the Drownbell boss and the M2-FP queue). Its newest log is `docs/kb/handoffs/live/first-playable.md` on that branch. **Merge it after a scoped gate.** |
| `gpu/*` | The PC GPU session's branches, one per item. **Unmerged:** `gpu/rnd-18-20-followups` (lavapipe check ci35 was running at handoff), `gpu/rnd-21-mouth-fill` (needs the asha_* shots, the Blender asha job, and re-approval of asha_face_grief), `gpu/m2-rnd-01-undertow` (WIP), plus any newer branch. Everything else is merged. The PC's newest log, `pc-gpu.md`, is on its newest branch. |
| `worktree-agent-*` | Local to the old Lead's container. **Gone after the handoff**; anything not merged is lost, so the tasks say what to redo. |

## 3. Environments for the NEW account (recommended)
1. **The new Lead, a cloud session** that orchestrates, merges, reviews and runs the gates. It may use subagents in worktrees. 4 CPUs are enough with scoped gates.
2. **Optionally, a second cloud session as a dedicated feature track.** The old account's "First Playable" session worked well in its own container: spawn it with `create_session`, give it `outcome_branch` set to a `claude/<track>` branch, and give it a standing queue. Good next tracks:
   - **(a) the M2 vertical slice content:** the Drownbell boss, Haluna to slice quality, the Shell Shrine temple trial, the first Vowbound, Cutscene A and B facial animation, M2-FP-05 and M2-FP-06, M1-ARC-15;
   - **(b) Characters:** Rhen and Toma on the MPFB2 pipeline; Asha's animation clips.
3. **The PC GPU worker:** a Remote Control session on the human's Windows PC (RX 9070 XT, official Godot 4.6.3 and Vulkan). It **can message the Lead back** via `send_message`. It has been the most productive worker. Give it a standing queue of GPU-heavy items: captures and look judgements, perf, raymarching, shaders, GPU checks before lavapipe re-approvals.
   - **The human's rules for it:** cumulative CPU, memory and GPU load at or under **75%**; GPU timing benchmarks run one at a time; keep the PC awake with the monitor on (a switched-off monitor broke the swapchain once).
   - **Branch rules:** new `gpu/*` branches only; never overwrite lavapipe baselines; list the drifting shots; Asha's materials change only via `assets_src/characters/asha/write_materials.py`; run validate_data and the tools tests before pushing.
   - **The PC's unfinished queue** (also in pc-gpu.md): M2-RND-01 Undertow production (WIP) → M1-RND-22 prewarm hitch floor → M2-RND-03 battle VFX library → M2-RND-02 underwater → M2-RND-04 Drownbell VFX and flood rig.

## 4. Process that works (keep it)
- **Standing queues:** never one task at a time; ask each environment to message when it's two items from the end.
- **Review sweeps:** after each merge batch, a fresh reviewer agent covers every `status: review` task. On approve or approve-with-fixes, close the task and file the fixes as new tasks. On request-changes, reopen it.
- **Gate scope** (CLAUDE.md): agents run only checks their change can break. The Lead runs the full `tools/ci_local.sh` (about 60–90 min on 4 CPUs) after a batch of code or render merges, in a separate `lead/integration` worktree.
- **NEVER merge a `gpu/*` branch before running its affected shots on lavapipe.** Test-merge in a scratch worktree (for example `lead/test`), run `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=<ids> HYMN_LOG_DIR=$(mktemp -d) tools/ci_local.sh`, view every drift side by side, then copy `tests/screenshots/out/<id>.png` to `baselines/` and merge. Two PC merges had to be reverted for skipping this.
- **Merging:**
  - Append-only conflicts go through `python3 tools/dev/merge_union.py <file>`. Check for duplicate loc keys with `cut -d, -f1 game/data/loc/strings.csv | sort | uniq -d`.
  - Never commit conflict markers; check with `git grep -n '^<<<<<<< '`.
  - Run `timeout 900 python3 -m unittest discover -s tools/tests`, which takes about 4 minutes; a 280 s timeout cuts it off silently.
- **Number collisions:** parallel agents collide on task ids, ADR numbers and handoff numbers, so check every merge. Valid task roles are listed by `taskboard.py --check`; use `character` for art.
- **Coverage baseline:** ratchet it up after test-adding merges with `python3 tools/coverage/run_coverage.py --update-baseline`. Currently battle 99.93% and progression 96.52%.

## 5. Exact next steps for the new Lead
1. `git fetch origin` and check out `claude/new-session-mj8c3c`. Set up the tools: `python3 tools/dev/fetch_godot.py`, `fetch_render_deps.py` and `fetch_blender.py`.
2. Merge, with lavapipe checks:
   - `gpu/rnd-18-20-followups`: affected shots are water_*, undertow_*, haluna_h01 and h04; the PC expects zero drift.
   - `gpu/rnd-21-mouth-fill`: the asha_* shots, plus `python3 tools/dev/verify_blender_builds.py --job asha`; re-approve asha_face_grief after viewing it.
   - Then `claude/first-playable` (scoped battle, field and FP shots, plus `python3 tools/balance/sim.py --check` for the Drownbell suite).
   - Then any newer `gpu/*` branch, such as `gpu/m2-rnd-01-undertow` once it's in review.
3. Run the full gate. Then a review sweep over the review column: M1-ENV-03, RND-15, RND-16, RND-17, RND-18, RND-20, RND-21, CHR-03, CHR-10, M2-CMB-02, M2-NIT-03, M2-UI-01 and M2-UI-02.
4. **M1-CHR-11 (Asha round 6)** was in flight in the old Lead's local worktree. Check `lead-cloud.md` for whether it was merged. If not, re-launch it from its task file.
5. Message the new PC GPU session with its queue (§3) and the rules. Spawn the second cloud track if wanted.
6. Keep this file and `lead-cloud.md` current after every merge batch.

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
