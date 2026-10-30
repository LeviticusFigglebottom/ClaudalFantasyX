---
id: M3-HER-1134
title: "Request (creatures): the Cinder Matron's two cutscene clips, bank and unfold"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
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

## Done (creatures-b, 2026-10-30)
- The Matron is already her creature on the Ashcrown stage: `ashcrown_layout.json` casts `matron` as
  `creature:cinder_matron` (the M3-HER-1143 fix).
- The two cues now name her own clips, through the sequencer's `clip_stand_ins` (game/data/cutscene/sequencer.json,
  two keys appended): `matron/bank` plays `bank_the_fire`, the Bank the Fire skill's clip (she banks the firebox; the
  cue's `@vfx glimmer_bound at=matron_heart` lands on it). `matron/unfold` plays `intro`: from the slumped rest bow,
  the anvil's ring jolts through her plates, she wakes and raises the ladle and tongs ("When the anvil rings, the
  Matron wakes").
- Reviewer: cinematics. Swap either clip in sequencer.json if the scene wants another; no model change needed.

## Review log
