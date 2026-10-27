# Hesk, the Cord-Keeper (`hesk`), Asha's Vowbound: design sheet (proposed, M3-CRE-643)

**Who:** the fourth Vowbound (docs/kb/story/vowbound.md §4): the glimmer of **Ama Quillo**, the 47th Cantor, about 175
years ago. She was an Ullari keth-reader and a devout believer who started *counting* on her pilgrimage, and hung
the arithmetic in keth among the thousands of cords in Cloudloom's open hall. She is bound at Cloudloom, on the
summit of the Ullar Heights (Ch12). **Kind:** a Vowbound: bound light. **Role:** an ally, Holy. Her battle identity
is holy damage, cleansing (she lifts statuses off the party) and Regen. Her Swell is *Pass-Cord*, a line of shining
knots across the field. **Status:** a sheet ahead of the build. She is not yet in vowbound.json; Combat adds the row.

**The idea:** a great condor whose wing feathers are **knotted cords**, patterned like Ullari weaving and lit from
inside. She clutches **a keth bundle** in one talon, the keepsake. She reads as **a reader, steady and plain**. She
is no angel and no thunderbird: a high-pass carrion-eater, the bird that lifts the dead off the passes. That is the
Ullari meaning, and it fits "her light is the truth held up to be read".

Original design (README rule 1). It starts from the Andean-type condor (broad fingered primaries, a ruff, a bare
head) and from keth, the knotted-cord records of the Ullari (docs/kb/glossary.md). The cords are the game's own keth,
not any real-world script.

## Silhouette and size

| | |
|---|---|
| Wingspan | **4.2 m** when spread, but she rests **perched**, wings half-folded and mantled: 2.6 m across at rest, so the HUD's right edge stays clear (Ilun's tail crossed it) and the span is kept for the clips |
| Height | 2.4 m perched (head at 2.1 m) |
| Perch | she stands on the water's surface on her talons, grounded: every frame at y ≥ 0 (GroundedClipsTest). The keth bundle hangs from her left talon to 0.1 m above the water |
| Primaries | each of the eight "fingers" of each wing is a **cord** (a twisted rope, 1.1–1.5 m), knotted along its length: long knots, figure-eights and single knots in readable groups, like keth |
| Ruff | a collar of short, soft cords around the neck, `gauze_white` |
| Head | a condor's bare head: smooth, `bone`, a small dark beak, with two soft eyes, never a vulture's grimace |

## The knots

Built as geometry by the build script, from a seeded `default_rng` and a small table of knot kinds: a bead (single
knot), a long coil (2–5 turns) and a figure-eight. Each cord carries 3–7 knots in clusters, the clusters spaced like
digits. The patterns can come from **real numbers**: the build script can encode "47", "7" and the Cantor counts from
vowbound.md as knot clusters on her primaries, so a reader who knows keth (Ysolde, in the Ch12 scene) could read her
wings. Narrative decides whether that is said aloud; the geometry costs nothing extra.

## Colour (palette.json swatches)

| Part | Albedo | Light |
|---|---|---|
| Body plumage | `overcast_slate` `#6F7E8E` toward `storm_slate` `#3E4A57` | none |
| Cord primaries and ruff | `gauze_white` `#EBE7DF`, cords twisted with a `sand_cloth` strand | `glimmer_bound` at 1.2 from inside, with a mask strongest **at the knots** (1.0) and faint along the cord (0.2): the knots are what shines |
| Head | `bone` | none |
| Eyes | `deep_teal_shadow` | `glimmer_bound` 0.55 |
| The keth bundle | `sand_cloth` and `faded_teal_cloth` cords | none: it is an object |

**The "white light" of vowbound.md.** The story calls it "the clean white light of the high passes". The palette
allows only `glimmer_bound` for Vowbound light, so she shines in `glimmer_bound`. The whiteness comes from the
`gauze_white` cords around that light, and from the high-pass lighting of the zone and the arena. That keeps one bound
light colour for every Vowbound (rule 2) and reads white against the slate body. If the Lead wants a true white-gold
holy light, that is a palette ADR (`glimmer_bound` is defined as the one bound colour), not a sheet decision.

## Clips

| Clip | Length | What it shows |
|---|---|---|
| `idle` | 4.0 s, loop | perched; she shifts her weight from talon to talon; the cords sway |
| `ready` | 1.4 s | the wings half open, the cords lift, the head raised |
| `attack` | 1.2 s, contact ~0.55 s | a wing-buffet: one wing swung forward, the cords lashing |
| `cast` | 1.6 s, contact ~0.8 s | the holy light: wings spread wide, the knots lit, held |
| `cleanse` (or `cast` again) | 1.6 s | wings brought forward and around the party's side in a lifting sweep, the way the high passes lift the dead. A separate clip only if Combat's cleanse skill wants one |
| `hit` | 0.5 s, peak ~0.1 s | a flinch, the head drawn into the ruff |
| `defend` | 1.2 s | the wings mantled forward |
| `ko` | 1.8 s | she settles down onto the water, wings spread flat, the head bowed |
| `victory` | 2.2 s | full span, the cords raised |
| `rise` | 2.6 s | from hunched and folded she opens and stands |
| `dismiss` | 1.0 s | folding and hunching down |
| `special` | 2.4 s, contact ~1.45 s | Pass-Cord: she spreads to the full 4.2 m, then sweeps both wings down and forward, and the line of shining knots runs across the field (VFX) |

## Rig and budget

About 26 bones: `root`, `body`, a 3-bone `neck`, `head`, three bones per wing plus a chain root for each cord
primary's base (the cords sway as soft chains), two bones per leg plus `talon`, and a two-bone chain for the bundle.
Up to 14k triangles; the cords and knots are about half of it. Six slots: `plumage`, `cord`, `head`, `eye`,
`bundle`, `ruff`.

## Open questions
- Her vowbound.json row (Combat).
- Holy light as `glimmer_bound` (the default above) or a new swatch (a Lead/art ADR).
