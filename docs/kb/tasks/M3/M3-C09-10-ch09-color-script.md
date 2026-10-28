---
id: M3-C09-10
title: "Ch9 color script: the ch09 night, the ch09_dawn frame and the act-break vigil"
role: rendering
status: review
reviewer: art
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; rendering's zone looks, Lead 2026-10-28)"
depends_on: [M3-C09-02]
milestone: M3
request-from: cinematics
---
## Goal
act1_ch09.md §9 (Art, color script):
1. **A new frame, `ch09_dawn`** (B09, 05:50): a washed, low gold dawn after the storm, the **last warm light of Act I** before Act II's overcast (SPEC §7.2). Low sun from the east, a wet laterite road, and the sea to the south still faintly glowing in the dawn shadow.
2. **The act-break vigil (P02)** reuses `prologue`, a few minutes deeper into the dusk (the sun about 1° lower), with the lantern flame's practical at about 0.85×. The motes in this frame are the Prologue's own, so the exception to rule 1 is the Prologue's light, not Ch9's.
3. **The gilt line.** Confirm its first appearance (N06) against N-04 and Asha's mask layer.

## Acceptance criteria
- [x] The `ch09` night, `ch09_dawn` and the deeper `prologue` vigil frames in the color script, with grades for the grade ids (M3-C09-09).
- [ ] **The greybox's light.** The zone `ch09/corrow_night` lights the night as the layout's sun and environment, and the dawn as a `variants` row. The vigil stand-in (x 300 in the same zone) is lit by whatever variant is active, which is dawn, not dusk. Give the vigil its own light when its staging is settled (M3-C09-04).

## Notes
- **env-art-b, 2026-10-28:**
  - The colour script has the `ch09_dawn` and act-break vigil frames, appended to the Ch9 block. The `ch09` night row was already there; the zone's grade carries the lift from M3-ENV-1309.
  - The dawn variant now loads its own grade, `corrow_ch09_dawn_environment.tres`: a clearing pale zenith, a gold east, broken cloud lit from beneath, and warm ambient at exposure 0.9. Before, it borrowed the Ch8 storm grade. The grade is written by `tools/act1/ch09_corrow_night.py`.
  - Viewed `ch09_corrow_road`: a washed low-gold dawn on the wet road.
  - The vigil's own light waits on M3-C09-04's staging, as this task says, so that criterion stays open.
  - **The gilt line (item 3)** is a story and character check (N06 against N-04 and Asha's mask layer). It belongs to cinematics and characters, and is not confirmed here.

## Review log
