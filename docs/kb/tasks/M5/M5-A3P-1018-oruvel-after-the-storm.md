---
id: M5-A3P-1018
title: "Request (environment + act1-chapters): Oruvel after the storm, for Ch18's revisit: the rebuild begun, no Kell, and a Kite destination"
role: environment
status: todo
owner_session: ""
depends_on: [M5-A3P-1004]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
`ch18_revisit_oruvel` (act3_ch18.md §4) is the last Ch18 revisit without a place to play. `ch01/oruvel` is the raft-town on the day before the storm (Ch01Zone, with no states or variants). In Ch18 it would still show Kell at her stall, and Act III's rule is that Kell is never seen (act3_ch18.md §10 Q3).

## Ask
- **Environment:** Oruvel some months after the storm.
  - New hulls lashed to the old keel-hull, and Kell's stall an empty frame on the second mooring.
  - None of Ch1's cast, except Tavi when `ch07_told_tavi` is set.
  - Either a new location (for example `ch18/oruvel_rebuilt`) or a variant of `ch01/oruvel` keyed on `ch18_started`. A variant needs Ch01Zone to gain states or variants (act1-chapters).
- **UI data:** a `kite.json` destination for it, `requires_flag: ch18_world_open`.
- **Story, once that exists (act2-plan):**
  - the marks `kell_stall` and `kell_stall_b` (Rhen and Tavi), the shot K18, and Tavi cast as `tavi`;
  - a `ch18_revisit` trigger and the block in `ch18.json`.

## Review log
