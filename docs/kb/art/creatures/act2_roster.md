# Act II bestiary: roster proposal (M3-CRE-620)

The creatures track's proposal for Act II's foes (act_outline.md Ch10–Ch16, "The Truth"), written ahead of the
Act II encounter design so the chapters have bodies to place. Ids are proposals: the chapter track that designs the
Act II encounters decides which ship, their stats, skills and AI. Art writes a design sheet for each kept row
(README.md rules), then builds it (pipeline.md). Bosses are the ones act_outline.md names; the regular foes are
new.

**The README rules hold:**
- a real animal or object of Maresh, with one exaggeration;
- weak points glow `spawn_wound`;
- Undertow-spawn carry the wet lacquer carapace and drifting `glimmer_held` motes;
- a Lit Age construct's bound light is `glimmer_bound`;
- reef and land beasts never use glimmer swatches.

Act II's colour is overcast, storm, moonlight and cold blue stone (act_outline.md), so the beasts here are
cooler and paler than Act I's: tannin browns in the fen, salt-glass and verdigris in the drowned galleries, wool
creams and slate in the heights, bone-white on the Pale Rim.

**What this track does not build:** people. The Kirru are a people (glossary: heron- and otter-like), so no foe
here is a heron, an egret or an otter, and no Kirru is ever a monster. The Abiding, the Stillguard, Warden Malcor
Venn and Sefir's guard are people: the characters track. The storm's waking at the Choir is the Undertow render.

## Chapter by chapter

| Ch | Zone | Id | What it is | Battle role (what it teaches) | Kind |
|---|---|---|---|---|---|
| 10 | Ossa Fen, the mangrove channels | `tannin_archer` | An archerfish grown to a dog's length in the tannin-dark water; it knocks things off branches with a jet of water | A ranged striker whose jet **delays** its target on the timeline: the first foe that pushes a hero back | fen beast |
| 10 | Ossa Fen | `root_crab` | **Variant of the reef crab**: a mangrove tree-crab, bark-brown and lichen-spotted, that lives in the roots and drags prey into them | The reef crab's defender, with a new skill that **roots** one hero (no swap) | variant |
| 10 | Ossa Fen | `fen_leech` | **Variant of the sail leech**: a ribbon-flat leech of the dark water, its underside a faint tannin-amber | A drainer: it heals by what it takes (a first lesson in denying healing) | variant |
| 10 | Ossa Fen, the roots (boss) | `mangrove_drowner` | **The Mangrove Drowner**: Undertow-spawn grown through a mangrove's prop-roots; its body is the root cage, its wounds between the roots. Phase 1: rooted, it drags the party's footing (the water rises along the roots); phase 2: it tears free of the tree and stands on the roots like legs | Two phases (act_outline). The held motes it has dragged out of the fen snag in its roots; breaking a root lets a few go **upward**, a quiet foreshadow of the Letting | spawn, boss |
| 11 | Sunken Vey, the drowned galleries | `gallery_ray` | A pale cave ray that glides along flooded corridors, nearly the colour of the salt-glass floors | A flier among the columns: it is out of reach every other turn (it glides above the water line) | reef beast |
| 11 | Sunken Vey | `rime_urchin` | A long-spined urchin from where the deep's cold wells up; its spines carry a crust of rime | Ice-element counter: striking it in melee chills the striker (pick magic or reach) | reef beast |
| 11 | Lowlight temple | `conduit_crawler` | A Lit Age conduit-cleaning machine still at its rounds: a salt-glass shell on six brass feet, a dim bound light inside | A construct that **repairs** the Lamp Engine's parts; it ignores the party until the engine is struck | construct |
| 11 | Lowlight, the engine hall (boss) | `lamp_engine` | **The Lamp Engine**: a still-running Lit Age machine full of bound dead; a lattice of salt-glass lamps on a brass frame around one core. Phase 1: its lamps; phase 2: the core, bared | Two phases (act_outline); releasing the core makes a small upward lift (the foreshadow). Its bound light is `glimmer_bound`, steady | construct, boss |
| 12 | Keth Pass | `ridge_lynx` | A high-pass lynx in a thick slate-grey winter coat, ear tufts frosted | A quick pouncer that strikes the back row first (formation matters) | beast |
| 12 | Keth Pass, the pass-cords | `cord_moth` | A pale moth whose larvae live in old keth cords; the adults' wings carry the knot patterns they ate | It **unravels** buffs (removes one); fire-weak. The knots on its wings are real keth knots: Ysolde can read one | beast |
| 12 | Cloudloom approach | `scree_crawler` | **Variant of the slag tortoise**: a mountain tortoise whose shell carries frost-split scree instead of slag | The armour-break niche again, in the cold, with a frost counter | variant |
| 12 | the terrace wall (boss) | `avalanche_ram` | **The Avalanche Ram**: a woolback grown monstrous on drowned glimmer seeping from a Lit Age terrace wall; its fleece is matted with ice and the seep's cold light shows through the parting (wounds); a long neck, as every woolback | A charging boss whose charge **brings down the snow** (a field hazard round by round) | spawn-touched beast, boss |
| 14 | the lagoon, the pursuit barge (boss part) | `flat_engine` | The **flat-engine** on Malcor Venn's barge: a bound Lit Age engine that pulls the water flat and still. Not a creature: a breakable part (CreatureActor `break_parts`) on the barge the boss stands on | Phase 1: while it runs, the timeline slows (act_outline); Liss breaks it. The Warden himself is the characters track's | construct, boss part |
| 15 | the open sea at night (boss) | `wakefin` | **The Wakefin**: Undertow-spawn that followed the first wake out of Ansedra; a long dorsal blade cutting the black water, the body below seen only by the sea-glow along it | A boss fought in the dark: its telegraphs are **sounds and the sea-glow**, not light (pillar 4 holds: the timeline still shows it) | spawn, boss |
| 16 | the Pale Rim, the white shallows | `glass_skate` | A skate that buries itself in the white sand, its back the colour of the shallows; only its eyes show | An ambusher that is untargetable until it has acted once (learn to wait) | reef beast |
| 16 | the Pale Rim | `rim_crawler` | **Variant of the tide crawler**: Undertow-spawn crawlers bleached by days of white water, their carapace chalky, wounds dimmer | The tide crawler's swarm, in the open: no wall to hold | variant |

**Not foes on purpose:**
- Reedhollow (the Kirru village), Quellan, Ansedra and the Lamp Archive have no fights.
- Ch14's lagoon pursuit is the Warden's fight (people), plus the flat-engine part.
- Ch15 has only the Wakefin: the drifting barge has no random fights.
- Ch16's boss is Sefir's Abiding guard (people), then the storm.

**Counts:** 9 new regular foes and 5 variants, 5 bosses (the Drowner, the Engine, the Ram, the Wakefin, and the
flat-engine as a boss part). With Act I's 17, that is about a quarter of SPEC §5's ~120 types by the end of Act II.

## Order of work (art)

1. **Design sheets** (`docs/kb/art/creatures/act2/<id>.md`, the README template), in chapter order, bosses first:
   the Mangrove Drowner, the Lamp Engine, the Avalanche Ram, the Wakefin, then the regulars.
2. **Builds**, the same order: procedural numpy on `common/creature_kit.py`, a Blender job each, creatures.json
   rows, review shots. Variants are cheap (a materials.json and a creatures.json row on the base rig), so they go
   with their base's chapter.
3. Everything stays within the pipeline's budgets (pipeline.md) and the clip contract (idle, attack, cast, hit with
   its peak near 0.1 s (M3-CRE-617), ko, plus phase clips for the bosses).

## Open questions (for the chapter designer, not the human)
- Ch10: does the farewell-tide scene want the fen's foes kept out of Reedhollow's channels entirely (proposed: yes)?
- Ch11: is the conduit crawler a foe or a hazard (it repairs, and never attacks first)?
- Ch14: is the flat-engine its own combatant (a target on the timeline) or a part of the Warden's barge row?
