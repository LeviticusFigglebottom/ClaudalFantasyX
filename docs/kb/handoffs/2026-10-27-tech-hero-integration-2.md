# Handoff — tech (integration-qa, was hero-integration) — 2026-10-27 #2

## Done
- M3-HER-1121's four guards are in and green on claude/hero-integration (big12 merged in):
  - test_qa_threads: every story thread under a QaLogger;
  - test_qa_capsules: zones and their layout variants, party battle actors, foes, summons and the Vowbound;
  - test_qa_flag_reach.py: softlocks;
  - test_qa_save_shrines: Haluna's shrine plus Act I's 8 rest beats, with a save and load round trip.
- Ran them on big12 and on big12 plus each of the 8 track heads. Filed: M2-HER-1127 (slice-polish, the renamed
  offering prop) and M3-HER-1126 (creatures, the Vowbound's bodies). The Lead's capsules are KNOWN with owners.
- Viewed gpu/render-hero-integration-d443039 (Ysolde's battle model). Not approved, because it predates big12. Asked
  for a re-render at the new head.

## In progress
Nothing half-written.

## Exact next step
Approve the Ysolde re-render when the PC posts it (live log, Render requests), after viewing it. Then re-run
`--filter=qa_` on each new batch and track head.

## Known issues
- Integration still draws Ysolde as a capsule until this branch's next merge.
- M3-ARC-1216 waits on act1-chapters placing Ashcrown's flights.
- Kerrid has no exported model yet (M3-CHR-505).

## Files touched
tests/integration/test_qa_save_shrines.gd, tests/integration/test_qa_capsules.gd, tests/integration/qa_known.json,
docs/kb/tasks/M3/M3-HER-1121*, M3-HER-1125*, M3-HER-1126*, docs/kb/tasks/M2/M2-HER-1127*,
docs/kb/handoffs/live/hero-integration.md.
