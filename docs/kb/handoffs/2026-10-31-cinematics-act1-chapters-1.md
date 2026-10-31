# Handoff: act1-chapters (the Act III chapters track, with the combat seat), 2026-10-31, session 1

## Done
- **The Lead's 23:05 Act I FAST-TRACK (logged earlier):**
  - Touch beats entered during a scene now play after it (ZoneStory `pending_touches`).
  - The Ch9 landing marker sits back on the floor.
  - Ch8's interior plays headless to its end.
- **Act III flows, each with a greybox zone, shots, marks and a thread test:**
  - Ch17 (M5-A3P-1001), Ch18 and the Kite (1004), and Ch19 (1007): earlier today.
  - Ch20 `ch20/undertow_layers` (1011): a walled stair of floors down the well, each flight veiled until the floor
    above is done.
  - Ch21 `ch21/heart` (1015): H01–H09.
  - The Ending's E1–E4 aboard the Kite (`chapters/ending.json`, read by Ch18Zone once `ch21_unbound` is set).
- **Act III fights**, each in its band at 500 seeds (the bands are in balance_targets.md "Act III"):
  - The Wardens (1009); the six held release fights and the Cage (1013); Kesh and Sefir's three phases (1017). The
    Letting is a ward set piece.
  - The eight Act III regulars (1849); the Ch18 optional bosses (combat rows for 1852 and 1853).
- **Audits:**
  - battle_vfx_coverage INTENDED rows explain the set-piece and Act III gaps.
  - The Act I flow and audio audits leave out later acts' rows.

## In progress
- Nothing un-pushed. The live log's last MERGE-READY line is the head.

## Exact next step
BACKLOG EMPTY. Each remaining item waits on another track (the live log's "Exact next step" has the list):
- M5-A3P-1009's mid-battle line hook, for the fight lines.
- M5-A3P-1203: E5–E7 at Haluna and Oruvel, and the credits' vignette and `next_scene`.
- Design's Kite world map: placement of the optional bosses.
- The battle models for Sefir, the Stilled, the founders, the Tide Matron and the Old Leviathan.

## Known issues
- **Missing staging:** H09's montage places (`iskarra_columns`, `tamsule_bell` and others) are inserts in other zones,
  so the sequencer warns in the heart. R1's per-member lines need the party standing as talkable actors.
- **MP drain:** `drowned_lantern`'s MP drain draws HP until the battle core has an MP-damage key.
- **The shoal's start:** `held_shoal` starts targetable until the first blow. The validator wants every phase below
  full HP.
- **Missing music:** `ch21_sefir_warden` has no `encounter_music` row (audio).
- **Failing, not mine:** `test_audio_loudness` and `test_rig_integrity.TestRigIntegrityAsha` fail in the full tools
  run. This branch touched no audio asset or rig.

## Files touched (main)
- `tools/act3/ch18_greybox.py`, `ch19_greybox.py`, `ch20_greybox.py`, `ch21_greybox.py`; `tools/act2/ch15_16_greybox.py`.
- `game/levels/ch18/**`, `ch19/**`, `ch20/**`, `ch21/**` (layouts and scenes; Ch18Zone and Ch19Zone).
- `game/data/flow/chapters/ch17.json`–`ch21.json`, `ending.json`, `chapters.json`, `ch18_field.json`.
- `game/data/battle/{enemies,skills,encounters,vowbound,sim_policies}.json`, `tools/balance/targets.json`.
- Shared appends: flags.tres, loc ch17–ch21, locations.json, creature_voices.json, qa_known.json, ownership.md,
  music.json (pending list).
- `tools/battle_vfx_coverage.py`, `tools/act1/flow_audit.py`, `tools/audio/act1_audio_audit.py`.
- Tests: `test_ch17_thread`, `test_ch20_thread`, `test_ch20_walkable`, `test_ch21_thread`, `test_ch21_walkable`.
- Task files: M5-A3P-1011, 1013, 1015, 1017 and 1849 (review); M5-A3P-1203 (a new request).
