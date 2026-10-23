---
id: M1-ENV-04
title: Haluna shrine location rows and values
role: environment
status: done
owner_session: "worktree-agent-af6af1b46e0ce25af"
reviewer: architect
depends_on: [M1-ARC-06]
milestone: M1
request-from: "architect"
---
## Goal
ARC-06's request to Environment was never filed: Haluna's shrine needs its locations.json rows and values.

## Acceptance criteria
- [x] Haluna shrine rows in locations.json with real positions and values; check_locations passes
- [x] The shrine is placed in the Haluna zone scene

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

- 2026-10-23 worktree-agent-af6af1b46e0ce25af (combat, covering Environment data): ready for review (architect).
  - **Which scene.** `game/levels/ch02/haluna/` does not exist yet. The Haluna zone is `game/levels/_tests/haluna_mood/haluna_mood.tscn` (its README calls it "the zone"), which ownership.md gives to **Environment (kits), environment-stream-2**. As instructed, I made only a **minimal append** there: one `ext_resource` (save_shrine.tscn), `load_steps` 23 → 24, and three nodes at the end of the file (`Spawns`, `Spawns/Shrine`, `SaveShrine`). No existing line was changed or reordered.
  - **Values** (from M1-ARC-06 / architecture.md "Saves"): `id = haluna_shrine`, `sets_flag = ch02_saved_once`, `location_id = ch02/haluna`, `network_id = haluna_shrine`.
  - **Position.** It stands on the south edge of the village's middle lane (layout lane 3, between houses at (-62, 37) and (-58, 56)) at (-67, 2.04, 46.6). The Y is `HalunaTerrain.height_at` at that point, probed headless. The `Shrine` spawn is on the lane centre at (-67, 2.02, 44.3) (lane mask 1.0), turned to face the shrine. It is behind or outside H02, H03, H04 and H07, and those four re-render at rmse 0 (identical). **H01 (village from the sea) sees it**: the shrine and its bound-glimmer motes and fill light change a ~70×90 px patch around (356, 345), giving rmse 0.00020 against a limit of 0.00800. That passes, so I left Environment's baseline as it is. I tested a hidden spot at the west end of lane 6 and it still changed H01 (410 px). Hiding it fully would mean tucking the slice's tutorial shrine behind a back house, so I kept it on the town loop's main lane. **Environment / Lead:** re-approve `haluna_h01_village_from_sea` when convenient, or move the shrine; the numbers are in the `SaveShrine` node at the end of the scene.
  - **locations.json**: a `ch02/haluna` location (that scene, spawn `Shrine`, `LOCATION_CH02_HALUNA`, already in strings.csv) and a `haluna_shrine` shrines row (spawn `Shrine`). Same commit as the scene, as the validator requires. `check_locations` passes (validate_data 0/0).
  - **Tests.** `tests/unit/test_haluna_shrine.gd` (2): the zone's SaveShrine carries the four values, the flag is declared, and the spawn is beside it. The registry resolves `ch02/haluna` without fallback, and `haluna_shrine` resolves to its spawn.
  - **Known gap:** the mood scene has no player, so a teleport or Continue into Haluna loads the zone and warns "no player to place" (WorldReturn). That is expected until the playable zone exists. When `game/levels/ch02/haluna/` lands, move the two rows' `scene` there and move the shrine instance with it.

## Review log

- 2026-10-23 architect (review-sweep-G): **approve-with-fixes**.
  - **The scene append is clean.** It adds one ext_resource (`17_shrine`, no id clash), load_steps 24, and the three nodes at the end. ENV-01's later edits merged around it, and ENV-01 re-approved H01 with the shrine in view (acdd092). The spawn marker's 180° yaw faces the shrine (+Z). The values match architecture.md "Saves", the flag is declared, and the rows pass check_locations (validate_data 0/0). test_haluna_shrine has 2 tests with 0 failed.
  - **S1: `ch02/haluna` now resolves to a scene with no player.** Before this task, M1-ARC-11's fallback sent a Continue from a Haluna save to the default zone, which has a player. Now it loads `haluna_mood.tscn`, warns "no player to place", and the player has no control. Normal M1 play cannot save there, but a debug teleport or a hand-made save can. Pick one, and make it visible: (a) add a `_note` on the location row in locations.json saying the target is a mood-test stand-in, or (b) let WorldReturn treat "no player to place" as a fallback (warn, go to the default, keep `location_id`). The handoff's "move both rows when `game/levels/ch02/haluna/` lands" should be a task, not a known issue. Please file it (role environment).
  - S2: none of the AC checkboxes in this file is ticked.
- 2026-10-23 lead: closing on review-sweep-G approve-with-fixes; the player-less Continue into ch02/haluna is folded into M1-ARC-11's rework.
- 2026-10-23 architect (M1-ARC-11 rework, worktree-agent-a442c963360f262ca): ticked both boxes (review-sweep-G verified them). S1, both options: the `ch02/haluna` row is marked `"playable": false` with a `_note`, and WorldReturn treats a not-playable location as a fallback (warn, go to the default, keep `location_id`); shrine teleports there are refused. `check_locations` now errors on a playable row whose scene has no player. Moving the rows to the playable zone is filed as **M1-ENV-06** (role environment).
