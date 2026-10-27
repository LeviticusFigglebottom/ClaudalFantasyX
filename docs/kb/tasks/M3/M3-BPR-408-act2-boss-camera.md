---
id: M3-BPR-408
title: "Act II bosses' camera language: intros by enemy id; the Lamp Engine's opening, the Avalanche Ram's charge"
role: combat
status: doing
owner_session: claude/battle-presentation
depends_on: [M3-BPR-404]
milestone: M3
request-from: lead
---
## Goal
Creatures has built the Act II bosses (claude/creatures): the Lamp Engine (Ch11, two phases, `opened`) and the
Avalanche Ram (Ch12). Each needs a boss intro and framing for its signature move.

## Done (2026-10-27)
- [x] `boss_intro.by_enemy`: an intro row by the boss's enemy id. Wherever it first appears it gets its intro; an
      encounter's own row wins.
  - The Lamp Engine: `boss_tall`, "The Lamp Engine / It still burns with the bound dead".
  - The Avalanche Ram: `boss`, "Avalanche Ram / Grown monstrous on the drowned light".
  - Both get the M3-BPR-404 model fit and card clearance. Test:
    `test_an_act_two_boss_gets_its_intro_wherever_it_appears`.

## Waiting (no enemies.json rows or skills for them on any branch yet)
- [ ] The Lamp Engine's phase change to `opened`. Planned:
  - a phase beat that pushes the camera in on the core as it opens (BattleBossVfx, as the Drownbell's flood);
  - releasing the core gets a small upward lift (act_outline Ch11: the foreshadowing). Never gold mote-light.
- [ ] The Ram's charge: its telegraph is read as the Breach's is (`camera.pressure` row, keyed by the charged skill),
      and the charge plays a `charge` style, a long low run, with the camera low and side-on.
- [ ] Shots: battle_boss_intro_lamp_engine and battle_boss_intro_ram once their encounters exist (render requests).
- Ask: whoever writes the Act II enemies and encounters (act1-chapters' successor, or m2-slice), name the skill ids
  here, and I'll wire the rows.

## Review log
