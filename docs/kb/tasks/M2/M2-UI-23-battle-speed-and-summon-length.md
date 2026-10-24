---
id: M2-UI-23
title: Battle speed and Vowbound call cinematic length settings
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 6: two new settings. Battle speed scales how fast battle presentation plays without changing the battle. Summon cinematic length picks how much of a Vowbound's call cinematic plays (SPEC §6.3).

## Acceptance criteria
- [x] `battle_speed` row (Slower 0.75 / Normal 1.0 / Faster 1.5 / Fastest 2.0; default Normal), with the same id and values as BattleChoreo's speed (M2-BPR-03). It scales the controller's pacing waits, damage numbers and float words, the camera shake and the hit recoil through one factor (`UiSettings.battle_speed()`, `BattleHud.battle_speed()`).
- [x] It never changes engine outcomes or the rng: the same inputs give the same actors and HP at 0.75 and 2.0 (test). The Swell input windows (`SwellRingClock`, `SwellInput`) stay real time. Instant pacing stays instant.
- [x] `summon_cinematic` row (Full / Short / Off; default Short, SPEC §6.3), with `UiSettings.summon_cinematic_cut(first_call)` returning full, short (skip the middle beats) or none (straight to the effect).
- [x] Both rows are on the Accessibility page, with loc keys, and are saved in `settings.cfg`. Tests are in `tests/unit/test_accessibility_battle_speed.gd`, the `settings_accessibility` shot is re-approved, and the docs are in `docs/kb/tech/ui.md` § Battle speed and the Vowbound call cinematic.

## Notes
- **No call cinematic exists yet** (claude/ui or claude/battle-presentation): a call re-seats the stage at once. **Who must read the setting:** battle presentation (role combat, the battle-presentation track), in M2-BPR-04's "Vowbound call" and the C10 Ilun cinematic. It asks `UiSettings.shared().summon_cinematic_cut(first_call)` and keeps the per-Vowbound first-call record. Request: [M2-BPR-07](M2-BPR-07-summon-cinematic-length.md).
- **Merge with claude/battle-presentation:** that branch (M2-BPR-03) already adds `battle_speed` and `battle_animations` rows to `accessibility.json` and the six `SET_BATTLE_SPEED*` loc rows. This branch adds the same `battle_speed` row and the same six loc rows, with identical text. When the branches meet, keep one copy of each: drop the duplicate loc rows, or validate_data and the CSV import see the key twice. Keep both their `battle_animations` row and this `summon_cinematic` row. Their `test_ui_settings` id list needs the union too.
- BattleChoreo's `hold_after(base)` takes `max(base, remaining / speed)`. `base` comes from `_pace`, which is now divided by the speed too, so at Fastest both shrink together.

## Review log
