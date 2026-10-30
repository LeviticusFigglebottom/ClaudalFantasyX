---
id: M4-A2P-055
title: "Sefir Aurane at final quality for Act II's close scenes"
role: character
status: review
owner_session: "claude/characters"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Sefir hosts (Ch13), officiates (Ch14) and tempts (Ch16) in close-up. Check the Act I model against those framings (sefir_review.md) and finish what the close scenes need: the officiant's robes, faces for the warm temptation.

## Acceptance criteria
- [x] Review against the Ch13–16 framings; any fixes built; shots viewed.
- [x] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13, Ch16.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 (characters): reviewed at the close framings (Ch14 W04 50 mm, Ch16 C11 50 mm and C12 85 mm).
  - **The officiant:** "pale still-water silk and the gilded bowl-crown" is the Act I model as built, now with
    row 54's pleated gown and fuller front locks. Nothing more is needed for the robes.
  - **The temptation:** `tender` (warm) and `sad` (the sorrow at C17, a trace of smile kept) were too faint at
    85 mm. They are raised in the data, act1_npcs.md §1 and test_sefir, and still symmetric and restrained (his
    tell).
  - **The memory (K06-K07):** young Sefir is the same face (K02: "the player knows the face at once"). For K06 he
    is grief-grey at forty: the `skin_head_grief` material variant (a cool grey drain, a cooled scatter, the face
    drawn), swapped in with CostumeVariant on slot `skin_head` and dropped at K07 when his face goes smooth.
  - **Shots (pending baselines, viewed):** sefir_temptation_tender, sefir_temptation_sad, sefir_memory_grief.

## Review log
