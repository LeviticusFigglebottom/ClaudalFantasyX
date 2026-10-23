---
id: M1-CHR-07
title: Asha face round 3: smile driver, lip shape, hairline, brows, hair colour
role: character
status: done
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
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve the round as an improvement (the smile driver is fixed); strict SPEC §14 verdict: not a pass.** No blockers for merge: the round's own verdict says the same thing.
  - **Smile driver, verified:**
    - `python3 -m unittest tools.tests.test_asha_face_drive`: 5/5 OK on the committed GLB.
    - The same `TestEmotionsDriveTheFace` run against the CHR-04 GLB and poses (`git show 378fec4:…`) gives **41 failures** (for example, cheek_raise's full-weight peak is 3.61 mm against a 4.0 floor), exactly as the notes claim. The test mirrors `AshaStage._put_weight` (asha_stage.gd:160-169).
    - **In Godot:** I loaded the imported asha.glb headless. The Head's `skin_head` surface has morph normals that survived import: `cheek_raise_L` changes 1,315 normals and `lid_squint_L` 1,388, while `vis_aa` changes 0, as designed.
    - On the baselines, the smile moves 1,509 px in the eye and cheek band against neutral. In a 2× crop the lower-lid lift and the cheek bunching are visible.
  - **Should-fix:**
    - **S1: only the `skin_head` primitive gets morph normals** (asha_glb.py:191, `material="skin_head"`). The `mouth` primitive moves 88 vertices under `mouth_smile` with unchanged normals (Godot surface 1). It is small, but the inner lip corners shade at rest when the smile is on.
    - **S2: diagonal striations at the smiling mouth corner** (asha_face_smile, toward the shadow side). They look like the QA-05 shadow-terminator pattern on the deformed corner. Check with sun shadows off on lavapipe (QA-05 showed lavapipe and GPU agree at scene settings, so a GPU isn't needed for this).
  - **Hairline criterion:** unticked and partial, as recorded. CHR-09 carries it.
- 2026-10-23 lead: closing the round on review-sweep-L approve; the SPEC §14 work continues in M1-CHR-10.
