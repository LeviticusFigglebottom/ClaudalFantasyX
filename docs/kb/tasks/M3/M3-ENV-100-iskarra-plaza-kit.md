---
id: M3-ENV-100
title: "Request: an Iskarra plaza kit for the Prologue (the game's first frames are still primitives)"
role: environment
status: done
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
The Prologue, "The Last Time" (`prologue_iskarra_dusk`; color_script.md "Prologue"), is the first scene a new game
shows, and its whole set is still made of primitives (`game/levels/prologue/prologue.tscn`, City/*):
- a 600 m flat water plane;
- a 34 × 18 m box terrace and a 10 × 6 m box rise;
- nine cylinder "white towers" (radius 5–6 m, up to 52 m), with cylinder caps and crowns;
- box arches (two posts and a lintel) and a fallen pillar;
- four cylinder lamp columns with sphere heads.

The human's playtest calls these "primitive moments". Cinematics has replaced every other one in the M2 slice
(M2-FP-116 moved the First Verse into the real shrine). The Prologue is the one left, and no kit has Iskarra's
architecture. The Oruvel Underway kit is Lit Age, but it is drowned and grown over.

## What the set has to hold (keep the staging; it is reviewed)
- **The plaza.** A terrace at deck height y 1.0 (the cast stands at y 1.0; Toma and Ysolde at 0.4 on a lower step)
  over still water at y 0.
  - Rhen at (1, −0.4); Asha at (−3.2, −3.0) with the `by_asha` mark beside her.
  - The vigil silhouettes far apart across the plaza: Toma (−12, 3.5), Ysolde (7.5, 1), Kerrid (9.5, −5.5),
    Pell (−12, 1.5) and Liss (4.5, −6.5). "Seven silhouettes apart, each keeping a vigil."
- **The white towers.** Lit Age ceramic, "dwarfing" the cast, from 40 to 70 m north (−Z). Today: (−46, −70)
  52 m, (−8, −60), (26, −40), and six more. Gorgeous and doomed (Pillar 2): whole, not ruined. The Lit Age is
  dead, but Iskarra still stands.
- **An arch** at (−18, −18) about 10 m tall, framing the towers, and a fallen pillar.
- **Four lamp columns** around the plaza (nothing lit: "there is no fire; the one practical is Rhen's oil
  lantern").
- **Shots.** P01 is wide from (1.5, 3.4, 21) toward (−4, 7.5, −40) at 40°. P02 is the two-shot from
  (−0.3, 2.4, 1.6) toward (−2.8, 2.0, −2.8) at 32°.
- **Light.** Dusk 18:40, the sun at 3° and 285° (behind the towers, frame-left in P01). Key `#FF9F46` 2.2, rim
  `#F2A64A` 1.4, fog albedo `#C98A5A` at 0.012, and the `lagoon_low_sun` water.

## Reuse
- **Ch9's Iskarra vigil (B10).** M3-C09-04 asks for "the Prologue's plaza pieces" to dress its stand-in plaza.
- **Ch19 "Iskarra"** (color_script.md) plays in the same zone (`prologue/iskarra_dusk (full)`) and adds the spire.

One kit should serve all three: build it as a kit with a design note, in the usual format.

## Acceptance criteria
- [ ] Design notes `docs/kb/art/environments/iskarra.md` (references in words only).
- [ ] A procedural kit under `assets_src/environments/kits/iskarra/`, with PROVENANCE rows.
- [ ] A swap-in note for cinematics (slice-polish): which pieces replace which City/* node, and at what heights.
  Cinematics swaps them into `prologue.tscn` and keeps the staging and the shots.

## Review log
- 2026-10-27, slice-polish: superseded. Env-art built the Iskarra kit and a drop-in scene under M3-ENV-710 (big12), and slice-polish swapped it into the prologue under M3-ENV-711.
