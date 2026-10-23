---
id: M1-ARC-11
title: Save and camera fixes from review-sweep-F
role: architect
status: todo
reviewer: qa
owner_session: "worktree-agent-abfc1d79a20572a9b"
depends_on: [M1-ARC-10]
milestone: M1
request-from: "qa"
---
## Goal
Review-sweep-F findings on ARC-06/07/08/10 and PRG-03.

## Acceptance criteria
- [x] MUST: a leftover .tmp is never 'recoverable' over a slot from a newer build or a newer version (save_system.gd ~:190); test with v99
- [x] v2 (and every older) migration runs after, or is guarded by, shape validation; malformed old inventories read as corrupt (save_system.gd ~:368-371)
- [x] A camera director reparented mid-cutscene drops its scripted shot (or the hold) so the autosave hold cannot leak
- [x] Continue with a location missing from locations.json warns and never records a test location as the new save location (world_return.gd ~:80-102)
- [x] An equipment piece cannot be worn by two heroes or by the wrong hero; load rejects it
- [x] Second set-aside does not overwrite an existing .recovered file; same-second saves stay recoverable
- [x] ADR 0018 amendment wording matches what Continue picks
- [x] Tests for each

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

### Done (architect, worktree-agent-abfc1d79a20572a9b)
- **MUST (ARC-10 F1).** `SaveSystem.temp_is_newer(tmp, main)` now decides `recoverable`. An empty or damaged
  slot is older; a `STATUS_NEWER` slot, or a slot of a newer save version than the temp file, never is.
  `recover_temp` returns `ERR_FILE_CORRUPT` and the slot is untouched. Tests (test_save_recovery.gd): the
  reviewer's v99 probe with the temp at `saved_at` 1 and at a later time; a v3 temp beside a v4 slot; the rule
  table.
- **Migrations (ARC-08 F1).** `_migrate_v2_to_v3` converts only `SaveShape.is_whole` values >= 0 and passes the
  rest (and a non-Dictionary inventory) through, so the shape check reads the save as corrupt. v0 and v1 run
  through the same step. Test: 7 malformed inventories x v0/v1/v2, each through deserialize, slot_info and
  load_from_slot (the runner fails on any script error). This includes the three probe cases. A negative v2
  count is now corrupt instead of dropped (test_save_system.gd updated to match).
- **Camera (ARC-07 F1).** When `_exit_tree` pays an owed `blend_finished`, it also drops the scripted shot,
  so `_enter_tree` has nothing to re-hold. A settled scripted shot keeps the sweep-E S2 behaviour. New test:
  reparent with an owed blend, the documented sequencer stops on `is_leaving()`, re-add, and
  `autosave_holders()` is empty. The existing reparent test now settles first. field_camera.md says a
  reparent mid-move ends the cutscene.
- **Continue fallback (ARC-06 S2).** `WorldReturn._travel` warns, naming the missing id, when the location
  falls back, and keeps `Game.state.location_id` (the respawn was already kept). An empty location uses the
  default silently, as documented. Tests: Continue from `ch02/haluna` (warned, location kept, the next save
  records it), go_to an unknown id, and an empty location.
- **Equipment (ARC-08/PRG-03 nits).** `SaveShape` rejects a piece worn in two loadout slots.
  `_read_save` runs the new `EquipmentBag.loadout_problem()` on a copy (wearer via `equip_error`, own slot).
  `grant_starting` treats a slot holding an unwearable piece as empty. Tests: five bad loadouts are corrupt
  in listing, load and deserialize; a valid one loads; `loadout_problem` messages; grant over another
  hero's weapon.
- **Set-aside and same second (ARC-10 nits).** Set-asides use the next free name (`.recovered`,
  `.recovered.2`, ...); a same-second temp with at least the slot's play time is recoverable. Tests for both.
- **ADR 0018 Amendment 2** (append-only): Continue offers the newest `saved_at`, so a shrine save on a replayed
  older branch becomes the Continue slot; and the director's reparent rule. The toast is filed as
  **M1-UI-09** (role ui).
- Not done (nit, not an AC): `TitleMenu.start_new_game` ordering (ARC-06), `ShrineNetwork._loaded` strong refs.

## Review log

- 2026-10-23 qa (review-sweep-G): **request-changes**. Every AC is implemented and its tests pass (filtered runs with a private XDG_DATA_HOME: save 122, camera_director 34, world_return 14, equipment 44, shrine 18; all 0 failed). The v99 temp probe, the malformed v0/v1/v2 inventories, the reparent-mid-blend hold, the Continue fallback and the numbered set-asides all behave as documented. Then I tried to lose data with a scratch probe (not committed), and the new loadout check opens a path that destroys a whole save.
  - **B1 (data loss, introduced here): stale item tables make a save CORRUPT, and a CORRUPT slot is then overwritten with no copy kept.** `_read_save` now runs `EquipmentBag.loadout_problem()` against the *current* item tables (save_system.gd:318-319, equipment_bag.gd:164-181). A piece whose base was renamed or removed, or moved to another hero or slot in a later equipment.json, makes the whole save `STATUS_CORRUPT`. Then:
    - `autosave_is_further_along` treats corrupt as "never further along" (save_system.gd:528-529), so the next chapter autosave writes over it. Probe: slot 0 at ch 7 / 99,999 s wearing `old_reef_hooks` reads corrupt, a ch 2 chapter autosave returns OK and replaces it, and only `slot_00.json` is left.
    - `temp_is_newer` treats corrupt as older (save_system.gd:206-207), so `recover_temp` renames a ch 1 temp over a ch 9 slot that is corrupt only by this check. Probe: recoverable = true, recover = OK, slot replaced.
    - `lantern_staff` worn by Rhen is also corrupt (P1b). That is correct for tampering, but it is exactly what a balance patch that re-assigns a weapon produces.

    Before this task, these saves loaded. Fix (both parts, please):
    - (a) Make the table-dependent mismatches repairable, not fatal. Wrong hero, wrong slot or unknown base: unequip the piece into the bag with a warning, and let `grant_starting` refill the slot (it already treats an unwearable slot as empty). Keep the hard rejection for what no table change can cause: a piece worn twice (SaveShape already rejects it) and an unowned uid.
    - (b) Never destroy a non-empty CORRUPT slot. `save_to_slot` (the autosave) and `recover_temp` should move it to a numbered `.corrupt` copy first (the same scheme as `free_recovered_path`).
    - A test for each part.
  - **S1: the frozen v2→v3 literal changed behaviour.** A negative v2 count used to be dropped, and the old test said so explicitly (`"drag_net": -2`). Now it makes the save corrupt (save_system.gd:429). B1(b) then also applies: a v2 slot 0 with one bad stack is overwritten. Unless someone can show v2 never wrote a negative count, keep dropping whole numbers < 0 and pass through only non-whole values.
  - **S2: a temp file from a newer build is silently destroyed.** A `version: 99` `.tmp` beside an ordinary slot is `status: newer`, not recoverable, not reported at startup, and the next `save_to_slot` overwrites it with no `.recovered` copy (probe P2; save_system.gd:252-255, then :140). Set aside any temp that parses but is not older (STATUS_NEWER included), and log it in `report_leftover_temps`. This is the downgrade case the MUST was about, from the temp side.
  - **S3: Continue skips a good `location_id` when the respawn is unknown.** `WorldReturn.resolve` (world_return.gd:39-45) falls back to the default when `respawn_location_id` is stale, even when `location_id` is registered. Try `location_id` before the default. The warning and keep-the-id behaviour are correct.
  - Nits: after 99 set-asides the next temp is replaced (bounded, and it warns; fine). Continue takes the newest `saved_at`, so a save made with a wrong system clock wins forever (worth a sentence in ADR 0018). The reparent rule also drops a scripted shot that nobody awaited (fire-and-forget `play_shot` plus a timer). That is documented in field_camera.md, and the sequencer's own hold still covers the autosave.
  - Verified OK: Amendment 2 matches `TitleSaveEntry.continue_slot` (OK slots only, newest `saved_at`). `_drop_scripted_shot` runs only when an owed emit is paid. A same-second temp with less play time is not recoverable. The set-aside numbering is never overwritten. Python gates: validate_data 0/0, 322 tool tests OK, taskboard OK, gdlint and gdformat clean.
- 2026-10-23 lead: reopened on review-sweep-G request-changes (B1 data loss). Also carries NAR-10 S1/S2, the CMB-08 petrify constant and the unticked boxes, and the ENV-04 player-less Continue.
