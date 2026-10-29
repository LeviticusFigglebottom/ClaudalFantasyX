---
id: M3-CHR-543
title: "Request: stage Asha's beach kneel beside Rhen, not over him (act1_gpu_qa row 31)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-CHR-542]
milestone: M3
request-from: character
reviewer: character
---
## Goal
(For the m2-slice session, which owns the Ch2 Cutscene A stage.)
Act I GPU QA row 31 (big14 playtest on lead/gate-ft-beach, newgame_13–17): "Asha's skirt balloons into a large blue mass
over Rhen's chest and passes through him while she kneels."

The cause is the staging. `Actors/asha` in the Ch2 Cutscene A stage is posed kneeling at (0.2, −0.01, 8.0), facing
Rhen 1.2 m away, and Rhen lies with his head and chest toward her. Asha's skirt covers her thighs, so in the kneel it
reaches **0.67 m forward of her root**: her knees are at 0.38 m and the floor-length cloth drapes out past them. Across
her it spreads about **0.85 m to either side**. Rhen's head and chest are inside that, and the skirt is solved against
Asha's own legs only, so it passes through him. No skirt setting fixes this: a real kneeling skirt would lie on him too.

## Acceptance criteria
- [ ] Asha kneels **at Rhen's side**, her forward axis across his body (not along it, toward his head), with every part of
      Rhen at least **0.75 m** in front of her root and outside her 0.85 m side spread. Or Rhen lies so that this holds.
- [ ] H05 (Rhen's POV, Asha on the right third) and H06 (the side-on two-shot) still frame both faces.
- [ ] Re-capture newgame_13–17 (or the H05/H06 shots) and view them: the skirt lies on the sand beside him.

## Notes
- Filed 2026-10-28 by the characters track. The skirt itself was reworked since big14: the pooled hem drapes and folds
  (M2-CHR-522 drape @ 8e7d5f67, M2-CHR-542 / ADR 0140 @ 67a1b2a0). Merge those first, then re-stage.
- The measurement is hero_clips' posed cloth for `kneel_over_rhen` at its last frame, in Asha's skeleton frame.

## Review log
