---
id: M5-A3P-1853
title: "old_shoal (the roster's old_leviathan; Ch18 secret superboss)"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
reviewer: combat
depends_on: [M3-CRE-649]
milestone: M5
---
## Goal
act3_roster.md Ch18: a whale-sized sea turtle older than the Calm, its shell a reef, asleep on a secret shoal; the
secret-coordinates superboss (a long, patient fight). Optional content: last (roster order of work, 5).

## Progress
- 2026-10-30: the design sheet, docs/kb/art/creatures/act3/old_shoal.md. It is renamed from `old_leviathan` because
  "Leviathan" is a recurring summon name in the series we may not echo (CLAUDE.md §2); LEAD-ASK in creatures-b.md.
  Next: the build, assets_src/creatures/old_shoal/build_old_shoal.py.
- 2026-10-31: built. assets_src/creatures/old_shoal/build_old_shoal.py writes assets/creatures/old_shoal/old_shoal.glb.
  - It is 16.6k triangles with 18 bones: a 9 m reef-crusted shell with coral domes, standing stones and weed; a
    folded neck; a head with its own jaw and eyelids; two fore-flippers on the sand.
  - It reproduces byte for byte.
  - Clips are as the sheet's table, with `settle` as the KO.
  - Materials: skin, shell, eye, weed and stone, none emissive.
  - Also built: the Blender job `creature_old_shoal`, its battle scene, the creatures row (`ko: settle`; contacts
    for attack, cast and bite; no `clip_by_skill` until Combat writes its skills), a portrait, PROVENANCE rows and
    tools/tests/test_old_shoal.py.
  - Polish once battle presentation frames it: the face's close read (the lids and the beak) at the arena camera.
  - For Combat (review): the skills and the enemy row, and the sheet's open questions.

## Review log
