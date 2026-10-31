# Gate big38 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ f5305b15 (Merge lead/gate-big37).

## Pinned heads (merged --no-ff, in order)
- claude/act1-chapters @ 0d67fa13
- claude/env-art @ 8711ab0d
- claude/env-art-b @ 4654e48c
- claude/battle-presentation @ aa7cedc0

- In: Act II **row 86** (env-art 2707ac2a, still water without white flakes and Ossa Fen's mud; env-art-b baf421df and 5628c704, the
  Lamp Archive's marble and the Lacquer Court's fills) and **row 87** (battle-presentation f5aa0d78, the Ram's intro framing measured at
  3 ms behind the fade; a GPU trace is asked for). env-art's 8711ab0d raises a LEAD-ASK in its own log (Lowlight's floor patch).
- **Priority Act I fixes not posted yet:** act1-chapters' test_ch08_flow and test_act1_flow_audit (both still red at its head
  0d67fa13), integration-qa's test_clean_shutdown, and characters' rig and clips (neither branch has new commits). A watcher is on
  all three; each is merged between test runs, then a fresh import and a re-gate.
- **Held out:** claude/act2-plan, still not rebased onto act1-chapters' Ch17 (30 conflicts in a dry run).

## Resolutions
- Every merge was clean. flags.tres went through merge_union (the 2 real bases); no flag was dropped or duplicated.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1096 files) · test_gdignore_imports OK
· no conflict markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ 665ebfa0

## Fast gate
- Selected: 0 test files.
- Lane A (mine): 0; lane B (GATE-HELPER): 0, in `gate-big38-lanes-b.txt` @ bdfd9311.

## Mid-batch merges (Godot idle; each followed by a fresh import and a re-gate)
- claude/hero-integration @ ba89bad0: **row 85's test fix**, child Godot launched through the fetched build's wrapper when started via its
  loader. claude/characters @ 10811699: row 56 WIP (Asha's hem carries momentum in walk and run). Re-gate: test_scene_router_swap 17/0,
  test_battle_return 2/0, **test_clean_shutdown 1/0** (green now). Import and boot clean; `Parameter "t" is null`: not seen.
- claude/act1-chapters @ 4108b7fb: da1258a0 (M5-A3P-1017: the Act III VFX gaps explained; the Act I audits skip later acts' rows) and the
  Ch20, Ch21 and Ending flows. Now green: **test_act1_flow_audit, test_act1_audio_audit, test_battle_vfx_coverage**.
  - Still red: **test_ch08_flow**: `ch08.json: zones.ch08/corrow.arrive[0].steps[3]: unknown location 'ch18/kite'`. It comes from
    act1-chapters' b9ba89ca (M5-A3P-1004), already on integration since big37, and the ch18/kite zone is act2-plan's held-out Ch18 Kite work.
    Not batch-caused. Routed: **act1-chapters** (declare the location, or wait for act2-plan's rebased Ch18).
- characters' later row 56 commits (4293ae37, a480b2cb, the viewed run sheet) go to big39.
- act1-chapters re-gate (18 files, fresh import): **all green**; import and boot clean; log check 0; `Parameter "t" is null`: not seen.

## Fast-gate results
- Godot: no file selected at the pin (lighting and material data only); every mid-batch re-gate is green (3 + 18 files).
- Tools suite (221 units; it overlapped the mid-batch merges, and the audits were re-run green on the final tree):
  - **Now green:** test_act1_flow_audit, test_act1_audio_audit, test_battle_vfx_coverage (act1-chapters' da1258a0), test_clean_shutdown
    (Godot, integration-qa's ba89bad0) and test_rig_integrity Asha.
  - **test_hero_locomotion**: red on claude/characters alone (both at the merged 10811699 and at its head 5880037c): row 56 WIP. Routed:
    **characters**.
  - test_ch08_flow: `unknown location 'ch18/kite'` (on integration since big37; the zone is act2-plan's held-out Ch18). Routed:
    **act1-chapters**.
  - Still routed: test_status_names (ui), test_freed_cast_lint (audio), test_creatures (creatures-b), test_cutscene_sfx_files,
    test_villagers and test_hero_clips (act2-plan's Act III, and characters' clips). Known: test_palette_check, test_screenshots.
- integration-qa has posted no culprit for the big37 return regression yet. env-art-b's row 78 fix (e36768b0) and characters' hem
  follow-ups landed after the pin; they lead big39.

GATE-FAST-DONE @ 71bf9d68 (merge-approved: no batch-caused red). In: rows 86/87, row 85's test fix, and act1-chapters'
Act I audit fixes plus its Ch20/Ch21/Ending flows. Held out: act2-plan (not rebased). Routed: characters (test_hero_locomotion), act1-chapters
(test_ch08_flow), ui, audio, creatures-b, act2-plan (as listed).
