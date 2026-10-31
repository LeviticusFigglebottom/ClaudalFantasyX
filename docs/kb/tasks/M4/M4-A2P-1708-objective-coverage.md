---
id: M4-A2P-1708
title: "Objective coverage: every mapped Act I and Act II zone has a main objective; the empty line only when nothing calls"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
cloud-qa found Ch6's objective line reading "No errand calls just now" with no marker. act1-chapters is adding the Ch6
and Ch8 rows. ui-menus checks that the line and the Where-to-next card handle them, and that the empty line only shows
when nothing is pending.

## Acceptance criteria
- [x] ObjectiveHud: the line slides in by itself only when an objective applies; the empty line (OBJ_NONE, or the
      zone's idle_keys line) waits for the button. Checked: test_objective_coverage::test_the_empty_line_waits_for_the_button.
- [x] Guard: every location with a zone map (prologue to Ch13) has at least one main objective row
      (test_objective_coverage). Brine Shoals, Corrow and the Coilspire are KNOWN_EMPTY until act1-chapters' rows land.
- [x] New rows need nothing from the UI: ObjectiveTracker reads them, and validate_data checks their targets.

## Notes
- **Mid-zone gaps found, for act1-chapters to check** (a main row's `until` that no later row in its zone requires,
  outside a chapter's end; the line goes empty there unless a cutscene bridges it):
  - ch04/haluna_wake `w_wall` until `ch04_shell_set`, then `w_sleep` requires `ch04_dock_comforted`;
  - ch05/pemakar `p_crown_bell` until `ch05_met_kerrid`, then `p_harbour_road` requires `ch05_after_seen`;
  - ch07/tamsule_bell_galleries `g_rim` until `ch07_tidecup_played`, then `g_to_port` requires `ch07_tavi_withdrew`;
  - ch09/corrow_night `c_landing` until `ch09_ebbing_danced`, then `c_road` requires `ch09_pell_joined`.

## Review log
