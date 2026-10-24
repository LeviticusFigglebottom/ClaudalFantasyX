---
id: M1-QA-08
title: GPU 2x High re-capture of Asha's grief and smile after M1-CHR-11 and M1-RND-21
role: qa
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/qa-08-asha-recheck)"
depends_on: [M1-CHR-11, M1-RND-21]
milestone: M1
request-from: "lead"
reviewer: character
---
## Goal
M1-CHR-11's verdict (asha_review.md §11) is that grief can't pass SPEC §14 until M1-RND-21 lights the mouth interior, and that the GPU re-capture of grief and smile is the judge. No task carried that re-capture, so review-sweep-O filed this one. It is PC GPU work, like M1-QA-05c.

## Acceptance criteria
- [x] After M1-CHR-11 and M1-RND-21 are both on the integration branch, capture `asha_face_neutral`, `asha_face_smile`, `asha_face_grief` and `asha_face_stylized_compare` at 2× High on the GPU, the same way as M1-QA-05c.
- [x] A strict SPEC §14 verdict per shot in `docs/kb/qa/gpu/`, with crops committed, covering the faults still open in M1-CHR-12 (crown, lid band, lip bow, the smile's eyes and skin evenness).
- [x] ADR 0024 check 2 is re-confirmed on the new build (near-black hair with a dark-brown sheen).

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-qa-08-asha.md`; images in `docs/kb/qa/gpu/qa08/` (High and Ultra, 2×).
- **Neutral:** passes.
- **Smile:** passes on shading (the RND-20 striations are gone). At 1× it reads as a lopsided smirk, not the
  ADR 0025 Duchenne smile (CHR-12).
- **Grief:** still fails, on two Character mouth faults: a hard black rim along the open mouth, and peg teeth.
- **Compare:** polish only.
- **CHR-12 items:**
  - The crown and hairline fail.
  - The lid band fails: R:B 3.7–3.8 against the cheek's 2.0–2.5.
  - The lip bow passes at 5×.
  - The smile's eyes fail.
  - Skin evenness passes.
- **ADR 0024 check 2:** re-confirmed. The crown is sRGB (30, 17, 12); the sheen is a dark gold-brown.
- **Teeth `ao_light_affect` 0.2:** tried through write_materials.py; no clear help, so not committed.
- Supersedes the "QA-05d" branch `gpu/qa-05d-asha-recheck`, which had the same captures without the compare shot.

## Review log
- 2026-10-24 review-sweep-P (character): **approve with fixes.** I judged the report's rigour only, not the art.
  - **What is rigorous.** It names both build commits and proves that no asset or shader differs between them. The capture command can be re-run. High and Ultra are both checked. It walks every QA-05c fault and every CHR-12 item, with evidence per row. It separates owner from class, and it declines to commit an unvetted material trial.
  - **Crops checked.** I looked at `crop_mouths.png` and `crop_eyes.png`. They show what the report says: the hard black rim and peg teeth on the grief mouth, and the heavy, spiky lashes.
  - **Three rigour gaps, filed as M1-QA-09** (the next re-run):
    1. The lid and cheek R:B boxes are not given as pixel rectangles, so "3.7–3.8 against 2.0–2.5" can't be reproduced. The report itself says the lid is about 4× darker, and sRGB R:B inflates at low values. Record the boxes, and give linear R:B too.
    2. Fault A, the hard black rim, is classed as an asset fault "probably", but the shadows-off check the report asks for was not run. M1-RND-24 shows the bounce is shadowed by the stage Key, so the class may be wrong.
    3. `crop_eyes.png` shows a soft dark blotch on the nose bridge, between the inner eye corners, in all six frames. The report doesn't mention or classify it.
