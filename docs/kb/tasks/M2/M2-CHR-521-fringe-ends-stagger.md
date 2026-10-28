---
id: M2-CHR-521
title: "Liss's and Rhen's fringe: the crop cards end staggered, not on one hard line"
role: character
status: review
owner_session: "characters (branch claude/characters)"
depends_on: [M3-CHR-03]
milestone: M2
request-from: ""
reviewer: rendering
---
## Goal
The first Liss render (liss_review.md) showed her fringe as a hard, banded edge, a helmet line across the forehead.
Rhen's approved face shows the same edge. The cause: every crop card that reaches the hairline stops there (the same
spill for every card), and the stopped card's remaining segments pile up on that line, so the texture's strand ends
compress into a band.

## Acceptance criteria
- [x] Each crop card has its own spill past the hairline (`FRINGE_STAGGER` × `FRINGE_SPILL`), and a card that stops is
      cut where it stopped, its V range cut with it (`liss_hair._trace`; `rhen_hair._trace_kept`/`_emit_kept`, with
      `rhen_hair._trace` unchanged for its other callers).
- [x] `verify --job liss` and `--job rhen` identical on native, X86_V4-off and X86_V3+V4-off; rig probe clean.
- [ ] The PC render shows a broken, natural fringe line (liss_face, liss_face_stylized, rhen_face_neutral,
      rhen_face_smile, and the full-body shots that show the head).

## Notes
- Filed and done 2026-10-27 by the characters track (the backlog's "parts look primitive" audit).

## Review log
- 2026-10-28 characters: verify --job liss and --job rhen identical on all three numpy paths. MERGE-READY; the render is requested (liss_face, liss_face_stylized, rhen_front, rhen_face_neutral).
