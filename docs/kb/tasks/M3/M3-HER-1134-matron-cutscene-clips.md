---
id: M3-HER-1134
title: "Request (creatures): the Cinder Matron's two cutscene clips, bank and unfold"
role: character
status: todo
owner_session: ""
reviewer: cinematics
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The Act I hero-motion audit (docs/kb/qa/act1_hero_motion_audit.md, M3-HER-1132) finds two cues on the Cinder Matron
that do nothing: `@anim matron bank` (ch05_kahre) and `@anim matron unfold` (ch05_matron_wakes). On those stages
she is still a capsule. Her creature actor exists for battle, so either the stage uses her creature scene and gains the
clips, or the scripts call clips she already has.

## Acceptance criteria
- [ ] On ch05_kahre and ch05_matron_wakes the Matron is her creature, not a capsule, and `bank` and `unfold` play (or
      the scripts name existing clips).
- [ ] The audit reports them as real.

## Review log
