---
id: M3-RND-25
title: "The underwater battle arena's look under the battle camera (underway_tower)"
role: rendering
status: todo
owner_session: ""
depends_on: [M3-ENV-06, M3-RND-24]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
`underway_tower` (M3-ENV-06; docs/kb/tech/battle_arenas.md "The underwater arena") is the first battle fought under
the sea: the lamp gallery (F9) of Ch1's drowned tower, 22 m down, lit only by Rhen's oil lantern, the breach's
morning teal and held cyan motes (colour script `ch01`, oruvel_underway.md §0 `ch01_underway_int`). Environment built
its best proposal on the existing `UnderwaterRig` (M2-RND-02, M2-RND-09) without waiting for an agreement; this task
asks Rendering to agree (or change) that look and to take over the stand-ins. It extends M3-RND-24 (downwelling and a
per-area scale for the Underway zone) to the battle camera. Baseline: `battle_arena_underway_tower`
(`game/levels/_tests/battle_arenas/preview_underway_tower.tscn`, lavapipe).

## What the arena carries now (stand-ins)
- `Arena/Underwater`: an `ArenaUnderwater` (`game/world/arenas/arena_underwater.gd`), the rig plus one export,
  `light_scale` 0.33, which scales the in-scatter's light level (the rig lights its water with the sun and no
  occlusion, so indoors the water glowed like the open sea and drowned the lantern). It never writes the rig's shared
  `load_data()` cache.
- The sun and the ambient baked tinted by the rig's own transmittance over 21 m (`#FFEFE1` → `#5BBDB4`, `#8FC3E0` →
  `#2F9AB3`; `arena_scenes.water_tinted`, the kit preview's formula): the downwelling the rig does not do.
- `Arena/Lantern`: a bare Node3D at Rhen's lantern hand on party slot 0 (2.1, 0.7) + 0.6 m towards the foe; the rig
  hangs its oil-lamp OmniLight and the post's halo there.
- `Arena/HeldMotes`: a held GlimmerField with `follow_scene_intensity` off (energy 1.5), because a day battle keeps the
  `hymn_glimmer` gate shut.
- `Sea` (the lagoon's surface) at y +22.4: the battle's hymn_water_level publisher, so everything is wet.

## What the arena needs from the rig under the battle camera
1. **A light scale on `UnderwaterRig` itself** (M3-RND-24 item 2), so the arena points at the rig and
   `ArenaUnderwater` goes. The battle needs a fixed value per arena (0.33 in the gallery), not a blend.
2. **Downwelling** (M3-RND-24 item 1), per pixel or per object: then the arena's sun and ambient go back to the
   `ch01` key and fill. Until then a hint camera high in the gallery is lit like the floor.
3. **The lantern on Rhen.** In battle Rhen is a fighter: the rig's `lantern_target` should be his lamp node, set by
   the presentation track (`Arena/Underwater.lantern_target = <Rhen's lamp>`), or the rig should find a lamp node by
   group. Agree which, and the presentation track wires it; the arena's `Lantern` then goes. When Rhen is not in the
   party (a later underwater fight), whose light is it?
4. **The halo near the lens.** The post's warm halo turns into a haze over the frame when the lamp is within ~2.5 m of
   the lens (seen in the kit preview's U06/U07). The default BattleCamera keeps 7.7 m off; the camera hints
   `party_side` and `foe_side` come within ~3 m of slot 0. Either the halo fades near the lens, or the camera director
   keeps 2.5 m off the lamp (tell battle-presentation).
5. **Battle VFX under the post.** Everything drawn before render priority 126 is absorbed and in-scattered: a spell 9 m
   off loses two-thirds of its red. Decide whether battle VFX (and the target rings, damage floats in 3D) opt out of
   the post or are tuned for it; held cyan and the oil lamp must stay the only "light" colours (oruvel_underway.md
   checklist).
6. **God rays indoors.** The shafts' FogVolume follows the camera and the volumetric fog is shadowed by the sun's
   shadow map; check on the GPU tier that no shafts draw inside the gallery where the walls block the sun, and that
   the breach's shafts read.
7. **Glimmer.** Agree the held field's own energy (1.5) under the battle's shut gate, or have the battle open the gate
   for an underwater arena.
8. **Cost.** The rig's +0.3–0.37 ms (High, 1440p) on top of the battle's frame, plus the gallery's ~360 kit instances
   and its one shadowed lantern: measure on the GPU tier.

## Acceptance criteria
- [ ] Rendering agrees the look (or files its changes) and answers items 3–7; Environment updates the arena.
- [ ] Items 1–2 land on the rig (with M3-RND-24); the arena's stand-ins are removed and `battle_arena_underway_tower`
      re-approved after viewing.
- [ ] GPU-tier capture and cost of the arena at High.

## Review log
