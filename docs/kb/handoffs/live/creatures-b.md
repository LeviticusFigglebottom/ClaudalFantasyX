# Live log: creatures-b environment

Feature track for **the Act I bosses and the Act I Vowbound at final quality** (ADR 0041), branch `claude/creatures-b`,
started 2026-10-28 from `origin/claude/undertow-lead-handoff-ze8rrn` bd3ab5b. **This environment owns this file**
(CLAUDE.md §7a). Regular enemies and wildlife stay with the creatures track (`creatures.md`); the shared creature kit,
CreatureActor and the validator are theirs too (kit or tool changes go to them as request tasks).

## Scope (from game/data, 2026-10-28)
- **Bosses** (enemies.json rows with phases, or a choreo.json `boss_intro` row): `hullgnaw` (Ch1), `drownbell`
  (the slice, Ch3), `bottle_hermit` and `spar_wraith` (Ch4), `cinder_matron` (Ch5), `undertows_reach` (Ch8).
  `stillguard_inquisitor` (Moll, Ch6) is a person: the characters track builds him (M3-CHR-507, on claude/characters).
  The Lamp Engine is Ch11 (Act II, paused by ADR 0041). Ch7 has no foes and Ch9 no fight.
- **Vowbound met in Act I:** `ilun` (Ch3), `kahre` (Ch5), `virel` (Ch8). The creatures track built all three
  (M3-CRE-638/640/641) on claude/creatures; they are not on the integration branch yet, which is why Ilun still reads as
  a capsule there.
- `docs/kb/qa/act1_final_inventory.md` does not exist yet (integration-qa); these rows come from my own audit until it
  lands.

## Base
- **claude/creatures @ 851c4136 is merged into this branch** (813677a4): every model above is there, and the
  integration branch is not. **Lead: merge claude/creatures before (or with) claude/creatures-b.**

## NEW ACCOUNT (from 2026-10-25)
- 2026-10-28: branch made, binding docs read, ownership claimed (339557e6), toolchain set up.
- **Audit done (M3-CRB-001, 2a4a9db1):** all nine self-rendered on the review stage and viewed; the table is in the
  task file. Primitive (full rework): hullgnaw, undertows_reach, bottle_hermit, ilun, kahre, virel. Medium:
  spar_wraith. Light: drownbell, cinder_matron (and the Matron needs a small closed spawn_wound mark, ADR 0151).
  Every boss lacks `ready` and `intro` clips; nothing has VFX anchor bones yet.
- **Hooks (the contract, no data key):** every boss GLB gains an `intro` clip and unweighted bones `vfx_wound`,
  `vfx_core`, `vfx_phase`; every Vowbound `vfx_core` and `vfx_keepsake`. Requests filed: **M3-CRB-009** (combat /
  battle-presentation: BattleBossIntro plays `intro`; intro and phase VFX start at the anchors) and **M3-CRB-010**
  (creatures: CreatureActor.vfx_anchor, M3-CRE-651, resolves a bone named `vfx_<name>`).
- **In progress (worktree agents):** M3-CRB-002 hullgnaw, M3-CRB-004 bottle_hermit, M3-CRB-008 ilun. Next wave:
  spar_wraith, kahre, undertows_reach, then virel, drownbell, cinder_matron.
- **MERGE-READY @ 2f37abe7: M3-CRB-008 part 1, Ilun to final quality** (worktree agent, viewed by me).
  - A thick-bodied manta (0.42 m disc, spine ridge, broad head, gill slits, scroll lobes), a continuous knotted net
    of glimmer_bound light along the wing's span and chord, three long plumes, a whip tail and the glass float in a
    cord net. Wingspan 5.1 m: the biggest thing on the field at battle distance, inside the safe frame at rest.
    15.6k triangles, 20 bones (`vfx_core`, `vfx_keepsake` added, unweighted). Clips and contact times unchanged.
  - **Checks run:** Blender verify identical (creature_ilun); tools test_creatures and test_blender_builds 48 OK;
    validate_data 0 errors; Godot ilun 6/0, vowbound 83/0, creature 74/1 (test_creature_portraits: the ~26 unbaked
    portrait PNGs, known on claude/creatures, not this change). **Skipped:** gdlint/gdformat (no .gd), coverage.
  - SELF-RENDERED @ d5101f4f: creature_ilun, battle_vowbound_out, battle_choreo_summon, battle_choreo_vowbound_rise —
    drift (the new model, intended); viewed: reads as a vast luminous manta with net, crest and float. Open polish:
    the near wing is pale at the battle camera's grazing angle; a true see-through look needs a spectral material in
    the kit (creatures').
- **In progress:** M3-CRB-002 hullgnaw, M3-CRB-004 bottle_hermit, M3-CRB-008 kahre (worktree agents).
