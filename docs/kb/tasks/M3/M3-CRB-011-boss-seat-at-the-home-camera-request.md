---
id: M3-CRB-011
title: "Request (creatures-b): seat or frame a lone Act I boss so the default battle camera shows all of it"
role: combat
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: creatures-b
---
## Goal
ADR 0041 (pillar 4, tactical clarity). creatures-b rendered each Act I boss encounter on the big14 gate tree
(lead/gate-big14 @ 8707ff90) at the **default battle camera**, no intro, with the chapter's real party (a scratch
fixture modelled on game/battle/scene/shots/boss_intro_shot.gd that skips the intro; never committed). A lone boss
sits on EnemySlots/Slot0 (-2.4, 0, 0.9), close to the camera (BattleCamera at (0.6, 2.8, 8.4)) and near the frame's
left edge:
- **hullgnaw, drownbell, bottle_hermit:** read well (whole silhouette, good scale against the party).
- **cinder_matron (3.6 m):** her hood is clipped by the phase label at top-left.
- **spar_wraith (3.4 m, spars spread wide):** most of the A-frame is out of frame or behind the phase label and
  command menu; the body reads only as a fragment. **The worst read after the Reach.**
- **undertows_reach (a 16 m limb):** the hand fills the left two-thirds of the frame and crowds the camera; the
  party stands under its fingers (also in M3-CRB-009, ask 3).

## Ask
For an encounter whose boss has a choreo.json `boss_intro` row (or a new per-encounter flag), seat the boss on a
boss mark further back and nearer the centre (e.g. about (-1.6, 0, -2.4) for the 3–4 m bosses; further for the
Reach), or apply the intro's `fit` logic (M3-BPR-404: fit the model's bounds in the safe frame, card clear) to the
**home** camera for that encounter. The models cannot do this themselves: moving a model inside its own scene would
pull it off its target ring and the stand-in's VFX anchor heights, and creatures.json `stand_in` has no offset key.
creatures-b re-renders the six encounters at the home camera when it lands.

## Review log
