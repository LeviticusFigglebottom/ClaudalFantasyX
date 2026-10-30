---
id: M5-A3P-1703
title: "Act III UI: the Kite's log: the revisits and the heirloom errands, read on the chart"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: [M5-A3P-1702]
reviewer: narrative
milestone: M5
request-from: lead
---
## Goal
ADR 0207 and the Lead's 23:26 note ("the optional-content log"). Act III opens the world (act3_ch18 §4 and §5). The
player needs one place that remembers what the Kite has seen and what still waits, without turning grief into a
checklist (act3_ch18 rule 3).

## Acceptance criteria
- [x] **KiteLogModel** (`game/ui/kite/kite_log_model.gd`), Node-free. Data: `game/data/world/kite_log.json`.
  - **Places:** the eight revisits, each listed once the chart lists it. It reads Seen once its side scene has
    played (`ch18_revisit_<town>`, newly declared), and its line says what changed there; before that, "Not visited
    since the Kite flew."
  - **Heirlooms:** one per hero, labelled "<hero>, for <someone lost>", listed once `requires_flag` is set (Pell's
    needs `ch18_pell_named`). Before `ch18_heirloom_<hero>` the line says where it waits; after, it reads Carried
    and the line says what is carried.
  - No counts and no percentages.
- [x] **KiteMapMenu:** a new row, "The ship's log", between Search and Leave, opens the log page.
  - The rows are read, not chosen from. The chart's ring points at each row's place (an heirloom's at where it
    waits).
  - Cancel, or "Back to the chart", returns to the list on the log's own row.
- [x] Loc: `KITE_LOG_*` in kite.csv. The lines are drafted from act3_ch18 §4 and §5 for Narrative to rewrite.
- [x] **tests/unit/test_kite_map.gd (15/0):**
  - the log's listing, Seen and Carried, the chart pointer, read-only rows, and Cancel back;
  - the shipped log is whole: every flag declared, every key translated, every place on the chart, eight revisits
    and seven heirlooms.
- [x] **Shot `kite_log`** (pending_baseline): rendered and viewed.

## Notes
- The revisit side scenes (`ch18_revisit_*.dlg`) don't set a flag yet. Request M5-A3P-1704 asks cinematics to set
  `ch18_revisit_<town>` when each one plays.

## Review log
