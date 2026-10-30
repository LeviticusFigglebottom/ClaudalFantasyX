# CONSOLIDATED HANDOFF: the new Lead starts here

## STATE 2026-10-30 00:25 UTC
- **The PC is back** (`session_01UPFyEABtMznCLCcXCPdmda`, desktop-jj0o43o) and briefed: Act I real-GPU QA pass 3 on lead/gate-big18 → `gpu/act1-qa-3`, every track's PC-QUEUE item, the Act I perf budget, its own RND work, and the Blender verifies. Cloud gate sessions keep running the batches.
- **ADR 0203:** Act II starts the moment Act I passes the completion gate. That means the audit at zero, the continuous playthrough, a green batch with main fast-forwarded, no open Act I real-GPU rows, and hitches in budget. Evidence goes in `docs/kb/qa/act1_complete.md`, plus the tag `act1-complete`.
  - Prep under way: the act2-plan session `session_01UPFyE8YdUYQ5LuuhgfZtqS` (docs only) writes `docs/kb/plan/act2_plan.md`, `act2_tracks.md` and the M4 tasks (blocked-by ADR 0203).
  - integration-qa adds `placeholder_audit --act 2` and an Act I gate checker.
- ADR 0202: the status names. M3-CIN-1233: New Game plays Act I continuously, and the slice's end card becomes a Ch4 chapter card with the credits moved to the end of Act I (slice-polish, big19).
- LFS uploads are blocked by the network policy (`lfs.github.com`). The human has been asked to allow it; meanwhile small binaries go in as plain blobs.

## STATE 2026-10-29 21:30 UTC (Lead `session_01Bg3iP7cPGyjbX4CyniBahc`)
- **big17 is merged** into `claude/new-session-mj8c3c` @ 96222b30, ahead of its shots, at the human's request to play it now.
  - The non-render checks are green except 5 suite reds: 4 pre-existing (routed: env-art ×2, creatures, env-art-b) and Pell's portrait (fixed on claude/ui).
  - big17's shots are capturing in the gate session `session_01UPFyE6NmbMsX7kaGj7ousX`, with GATE-DONE expected around 01:00–03:00 UTC. The Lead then approves the baselines, commits them to the integration branch and posts `BASELINES big17 APPROVED @ <sha>` in lead-cloud.md.
  - `main` is not fast-forwarded until a batch is fully green, shots included (ADR 0042).
- **big18:** the gate session `session_01UPFyEAXofxWazWNnRTzFGJ` builds `lead/gate-big18` from the integration branch plus every track head, runs the non-render checks now, and captures shots after the big17 baselines are approved. Its log is `gate-big18.md`.
- **Decisions today:** ADR 0201 (Pell's niche wording, SPEC v1.5, `i:blue mage` banned).
  - Battle-presentation took combat's M3-C05-06 and M3-C06-05 (the Kerrid and Liss Swell techniques).
  - creatures and creatures-b were started.
  - act1-chapters' duplicate M3-CRE-627 request becomes M3-CRE-700.

## TAKEOVER 2026-10-29 (Lead `session_01Bg3iP7cPGyjbX4CyniBahc`). This overrides §0–§4 where they differ
- **Integration branch: `claude/new-session-mj8c3c`**, fast-forwarded to `claude/undertow-lead-handoff-ze8rrn` @ 4d64a73e. That is the only branch this Lead can push, so -ze8rrn is retired. Tracks merge `origin/claude/new-session-mj8c3c`.
- **The PC is OFFLINE for an extended period** (the human). Nothing waits on it:
  - **Tracks self-render** their own changed shots (TRACK-RULES "FROM 2026-10-29").
  - **Batch gates** run in a dedicated cloud **gate session**, which builds `lead/gate-bigN`, runs the full `tools/ci_local.sh` and publishes `lead/gate-bigN-shots`. The Lead views every shot, approves and merges.
  - **GPU-only work waits** under `### PC-QUEUE` lines in each track's log and in pc-gpu.md: real-GPU QA rows, perf, benchmarks, and the PC's unfinished M2-RND-01, RND-22, M2-RND-02/03/04. When the PC returns, the Lead sends it the PC brief plus that queue.
- **big16 was never gated:** `lead/gate-big16-shots` doesn't exist. **The next batch is big17** = `lead/gate-big16` @ ff82858c, plus the current heads of env-art, characters (Pell), creatures, battle-presentation, ui, hero-integration and m2-slice. Already in big16: env-art-b, creatures-b, act1-chapters, audio.
- **Sessions created on 10-29:** the 8 "start small" tracks from SESSION-BRIEFS.md, plus the gate session. Ids are in lead-cloud.md.

**Handover:** 2026-10-28 ~18:30 UTC, from Lead `session_018aiGwGLGkxsnMnu8VfCu1m` (old account, out of usage). It is written for a **new Lead on a new account with no context**. At handover only two sessions exist: you (the new Lead) and one remote session (the human's PC, via Remote Control). You recreate every other environment yourself, as §4 says.

The previous version is `CONSOLIDATED-history-2026-10-28.md`. It has the deep history, the toolchain gotchas (its §7) and the old roster.

---

## 0. Your first hour (in order)
1. Read CLAUDE.md (binding) and this file. Then read `TRACK-RULES.md`, `SESSION-BRIEFS.md`, ADR 0041 and ADR 0042 (`docs/kb/decisions/`), and `lead-cloud.md` (your own log; append to it).
2. Run `git fetch origin`. **Integration branch: `claude/undertow-lead-handoff-ze8rrn`.** It's the "playable branch" the human tests. `main` lags behind it, and you fast-forward `main` after each fully green batch (ADR 0042).
   - The new account gives you a new session branch. You can either keep using `claude/undertow-lead-handoff-ze8rrn` as the integration branch (preferred, since every track merges from it), or fast-forward yours to it and announce the change in this file. Never rewrite history.
3. Find the PC session: `list_sessions` (environment_kind `bridge`). Send it the PC brief from SESSION-BRIEFS.md, with your session id, and **the big16 gate request** (§2).
4. Create the cloud tracks from SESSION-BRIEFS.md, starting with the 8 the "start small" line names.
5. Arm your 20-minute heartbeat (§3) and start the loop.

---

## 1. The game, as of now (honest)
- **What it is:** *Hymn of the Undertow* is an original cinematic CTB RPG in Godot 4.6.3. The scope is SPEC.md.
- **The human's directive (ADR 0041):** Act I as played (the title → the Prologue → the vertical slice → Ch1–Ch9) at FINAL quality: no greybox, capsules or placeholders. **Act II and later are paused.**
- **The playable branch is big13** (90ecee18 plus docs). It runs title → Ch9 end to end:
  - the CTB battles, Swell, Vowbound and statuses work;
  - Ch1–9 are mostly dressed;
  - the party and most foes are on real models.
- **Not merged yet (waiting in big16):**
  - all six Act I bosses and three Vowbound on real models;
  - named NPCs and village crowds;
  - fixes for the human's four playtest reports (big15/16; see the table below);
  - loads under 1 s (ADR 0111);
  - many art fixes;
  - the lore codex entries.
- **The human's four playtest reports, verified on the GPU on big15:**

  | Report | Status |
  |---|---|
  | The Prologue's colour | fixed |
  | The run reads grounded | fixed |
  | The beach staging (Asha toward Rhen, both faces) | fixed (two small rows open, owned by slice-polish) |
  | The party at the start | partly. Rhen is on screen, but the camera opens far back; integration-qa is fixing it |

  The human's crash ("Trying to cast a freed object" on entering a fight) is fixed on the integration branch (de5fdc6c).
- **What remains before Act I plays as intended:**
  1. Merge big16 (§2).
  2. Close the open rows in `docs/kb/qa/act1_gpu_qa.md` (on the PC's newest `gpu/act1-qa-*` branch; about 12 were open on big15) and in `docs/kb/qa/act1_final_inventory.md` (integration-qa's; about 44 items at last count, many fixed since).
  3. Pell's model (characters).
  4. A final GPU walk of title → Ch9 with nothing flagged.
  5. The human plays it.

  Estimate: two or three batches.

## LIVE STATUS (kept current by the outgoing Lead; newest at top)
- **22:50 UTC:**
  - PELL is MERGE-READY (claude/characters @ 3346484b; a second look-dev pass follows). Fold it in with big16, or with big17 if big16 is already gating.
  - big16 cloud gate: 533/~600 shots; the published results are expected within ~1 h.
- **21:30 UTC:**
  - PELL is built (claude/characters @ b51dcc3d) and in a look-dev pass before MERGE-READY.
  - big16 cloud gate: 396/~600 shots; the slow beach and Haluna crowd shots take 6–10 min each.
  - The integration branch now has HYMN_STEP_TIMEOUT 3 h by default (036245a7) and STALE-BRANCHES.md.
  - The PC is still offline.
- **19:40 UTC:**
  - The human's 4th fix (the PARTY START) is fixed on claude/hero-integration @ 5c11d034, re-rendered and viewed on big16. Fold that head into big16.
  - big16 cloud gate: 282/~600 shots.
  - characters is still on Pell.
- **19:20 UTC:**
  - big16 cloud gate: 238/~600 shots.
  - battle-presentation is MERGE-READY @ e641579e (the Ch8 Climb's camera cut with stair effects) and its backlog is empty.
  - characters is building PELL (M3-CHR-506).
  - integration-qa is rendering the party-start lane-turn fix.
  - The PC is still offline.
  - No open LEAD-ASKs.
- **18:45 UTC:**
  - The cloud gate of big16 (/home/user/wt/gate16 in the old Lead's container) had 171/~600 shots captured. Expect `lead/gate-big16-shots` around 22:00 UTC if the container survives. If that branch doesn't exist, re-gate big16 on the PC.
  - Every track is idle, with its Act I list done or waiting, except three just nudged: characters (Pell's model), integration-qa (verify or fix the party-start camera), battle-presentation (hook the Fisher Stair).
  - Track heads to fold into big16 before merging (all MERGE-READY):
    - creatures f6846325;
    - hero-integration a6e9d548 or newer;
    - env-art b68d1920;
    - env-art-b a5e650bd;
    - ui b2118f76;
    - m2-slice 595be6eb.
  - Any newer heads at your start supersede these.

## 2. In flight at handover: big16 (the next merge)
- **`lead/gate-big16` @ ff82858c** = big15 (`lead/gate-big15` @ 6466a6f5) plus every track head as of about 16:30, plus the Shell Shrine GI inputs re-recorded (no rebake needed; the new codex spot has no mesh or light).
- **big15 will not be merged separately.** big16 contains it. big15's cloud suite ran 3189 tests with 6 failures:
  - 2 were the cloud probe's exit 127 (environment; they pass on a rerun);
  - 4 were real and are fixed on the track branches: creatures f6846325 (crowd post-import scripts), hero-integration a6e9d548 (the follower face test), and env-art and m2-slice (already passing on big16).
- **The old Lead's cloud gate of big16** was running in its container: tools, then the Godot suite, then the full manifest, published to `lead/gate-big16-shots`. **If that branch exists, use it. If not, have the PC gate big16** (preferred), or run it in your own container (about 4 h on 4 CPUs).
- **To merge big16:**
  1. Merge the newer heads of `claude/creatures` and `claude/hero-integration` (and any others marked MERGE-READY since) into lead/big16. Rerun `--filter=post_import`, `hero` and `party`, plus validate_data and lint.
  2. Run `python3 tools/dev/lead/contact_grid.py <gate-run dir> <scratch>` and **VIEW every image** (Read tool). Never approve a black, broken or placeholder-looking shot blind. Note problems as owner rows.
  3. Run `python3 tools/dev/lead/approve_shots.py <gate-run dir>` in the batch worktree. It copies the out PNGs and writes the REAL lavapipe metadata; `compare.py --update-baselines` writes "?", which is wrong. Commit.
  4. Merge the batch into the integration branch with `--no-ff`. Run validate_data, taskboard --check, dlgc --check, gdlint and gdformat. Push.
  5. If the gate was fully green (the suite bar listed known reds, coverage ok, every shot viewed): fast-forward `main` (ADR 0042).
  6. Update this file's §1 and §2, tell the tracks to merge the integration branch, and tell the human what's merged in plain words.

## 3. How to run the project (the loop that works)
- **The 20-minute heartbeat:** run `sleep 1200; echo heartbeat` in the background (re-arm it every time it fires). On each wake:
  1. `list_sessions`: who is idle, blocked, or running.
  2. `tools/dev/lead/leadask.sh`: answer every new `LEAD-ASK:` line with `send_message`. Decide and don't stall. Tracks can't message you.
  3. Check the PC's newest `gpu/*` branch (`pc-gpu.md`) for gate results and QA rows.
  4. **Read an idle session's last result before you nudge it** (`list_events` kinds=result). Give concrete next work. If its list is genuinely empty, leave it idle; the account's 7-day usage was at its warning level.
  5. When enough MERGE-READY work has piled up (or a human fix lands), build the next batch (§3a).
- **Batches (§3a):**
  - **Build:** a local merge agent builds `lead/bigN` from the integration branch (or the last batch) plus every track head, using the conflict rules in the big15 and big16 merge-agent prompts. Those rules: append-only files via `tools/dev/merge_union.py` (then check duplicate PROVENANCE rows; validate_data must be 0/0); `baselines.json` via `tools/dev/lead/merge_baselines.py ours`; baseline PNGs ours; owners win their files; never let `docs/kb/qa/gate-runs/**` images in.
  - **Gate:** push as `lead/gate-bigN`, post `GATE-REQUEST lead/gate-bigN @ sha` in lead-cloud.md, and message the PC. It publishes `gpu/gate-bigN-shots`.
  - **Route** every failure to its owner with the exact message. Tracks fix on their branches; fold the fixes into the next batch.
  - **View**, approve and merge as in §2.
- **The human's playtest reports are FAST-TRACKS:** route each to its owner as top priority. If a track won't act on it, do it yourself with a local agent on a `lead/ft-*` branch.
- **Decisions are yours** (ADR 0042: the human delegated them). Record cross-role decisions as ADRs (next free number: 0043). Bring the human only what is truly theirs: hardware, accounts, money.

## 4. Environments to create (all in SESSION-BRIEFS.md)
| Env | Branch | State at handover |
|---|---|---|
| PC (Remote Control, `bridge`) | `gpu/*` | Offline since ~13:24 UTC; the human was asked to check it. Its last state: big15 lane B done (375 non-PASS of 593), Blender was running. Its newest log is on `gpu/act1-qa-2`. |
| env-art | `claude/env-art` | Active. Ch1 rows, the Underway walls fixed; checking U03 and the Oruvel booth orientation on big16. |
| env-art-b | `claude/env-art-b` | Active. Placeholder audit Ch5–9, the Fisher Stair prop, the Ebbing motes done. |
| characters | `claude/characters` | Named NPCs merge-ready; Pell pending; prop grips; the skirt (helper bones). |
| act1-chapters | `claude/act1-chapters` | Cameras, 36 cutscene walks and pacing done; playthrough list. |
| integration-qa | `claude/hero-integration` | The party-start camera, merge_union base-aware, M3-ARC-1326 (the Ebbing cue hook), trial merges. |
| slice-polish | `claude/m2-slice` | Beat audit; rows 31 and 32 (beach skirt clip, waist framing). |
| ui-menus | `claude/ui` | Loads done (<0.6 s); codex done; portraits as NPCs land. |
| battle-presentation | `claude/battle-presentation` | Boss intros, Ilun, Moll done; hook the Fisher Stair. |
| creatures / creatures-b / audio | their branches | Act I done. Start only if new rows appear. |

**Session quirks you will hit:**
- Tracks end their turns often. Nudge them with concrete work.
- Some sessions refuse a Lead message as an instruction. The preamble now says the Lead carries the human's authority. If one still refuses, replace it with a fresh session on the same branch (the live log carries the context), as slice-polish was replaced.
- Never let tracks use send_message or send_later (the prompts block them).
- Container restarts kill your local agents and background sleeps: re-arm the heartbeat.
- When the PC is offline for more than an hour, gate in your own container (a local agent; the prompts are in this file's history).

## 5. Open items and decisions log (latest)
- ADR 0041 (Act I first) and ADR 0042 (the delegated decisions):
  - M2 is approved;
  - the music stays self-synthesized;
  - Asha's face direction is kept;
  - no GPU clock cap;
  - `main` fast-forwards per green batch.
- Role seats with no track:
  - rendering → battle-presentation (battle VFX and effects.json) and env-art-b (zone looks);
  - narrative → ui-menus;
  - architect and tech → integration-qa.
- Ownership:
  - dressing: env-art for the Prologue–Ch4, env-art-b for Ch5–9;
  - act1-chapters: encounters, placement, cameras;
  - slice-polish: the cutscene side of the slice and Ch1;
  - capsules: party → integration-qa, villagers → creatures, named NPCs → characters.
- Git LFS is LIVE (ADR 0039) for `assets/audio/music/actN/**`, `assets/audio/sfx/act3/**` and `assets/lfs/**`. Run `git lfs pull` before importing.
- Known: big14-era coverage fails while the suite has reds. The suite takes ~45 min, so use HYMN_STEP_TIMEOUT=10800 (the default since 036245a7, merged from gpu/ci-step-timeout-3h).

## 6. Tools (`tools/dev/lead/`)
- **Branch hygiene:** `STALE-BRANCHES.md` lists ~79 merged or retired branches that are safe to delete. Cloud sessions get a 403 on deletes, so do it from the PC or in the GitHub UI.

- `leadask.sh`: scans the tracks' live logs for `LEAD-ASK:` lines.
- `contact_grid.py`: six contact sheets per image, for fast viewing.
- `approve_shots.py`: copies the out PNGs and writes the real baseline metadata.
- `merge_baselines.py`: the 3-way `baselines.json` merge during a conflicted merge.
- Plus `tools/placeholder_audit.py` (the Act I inventory), `tools/dev/merge_union.py` and `tools/ci_local.sh` (the full gate).
- The deeper toolchain gotchas are in `CONSOLIDATED-history-2026-10-28.md` §7. Read them before your first gate.
