---
id: M1-ARC-11
title: Save and camera fixes from review-sweep-F
role: architect
status: review
reviewer: qa
owner_session: "worktree-agent-a442c963360f262ca"
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

### Rework (review-sweep-G)
- [x] B1 MUST (a): wrong-hero, wrong-slot or unknown-item loadouts are repaired on load (unequip into the bag, drop unknown ids, with a warning), not corrupt; a piece worn twice or an unowned uid stays corrupt
- [x] B1 MUST (b): no save path overwrites a non-empty corrupt slot without first moving it to a numbered `.corrupt` copy; tests reproduce the probes (ch 7 renamed weapon + ch 2 autosave; the same for recover_temp)
- [x] S1: a negative v2 (and v0/v1) inventory count is dropped with a warning; v3+ stays corrupt
- [x] S2: a .tmp from a newer build is set aside and logged, never silently overwritten
- [x] S3: Continue uses a valid location_id when respawn_location_id is stale
- [x] NAR-10 S1/S2: `Narrator(asha)` alone errors; `Narator(asha) The bell.` errors with a hint
- [x] CMB-08: one shared petrify constant; CMB-08 boxes ticked
- [x] ENV-04: Continue or teleport into a player-less location never strands the player; ENV-04 boxes ticked
- [x] ADR 0018 Amendment 3 (append-only)

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

### Rework done (architect, worktree-agent-a442c963360f262ca; review-sweep-G)
- **B1(a) repair, not reject.** `_read_save` no longer runs `loadout_problem()` (`_equipment_problem` removed).
  `_post_load` calls the new `EquipmentBag.repair_loadout()` before `ensure_starting_gear`: a worn piece that
  is known but no longer fits its wearer or slot (`misfit`: `wrong_character`, `unknown_slot`, new
  `ERR_WRONG_SLOT`) comes off and stays in the bag; a piece whose base is unknown is taken off and dropped
  (worn or not), each with a `SaveSystem: equipment.<path>: ...` warning. `grant_starting` refills the weapon
  (a fitting spare first). `SaveShape` still rejects a piece worn twice and an unowned uid. Listings no longer
  depend on the item tables at all.
- **B1(b) keep a copy.** `_set_aside_corrupt_slot` runs in `save_to_slot` (after the checked temp write,
  before the rename) and in `recover_temp`: a non-empty slot whose status is corrupt is renamed to the next
  free `slot_NN.json.corrupt`, `.corrupt.2`, ... (`corrupt_path`, `free_corrupt_path`, `MAX_CORRUPT = 99`).
  If no name is free or the rename fails, the write is refused (temp removed) and the slot kept. A 0-byte
  file is replaced without a copy.
- **Probe tests (test_save_recovery.gd).** P1: a ch 7 / 99,999 s slot 0 wearing `old_reef_hooks` lists OK, a
  ch 2 chapter autosave is skipped (`ERR_ALREADY_EXISTS`), slot 0 is byte-identical, and it loads with Rhen
  re-armed. P3: a ch 1 temp beside a ch 9 renamed-weapon slot is not recoverable and `recover_temp` refuses.
  Real corruption (a piece in two slots, `{torn`): the autosave writes, the old bytes are in `.corrupt`, a
  second one goes to `.corrupt.2`, a readable slot is never copied; `recover_temp` over a corrupt slot keeps
  `.corrupt`. test_save_shape.gd: four table-drift loadouts load (listing, load_from_slot, deserialize) with the
  weapon refilled and the piece kept or dropped; worn-twice / two-slots / unowned stay corrupt.
  test_equipment.gd: `repair_loadout` notes, idempotence, the refill from the bag.
- **S1.** `_migrate_v2_to_v3` drops whole counts <= 0 again and warns for a negative one; only non-whole values
  pass through to the shape check. The `"drag_net": -2` line is back in test_save_system.gd, plus a v3
  negative count that is corrupt; test_save_shape.gd checks v0/v1/v2 drop and v3 corrupt.
- **S2.** `leftover_temp_info` gains `keep` (`temp_worth_keeping`): recoverable, a `STATUS_NEWER` temp, or a
  readable temp beside a newer build's slot. `_set_aside_leftover_temp` uses `keep`, so those go to
  `.recovered` before the next write. `report_leftover_temps` logs every kept temp (new `kept_leftover_temps`)
  and still returns only the recoverable slots. Tests: the v99 temp probe (P2), a temp beside a v99 slot, the
  rule table.
- **S3.** `WorldReturn.resolve` tries the respawn only when `registry.can_enter` it, else `location_id` (at the
  location's own spawn), else the default; the result carries `asked` and `respawn_skipped`, and Continue
  warns once for a skipped respawn. Test: a stale respawn with a good `location_id`, then both stale.
- **ENV-04 (player-less Continue): both options.** `"playable": false` on a locations.json row (with a
  `_note` on `ch02/haluna`); `LocationRegistry.is_playable` / `can_enter`; `resolve` falls back for it with
  `reason: not_playable` (also `empty`, `unknown`); Continue and `go_to` warn "has no player to place" and keep
  the location; `ShrineNetwork.request_teleport` refuses it. `check_locations` (validate_data.py) errors on a
  playable row whose scene has no `Player` under the root and no node in group `"player"`, and on a
  non-playable `default_location` / `new_game` (tools/tests/test_locations_validate.py: 2 new tests; the
  fixture zone gained a Player). Filed **M1-ENV-06** (environment) to move the rows to the playable zone.
  ENV-04 boxes ticked.
- **NAR-10 S1/S2 (tools/dlgc.py).** New `BodyParser.narrator_identity(name, identity)`: Narrator or a Narrator
  misspelling followed by a known `(speaker id)`. It counts as evidence in `check_bare_speaker` (which now runs
  before the wrong-bracket check, so `Narrator(asha) [grief]` alone gets the bare-head fix `': ...'`) and in the
  missing-colon check. `Narrator(asha)`, `Narator(asha)`, `Narator(asha) The bell.` error with hints;
  `Narator The bell.`, `Narrator(kerid)` and `Toma(rhen)` stay narration. Test
  `test_narrator_identity_is_evidence`; dialogue_format.md has the row, the `Narrators [grief]` known limit and
  the case rule (names any case, emotion ids not).
- **CMB-08.** `BattleCombatant.STATUS_PETRIFY`, used by combatant.gd, ctb_timeline.gd, battle_vitals.gd and
  item_battle_action.gd; an order comment at `BattleVitals.setup` (S3). CMB-08 boxes ticked.
- **ADR 0018 Amendment 3** (append-only) records the repair rule, the `.corrupt` copies, kept temps, legacy
  counts, and the wrong-clock nit. architecture.md "Saves" has a sweep-G block.
- Not done: battle_engine.gd:332 still tests a JSON string array for `"petrify"` (the engine is at its size
  limit; a `String(...)` of the constant would push the line past 120). The reparent nit (a fire-and-forget
  scripted shot is dropped) is unchanged, as documented in field_camera.md.

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
- 2026-10-23 qa (review-sweep-H, fresh reviewer, re-review after sweep G): **approve-with-fixes.** Every sweep-G item is fixed, and the probes that lost a run in sweep G now keep it. I read the task, the sweep-G entry, handoff architect-12, and `git log -p` for baa537d, 3c00ab4, 8ca2ae5, 65ef881 and a48ec27.
  - **Checks run:**
    - `validate_data` gives 0/0. The tools tests give 329 OK. `taskboard --check`, `gdlint` and `gdformat --check` are clean. `dlgc --check` gives 0/0.
    - Godot runs were filtered, with a private XDG_DATA_HOME. All had 0 failed: save 132, world_return 17, equipment 45, shrine 18, haluna 2, camera_director 34, ctb 15, battle_vitals 14, battle 230, item 60, status 39, dialogue 48.
    - I also ran a scratch probe file of 7 tests (deleted, not committed).
  - **Verified with probes:**
    - **repair_loadout, not corrupt.** A known piece moved to another hero (Asha's staff on Rhen) comes off into the bag. The bag still holds 4 pieces, and both heroes are armed. A loadout for an unknown hero id (`rhenn`) loads OK, and the piece comes off. SaveShape still rejects a piece worn twice and an unowned uid.
    - **`.corrupt` before an overwrite.** A v3 save with a negative count reads corrupt, and the chapter autosave over it keeps a byte-identical `slot_00.json.corrupt`. A torn slot with a v99 `.tmp` beside it, then a manual save, keeps both `.recovered` and `.corrupt`. A readable slot is never copied.
    - **Legacy counts.** In v2, `-2` is dropped with a warning, `3.0` loads as int 3, and `0` is dropped. `-2.5` is corrupt. In v3, a negative count is corrupt.
    - **Newer-build temps.** A v99 `.tmp` beside an empty slot is `keep` and not recoverable, and the next save sets it aside byte for byte. The same holds beside a corrupt slot.
    - **Continue and `"playable": false`.** Continue with a stale respawn tries `location_id` first. `ch02/haluna` is never entered: Continue warns and keeps the location, and teleports are refused. `check_locations` requires the mark, and its two tests pass.
    - **dlgc.** I re-ran the narrator lines myself. `Narrator(asha)`, `Narator(asha)`, `Narator(asha) The bell.` and `Narrator(asha) [grief]` all error with the documented hints. `Narator The bell.`, `Narrator(kerid)` and `Toma(rhen)` stay narration. `NARRATOR(ASHA): The bell.` is accepted.
    - **STATUS_PETRIFY.** It is used in combatant, ctb_timeline, battle_vitals and item_battle_action. The battle, item and status tests are green.
    - **ADR 0018 Amendment 3** matches the code, except for the Consequences sentence below.
  - **Should-fix:**
    - **S1 (data loss, new path; land it before any build whose saves testers keep). If the item tables fail to load, the next load wipes the whole equipment bag, and the next save makes the loss permanent.**
      - How it happens: `ItemDB.load_default` turns an unparseable table into `{}` with only a push_error (item_db.gd:49-53). `_post_load` then runs `repair_loadout` against that DB (save_system.gd:451-457). Every owned piece reads as an unknown base and is dropped (equipment_bag.gd:207-211).
      - Probe H-P1 (`SaveSystem._item_db = ItemDB.from_tables({})`): a ch 6 slot with four pieces, one of them customised, loads with `owned` = {}. After `save_to_slot` and a reload with the real tables, only the two re-granted starting pieces remain. There are 7 warnings and no copy.
      - Probe H-P2: a single unworn spare whose base was renamed is dropped the same way, slot abilities included, and the next save makes that permanent. That is what the sweep-G AC asked for ("drop unknown ids"), but it is the one repair that destroys data.
      - Fix, at minimum: skip the unknown-base drop when the DB has no equipment rows, or when any table failed to parse. Better: keep unknown pieces in `owned`, unworn and hidden by `pieces_for`, so that a later build which restores or aliases the id gets them back.
      - Then correct ADR 0018 Amendment 3's Consequences ("at worst a hero's piece comes off", 0018:61). Today an unknown base is dropped from the save, not taken off.
    - **S2. A confirmed manual save over a newer build's slot keeps no copy (probe H-P6).** A corrupt slot now always gets a `.corrupt` copy. A v99 slot, which a newer build can read in full, is replaced outright after `SAVE_CONFIRM_OVERWRITE_NEWER`. Give it the same numbered copy (for example `.newer`) in `_set_aside_corrupt_slot` (save_system.gd:356). It costs one status test, and it is the downgrade case from the slot side.
  - **Nits:**
    - combatant.gd:12-13 says "The one copy in code: the engine, the timeline and BattleVitals all use it", but battle_engine.gd:332 still tests `"petrify"`. That is documented in the handoff. Reword the comment, or add a local `const PETRIFY_ID := String(BattleCombatant.STATUS_PETRIFY)` to the engine.
    - `Narrator (asha)` and `Narrator (asha) The bell.`, with a space before the parenthesis, still ship as raw narration. The colon form `Narrator (asha): ...` already errors with the no-space hint, so the bare and missing-colon heads could reuse it. This is the same class as NAR-10 S1/S2.
    - `repair_loadout` leaves an empty loadout entry for an unknown hero id (`"rhenn": {}`). It is harmless, but it is saved forever.
    - `scene_has_player` (validate_data.py:1299) only sees a `Player` directly under the root, or a group set in the level file itself. A player inside an instanced sub-scene, or a zone that places its player through `place_at`, would be a false error. The rule is conservative, so this is acceptable for now; note the limit in the function's docstring.
  - **To close:** S1 (the empty-table guard at minimum, plus the ADR wording). S2 can be a follow-up task.
