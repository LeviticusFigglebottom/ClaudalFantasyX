---
id: M3-UI-1242
title: "Request: Act II chapter-closing objectives end on chNN_complete, not the next chapter's start flag"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: cinematics
milestone: M4
request-from: cinematics
---
## Goal
To ui-menus (the Lead's 10-30 12:08 list, item 4, from big22's gate). test_qa_threads requires every main objective's
`requires` and `until` in a chapter's zones to be raised by that chapter's thread. Six Act II objectives use the
*next* chapter's start flag as their `until`. That flag is set by the next chapter's arrive row, so the chapter's own
thread never raises it:

| objective | zone | until now | proposed `until` |
|---|---|---|---|
| reed_clutch | ch10/reedhollow | ch11_started | ch10_complete |
| low_sanctum | ch11/lowlight | ch12_started | ch11_complete |
| cloudloom_dais | ch12/cloudloom | ch13_started | ch12_complete |
| archive_ledgers | ch13/lamp_archive | ch14_started | ch13_complete |
| court_barge | ch13/ansedra_lacquer_court | ch15_started | ch14_complete |
| hollowmere_house | ch17/hollowmere | ch16_started | ch15_complete |

Each `chNN_complete` is declared in flags.tres and set by that chapter's closing scene: ch10_dawn_gate,
ch11_held_by_you, ch12_down_the_other_side, ch13_the_pact, ch14_left_standing, ch15_the_ship. This matches Act I's
pattern (`p_harbour_road` ends on `ch05_done`). The player sees no difference, because the objective already drops
when the closing scene ends and the next chapter starts.

Two zone-prefix notes for the same edit. The guard attributes a row to a chapter by its zone's prefix:
- court_dais and court_barge are Ch14 objectives in a `ch13/` zone. Ch13's thread is checked for ch14_started,
  ch14_declared_heretics and (after this fix) ch14_complete.
- hollowmere_house is a Ch15 objective in a `ch17/` zone, so no thread checks it.

The least invasive fix is for the guard to read an optional `"chapter"` on a row (CHAPTERS_OF-style) when its zone's
prefix isn't its chapter. Chapters can add that in test_qa_threads.gd if ui adds the field. If you'd rather not,
list those flags in qa_known.json "unraised" with this reason.

## Acceptance criteria
- [x] The six `until`s name their own chapter's `chNN_complete`.
- [x] test_qa_threads reports no Act II "never raises" failure (or only qa_known rows with a reason).

## Answer (ui-menus, 2026-10-31)
Already settled by the data. M4-A2P-109 rewrote Act II's objective rows, and none of the six ids remains. No Act II
row (a `ch1N/` zone) ends on a later chapter's `chNN_started` now; a scan of objectives.json finds none.
test_qa_threads passes 1/0 with no Act II "never raises" failure. No `"chapter"` field was needed.

## Review log
