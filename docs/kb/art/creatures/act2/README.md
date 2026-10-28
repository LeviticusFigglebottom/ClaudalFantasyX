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
| The Wakefin | [wakefin.md](wakefin.md) | spawn, boss | 2.2 m of fin above the water | the open sea at night, the bridal barge (Ch15) | built (M3-CRE-626), first PC render pending |
| Tannin archer | [tannin_archer.md](tannin_archer.md) | fen beast | 1.1 m long, 0.58 m on its root | Ossa Fen, the mangrove channels (Ch10) | built (M3-CRE-627), first PC render pending |
| Gallery ray | [gallery_ray.md](gallery_ray.md) | reef beast, flier | 1.6 m across, hovering at 1.4 m | Sunken Vey, the drowned galleries (Ch11) | built (M3-CRE-627), first PC render pending |
| Rime urchin | [rime_urchin.md](rime_urchin.md) | reef beast | 1.8 m to the top spines (0.9 m test) | Sunken Vey, the cold wells (Ch11) | built (M3-CRE-627), first PC render pending |
| Conduit crawler | [conduit_crawler.md](conduit_crawler.md) | construct | 0.45 m (0.7 m long) | Lowlight temple, its conduits (Ch11) | built (M3-CRE-627), first PC render pending |
| The ridge lynx | [ridge_lynx.md](ridge_lynx.md) | beast | 0.77 m at the withers (coat included) | Keth Pass (Ch12) | built (M3-CRE-628), first PC render pending |
| The cord moth | [cord_moth.md](cord_moth.md) | beast | 1.4 m span, hovering at chest height (1.31 m) | Keth Pass, along the pass-cords (Ch12) | built (M3-CRE-628), first PC render pending |
| The glass skate | [glass_skate.md](glass_skate.md) | reef beast | a disc 1.4 m across, 0.16 m tall | the Pale Rim, the white shallows (Ch16) | built (M3-CRE-628), first PC render pending |
| The root crab | [variants.md](variants.md) | variant of the reef crab | 0.72 m, 1.94 m across the legs | Ossa Fen (Ch10) | built (M3-CRE-628), first PC render pending |
| The fen leech | [variants.md](variants.md) | variant of the sail leech | 2.74 m long, hovering (1.38 m) | Ossa Fen (Ch10) | built (M3-CRE-628), first PC render pending |
| The scree crawler | [variants.md](variants.md) | variant of the slag tortoise | 0.82 m | the Cloudloom approach (Ch12) | built (M3-CRE-628), first PC render pending |
| The rim crawler | [variants.md](variants.md) | variant of the tide crawler | 0.75 m | the Pale Rim (Ch16) | built (M3-CRE-628), first PC render pending |
| The flat-engine | [flat_engine.md](flat_engine.md) | construct, boss part | 1.8 m drum, 3 m paddles on the water | Malcor Venn's barge, the lagoon (Ch14) | built (M3-CRE-637), first PC render pending |

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

The Wakefin (M3-CRE-626): `assets_src/creatures/wakefin/`, 11,128 triangles (budget 14k), 6.0 m from the tail lobes'
tips to the bill's point, its swept dorsal blade standing 2.21 m above the water, 20 bones: root, head, the sheet's
spine 10, the bill, a blade of 3 (by height, each hinged along the back's line), two pectorals and two tail lobes. y 0
is the water's surface: the spine axis (the root) sits at y −0.38, the back's height under the blade's front root, so
the waterline falls where the blade meets the back (−0.06..+0.05 over the idle). Clips: `idle` (4 s, in place: it
banks and yaws into a turn and back, a swimming wave runs down the spine, the blade leans and its top curls, it
surfaces a little twice a loop), `attack` (the breach: the whole fish out of the water, rolled so the blade sweeps
flat across the deck; contact 0.8 s of 1.6 s), `cast` (the dive: the blade goes under, 0.9–1.3 s, and it rises at
1.5 s, the contact), `hit` (the blade jerks over and the body rolls, peak 0.1 s) and `ko` (the blade flops flat, it
rolls belly-up and floats up to lie at the surface, drifting away; it ends at y −0.46..+0.79). No phases. Lights: a
`sea_glow` seam along each flank (its own slot, the sea's light) and eight `spawn_wound` wounds along the spine (the
body slot's emission mask, the weak points). It was checked without a render (numbers in the task file); its review
shot `creature_wakefin` (three-quarter, idle) waits for its first PC render. No enemies.json row yet. Not modelled, by
the sheet: the sea-glow wake, the dark water and the surfacing ring of the dive, and the `glimmer_held` the wounds
shed (VFX).

**The Act II regulars (M3-CRE-627).** Four builds, each checked without a render (numbers in
`docs/kb/tasks/M3/M3-CRE-627-act2-regulars-ch10-11.md`); their review shots `creature_tannin_archer`,
`creature_gallery_ray`, `creature_rime_urchin` and `creature_conduit_crawler` (three-quarter, idle) wait for their
first PC render. None has phases or an enemies.json row yet (no Act II encounter exists).

- **Tannin archer** (`assets_src/creatures/tannin_archer/`): 4,464 triangles (budget 6k), 10 bones (root, spine 5,
  tail, jaw, pectorals). It lies nose-up along a mangrove root (the root prop is on `root`, which never moves; y 0 is
  the fen's water), the fish 0.02..0.58 m. Six `lacquer_black` bars on `sand_cloth` flanks, a dark teal back, a `bone`
  belly, a `dusk_gold` eye, the gill slit the `spawn_wound` weak point. Contacts: the spit 0.55 s, the long jet 0.9 s.
  The KO rolls it off the root onto its side at the water. The jet is VFX.
- **Gallery ray** (`gallery_ray/`): 4,504 triangles (budget 5k; 4,104 before the M3-CRE-645 polish), 12 bones (root,
  body, wing chains of 3, tail of 4).
  A flier: the origin is its hover point and creatures.json's `stand_in.hover` is 1.4 m (head height); the KO drops
  the root by that and lays it flat on the floor. A `margin` slot carries its faint `sea_glow`; the camera-side
  spiracle's shut valve is the weak point, one small closed `spawn_wound` mark (ADR 0151; M3-CRE-645 added the keel,
  pectorals, brow ridges, rimmed spiracles, the barbed whip tail and the idle's tip curl). Contacts: the wing sweep
  0.6 s, the pool 0.9 s (the cast settles it onto the floor). The pool's flare is VFX.
- **Rime urchin** (`rime_urchin/`): 8,822 triangles (budget 9k), 10 bones (root with the ice plinth, body, eight
  spine-field sectors). 184 rimed spines up to 0.9 m on a 0.9 m test, 1.79 m to the top spine. The mouth underneath is
  the weak point. Contacts: the roll 0.5 s, the aimed spines 0.8 s. The frost bloom and the melting rime are VFX.
- **Conduit crawler** (`conduit_crawler/`): 4,752 triangles (budget 5k), 18 bones (root, body, six legs of 2, two
  arms of 2), the feet at y 0. Its bound light is `glimmer_bound`, steady, on the shell's emission (rule 3); the
  shell's seam is the weak point. Contacts: the brush jab 0.45 s, the repair 1.0 s. The KO folds its knees up and
  sinks it onto its belly plate; its light dimming on the KO is not modelled (the shader's emission is static).

**The regulars and the variants (M3-CRE-628).** Each was checked without a render (numbers in
docs/kb/tasks/M3/M3-CRE-628-act2-regulars-ch12-16-and-variants.md). Their review shots `creature_<id>` (three-quarter,
idle) wait for the first PC render. None has an enemies.json row or phases yet.

- **The ridge lynx** (`assets_src/creatures/ridge_lynx/`): 7,304 triangles (budget 8k; 6,988 before M3-CRE-645's
  wedge muzzle, nose leather, whisker pads and whiskers), 27 bones (the sheet's quadruped on a `body` carrier, plus
  two ear bones).
  - The legs are posed by a planar two-bone solve, so its paws stay planted through the crouch and the landing.
  - The pounce is the crouch (the telegraph), a 0.64 m leap and the strike on the back row (contact 0.7 s). The yowl,
    a twist aside on the hit (peak 0.1 s), and a KO that limps two steps and lies down on its side.
  - Its weak point is the old sling wound, a small glowing slit on its camera-side flank.
- **The cord moth** (`cord_moth/`): 4,144 triangles (budget 5k), 12 bones. It hovers at 1.25 m (`stand_in.hover`).
  - The knot rows are raised strips of cord in the cords' faded dyes, with knots in counted, seeded groups: an
    abstract, original pattern.
  - The cast tips it up toward the party with its wings open full, so the rows catch the light. The KO drifts down
    the hover height like a dropped scarf.
  - Its weak point is a thorax crack.
- **The glass skate** (`glass_skate/`): 3,638 triangles (budget 4k; 2,624 before M3-CRE-645's thornback rows,
  `sand_wet` margin rim and taller turrets), 14 bones (disc chains of 3 a side, a tail of 4, two eye bones).
  - A flat disc on the sand with eyes on turrets. Its nearly clear back is pale and glassy on a glossy, rim-lit
    material.
  - It erupts and slaps (contact 0.5 s), hides by rippling its edges, buckles on a hit (its own `hit_b`), and
    flattens on the KO.
  - Its weak point is a split at the tail root.
- **The variants** import their base's build module and play its clips:
  - the root crab, on the reef crab's new `LEG_KNEE` and `LEG_FOOT` parameters (longer climbing legs), in bark and
    lichen, with a knot of roots on its back;
  - the fen leech, on new sail leech parameters (ribbon-flat and 2.74 m long), lacquer black over a tannin-amber
    underside;
  - the scree crawler, on new slag tortoise parameters (40 faceted plates, a tufted skin), in slate scree and rime;
  - the rim crawler, a palette variant of the tide crawler: chalk with black joints and dimmer wounds.

  The base jobs (reef crab, wallcrab, wreck crab, sail leech and slag tortoise) still verify identical.
