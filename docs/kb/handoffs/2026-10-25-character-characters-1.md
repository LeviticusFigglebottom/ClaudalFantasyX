# Handoff — character (characters environment) — 2026-10-25 #1 (ACCOUNT HANDOVER)

Cloud session `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch `claude/characters`. The full picture is in
[`live/characters.md`](live/characters.md) under **STATE AT HANDOVER (2026-10-25)**. This file is a summary.

## Done (on claude/characters; merge-ready lines are in the live log)
- **M1-CHR-14:** braid, clipping, rig guards (`tools/dev/rig_probe.py`, `rig_checks.json`, `test_rig_integrity.py`) and host-independent Asha. Already on the integration branch via big7.
- **M2-CHR-07:** hero battle clips. **M2-CHR-12:** field locomotion, wired in by hero-integration.
- **M2-CHR-11, base_body and villager half:** identical on three numpy SIMD paths.
- **M3-CHR-01 Ysolde** and **M3-CHR-02 Sefir:** hero builds (review).
- **M3-CHR-03 villager half:** Tavi and Kell, plus the wick props.
- Design sheets for Liss, Tavi, Kell, Kerrid and Pell.
- **M2-BPR-10:** reviewed and approved (data only).

## In progress
- **M1-CHR-15**, complete but unmerged: `wip/M1-CHR-15.patch`.
- **M2-CHR-513**, WIP: `wip/M2-CHR-513.patch`.
- **Paused:** Liss (`wip/M3-CHR-03-liss.patch`) and Kerrid (`wip/M3-CHR-505-kerrid.patch`). Pell is blocked on M3-NAR-01.
- **The Lead's M3-CHR-05** (32 Ch4–Ch9 clips): not started.

## Exact next step
Merge M1-CHR-15 into claude/characters:
1. Apply the patch (base becc8ca3) or merge its branch.
2. In `hero_clips.py`, keep both the M1-CHR-15 and M2-CHR-12 blocks.
3. Rebuild asha, rhen and toma with build.sh, regenerate every clip library, re-capture and view the hero shots.
4. Verify on three numpy paths.

Then finish M2-CHR-513 on top of that.

## Known issues and gotchas
See the live log: SIMD host determinism, garment rules, the shared hero_clips.py, the id blocks, and the fact that send_message to the Lead is refused.

## Files touched this session (high level)
- `assets_src/characters/{asha,rhen,toma,sefir,ysolde,villagers,props,base_body}/`
- `assets/characters/**`
- `tools/dev/{rig_probe.py,rig_checks.json,blender_builds.json}`
- `tools/tests/test_{rig_integrity,hero_*,sefir,ysolde,villagers}.py`
- `tests/screenshots/**`
- `game/data/characters/locomotion.json`
- `docs/kb/{art/characters,tasks,handoffs}/**`
