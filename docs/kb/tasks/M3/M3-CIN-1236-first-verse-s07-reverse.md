---
id: M3-CIN-1236
title: "PC GPU QA pass 3, row 60 (slice-polish, Ch3): slice_verse_hall's camera is jammed between Rhen and Toma"
role: cinematics
status: review
owner_session: slice-polish (claude/m2-slice)
depends_on: []
milestone: M3
request-from: lead
---
## Goal
Row 60: S07 (the First Verse's opening, Asha leaving for the chamber) sat 1.6 m behind Rhen and Toma, exactly between
them, so Rhen's shoulder and Toma's shield filled both sides of the frame, and Rhen spoke from behind.

## Acceptance criteria
- [x] S07 pulls back and up to a clear over-the-shoulder on Asha (pos (-18.4, 1.75, -0.35), fov 42).
- [x] A new reverse, S07R, from inside the hall: Rhen and Toma answer her on their faces (lines 002, 004, 006);
      Asha's lines (003, 005) cut back to S07.
- [x] slice_verse_hall re-rendered and viewed: Rhen speaks in frame, Toma beside him, Asha's shoulder at the edge.

## Review log
