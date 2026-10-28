---
id: M3-BPR-408
title: "Act II bosses' camera language: intros by enemy id; the Lamp Engine's opening, the Avalanche Ram's charge"
role: combat
status: blocked
blocked-by: ADR 0041
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

- [x] **The Lamp Engine's opening** (choreo.json `bosses.lamp_engine.phases.opened`, BattleBossChoreo `phases`):
      on the phase change to `opened`, once the action playing is done, the boss's root rises a little (its core
      lifting as the housing parts) and the party steadies in turn (defend, 0.1 s apart). The creature plays its own
      `phase_change` clip under it. Never gold mote-light.
- [x] **The Avalanche Ram's charge:**
  - the camera rides low and side-on on the Ram's actions (`camera.enemy_by_actor.avalanche_ram` = `charge_side`),
    falling back to the default if that shot fails the safe frame;
  - any charge it gathers (`bosses.avalanche_ram.charge_skill: "*"`) paws the ground each turn, and the camera
    closes in a step a turn (`camera.pressure.by_enemy`).
  - Its own long, low `charge` run style is ready, but waits on a sound row in audio's choreo_sfx.json (request
    **M3-BPR-410**). `style_by_actor` is in place to turn it on. Until then it plays the melee.
- [x] **The Ch10–11 regulars:** no bespoke framing. The model fit, the footprint spacing (402) and the line-up
      spread (403) all work from their real models.
- [x] Validator (tools/validate_choreo.py: `"*"` charges, `phases`, `style_by_actor`, `enemy_by_actor`) and tests
      (tests/unit/test_battle_act2_bosses.gd 3/0, tools test_choreo_validate 21/0).
- [ ] Shots once their encounters exist: battle_boss_intro_lamp_engine, battle_boss_intro_ram, a charge
      freeze-frame. Then render requests.
- Ask: whoever writes the Act II enemies and encounters, keep the ids `lamp_engine` and `avalanche_ram` (the
  creatures' scenes), and the phase id `opened`.

## Review log
