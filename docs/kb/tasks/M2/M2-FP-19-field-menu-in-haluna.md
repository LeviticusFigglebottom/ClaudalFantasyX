---
id: M2-FP-19
title: The field menu in Haluna, with the real party (Asha and Toma join after Cutscene A)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: lead
depends_on: [M2-UI-04]
milestone: M2
request-from: lead
---
## Goal
The Lead's queue top-up (item e): wire M2-UI-04's field menu into Haluna. The menu's hook is in `FieldController._unhandled_input` (`ui_cancel`, under `accepts_input`), so Rhen in Haluna already opens it. What was missing is the party: the first playable never wrote `party_ids`, so the Heroes page used UI-04's fallback (first_playable.json `field_battle`).

## Acceptance criteria
- [x] Asha and Toma join after Cutscene A. `HalunaStory` fills an empty party from first_playable.json haluna `party_after_intro` (party `rhen`, `asha`; reserve `toma`, the tideline fight's own party) once `ch02_met_asha` is set. A save from after the beach with no party gets one on its next arrival.
- [x] Escape opens the field menu in Haluna's free play, never while a scene holds Rhen, and the Heroes page lists the real party.
- [x] Tests: `tests/integration/test_haluna_field_menu.gd` (3).

## Notes
- UI-04's fallback in `FieldMenuModel.from_game` is no longer reached in the slice. UI can drop it once other zones write `party_ids` too. Not touched here, because it's UI's file.
- PLAYTEST.md already has the field-menu row (UI-04).

## Review log
