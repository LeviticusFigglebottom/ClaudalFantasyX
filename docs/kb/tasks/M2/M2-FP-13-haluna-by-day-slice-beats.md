---
id: M2-FP-13
title: Haluna by day at slice quality (B02 Neme's table, B03's four overheard fragments, B05 Low tide)
role: cinematics
status: doing
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-04, M2-FP-09]
milestone: M2
request-from: lead
reviewer: narrative
---
## Goal
Queue item 4 of the m2-slice track. The playable Haluna has Cutscene A, three of the four "Cantor" fragments as interact-only barks, the tideline battle, the save shrine and the causeway trigger. The vertical-slice beat sheet (docs/kb/story/beats/vertical_slice.md §1–2) asks for more: Neme's table (B02) after the beach, the four fragments *overheard by walking past* (B03), and the low-tide beat at the causeway head (B05) before the pilgrimage starts. Stage those in engine.

## Acceptance criteria
- [ ] B03 fragment 4: the lane child's skipping rhyme (`ch02_bark_lane`, a new `child` speaker) and a child stand-in in the lane.
- [ ] All four fragments play once each when Rhen walks past (TOUCH triggers after `ch02_met_asha`). They don't freeze the player, they advance by themselves, and they never block the battle or causeway triggers. Talking to the villager still plays the bark.
- [ ] B02: after Cutscene A, Rhen wakes at Neme's (the Village spawn) and `ch02_nemes_table` plays in engine (a new `neme` speaker, about 40 words, starting black).
- [ ] B05: the causeway-head trigger plays `ch02_low_tide` (Toma and Asha, about 40 words) in engine before handing off to Cutscene B.
- [ ] Data-driven (first_playable.json), loc through `.dlg` `#line:` tags, and tests; the whole-thread test still passes.

## Not in this task (filed separately)
B04 (Pila's granddaughter, optional), B11 (the dock at night), the inn and the equipment shop, the lintel-gull look-at (H03), and the camera insert of Asha's packed bag in B02.

## Review log
