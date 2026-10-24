---
id: M2-HER-1105
title: "Clip gaps for natural hero motion: run, turn-in-place, walk start and stop (request to the characters track)"
role: character
status: todo
owner_session: ""
reviewer: cinematics
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
What the hero motion layer (M2-HER-1101..1104) still fakes procedurally, as clips on Rhen, Asha and Toma, in place, in the
hero_clips.py pipeline. The exact list is filled in below and mirrored in the characters live log.

## Acceptance criteria
- [ ] The list below, built and committed with the libraries regenerated.

## Requested clips
Draft (2026-10-24; final after the field and cutscene passes). All in place (no root motion), the 31 body bones,
for Rhen, Asha and Toma, with each persona's sway and stance. The motion layer blends to and from `idle`, `walk`, `run`.

| Clip | Loop | Why (what the layer fakes today) |
|---|---|---|
| `walk_start` | no, ~0.45 s | the first step from idle: weight shifts onto the stance foot, the lead foot lifts (today: a blend idle -> walk) |
| `walk_stop` | no, ~0.5 s | the trailing foot comes alongside, the body settles (today: a blend walk -> idle, feet can slide) |
| `run_stop` | no, ~0.6 s | a two-step brake from a run, the torso leans back then settles |
| `turn_in_place_l90`, `turn_in_place_r90` | no, ~0.6 s | head leads, then chest, hips and a foot step (today: the whole body rotates on the spot) |
| `turn_in_place_180` | no, ~0.9 s | a stepped about-face (today: a rate-capped spin) |
| `idle_shift` | no, ~2.5 s | a weight change onto the other leg, for long idles (today: procedural micro-motion only) |

Story clips for the M2 beach scene that are still missing are in M3-CHR-01's `requested_clips.json` (Rhen
`sit_up`, `sit_in_shallows`, `turn_from_sea`, `stand_unsteady`); not repeated here.

## Review log
