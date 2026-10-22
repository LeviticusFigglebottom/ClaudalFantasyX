---
id: M1-UI-02
title: "Battle HUD follow-ups: swap preview, fail copy, Provoke, auto-turns, status display, fixture captures, accessibility settings"
role: ui
status: doing
owner_session: worktree-agent-a442bf3baa0b90315
reviewer: lead
depends_on: [M1-CMB-01, M1-CMB-02]
milestone: M1
request-from: ""
---
## Goal
Close the M1-CMB-01 review follow-ups and the UI-01 lead-review follow-ups on the battle HUD (SPEC §1 pillar 4, §6.1, §6.11, §7.6).

## Acceptance criteria
- [ ] Swap-out state previews the timeline with `BattleEngine.preview_swap(out, in)`; chips move while hovering a reserve member
- [ ] The help line shows a localized message for every engine failure reason (no raw ids); keys appended to `game/data/loc/strings.csv`
- [ ] The target cursor respects Provoke (`forced_target()`), with a clear marker on the provoker
- [ ] Berserk and Confuse party turns get their own labels and pacing (auto-run turns, not enemy actions)
- [ ] Doom countdown on timeline chips and the party panel; Reflect bounce indicator and float text; Petrify state (stone-tinted greyed portrait, off the timeline); Zombie/Regen inversion feedback; every new status icon is a colorblind-safe vector shape
- [ ] Victory/defeat/HUD captures render from deterministic fixture UI state, independent of `enemies.json` tuning; baselines re-approved after visual check; one new statuses shot (Doom, Reflect, Petrify, Provoke)
- [ ] Data-driven accessibility settings layer (reduced motion, HUD text scale, colorblind palette) with tests
- [ ] A more prominent current-actor marker (UI-01 lead review)

## Notes

## Review log
