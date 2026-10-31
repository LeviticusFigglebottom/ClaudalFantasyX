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
