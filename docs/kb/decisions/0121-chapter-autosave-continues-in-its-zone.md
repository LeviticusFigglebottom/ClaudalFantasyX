# 0121 — A chapter autosave continues in the zone the chapter began in

- **Status:** accepted
- **Date:** 2026-10-30
- **Roles affected:** tech (SaveSystem), ui (the save and load lists), story and levels (where a chapter starts)
- **Author role:** ui (ui-menus, the Lead's save and load pass, M4-A2P-1705)

## Context
SaveSystem writes the autosave (slot 0) at each chapter boundary (SPEC §6.6). Continue on the title, and "return to
last save" after a defeat, go through WorldReturn.resolve, which prefers the state's respawn point (the last shrine
rested at) over its location (M1-ARC-11).

A chapter usually begins in a new zone, but the last shrine is still the one in the zone before. So the autosave's slot
read "Chapter 4, Haluna's wake" (its location), and Continue put the party at the Shell Shrine, a chapter back.
tests/integration/test_continue_every_act1_zone.gd found this in 16 of Act I's 17 enterable locations.

## Options
1. **WorldReturn.resolve prefers the location for an autosave.** resolve sees only the state, not the save's reason,
   so it would need the reason threaded through every load path.
2. **The chapter autosave records its location as the respawn**, on a copy. Game.state keeps its shrine.
3. **Leave it, and label the slot with the respawn instead.** The label would be honest, but Continue would still
   send the player a chapter back.

## Decision
Option 2. SaveSystem.autosave_state(): a chapter-boundary autosave records a copy of the state whose respawn is its
current location, at the location's own spawn (respawn_spawn ""). Every other save (a shrine's, a manual one) is
written as it is. Continue and "return to last save" then start where the slot says.

## Consequences
- A chapter that begins mid-zone continues at that zone's own spawn (locations.json), not the exact spot of the
  boundary. That is still the place the slot names.
- The autosave's respawn no longer remembers the last shrine. The next shrine rest sets it again, and the shrine
  network keeps its own list (attuned_shrines).
- Tests: test_autosave::test_a_chapter_autosave_continues_in_the_chapter_s_zone, and the Act I sweep above. Both fail
  on the old code.
