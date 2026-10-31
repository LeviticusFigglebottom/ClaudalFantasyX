---
id: M5-A3P-1852
title: "tide_matron (Ch18 optional revisit boss): the Cinder Matron's rig as a coral kiln"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
reviewer: combat
depends_on: [M3-CRE-649]
milestone: M5
---
## Goal
act3_roster.md Ch18: a variant of the Cinder Matron's rig for the reef, a coral kiln with no fire, her heart bound in
salt-glass (the bank-not-break lesson, mastered). Optional content: after the Cage (roster order of work, 5).

## Progress
- 2026-10-30: the design sheet, docs/kb/art/creatures/act3/tide_matron.md (her sister's rig with the reef, the shut
  firebox, the fight's proposal, clips, open questions). Next: Combat's answer on the fight, then the build (a `tide`
  flag in build_cinder_matron.py writing a second GLB).
- 2026-10-30: the build. `build_cinder_matron.py --tide` writes assets/creatures/tide_matron/tide_matron.glb from her
  sister's rig and mesh (the Cinder GLB rebuilds byte-identical; both builds reproduce): the frame recoloured to
  verdigris over brass, every lit vertex (the firebox, the mouth grille, the ladle's slag, the seams) turned to dark
  stone grown over (no emission but the heart and the sight-glass), the slag `Crust` rebuilt as a coral `Reef`, and a
  `Kelp` mesh (9 two-bone ribbons round the lowest belly course that sway through idle and ready; 3 rigid ones off
  the ladle). Clips: her sister's ×1.25, renamed `bank_the_tide`, `tide_pour`, `regrow_gather`, `regrow`; `ko` is
  `bank` (2.8 s, the head bowing last, held at rest) and `phase_change` is the Calm (she draws in and bows; no burst).
  Materials assets_src/creatures/tide_matron/materials.json (metal, reef, heart, leather, wound, kelp); the Blender job
  `creature_tide_matron`; game/creatures/tide_matron/tide_matron_battle.tscn; the creatures.json row (`ko: bank`,
  contacts ×1.25; no `clip_by_skill` or phases until Combat writes her skills and enemy row). Test
  tools/tests/test_tide_matron.py. tools/creatures/clip_sheet.gd now plays a row's own `ko` clip.
  Departures from the sheet (amended): no `ReefGrow` bone (one rig: the shelf growing on `bank_the_tide` is an effect
  at vfx_phase, battle presentation's); the weak point stays her sister's sight-glass. For Combat (review): the skills
  for `attack`, `tide_pour`, `bank_the_tide`, `regrow_gather`, `regrow` and the Calm phase id.

## Review log
