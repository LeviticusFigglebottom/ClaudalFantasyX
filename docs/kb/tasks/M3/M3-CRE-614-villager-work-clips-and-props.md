---
id: M3-CRE-614
title: "Villager work clips, hand props and bodies for Haluna's town keepers (request from creatures)"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: [M2-CHR-03, M3-CRE-613]
milestone: M3
request-from: creatures
---
## Goal
FieldNpc (M3-CRE-613) can play a work clip at rest and a storm clip when braced, but the seven M2-CHR-03
villagers have only idle, talk and walk, and no hand props. The capsule stand-ins had a broom (Reed) and a
bowl (Osu); the villager bodies hide those, so the work currently reads only through the head (looking down
at the work, up now and then). The town's shopkeeper, smith and innkeeper still have no bodies, so they stay
capsules.

## Acceptance criteria (characters, through villager_clips.py EXTRA_CLIPS)
- [ ] Looping work clips, in place, 4–8 s, ending where they start:
  - netmender `mend_net` (hands working a net across the lap or a rail);
  - vendor `tend_stall` (setting out and turning wares at about 0.95 m);
  - reed `sweep` (a broom's sweep, stepping a little);
  - osu `hold_bowl` (the bowl at the chest, a slow stir or lift);
  - fisher `coil_rope` (optional: the fisher mostly chats).
- [ ] An optional looping `brace` clip (shoulders up, weight low, a hand at the brow) any villager can share
  in a storm.
- [ ] Hand props (bone-attached, from source like the bodies): Reed's broom, Osu's bowl, the netmender's net
  section.
- [ ] Bodies for the town's Shopkeeper, Smith and Innkeeper (Haluna NPCs/Town), or a decision to reuse three
  of the seven with costume variants.
- When a clip lands, creatures adds `"clips": {"work": "<clip>"}` to that villager's npc.json row (or
  characters may add it; npc.json is creatures', so a one-line request is fine).

## Notes
- Clip contract: docs/kb/tech/field_npc.md "Work" and "Storm"; FieldNpc plays `clips.work` only when the actor
  has it, so the clips can land in any order.

## Review log
