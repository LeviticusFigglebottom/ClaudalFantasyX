---
id: M2-FP-18
title: Cutscene A/B facial animation at slice quality (blinks, text-driven visemes)
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-08]
milestone: M2
request-from: lead
reviewer: character
---
## Goal
SPEC §10.2 asks the slice for "two cutscenes with facial animation". M2-FP-08 drives Asha's emotion poses (`@face`, line emotions) and an on/off lip-flap that holds one mouth shape (`vis_aa` plus `jaw_open`). Her rig has a full viseme set (`vis_aa/e/i/o/u/mbp/fv/l/st`, `vis_rest`) and lids (`lid_close_L/R`) that nothing uses yet. A face that never blinks and opens to the same shape on every syllable reads as dead at dialogue range. That's the §14 risk.

## Acceptance criteria
- [ ] Blinks: every face rig blinks on a seeded, deterministic timer (interval range, close, hold and open times in sequencer.json), layered over the expression. It also blinks once on each emotion change, which reads as a thought. No blink is drawn while the pose already closes the lids.
- [ ] Text-driven visemes: each mouth opening takes the next syllable's vowel shape from the line's text (a, e, i/y, o, u). Each closing takes a closed-lip shape when the next consonants are m, b or p (and f/v likewise), else rest. The letter → viseme → shape-weight tables live in sequencer.json. A rig without those shapes falls back to the old lip-flap.
- [ ] Rigs exist from the scene's start for every actor with a face-poses row, so they blink before their first line.
- [ ] Tests (a synthetic rig): blink timing, determinism, layering, the viseme sequence for a known line, and the fallback.

## Review log
