# Gate big40 (fast gate, ADR 0205)

Base: **lead/gate-big39 @ 700bf014** (the rebuilt big39's GATE-FAST-DONE tip; the Lead asked for big40 straight away).

## Pinned heads (merged --no-ff, in order; pass-7 art rows first)
- claude/env-art-b @ db144a6c
- claude/battle-presentation @ 519cbf4b
- claude/m2-slice @ e772aa1f
- claude/hero-integration @ abdd0a05
- claude/act1-chapters @ 5a166cf2
- claude/ui @ aa45f467
- claude/creatures-b @ 80af10c4

- env-art-b @ db144a6c: **row 81** (7e7a4d38: the Brine channel's banks sink flush with the flats).
- battle-presentation @ 519cbf4b: **row 61 signed off on big38** (0afcaf44: the Undertow's Reach lit, with a moonlight rim and key). 34bb40ca was already in.
- m2-slice @ e772aa1f: slice-polish's row 75 note (on the PC's big38 still: 34% dark, the hull reads).
- env-art: **no new commits.** The Lead's "env-art 2a0e5c12" isn't on any branch (unknown object); it goes in when pushed.
- **characters: held at b0cf4111** (in big39). Its head still carries the Act III WIP: `assets/characters/props/act3/` with no PROVENANCE
  rows, and e12c0305e parks the Wardens' entries. There are no new Act I rows past b0cf4111. It comes back once the rows exist.
- Held out: claude/act2-plan (not yet rebased onto act1-chapters' Ch17).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1106 files) · test_gdignore_imports OK · no
conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids. The characters WIP (c61187ce) didn't come in through any branch.

GATE-BUILT @ 5bf99483

## Fast gate
- Selected: 43 test files.
- Lane A (mine): 22; lane B (GATE-HELPER): 21, in `gate-big40-lanes-b.txt` @ 9c120402.

## Mid-batch (the Lead, 05:22): the rest of the pass-7 Act I fixes
- Already in: battle-presentation 519cbf4b (row 61), creatures-b d17cb8db (the Surge rim), act1-chapters 5a166cf2, env-art-b's rows 78/81, ui's
  newest (the flight card), slice-polish's row 75.
- Merged after lane A finished: **env-art @ 210b792e** (rows 24 and 47, 8f0b0188: the wake's lamps line the dock; the ferry landing lit) and
  **characters @ ea01d1c0** (row 54: a backing sheet under Sefir's front falls; row 55: Fenn's and Sabe's white hair). characters' head now
  **meets the guardrail**: 33fe3223 adds the Act III props' PROVENANCE rows and import files, and e12c0305 parks the Wardens' jobs until
  their clips land. After the merge: validate_data 0/0, test_blender_builds 28/0, test_stillguard 18/0, test_gdignore_imports OK.
- Re-gate (7 files, fresh import): all green; import and boot clean; `Parameter "t" is null`: not seen.

## Fast-gate results
- Lane A (mine, 22 files): all green. Lane B (GATE-HELPER, 21 files @ 9c120402, arrived 05:07): 20 green.
  - **test_battle_party_kits** 4/1: Act III foes' melee skills have no run at one hero (hesper_oan wardens_go_home; cage_orin, cage_halde,
    cage_isse and cage_cael cage_chains). Red on claude/act1-chapters alone (probed; the Wardens are its 28014519, M5-A3P-1009). Routed:
    **act1-chapters** (run staging with battle-presentation).
- Tools suite (221 units): **test_ch08_flow is green now**. test_hero_locomotion re-run on the final tree: FAILED (test_hero_locomotion). The rest is the routed set
  (test_status_names: ui; test_freed_cast_lint: audio; test_creatures: creatures-b; test_cutscene_sfx_files, test_villagers, test_hero_clips).
  Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ fc85ef70 (merge-approved: no batch-caused red). In: PC pass-7 Act I rows 24, 47, 54, 55, 61, 75, 77, 78, 81 and
the Surge rim. Held out: act2-plan (not rebased). Routed: act1-chapters (test_battle_party_kits), plus the standing list.
