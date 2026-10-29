---
id: M2-BPR-100
title: "The Drownbell's boss intro: Toma's real body fills the right third of the frame"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-404]
reviewer: cinematics
milestone: M2
request-from: cinematics
---
## Goal
Seen in the PC render `gpu/render-m2-slice-fdec3cc` of `battle_boss_intro_drownbell` (rmse 0.064 against big10's
baseline). With big11's real battle heroes, Toma's body and shield stand large in the right third of the boss's
introduction frame, silhouetted beside the bell. In the big10 baseline the heroes were capsules out of frame.
The title card still reads, but the slice's one boss introduction now shares its frame with a hero's back.

## Acceptance criteria
- [x] (Done by M3-BPR-404's big11 fix, c1d1e3e6 and 60cbb212.) The intro camera, which already fits the boss's model bounds (M3-BPR-404), keeps the party's hero bodies out
  of frame or small and soft at its edge. Alternatively, the heroes are placed or hidden for the intro hold.
- [x] (All six viewed and approved: drownbell, matron and wraith at 7aa31b6f from PC render c1d1e3e; hullgnaw at
  d8e2c6fc from cloud render 60cbb21; hermit and inquisitor unchanged.) Re-render `battle_boss_intro_drownbell` (and the Hullgnaw, Matron, Hermit, Inquisitor and Wraith intros, which
  may show the same thing), view the renders and approve them.

## Review log
