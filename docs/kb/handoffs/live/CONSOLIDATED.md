# CONSOLIDATED HANDOFF: start here

**Rewritten:** 2026-10-24 by the Lead, cloud session `session_019iimsngAgPLEram1wcbLpE` (new account). It replaces the old account's handoff; that version is in git history at a504072. Each environment's detail is in this folder (`lead-cloud.md`, `pc-gpu.md`, and `m2-slice.md` / `characters.md` on those tracks' branches). **Fetch every branch first: the newest per-environment log is on that environment's own branch.**

## 0. Read these, in this order
1. [`CLAUDE.md`](../../../CLAUDE.md): the operating rules for every agent. They include "Gate scope", §7a live logs, and §8a shared-machine and scratch rules.
2. [`SPEC.md`](../../../SPEC.md) v1.3: the brief. Only the Lead edits it, and every change needs an ADR plus a version note.
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
| `gpu/*` | The PC GPU session's branches, one per item. Merged: rnd-21-mouth-fill, qa-07, qa-08-asha-recheck. **Don't merge:** qa-05d-asha-recheck (superseded by qa-08), chr-04-materials and qa-05b-asha-recheck (overtaken by later rounds). Merged on 2026-10-24: rnd-01(b), rnd-22, rnd-02, rnd-03 and fp-10-keylight-check. **Pending:** m2-rnd-04-drownbell-vfx. |
| `lead/test`, `lead/fp`, `worktree-agent-*` | Local to the Lead's container. Lost on a restart; anything unmerged is redone from its task file. |

## 3. Environments (live)
1. **Lead:** cloud `session_019iimsngAgPLEram1wcbLpE`, 4 CPUs. It orchestrates, merges, reviews and runs the gates, with up to ~3 local subagents in worktrees (Character, Combat, UI, Reviewer). An **hourly check-in routine** (`trig_01LJyLo42xCq3WVmAza3BMhe`, :54 each hour) checks every environment, merges what's ready and refreshes these logs.
2. **pc-gpu:** Remote Control `session_01UFcBRsk9M9EKtxJKdBU2mB` (desktop-jj0o43o) on the human's PC (RX 9070 XT, Windows, official Godot 4.6.3). It **can message the Lead**.
   - **Queue:** M2-RND-01 Undertow production (with the compute-pass occlusion) → M1-RND-22 prewarm floor → M2-RND-03 battle VFX → M2-RND-02 underwater → M2-RND-04 Drownbell VFX and flood rig. GPU checks before any lavapipe re-approval jump the queue.
   - **The human's rules:** total CPU, memory and GPU load ≤ 75%; one GPU benchmark at a time (a CPU-light subagent alongside is fine); new `gpu/*` branches only; never overwrite baselines; Asha's materials change only via write_materials.py; keep pc-gpu.md current; message the Lead when two items remain.
3. **m2-slice:** cloud `session_01DQ9tdk8Uatb8Jr6raAkXiC`, branch `claude/m2-slice`, Auto mode, 2–3 subagents allowed. Queue: M2-FP-10 dialogue key light → M2-FP-11 (undo FP-09's zone-sun bias 3.0; two waiting router callers) → Drownbell follow-ups (its boss status strip is being renumbered from a colliding FP-11 to FP-12) → FP-05/ARC-15 follow-ups → Haluna at slice quality → Shell Shrine trial → first Vowbound, Cutscene A/B faces. Log: `m2-slice.md` on its branch.
4. **characters:** cloud `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch `claude/characters`, Auto mode, 2–3 subagents allowed. Queue: **M1-CHR-12 Asha round 7 first** (grief lip-edge rim and peg teeth, lid band, smile eyes, crown; from QA-08), with M2-CHR-01 Rhen and Toma in parallel (parked WIP in assets_src/characters/rhen/, see WIP.md) → Asha's clips (M2-FP-07) → M1-ART-06. Log: `characters.md` on its branch.
- **Permissions:** `.claude/settings.json` allow-lists the read-only checks and cross-session messaging (the human's directive). Sessions pick it up after merging the integration branch.

### 3a. Standing queues (2026-10-24, also sent by message; messages can arrive hours late, so this section is authoritative)
- **m2-slice:**
  0. CMB-05 reconciliation: take the integration branch's mechanics (rolled absorb, HP 100%, rate 150), keep the FP-17 wiring, remove `call_ilun` (UI-05's Call row is merged), do M2-CMB-06.
  1. M2-FP-22, M1-UI-11, M1-ENV-11.
  2. M2-FP-20, M2-FP-21.
  3. M2-ENV-04 (wake-shell wall), M2-ENV-03 (shrine interior kit).
  4. M2-UI-06 (shop and inn).
  5. zone_weather.json rows for first_verse, shell_shrine and Haluna-night.
  6. Swap the capsules for Rhen, Toma and the villagers when the characters branch merges.
  7. Another playthrough pass.
- **characters:**
  0. **TOP PRIORITY (the human, 2026-10-24): M1-CHR-14.** Asha's braid is detached from her head; clothing and staff clip; some limbs look detached. Fix it properly and add automated guards; same checks for Rhen and Toma.
  1. M1-CHR-13 (vest normals, plus the shared `_panel` winding fix; rebuild Asha, Rhen and Toma).
  2. M1-RND-25 (the inner lip onto the mouth material).
  3. Toma follow-ups, plus Toma's clips.
  4. M2-CHR-03 (the Haluna villagers: Neme, Osu, Pila, the lane child, plus 3 generic).
  5. The CHR-12 smile §12.4 as a switchable variant, for the human.
  6. Battle-scale hero LODs.
- **pc-gpu:** the ADR 0029 follow-ups (no threaded loads) → the slice perf sweep → M1-QA-09 (Asha re-check, after CHR-12 merges) → the night GPU cost at Haluna H10 (M2-ENV-02) → the Low-preset storm cost (Low's full-res shells cost 1.36 ms against High's 0.66 ms compute; file it).
- **Wake-ups:** the hourly routine `trig_01LJyLo42xCq3WVmAza3BMhe` FAILS with ACCESS_DENIED (as in the old account). The Lead keeps a background `sleep 2700` heartbeat in its own session instead, and re-arms it on each wake.

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
**The live list is in [`lead-cloud.md`](lead-cloud.md) § "Exact next step"**, updated after every merge batch. As of 3e59f8d:
1. Merge `gpu/m2-rnd-04-drownbell-vfx` (built on RND-03, which is merged). Add the pending shots (drownbell_flood, underwater_below/window/waterline) to shots.json, approve them on lavapipe after viewing, and merge.
2. m2-slice does M2-FP-17 (the real Ilun call) now that CMB-05 is in. The steps are in handoff combat-13.
3. Review sweep Q over the review column.
4. Keep ~3 local agents busy on M2 work (M2-UI-05 Vowbound HUD, M1-ENV-10, ...). The PC queue was topped up 2026-10-24; message it when it reports two items left.
5. When the characters track lands M1-CHR-12, the PC does M1-QA-09, and then M1-LEAD-01 waits only on the human's music listen.
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
