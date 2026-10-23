---
id: M1-NAR-11
title: Story consistency and residual echoes after the Kerrid re-staging (review-sweep-F)
role: narrative
status: review
reviewer: cinematics
owner_session: "worktree-agent-a34ff8effe727a250"
depends_on: [M1-NAR-09]
milestone: M1
request-from: "cinematics"
---
## Goal
The review-sweep-F entries on M1-NAR-09 and M1-NAR-08.

## Acceptance criteria
- [x] Kerrid is not a famous Order hero or legend: captain of Corrow's conscripted fisher watch, no "Hero of Corrow" title (consistent with ADR 0017's no-legend rule)
- [x] Lead decision: **Dace is no longer Imra's guardian** (the hero's father guarding the heroine's sacrificed parent is the largest remaining echo and SPEC does not require it); re-stage their bond and update every doc that depends on it
- [x] Consistency gaps: Toma's 1001 timeline against knowing Kerrid only "by reputation"; Toma's oath age (nine or fifteen); who can recognise Kerrid's face (Sefir in Ch6, the Corrow wall comrades); why Kerrid stays with the party after Ch8; the colour of the rope-burn glow (gold means released, cyan means held)
- [x] Echo rows (in a new ADR at the next free number, or appended to ADR 0020) for: Kerrid avoiding the Ebbing as the tell that he is dead; Sefir and Kesh as the founding couple; Rhen recognising the temple song in Ch3. Each is resolved or accepted with a reason
- [x] palette.json night sea-glow minimum gets an explicit Ending exception (0.07/0.06), validated
- [x] Liss's line-marks on one arm consistently; nits: "the place he once sent Imra"; decisions_log still says 0020 is proposed; dialogue_format.md Ch14 should be Ch15
- [x] All .dlg compile; validators pass

## Notes
- 2026-10-23 narrative (worktree-agent-a34ff8effe727a250): everything is recorded in [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (proposed) and decisions_log N-23. Append notes are on ADRs 0016, 0017 and 0020, and the glossary is appended.
  - **Dace and Imra:** strangers until the Corrow storm of 1001. Dace was Kerrid's hired diver, re-seating the stair-foot rings. Imra was there for the Coilspire trial, and Kerrid walked her to the temple each day. They never met. In the storm she went down the Fisher Stair into the sea for him, a diver she'd never met, and Kerrid died holding the stair for both. She gave Dace her comb to carry home to Asha (the new source of Asha's Ch2 stillness at the lantern). He began the hull at Hollowmere and sailed into the storm after her, to repay the debt ("first down the stair"). He never walked her road. Rejected: "walked with her unasked" (same shape) and "the boatman who refused" (no reason for the ask; a bystander).
  - **Kerrid:** captain of Corrow's conscripted fisher stair-watch, no Order rank, no "Hero of Corrow". The stair-law and "Stair's clear." are the watch's. His cord is the watch's, in faded watch-red.
  - **Consistency:**
    - Toma was at Ansedra 997–1002 and on the Corrow wall 1002–1009, and was sworn at Asha's naming at fifteen.
    - Only Corrow's old watch knows Kerrid's face. Sefir sees what he is, not who, and lets him be in Ansedra. Kerrid sits nights at the outer moorings and is last onto Merel's barge.
    - The Ch8 fishwife beat is staged storm-dark, with Toma out of earshot.
    - He stays after Ch8 because "Somebody's still below." (Ch9 dawn).
    - The rope-burns leak `glimmer_held` from Ch10 on, never in Ch5 or Ch8, and lerp to lift at H09.
  - **Echo rows:**
    - The Ebbing: re-staged with a practical cause (he brings up the drowned at the stair foot), and the tell is dropped.
    - Sefir and Kesh: accepted with reasons (Lead to sign off).
    - Ch3 recognition: accepted with reason.
  - **Palette:** `sea_glow_rule` names the exception, and structured `sea_glow_night_exceptions` is checked by the new `tools/tests/test_palette_rules.py` (validate_data has no palette checks).
  - **Liss:** line-marks on the right arm.
  - **Nits:** fixed. The .dlg changes are comment-only, with the same line count, so the compiled JSON is unchanged.
  - **Not done:** SPEC.md:522 cites ADR 0021, which is reserved for the MPFB2 ADR (Lead/character). No edit.

## Review log
