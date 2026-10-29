# Chain lamp (`chain_lamp`), Ch19

**Where:** the Iskarra Lamp Spire (act_outline Ch19). **Kind:** Lit Age construct. **Role:** a hazard-foe. Every few
turns its beam sweeps the field, so the player learns to act between beams. Pillar 4: the timeline shows the beat. The
chapter designer sets the beat, the stats and the AI.

## The idea

One of the spire's own lamps, a Lit Age signal lamp: an eight-sided brass lamp-cage on a long chain from the spire's
dark ceiling. Its bound light sits inside behind eight hinged louvres. The keepers swept it over the sea to call boats
home, and it still sweeps on the beat it was set to a thousand years ago, over a room that has no sea in it.

The one exaggeration: **a hanging lamp that keeps its own time.** Its parts are a real signal lamp's (louvres, a
gimballed cage, a chain and shackle). It only works by itself.

**How its beat keeps the bound-light rule.** `glimmer_bound` is steady: no flicker, no pulse (color_script.md rule 2).
So **the light never changes; the louvres do.** On the beat the louvres open a hand's width and shut again, and the
light seems to pulse while its emission holds. The sweep is the same: the louvres on one side open and the cage turns.

## Silhouette and size

- **The cage:** an octagonal lantern **0.9 m tall and 0.55 m across**, a domed brass cap with a finial on top and a drip
  cone underneath. Eight louvred sides, each louvre a tall brass leaf on a vertical hinge.
- **Its height:** the cage hangs with its base at **0.9 m** and its cap at **1.8 m**, at the party's chest, where the
  beam meets them.
- **The chain:** heavy iron, rising straight up from a shackle on the cap to a ring at **5.0 m**. That is above the
  battle frame's top edge at every sandbox enemy mark (3.9–4.2 m there), so in battle the chain runs out of frame and
  the lamp reads as hung from the dark. Nothing else on the field is a vertical line with a light on it.
- **Battle camera** (about 110 px a metre at 720p): the cage is about 100 px tall and 60 px wide, with a chain line
  above it to the top of the screen. It has no facing, so it fits any of the three enemy marks with room to spare.
- **Kept apart from the drowned lantern** (Ch20): that one is a round glass globe that floats with no chain above it,
  its chains hanging below, in held cyan. This one is an eight-sided brass cage on a chain from above, in bound teal.
- **Stand-in:** `height` 1.8 (the cap), radius 0.35. `chest` (1.08 m) is inside the cage, `head` is the cap.

## Palette

| Part | Albedo | Light |
|---|---|---|
| Cage frame, cap, louvres | `brass` going to `bronze_patina` on the cap; louvre edges worn bright | none |
| Chain, shackle | `lacquer_black` iron, dry | none |
| The lamp inside (a salt-glass core seen between the louvres) | `salt_glass` | `glimmer_bound` `#4FB3B0`, energy 1.5, **steady** |
| The inner faces of the louvres | `lit_ceramic` (a reflector: what the beam comes off) | none |
| The shackle pin | `lacquer_black` | the weak point (below) |

The beam itself, a cone of bound light thrown from the open side, is **battle VFX**, not the model. It is
`glimmer_bound` and steady, and it moves only because the cage turns (rule 2: bound light moves only with its housing).

## Weak point (ADR 0151)

**One small closed `spawn_wound` mark:** a hairline crack round the shackle pin where the chain meets the cap, 4 cm.
It is a construct, so it has no open seam and no motes. It is the one part that, broken, ends it: the KO is the
shackle parting.

## Battle read and clips

**At battle distance:** a lamp hanging on a chain from the dark, light showing through its louvres in slits, opening
on a beat.

| Clip | Length | Contact or peak | What it shows |
|---|---|---|---|
| `idle` | 4.0 s, loop | | It sways 2° on its chain (0.11 m at the cage). **Two beats a loop:** at 1.0 s and 3.0 s every louvre opens 25° and shuts again over 0.3 s. That is its slow fixed beat; the light behind holds steady. |
| `attack` (the flash) | 1.0 s | contact 0.45 s | The two louvres facing the target snap open 80° and shut: a short beam (VFX) on one foe. |
| `cast` (the sweep) | 2.6 s | contact 1.3 s | The louvres on one side open 80°. The cage turns one full turn on its chain over 0.4–2.2 s, so the beam crosses the whole field. The contact is when it crosses the party's side. Then they shut. |
| `hit` | 0.6 s | peak 0.10 s | The cage is knocked back on its chain and swings, a decaying swing that has settled by the end. The louvres rattle half open. |
| `ko` | 1.8 s | | The shackle parts at 0.3 s. The cage falls the 0.9 m to the floor (lands 0.75 s), tips onto its side and rocks still. Every louvre shuts as it lands, so its light is shut in: the lamp goes dark without a mesh swap. The broken chain end whips up out of frame. |

**No travel.** A hanging lamp never leaves its chain. Its skills need a `travel: none` style in choreo.json
`style_by_skill` (open questions). The sweep's `beam` bone gives battle VFX the cone's origin and direction.

## Rig and budget

20 bones:
- `root` (the floor origin);
- a chain of 8 hanging from y 5.0;
- `shackle`, `cage`, eight louvres;
- `beam` (an attach bone at the cage's centre, pointing out of the louvres that open in the cast).

Five slots: `cage`, `louvre`, `lamp`, `chain`, `pin`. **Budget ≤ 5k triangles:**
- the cage and its louvres, about 2.8k;
- 26 chain links, about 1.3k;
- the cap and finial, the rest.

## Grounding

Built hanging, with its origin at the floor (as Nhoa is built hovering), so it needs no `stand_in.hover`. The cage's
lowest point is at 0.9 m in every clip except the `ko`, which lands it on the floor (y ≥ 0). The chain's top is a fixed
point that never moves.

## Open questions (for Combat and the chapter designer)

- **The beat.** How many turns between sweeps, and how the timeline shows it (UI's: pillar 4 says the player always
  knows). The model gives only the sweep clip; the idle's beat is a look, not a timer.
- **Can a sweep be dodged by timing** (act between beams), or is it a field attack on everyone? The clip works either
  way; its contact is the party's side.
- **Travel.** Every skill it has needs `travel: none` (a `style_by_skill` entry like the Drownbell's toll; battle
  presentation's file), or the sequencer will try to walk a hanging lamp across the room.
- **With the wick crawler:** does the crawler relight a chain lamp whose shackle has parted (a revive that lifts it
  back), or only buff one still hanging? A revive needs a `revive` clip (the reverse of the KO), which is cheap to add.
