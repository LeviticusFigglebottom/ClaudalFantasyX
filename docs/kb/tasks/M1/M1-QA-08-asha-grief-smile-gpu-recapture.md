---
id: M1-QA-08
title: GPU 2x High re-capture of Asha's grief and smile after M1-CHR-11 and M1-RND-21
role: qa
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/qa-08-asha-recheck)"
depends_on: [M1-CHR-11, M1-RND-21]
milestone: M1
request-from: "lead"
reviewer: character
---
## Goal
M1-CHR-11's verdict (asha_review.md §11) is that grief can't pass SPEC §14 until M1-RND-21 lights the mouth interior, and that the GPU re-capture of grief and smile is the judge. No task carried that re-capture, so review-sweep-O filed this one. It is PC GPU work, like M1-QA-05c.

## Acceptance criteria
- [ ] After M1-CHR-11 and M1-RND-21 are both on the integration branch, capture `asha_face_neutral`, `asha_face_smile`, `asha_face_grief` and `asha_face_stylized_compare` at 2× High on the GPU, the same way as M1-QA-05c.
- [ ] A strict SPEC §14 verdict per shot in `docs/kb/qa/gpu/`, with crops committed, covering the faults still open in M1-CHR-12 (crown, lid band, lip bow, the smile's eyes and skin evenness).
- [ ] ADR 0024 check 2 is re-confirmed on the new build (near-black hair with a dark-brown sheen).

## Review log
