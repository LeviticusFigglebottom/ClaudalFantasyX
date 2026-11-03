# Gate big47 (fast gate, ADR 0205)

Integration base: claude/undertow-lead-handoff-ze8rrn @ e2411fb0 (big45 plus the 11-03 Lead docs). big46 (characters' row 56 notch fix) isn't
merged yet; characters' head here carries it.

## Pinned heads (merged with --no-ff in this order)
The human's 11-03 playtest FAST-TRACKs, all five items:
1. claude/hero-integration @ e7cae923: **FAST-TRACK 1**, M3-HER-1231, the walk cycle no longer stops (3aee287c); placeholder_audit's summon
   scope (8c922bf4). Log: MERGE-READY @ 817699bb.
2. claude/combat-systems @ fa7476aa: **FAST-TRACKs 2 and 5**, M3-CMB-03..06: the Relighting Wick (revive) in the Act I economy, the fallen
   up at 1 HP after a win, field-castable spells (FieldSpell), the solo Ch1 Hullgnaw eased. Log: MERGE-READY @ 08eaf116 (plus log commits).
3. claude/characters @ 4a30d472: row 56 (big46's notch fix, verified), row 55 (Fenn, Sabe), row 54 steps (Sefir's hair). Log: MERGE-READY @ 6e3cd47a.
4. claude/ui @ e58f9938: **FAST-TRACKs 3 and 5**, M3-UI-1250 (status help, first-time cards, Codex Afflictions), M3-UI-1251 (the field Magic page on
   FieldSpell), M3-UI-1253 (field revive), Act I rows 68, 69, 73. Log: MERGE-READY @ 73699ed9.
5. claude/battle-presentation @ 60f90177: **FAST-TRACKs 3 and 4**, M3-BPR-450/451: statuses on the body (overlay, aura, prop, icon) and
   the storm fights' sky (BattleStorm). **Not marked MERGE-READY in its log** (one commit, 60f90177); taken as Act I FAST-TRACK content.
6. claude/act1-chapters @ 66c19e6e: **FAST-TRACK 4**, M3-C01-1252, the storm's fights on storm arenas with storm music. Log: MERGE-READY @ 1bcae269.
7. claude/audio @ 9ff655c1: **FAST-TRACK 4**, M3-AUD-865 storm music, M3-AUD-866 status, cure and revive cues. Log: MERGE-READY @ 25256466.
8. claude/env-art @ 9b51f2c8: **FAST-TRACK 4**, M3-ENV-1340 (oruvel_raft_storm with the Undertow); PC rows 24, 47, 77, 86. Log: MERGE-READY @ 4f450a7c.
9. claude/env-art-b @ 4d3c97ef: **FAST-TRACK 4**, M3-ENV-1334 (the Ch8 storm arenas); rows 71, 72, 82, 84; the anvil court rewrite. Log: MERGE-READY @ 211d8bd7.

Not moved since big45: m2-slice (slice-polish), creatures, creatures-b, act2-plan.

## Conflicts
- docs/kb/ownership.md (battle-presentation, env-art-b): three appended rows, all kept.
- assets/PROVENANCE.md, tests/screenshots/shots.json (audio, env-art): merge_union.
- **env-art-b vs env-art: both built `oruvel_raft_storm`** (env-art's 52bf4c11 through `arena_scenes.write_arena`; env-art-b's 6b8e416d through its
  new `tools/act1/storm_arenas.py`). env-art owns `assets/environments/arenas/**` (ownership.md), so **env-art's scene and preview are kept**, and
  env-art-b's duplicate PROVENANCE row is dropped. arenas.json takes act1-chapters' `storm` table, with `oruvel_raft_storm` pointed at its own scene
  and moved from `storm.pending` to `storm.arenas` (act1-chapters' logged next step; `drowned_choir_storm` stays pending).
- Merge fallout: two task files with id M3-ENV-1340 (env-art's arena; battle-presentation's storm FYI request). The request is renumbered
  **M3-ENV-1341** (its file, M3-BPR-451's and battle_status_looks.md's references).

### LEAD-NOTES (overlaps for the Lead to route; not changed by the gate)
- `tools/act1/storm_arenas.py` (env-art-b) still writes `oruvel_raft_storm`; re-running it would overwrite env-art's scene. Route: env-art-b to drop
  its Ch1 id, or env-art to hand the arena over.
- Three storm mechanisms meet in the Ch1 fights: BattleStorm (battle-presentation, keyed by encounter in storm_fights.json, adds the storm and the
  Undertow at spawn), env-art's storm arena (its own Undertow), and act1-chapters' storm table. A Ch1 storm fight may draw two Undertows. Also,
  storm_fights.json lists `ch08_headland_*` and `ch08_flue_moths` as storm fights, while act1-chapters' doc says the headland fights come before the storm.
  The shots will show it; route: battle-presentation + act1-chapters + env-art.

## Build checks
validate_data 0/0 · taskboard --check clean (after the renumber) · dlgc --check clean · gdlint and gdformat clean (1131 files) · no duplicate loc
keys · no conflict markers · no new binary over 5 MB · no gate-run images.

GATE-BUILT @ 16ee7393
