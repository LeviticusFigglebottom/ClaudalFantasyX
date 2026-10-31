---
id: M5-A3P-1710
title: "Post-game: the Memories gallery holds the rest of Act I (Ch4 to Ch9), ten scenes that replay clean"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: narrative
milestone: M5
request-from: lead
---
## Goal
The Lead's 10-31 note asked for post-game handling where the Act III sheets call for it. SPEC §6.11 calls for a
post-game "Memories" scene-replay gallery, and it held only the prologue through Ch3 (M3-MNU-02). This adds the rest
of Act I. Act II and III follow as their zones' stages settle.

## Acceptance criteria
- [x] `game/data/memories/memories.json`: chapters Ch4 to Ch9 (the act outline's names) and ten memories.
  - Ch4: The Shell Is Set.
  - Ch5: Lanternfall: The Weir; Kahre.
  - Ch6: The Barge Leaves No Wake.
  - Ch7: Tavi; After the Bell.
  - Ch8: The Binding of Virel; The Wall Falls.
  - Ch9: The Ebbing; The Road Out.
- [x] Each unlocks on a flag that is always set when its scene plays: the scene's own unconditional `<<set>>`, or
      for The Shell Is Set and After the Bell, the flow step straight after the scene. Each replays with that flag
      unset (`replay_flags`), so the zone looks as it did before the scene.
- [x] Titles and chapter names are in memories.csv. validate_data's check_memories passes.
- [x] Tests:
  - test_memories: the data test names all eighteen memories and ten chapters;
  - test_memory_replay `test_the_rest_of_act_one_replays_cleanly`: each of the ten plays to its end on its stage,
    with lines, no event and the record unchanged, then goes back to the title.

## Notes
- These are headless replays. A look at each in a real window (framing, the zone's state at the time) is for
  Narrative's review.

## Review log
