---
id: M3-C04-04
title: Ch4's hand-offs: the slice's end card into the wake night, and the ferry on to Ch5's Pemakar
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M3-C04-02, M3-C05-02]
reviewer: lead
milestone: M3
request-from: cinematics
---
## Goal
M3-C04-02 built Ch4 between two stand-ins:
- **Entry.** In the full game the slice's end card (B12) leads into the wake (act1_ch04.md §9 Systems). For the M2 build it still returns to the title, and Ch4 is reached at its own location (`ch04/haluna_wake`, spawn `NemeDoor`; F5 teleport). Add an optional `next_location` / `next_spawn` to `first_playable.json` `end_card` (EndCard goes there on accept instead of `return_scene`, with a test in `test_fp_end_card.gd`), and set it to `ch04/haluna_wake` / `NemeDoor` once the M2 review build no longer needs the title return.
- **Exit.** `ch05/pemakar` wasn't on the Ch4 branch, so `ch04.json`'s last ferry step is `{"scene": "res://game/flow/end_card.tscn"}`. When Ch5 (M3-C05-02) merges, repoint it to `{"go": {"location": "ch05/pemakar", "spawn": <its harbour arrival spawn>}}`, and change the last assertion of `test_ch04_thread` to match.

Do the exit first: with the end card pointing into Ch4 while Ch4 still exits to the end card, the two would loop.

## Acceptance criteria
- [x] Ch4's last step goes to Ch5's entry; `test_ch04_thread` asserts it.
- [ ] The end card leads into Ch4 in the full-game build; `test_fp_thread` and `test_fp_end_card` stay green.

## Notes
- 2026-10-24 m2-slice: the Lead approved the switch.
  - **The exit is already done.** Ch4's ferry goes on to `ch05/pemakar` at `Harbour` (M3-C05-02 merge).
  - **The entry switch is in.** `first_playable.json` `end_card.next_location` / `next_spawn` are both **empty**, so the M2 review build still ends at the title.
    - When they are set, `EndCard.accept` goes there through `FlowRouting.go_to` instead of `return_scene`.
    - `test_fp_end_card` has two tests: one that the data stays empty, and one that with the switch set, accept goes on to `ch04/haluna_wake` / `NemeDoor`.
  - **Left for the Lead:** set `ch04/haluna_wake` / `NemeDoor` once the human signs off the M2 review. That is the last box. Testers can reach M3 before then with F8 (M3-ARC-02).

## Review log
