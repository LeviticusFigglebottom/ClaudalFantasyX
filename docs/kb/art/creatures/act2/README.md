# Act II creature design sheets (M3-CRE-620)

One sheet per Act II foe the roster ([`../act2_roster.md`](../act2_roster.md)) keeps, written before its model and
checked against it. The rules are the slice's ([`../README.md`](../README.md)): one exaggeration on a real animal
or object of Maresh, `spawn_wound` weak points, spawn in wet lacquer black with `glimmer_held` motes, a Lit Age
construct's bound light in `glimmer_bound`, every colour a palette.json swatch, and the battle read by silhouette
alone. Hits peak near 0.1 s (M3-CRE-617).

| Creature | Sheet | Kind | Height | Where it fights | Model |
|---|---|---|---|---|---|
| The Mangrove Drowner | [mangrove_drowner.md](mangrove_drowner.md) | spawn, boss | 3.2 m (rooted), 3.6 m (risen) | Ossa Fen, the roots (Ch10) | built (M3-CRE-621) |
| The Lamp Engine | [lamp_engine.md](lamp_engine.md) | construct, boss | 3.4 m | Lowlight, the engine hall (Ch11) | built (M3-CRE-623), first PC render pending |
| The Avalanche Ram | [avalanche_ram.md](avalanche_ram.md) | spawn-touched beast, boss | 3.0 m at the head | the terrace wall above Keth Pass (Ch12) | built (M3-CRE-624) |
| The Wakefin | [wakefin.md](wakefin.md) | spawn, boss | 2.2 m of fin above the water | the open sea at night, the bridal barge (Ch15) | sheet only |

**Built models.** The Mangrove Drowner (M3-CRE-621): `assets_src/creatures/mangrove_drowner/`, 16,370 triangles
(budget 18k), root arches to 3.1 m (3.6 m risen) with the trunk stump's splinters to 3.8 m above them, 48 bones (the sheet's core chain of 4, twelve 3-bone roots and the stump, plus six splinter bones
that fly off in the phase). Its `uprooted` phase (creatures.json) plays `phase_change` (2.2 s), hides the `Stump`
mesh after it, idles on `idle_risen`, and strikes from the risen pose (`attack_risen`, `cast_risen`, `hit_risen`).
Contacts: the drag at 0.7 s, the rising water at 1.0 s. Review shots: `creature_mangrove_drowner` and
`creature_mangrove_drowner_risen`. It has no enemies.json row yet (no Act II encounter exists), so the validator
doesn't check its phase name against an enemy; the encounter designers add the row, with a phase `uprooted` at
50% HP. The snagged motes (`glimmer_held`, rising as `glimmer_lift` on the KO) and the drawing-in water of the
drag's telegraph are VFX, not modelled; the break part (the two snagged-mote roots) waits for a charge skill.

The Lamp Engine (M3-CRE-623): `assets_src/creatures/lamp_engine/`, 18,488 triangles (budget 20k), 3.40 m to the
finial with the feet at y 0, 50 bones: the sheet's body, core, three ring bones, twelve lamp gimbals, two arms of 3
and four legs of 2, plus a hinge bone per petal (twelve: a ring folds as four petals), a moving scissor blade per
arm and a foot per leg (kept flat while the KO kneels). Three gimballed rings of four petals each close a lantern
housing round the core; each petal carries its quarter of the hoop and a salt-glass lamp on a gimbal fork, whose two
hubs are the `spawn_wound` weak points. Its `opened` phase (creatures.json) plays `phase_change` (2.0 s: the middle
ring folds back 68°, then the top 50° and the bottom 22°, each lamp swinging back in its gimbal a beat behind), idles
on `idle_opened`, and strikes from the open pose (`attack_opened`, `cast_opened`, `hit_opened`). The KO starts open
(a boss falls in phase 2) and kneels 0.55 m. Contacts: the trim at 0.6 s, the gathering at 1.0 s. It was checked
without a render (numbers in the task file); its review shots `creature_lamp_engine` and
`creature_lamp_engine_opened` wait for their first PC render. No enemies.json row yet; the break parts (the three
rings) wait for a charge skill.

The Avalanche Ram (M3-CRE-624): `assets_src/creatures/avalanche_ram/`, 15,179 triangles (budget 16k), 4.0 m long
(rump fleece to muzzle) with the head at 2.86 m (its woolly cap tops out at 3.08 m), 38 bones: root, a `body` carrier
the legs hang from, the sheet's spine 5, neck 5, head, jaw, four legs of 3 and six fleece-lock chains of 2. The legs
are posed by a grid solve in each leg's plane, so a planted hoof stays at y 0 while the body moves (the charge's
lunge, the KO's kneel). Clips: `idle` (4 s: the neck sways, it chews, the locks swing), `attack` (the charge: the
head drops, a stamp of the right fore, it drives through; contact 0.75 s of 1.6 s, the hooves back where they stood
at the end), `cast` (the bellow: the neck rises, the jaw opens, peak 0.9 s), `hit` (it staggers back and the neck
whips, peak 0.1 s) and `ko` (3.8 s: it kneels on its fore knees, lies down with its legs folded under it, the locks
spread on the ground, and lays its head down; no thrash). The KO lowers `body`, not `root`, so tools/tests'
grounded-KO check holds; measured from the GLB nothing goes below y 0 in any frame. No phases (the sheet asks for
none). Weak points: seven `spawn_wound` partings in the coat (three a side and one along the withers), on the
fleece slot's emission mask. Review shot `creature_avalanche_ram` (three-quarter, idle) waits for its PC render.
No enemies.json row yet. Not modelled, by the sheet: the breath steam, the snow the bellow brings down off the
terrace wall (the field hazard), the ice that cracks off on a hit and the `glimmer_held` the partings shed (VFX).
