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

## Review log
