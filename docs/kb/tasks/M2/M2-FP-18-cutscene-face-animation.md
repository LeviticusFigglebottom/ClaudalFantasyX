---
id: M2-FP-18
title: Cutscene A/B facial animation at slice quality (blinks, text-driven visemes)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-08]
milestone: M2
request-from: lead
reviewer: character
---
## Goal
SPEC §10.2 asks the slice for "two cutscenes with facial animation". M2-FP-08 drives Asha's emotion poses (`@face`, line emotions) and an on/off lip-flap that holds one mouth shape (`vis_aa` plus `jaw_open`). Her rig has a full viseme set (`vis_aa/e/i/o/u/mbp/fv/l/st`, `vis_rest`) and lids (`lid_close_L/R`) that nothing uses yet. A face that never blinks and opens to the same shape on every syllable reads as dead at dialogue range. That's the §14 risk.

## Acceptance criteria
- [x] Blinks: every face rig blinks on a seeded, deterministic timer (interval range, close, hold and open times in sequencer.json), layered over the expression. It also blinks once on each emotion change, which reads as a thought. No blink is drawn while the pose already closes the lids.
- [x] Text-driven visemes: each mouth opening takes the next syllable's vowel shape from the line's text (a, e, i/y, o, u). Each closing takes a closed-lip shape when the next consonants are m, b or p (and f/v likewise), else rest. The letter → viseme → shape-weight tables live in sequencer.json. A rig without those shapes falls back to the old lip-flap.
- [x] Rigs exist from the scene's start for every actor with a face-poses row, so they blink before their first line.
- [x] Tests (a synthetic rig): blink timing, determinism, layering, the viseme sequence for a known line, and the fallback.

## Notes (m2-slice, 2026-10-24)
- `FaceVisemes` (new) and `CutsceneFace` (`configure_blink`, `blink_now`, `say`; the layers combine by max). The sequencer creates rigs at scene start, seeds each actor's blinks and loads every spoken line's text. Tables: sequencer.json `blink` and `visemes`. Docs: cutscenes.md, "Faces".
- **For Character's review:** the viseme weights. A lavapipe pass on `asha_stage` (Cameras/Face) rendered neutral, mid-blink, `aa`, `mbp` and `o`: the blink lowers the lids and `mbp` closes the lips. `aa` and `o` showed the tongue at first, so they came down to `aa` (0.55, jaw 0.18; the old lip-flap's values) and `o` (0.6, jaw 0.10). Please also judge the blink timing (2.2–5 s; 0.06 s close / 0.03 s hold / 0.11 s open).
- Not here: gaze, and Rhen's and Toma's faces (capsules until M2-CHR-01). B09's S10 layered reaction is Rhen's, so it waits for his rig.
- Tests: `tests/unit/test_cutscene_face_anim.gd` (6), and `test_cutscene_face.gd` unchanged and green. Full suite: 1311 green.

## Review log
