# Act I's crowd (M3-CRE-659, ADR 0152)

Act I's generic background people (the capsules the placeholder inventory gave creatures) are **crowd people**: 56
rows in [`game/data/world/npc/crowd.json`](../../../../game/data/world/npc/crowd.json), each wearing one of **22 crowd
bodies** built through the characters' villager pipeline (pipeline.md §15) at a crowd tier, and coloured per
person at runtime. Runtime and zone rows: [`docs/kb/tech/field_npc.md`](../../tech/field_npc.md) "Crowd rows".

## 1. Pipeline

| Step | File | What |
|---|---|---|
| Roster | `game/data/world/npc/crowd.json` | per person: `zone`, `stage_actor`, `role`, `community` (+ `island`), `age_band`, `sex`, `build`; generated: `body`, `tints`, `work`. Plus the `bodies` plan, `age_tuning` and `work_tuning` |
| Ranges | `assets_src/crowd/ranges.json` | per community: skin endpoints, hair mixes, cloth mixes (a, b, c), reach-bands, `accepts`; per role: kits, work clip, cloth; per age band / sex / build: body sliders; per band: face sliders; per hair kind; per kit: villager_costume pieces |
| Generator | `assets_src/crowd/gen_crowd.py` | seeded (crc32 of names), deterministic: `params/<body>.json` in the villager schema (+ `_work`) and the roster's generated fields. `--check` for CI |
| Build | `assets_src/crowd/build_crowd.py` | Blender: `build_villager.main` with its `PARAMS_DIR` moved; LOD0 to the bake dir, LOD1 shipped as `assets/crowd/<body>/<body>.glb`. python3: `villager_textures.skin` (head 512/256, body 256), `write_materials.tables` re-rooted (only the GLB's slots), `<body>_actor.tscn`, `villager_clips.build` plus the work clips |
| Work clips | `assets_src/crowd/crowd_clips.py` | `mend`, `sweep`, `carry`, `fold`, `haul`, `kneel_mourn`, `vigil` on hero_clips; kneels solved from each skeleton's bone lengths |
| Import | `game/data/import/crowd.json`, `crowd_post_import.gd`, `write_imports.py` | as the characters rule: slot materials, auto LODs, the clip library on an AnimationPlayer |
| Jobs | `tools/dev/blender_builds.json` `crowd_<body>` | verified byte for byte by `verify_blender_builds.py` |

Nothing under `assets_src/characters/` is edited: every module is imported and its module-level paths and sizes are
moved from outside. Rebuild one body: `blender --background --factory-startup --threads 4 --python
assets_src/crowd/build_crowd.py -- --body B --bake-dir D`, then `python3 assets_src/crowd/build_crowd.py --body B
--bake-dir D`.

## 2. Bodies

Five children (two boys, two girls, a girl of about thirteen), ten lay adults (men and women, lean, medium and
heavy), four elders, and two Order bodies in robes. Every villager_hair kind appears (short, cropped, bun, wrap).
Each face is rejection-sampled to stand at least `face_min_distance` (0.28, RMS in adult-range units) from every
Haluna villager's face (M3-CHR-100: crowd bodies are new people) and from the other crowd faces of its band
(`tools/tests/test_npc.py`). Per body about 0.6–0.85 MB of LOD1 GLB (15–19k triangles), 0.6 MB of maps and
0.3–0.8 MB of clip text.

## 3. Variety scheme

- **Assignment** (`gen_crowd.assign`): a person's body must match their age band and sex, come from a community
  theirs `accepts` (skin and dress close enough), be a robe body if and only if they are Order, and be **unused in
  their zone**. Among those it scores the build, the body's own community, a preferred kit, and each earlier use
  (−2.5), so bodies spread (at most four wearers). Zones with the most people go first; within a zone, the person
  with the fewest choices.
- **Tints**: cloth_a, cloth_b and cloth_c are drawn from the person's community sets (roles and the Reefball sides
  override), each a palette.json swatch mixed toward another (`[a, b, t_lo, t_hi]`), so every tint is a palette
  swatch or a two-swatch mix (validated). Hair moves along the body's own hair mix by up to 0.35, so the baked
  scalp underpaint still sits under a near colour. A person's tints are redrawn (24 tries) until they stand 40 sRGB
  units from every other wearer of the body in some cloth slot; the validator holds the line at 24.
- **Motion**: FieldNpc's per-id idle phase and HeroIdleMicro already keep two wearers out of step; work clips and
  chat pairs vary the silhouettes further.

## 4. Review

`game/levels/_tests/npc/crowd_lineup.tscn` (shots `crowd_lineup_a/b/c`, `crowd_market`, `crowd_work`,
`crowd_mourners`) and the real zones with a layer (`crowd_<zone>.tscn`, shots `crowd_zone_*`). See the task's
review notes for what each render showed.

## 5. Known limits (requests to characters in the task file)

- Saltwright line-marks and the brine-brand are not drawn: villager_textures paints only Low Reaches reach-bands,
  so the wrights' forearms are bare.
- No hand props: the work clips read through the hands and head alone (M3-CRE-614 covers props for the villagers).
- The build still makes and discards LOD0 (about a third of each Blender run).
