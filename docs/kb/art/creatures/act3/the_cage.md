# The Cage (`the_cage`), Ch20 boss frame

**Where:** the last layer of the Undertow (act_outline Ch20: "the four bound founders, Orin Tesk, Halde Moor, Isse
Varan, and Cael Imbrey, fought as one multi-part boss. They thank the party as they fall"). After it falls, the last
remembered room dissolves and the walk to the heart begins (act3_ending.md H01). **Kind:** Lit Age construct, boss
frame. **What this sheet covers:** the frame only. The four founders' figures are the characters track's (act3_roster
"What this track does not build"). This sheet gives them their places, their bones and their cues.

## The idea

Four Lamplighters (bible §3, the Founding: "lamp-engineers and singers") bound themselves around the first heart a
thousand years ago. The Cage is what they built to hold themselves there. It is a lattice of Lit Age lamp-bars and
chains, and it still works. The figures stand in it the way they chose to stand: upright, facing out, their backs to
the heart, guarding it. The lattice is not cruel. It keeps them, as the Lamp Engine kept its lamps.

The one exaggeration: **a lamp-housing built to hold a person.** Every part is a real Lit Age lamp-fitting:
- salt-glass chimney tubes for bars;
- gimballed crown lamps;
- a lantern's hinged doors for the gates;
- mooring chain to anchor it.

It is simply built at the scale of a body, four times over.

Original design (README rule 1). It is not a crystal, a prison block, a throne or a wheel. It is a row of four lamp
bays on a shallow arc, read as one object.

## Silhouette and size

- **Plan:** four bays side by side on a shallow arc, convex toward the party, as if they are the near quarter of a ring
  around the heart that the dark water hides. The chord is **4.0 m** and the arc is 0.35 m deep. Bay centres sit at
  local x −1.5, −0.5, +0.5 and +1.5. The outer bays are at z 0.16, turned 15° outward. The inner bays are at z 0.33,
  turned 5° outward.
- **Height:** a base rail 0.3 m high carries the four sills (y 0.30).
  - The two **inner bays** rise to their crown lamps at **3.3 m**.
  - The two **outer bays** rise to **2.9 m**.

  The stepped crown reads as one object with four parts, not four objects.
- **Each bay:** 0.8 m clear between its two side posts and 2.1 m clear above the sill (to y 2.4). Its arch closes over
  the head in a keystone clasp.
  - Its front is open from the knee up, so the founder is seen. Pillar 4: the player can see who is in it.
  - Three thin gate bars cover only the lower 0.55 m, at the shins, and part of the two gate leaves.
- **Anchor chains:** one per bay, from the back of its base rail down and back to an iron ring set in the floor, 1.2 m
  behind. They are held, not hanging: the frame is moored to the dark below.
- **Battle camera** (`battle_sandbox.tscn`: 40° from about 9 m, about 110 px a metre at 720p). The Cage is the only
  combatant, so it needs no slot spacing, but it is too wide for a slot as it is. These numbers are for its mark at
  (−2.2, 0, −0.1), between the sandbox's three enemy marks, with `stand_in.yaw_deg` **45**. That turns its face
  halfway between the party and the camera, so all four bays read, where a facing of 90 would show the camera its end.
  - It spans 0.12–0.46 of the screen width.
  - The nearest crown is 0.12 from the top of the screen.
  - A founder (1.75 m) is about 190 px tall.

  On the sandbox's slot 0 (−2.4, 0, 0.9), the near end reaches 0.02 of the screen width, too close to the edge.
  So the arena should give the Cage its own mark (open questions).
- **Stand-in:** `stand_in.height` 4.3, radius 2.0. The VFX anchors are fractions of the height (effects.json). At 4.3,
  `chest` (0.6) lands at 2.58 m, the row of keystone clasps, so **hits land on the frame, never on a founder's face**.
  At the frame's true 3.3 m, `chest` would land at 1.98 m, on the founders' heads. `head` (1.0) puts the damage
  numbers just above the crowns.

## Where each founder sits

Proposed order, from the Cage's own left (local −x, the end nearest the camera at yaw 45) to its right: **Orin Tesk,
Halde Moor, Isse Varan, Cael Imbrey** (the order act_outline names them). Quarters are numbered q1–q4 in that order.
The characters track and the chapter designer may reorder them. The build takes the seating as a list.

| Quarter | Bay | Founder | Sill (attach) | Wrist rings |
|---|---|---|---|---|
| q1 | outer left, crown 2.9 m | Orin Tesk | (−1.5, 0.30, 0.16), facing 15° out | ±0.36 m either side of the bay centre, y 1.10, 0.10 m behind the sill's front |
| q2 | inner left, crown 3.3 m | Halde Moor | (−0.5, 0.30, 0.33), facing 5° out | as q1 |
| q3 | inner right, crown 3.3 m | Isse Varan | (+0.5, 0.30, 0.33), facing 5° out | as q1 |
| q4 | outer right, crown 2.9 m | Cael Imbrey | (+1.5, 0.30, 0.16), facing 15° out | as q1 |

**The pose the frame expects:**
- Standing on the sill, back to the bay's spine bar, facing out of the bay.
- The arms are down and a little out and back, each wrist in a lamp-bar ring at hip height, the palms open forward.
- It is a standing vigil, as at the Prologue's dusk. It is **never arms spread wide or raised**: the frame must not
  stage a crucifixion.
- A figure up to 1.9 m tall fits the 2.1 m clear height.

## Bones and attach points the characters track needs

Each quarter has these bones (in model space, the Cage facing +z):

| Bone | What it is | Who uses it |
|---|---|---|
| `q<n>_sill` | the figure's root: on the sill at the feet, +z out of the bay | characters: a `BoneAttachment3D` holds the founder's figure scene, which plays its own clips |
| `q<n>_wrist_l`, `q<n>_wrist_r` | the ring centres, hinged so they spring open | characters: the hands' targets in the bound pose |
| `q<n>_crown` | the crown lamp's gimbal, above the head | rendering: the bay's small key light on the founder's face |
| `q<n>_clasp` | the keystone clasp, the weak point | battle VFX: the break's shards |
| `q<n>_bay`, `q<n>_gate_l`, `q<n>_gate_r`, `q<n>_chain_0..2` | the bay frame, its two gate leaves, its anchor chain | the frame's own clips |

The founders' scenes are instanced into `game/creatures/the_cage/the_cage_battle.tscn` (ours) by the characters
track's path. The scene holds a node per founder (`FounderQ1` … `FounderQ4`) so the phases can hide each one.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The frame (rails, posts, arches) | `brass` going to `bronze_patina` with a thousand years under water; `lacquer_black` joints and hinge pins | none |
| The lamp-bars (posts and arch ribs are salt-glass chimney tubes) | `salt_glass` | `glimmer_bound` `#4FB3B0`, energy 1.2, **steady** (README rule 3: a construct's bound light) |
| The crown lamps | `salt_glass` globes in `brass` gimbals, the rims `gold_leaf` (a thin line, far inside the 5% gold limit) | `glimmer_bound` 1.2, steady |
| The wrist rings, gate bars | `brass`, worn bright where the wrists rest | none |
| The anchor chains and floor rings | `lacquer_black` iron, wet (clearcoat), `bronze_patina` bloom | none |
| The keystone clasps | `brass` | the weak point: one small mark in `spawn_wound` |

Ch20 is lit only by glimmer (color_script.md, `act3_abyss`: `glimmer_held` cyan dominant, `glimmer_bound` secondary).
The Cage is the one large source of **bound** light in the held dark, so it reads at once as the Lit Age's work. The
lit bars should stay under about 10% of the battle frame, well inside the 35% set-piece limit. **No `glimmer_lift` on
the frame, ever:** the lift belongs to the founders at their fall (rule 1), which is VFX and the characters track's
material.

## Weak point (ADR 0151)

**One small closed `spawn_wound` mark on each quarter's keystone clasp,** four in all: a hairline seam across the
clasp, 6 cm, never open and never shedding motes (a construct). Four marks on one foe is the justified exception, the
Lamp Engine's case (one mark per breakable part). Each mark says "this quarter breaks here."

The marks sit above the founders' heads on purpose. **The party strikes the lock, never the person in it** (pillar 1).
A broken quarter's mark is gone: the broken mesh carries no emission.

## Battle read and clips

**At battle distance:** a wide, stepped row of four lit lamp bays on a shallow arc, a still figure standing in each,
chains running back into the dark. As the fight goes on, the row loses one lit bay at a time.

| Clip | Length | Contact or peak | What it shows |
|---|---|---|---|
| `idle` | 6.0 s, loop | | The lattice flexes a degree or two as if water moved through it. The anchor chains ease and draw. The crown lamps sway a little in their gimbals. The light never changes. The founders' own idles are the characters track's. |
| `attack` (the drag) | 1.4 s | contact 0.6 s | The anchor chains snap taut together and the whole frame leans back 4°, pulling: the held drag of the anchor. The hit VFX is a pull toward the Cage. |
| `cast` (the tightening) | 1.8 s | contact 1.0 s | Every gate leaf draws in 10° and the arches close a notch, a held breath; then it eases. |
| `hit` | 0.6 s | peak 0.10 s | The struck side jolts back on its rail, the crown lamps swing, the chains snap. `hit_b` (the kit's mirror) takes the other side. |
| `break_q1` … `break_q4` | 4.0 s each | | A quarter breaks (below). These are its phase changes, one per quarter. |
| `ko` | 5.0 s | | The last quarter breaks as the others did (0–4.0 s). Then the empty frame lets go: every anchor chain falls slack, the base rail settles 0.1 m, and the arches lean outward. It ends on the floor (y ≥ 0), open. |

**No travel.** A moored frame never leaves its mark. Its skills need a `travel: none` style in choreo.json
`style_by_skill`, as the Drownbell's toll has (open questions).

### A quarter's break (`break_q<n>`, 4.0 s)

The phase hides `Q<n>Whole` and shows `Q<n>Broken` at once (CreatureActor `hide`/`show`). The broken mesh is the same
bay with its lamp-bars cracked and dark (the shader's emission is static, so the light goes out by the swap, as the
flat-engine's window does), modelled **open**. The clip starts with its gate and ring bones keyed shut and ends at rest
(open). So every later clip, which leaves those bones at rest, shows the quarter open with no extra clips.

| Time | The frame | The founder (characters track; proposal) |
|---|---|---|
| 0.0–0.3 s | The keystone clasp springs apart; the arch's two halves part at the top. The bars are already dark. | still |
| 0.3–0.6 s | The wrist rings spring open. **0.5 s is the founder's cue.** | the wrists come free |
| 0.5–1.5 s | The gate leaves swing outward and down, 70°, like a lamp-housing's doors falling open. | they step down off the sill (0.3 m) and take one step toward the party |
| 1.0 s | The anchor chain parts at its floor ring and slides slack. | |
| 1.5–2.5 s | The bay sags 6° outward on the rail. The dark crown lamp swings in its gimbal. | they stand and look at the party: the thanks (the line is story's and the chapter designer's) |
| 2.5–4.0 s | The bay stills. | they go down on their knees, and their light makes rule 1's 1.5 s lerp from bound to `glimmer_lift` and rises (VFX motes, the figure's material: characters and battle VFX). The figure is hidden at 4.0 s (`hide_after` `FounderQ<n>`). |

Each founder is given 3.5 s from release to gone, the length of a Vowbound's `release` (3.3–3.5 s, M3-CRE-647), so the
four falls feel like the six releases before them. The founders never fall forward on their faces, and the frame never
throws them. They step down free.

**After each break:** that bay hangs open and dark, its gate leaves down, its chain slack. The other quarters stay lit.

## Rig and budget

46 bones:
- `root` and `frame` (the arc and base rail);
- per quarter: `q<n>_bay`, two gate leaves, the clasp, the crown, two wrist rings, the sill, and an anchor chain of 3.

The founder figures are not in the GLB. Five slots: `frame`, `lampbar`, `crown`, `chain`, `clasp`.

**Budget:** ≤ 22k triangles in the GLB, since every quarter is there twice (`Q<n>Whole` and `Q<n>Broken`, about 2.5k
each), plus the rail, chains and floor rings. That keeps about 12k on screen at once. The founders' budgets are the
characters track's.

## Grounding

Grounded. The base rail stands on the floor (y 0), and the anchor chains end in rings set **on** the floor, not through
it, so no `ALLOW` entry is needed in `GroundedClipsTest`. The `ko` ends with every part at y ≥ 0. The `attack`'s lean
is about the rail's back edge, so the front of the rail lifts rather than sinks.

## Open questions (for Combat and the chapter designer, not the human)

- **One combatant, as proposed here** (the roster's open question). The board has three enemy slots, so four
  combatants plus a frame cannot each stand on a mark. Proposal: one `the_cage` row with **phases at 75, 50 and 25%
  HP** (`break_q1`, `break_q2` and `break_q3`, each with `hide`/`show`/`hide_after` as above), and the KO breaking the
  last quarter. If Combat wants the player to choose which quarter to break, that needs targetable parts, which the
  engine doesn't have. The art works either way: each quarter is its own mesh pair and clip, so any order plays.
- **The break order.** Fixed (the designer picks it and the `ko` opens the last quarter) or driven by charge skills
  (CreatureActor `break_parts`)? A fixed order is the proposal.
- **The last quarter's light at the KO.** The KO can't swap meshes, so the last quarter's bars stay lit while the Cage
  fades out (`foe_ko_alpha` 0). If that reads wrong, either Tech adds `hide`/`show` to the KO, or Combat adds a fourth
  phase just above 0 HP.
- **The thanks.** Is each founder's thanks an in-battle beat (a short line during `break_q<n>`'s 1.5–2.5 s) or a
  cutscene after the fight? The frame's timing assumes in-battle. A cutscene needs only the figures.
- **Its mark and choreography.** The arena needs a boss mark near (−2.2, 0, −0.1) rather than slot 0. All its skills
  need `travel: none` (a `style_by_skill` entry like the Drownbell's toll; battle presentation's file).
- **The VFX anchor height** (battle VFX): `stand_in.height` 4.3 so `chest` lands on the clasps, or a per-row anchor
  override if one is added.
- **For the characters track:** the founders' heights (≤ 1.9 m), their bound-light material (`glimmer_bound`, steady,
  as the Vowbound) and the `freed` clip timed to the cue at 0.5 s.
