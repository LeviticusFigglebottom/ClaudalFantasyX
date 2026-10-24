---
id: M1-QA-08
title: GPU 2x High re-capture of Asha's grief and smile after M1-CHR-11 and M1-RND-21
role: qa
status: review
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
