---
id: M1-CHR-09
title: "Asha round 4: crown hair card layout, face-framing lock, lips, doll-like read"
role: character
status: doing
owner_session: "worktree-agent-aaf1e4bd7d4a529a9 (session_01Bg3iP7cPGyjbX4CyniBahc)"
depends_on: [M1-CHR-07]
milestone: M1
request-from: "lead"
---
## Goal
Close the faults that still fail SPEC §14 at dialogue range in asha_review.md §8.3, plus an honest look at the doll-like read of the face. First find triangle headroom without visible loss (LOD0 is at exactly 63,500).

Out of scope (the PC GPU session owns them): shadow settings, and the cloth, vest and bodice materials, including `write_materials.py`'s cloth entries.

## Acceptance criteria
- [ ] Triangle headroom found without visible loss: hidden or interior geometry decimated, or the costume or body rebalanced. LOD0 stays at or under 63,500
- [ ] The crown no longer reads as a smooth shell: a card-layout pass with layered cards, breakup, strand clumps and flyaways
- [ ] The face-framing lock reads as loose hair, not a dark streak
- [ ] The lips are slightly fuller, and the bow's shoulders don't wobble
- [ ] The face no longer reads doll-like (eye white or iris scale, skin subsurface warmth), judged honestly from the asha_face_* shots
- [ ] Material changes go only through `assets_src/characters/asha/write_materials.py`
- [ ] `verify_blender_builds.py --job asha` reports all identical; every file under 5 MB
- [ ] Only the asha_* baselines that intentionally change are re-approved, each looked at; the §14 review is re-run strictly in asha_review.md §9

## Notes

## Review log
