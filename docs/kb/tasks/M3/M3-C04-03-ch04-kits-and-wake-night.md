---
id: M3-C04-03
title: Ch4 kits swap-in (the ferry, the derelict, the islet landing) and Haluna's wake-night dressing
role: environment
status: todo
owner_session: ""
depends_on: [M3-C04-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch4's two zones are greybox blocks: `game/levels/ch04/haluna_wake/` (a stand-in for Haluna's night) and `game/levels/ch04/brightwater_ferry/`. Their story data doesn't depend on the blocks. Swap in what act1_ch04.md §9 Environment Art asks for:
- **`ch04/brightwater_ferry`:** the islet's seaward landing; the ferry *Kind Weather* (deckhouse with a small Order shrine, passenger awning, lashed cargo, the skiff on davits, a lookout's perch); the derelict *Seventh Terrace* alongside, built once with Ch1's (its name-board is the Ch1 O07 hero prop, D06 must match O07), with sails set and a lowered state, spawn membrane in the rigging, fenders and boathooks between the hulls, never a lashing; the open strait.
- **Haluna's wake night:** on M2-ENV-02's night lighting, the windows unlit with per-window toggles (C4-01), the causeway head as a feast with about 100 oil lamps, Asha's shell in the gap (state `ch04_shell_set`) beside Imra's with faded and re-inked states, Ysolde's ink kit, the dock with no lamps, and the dawn wall with guttering lamps.
- The `brightwater_ferry.md` environment sheet with shots F01–F06 and D01–D08, and haluna.md §5.1's H12–H16.

Keep every spawn, mark, trigger, shot and `states` id (Ch04Zone hides and shows them by flag). When the dressing lands on the real `ch02/haluna`, the chapter's `ch04/haluna_wake` block can move there with Haluna's move to ZoneStory (ADR 0035); until then the stand-in stays.

## Acceptance criteria
- [ ] Both zones play `tests/integration/test_ch04_thread.gd` unchanged.
- [ ] Every route can be walked with the kit's collision, and the ferry and the derelict stay unjoined (ADR 0017 (d)): rails, no walkway.
- [ ] The shots are composed on the kit; H13 is never on the `ending_dock` axis.

## Notes

- **env-art, 2026-10-27 (the kit side is done; the rest is placement):**
  - **The ferry and the derelict:** the Brightwater ferry kit (M3-ENV-08; sheet `brightwater_ferry.md`, shots F/D),
    including the Seventh Terrace and the transom winding (M3-ENV-700).
  - **Haluna's wake night:** M3-ENV-709, in the dresser's story sets: the causeway-head feast lamps; Asha's shell
    beside Imra's, faded and re-inked; the night lamps per house (M2-ENV-02, `set_night_lamp`).
  - **What's left is placement,** which is act1-chapters' under ADR 0200 (ZoneKitDressing), as for Ch5–Ch9.
    act1-chapters' log keeps `haluna_wake` on the real Haluna once it is ZoneStory (slice-polish). For the Lead:
    re-route this task, or close it into act1-chapters' swap task.

- **env-art, 2026-10-28 (ADR 0041):** the wake night is dressed on the greybox stand-in itself
  (M3-ENV-743, mount request M3-ENV-744 to act1-chapters), so Ch4 needn't wait for Haluna's ZoneStory move.
  The ferry zone is dressed (`brightwater_ferry_dressing.json`, mounted).

## Review log
