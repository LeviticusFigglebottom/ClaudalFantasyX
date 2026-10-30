---
id: M4-A2P-062
title: "The Wakefin in the dark: a battle lit only by the sea-glow, telegraphs by sound and glow"
role: combat
status: review
owner_session: claude/battle-presentation (session_01UPFyEA8QkJULH74MGgnMvJ; ADR 0205: Act II starts for battle-presentation)
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Fight presentation for Ch15: the barge arena lit by the sea-glow alone, the Wakefin's telegraphs as glow and sound, and the timeline still showing everything (pillar 4).

## Acceptance criteria
- [x] Arena lighting profile, telegraph cues, viewed shots.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch15. M3-BPR-418 already stages the blade-under telegraph.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **battle-presentation, 10-30 (to review: rendering):**
  - Lighting: effects.json `dark_arenas.bridal_barge_night` scales every effect layer's energy by 0.35, except the
    sea-glow's (BattleVfx.dark_scale). A hit's white core was a flash in the night. 8d0fe783.
  - Telegraph: Sound Dive's sea-glow rises at the Wakefin's crest as it dives, beside the timeline's Breach float
    (effects.json `anchor_centred` keeps the crest on the fin; its near face is against the hull). f2bbb673.
    Verified in live play with the charge started.
  - Intro: battle_boss_intro_wakefin looks down over the rail (camera.shots.boss_over_rail). c3e45bb0.
  - Viewed: the intro, all four moves on tools/vfx/boss_camera_sheet (lead, contact and 0.8 s after), and the
    probe. Tests: test_battle_act2_ability_vfx (the dark scale, the crest).
  - **Open for the second box:** the Act II skills' sounds are stand-ins on the Act I hits (battle_sfx.json), so
    the telegraph's sound is audio's to write. The PROVISIONAL rows (M3-BPR-419) and the evasion-up status
    (M3-BPR-428) are the combat seat's.

## Review log
