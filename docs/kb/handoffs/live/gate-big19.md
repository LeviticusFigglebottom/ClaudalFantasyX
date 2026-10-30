# Gate session live log: big19

The big18/big19 cloud gate session (`session_01UPFyEAXofxWazWNnRTzFGJ`) builds `lead/gate-big19`, runs every check
and publishes the shots to `lead/gate-big19-shots`. It never writes or approves baselines. The process is the same as
big17's and big18's (`gate.md` on `lead/gate-big17`, `gate-big18.md` on `lead/gate-big18`).

The Lead's plan change (2026-10-30 01:29 UTC): big18's shots are skipped. big19 contains big18 and replaces it.

## big19

GATE-BUILT big19 @ d4101e05 (branch `lead/gate-big19`), from `lead/gate-big18` @ 32ab8f0b.

Pinned heads, merged with `--no-ff` in this order:
1. claude/new-session-mj8c3c @ 4c116db4: clean. It brings ADRs 0202–0204, the Act II plan and the 187 approved
   big17 baselines.
2. claude/env-art @ 08ffac58: PROVENANCE by merge_union.
3. claude/env-art-b @ 0d59db7d: union files only.
4. claude/characters @ 36b06105: union files only.
5. claude/creatures @ 6046146b: shots.json by merge_union, which now handles the criss-cross virtual base itself.
6. claude/creatures-b @ 155b0870:
   - `creatures.json`: one hunk, two adjacent rows. `sail_leech` from ours (creatures' audit, hover 1.26);
     `bottle_hermit` from theirs (creatures-b owns it: M3-CRB-013's contact timings).
   - `bottle_hermit.glb`: both sides changed `build_bottle_hermit.py` (creatures' feet pinning 6b399185c; creatures-b's
     M3-CRB-013 clips), and each committed its own glb. The sources merged clean, so the glb is rebuilt from them with
     the pinned Blender (d4101e05; the job then verifies 5 identical).
7. claude/battle-presentation @ c72011bd: clean.
8. claude/act1-chapters @ f6cb8190: `oruvel_layout.json` scaleman kept ours (big18's position with characters'
   scaleman model); M3-ENV-744's task kept ours (keeps both review lines).
9. claude/ui @ f5098f6b: union files only.
10. claude/hero-integration @ 86c5b9ac: M3-HER-1140 and M3-HER-1142 took theirs (`status: done`; integration-qa, the
    reviewer, accepted both in their review logs).
11. claude/m2-slice @ 54bf0aa6: `tests/unit/test_cutscene_vfx_hosts.gd` took theirs. Both sides fixed big17's
    `CutsceneMotes` parse error: env-art-b's FAST-TRACK counts `Vfx_*` fields, m2-slice's counts every GlimmerField.
    m2-slice's goes with its M2-FP-120 change (a0ed23c3), which also lists `@vfx follow=`/`anchors=` as unperformed.
12. claude/audio @ 7b2573fb: union files only.

Not merged: claude/act2-plan (already in the integration branch, the Lead's word); claude/menus (nothing new);
claude/first-playable, claude/gate-runner-a/-b (stale since 10-23/10-24); the retired -ze8rrn/-423ixt.

Merge fallout fixes (5a0eadff):
- PROVENANCE: removed the same 6 rows for deleted assets that the line union re-added on big18.
- `game/audio/music_deck.gd:7–8`: claude/audio's M3-AUD-864 doc comment ran to 142 and 143 characters
  (gdlint max-line-length). Rewrapped; no code changed. Audio should take the same wrap.

Checks at the build: validate_data 0 errors 0 warnings; taskboard --check ok; dlgc --check 0/0; gdlint and
gdformat --check clean; no duplicate loc keys, PROVENANCE rows or shot ids (623 shots); no conflict markers; no
`docs/kb/qa/gate-runs/**` images.

### big19 checks in progress (on eb3db1a8)
- 2026-10-30 01:40 UTC: every non-shot step started (HYMN_STEP_TIMEOUT=10800, own HYMN_LOG_DIR and XDG_DATA_HOME, in
  a worktree). Data 0/0; audio, manifest ok; Godot import clean.
- **Tool suite: 190 units, 1960 tests, 5 failing units** (big18: 3). Fixed since big18: test_zone_map_pois (Kell's
  POI), test_glimmer_forms (stays green). Each red re-run on the track heads:
  - **NEW, branch content (characters):** test_asha: "68696 not less than or equal to 65000" (Asha's LOD0 over its
    budget) plus test_part_budgets. test_villagers::test_kell_and_tavi_follow_the_sheet: "1.144 != 1.196". Both red on
    `claude/characters` @ 36b06105 alone.
  - **NEW, branch content (characters, with creatures' crowd):** test_npc: "crowd_elder_woman_a is too near reed_c
    (0.243 < 0.28)" and the generator output differs from the committed json. The same message on `claude/characters`
    alone. (big17 and the integration branch carry the older "crowd_girl_teen too near wright_child_a".)
  - **NEW, from the integration branch (the Lead's big17 approvals):** test_palette_check: "haluna_h07_chapel_court
    chapel sun face on order_marble 0: median #B0B2B2 ΔE_ok 0.042 (max 0.03)". Red on `claude/new-session-mj8c3c`
    @ 4c116db4 itself.
  - **CHANGED:** test_screenshots: "slice_end_card is approved: drop its pending_baseline key". The integration branch
    approved `slice_end_card`; m2-slice's M3-CIN-1233 (782351c7, no demo card mid-Act I) changed what it shows and
    marks it pending. big18's `villager_shopkeeper_front` (no baseline) is fixed by the approvals.
LEAD-ANSWERED: test_screenshots and test_palette_check come from the big17 approvals meeting the tracks. `slice_end_card`
is approved, but m2-slice's M3-CIN-1233 marks it pending (new content), so either the approval goes or the pending key
does. The approved `haluna_h07_chapel_court` fails its palette check (ΔE 0.042 > 0.03). I'm not changing either on
the gate.

### FAST GATE (ADR 0205; the Lead, 02:26 UTC): big19 @ 65fff30b (= eb3db1a8 + 4fa31522 + the integration branch @ 1296e499, docs only)
- The full suite in progress was stopped (my PIDs only); it runs again, non-blocking, after GATE-FAST-DONE.
- Blocking so far: validate_data 0/0, taskboard ok, gdlint and gdformat clean, the tools suite (5 reds, above, none
  merge fallout), **boot smoke 0 ERROR lines**.
- **Filtered Godot tests:** 282 of 436 test files, meaning every changed test file plus every test that names a changed
  game/ or assets/ file by its res:// path or class_name (diff against `claude/new-session-mj8c3c`). They run one file
  per process in 3 parallel lanes.
- **Shots: 254.** 41 named in the tracks' SELF-RENDERED / MERGE-READY / RENDER-REQUEST lines since big17, plus 237
  whose scene or the scenes, resources and data it loads changed (code excluded; the tests cover it). Asha's glb alone
  reaches 45 shots; the Corrow and Brine Shoals slot materials and Ch1's dressing most of the rest. Two parallel
  lavapipe captures, each with its own XDG_DATA_HOME.
- (Lead, 02:48: screenshots don't block (ADR 0205 amendment, 78b94328); `slice_end_card`'s stale baseline was dropped
  on the integration branch (c0104864); test_palette_check routed to env-art and test_npc to creatures, neither
  blocking.) Merged the integration branch @ 78b94328 again (bf502055). test_screenshots now stops at `kerrid_front`:
  160 manifest shots have no baseline yet (the 187 approved so far cover only part of big17's 372 captured). That
  waits on approvals and is not batch fallout.
- Gate fixes on big19:
  - b7a06f31: the .import/.uid files Godot's import generated (officer textures, two new scripts).
  - **85b0d58b, batch content made the merge red:** test_qa_capsules: "corrow.tscn: figure is KNOWN but no longer a
    capsule; drop it from qa_known.json". creatures' M3-HER-1142 (3d66961a) gave the Corrow storm figure a body.
    Dropped the one entry; the test passes (3/0). Red on `claude/creatures` alone, so creatures should take the same
    removal (FAST-TRACK).
- The two captures are paused (SIGSTOP on my two capture.sh loops, between shots) so the blocking test lanes get the
  CPUs (48 of 282 files in the first 25 min). They resume after GATE-FAST-DONE.

GATE-FAST-DONE big19 @ 5993e490 (03:17 UTC). The blocking checks:
- validate_data 0/0, taskboard --check ok, dlgc 0/0, gdlint and gdformat clean, boot smoke 0 ERROR lines.
- Tools suite: 5 reds, none from the batch's merge: characters' test_asha, test_villagers and test_npc (routed);
  test_palette_check (routed to env-art) and test_screenshots (160 shots awaiting their first baselines), both known.
- **Filtered Godot tests: 282 of 436 files, 280 green**, and no script errors in any log (godot_log_check, every file).
  - test_qa_capsules: batch content, **fixed on the gate** (85b0d58b, Corrow's figure dropped from qa_known.json;
    3/0 after). creatures should take the same line.
  - test_slice_shots: "slice_dock_night_yes holds a line of its scene (ch03_dock_007)". **Known from big18**, red on
    claude/m2-slice alone, routed to m2-slice. Not blocking.
- Not run in the fast gate (non-blocking, next): the full Godot suite (incl. test_qa_threads and the water-publisher
  order question from big18), Blender for the jobs touched since lead/gate-big18, and the 254 shots (resuming now).

### After the merge (the Lead merged big19 into claude/new-session-mj8c3c @ 2f544938, 03:24 UTC)
- Shots, non-blocking, published in batches to `lead/gate-big19-shots` (`docs/kb/qa/gate-runs/big19/`):
  - 03:36 PARTIAL 101 of 254 (392108015): 53 PASS, 48 drift, 0 new. The largest drifts, noted but not judged:
    oruvel_o17_pen_split (a greyer, heavier storm sky, rmse 0.164); creature_hullgnaw (now comes up through a
    deck breach, creatures-b's M3-CRB-013); creature_oil_slug (a brighter sheen and rim, GPU QA row 40).
- Blender since lead/gate-big18 (122 jobs) is running; the full suite follows the shots. Then the rolling cadence:
  big20 about 90 min after the merge, or sooner once 3 or more tracks post new MERGE-READY lines, with one log per
  batch (`gate-big20.md`).
