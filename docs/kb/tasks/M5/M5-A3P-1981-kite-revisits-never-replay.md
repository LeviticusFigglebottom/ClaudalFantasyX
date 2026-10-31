---
id: M5-A3P-1981
title: "Open-world unlock: a Kite revisit never replays a chapter's arrival (data guard)"
role: qa
status: review
owner_session: "hero-integration (claude/hero-integration, 2026-10-30)"
depends_on: [M3-UI-205]
milestone: M5
---
## Goal
Once the Kite flies (Ch18, "the world opens"), every place in `kite.json` can be revisited with the story done. A
zone story's `arrive` row that still holds would replay that chapter's arrival: its `chapter` step would roll the
chapter number back, and its `battle` would refight.

## Acceptance criteria
- [x] `tools/act3/kite_revisit_check.py`: under the most-advanced state (every flag any chapter step, battle,
      trigger, `.dlg` or script can set, plus `kite_flying`), no `arrive` row of a destination's or secret's zone
      holds.
- [x] `tools/tests/test_kite_revisit_check.py` covers the fixtures and the repo (5/0). Today it reports 0 problems
      over the 8 destinations.
- [ ] When the Act III chapters land (Ch18 and later), a `ch18` chapter_select start with the full flag list would
      let the runtime smoke (`act1_gate_check`-style) land at each destination too. That's a follow-up once the
      chapters exist.

## Notes
- 2026-10-30 (hero-integration):
  - Leaving out the `.dlg` and script flags (86 flags rather than 225) makes Corrow's
    `reach_survived && !wall_fell` row hold, so the check does see a replay when a flag can't be set.
  - Paired with M5-A3P-1980, the landing guard. Reviewer: qa.

## Review log
