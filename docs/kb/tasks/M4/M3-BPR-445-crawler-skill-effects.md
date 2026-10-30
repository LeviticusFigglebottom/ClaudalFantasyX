---
id: M3-BPR-445
title: "Request: effects ids for the conduit crawler's brush_jab, crawler_mend and crawler_tend"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-022]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation (the Lead's 10-30 12:08 list, item 2, from creatures' audit). big22's gate counted six Act II
foe skills with no `effects`. Integration has since mapped three, so on the chapters head (after merging
claude/new-session-mj8c3c, 10-30) only the conduit crawler's three remain. That crawler is the Lamp Engine's tender
(plan/act2/bosses/lamp_engine.md §4):
- `brush_jab` (physical, single_foe): the brush arm cocks back and jabs. A short brass-bristle swipe; `hit_none` is fine.
- `crawler_mend` (support, single_ally, `restores_part`): it relights a broken ring. M3-BPR-441 already covers the
  part relight on `part_restored`, so this cast only needs a small cast-side spark on the crawler.
- `crawler_tend` (support, self): it tends the engine and pays the party no mind. A quiet idle shimmer, or an explicit
  `"effects": "none"` row if the coverage tool should accept that silence on purpose.

## Acceptance criteria
- [ ] Each of the three has an `effects` id (or an intended-none row) and tools/battle_vfx_coverage.py reports no Act II
  foe skill gap.

## Review log
