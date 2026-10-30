---
id: M4-A2P-022
title: "Repairing adds: the conduit crawler restores the Lamp Engine's broken parts"
role: combat
status: review
owner_session: act1-chapters
depends_on: [M4-A2P-024]
reviewer: character
milestone: M4
request-from: lead
---
## Goal
`conduit_crawler` repairs a broken part and ignores the party until the engine is struck (act2_roster). Add a `restores_part` skill effect, the crawler's enemy row and AI, and wire the Engine's ring break parts (M3-CRE-623's notes: a charge skill per ring and the ring meshes).

## Acceptance criteria
- [ ] Skill key, validator rule, tests; the Engine's `break_parts` validate.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch11.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30: the engine is in.**
  - **BattleParts** (game/battle/battle_parts.gd):
    - `parts` on an enemy row names charge skills. A weak-point break of one keeps it in `broken_parts`, and every
      gather of that charge is off the AI's menu (choose and the timeline's prediction).
    - `restores_part` on a skill mends the target ally's oldest broken part: the `part_restored` hit field and the
      BattleEngine `part_restored` signal.
    - AI: conditions `ally_part_broken` and `ally_struck` (bools), and the target selector `broken_ally`. Hits from
      the party set `struck`.
  - **Validator:** parts must be the charge of one of the enemy's own skills; `restores_part` is a bool; the new AI
    keys.
  - **Tests:** tests/unit/test_battle_parts.gd (4), plus battle_engine, boss, set_piece and sim, all green.
  - **Still to do (data):**
    - The Lamp Engine's `parts` (a charge per ring) and the `conduit_crawler` row with its `crawler_mend`. This waits
      on battle-presentation's provisional `lamp_engine` row reaching the integration branch (1dbfed6d5); it lands
      with the boss tune.
    - Then re-run `ch11_lamp_engine` with a real role band.
  - **The stage relight and the mend shot:** M3-BPR-441.

- **act1-chapters, 2026-10-30, the data is in on the record `lamp_engine` row (big20):**
  - **The engine:** a weak point (2 quick hits while it gathers, `PART_LAMP_ENGINE_LAMPS`). `parts: ["lamp_flare"]`:
    breaking the gather darkens its lamps and silences Lamp Gather until a crawler mends them.
  - **The crawlers:** `conduit_crawler` (creatures-b's model). Brush Jab, Mend (`restores_part`), Tend. Its AI mends
    first, jabs only once the engine is struck, and tends otherwise. Role answer Ysolde.
  - **The encounter:** `ch11_lamp_engine` is the engine plus two crawlers.
  - **The sim:** `ch11_lamp_engine` now has a real role band.
    - 1,000 seeds: naive 0.2, role 63.2 (Ysolde clears the tenders, then Liss works the engine), smart 100 over 30+
      turns.
    - A one-seed trace showed Liss's quick hits break the lamps mid-gather and a crawler walk over and relight them.
  - **Numbers are low for Ch11** (engine strength 5, HP 2000) because the suites still run on `ch08_seawall`, whose
    casters have 280–340 HP. Re-tune on M4-A2P-019's Ch11 loadout.
  - The stage relight is M3-BPR-441. The ring meshes per part are creatures-b's: `break_parts` keyed `lamp_flare`.

## Review log
