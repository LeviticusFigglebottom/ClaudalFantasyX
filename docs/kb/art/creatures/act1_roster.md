# Act I bestiary: roster proposal (M3-CRE-01)

The creatures track's proposal for Act I's foes (act_outline.md Ch1, Ch4–Ch9), for **m2-slice**, which designs the
Act I encounters (M3-C0x tasks). Ids are proposals: m2-slice's encounter and enemies.json work decides which ship,
their stats, skills and AI. Art builds a design sheet (README.md rules) and then a model (pipeline.md) for each one
m2-slice keeps. Bosses are named by act_outline.md; the regular foes are new.

**The rules from README.md hold:** a real animal or object of Maresh with one exaggeration; weak points glow
`spawn_wound`; Undertow-spawn carry the dark wet carapace and the drifting held-glimmer wounds (bible §177); reef
beasts never use glimmer swatches. SPEC §5 allows palette variants with new behaviour, so some rows are variants of
a slice creature (cheap: a materials.json and a creatures.json row, the same rig and clips).

## Chapter by chapter

| Ch | Zone | Id | What it is | Battle role (what it teaches) | Kind |
|---|---|---|---|---|---|
| 1 | Oruvel Underway (the drowned-tower dive, lantern-lit) | `wickfry` | A shoal of finger-long glass shrimp drawn to lamp light, fought as one combatant: a loose cloud that tightens to strike | Fast, frail, acts often: the timeline's first lesson (who acts next) | reef beast |
| 1 | Oruvel Underway | `tower_limpet` | A cartwheel-sized limpet clamped to the tower stair, its shell grown over a shutter it took with it | Slow wall that delays: you can skip it, the timeline shows how long it takes | reef beast |
| 1 | Oruvel Underway | `oil_slug` | A sea slug that feeds on lamp oil leaking from drowned lamps; its frills glow the warm colour it ate (`oil_lamp`), dimming the diver's lantern | Caster: blinds (the light is stolen), weak to fire | reef beast |
| 1 | the breaking raft (boss) | `hullgnaw` | **Hullgnaw**: an Undertow-spawn eel grown through a ship's ribs, the ribs its carapace, wounds between them | Timeline tutorial boss (act_outline) | spawn, boss |
| 4 | the drifting trader (Brightwater) | `bottle_hermit` | A hermit crab living in a ship's lamp glass; the glass magnifies its own small light | Reflects or blocks magic through the glass (Ysolde's introduction: pick the element) | reef beast |
| 4 | the drifting trader | `sail_leech` | A flat ray-shaped spawn that clings to wet canvas and drops from the yards | Ambusher: it acts first, then is fragile | spawn |
| 4 | the derelict's deck (boss) | `spar_wraith` | **Spar-Wraith**: a spawn tangled in the dead ship's rigging, its body hanging in the shrouds, spars for limbs | Elemental weak points that change (Ysolde's magic) | spawn, boss |
| 5 | Pemakar terraces, Lanternfall | `ashwing` | A broad grey moth drawn to the festival's leaf-boat lights, its wing-dust ash | Flier, fire-weak, sleeps the party with its dust | beast |
| 5 | Pemakar terraces, the copper veins | `slag_tortoise` | A terrace tortoise whose shell carries cooled slag from the ash-plume | Armoured: the armour-break niche (Kerrid) | beast |
| 5 | Ashcrown (boss) | `cinder_matron` | **Cinder Matron**: a magma-crusted temple guardian construct, two phases (the crust breaks) | Armour break (act_outline) | construct, boss |
| 6 | Brine Shoals (wrecks, mud-flats) | `shoal_skipper` | A mudskipper grown to a dog's size, salt-crusted, hopping the flats | Quick striker, low HP | beast |
| 6 | Brine Shoals | `wreck_crab` | **Variant of the reef crab**: salt-white crust, wreck timber instead of house coral | The reef crab's defender, with a new skill | variant |
| 6 | Brine Shoals (boss pair) | `raid_hound` | The Order raid's hound: a lean coursing dog in a branded leather harness (the Stillguard Inquisitor is a person: the character track) | Protects the Inquisitor; Toma refuses to kill | beast, boss pair |
| 8 | the seawall, the Fisher Stair | `tide_crawler` | Undertow-spawn shore crawler: crab-legged, wet black carapace, glimmer wounds; comes in waves | The set-piece's swarm | spawn |
| 8 | the seawall | `squall_wing` | Undertow-spawn flier: a gull-shaped hole in the rain with held-glimmer wounds (echoes the gull harrier) | Flier among the waves | spawn |
| 8 | the seawall | `wall_polyp` | **Variant of the spawn-polyp** rooting on the wall's stones | Healer behind the crawlers | variant |
| 8 | the storm (boss) | `undertows_reach` | **The Undertow's Reach**: a colossal limb of the storm. Mostly the storm itself (Rendering's Undertow), so art makes the limb's near part: a lashing mass of black water and spawn that reaches over the wall | Multi-phase, scripted escape (act_outline) | storm, boss |
| 9 | Corrow at night (the Ebbing) | none | The Ebbing has no fight in act_outline | | |

**Counts:** 11 new regular foes and 2 variants, 4 bosses plus the Reach. That is about a sixth of SPEC §5's ~120 types,
in line with Act I's share of the game.

## Order of work (art)

1. Design sheets for all of them (this file's ids), Ch1 first (it opens the game), in `act1/<id>.md`. Done: Ch1 (`hullgnaw`, `wickfry`, `tower_limpet`, `oil_slug`).
2. Models in chapter order: Ch1 (wickfry, tower_limpet, oil_slug, Hullgnaw), Ch4, Ch5, Ch6, Ch8. Variants are cheap
   and go with their chapter. The Reach needs the PC GPU session (the storm limb is theirs; the creature part is
   ours).
3. Each lands with `"model"` on its enemies.json row once m2-slice has added the row; until then the model sits in
   `game/creatures/<id>/` with a creatures.json row and a review shot.

## Open questions for m2-slice

- Keep, cut or rename any of these? Encounter sizes per zone (how many on screen at once) set the triangle budgets.
- Hullgnaw is fought on a breaking raft: is the raft part of the arena (environment) or of the boss?
- The Cinder Matron and the Stillguard Inquisitor are a construct and a person: confirm the construct is creatures'
  and the Inquisitor the character track's.
