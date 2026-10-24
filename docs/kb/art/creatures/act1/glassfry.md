# Glassfry (`glassfry`), Ch1 Oruvel Underway

*Renamed from `wickfry` (m2-slice, act1_ch01 §9): the word "wick" stays Mother Kell's.*

## The idea

A shoal of finger-long glass shrimp that live in the drowned tower and swarm to lamp light. Divers call them glassfry, for
the glass of them: you see the light through their bodies before you see the bodies. Fought as **one** combatant: a loose cloud of about 40 shrimp that
tightens into a fist to strike. A reef beast, not spawn: harmless-looking and very fast.

The one exaggeration: they move **as one body**.

## Silhouette and palette

- A loose cloud about 1.1 m across at chest height (hover 0.6 m), denser at its centre: at battle distance a glinting
  haze, read by its movement and by the 40 tiny lights of their eyes.
- Each shrimp: a curved translucent body (`salt_glass`, rim sheen), legs a fringe, black eye-dots
  (`lacquer_black`). The weak point is the cloud's heart: one larger shrimp with a `spawn_wound` glow it carries
  from feeding near the tower's dead (it reads as the cloud's lit centre).

## Clips

- `idle`: the cloud breathes (expands and contracts) and drifts in a slow circle; every shrimp flicks on its own phase.
- `attack`: the cloud tightens to a fist and darts forward, then bursts apart.
- `cast`: the cloud spreads into a ring and spins (a dazzle).
- `hit`: the cloud scatters and re-forms.
- `ko`: the shrimp sink and scatter, a few at a time, the heart's glow last.

Built as ~40 small rigid meshes on their own bones (one bone per shrimp, parented to a few cloud bones), so clips move
the cloud and each shrimp. Budget ≤ 5k triangles (~110 per shrimp).
