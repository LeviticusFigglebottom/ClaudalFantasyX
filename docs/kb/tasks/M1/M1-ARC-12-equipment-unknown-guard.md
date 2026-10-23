---
id: M1-ARC-12
title: Never drop equipment when the item tables are missing or fail to parse
role: architect
status: review
owner_session: "worktree-agent-a5a8cfa05f7795b89"
depends_on: [M1-ARC-11]
milestone: M1
request-from: "qa"
reviewer: qa
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [x] MUST: if item tables are empty or failed to parse, no loadout repair runs and no save is written over a slot (a guard plus a loud error); test with a broken equipment.json
- [x] Unknown item ids are kept in the bag as unknown pieces (round-tripped untouched) rather than dropped; only equipping them is refused
- [x] A confirmed manual save over a newer build's slot keeps a numbered copy (S2)
- [x] ADR 0018 amendment wording corrected (~:61 'at worst a hero's piece comes off')
- [x] Nits: the battle_engine petrify literal comment; `Narrator (asha)` with a space errors; the validate_data player-detection handles instanced players

## Notes
- 2026-10-23 architect (worktree-agent-a5a8cfa05f7795b89): ready for review (reviewer qa).
  - **MUST:** `ItemDB.load_dir` records missing or unparseable tables in `load_errors`. `integrity_problem()` also flags an equipment table with no equipment, gear types or equip slots. While `SaveSystem.item_tables_problem()` is non-empty, `_post_load` runs no repair and no starting gear (push_error), and `save_to_slot` returns `ERR_UNCONFIGURED` (push_error) before touching any file. Tests: test_save_item_tables.gd, covering a torn, a missing and a hollow equipment.json, a byte-identical slot 1 and slot 0, a refused autosave, and the whole bag back with the real tables.
  - **Unknown ids are kept:** `repair_loadout` deletes nothing. A worn unknown piece comes off. `equip_error` returns `unknown_equipment`, `pieces_for` hides the piece, and `unknown_uids()` lists it. A save and reload round-trip is untouched (test_save_item_tables, test_equipment, test_save_shape).
  - **S2:** a `STATUS_NEWER` slot is moved to `.newer`, `.newer.2`, … before a write (manual confirmed and New Game autosave).
  - **ADR 0018 Amendment 4** (append-only) corrects Amendment 3's Consequences.
  - **Nits:**
    - The engine uses `PETRIFY_ID := String(BattleCombatant.STATUS_PETRIFY)`, and the combatant comment is reworded.
    - dlgc: `Narrator (asha)` and `Narrator (asha) The bell.` now error with the no-space hint.
    - `scene_has_player` follows instanced sub-scenes (group "player"), inherited scenes, and a root script's `place_at`.
  - **Gate:** `HYMN_SHOTS=boot_title,save_shrine_field tools/ci_local.sh` passed every step (883 Godot tests, 0 failed; coverage within baseline; 2 shots compared, 0 failed).
  - **Not done (not in the ACs):** the `"rhenn": {}` empty loadout entry for an unknown hero is still saved.

## Review log
