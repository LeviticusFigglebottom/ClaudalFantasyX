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
