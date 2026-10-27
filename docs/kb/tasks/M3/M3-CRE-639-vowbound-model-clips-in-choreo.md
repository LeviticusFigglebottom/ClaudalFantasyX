---
id: M3-CRE-639
title: "Vowbound choreography: play Ilun's model clips (rise, dismiss, special) once his model lands"
role: combat
status: todo
owner_session: ""
depends_on: [M3-CRE-638]
milestone: M3
request-from: creatures
reviewer: art
---
## Goal
Ilun, Asha's Vowbound, stops being a teal capsule (the Lead, 2026-10-27, after viewing big12's renders of
battle_vowbound_out, battle_choreo_summon and battle_choreo_vowbound_rise). Creatures is building his model (M3-CRE-638):
a vast spectral manta with a heron's crest, the net pattern in glimmer_bound light, and the glass net-float.

The model gets the stand-in's usual clips (idle, ready, attack, cast, hit, defend, ko, victory), so today's choreography
works unchanged:
- the entry and dismiss *translate* him (depth_m 2.6) and play `ready`;
- the fall plays `ko`.

It also has three Vowbound clips that only the choreography can trigger:
- `rise`: he unfurls up out of the water (entry, and summon_cinematic.entry);
- `dismiss`: he folds down to sink;
- `special`: Floodnet, the Swell technique, with the wings flung wide and then sweeping down.

## Ask (battle-presentation; game/battle/scene/** and game/data/battle/choreo.json are yours)
1. In choreo.json `vowbound.entry`, `summon_cinematic.entry` and `vowbound.dismiss`, play `rise` and `dismiss` when the
   stand-in has them (BattleClips.has_clip), falling back to `ready`. Match the clip's length to the translation's `sec`:
   - the clip's authored length is in the M3-CRE-638 task file;
   - creatures will re-time the clip to your `sec` if you'd rather not scale speed.
2. Play `special` for his Swell technique (floodnet), as the `finisher` style's actor clip.
3. Keep the summon camera shot's framing in mind. M3-CRE-638 lists his wingspan and height above the slot. Tell us if
   the summon shot needs him smaller, rather than reframing.

## Notes
- Ilun is attached through CreatureModels.stand_in_overrides (a creatures.json row with `"vowbound": true`), so
  game/data/ui/battle_sandbox.json's capsule row stays as the fallback and needs no edit.
- Bound light rule (color_script.md): his light is steady and moves only with his body, so no trails on the rise.

## Review log
