# 0152 — Act I's background villagers: a crowd generator on the characters' villager pipeline

- **Status:** accepted (creatures, on the Lead's assignment of 2026-10-28)
- **Date:** 2026-10-28
- **Roles affected:** character (creatures and characters), cinematics (slice-polish), narrative (act1-chapters), qa
- **Author role:** character (creatures)

## Context
ADR 0041 puts Act I at final quality: no capsules. The placeholder inventory (docs/kb/qa/act1_final_inventory.md,
M3-HER-1144) lists 105 capsule people in the Act I zones. The Lead moved the **generic background people** to
creatures, as the VillagerLayer/FieldNpc owner: netmenders, mourners, tenders, children, vendors, fishers, boatmen,
traders, townsfolk, divers, wrights, sweepers, folders, a lacquerer, a cook, a clerk, passengers, a ferryman's mate
and a brand girl. That is about 51 people in 10 zones (Haluna's own villagers at the wake already have bodies). The
ask is a parametric villager generator (body, age, build, outfit by island and role, palette) with real meshes and
idle, walk and work clips, varied enough that no two look cloned.

The characters track already has a parametric villager pipeline (pipeline.md §15, M2-CHR-03): one build
(`build_villager.py --npc <id>`) and one params file per villager, the shared cloth atlas, per-villager skin maps,
and idle, talk and walk clips. At its NPC budget a villager is about 2.5 MB (LOD0 plus LOD1) with its maps, so 51
unique ones would add about 130 MB of plain git.

## Options
1. **A separate low-poly crowd body.** Cheap, but it would read as a second, cruder human beside the M2-CHR-03
   villagers in the same zones: not final quality, and an uncanny mix.
2. **One full villager per person through the characters' pipeline.** It looks best, but costs about 130 MB and 51
   Blender jobs, and the characters track would carry 51 params files it doesn't own.
3. **A crowd generator on the same pipeline, as a tier:** a roster samples params (body, face, skin, hair, costume
   and tints by island, role, age band, sex and build). A set of distinct crowd bodies is built through the
   characters' modules unchanged, and runtime colour variants are spread so no two people in sight match.

## Decision
Option 3.
- **Where:**
  - `assets_src/crowd/` and `assets/crowd/` (claimed by creatures);
  - the roster `game/data/world/npc/crowd.json`;
  - the zone rows in `game/data/world/npc/zones/<zone>.json`.

  The characters' villager modules are **imported, not edited**. A wrapper points their params and output paths at
  the crowd folders. If a module needs a real option, that's a request to characters.
- **The crowd tier:** ship only the LOD1 mesh (about 0.65 MB) and the 512-pixel head maps. Crowd people are seen at
  walking distance, never in a talking close-up. Speakers get their own bodies from characters.
- **Variety:** about 20 bodies span the age bands (child, adult, elder), sexes and builds, with island skin and hair
  ranges. The roster assigns each person a body plus cloth, hair and accessory tints (material overrides at
  runtime). No two people in one zone share a body with the same tints, and repeated bodies are kept to zones far
  apart. A test checks both.
- **Clips:** the villager set (idle, talk, walk), plus work clips per role (mending, sweeping, carrying, folding,
  hauling). Work comes from a crowd clip module in `assets_src/crowd/`, since M3-CRE-614 is characters'.
- **In the zones:** each capsule becomes a VillagerLayer row (`attach: child` on its stage actor), which hides the
  capsule. A GreyboxZone adds the layer (request M3-CRE-657 to slice-polish).

## Consequences
- About 20 GLBs at about 0.7 MB each, rather than 51 at 2.5 MB.
- A crowd person looks like a cousin of the M2-CHR-03 villagers, because it is one: the same topology, shaders and
  cloth atlas.
- Named speakers stay with characters (M3-HER-1144): Garo, Ivo, Hobb, Marra, Fenn, the ferrymaster, the purser,
  Sabe, Skipper Sadi, the scaleman, the elder, the gatekeeper and the stillguard.
- **Watch:**
  - Haluna's villagers must not stand in for other towns (M3-CHR-100), so the crowd bodies are new people, never
    Haluna's faces.
  - The tints must stay inside palette.json.
