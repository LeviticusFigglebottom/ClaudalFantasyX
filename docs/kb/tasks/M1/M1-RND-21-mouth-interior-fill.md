---
id: M1-RND-21
title: Mouth-interior fill light and cavity shading (grief goes near-black)
role: rendering
status: review
reviewer: character
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU)"
depends_on: [M1-QA-05]
milestone: M1
request-from: "character"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [x] The mouth interior in grief and open-mouth visemes is not near-black: a cavity fill term or a bounce approximation in the skin and mouth shading, tiered
- [x] Applies to every hero, not only Asha; documented in character_shading.md
- [~] Measured on the GPU; lavapipe shots re-approved by the Lead (measured; `asha_face_grief` awaits re-approval)

## Notes (PC GPU session, branch `gpu/rnd-21-mouth-fill`)
Report: `docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md`. Design: character_shading.md, "Mouth interior".
- **New family:** `mouth` (`character_mouth{,_medium,_low}.gdshader`), with an unshadowed cavity bounce per light.
  The bounce fades with the baked occlusion and with the light behind the face, and is on every tier.
- **Asha:** teeth, tongue and mouth moved to it through `write_materials.py`, with the same values.
- **Interior luminance** (grief, GPU): the median rises 0.0121 → 0.0174 at High and 0.0121 → 0.0180 at Low. The share
  below 0.01 falls 0.30 → 0.16 at High and 0.29 → 0.14 at Low.
- **Drift:** `asha_face_grief` 0.0023 on the GPU; the other asha_* shots are unchanged (0.0000).
- **Not addressed:** the teeth still read khaki (their albedo: fault 3, M1-CHR-11).
- **Tried and dropped:** a stage fill light. It lights the whole face (too global), and a stage light doesn't reach
  zones.

## Review log
