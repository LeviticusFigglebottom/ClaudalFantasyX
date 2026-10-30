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

### Gate-commit prep (2026-10-30)
- MERGE-READY @ be30b8cc:
  - `docs/kb/plan/act2_consistency.md`: the rows grouped by owner in a routing table (chapters 27, creatures-b 17, creatures 4, ui-menus 12, audio 13, env-art-b 10; a row may list two owners). The drafts' own rows are all closed, including N7 `drowner_haul`, N8 "the Veil-First", N9/P15 `court_steps` and `peace_wedding_break`, and F10 the reads lists.
  - `docs/kb/plan/act2_tracks.md`, updated to the Lead's answers:
    - §3a: 11 ownership rows to append, paste-ready, with `<GATE>` as the date;
    - §3b: the narrowing edits (act1-chapters' row, which appears **twice** in ownership.md today; the m2-slice session renamed to cinematics);
    - §4a: the COMMON PREAMBLE's ADR 0203 rule;
    - §4b: the Act II track-briefs table (12 tracks, eight on day 1).
  - Checks: validate_data 0/0, taskboard --check clean. Skipped: Godot (docs only).
- BACKLOG EMPTY: all of the Lead's items are done. The rest is the gate commit (the Lead) and the lanes' consistency rows (owners).

### Story track: Act II scripts (from 2026-10-30, ADR 0205)
- MERGE-READY @ f068e5de: **Ch10, Ch14, Ch15 and Ch11 scripts** (M4-A2P-001, 005, 006, 002, now in review; M4-C10/C11/C14/C15-01 in review):
  - 71 `.dlg` scenes in `game/data/dialogue/ch1{0,1,4,5}/`, compiled, with `dialogue.csv`;
  - new speakers `owa`, `kirru`, `kirru_child`, `tobin`, `merel`, `malcor_venn`, `brannoc_hale`, `hull_captain`, `aldous_varrow`, `hull_widow`: `speakers.json`, `CHAR_*` rows in `loc/ch1x.csv`, and `voices.json` rows borrowed from existing timbres (audio to tune);
  - about 40 flags declared in `flags.tres`;
  - `tests/unit/test_act2_dialogue.gd`: every Ch10–Ch16 scene down every option path, all flags unset and all set, checking END, no runner warnings, letterbox off, translated keys, known speakers, emotions and the light rules.
  - Checks run: dlgc --check 0/0; validate_data 0/0; taskboard --check; gdlint and gdformat on the test; Godot `--import`; `--filter=act2_dialogue` 1 run, 0 failed.
  - A pre-existing "Invalid UTF-8 leading byte (a7)" warning shows at Godot start. No text file under game/ or tests/ has invalid UTF-8, so it isn't from this work.
  - Skipped: the coverage step (no battle or progression code) and screenshots (no scene changed).
- **Requests the scripts make** (for the owners; also in each scene's header):
  - **cinematics/UI:** the hold_input prompt rows `hold_to_watch`, `release_tide` (Ch10), `pole_stroke` (Ch14), `hold_steady`, `turn_collar`, `seat_it` (Ch11) need loc keys in each chapter's field data, as `ch09_field.json`'s `raise_staff`. The farewell-tide's "Release" variant is still a UI request.
  - **chapters:** the flow sets `ch10_drowner_felled` and `ch14_steps_held` on those fights' ends (declared), and plays the scenes in order. The scenes hand off with `start_battle` on encounter ids `ch11_lamp_engine`, `ch14_water_steps`, `ch14_malcor_venn` and `ch15_wakefin` (ids to create, or rename here).
  - **systems/cinematics:** `cues.json` has no grade ids for ch10–ch16 and no sideways drift for held light. The scripts use no `grade=` and give held motes no drift until those are added.
- Next: Ch12, then Ch13, then Ch16 (M4-A2P-003, 004, 007), then M4-A2P-008 (heresy barks and the people's codex).
- MERGE-READY @ 1f4c792d: **Ch12 and Ch13 scripts** (M4-A2P-003, 004, and M4-C12/C13-01, all in review): 33 scenes; speakers `ullari`, `ullari_woman`, `householder`; 18 flags. The Archive's record texts (the torn Binding Ledger fragment, ADR 0204 §15) are narration lines with `DLG_CH13_REC_*` keys for the document reader. Checks: dlgc --check 0/0, validate_data 0/0, Godot `--filter=act2_dialogue` PASS (all Act II scenes so far, every path). Next: Ch16 (M4-A2P-007), then M4-A2P-008.
- MERGE-READY @ 6e4ffd4d: **Ch16 scripts** (M4-A2P-007, M4-C16-01 in review):
  - 11 scenes: the Rim, Kesh's memory sequence (shown, never said), Sefir's temptation with ADR 0016 (c)'s fixed lines and "Captain.", the act-break VO, and the "Act III: The Unbinding" caption;
  - speaker `kesh`; 6 flags (`ch16_guard_beaten` and `ch16_line_held` are set by the flow on those fights' ends).
  - **All seven Act II chapters are now scripted** (about 130 scenes).
  - Checks: dlgc --check 0/0; validate_data 0/0; Godot `--filter=act2_dialogue` PASS; `--filter=voice` 15/0.
  - `--filter=dialogue` was 86 run, 1 failed: `test_dialogue_box::test_every_act1_speaker_with_a_model_has_a_portrait` (Pell has a model and no portrait under assets/ui/portraits). It's pre-existing, reads only `ch0*` scenes, and is an Act I row for characters or ui-menus, not from this work.
- LEAD-ASK: the Act I red above (`test_every_act1_speaker_with_a_model_has_a_portrait`, Pell's portrait). Route it to ui-menus or characters as an Act I FAST-TRACK? Not mine to fix (`assets/ui/portraits/**` is ui-menus').
- Next: M4-A2P-008 (heresy barks, Kerrid's post-reveal barks, the people's codex text).
- MERGE-READY @ 2e6369bd: **M4-A2P-008** (in review):
  - 12 Act II people in the codex; `kerrid_stair` is Kerrid's post-reveal page, in the bible's words;
  - three heresy-state barks and two Kerrid post-reveal barks.
  - Checks: validate_data 0/0, dlgc --check 0/0, Godot `--filter=act2_dialogue` PASS and `--filter=codex` 15/0.
  - Note for ui-menus: `test_codex.gd` pins the world and records counts, so the Archive's records stay in `ch13_archive_*` scripts (keys `DLG_CH13_REC_*`) for the document reader to show, not codex rows. If ui-menus wants them in the codex, add them with the test update.
- **Story track status:** all eight story tasks (M4-A2P-001…008) and the seven beat sheets (M4-C10…C16-01) are in review, waiting on cinematics (and the Lead for Ch14–Ch16, and ui-menus for 008).
- BACKLOG EMPTY (story track): every story task is scripted and in review. When reviews come back, their notes are the next work.

## 2026-10-30 — merged integration @ c38ba639
- Lead: the Pell portrait red is fixed (big19). I merged `claude/new-session-mj8c3c`. The only conflict was in `tools/banned_terms.txt`; both sides had appended lines and I kept them all (`Farplane` plus the four `* break` terms). No Act II script uses the new terms.
- The **LEAD-ASK on the Pell portrait is closed**. Godot `--filter=dialogue`: 86 run, 0 failed. validate_data 0/0, dlgc --check 0/0, taskboard --check clean.
- MERGE-READY @ 1dc453a9 (merge commit; the next commit adds only this log entry).
- BACKLOG EMPTY (story track): every Act II script is in review.

## 2026-10-30: M4-A2P-009, Act II NPC barks and lore (Lead request)
- Checks: dlgc --check 0/0 · validate_data 0/0 (banned terms included) · taskboard --check clean · Godot `--filter=dialogue` 86/0, `codex` 15/0, `bestiary` 37/0 · gdlint and gdformat clean on `test_codex.gd`.
- MERGE-READY Ch10 @ bd779aed: barks for Pell at the edge and the gate, Owa, the shell-carver, the fisher, the Kirru child; Drowner lore; codex entries `farewell_tide` and `name_shells`.
- MERGE-READY Ch11 @ bd779aed: barks for the Lowlight keeper, Pell at the conduits, Kerrid in the galleries; Conduit Crawler and Lamp Engine lore.
- MERGE-READY Ch12 @ bd779aed: barks for the keth-reader, the boy, the well at night, the Cloudloom keeper, a traveller; Avalanche Ram lore.
- MERGE-READY Ch13 @ bd779aed: barks for the pole-barge man (with a heresy variant), the archivist, a child at the ledge, the seamstress (with a heresy variant), the kneeling woman.
- MERGE-READY Ch14 @ bd779aed: barks for a guest, a Lamplighter, a Stillguard; Warden Venn lore; codex entry `outside_the_level`.
- MERGE-READY Ch15 @ bd779aed: barks for a current-singer, the raft cook, the lookout, a child after the pyre-raft; Wakefin lore.
- MERGE-READY Ch16 @ bd779aed: barks for a cairn-wader and a wader turning back; Abiding Guard lore; codex entry `the_hush`.
- **For Combat (creatures-b):** when you add the enemies.json rows, point them at `name_key` `ENEMY_<ID>` and `lore_key` `LORE_<ID>`. The keys are already in the chapter csv files.
- **For ui-menus:** `test_codex.gd`'s World total goes from 12 to 16 (two pinned numbers).
- **For chapters and towns:** these barks still need NPC actors and interactables placed in the field.
- BACKLOG EMPTY (story track).

## 2026-10-30: FAST-TRACK (big20 tools reds) + consistency second pass
- Merged big20 (7dc3ab41). Conflicts:
  - `test_codex.gd`: World total is now 16, from ui-menus' `farewell_tide` and `name_shells` plus my `outside_the_level` and `the_hush`. My duplicate `farewell_tide` and `name_shells` entries were dropped.
  - `flags.tres`: both sides' rows kept.
  - Four boss loc rows that `strings.csv` now holds were dropped from the chapter csv files.
- **test_cutscene_sfx_files:** green (6/0). The Act II scripts named cues audio hasn't delivered.
  - Music: 15 `music_stand_ins` rows point at the delivered Act II files (`../act2/music/<id>`, `act2/<boss>_p1`). `abiding_guard` and `kesh_memory` go on `MUSIC_TODO`.
  - SFX: six cues moved to sounds that exist (`barge_pole`, `hearth_crackle`, `undertow_wall_roar`, `current_song`). Eleven go on a new `SFX_TODO` with the same may-only-shrink rule, plus a test that keeps that list honest.
  - Request: **M4-A2P-105** (audio).
- **test_hero_clips:** green (19/0, 531 s). 73 Act II `@anim` clips went on `requested_clips.json` `clips`, the M3-CHR-1000 pending list. Characters builds them (M4-A2P-105).
- **Flags (act2_consistency.md second pass):** the scripts now use the lane names that code already uses: `ch10_drowner_defeated`, `ch10_farewell_tide_seen` and `ch15_kerrid_revealed`. My three duplicates are retired.
  - For ui-menus: `kirru_eldest` duplicates `owa`.
  - For chapters: M4-A2P-015 still says `ch15_kerrid_told`.
- **Ch14–Ch16 barks and lore:** already covered by M4-A2P-009 (Ch14: 3 barks, Ch15: 4, Ch16: 2, plus Venn and Abiding Guard lore and the `outside_the_level` and `the_hush` codex entries).
- **Checks:**
  - validate_data 0/0, dlgc --check 0/0, taskboard clean;
  - test_cutscene_sfx_files 6/0, test_placeholder_audit 14/0, test_hero_clips 19/0;
  - Godot `codex` 16/0, `ch10_thread` 1/0, `act2_dialogue` 1/0, `status_menu` 7/0, `cutscene_music` 3/0;
  - after the merge, Godot needs `--import` to rebuild the class cache, or every test parse-fails.
- MERGE-READY @ 469b3980c
- BACKLOG EMPTY (story track).
