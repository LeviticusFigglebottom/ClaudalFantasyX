---
id: M3-RND-01
title: "Reefball arena look: the suspended water sphere (surface, refraction, the player-inside read, cost)"
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: character
depends_on: [M2-RND-02]
milestone: M3
request-from: "lead"
---
## Goal
SPEC §6.10: Reefball is played inside a suspended sphere of water (the default form), and SPEC's underwater
list (fog volume, god rays, particulate, caustics on characters) names Reefball. This is the R&D for the
sphere's look, on the PC GPU, before a Reefball zone exists. The UnderwaterRig (M2-RND-02/09) assumes a flat
rest plane; a sphere needs its own surface and an inside/outside test.

## Acceptance criteria
- [ ] **The sphere's surface, from outside:** a refracting, reflecting water ball, a few tens of metres across,
      held in the air. It has a rim Fresnel, refraction of the players and the far stands through it, and a slow
      surface swell that stays spherical. Water look swatches from palette.json (the lagoon set).
- [ ] **From inside (the player's view):** the underwater look applied with a spherical boundary. That means
      per-pixel absorption and in-scatter to the sphere's wall, total internal reflection and a Snell window on
      the inside of the wall, and the stadium seen warped through it. Plus god rays from the arena lights,
      particulate, and Rhen's lantern behaviour if it's in play.
- [ ] **The crossing:** a camera passing through the wall gets a clean, antialiased split (as M2-RND-09's
      waterline).
- [ ] **Cost** at High and Low, 1440p and 1080p, from outside and inside, against the tier budgets. Include a Low
      path that drops refraction for a tinted, Fresnel-only shell if needed.
- [ ] Key frames in `docs/kb/qa/gpu/`, outside, inside and crossing, for Art (character) to review against the
      colour script.

## Notes
- Caustic light on characters (SPEC §8.2 item 2, still open in tech/underwater.md) is needed here as well. File it
  separately if it outgrows this task.

## Review log
