---
id: M3-CRE-707
title: "FAST-TRACK, PC row 85: the storm figure's and the crowd's materials free after their meshes, and nothing swaps them at teardown"
role: character
status: review
owner_session: "creatures (claude/creatures)"
reviewer: qa
depends_on: []
milestone: M3
---
## Goal
The Lead, 2026-10-31 02:21. On the human's PC, `Parameter "material" is null` looped at shutdown and wrote a 59 GB
log. The storm figure's material (row 44's path: NpcSilhouette on a VillagerLayer `silhouette` row) is the likely
freed material. Check how it creates and frees its material: nothing should touch a freed material, and nothing should
run in `_process` once the node is leaving the tree. integration-qa owns the shutdown order.

## What was wrong (creatures' side)
- **FieldNpc `_exit_tree` called `NpcSilhouette.clear`** (the pass-3 fix for row 44). On every teardown it swapped
  the figure's surfaces back to the crowd body's own materials, mid-teardown, and freed the silhouette's materials in
  the same frame.
- **Without that clear**, a MeshInstance3D frees its override materials in its own destructor, before its base
  (VisualInstance3D) frees the render instance. So each surface's material dies while the instance still references
  it. Headless, that logged `material is null` once per surface (measured: 6 in the crowd suite).
- **NpcTints kept a static cache** of every tinted copy (every crowd person's cloth and hair). It is the same pattern
  as row 44's original static cache: the materials outlived the scene and were freed at script unload during
  shutdown.

## Fixed
- **FieldNpc** holds every override material it puts on its actor (`override_materials`: tints and silhouette) as
  well as the meshes. On free, the children (the meshes and their render instances) go first and the materials after,
  when the FieldNpc does.
  - The `_exit_tree` clear is gone, and so is `NpcSilhouette.clear`, so nothing swaps materials at teardown.
  - `tick` returns when the node isn't inside the tree.
- **NpcTints** caches its shared copies weakly: shared while any wearer lives, freed with the last.
- **CrowdFar** holds its one material as a member, so it frees after its MultiMeshes.

## Acceptance criteria
- [x] Godot crowd 26/0 with **0** `material is null` (it was 6 without the holder); villager 50/0, npc 10/0,
  zone_cast 5/0, all with 0.
- [x] A new test, `test_leaving_the_tree_keeps_the_materials_and_freeing_frees_them`, checks two things: out of the
  tree the figure wears the same materials, and freeing frees the tinted copies. The pass-3 test still holds: no
  silhouette material outlives the figure.
- [ ] **integration-qa / the PC:** a hardware run through Corrow (the storm figure) and a crowd zone, then quit. The
  log must carry no `material is null`. If the shutdown loop persists, it is elsewhere: the remaining instance-uniform
  writers are `vegetation_plant.gd` (SHELTER_PARAM) and `shell_shrine_level.gd` (SHIMMER), neither of them
  creatures'. Shutdown order is integration-qa's.

## Review log
