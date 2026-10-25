---
id: M2-MNU-08
title: Light Step: encounter_rate_pct feeds the field encounter meter
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-02]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
EquipmentEffects.encounter_rate_pct (Light Step) is computed but the field encounter meter never reads it.

## Acceptance criteria
- [x] The field encounter meter scales its danger gain by the party's worn encounter_rate_pct.
- [x] Tests; the owning track (m2-slice) told.

## Notes
- **Already there:** m2-slice's M2-FP-25 `FieldEncounters` (game/world/zone/field_encounters.gd) stretches each encounter gap by `100 / encounter_rate_pct`, read once at zone setup from `Game.state.party_ids`.
- **What was missing, now fixed (smallest change to their file):** (1) gear changed in the field never reached the gap in progress: the meter joins group `field_encounters` and `refresh_rate()` rescales what is left of the gap by old/new rate (no new rng draw, so runs stay deterministic); `EquipMenu.close()` calls the group. (2) With no joined party (the first playable), the rate counted nobody: it now falls back to `FieldMenuModel.field_heroes()`, the same heroes the field menus show.
- **Tests:** tests/unit/test_light_step_rate.gd (3): Light Step on worn armor gives the ability's rate for the stand-in party; the rescale math (half rate doubles what is left; same rate no change; a passed gap stays due); closing the Equip page refreshes a live meter. Also `--filter=equip` 66/66, `--filter=zone_story` 13/13, `--filter=equipment_effects` 12/12; gdlint/gdformat clean; validate_data 0/0.

## Review log
