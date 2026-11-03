# Gate big46 (fast gate, ADR 0205)

Integration base: claude/undertow-lead-handoff-ze8rrn @ e2411fb0 (big45 @ c972ea42 plus the 11-03 Lead docs).

## Pinned heads
- claude/characters @ 5e9cb380: **row 56, the notch fix** that big45 said would follow (979a5482: back to the a35fe528 look the Lead approved,
  fe54e656's skirt sources and the committed GLB; in the locomotion clips the back panels keep within 12° of their neighbours and a derived panel's
  hem within 5° of its knee, so the back cloth never folds over (the white notch at profile 0 and 11); Asha's library rebuilt and committed;
  5e9cb380: test_hero_stage samples Asha's offer_hand). Not marked MERGE-READY (its log is still @ a480b2cb); taken as the follow-up big45 named.
- No other head moved since big45 (every other track is an ancestor of the integration branch; the 11-03 tracks haven't pushed yet).
  claude/combat-systems doesn't exist on origin yet.

## Conflicts
None (clean merge, 11 files).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · no conflict markers · no gate-run images.

GATE-BUILT @ d75aeefc
