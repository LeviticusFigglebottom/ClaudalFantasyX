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
- Hullgnaw: the strike plunges the head into the deck; the intro and KO rise from and sink into solid planks. Fixed
  (2026-10-30): a breach in the deck is part of its model, and the intro, KO and frames go through it (a test holds
  it there). Gnaw lunges level (contact 0.8). Rib Lash (0.8), Thrash (1.25) and Coil have their own clips, and
  idle_b is authored. See docs/kb/art/creatures/act1/hullgnaw.md, "Move pass".
- Drownbell: its feet slid with every rock of the bell (up to 23 cm in the slam, 32 cm in the intro), five skills
  shared `cast`, hits and the flood phase barely moved, and `idle_flood` and `ready` looked like `idle`. Fixed: the
  feet are planted by IK at every frame; each skill has its own clip and contact (`toll` 1.0 s unchanged,
  `toll_gather` 1.6, `flood_surge` 1.0, `undertow_surge` 1.3, `rouse_polyp` 1.2, the slam 0.8); a lower, slumped
  flood stance with flood versions of the slam, the hit and `ready`; and a bigger intro, hit and phase change
  (docs/kb/art/creatures/drownbell.md "Move pass").

## Review log
