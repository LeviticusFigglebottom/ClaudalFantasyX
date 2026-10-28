---
id: M3-CHR-525
title: "Kerrid's battle strikes read as two-handed chops (seen at battle distance)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-505]
milestone: M3
request-from: ""
reviewer: rendering
---
## Goal
ADR 0041 self-render, `kerrid_battle_attack`: at contact the cleaver points sideways at shoulder height like a spear,
with the left hand raised and open. kerrid.md §10.3's haul-chop (both hands on the haft: lifted over the right shoulder,
held, then chopped down and forward to knee height) does not read. The keys were authored on the old grip
(`K_GRIP_STRIKE`) without being seen. The battle idle's two-handed stance (`K_GRIP`, `kerrid_battle_clips.tres`) reads
well and stays.

## Acceptance criteria
- [ ] attack, finisher, ready and defend are re-authored from the stance with both hands on the haft. The blade reads
      as a chop at contact; the contract tests and the rig probe pass.
- [ ] Self-rendered and viewed: kerrid_battle_idle, kerrid_battle_attack, and a finisher frame.

## Review log
