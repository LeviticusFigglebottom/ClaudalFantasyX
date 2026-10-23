---
id: M1-PRG-03
title: Starting gear on load, EquipmentEffects lifetime (review-sweep-A)
role: progression
status: review
owner_session: architect-stream-6
reviewer: qa
depends_on: [M1-PRG-02]
milestone: M1
request-from: "combat"
---
## Goal
Review-sweep-A findings on PRG-02 outside the engine.

## Acceptance criteria
- [x] After loading any save, grant_starting fills any missing required slots for joined party members (fixes migrated v2 saves)
- [x] EquipmentEffects modifier keeps its owner alive (no silent no-op when unreferenced); a test proves it
- [x] Ember Pot placement or price decided for the slice shops

## Notes
- 2026-10-23 architect-stream-6 (with M1-ARC-06, the same save path): ready for QA.
  - `EquipmentBag.grant_starting` is idempotent. A hero with no loadout gets the full starting set. A hero who has a loadout only gets a missing required slot filled, using an owned unworn piece first. `PartyGoods.ensure_starting_gear(state)` runs it for `party_ids` + `reserve_ids`, and `SaveSystem` calls it after every `load_from_slot` and `deserialize`. Tests: v2 → load gives weapons, a second load adds nothing, optional slots stay empty, and a vanished weapon is replaced.
  - `EquipmentEffects.modifier()` returns a hook that owns its EquipmentEffects. `compose()` now pushes an error for an invalid hook instead of skipping it silently. Tests: an unreferenced `EquipmentEffects.new(...).modifier()` still applies the harness through the engine, and a bare `apply_to` Callable is shown to die with its owner.
  - **Ember Pot**: the price is now 220 (was 110), and it stays out of the slice shops. Fixed defence-ignoring fire damage at rank 2 would undercut the role-answer lesson at 110. At the Quickwater tier it is a deliberate emergency buy, and its text points to the Pemakar kilns, so it belongs in Pemakar's shop. **Design** should update the Ember Pot row in `economy.md` (I can't edit it from this stream).

## Review log
