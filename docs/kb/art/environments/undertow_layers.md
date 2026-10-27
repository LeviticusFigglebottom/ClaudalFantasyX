# The Undertow's Layers (Ch20): Design Notes

Owner: Environment Artist (M3-ENV-727). Lighting review: Rendering. Story review: the rooms chosen.
- **Story:** [act_outline Ch20](../../story/beats/act_outline.md); bible §5 ("Inside (Act III)": layered rooms made of
  the drowned's memories, suspended in dark water lit by motes; at the bottom, the Cage and the heart);
  vowbound.md (the release order).
- **Grade:** [color script](../color_script.md) `ch20`.
- **Kit:** in the Haluna kit as `undertow_layers.py`.
- **Arena:** `undertow_cage` (the Cage, the four bound founders).

**The feeling in one line:** every room is someone's held grief, hanging in the dark. The places you've walked come
back as islands, and nothing is quite where it was.

## 0. Lighting (`ch20`)
- **No sun.** The motes' cold light comes from above: `#C4D6FF` 0.8, fill `#061A2B` 0.2.
- **Atmosphere:** dense fog `#0E3A48`, sky `#020610` over `#0E2A3A`, exposure 1.1.
- **LUT:** `lut_ch20_abyss` (navy-black base, the held cyan clean).
- **The practical light** is held glimmer (`kit_glimmer_held`, `#7FC6D9`): cold, steady, never warm. Warm light is
  the Letting's, in Ch21.
- **Underwater views** wait for the underwater shader (colour script: not validated). The arena is lit as a dark
  void, with the sea far below.

## 1. Kit pieces (metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `memory_island` | The floor every room stands on: a flat top (r 9) of Iskarra's flags with a ragged edge, a hanging root of stone and earth tapering 9 m down into strands; the founders' Lit Age sunburst laid in it | r 9 × 9 deep | 12k / 900 |
| `memory_kitchen` | A Corrow kitchen remembered (Ch8): two coral-stone walls, a cold hearth and its pot, a table and stools, a shelf of jars | r 5 | 7k / 500 |
| `memory_market` | An Oruvel market stall remembered (Ch1): a plank deck, a sea-blue awning, fish baskets, crates, a hanging scale | r 5 | 7k / 500 |
| `memory_stands` | A Reefball crowd remembered (Ch7): three tiers of benches, pennant posts, nobody on them | r 6 | 7k / 500 |
| `held_pillar` | A broken Lit Age lamp column threaded with held glimmer, the light hanging off its top in drops | 7 m | 3k / 200 |

**The rooms in the zone** (act1-chapters, or whoever stages Ch20):
- One island per layer, each a remembered place. They are stacked down into the dark, with gaps between them that
  the Kite drops through.
- Each Vowbound release flips that layer's held pillars to `glimmer_lift` (a material swap the release cue owns).

## 2. The Cage's arena (`undertow_cage`)
- **The floor:** the last remembered room, the founders' Iskarra, on `memory_island`. Flat at y 0 round the slots.
- **The Cage:** four `held_pillar`s stand round it behind the enemy line, each with a cyan light (`Lamp0–3`). The
  Cage itself, the four bound founders, is Creatures'.
- **Round the floor:** the other rooms hang at heights from −12 to +12 m and 25–65 m out (a kitchen, the market, the
  stands, a bare island) in the dense navy fog.
- **Hints:** `the_rooms`, `the_cage`.

## Revisions
- 2026-10-27 (env-art, M3-ENV-727): first issue, with the kit and the Cage's arena.
