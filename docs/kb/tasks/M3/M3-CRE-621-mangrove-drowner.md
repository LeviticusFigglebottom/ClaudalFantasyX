---
id: M3-CRE-621
title: "Build the Mangrove Drowner (Act II, Ch10 boss) from its design sheet"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a914f3f68a1829757 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The first Act II build from M3-CRE-620's sheets: the Mangrove Drowner (`mangrove_drowner`,
docs/kb/art/creatures/act2/mangrove_drowner.md) through the creature pipeline (docs/kb/art/creatures/pipeline.md).

## Acceptance criteria
- [x] `assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py` on the creature kit: a dome of twelve
      arched, knuckled prop-roots (arches to 3.1 m, 3.6 m risen; 5 m across the root centres, 5.6 m to the
      flared feet) round a wet black core, bark bleached to `bone` on
      top, `timber_weathered` down the arch, a `coral_stone_weathered` barnacle band and barnacles at the
      waterline, `lacquer_black` and wet below it; the core `lacquer_black` to `abyss_navy` with a `spawn_wound`
      seam in each gap between two roots; the trunk stump (its own mesh, `Stump`: its break at 3.2–3.6 m, its
      splinters to 3.8 m).
      Every colour is a palette.json swatch, and there is no green.
- [x] 16,370 triangles (budget 18k), 48 bones. Deterministic: `verify_blender_builds.py --job
      creature_mangrove_drowner` prints identical.
- [x] Clips: `idle` (4 s tide breath), `attack` (the drag: the two front roots reach 4.2 m out along the water and
      haul back, contact 0.7 s of 1.4 s), `cast` (the rising water: the roots spread and the core climbs, peak
      1.0 s), `hit` (the cage shudders and the core recoils, peak 0.1 s), `ko` (the roots let go one by one and
      splay out as it sinks 0.45 m), `phase_change` (2.2 s: it wrenches, the stump splinters and topples, six
      flat splinters fly, six roots plant as legs and the body lifts 0.55 m), `idle_risen`, and the strikes played
      from the risen pose (`attack_risen`, `cast_risen`, `hit_risen`, via `ck.in_pose`). Legs and hanging roots
      are placed by a deterministic grid solve in each root's plane (`solve_bend`); `--report` prints the feet.
- [x] materials.json (`bark`, `carapace`) and write_materials.py; the Blender job; PROVENANCE rows.
- [x] game/creatures/mangrove_drowner/mangrove_drowner_battle.tscn and the creatures.json row: phase `uprooted`
      (clip, `idle_risen`, `hide_after: ["Stump"]`, the risen strike map), contacts, loops, `stand_in.yaw_deg`
      90, `portrait` rim 2.8 and kick 1.8 (a dark row).
- [x] Import rule lists the folder; the `.glb.import` runs the creatures post-import script.
- [x] Review shots `creature_mangrove_drowner` (idle) and `creature_mangrove_drowner_risen` (phase 2), viewed and
      approved; only their baselines.json entries changed.
- [x] tests/unit/test_creature_actor.gd: the drowner uproots (stump seen splintering, hidden after), idles
      risen, drags from the risen pose with its contact, and its risen hit wins over the variants.
- [ ] Encounter (not this task): an enemies.json row with `model` and a phase `uprooted` at 50% HP, when the
      Ch10 encounter is designed. No enemy row was invented; the validator allows a creature no enemy uses yet.

## Notes
- Not modelled, by the sheet: the snagged motes (VFX, `glimmer_held`; on the KO they rise as `glimmer_lift`)
  and the drag's telegraph (the water drawing toward it). Request VFX when the encounter exists.
- Break part (the sheet's proposal, the two snagged-mote roots): needs a charge skill id for `break_parts`;
  not wired.
- Next look pass: the core still reads smooth and glassy under the noon light (bigger blisters or folds); the
  risen stance is spidery by nature (six legs), so a reviewer should judge it against rule 1.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
