# Hullgnaw (`hullgnaw`), Ch1 boss

**Where:** the breaking raft as the Rising tears Oruvel apart (act_outline Ch1). The game's first boss, a tutorial for
the turn-order timeline.

## The idea

Undertow-spawn: a great eel that grew **through** a sunken ship's hull. The ship's ribs ring its body like a cage
it carries; where the eel swelled between them the timber split, and the wounds bleed `spawn_wound` light. It is the
lantern eel's dark cousin: no lure, no beauty of its own, only what it took. It rises out of the water between the
raft's planks with the ribs streaming weed.

The one exaggeration: **the ribs it wears**. The eel is an eel; the ribs are a real ship's frames, oak gone black.

## Silhouette

- A thick black body rising 2.8 m in a hunched arc, then falling forward over the raft, the head low and forward.
- **Five curved ribs** round the body, spaced along it like a rib cage turned outside in, their broken ends
  sticking out past the body: a spiky, broken outline nothing else in Act I has.
- A blunt head with a lower jaw too wide for it, teeth like nails.

## Palette

`lacquer_black` to `abyss_navy` wet body (clearcoat); ribs `timber_weathered` darkened to near `lacquer_black` where
wet, with `bone`-pale salt at the broken ends; wounds between the ribs `spawn_wound` (emissive), shedding
`glimmer_held` motes (VFX). Eyes small, `spawn_wound` pinpoints.

## Battle read and clips

- **At battle distance:** a black arch hung with pale broken spars, cyan seams between them. Taller than Toma.
- `idle`: the body heaves with the swell, the ribs creak (they lag the body by a beat), the jaw works.
- `attack` (a slam): it rears back through the ribs, then falls on its target; contact at 0.8 s of 1.5 s.
- `cast`: the ribs spread like a trap opening and the wounds flare; a held breath.
- `hit`: the body flinches inside the ribs (the ribs barely move: they are dead wood).
- `ko`: it slides back down between the planks; the last thing seen is a rib going under.

Budget ≤ 14k triangles. Rig: a spine chain of 10, jaw, five rib bones (each riding one spine bone).

**Phase `breaking`** (m2-slice act1_ch01, 50% HP): the ship's frames are their own mesh, `Ribs`. `phase_break` (1.8 s)
thrashes the body while the frames burst off and fall into the water, and `hide_after: ["Ribs"]` removes them once
the clip has played. From then on it fights bare, with the wounds the frames held shut in plain view.
