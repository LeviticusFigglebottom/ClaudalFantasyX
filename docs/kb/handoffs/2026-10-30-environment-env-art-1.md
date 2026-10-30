# Handoff — environment (env-art) — 2026-10-30 #1

## Done
- **big19 H07 palette red** (b0eb0a49): the chapel's lime-wash damp dialled back into order_marble 0 (ΔE 0.018); the
  audit's palms west of the chapel became frangipani (one stood in H07's zenith sample).
- **The Lead's O17 sky check:** the storm slate is intended (M3-ENV-104). Answered in the live log.
- **Act II, env-art's share (ADR 0205): Ch10–Ch12 dressed**, all additive and merge-ready. Each zone's walks, rooms
  or ground are built from chapters' greybox, because the kit's fixed modules don't fit it. The kit's pieces are
  placed round them. Each zone has a grade, a preview with ten cameras (viewed) and tests.
  - Ch10, M4-A2P-040 (3abc9d20): `ch10_fen_dressing.py`, `fen_zones.py`, the four-variant mangrove system.
  - Ch11, M4-A2P-041 (272fce82, 79fc304f): `ch11_lowlight_dressing.py`, `vey_zones.py`, `lowlight_zones.py`.
  - Ch12, M4-A2P-042 (cd7fbf94): `ch12_keth_dressing.py`, `keth_zones.py`, plus `kit_keth_turf`. The kit's house
    and inn changed to granite walls and turf roofs.
- **Ch13–Ch15:** env-art dressed them in parallel (14ff2eb7, 562c7f57, 39968c35). It **withdrew** them in the big22
  merge because the integration branch already carries them, mounted, from session 01UPFyEA3.
- **FAST-TRACK:** `test_keth` follows the inn's dry-stone walls (c010ee90).
- **Mount requests filed to chapters:** M4-A2P-0401, 0411 and 0421.

## In progress
- M4-A2P-040/041/042 stay `doing` until each mount lands and env-art views the mounted zone (walk renders).

## Exact next step
1. Watch for chapters' mounts. Once one lands, walk-render that zone (`game/levels/_tests/walkthrough/walk_render.tscn`
   with the zone's own scene), fix what reads wrong, and set the task to `review` (reviewer: rendering).
2. The Lead's PC pass 5: row 59 (`ch01_o10_gull` framing, the roof's ring decals); rows 24/66 with integration-qa.
3. (Done: Ch10's Kirru roost weave was re-rendered close up and reads fine. No other env-art item is open.)

## Known issues
- **Ch12 shade:** near-black on lavapipe in every shadow. It's on the PC-QUEUE; the remedy is chapters' ambient or
  the crag tint.
- **Ch11, chapters' calls** (in M4-A2P-0411):
  - the well's mouth is open in the sanctum floor;
  - L02's wading needs the floor lowered;
  - the underwater rig below −2.05.
- **Ch10:** the layouts' ambient 0.5 → 0.85 (in M4-A2P-0401).

## Files touched
- **Built from the greybox:** `assets_src/environments/kits/haluna/{fen_zones,vey_zones,lowlight_zones,keth_zones}.py`.
- **Kit and build:** `assets_src/environments/kits/haluna/{ossa_fen,keth,materials,build}.py`, `shrine.py` (H07);
  `assets/environments/kits/haluna/*` (the new glbs, their imports, the manifest, materials); `assets/PROVENANCE.md`;
  `tools/dev/blender_builds.json`.
- **Generators and tests:** `tools/act2/ch1{0,1,2}_*_dressing.py`, `tools/tests/test_ch1{0,1,2}_*_dressing.py`.
- **Generated zone data:** `game/levels/ch1{0,1,2}/<zone>/*_{dressing.json,environment.tres,water_material.tres,waves.tres}`.
- **Previews:** `game/levels/_tests/{ossa_fen_kit,ch11_zones,ch12_zones}/*_dressed.tscn`.
- **Docs:** `docs/kb/art/environments/{lowlight,keth_pass}.md`; `docs/kb/tasks/M4/M4-A2P-04{0,1,2}*.md` and the
  `04{01,11,21}` requests; `docs/kb/handoffs/live/env-art.md`.
