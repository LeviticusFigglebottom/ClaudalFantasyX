---
id: M1-CHR-07
title: Asha face round 3: smile driver, lip shape, hairline, brows, hair colour
role: character
status: review
reviewer: rendering
owner_session: "worktree-agent-a092b4032f6c64db4 (session_01Bg3iP7cPGyjbX4CyniBahc)"
depends_on: [M1-CHR-04]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [x] Smile reads: the cheek raise 0.45 and lid squint 0.25 of asha.md:158 visibly drive in asha_face_smile (find the data or driver gap: shape-key names, the emotion mapping, or the weights); same audit for grief and every emotion tag
- [x] Lips: a defined cupid's bow and vermilion border; no dark slit in the smile
- [ ] Hairline: no helmet edge; no stray flat cards at the temples; hair reads black per asha.md:121 (check albedo and shader tint with Rendering). **Partial:** the hard edge, the comb card, the temple streak and the colour are fixed; the crown still reads as a smooth shell and the framing lock as a streak (asha_review.md §8.3)
- [x] Brows: hair strokes, not solid bars
- [x] Blender rebuild gate byte-identical; GLB under 5 MB; §14 dialogue-range review re-run honestly, side by side with CHR-04; baselines re-approved with reasons

## Notes

### Character, worktree `worktree-agent-a092b4032f6c64db4` (2026-10-23)

**Root cause of the smile gap.** The data and the wiring were correct: the poses JSON matches asha.md §6.3, AshaStage resolves L/R, and all 40 names exist. The gap had two parts:
1. CHR-03 exported the shapes **without morph-target normals**, so skin-bunching shapes shaded as at rest.
2. `cheek_raise` (3.6 mm peak) and `lid_squint` (2.6 mm lid lift) were too weak: 1.6 mm and 0.65 mm at the smile's weights.

`jaw_clench` was also dead (0.57 mm peak). The fix:
- `asha_glb.add_morph_normals` adds sparse normals on the 30 expression shapes (+0.53 MB).
- The shapes go to FACS scale, with the weights unchanged.
- The smile now lifts the lower lid 3.28 mm (was 1.63) and the cheek 2.98 mm (was 1.45).

The new `tools/tests/test_asha_face_drive.py` audits every tag. It fails 41 checks on the CHR-04 GLB and passes on this one.

**Also done:**
- The vermilion outline is drawn in the sealed-contact frame, with a bow, a border, a white roll and a philtrum.
- Smile, frown and `lip_upper_up` are sealed at the contact: parting ≤ 0.13 mm, no slit.
- Brows are stroke columns per layer; the arch step is fixed; the lower lashes are sparse.
- Hair: temple hairline, softer underpaint edge, seated comb, thinner framing lock.
- Hair lobe: exponent 400, jitter 0.25, indirect 0.1. The albedo is already #201A16; the gold was the primary lobe.

Details are in asha_review.md §8; there is a note on ADR 0021.

**For the reviewer (Rendering):**
- Confirm the hair lobe values on a GPU. They depart from asha.md §5's exponent 120.
- Check that the morph normals shade correctly on real hardware (GPU 2× captures).

**Not touched:** shadow settings, the banding, and the cloth, vest and bodice materials (`write_materials.py`'s cloth row came in by merge only).

**Verdict:** improved, smile gap closed; **not a clean §14 pass as built** (the crown shell, the framing lock, thin lips). Remaining work: a hair card-layout pass, which needs triangle headroom (LOD0 is at 63,500).

## Review log
