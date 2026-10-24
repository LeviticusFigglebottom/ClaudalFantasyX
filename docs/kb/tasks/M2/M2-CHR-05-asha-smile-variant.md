---
id: M2-CHR-05
title: Asha's smile, the M1-CHR-12 §12.4 proposal as a switchable variant with a side-by-side shot
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
reviewer: lead
depends_on: [M1-CHR-12]
milestone: M2
request-from: lead
---
## Goal
asha_review.md §12.4 proposes a less lopsided smile with a slight parting. Build it as data (a variant pose table),
not a replacement, plus a side-by-side shot, so the human can judge it with the ADR 0019 question.

## Acceptance criteria
- [x] The variant is selectable data; the default smile is unchanged.
- [x] A side-by-side shot (current | variant) with a lavapipe baseline.

## Delivery (2026-10-24)
- `asha_face_poses.json` gains `variants.duchenne_open` (smile only: `mouth_smile` [0.67, 0.67], `cheek_raise` 0.60,
  `lid_squint` 0.30, `lip_upper_up` 0.20, `jaw_open` 0.04). `AshaStage.face_variant` / `compare_variant` select it; nothing
  else reads it, so the default smile and every dialogue `@face` are unchanged.
- Shot `asha_smile_variant_compare`: the current smile (left) and the variant (right), new lavapipe baseline. For the
  human, with the ADR 0019 question; adopting it is Art's change to asha.md §6.3 (ADR 0025).

## Review log
