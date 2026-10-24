---
id: M3-C09-08
title: "Ch9 character art and animation (the gilt line, Ivo, Kerrid soaked, Pell's shell, the Ebbing dance)"
role: character
status: todo
owner_session: ""
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
act1_ch09.md §9 (Character Art). The greybox (M3-C09-02) stages every one of these on capsules:
1. **Asha's gilt line** (N-04's mask layer), first worn at N06 and kept through B08 with spray streaks.
2. **Ivo, dead** (B02): the Ch8 NPC lying in state, face washed and peaceful, the broken tooth showing. Never wounded on screen.
3. **Kerrid, soaked** (from Ch8), through B09. A child's sailcloth-wrapped body as a carried prop for N13, face covered.
4. **Pell's blank name-shell**, featured in B09 (a close insert).
5. **Corrow mourners:** a crowd variation set for kneeling, facing the water.
6. **Animation:**
   - the Ebbing dance: three movements of slow, wide staff sweeps, a hand-keyed hero clip of about 4 minutes in total, looping per movement while the input is held;
   - the strand's kneel.

## Acceptance criteria
- [ ] The items above, with each rig's clips named as the scripts call them. Today those calls do nothing on capsules.
  - Asha: `raise_staff`, `turn_on_raft`, `lower_staff`, `pole_out`, `pole_in`, `stand_gilt`.
  - Tender: `paint_gilt`.
  - Toma: `wipe_face`, `fold_cloth`, `hand_on_spear`.
  - Marra: `hold_hands`.
- [ ] **The held input.** The dance loops per movement while the input is held. With `CutsceneHoldGate` the scene's time stops on release, so the dance clip should idle-breathe rather than freeze. Agree the hook with Cinematics.
- [ ] **The placeholder clips.** `pole_out`, `pole_in` and `stand_gilt` are placeholder clips in the layout's `clip_marks` (a cut onto a mark). Keep or rename them with Cinematics.

## Notes

## Review log
