---
id: M3-CHR-102
title: "Asha's kneeling skirt balloons over Rhen and passes through him (Cutscene A; PC GPU QA row 31)"
role: character
status: todo
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
PC GPU QA (`docs/kb/qa/act1_gpu_qa.md` on `origin/gpu/act1-qa-2`), row 31, Ch2 beach on the Lead's re-stage
(lead/gate-ft-beach @ 93d0741e, newgame_13–17): "Asha's skirt balloons into a large blue mass over Rhen's chest and
passes through him while she kneels."

The staging is the human's playtest fix (the Lead's), and the PC has confirmed both faces read on big15, so the marks
stay:
- Asha kneels at (-4.75, 0.2, 8.2), turned 310°, at Rhen's left side, leaning over him;
- Rhen lies at `Spawns/Beach` (-4, 0.18, 8).

The skirt is the baked helper-bone solve (`game/data/characters/helper_bones.json` "skirt", M2-CHR-522). Kneeling
pools the floor-length cloth, and the lowest bones take `1 + gather_flare * (1 - gather)` across. That flare reads as
a balloon at this distance, and the solve clears only her own legs, never another body.

## Ask (rig side, Asha's `kneel_over_rhen`, and any kneel)
- [ ] Keep the pooled cloth close: lower the flare for a kneel, or let the hem fold back under her rather than out
      over what is in front of her knees.
- [ ] If a per-clip override is the cleaner fix, a `kneel_over_rhen` row with a smaller flare is fine.
- [ ] View `slice_beach_h05_asha` and `slice_beach_h06_toma` (they hold lines 002 and 017 on the kneel) and tell
      slice-polish. If the cloth can't clear him at these marks, say by how much, and slice-polish moves her mark
      that far (the faces must stay in H05 and H06).

## Review log
