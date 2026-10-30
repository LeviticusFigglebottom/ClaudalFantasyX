---
id: M4-A2P-061
title: "Nhoa, Hesk, Ethren and Kesh: summon cinematics (full and short) and Swell finishers"
role: combat
status: doing
owner_session: claude/battle-presentation (session_01UPFyEA8QkJULH74MGgnMvJ; ADR 0205: Act II per track)
depends_on: [M4-A2P-024]
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Each Vowbound's summon cinematic (full the first time, short after, the skip toggle) and Swell finisher: Farewell-Tide (the only finisher whose motes go up), Pass-Cord, Still Water, The Seven.

## Acceptance criteria
- [ ] Cinematics and finishers in data; hitch budget; shots viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.4.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **battle-presentation, 10-30:** the battle VFX and the four finishers are in tools/vfx/gen_act2_ability_vfx.py
  (VOWBOUND, 97e22896). Each is written once its skill row lands; the rows are on big21 (act1-chapters'
  vowbound.json). Checked there: all 19 written, validate_data clean.
  - **Next, once big21 is in the integration branch:** merge it in, regenerate, view each on a Vowbound sheet, then
    the summon cinematics (full and short, the skip toggle) on BattleVowbound's call camera.
  - Nhoa's ice is drawn as the deep's cold (deep teal and navy, no crystals: ADR 0204 for Ch12 to Ch15).
    Farewell-Tide's rising motes are released glimmer (rule 1), as act2_plan 4.4 asks. Both are for rendering's
    review.

## Review log
