---
id: M3-HER-101
title: "Request (slice-polish, to the hero track): the reserve walks with the party in the field (Toma vanishes on the slice's walks)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
ADR 0041 beat audit (self-rendered slice_causeway_head, slice_haluna_villagers_village): after Cutscene A,
`first_playable.json` party.joins puts Rhen and Asha in the party and Toma in reserve, so the first battle can teach
the swap. `HeroFieldParty.sync_party()` builds followers from `Game.state.party_ids` only, so in the field Toma is
gone. The story has him with them the whole way:
- B05: Asha and Toma at the causeway head;
- B06: "three voices walking", and his banter lines play on the causeway;
- B11: the dock at night.

His barks show him (M2-FP-107) and then he vanishes again. That reads as a placeholder.

## Acceptance criteria
- [ ] Followers fill from the active party first, then the reserve, in order, up to `field.followers.max`
      (it is 2 today, so Asha then Toma in the slice). Battles still seat only the active party.
- [ ] A test: party [rhen, asha] plus reserve [toma] gives two followers, Asha first.
- [ ] Ch4 onward, where the party grows past three: the cap still holds, so only the first two follow.

## Review log
