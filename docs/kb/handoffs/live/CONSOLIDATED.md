# CONSOLIDATED HANDOFF: start here

**Last updated:** 2026-10-23 ~23:00 UTC by the Lead (cloud session `session_01Bg3iP7cPGyjbX4CyniBahc`).
A new account, Lead or environment should be able to resume from this file and the files it links. Keep it current after every merge batch (CLAUDE.md §7a).

## 1. What this is
*Hymn of the Undertow* is an original, cinematic, turn-based RPG in Godot **4.6.3** (Forward+, typed GDScript). [`SPEC.md`](../../../SPEC.md) is the brief; it is at v1.1 and only the Lead edits it. [`CLAUDE.md`](../../../CLAUDE.md) holds the operating rules and applies to every agent. Project state is in [`docs/kb/STATUS.md`](../../STATUS.md), and decisions are ADRs 0001–0022 in [`docs/kb/decisions/`](../../decisions/).

**Milestone: M1 (Tech & Look Prototypes)**, about 70% of its tasks done. See `python3 tools/taskboard.py`. Exit criteria (SPEC §10.2):
- CTB battle sandbox ✅
- water ✅
- glimmer ✅
- Undertow prototype ✅ (perf solved: 3.95–5.35 ms at High 1440p on an RX 9070 XT)
- five-shot mood test ✅ (M1-ENV-01, Art and Rendering approved)
- **one hero at final fidelity 🔄**: Asha, M1-CHR-04 and M1-CHR-07. She still fails the SPEC §14 dialogue-range review: the smile doesn't drive cheeks or lids, the lips lack a cupid's bow, the hair edge is wrong, plus shadow banding and a plastic-looking vest.

After that, the Lead does the M1 review (M1-LEAD-01), then M2, the vertical slice, which is a blocking human review (SPEC §16 Q7).

## 2. Branches
| Branch | Owner | Role |
|---|---|---|
| `claude/new-session-mj8c3c` | Lead (cloud) | **The integration branch**, standing in for `main` (see ADR 0008: the local gate replaces GitHub Actions, which never runs). All merges land here. |
| `claude/first-playable` | First Playable cloud session | Builds the first playable minutes. The Lead merges it. |
| `gpu/*` | PC GPU session (the human's Windows PC, RX 9070 XT, Remote Control) | One branch per item. The Lead merges each when it's done. |
| `lead/integration` (local worktree only) | Lead | Fast-forward copy of the integration branch, used to run the full gate without blocking the main checkout. |

**Merged `gpu/*` branches:** results-2026-10-23, rnd-10, rnd-09, rnd-08, rnd-07, rnd-11, qa-05, rnd-12-sky, chr-04-materials.
**Open `gpu/*` branches still to merge:** `gpu/m2-rnd-01-undertow` (doing), plus any newer ones.
**`claude/first-playable` was merged at 823ad11. THE FIRST PLAYABLE THREAD WORKS END TO END;** see [`docs/PLAYTEST.md`](../../../PLAYTEST.md). The PC session is preparing `C:\Users\Aaron\Hymn_Playtest\PLAY.bat` for the human.

## 3. Environments and sessions
| Environment | Session | What it does now | Its live log |
|---|---|---|---|
| Lead, cloud (4 CPUs) | `session_01Bg3iP7cPGyjbX4CyniBahc` | Orchestrates, merges, reviews (fresh reviewer agents, one "sweep" per batch), runs the full gate, approves baselines on lavapipe | [`lead-cloud.md`](lead-cloud.md) |
| PC GPU (Windows, RX 9070 XT, official Godot 4.6.3) | `session_01778wbLbDFnRRLTKjnawv3T` (Remote Control; it cannot message back, so read its transcript or branches) | Standing queue, in order: CHR-04 materials and shadows → RND-12 sky tiers → M2-RND-01 Undertow production → ENV-03 vegetation → perf sweep → RND-15 prewarm and ghosting measurements → RND-17 dusk motes → RND-18 SSS crest fade. Its progress file is `docs/kb/qa/gpu/2026-10-23-pc-queue-progress.md` on its branches. | [`pc-gpu.md`](pc-gpu.md) |
| First Playable, cloud (own container) | `session_01ELR13ohWMPrprcpcgLa7UR` | **Thread done and merged.** Its new queue: cutscene skip, the Haluna load hitch, battle-loss retry, the Drownbell two-phase boss, an animation request for Character, and keeping PLAYTEST.md current. The original thread was boot → title → New Game → Prologue → Ch2 beach → playable Haluna → villagers → first battle → shrine save → Ch3 end card, plus `docs/PLAYTEST.md` for the human. Its progress is in `docs/kb/handoffs/first-playable-progress.md` on its branch. | [`first-playable.md`](first-playable.md) |

**Rules the human set for environments:**
- Keep every environment busy; give it a standing queue rather than one task at a time.
- The PC may run parallel work as long as **total CPU, memory and GPU load stays at or under about 75%**. GPU benchmarks run one at a time.
- Skip gate steps that can't catch anything in the diff (CLAUDE.md "Gate scope").
- Keep these handoff logs current.

## 4. In flight (Lead's own subagents, in local worktrees of the Lead's container)
These are lost if the container restarts. Re-launch from the task files if so.
- **M1-CHR-07:** Asha face round 3. The smile driver gap comes first; then lips, hairline, black hair and brows.
- (ARC-14 and NIT-01 merged at 823ad11.)
- ci27 failed: cloth.tres had been hand-edited on the PC. Fixed at 6e09360, where the values now live in write_materials.py.
- ci28 drift was expected: the haluna_h0* shots were re-approved at 23f0c79 (palette checks OK), and the asha_face_* shots were superseded by CHR-07's own re-approval.
- M1-CHR-07 is merged at d7d56ea. It fixed the smile driver: missing morph normals and too-weak shapes. A new test, tools/tests/test_asha_face_drive.py, covers it.
- **Running:**
  - ci29, a scoped confirm of the haluna and asha shots;
  - review sweep K1 (the M2-FP thread, ARC-14, NIT-01, RND-12, RND-15, QA-05);
  - M1-CHR-09, Asha hair round 4 (crown shell, face-framing lock, lip thickness, doll-like eyes).
- **Rule learned:** Asha's materials change only through write_materials.py.

## 4e. Latest (Lead, ~23:00 UTC)
- **Merged:**
  - M2-ARC-01 + M2-CMB-01 (save **v6**, Swell inputs for all four heroes, unlocks, Swell in the sim): 5b6243a;
  - M1-ART-02 (post-import scripts): 99d2b26;
  - M1-RND-19 (shader-tier copy-on-swap): 1ed245b;
  - M1-CHR-10 (Asha round 5: black hair per ADR 0024 *proposed*, lashes, lid, brows, teeth, mouth normals): 3907e54.
- **Pending merge:** M2-UI-01/02 (the UI agent is resolving conflicts with M2-CMB-01 in battle_controller, battle_menus, swell_timing_ring, formulas.md and strings.csv).
- **Asha:** still fails strict §14 at dialogue range, with diminishing returns per round. **Asha rounds are paused** until the PC's 2x GPU capture (M1-QA-05c) and the human's playtest impression. If both say no, take ADR 0019's stronger-stylisation path and decide it with the human.
- **PC queue front:** QA-05c, then RND-20 (smile-corner terminator), then the rest.

## 4d. Earlier (Lead, ~21:15 UTC)
- **Merged:** M1-NIT-02. The coverage baseline is ratcheted: battle 99.93%, progression 96.52% (4c462ee).
- **Lead subagents running:**
  - M1-CHR-10 (Asha round 5);
  - M1-ART-02 (post-import scripts);
  - M2-UI-02 + M2-UI-01 (Read panel, bestiary menu, Swell mode menu);
  - M2-ARC-01 + M2-CMB-01 (Swell carry into **save v6**, unlocks, the other heroes' inputs, Swell in the sim).
- **Save versions:** v6 is owned by M2-ARC-01. The First Playable session was told not to bump it.

## 4c. Earlier (Lead, ~20:30 UTC)
- **The full gate is green at fc3940c (ci30):** 1,063 tests, 60/60 shots, Blender --all byte-identical, and the known-failure list is EMPTY.
- **Merged:**
  - M1-CMB-03 (Read, bestiary, save **v5**, openings; ADR 0023);
  - the integration batch (ENV-05, ENV-06, RND-13, RND-16 API, UI-09);
  - the Blender pipeline set (CHR-05, CHR-06, RND-14, ENV-07).
- **Sweep L1 closed 11 tasks.** Board: 86/107.
- **Lead subagents running:**
  - M1-CHR-10, Asha round 5: black hair, lashes and lid band, brows, teeth, mouth normals, skin lighting;
  - M1-NIT-02, the sweep-L nits.
- **Next:** when CHR-10 lands, the PC makes a 2x High GPU capture as the §14 final judge (file it as M1-QA-05c). The M1 review (M1-LEAD-01) follows once Asha passes or the human accepts the ADR 0019 stylisation.

## 4b. Earlier (Lead, ~19:00 UTC)
- **Merged:**
  - sweep K1 at 7f4c76b: M2-FP-01 to 04 closed; PLAYTEST.md fixed;
  - M1-CHR-09 at 20082e3: Asha crown clumps, temple lock, lips, eye whites; LOD0 at 62,290.
- **Asha:** the Lead judges her not yet at final fidelity at dialogue range. She reads as polished CG, and the costume is still glossy. The GPU re-check (PC, QA-05b) and the human's playtest are the next judges. The human question is recorded in STATUS.
- **Lead subagents now running** (local worktrees):
  - M1-CMB-03 Read/bestiary/ambush;
  - the Blender pipeline set (CHR-05, CHR-06, RND-14, ENV-07);
  - the integration batch (ENV-05, ENV-06, RND-13, RND-16, UI-09).
- **First Playable session queue:** cutscene skip, load hitch, loss retry → M2-FP-05 thread hardening → M1-ARC-15 (presets never applied in play) → Drownbell boss → animation request.
- **PC queue:** M2-RND-01 Undertow production → ENV-03 → perf sweep → RND-15 prewarm and ghosting → RND-17 → RND-18 → QA-05b Asha GPU recheck; plus refresh the playtest copy (PLAY.bat).

## 5. Exact next steps for a Lead
1. `git fetch origin` and merge every finished `gpu/*` branch and `claude/first-playable` into `claude/new-session-mj8c3c`.
   - Resolve append-only conflicts with `python3 tools/dev/merge_union.py <file>`.
   - For other files, keep both sides. Never commit conflict markers; check with `grep -c '^<<<<<<<'`.
   - Run validate_data and unittest after each merge. Branches from the PC have twice missed a loc key or tripped the validator.
2. Run the full gate in the `lead/integration` worktree (`HYMN_LOG_DIR=... tools/ci_local.sh`, about 60–90 min on 4 CPUs). Look at every failing shot side by side before copying `tests/screenshots/out/<id>.png` to `baselines/`.
3. After each batch, send a fresh reviewer agent over every `status: review` task. Close a task on "approve" or "approve-with-fixes", and file the fixes as new tasks. Reopen it on request-changes.
4. Keep the PC GPU session and the First Playable session fed; check `get_session` and `list_events`.
5. When CHR-04 and CHR-07 pass §14 honestly, run M1-LEAD-01, the M1 review, then plan M2.

## 6. Open questions for the human (also in STATUS.md)
- **Music:** listen to the three cues (docs/kb/audio/listening_notes.md, §16 Q3). AUD-01 and AUD-02 wait on this.
- **Git LFS:** may it be enabled? Baselines and assets are growing, and the 5 MB file cap is binding for character GLBs and textures.
- **GitHub Actions:** runs never leave `queued`; check the repo's Actions settings.
- **Reefball arena form:** the default is to keep it.
- **Answered:** Q2 (MPFB2 CC0 data allowed, ADR 0021); the prologue line replaced (SPEC v1.1).

## 7. Toolchain and gotchas (read before running anything)
**Getting the tools:**
- Godot 4.6.3: `python3 tools/dev/fetch_godot.py` (from the Ubuntu archive; GitHub releases are blocked).
- Blender 5.0.1: `python3 tools/dev/fetch_blender.py`.
- Software render (lavapipe and Xvfb): `python3 tools/dev/fetch_render_deps.py` (ADR 0009). Baselines are **lavapipe**; never approve GPU captures as baselines.

**Shared-machine safety:**
- Never kill processes by pattern (CLAUDE.md §8a).
- Godot `user://` is isolated per run via `XDG_DATA_HOME`.
- Parallel full gates overload 4 CPUs.

**Blender gate:**
- Thread counts are pinned per job: 1 for base_body and vegetation, 4 for the others.
- Known failures: base_body (M1-CHR-05) and shader_test (M1-RND-14).
- With no `main` ref, set `HYMN_BLENDER_BASE=<base sha>`, or it rebuilds every job (about 6 min).

**IDs and numbers:**
- Task-id and ADR-number collisions happen when parallel agents create files. Check them on every merge (this happened with ADR 0016/0017 and with RND-12; CHR-03 is currently duplicated).
- Valid task roles are listed by `taskboard.py --check`. Use `character`, not `art`.

**Restarts and timeouts:**
- Scheduled `send_later` check-ins failed with ACCESS_DENIED after the trust elevation, so don't rely on them.
- Container restarts kill local worktrees' background agents. Results survive only if they were committed in the worktree.

## 8. Where things are
- **Story:** docs/kb/story/ (bible, act_outline, characters, beats) and ADRs 0015–0017, 0020, 0022. These are IP-echo re-stagings; the guardrail is strict.
- **Art:** docs/kb/art/ (palette.json, color_script.md, characters/asha*.md).
- **Tech:** docs/kb/tech/ (architecture, field_camera, dialogue_format, battle_ctb, ui, water, glimmer, undertow).
- **GPU reports:** docs/kb/qa/gpu/.
- **Per-task handoffs:** docs/kb/handoffs/2026-10-23-*.md.
