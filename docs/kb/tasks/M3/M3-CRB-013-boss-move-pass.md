---
id: M3-CRB-013
title: "Final-quality move pass: every move of the six Act I bosses and three Act I Vowbound, from the battle camera"
role: character
status: doing
owner_session: "creatures-b (the Lead's 2026-10-29 23:10 brief)"
reviewer: combat
depends_on: [M3-CRB-001]
milestone: M3
---
## Goal
ADR 0041. Each move (intro, idle, each attack, hit, phase change, defeat) self-rendered from the battle camera and
checked for: foot sliding, interpenetration and pops; a telegraph that reads before the blow lands; the silhouette
against the arena; close-up detail (faces where they have them); and every move having its own animation, not a
shared generic one.

## Method
A scratch fixture (never committed) freezes every clip at five beats (start, wind-up, just before contact, contact,
end) from the battle camera in the creature's own fight, plus head close-ups; a numeric pass samples every clip at
30 Hz for bone slide while grounded, depth under the floor, per-frame jumps, loop seams and skill-to-clip sharing.

## Findings (2026-10-29, big18)
- Systemic: most bosses play one `attack` and one `cast` for 2-6 different skills (the Reach 6 on 2, the Drownbell
  5 on `cast`, the Spar-wraith 5 on 2, the Hullgnaw 3 on `attack`, the Matron 4 on 2); Ilun's Brine Lash is his
  basic attack. Each skill gets its own clip (creatures.json `clip_by_skill`, phase `clips` maps for phase poses).
- Bottle hermit: the glass never moved, so every move read faint at battle distance. Fixed (9e2c4f93, 119af519).
- Hullgnaw: the strike plunges the head into the deck; the intro and KO rise from and sink into solid planks.

## Review log
