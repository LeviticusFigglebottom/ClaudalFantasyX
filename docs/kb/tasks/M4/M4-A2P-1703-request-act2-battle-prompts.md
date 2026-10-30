---
id: M4-A2P-1703
title: "Request (ui-menus): wire the Act II battle prompts (rooted, drain, Listen and the bosses') into encounters.json"
role: combat
status: todo
owner_session: ""
depends_on: []
reviewer: ui
milestone: M4
request-from: ui
---
## Goal
The new statuses and the Act II fights are taught by battle prompts (act2-plan's docs/kb/plan/act2/ui/tutorials.md,
"Battle prompts"). The text is in (TUT_CH10_ROOTED, TUT_CH10_DRAIN, TUT_CH10_LISTEN in ch10.csv; TUT_DROWNER_ROOTS;
TUT_LAMP_ENGINE_CRAWLERS in ch11.csv; the rest as act2-plan writes them). No encounter names them yet. On the UI side
nothing is needed: BattleBossHud puts an encounter's `prompt_key` (or `turn_prompt_hero` with `turn_prompt_key`) on
the help line once, when the next command menu opens, as TUT_CH01_COMMANDS does in Ch1's first fight.

## Ask
Set, in game/data/battle/encounters.json:
- `ch10_fen_roots`: `prompt_key` TUT_CH10_ROOTED.
- `ch10_fen_leeches`: `prompt_key` TUT_CH10_DRAIN.
- `ch10_fen_archers` (Pell's first fight): `turn_prompt_hero` pell, `turn_prompt_key` TUT_CH10_LISTEN.
- `mangrove_drowner`: `prompt_key` TUT_DROWNER_ROOTS.
- `lamp_engine`: `prompt_key` TUT_LAMP_ENGINE_CRAWLERS.
- The later rows in the tutorials.md table, as their encounters land.

## Acceptance criteria
- [ ] Each row above names its key; `validate_data` passes. ui-menus checks the help line at 100% and 130% once they
      are in (M4-A2P-1702's follow-up).

## Review log
