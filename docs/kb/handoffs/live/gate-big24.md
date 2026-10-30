# Gate big24 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 8fe3644b (Merge lead/gate-big23).

## Pinned heads (merged --no-ff, in order)
- claude/hero-integration @ 7e0f4480 (PLAYTEST: row 38, the Encounter fallback moves into place_at)
- claude/env-art @ 51ac308c
- claude/m2-slice @ 1a805464
- claude/env-art-b @ 88607c44
- claude/creatures @ fbcf9ee2
- claude/creatures-b @ 2415d4f0
- claude/battle-presentation @ aa227a57
- claude/ui @ 32179772
- claude/audio @ 577a2b20
- claude/act2-plan @ cfc5658d
- No new commits: characters, act1-chapters, slice-polish.

## Resolutions
- hero-integration, `greybox_zone.gd`: theirs moves the before-any-fight fallback into `place_at` (the layout's first spawn).
  `build()` keeps act1-chapters' M3-HER-1159 rule, so a layout that names its own `Encounter` spawn keeps it, and
  otherwise it adds the origin marker for `place_at` to override. Both changes are kept.
- hero-integration, `test_qa_field_camera.gd` KNOWN: ours. The integration head had already dropped the M3-HER-1159 rows
  (act1-chapters' fix, big23), and theirs re-added them along with `coilspire.tscn:Encounter`.
- ui, `objectives.json`: ours at the ui step. ui's edit only touched the zone-level rows, and the integration head held act2-plan's
  per-chapter rows there.
- act2-plan, `objectives.json`: the owner now ships ui's 17 zone-level main rows (their 30 per-chapter main rows were dropped
  and kept in git; see act2-plan.md 2026-10-30), so I took theirs. ui's M4-UI-PLAYTEST `until: null` fix is
  re-applied on top to reed_clutch, low_sanctum, cloudloom_dais, archive_ledgers and court_barge. ui's qa_known
  `unraised` ch14_started and ch14_declared_heretics rows now match those rows.
- PROVENANCE: removed three stale duplicate rows that were already on the integration head (ysolde_theme .ogg/.loop.json
  from before M3-AUD-863; asha.glb from before the donor). No new duplicate PROVENANCE rows, loc keys or shot ids.

## Build checks
validate_data 0/0 · taskboard --check clean · gdlint clean · gdformat clean (1046 files) · no conflict markers.

GATE-BUILT @ 019596bb (merge tip; this log commit sits on top)

## Fast gate
- Selected: 71 test files (changed tests plus tests naming changed res:// paths or class_names). Lane A (mine) has 36;
  lane B (GATE-HELPER) has 35, in `gate-big24-lanes-b.txt` @ 797b02cc.
