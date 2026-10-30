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
LEAD-ASK: test_screenshots and test_palette_check come from the big17 approvals meeting the tracks. `slice_end_card`
is approved, but m2-slice's M3-CIN-1233 marks it pending (new content), so either the approval goes or the pending key
does. The approved `haluna_h07_chapel_court` fails its palette check (ΔE 0.042 > 0.03). I'm not changing either on
the gate.
