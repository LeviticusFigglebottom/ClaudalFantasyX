# Creatures: design sheets (M2-CRE-01)

One sheet per battle creature in the M2 vertical slice. Each one is written before its model (SPEC §7.5) and the
model is checked against it. The pipeline that builds them is [`pipeline.md`](pipeline.md).

| Creature | Sheet | Kind | Height (stand-in spec) | Where it fights |
|---|---|---|---|---|
| Reef crab | [reef_crab.md](reef_crab.md) | reef beast | 0.62 m body, 1.4 m across | the causeway, the tideline |
| Lantern eel | [lantern_eel.md](lantern_eel.md) | reef beast | 2.1 m out of the water | the shallows |
| Gull harrier | [gull_harrier.md](gull_harrier.md) | sea-bird | 0.45 m body, hovering at 1.05 m, 2.5 m wingspan | the causeway, the beach |
| Spawn-polyp | [spawn_polyp.md](spawn_polyp.md) | Undertow-spawn | 0.6 m | under the Drownbell's flood |
| The Drownbell | [drownbell.md](drownbell.md) | Undertow-spawn, boss | 2.4 m, rim radius 0.85 m | the Saltgrass Causeway arena, B10 |

## Rules every sheet follows

1. **Originality (CLAUDE.md §2, references.md rule 4).** Every creature starts from a real animal or a real object of
   our world, with **one** supernatural exaggeration (references.md "Creatures"). If a reviewer can name a creature
   from the inspiring game that it resembles, it gets redesigned, without argument. No sheet borrows a name, a
   silhouette or a signature attack from it.
2. **Rooted in Maresh.** Each creature says something about the drowning archipelago: the reef crab wears the
   houses the sea took, the lantern eel imitates a lamp-diver's lamp, the gull harrier carries a storm's leavings,
   and the Drownbell is the Shell Shrine's lost bell.
3. **The three lights stay distinct** (color_script.md rule 1, art README). Creatures never use `glimmer_lift`
   (released dead) or `glimmer_bound` (a Vowbound). A creature's **weak point** glows `spawn_wound` `#3FE0C8`, the
   swatch reserved for creature weak points, and the motes an Undertow-spawn sheds are `glimmer_held` `#7FC6D9`
   (sinking, seaward). A reef beast's own bioluminescence uses sea colours (`salt_glass`, `sea_glow`), never glimmer.
   The one exception is a Lit Age construct: it is a machine, so what the Lit Age bound into it is `glimmer_bound`
   (color_script.md rule 2), steady and unpulsing. The Cinder Matron's heart is the first case.
4. **Undertow-spawn read at a glance** (SPEC §7.5): dark, wet, lacquer-black carapace (`lacquer_black` to
   `abyss_navy`, clearcoated) and drifting `spawn_wound` wounds. Reef beasts are sun-faded and dry-topped, with only a
   small `spawn_wound` weak point.
5. **Beauty in decline** (pillar 2). Every creature is handsome first and wrong second: worn, weathered, carrying
   something lost.
6. **The battle read (pillar 4).** At the battle camera (`battle_sandbox.tscn`: 40° vertical FOV from about 9 m,
   so roughly 110 px a metre at 720p) every creature must read by **silhouette alone** in under a second, and its
   attack must telegraph before it lands. The clip list is fixed by the pipeline: `idle` (loops), `attack`, `cast`,
   `hit`, `ko`, and `phase_change` for the boss.
7. **Albedo stays inside the palette's floor and ceiling** (`#1D1916` to `#EBE7DF`, palette.json global rules), and
   every colour named here is a palette.json swatch.

## Scale against the heroes

```
 2.4 m  |                                   ____
        |                                  /    \     the Drownbell (hood top)
 1.9 m  |  Toma ·                         |      |
 1.77m  |  Rhen ·                         |      |
 1.63m  |  Asha ·           eel ~         |      |
 1.05m  |              gull >-<           |      |
        |                    (hover)      |______|  <- rim at 0.29 m
 0.62m  |   crab ▄▄▄       polyp ¥        ‾‾‾‾‾‾‾‾‾
 0.0 m  +-------------------------------------------- ground / low water
```

The heights in each sheet are the ones `game/data/ui/battle_sandbox.json` gives the stand-in: the battle VFX anchor
their effects at fractions of that height (`effects.json` `anchor_heights`: feet 0.05, rim 0.12, chest 0.6, hood 0.85,
head 1.0), so a model must keep its parts where those fractions land.
