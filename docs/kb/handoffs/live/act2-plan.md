# Live log: act2-plan

Branch `claude/act2-plan`, cut from the integration branch `claude/new-session-mj8c3c` @ 57ba06b2 (2026-10-30).
Lead: `session_01Bg3iP7cPGyjbX4CyniBahc`. Mandate: ADR 0203 §"Preparation now" (a planning session; **docs only**:
no game content, scene, asset, data table or test changes while ADR 0041 stands).

## Scope
- `docs/kb/plan/act2_plan.md`: the Act II work list (Ch10–Ch16), the inventory summary, the critical path, the risks, the task index.
- `docs/kb/plan/act2_inventory.md`: the branch-by-branch evidence for the inventory.
- `docs/kb/plan/act2_tracks.md`: the **proposed** track split, ownership globs and SESSION-BRIEFS rows (the Lead applies them).
- `docs/kb/tasks/M4/M4-A2P-*.md`: 67 gap tasks, `status: blocked`, `blocked-by: ADR 0203`.
- **Id block:** `M4-A2P-001`…`M4-A2P-199` (no other branch uses the `A2P` prefix).

## NEW ACCOUNT (from 2026-10-25)
- 2026-10-30: plan and track-split drafts committed.
- 2026-10-30: inventory (every `origin/claude/*` branch), 67 tasks, critical path and risks done. See MERGE-READY below.

### LEAD-ASKs (each has a default the plan already uses; overrule any)
- LEAD-ANSWERED: **The gate's flip list** (act2_plan §3): 58 ADR-0041 tasks go to `todo`, 18 Act III ones stay blocked, and 3 close (M3-AUD-804/805 superseded; M4-AUD-1001 already satisfied). M3-CRE-649 is split (Kesh's sheet is Act II, now M4-A2P-057). M3-AUD-837 is tooling. Confirm the list?
- LEAD-ANSWERED: **Merge the three Act II commits** that are only on track branches (`e1db6170` kirru_roost determinism; the rim_crawler rebuild `2224e784`/`c3f61ea6`; `6b399185` grounding), in the gate's first batch, before anything is rebuilt. Default: yes.
- LEAD-ANSWERED: **The tracks** (act2_tracks.md): add a **story** track (the seven beat sheets and scripts are the long pole); rename slice-polish → **cinematics**; fold combat into chapters and progression into chapters plus ui-menus; start eight tracks on day 1. Apply the ownership rows and narrow act1-chapters' `ch1[0-9]` glob?
- LEAD-ANSWERED: **Beat sheets out of order:** the story track writes Ch10 first, then **Ch14 and Ch15** (the wedding and the reveal: M4's named set piece and the characters track's longest lead), then Ch11–13 and Ch16. The chained `depends_on` in M4-C1x-01 stays; the Lead waives it for Ch14/15. Default: yes.
- LEAD-ANSWERED: **Design defaults** (Narrative and Combat confirm):
  - (a) Lowlight's sanctum is walked to a ledge and seen underwater, not swum;
  - (b) the wedding trap is a step-hold set-piece battle on the water-steps (ADR 0100's schema) before the barge escape;
  - (c) after the heresy, Order shrines go dark and refuse, and Saltwright and Kirru places keep working;
  - (d) the flat-engine is a breakable part with a timeline entry row, not its own combatant;
  - (e) the storm's waking at the Choir is a `scripted_escape` set piece.
- LEAD-ANSWERED: **Human item (environment):** `lfs.github.com` is denied, and `assets/audio/music/act2/**` is LFS. Act II's 14 unwritten cues can't be pushed as specified. Can the human allow the host? Default meanwhile: files under 5 MB go as plain blobs outside the LFS paths (TRACK-RULES), bigger ones wait in PC-QUEUE.
- LEAD-ANSWERED: **Human item (scope, SPEC §10.2):** should the cut list be put to the human for Act II now (Keth Pass folds into Quellan first, per act_outline's Cut Notes), or only if Act I's velocity data says so? Default: no cuts; revisit after Ch12.
- LEAD-ANSWERED: M4-A2P-100 (`placeholder_audit.py --act 2`) is tools work that ADR 0203 allows **before** the gate. Hand it to integration-qa now as `todo`? It's filed `blocked` like the rest.

### MERGE-READY
- MERGE-READY @ b470c65b: the Act II plan (act2_plan.md, act2_inventory.md, act2_tracks.md proposed), 67 M4-A2P tasks blocked by ADR 0203, LEAD-ASKs above; integration @ 89021833 merged in. Checks run: validate_data 0/0, taskboard --check clean, banned-terms grep over every new file clean. Checks skipped: Godot, lint, format, dlgc, tools tests (docs only; no code, data or dialogue touched).
- BACKLOG EMPTY: every deliverable in the brief is done (plan, inventory, tasks, track split, critical path and risks); the next steps are the Lead's (LEAD-ASKs). Act II content stays paused (ADR 0041) until the gate.

### Lead's answers (2026-10-30, by message)
1. The flip list is confirmed as written.
2. The three commits merge in the first batch after the gate.
3. The tracks are approved; the Lead applies the ownership rows at the gate, not before.
4. Beat sheets out of order: Ch10, then Ch14/15; the chained depends_on is waived for Ch14/15.
5. Design defaults (a)–(e) are accepted (Narrative and Combat confirm in review).
6. LFS: asked of the human; the default stands meanwhile.
7. No cuts now; revisit after Ch12 with velocity data.
8. M4-A2P-100 is `todo` now, integration-qa's.

**Next (the Lead's assignment):** draft beat sheets, marked `draft: pre-gate`, docs only: Ch10, then Ch14, then Ch15.
- MERGE-READY @ f6f406fa: `docs/kb/story/beats/act2_ch10.md` (draft: pre-gate; M4-C10-01's sheet, not yet reviewed). Checks: validate_data 0/0 (banned terms over docs/kb/story), taskboard --check clean. Skipped: dlgc (no .dlg), Godot (docs only).
- MERGE-READY @ a273058e: `docs/kb/story/beats/act2_ch14.md` (draft: pre-gate; M4-C14-01). Proposes the names Commander Brannoc Hale and Warden Dask, and "Outside the Level" as the heresy's words (banned-terms clean). Lead review asked (IP-echo-sensitive). Checks: validate_data 0/0. Skipped: dlgc, Godot (docs only).
- MERGE-READY @ 4821524b: `docs/kb/story/beats/act2_ch15.md` (draft: pre-gate; M4-C15-01): Kerrid's confession uses ADR 0020/0022's fixed lines verbatim. Open questions: Tobin's light caught in a Saltwright lamp (§10.1), the dock-master named Aldous Varrow, the word "Stilled" in K15. Ch14 gains Tobin's held motes at his death (ties to Ch15). The M4-C10/C14/C15-01 task notes point at the drafts. Checks: validate_data 0/0, taskboard --check clean. Skipped: dlgc, Godot (docs only). Next: Ch11, Ch12, Ch13, Ch16 drafts in that order (the Lead's order).
- MERGE-READY @ 8594451a: `docs/kb/story/beats/act2_ch11.md` (draft: pre-gate; M4-C11-01). Ch15's Hollowmere watch corrected: Liss's Ch11 line names Dace's ship, so only the hull stays closed until Ch17. Checks: validate_data 0/0. Skipped: dlgc, Godot (docs only). Next: Ch12.
- MERGE-READY @ 18bf1e77: `docs/kb/story/beats/act2_ch12.md` (draft: pre-gate; M4-C12-01). Checks: validate_data 0/0. Skipped: dlgc, Godot (docs only). Next: Ch13.
- LEAD-ANSWERED (2026-10-30: the default; filed as M4-A2P-059, creatures-b, blocked by ADR 0203): **The Avalanche Ram's ice vs ADR 0015.** avalanche_ram.md (built, M3-CRE-624) has ice plates and icicles on its fleece; ADR 0015 and keth_pass.md say no ice in any temple **or set piece** from Ch12 to Ch15. Default in act2_ch12 §10.1: creatures-b swaps the ice for wet, matted, seep-lit wool at the gate (a materials change, not a rebuild). Or rule a creature's frosted fleece on an open mountain as weather?
- MERGE-READY @ 15f641de: `docs/kb/story/beats/act2_ch13.md` (draft: pre-gate; M4-C13-01). §10.2 asks the Lead whether the ledger phrase "the heart sung in" spends the Choir early. Checks: validate_data 0/0. Skipped: dlgc, Godot (docs only). Next: Ch16.
- MERGE-READY @ 4a1602ae: `docs/kb/story/beats/act2_ch16.md` (draft: pre-gate; M4-C16-01). **All seven Act II beat sheets are drafted** (Ch10–Ch16, about 4,600 words written, 3,300 on the critical path). A cross-check finds every flag a draft reads declared in a draft, in Act I's sheets or in flags.tres. Checks: validate_data 0/0, taskboard --check clean. Skipped: dlgc, Godot (docs only).
- LEAD-ASK: **Review flags across the drafts** (each has a §10 with its open questions; defaults are in the text):
  - Ch15 §10.1: Tobin's light is caught in a Saltwright lamp at the pyre-raft (plants Liss's Act III), or goes out on the tide?
  - Ch16 §10.3: Sefir's one word to Kerrid, "Captain."; keep, or is it too close to naming the dead?
  - Ch13 §10.2: the ledger phrase "the heart sung in"; does it spend the Choir truth early?
  - Ch16 §10.5: act3_ending H03 says Sefir "raises Kesh from the stones" in Ch21, but Ch16 binds her to Asha; Act III's to reconcile.
  - Names proposed (banned-terms clean): Commander Brannoc Hale, Warden Dask, the dock-master Aldous Varrow, the Kirru eldest Owa (or unnamed); "Outside the Level" as the heresy's words.
- BACKLOG EMPTY (2026-10-30, second pass): the plan, the inventory, the tasks, the track split, the critical path and all seven Act II beat-sheet drafts are done and pushed. The rest waits on the Lead's review or the gate: no .dlg or game data before it (the Lead's instruction).
- MERGE-READY @ a3c86c7a: M4-A2P-059 (the Ram's ice to wet wool; creatures-b; blocked by ADR 0203), the Ch12 §10.1 answer recorded, and the plan's pointer to the lane docs in docs/kb/plan/act2/<lane>/ (none on the integration branch yet). Checks: validate_data 0/0, taskboard --check clean. BACKLOG EMPTY again.

### ADR 0204 applied (2026-10-30)
- MERGE-READY @ f9f8c709 (+ the next commit for the tasks):
  - every Act II draft now follows ADR 0204: Owa named; Tobin's light caught and the lamp cracked; the Wakefin is one animal, with `sound_dive` as evasion up and `close_circle` kept; the ledger phrase is a torn fragment; the Ram's `torn_fleece` in wet wool; snow and grit on the Ch12 regulars; `battle_heretic` from Ch14; the `hush_first_verse` and `ysolde_theme` reprises; ORDER_HUM sung once; Kesh at 4.2 m in battle; the Lamp Engine's two dormant crawlers; Nhoa copies ordinary skills only;
  - M4-A2P-056 (no Ansedra wildlife) and M4-A2P-090 (`tobin_pyre` withdrawn).
  - Checks: validate_data 0/0, taskboard --check clean.
- Depth check: all seven drafts have the same 11 sections at 5,600–8,700 words. Ch11, Ch12, Ch13 and Ch16 aren't thinner than Ch10, Ch14 and Ch15, so none was expanded.
- In progress: the consistency pass across the drafts and the six lane-doc sets on the track branches.

### Consistency pass (2026-10-30)
- MERGE-READY @ 8d430289: `docs/kb/plan/act2_consistency.md`, about 90 rows (names, flags, cast, ADR 0204, facts, drafts against each other), each with an owner.
  - The act2-plan-owned rows (D1–D7, plus the drafts' side of A3 and P14) are fixed.
  - `tools/banned_terms.txt` gains `Farplane` (its own commit; case-sensitive, so it doesn't hit `FarPlane` node names).
  - Checks: validate_data 0/0, taskboard --check clean. Skipped: Godot (docs only).
- LEAD-ASK: **Route the lane mismatches** (rows in act2_consistency.md by owner):
  - **chapters** (act1-chapters), 23 rows:
    - its flags are renamed copies of the drafts' §3 flags, including `act2_complete` against `ch16_act_two_complete`, `ch15_kerrid_revealed` against `ch15_kerrid_told`, and the set-piece ids;
    - Ch14: Tobin dies after the steps (the draft has him die before them); no Toma lock and no Liss `unavailable`; Liss locked for Venn (ADR 0204 §8 says a lent skill);
    - Kerrid is inside Reedhollow, walks the city by day, and the pact is staged with Sefir instead of at the moorings;
    - the Ram's hazard is snow.
  - **creatures-b**, 13 rows:
    - the Abiding guard's sheet still allows them to be revenants (ADR 0016: no revenant fought openly before Ch19, so living);
    - the Wakefin's `sound_dive` is untargetable (ADR 0204 §3: evasion up);
    - `wakefin_breaching` is unmapped;
    - Venn boards at 50% before the engine breaks;
    - the storm is a guard phase (the draft has the `ch16_storm_wakes` set piece);
    - the Ram's hazard is snow.
  - **creatures**, 3 rows: `ridge_lynx` and `scree_crawler` still have frost (ADR 0204 §2); `rime_urchin`'s ice-crust base breaks Ch11's no-frost rule.
  - **ui-menus**, 8 rows:
    - "Heretics of the Level" should be "Outside the Level";
    - nine codex unlock flags are never set;
    - Kerrid's flag should be `ch15_kerrid_told`;
    - the Ram's hazard is snow.
  - **audio**, 11 rows:
    - a new `ysolde_confession` cue (ADR 0204 §12 says reprise `ysolde_theme`);
    - `kesh_bound`'s element order;
    - `kerrid_at_sea`'s length (about 7–8 min of scene);
    - the Ram's hazard is snow.
  - **env-art-b**, 7 rows: Kerrid at the Sanctum vestibule (he never enters the Sanctum); shot ids reused from the drafts for other frames.
- BACKLOG EMPTY: the Lead's item is done: ADR 0204 applied, the depth check passed, and the consistency pass is logged with owners. Lane fixes belong to their tracks.
