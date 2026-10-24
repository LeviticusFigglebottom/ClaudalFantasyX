# Lantern eel (`lantern_eel`)

> *"It hangs a cold light in the shallows. Divers who follow the light are not found."* (`LORE_LANTERN_EEL`)

**Battle role:** the caster. Quick (agility 14), high magic defense, weak to fire, immune to lightning. Its one skill
is `lure_glow`, a magic attack. The read has to say **watchful, swaying, the light is the threat**.

## The idea

A moray-like eel that has learned to look like a lamp-diver. Lamp-divers (Rhen's trade) work the reef by the warm
light of a caged oil lamp. The eel grows a **bony cage on a stalk** from its brow, and inside the cage it holds a
cold point of light. From under the water, at a distance, it is a diver's lamp. Up close, the light is the wrong
colour: cold, still, sea-white, not the warm flicker of oil.

The one exaggeration is the **lantern-cage lure**. The rest is an eel: a long laterally flattened body, a continuous
dorsal fin, a heavy jaw, small eyes set far forward.

## Silhouette

- **A tall S-curve.** It rises out of the water or sand to 2.1 m at the head, with the body leaning toward the party,
  so its silhouette is a **question mark** with a lit point hanging in front of the face. Nothing else in the slice
  stands that tall and that thin.
- **The lure** hangs on a curved stalk 0.5 m long from the brow, swinging slightly in front of the head: the cage is
  six thin ribs around the light, the shape of a small lantern.
- **The dorsal fin** runs the whole length, a translucent frill that catches backlight.
- **The jaw** is long and slightly open, with a row of fine teeth catching the light.

## Palette

| Part | Swatch | Notes |
|---|---|---|
| Back and flanks | `deep_teal_shadow` `#0E4A55` to `abyss_navy` `#061A2B` along the spine | Wet and glossy (clearcoat): it lives in the water |
| Belly | `sand_wet` `#B59D74` | A pale line along the underside of the S, so the curve reads against dark water |
| Flank spots | `sea_glow` `#1C6B78`, faintly emissive | A row of photophores, its own bioluminescence (not glimmer) |
| Dorsal frill | `lagoon_teal` `#1FA3A6`, thin and translucent | Back-lit by the low sun in C08-type light |
| The lure cage | `bone` `#E6DAC0` | |
| **The light in the cage** | `salt_glass` `#BFE6E0`, emissive | Cold and steady. **Never** `oil_lamp` and never a glimmer swatch: it is a creature imitating a lamp, not the dead |
| **Weak point** | `spawn_wound` `#3FE0C8` | The gill slit behind the jaw, a small glowing seam |

## The battle read

- **At 9 m:** a tall dark curve with one cold bright point in front of it. The light draws the eye first, which is the
  point (the lore), and the belly line gives the shape.
- **Idle:** a slow figure-of-eight sway of the whole S (1.5° to 3° per segment, travelling up the body), the lure
  swinging a beat behind the head, the jaw breathing.
- **Facing:** three-quarter toward the party, the lure between them.

## Clips

| Clip | Read | Timing |
|---|---|---|
| `idle` (loop) | The travelling sway; the lure pendulum lagging the head | 3.0 s |
| `attack` (a bite; no slice skill uses it yet) | Coil back (the S tightens), then a straight lunge and a jaw snap | 1.1 s, contact at 0.55 s |
| `cast` (`lure_glow`) | **The tell:** the head draws back and **lifts the lure high and forward**, the cage swings toward the target and steadies; the body goes still while the light holds. Then a slow sway back | 1.6 s, release at 0.9 s |
| `hit` | The body kinks away from the blow at the middle, the head whips back, the lure swings wide | 0.5 s |
| `ko` | **The light goes first:** the lure droops. Then the S slackens from the head down, and the body folds down into a low coil on the ground | 1.6 s |

## Notes for the model

- Body: a tube along a spline, 16 segments, oval cross-section (taller than wide), tapering to the tail into the
  ground; the dorsal frill is a ribbon on the spine.
- A chain of 9 spine bones plus jaw and two lure bones. The body deforms smoothly (skinned), the cage is rigid.
- Budget: ≤ 9k triangles.
- Battle VFX anchors (fractions of 2.1 m): chest 1.26 m (the upper curve), head 2.1 m (the brow).
