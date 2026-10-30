# Handoff: character (creatures-b) 2026-10-28 #1

Branch `claude/creatures-b` (from integration bd3ab5b, with claude/creatures 851c4136 merged in). Live log:
`docs/kb/handoffs/live/creatures-b.md`.

## Done
- M3-CRB-001: the audit of the Act I bosses and Vowbound (self-rendered and viewed), the hook contract, and its test
  `tests/unit/test_creature_bosses_act1.gd`.
- Final-quality passes, each self-rendered and viewed at battle distance (worktree agents, merged here):
  M3-CRB-002 hullgnaw, 003 drownbell, 004 bottle_hermit, 005 spar_wraith, 006 cinder_matron, 007 undertows_reach,
  008 ilun, kahre, virel; plus two polish rounds (Kahre's hammer and plates; the Reach's facets and the hermit's gloss).
- Every boss has `ready` and `intro` clips and unweighted `vfx_wound`/`vfx_core`/`vfx_phase` bones; every Vowbound
  `vfx_core`/`vfx_keepsake`. The Matron gained her spawn_wound weak point (a sealed sight-glass).
- Requests filed: M3-CRB-009 (combat / battle-presentation: play `intro`, start intro and phase VFX at the anchors,
  the Reach's crowded battle camera, the Fisher Stair capsule) and M3-CRB-010 (creatures: vfx_anchor resolves
  `vfx_<name>` bones).

## In progress
- None. (The minor-polish round merged at b4ee2492.)

## Exact next step
1. When the Lead merges claude/creatures and this branch, merge the integration branch back and re-run those filters.
2. When battle-presentation answers M3-CRB-009, render battle_boss_intro_* to check the intro clips play.

## Known issues
- test_creature_portraits fails on unbaked portrait PNGs (ui-menus' bake; every reworked creature's portrait is stale).
- A true see-through spectral material for the Vowbound needs a kit change (creatures').
- Virel's S is near edge-on from the held shot's front view (Act III, paused).
- The Ch5 arena's front edge shows stretched texture streaks (env-art / battle-presentation).

## Files touched
assets_src/creatures/{hullgnaw,drownbell,bottle_hermit,spar_wraith,cinder_matron,undertows_reach,ilun,kahre,virel}/,
assets/creatures/<same>/, game/data/creatures/creatures.json (these rows), docs/kb/art/creatures/ sheets for these,
docs/kb/tasks/M3/M3-CRB-*.md, tests/unit/test_creature_bosses_act1.gd, tests/unit/test_creature_virel_vowbound.gd,
assets/PROVENANCE.md (two Matron rows), docs/kb/ownership.md (one row), docs/kb/handoffs/live/creatures-b.md.
