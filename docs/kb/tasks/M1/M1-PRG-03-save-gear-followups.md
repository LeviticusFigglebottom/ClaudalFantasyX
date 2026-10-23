---
id: M1-PRG-03
title: Starting gear on load, EquipmentEffects lifetime (review-sweep-A)
role: progression
status: done
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
- 2026-10-23 qa (review-sweep-F, fresh reviewer): **approve-with-fixes.** I read e7a2495, the current equipment_bag.gd, equipment_effects.gd (`compose`, `modifier`, `apply_to`), party_goods.gd and the `_post_load` call sites in save_system.gd (:249, :262). Checks: validate_data 0/0; `unittest discover -s tools/tests` 300 OK; taskboard --check rc 0; `dlgc --check` 0/0; gdlint and gdformat clean. Godot: `--filter=equipment` 43/0, `--filter=save` 114/0.
  - **AC1 is met.** `grant_starting` (equipment_bag.gd:197-216) is idempotent. A hero with no loadout gets the full set once, and a hero with a loadout only gets a missing *required* slot, using the lowest-uid unworn piece first. `_post_load` runs it for `party_ids` + `reserve_ids` after `load_from_slot` and `deserialize`, but not in `slot_info`, so listing a slot never mutates anything. The order is deterministic (ascending uids).
  - **AC2 is met.** `modifier()` (equipment_effects.gd:79-81) captures `self` in the lambda, and `compose` (:63-73) reports an invalid hook both when composing and when calling it.
  - **AC3 is met in data:** `ember_pot` costs 220 (items.json:15) and is in no slice shop.
  - **Should-fix S1: the price change is not reflected in the design doc, and no request was filed.** economy.md:139 still prices "Drag Net / Quiet Tea / Ember Pot" at "80–110". The note asks Design to update it, but there is no `role: design` request task. Player-facing tooltips and balance notes get written from economy.md, so file the request (or have Progression append the row, since economy.md is append-only for non-owners).
  - Nit: `SaveShape` lets one uid be worn by two heroes, or by the wrong character. A review probe passed `loadout {rhen: {weapon: 1, armor: 1}, asha: {weapon: 1}}` with an unknown `base`. `grant_starting` (:209) then treats the slot as filled, because it only checks `has_piece`, so both heroes fight with the bogus piece. Consider `equip_error(cid, uid) == RESULT_OK` in that check (and see M1-ARC-08 F-nit).
  - Nit: `grant_starting` returns true for a hero with no loadout even when `_equip_new` fails for every slot (:201-206). The return value isn't used yet.
- 2026-10-23 lead: closing on review-sweep-F approve-with-fixes; the economy.md Ember Pot price and the equipment double-wear check are in M1-CMB-08 and M1-ARC-11.
