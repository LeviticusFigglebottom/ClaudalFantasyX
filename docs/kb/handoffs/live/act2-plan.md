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
- Follow-up: Godot `cutscene_face_anim` passes 7/0 after the class-cache rebuild. Its earlier failures came from a run started before `--import`. The full `--filter=cutscene` sweep took more than 28 min and was cut off with no failures up to that point. The Lead's full run on merge covers the rest.
- Task renumbered: M4-A2P-105 → **M4-A2P-107**, because integration took 105 for a Ch15 task. `abiding_guard` landed (big21), so it's off `MUSIC_TODO` and has a stand-in row.

## 2026-10-30: M4-A2P-108, Act II side content and camp conversations (Lead request)
- Merged integration first (big21). Fallout:
  - codex: theirs taken, then `kerrid_stair` and `farewell_tide` re-pointed at the lane flags. My `outside_the_level` was dropped in favour of ui-menus' fuller `heresy` page, so World is now 18 and `test_codex.gd` is pinned to 18.
  - The four boss loc rows are restored in ch10, ch11, ch12 and ch15.csv. big21 deferred to them, but I'd dropped them after big20.
  - `abiding_guard` is off `MUSIC_TODO` with a stand-in row.
  - The request task is renumbered to M4-A2P-107.
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · test_cutscene_sfx_files OK · Godot `act2_dialogue` 1/0 (every path of the 21 new scenes, all flags unset and all set) · `dialogue` 86/0 · after the merge, `codex` 16/0, `status_menu` 7/0, `bestiary` 37/0. No `@anim` was added, so the hero-clips test can't change.
- MERGE-READY Ch10 @ f2d13a64c: `ch10_side_the_three_nets`, `ch10_find_guardian_strap`, camp `ch10_camp_what_you_carry` (Rhen and Pell).
- MERGE-READY Ch11 @ f2d13a64c: `ch11_side_the_altar_lamp`, `ch11_find_lampmakers_plate`, camp `ch11_camp_she_sounded_glad` (Asha and Pell).
- MERGE-READY Ch12 @ f2d13a64c: `ch12_side_the_boys_knot`, `ch12_side_dorros_cord`, camp `ch12_camp_the_end_of_the_road` (Toma and Ysolde).
- MERGE-READY Ch13 @ f2d13a64c: `ch13_side_the_leaning_flame`, `ch13_find_velamir_register`, camp `ch13_camp_twenty_four_years` (Ysolde and Asha).
- MERGE-READY Ch14 @ f2d13a64c: `ch14_side_the_oar_pin`, `ch14_side_six_lamps`, camp `ch14_camp_the_whole_of_him` (Liss and Rhen).
- MERGE-READY Ch15 @ f2d13a64c: `ch15_side_the_current_phrase`, `ch15_side_the_tally_hull`, camp `ch15_camp_the_bottom_step` (Toma and Kerrid).
- MERGE-READY Ch16 @ f2d13a64c: `ch16_side_the_fallen_cairn`, `ch16_find_the_counting_stone`, camp `ch16_camp_coming_up` (Asha and Rhen).
- **Requests (see M4-A2P-108):**
  - chapters and towns: place the interactables, NPC actors and camp rest points;
  - ui-menus: add the errands' `side` rows in objectives.json, with `OBJ_SIDE_*` keys.
- BACKLOG EMPTY (story track).

## 2026-10-30: M4-A2P-109, Act II objectives, tips, items and shrine text (Lead request)
- Integration merged first (clean).
- **Checks:** validate_data 0/0 · dlgc --check 0/0 · taskboard clean · tools tests `test_loc_key_names`, `test_loc_literals`, `test_loc_readiness`, `test_tutorial_tips` and `test_cutscene_sfx_files` OK · Godot `objective` 15/0, `act2_dialogue` 1/0, `zone_map` 22/0, `pseudo_loc` 26/0.
- **Coordinating ids with act1-chapters, progression, combat and ui-menus:** `docs/kb/plan/act2/act2_text_ids.md` lists every id and its owner. I don't use send_message, so this file is the handoff.
- MERGE-READY Ch10 @ 11f5c5c18: 5 objective rows; `TUT_CH10_*`, `TUT_DROWNER_ROOTS`, `FORMATION_AWAY_PELL_FEN`; `tannin_bark`, `reed_salve`, `rhen_fenroot_hooks`, `INN_REEDHOLLOW`; `ch10_shrine_reedhollow`.
- MERGE-READY Ch11 @ 11f5c5c18: 5 rows; `TUT_LAMP_ENGINE_CRAWLERS`; `conduit_glass`, `asha_conduit_staff`, `liss_lowlight_sleeve`; `ch11_shrine_lowlight`.
- MERGE-READY Ch12 @ 11f5c5c18: 8 rows; `TUT_CH12_UNRAVEL`, `TUT_RAM_FIELD`; `woolback_felt`, `butter_tea`, `asha_keth_bangle`, `toma_felt_shield`; `ch12_shrine_quellan`.
- MERGE-READY Ch13 @ 11f5c5c18: 9 rows; `TIP_RECORDS_*`; `torn_ledger_line`, `ysolde_archive_copybook`, `INN_ANSEDRA`; `ch13_shrine_ansedra`.
- MERGE-READY Ch14 @ 11f5c5c18: 4 rows; `TUT_CH14_HOLD_STEPS`, `TUT_MALCOR_ENGINE`, the step-hold HUD lines, `TIP_DARK_SHRINE_*`; `red_lacquer_chip`, `tobins_cracked_lamp`, `ysolde_red_lacquer_guards`.
- MERGE-READY Ch15 @ 11f5c5c18: 7 rows; `TUT_WAKEFIN_DARK`; `seaglow_scale`, `current_broth`, four gear pieces; `ch15_shrine_hollowmere`.
- MERGE-READY Ch16 @ 11f5c5c18: 4 rows; `TUT_CH16_*`, the line-hold HUD lines, `TIP_SWELL_MODE_*`; `rim_salt`, `kerrid_rim_wraps`; `ch16_shrine_pale_rim`.
- **LEAD-ASK (route to progression or ui):** `ITEM_RIME_SHARD_DESC` says "Highland ice that does not melt", which breaks ADR 0015 if the item drops in Ch12–Ch15.
- BACKLOG EMPTY (story track).

## 2026-10-30: ADR 0015 text sweep (Lead answer to the Rime Shard ask)
- I grepped every loc csv, `dialogue.csv` and the Act II `.dlg` files for ice, icy, frost, frozen, freeze, glacier, rime, icicle, snow and sleet. Fixed:
  - `ITEM_RIME_SHARD_DESC`: "Highland salt-rime that never dissolves, even in the sea."
  - `LORE_RIME_URCHIN` (Ch11): the rime is now a salt crust ("the water never takes it back"). Lowlight is "nothing frozen".
  - `LORE_RIDGE_LYNX` (Ch12): frost → blown snow. `LORE_SCREE_CRAWLER` (Ch12): frost-split → weather-split scree and grit. Both follow ADR 0204 §2.
- **Kept on purpose:**
  - Ch12's snow on the road (`OBJ_CH12_WALL`, `TUT_RAM_FIELD`, the Ram's lore). ADR 0015 calls the pass's snow weather, which is allowed outside temples.
  - The game element Ice (`ELEMENT_ICE`, `ABILITY_RIME_*`, `SKILL_FROST`, Kesh's `SKILL_VOICE_ICE` in Ch16). These are element names, not Ch12–15 imagery.
  - "cold" lines in Ch11 (the deep's cold).
- validate_data 0/0; loc tools tests OK.
- MERGE-READY @ dc18517e3

## 2026-10-30: Act I proofread pass (Lead request), in progress
- **Mechanical checks on Act I text (about 2,900 strings):** doubled words, spacing, unbalanced quotes and brackets, a spell-check against the glossary, and near-duplicate proper nouns. No defects found. Every hit was intentional: ellipses, spaced formats, coined words, and Daro Pemakan's surname.
- **LEAD-ASK (needs an ADR; it touches ui-menus, combat and progression):** the house spelling is mixed.
  - Prose, lore and the glossary use British: colour, armour, grey, harbour, honour, favour, traveller, practised, metres.
  - The UI and stat strings use American: `STAT_DEFENSE` "Defense", `STATUS_*_BREAK_DESC` "defense", `EQUIP_MENU_SLOT_ARMOR` and `STATUS_MENU_ARMOR` "Armor", `FIELD_MENU_EQUIP_DESC` "armor", `TUT_CH05_ARMOR_BREAK` "Armored … armor" (while the same chapter's `ROLE_KERRID` says "Breaks armour"), `SET_PALETTE*` "Color palette / colors / Colorblind-friendly", `TITLE_HELP_SETTINGS`, `FIELD_MENU_SETTINGS_DESC`, `SET_MENU_HELP_ACCESSIBILITY`.
  - "Customize" (‑ize) is consistent and fine under Oxford spelling.
  - **Proposal:** British (Oxford) everywhere a player reads it, as the glossary already does. That means Defence, Armour, Colour palette, Colour-blind-friendly; keys unchanged. It's about 15 strings; I'll do it as one FAST-TRACK when you say yes.
- **Act I proofread, read-through:** a reviewer read every Act I string against the glossary and voice guide, and I checked each finding against the source. I applied 9 and skipped 1 as style. All are FAST-TRACKs:
  - **Two rows truncated in game:** `ITEMS_MENU_ERR_KEY_FMT` and `FORMATION_MENU_ERR_OPEN_PLACE` had an unquoted comma, so the player saw "It is kept" and "Pick a hero first". They're quoted now. A new `tools/tests/test_loc_csv_shape.py` fails on any loc row whose column count is wrong; these were the only two in the repo.
  - `TUT_CH04_VOWBOUND`: Ilun is Teyo Marrin, so "Call him … he fights … he leaves" (the codex and Ch3 already say "him").
  - `RBL_SIDE_PEMAKAR` and `RBL_DIVER_PEM_*` showed "Pemakar Terraces", but Ch7's opponent is **Sorrin** (act1_ch07.md §203, the board and market barks). The display text now says Sorrin. **For reefball's owner:** the side id `pemakar` in sides.json and matches.json could be renamed to match, at your call.
  - `DLG_CH03_BARK_CAUSEWAY_TIDEPOOL_002`: "Two copper" → "Two lume". The glossary has one currency.
  - `FLOW_END_CARD_TITLE` and `CREDITS_SLICE`: "Act One" → "Act I", to match the act cards' "Act II" and "Act III".
  - `ITEM_TIDEWASH_SALVE_DESC`: "every Break" → "Sundered, Unmoored, Weakened and Dimmed", the names the player sees.
  - `ABILITY_DEEP_LUNGS_DESC` "Max HP"; `HUD_ITEM_COUNT_FMT` "×{n}", like every other count; `CODEX_BELL_GALLERIES_BODY` "where the Tidecup is played".
  - Skipped: `DLG_CH07_TAVI_016` ("Asha. I'm so sorry…"). It reads as an introduction in context; that's style, not a defect.
- **Checks:** validate_data 0/0 · dlgc --check 0/0 · loc tools tests plus the new one OK · Godot `formation` 18/0, `items_menu` 13/0, `reefball` 80/0, `end_card` 5/0, `pseudo_loc` 26/0.
- MERGE-READY @ 090457c88
- BACKLOG EMPTY (story track). The British-spelling LEAD-ASK above is still open.

## 2026-10-30: British spelling (Lead decision)
- 18 player-facing strings, keys unchanged:
  - Armour, armoured;
  - Defence and Magic Defence (the stat names, the Break status descriptions, the Lattice facets and the abilities);
  - Colour palette, colours, colour blindness, Colour-blind-friendly.
- Files: `ch05.csv` (`TUT_CH05_ARMOR_BREAK`), `menus.csv`, `menus_equip.csv`, `menus_items.csv`, `strings.csv`. No American forms are left in any loc csv.
- The rule is now in the glossary (an appended "Spelling" section) and in the voice guide's global rules: British with Oxford -ize (Customize stays), and keys and ids keep their spelling.
- **Checks:** validate_data 0/0 · loc tools tests OK · Godot `settings` 48/0, `equip` 66/0, `status_menu` 7/0, `lattice` 67/0, `pseudo_loc` 26/0.
- MERGE-READY @ 73c2cb482

## 2026-10-30: Act II proofread and spelling pass (Lead request)
- The automated pass over 822 Act II strings (spell, spacing, quotes, American spellings) found nothing. A reviewer then read all of them against the glossary, voice guide, beat sheets and ADRs 0015, 0016 and 0204. I checked all 13 findings against the source and applied all 13.
- **Continuity, the important ones:**
  - **Imra walked on to the Choir** (Ch15 K "She walked on to the Choir"; Ch16 "My mother walked here"). My Ch13 register line "Mother never got this far" was wrong. It's now "Mother would have stood right here", and the script note and M4-A2P-108 are corrected.
  - **Herd-cord errand:** Pell already ties the cord on the pass in B07, so the errand no longer hands the cord over. Dorro's daughter asks after the animal and learns it's on the road with him. `OBJ_CH12_SIDE_CORD` and the flag's description are updated.
  - **"Lamplighters"** is the glossary's proper noun for the six founders. The wedding's lamp-carriers I invented are now **lamp-bearers**: the speaker labels in `ch13_side_the_leaning_flame`, `ch14_side_six_lamps` and `ch14_bark_lamplighter`, plus `OBJ_CH13_SIDE_FLAME`. The ids and flags keep "lamplighter".
  - **Seamstress:** "a Cantor's wedding" → "the wedding". The bride is Merel, not Asha.
  - **Wakefin lore:** it's now Undertow-spawn that "followed the first ripples out of Ansedra's lagoon" (glossary and ADR 0016), not a fish the Saltwrights know.
  - **Drowner lore:** "the full moon before last", to match Pell.
- **Codex rows** (ui-menus wrote them; I fixed them as proofread):
  - `CODEX_HERESY_BODY`: "Outside the Level" capitalised.
  - `CODEX_LOWLIGHT_BODY`: the cold wells up *and* the glimmer sifts down.
  - `CODEX_SUNKEN_VEY_BODY`: copper conduits holding a steady light, not ceramic and not pulsing (Ch11 rule 3).
  - `CODEX_REEDHOLLOW_BODY`: one clutch, so each lodge is a family's.
  - `CODEX_MALCOR_VENN_BODY`: "decree" → "declaration".
- **Voice:**
  - Rhen's "Big fan" → "My favourite kind". It came from the beat sheet, but it's modern slang.
  - Toma's "anymore" → "any more" (British).
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · loc tools tests OK · Godot `act2_dialogue` 1/0, `codex` 16/0, `bestiary` 37/0.
- MERGE-READY @ 348b65795
- BACKLOG EMPTY (story track).

## 2026-10-30: Act III planning sheets (Lead request; docs only, Act III production stays paused)
- New folder `docs/kb/story/act3/`:
  - `README.md`: the act in one paragraph, a pillar-6 table (what each person does not keep), and rules for every sheet.
  - `act3_ch17.md` "Hollowmere": the ledger read on screen and never voiced, with ADR 0022's facts exact; Asha chooses the Unbinding; the Kite's first lamp is bound light, said aloud.
  - `act3_ch18.md` "The Kite": a short critical path. Pell walks through the gate, is named again and teaches the farewell-tide wordless. Eight revisits, each showing its grief changed; Haluna lifts its own (optional, flagged); seven heirloom errands.
  - `act3_ch19.md` "Iskarra": the Prologue vigil shot for shot, with the line verbatim. Kerrid teaches Rhen Dace's hitch (holds, then one pull and it lets go). The Lamp Spire; Hesper Oan and Ilsabet Rue fought openly as revenants; the eye opens.
  - `act3_ch20.md` "Undertow": six memory layers and six releases in vowbound.md's order, each with its companion, then the Cage and "thank you".
  - `act3_threads.md`: the consistency pass.
- Each sheet uses the Act II format §0–§10, and §10 holds the open questions and defaults. Ch21 and the Ending stay in the existing `beats/act3_ending.md`.
- **Consistency pass:**
  - All 37 Act I/II flags the Act III sheets read are declared.
  - Every companion's Act III arc in their character sheet is traced to a beat; three gaps were filled (Toma, Ysolde, Kerrid's teaching).
  - Every Vowbound is traced from binding to release.
  - 14 mismatches are logged, T-01 to T-14. Applied: T-02 (act2_ch14's Venn row corrected: no Ch19 rematch), T-09, T-12, T-14.
- **LEAD-ASKs** (act3_threads §4):
  - **T-01:** act3_ending H03 "raises Kesh from the stones", but Ch16 binds her to Asha. I propose Asha calls her out of the sleeve one last time and Kesh is released like the six.
  - **T-04:** the Eighth Verse's sources disagree across vowbound.md, pell.md and ysolde.md. I propose: the melody is in the stones, read through the farewell-tide; the words are in the stones; the count is Ama's question-knot.
  - **T-07:** the Prologue's "glimmer rises" breaks light grammar for a Ch19-dusk frame. I propose the motes drift instead.
- **Checks:** banned-terms scan of the new docs: 0 hits. validate_data 0/0. taskboard clean. No game file touched.
- MERGE-READY @ 49ae12a1f
- BACKLOG EMPTY (story track).

## 2026-10-30: Lead answers applied; the ending-cost audit
- **Spelling (ADR 0206):** the FAST-TRACK was already applied (18 strings, keys unchanged). I merged integration with ADR 0206: no American forms are left in any loc csv.
- **T-01 (accepted):** act3_ending H03 now has Asha call Kesh out of the sleeve one last time; she is released like the six. vowbound §7 gains a Release line.
- **T-04 (accepted):** the Eighth Verse's sources are reconciled in vowbound.md (Kesh §7, Hesk §4), pell.md and ysolde.md, and act3_ch19 I04 matches: the words are in the stones; the melody is in the stones, read through the farewell-tide; the count is Ama's question-knot.
- **T-07 (accepted):** act_outline's Prologue now says the held glimmer drifts and never rises. The cue in `prologue_dead_city.dlg` (`glimmer_lift`) and its shot baseline (`slice_prologue_vigil_line`) are **M4-A2P-111** (cinematics, todo), because it moves a rendered baseline.
- **Reefball `pemakar` → `sorrin`:** **M4-A2P-110** (progression, the reefball data owner, todo).
- **Ending-cost audit** (`docs/kb/story/act3/ending_cost_audit.md`): for every companion, what they lose, the chain of scenes that earns it, a verdict and a fix. Three gaps, all closed in my Act III sheets:
  - Asha's voice was only ever heard as a Cantor's. Ch18 K05 now has her give Pell the Velamir lullaby, the one time she hums for herself.
  - Liss never chose to let go of anything. Ch20 U00 now has her seat Tobin's lamp in the Kite's engine and spend it on the last charge.
  - Ysolde's want ("a good death") never turned. Ch19 I04 adds "a long, dull life instead".
- One proposal for act3_ending: Toma's beach rite gets a fallback line when Ch18's lifting was skipped. Rhen's E2 needs a check that it rhymes with Ch8 B17.
- **Checks:** banned-terms scan of every edited doc: 0 hits. validate_data 0/0. taskboard clean.
- MERGE-READY @ 39859600c
- BACKLOG EMPTY (story track).

## 2026-10-30: ending-cost proposals applied; Ch10 staging review (Lead request)
- **act3_ending (accepted):**
  - E2 now rhymes with Ch8 B17: Dace's turn toward Rhen mirrors W22's turn away, and the reverse at "Goodbye, Dad." uses W23's lens and distance.
  - CR stages Toma's beach rite as a credits vignette. Its fallback line, when `ch18_haluna_lifted` is unset: "Backs to the water. Like this. They go easier when nobody watches."
  - ending_cost_audit.md is marked accordingly.
- **ADR 0206 spelling FAST-TRACK:** pushed on `origin/claude/act2-plan` (bdc5be59d, 18 strings). Integration has ADR 0206 but not this commit yet; it lands with this branch's next merge.
- **Ch10 staging review** (slice-polish, `origin/claude/m2-slice`, M4-A2P-070/M4-CIN-1304): **M4-A2P-112** (cinematics, todo). I can't edit another environment's live log, so the notes are in that task. The review walked each scene's cues and checked every spoken line against the active shot. Findings:
  1. Their farewell-tide still sets the retired `ch10_tide_witnessed`. Take `ch10_farewell_tide_seen` at merge.
  2. Dawn gate: R10 framed empty air, because Pell was never placed on `causeway_last_root`. **Fixed here** in `ch10_dawn_gate`.
  3. B06: Owa's first line is about 38° off R02's axis (R02 is the layout's shot, never staged). It needs the 50 mm singles.
  4. B05: Pell's "It is the direction." was spoken from behind O07's lens. **Fixed here**: the line now comes before his exit.
  5. B09: Ysolde has no mark for "Turn around".
  6. Pacing: every staged scene runs 3–5× shorter than act2_ch10 §1, with specific holds proposed.
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · Godot `act2_dialogue` 1/0 and `dialogue` 86/0.
- MERGE-READY @ 4185052e2
- BACKLOG EMPTY (story track).

## 2026-10-30: big22 merged; two tools reds fixed (Lead FAST-TRACK)
- Merged integration (big22) @ 3ef552f87. The fixes are in the merge commit:
  - **test_cutscene_sfx_files:** big22 delivered all 11 pending SFX and `kesh_memory`, so `SFX_TODO` and `MUSIC_TODO` are now empty, as the test demands. `kesh_memory`'s stand-in row came with the merge. M4-A2P-107's audio rows are ticked; characters' clips remain.
  - **test_status_names:** the Kirru speaker label "Shell-carver" collided with ADR 0202's retired status name Shell. It's now **"Name-carver"** (she carves the name-shells), and act3_ch18 is updated to match.
- **Conflicts:**
  - `ch11.csv`: both appends kept.
  - `objectives.json`: integration's zone-level main rows (8287ca8b3) are pinned by `test_act_two_zones_point_along_the_main_path`, and my beat-level main rows clash with them in either order. **I dropped my 30 main rows and their `OBJ_CH1N_*` text and kept my 13 side errands.** M4-A2P-109 and act2_text_ids.md are updated.
- **LEAD-ASK:** later, when the chapter flows set the story flags, should the beat-level main lines replace the zone-level ones? They're in git history at 1a3aa7b9a. Owner of the test: whoever wrote 8287ca8b3.
- **Checks:**
  - tools: test_cutscene_sfx_files and test_status_names (8 tests) OK; loc_csv_shape, loc_key_names, loc_literals and loc_readiness OK; the hero-clip subset (7 tests) OK.
  - validate_data 0/0 · taskboard clean · dlgc 0/0.
  - Godot: `objective` 16/0, `zone_map` 22/0, `pseudo_loc` 26/0, `act2_dialogue` 1/0, `codex` 16/0.
- MERGE-READY @ 3ef552f87

## 2026-10-30: dropped objective rows checked; Ch10 staging re-checked; Ch11 direction notes
- **The 30 dropped main objective rows. Were they duplicates of the existing rows? Partly, not wholly.** I compared each against integration's 17 zone-level rows (8287ca8b3):
  - **16 had a direct counterpart** (same zone and target): the fen to Reedhollow, the galleries to Lowlight, Lowlight's sanctum, the pass to Quellan, Quellan to Cloudloom, Cloudloom's dais, the Sanctum, the Archive, the ledgers, the court dais, the barge, the sea watch, Hollowmere, the Rim, and the Choir. That content isn't lost; it's said in their words.
  - **14 were beat-level steps with no counterpart in the shipped rows**:
    - Ch10: the Drowner's clearing, the shore at dusk, Pell at the gate;
    - Ch11: back up and out of Lowlight;
    - Ch12: the snow wall on the terrace, the Quellan inn night, the descent;
    - Ch13: the ledge, the Cantor roll, Kerrid at the moorings, the High Warden's house;
    - Ch14: hold the water-steps, the water-gate;
    - Ch15: the dock-master, the pyre-raft, the ship south;
    - Ch16: hold the line.

    Those are **out of the game data, but not lost**: the rows and their text are in git (1a3aa7b9a). The LEAD-ASK above stands: when the flows set the story flags, restore them as finer steps under the zone rows.
- **Ch10 staging re-check** (m2-slice @ a9e826427), recorded in M4-A2P-112's status section:
  - resolved: 1 (the flag);
  - fixed in my scripts, reaching their branch with the next merge of this branch: 2 (dawn gate) and 4 (Pell's exit);
  - still open: 3 (R02 singles for Owa), 5 (Ysolde's mark; waits on M4-CIN-1305) and 6 (pacing). Their new stills are greybox, before the actors.
- **Ch11 direction notes:** `docs/kb/story/beats/act2_ch11_direction.md`, per scene. Each has the blocking (proposed marks with coordinates in the greybox frame), every shot (lens, position and target), and for **every spoken line who is in frame**, each checked with the frustum test, plus the pauses against §1's minutes.
  - **A collision caught and fixed in the scripts:** the greybox layout's own L01–L07 aren't lowlight.md's composed shots (the layout's L05 is a sanctum view), so `@camera L05` would have staged the engine scene in the wrong room with no error. The scripts now use V00, V10 and T00 for the art doc's L01, L03 and L05, and Pell kneels on the layout's `pell_kneel`.
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · Godot `dialogue` 86/0.
- MERGE-READY @ e25478fd1
- BACKLOG EMPTY (story track).

## 2026-10-30: Ch12 and Ch13 direction notes (Lead request)
- `docs/kb/story/beats/act2_ch12_direction.md` and `act2_ch13_direction.md`, in the Ch11 format.
- A script (kept in the scratchpad, not the repo) frames each shot on its subjects in the greybox frame, runs each scene's cues and checks every spoken line's speaker against the active shot. **Ch12:** all lines in frame, one deliberately off (Ysolde over the Ram). **Ch13:** 58 in frame, 5 deliberately off (voices over the reader, Rhen over the polers' wide).
- Each doc lists the **greybox ids that collide with a different picture**, to replace in staging (Ch12: K01, K04, C02, C03; Ch13: A03–A06, S02), and the pacing per beat against §1. Every scene runs 2–8× short; the notes say where the holds go.
- **Blocking bugs fixed in my scripts:**
  - Kerrid and Tobin shared `outer_moorings`, so Kerrid now stands on the layout's `kerrid_moorings`;
  - Merel and Tobin shared `guest_moorings`, so Merel uses `guest_moorings_b`;
  - the house side scene now cuts between A15b (the street) and A15 (the front room), with Rhen on his own marks.
- act2_ch13 §7's A03 said Kerrid sits; it now says he stands, per ADR 0204.
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · Godot `dialogue` 86/0.
- MERGE-READY Ch12 @ d56bcb66d · MERGE-READY Ch13 @ d56bcb66d
- Next: the Ch14–Ch16 notes.

## 2026-10-30: Ch14, Ch15 and Ch16 direction notes (Lead request)
- `docs/kb/story/beats/act2_ch14_direction.md`, `act2_ch15_direction.md` and `act2_ch16_direction.md`, in the Ch12 and Ch13 format. Each has the greybox ids to replace, the script fixes, pacing per beat against §1, and per scene every shot (lens, cam → look, fov) with who is in frame on every spoken line.
  - **Ch14:** 25 lines in frame. Replace the greybox's W03–W07 (the Lacquer Court, in ch13's level folder).
  - **Ch15:** 72 lines in frame, 1 deliberately off (Pell over the fin). Replace U01–U07 (open_sea) and H01–H04 (hollowmere).
  - **Ch16:** 25 lines in frame, 4 deliberately off (Kesh's voice in the memory, and Ysolde over Sefir's smile). No greybox collision. The vigil's P04 shares its name with pale_rim's P04 (legal, because ids are per zone; the doc suggests `P04_vigil`).
- **Script fixes (story's own files):**
  - **Ch14:** Merel goes to the layout's `merel_gate`.
  - **Ch15:**
    - `ch15_current_song` played sea and Hollowmere in one scene, so B10 is now its own scene, **`ch15_the_dock_master`** (`ch17/hollowmere`). It still sets `ch15_liss_told_father`.
    - The party uses the layout's `reveal_*`, `bow_liss`, `confess_toma` and `supper` marks.
    - Each actor gets their own jetty-end and ship-deck marks.
    - K18b and K19b are added, so Rhen and the group are in frame for their lines.
  - **Ch16:**
    - Asha, Toma and Rhen walked onto `kesh` (the Saint's own mark), and four of the party never reached the dais. All seven now walk to new `dais_*` marks, with Kerrid behind.
    - Sefir's `015` cuts back to C12.
- **For Chapters (one line):** no flow plays `ch15_current_song` yet. When the Ch15 flow is wired, play `ch15_the_dock_master` on arrival at Hollowmere.
- **Merged integration:**
  - The Lead restored my beat-level objective rows (fbecf6051), so **the objectives LEAD-ASK above is answered**.
  - I took integration's `objectives.json` and the `ch10`–`ch16` loc files with their `OBJ_CH1x_*` rows.
- **Checks:** dlgc --check 0/0 · validate_data 0/0 · taskboard clean · tools dialogue, cutscene and loc tests 183 OK · Godot (after the merge and an `--import`): `dialogue` 86/0, `cutscene_directives` 2/0, `cutscene_music_resolves` 3/0, `cutscene_vfx_hosts` 4/0, `cutscene_mark_via` 4/0, `cutscene_staging` 2/0. Skipped: the QA motion audit (report-only, Act I) and the render tests (no scene, shader or asset touched).
- MERGE-READY Ch14 @ 603fb1f36 · MERGE-READY Ch15 @ 603fb1f36 · MERGE-READY Ch16 @ 603fb1f36
- BACKLOG EMPTY (story track).
