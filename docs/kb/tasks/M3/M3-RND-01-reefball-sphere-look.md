---
id: M3-RND-01
title: "Reefball arena look: the suspended water sphere (surface, refraction, the player-inside read, cost)"
role: rendering
status: review
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
- [x] **The sphere's surface, from outside:** a refracting, reflecting water ball, a few tens of metres across,
      held in the air. It has a rim Fresnel, refraction of the players and the far stands through it, and a slow
      surface swell that stays spherical. Water look swatches from palette.json (the lagoon set).
- [x] **From inside (the player's view):** the underwater look applied with a spherical boundary. That means
      per-pixel absorption and in-scatter to the sphere's wall, total internal reflection and a Snell window on
      the inside of the wall, and the stadium seen warped through it. Plus god rays from the arena lights,
      particulate, and Rhen's lantern behaviour if it's in play.
- [x] **The crossing:** a camera passing through the wall gets a clean, antialiased split (as M2-RND-09's
      waterline).
- [x] **Cost** at High and Low, 1440p and 1080p, from outside and inside, against the tier budgets. Include a Low
      path that drops refraction for a tinted, Fresnel-only shell if needed.
- [x] Key frames in `docs/kb/qa/gpu/`, outside, inside and crossing, for Art (character) to review against the
      colour script.

## Notes
- Caustic light on characters (SPEC §8.2 item 2, still open in tech/underwater.md) is needed here as well. File it
  separately if it outgrows this task.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
A prototype rig and a test scene; the details are in docs/kb/tech/water_sphere.md. Key frames are in
`docs/kb/qa/gpu/reefball/` (`sheet.png`: outside, inside, looking up into the sun, crossing at High; outside and
inside at Low). Reviewer: **Art (character)**, against the colour script's Act I festival match.
- **Outside:** refraction (with no ghosting of the players in front of the wall), a Fresnel sky reflection and the
  sun's glint. The ball absorbs what's behind and inside it.
- **Inside:** the underwater look up to the wall. The Snell window shows the stadium refracted, with TIR outside it,
  and god rays come from the sun.
- **The crossing:** a clean split with a 1.5 px meniscus line.
- **Cost (RX 9070 XT):** +0.08–0.24 ms from outside, +0.13–0.50 ms from inside, Low to Ultra, 1080p to 1440p.
- **Low:** a tinted Fresnel shell with no refraction or god rays.
- **Open:** caustics on the players (SPEC §8.2), snow, a night match with the lantern, and the reflection-before-water
  split at the rim.
- Four shots are pending a lavapipe baseline: `docs/kb/qa/gpu/2026-10-24-reefball-pending-shots.json`.

## Review log
