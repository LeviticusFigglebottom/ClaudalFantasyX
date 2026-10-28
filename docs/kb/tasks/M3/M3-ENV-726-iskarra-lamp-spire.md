---
id: M3-ENV-726
title: "The Iskarra Lamp Spire (Ch19): the crown, the anchor-engine and the revenant pair's arena; the Iskarra sheet"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-724]
milestone: M3
reviewer: rendering
---
## Goal
Ch19 (act_outline): the party climbs Iskarra's Lamp Spire to shut down the founders' anchor-engine, and fights
Warden Hesper Oan and Ilsabet Rue at the top. This builds on the Prologue's Iskarra (M3-ENV-724). Iskarra had no
sheet, so this task writes it.

## Acceptance criteria
- [x] `docs/kb/art/environments/iskarra.md` (the city, the kit and the Lamp Spire).
- [x] `iskarra_spire.py`: `spire_crown_floor` and `anchor_engine`.
- [x] The `lut_ch19_spire` grade (zone_lut; every other LUT is byte-identical).
- [x] The arena `iskarra_spire_crown`.
  - `arena_scenes.py`'s `extra_glbs` gains a `(glb, (x, y, z))` form for the city below; every other arena is
    byte-identical.
  - Wired into `arenas.json`, the preview fixture, test_battle_arenas, the shot and battle_arenas.md.
- [x] Tests: `tools/tests/test_iskarra_spire.py` (4).
- [ ] PC render viewed and approved: battle_arena_iskarra_spire_crown.

## Notes
- **2026-10-27 (env-art):** built. The spire's climb (interior stair drums, the exterior) waits for Ch19's beat
  sheet.
- **For combat and act1-chapters:** set the Ch19 revenant pair's encounter arena to `iskarra_spire_crown` when the
  encounter exists. It is not in encounters.json yet.

- **2026-10-27 (env-art):** a shadow sweep over every arena after fca9987 (a 24 m singer's moon-shadow lay over the
  Choir's party) found the same failure here before the first render. The 2° afterglow came from behind the enemy
  line, so the 7.4 m engine's ~200 m shadow lay across the enemy slots. The afterglow now comes from behind the party,
  as the arena's own note intended (azimuth 100°). `test_the_engines_shadow_misses_the_slots` holds it.
- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log
