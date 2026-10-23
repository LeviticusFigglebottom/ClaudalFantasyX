---
id: M1-ARC-11
title: Save and camera fixes from review-sweep-F
role: architect
status: review
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
