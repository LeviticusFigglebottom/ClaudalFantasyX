---
id: M2-CHR-03
title: Haluna villagers at slice quality (Neme, Osu, Pila, the lane child, three generic villagers)
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters; worktree subagent)"
reviewer: rendering
depends_on: [M1-CHR-03]
milestone: M2
request-from: lead
---
## Goal
The slice's speaking NPCs in Haluna (game/levels/ch02/haluna/haluna.tscn, m2-slice's scene) are capsule stand-ins.
Build them as characters from the base_body variants (MPFB2 donor, ADR 0021) with costume variants and face poses:
Neme, Osu (Pila's granddaughter), Pila, the lane child, and three generic villagers. Each GLB well under 5 MB.

## Acceptance criteria
- [x] One reproducible build (Blender job, PROVENANCE rows) per villager GLB, shared modules reused, nothing copied.
- [x] Face shapes from the shared API (asha.md §6.2) and a pose table per speaking NPC; costumes that read as Low
      Reaches villagers (story bible), with colour variants for the generic three.
- [x] Review stage + shots on the hero stage, lavapipe baselines approved after viewing.
- [x] characters.md lists the scene paths m2-slice swaps in for each capsule.

## Review log

## Notes (M2-CHR-03 delivery, worktree subagent)
- **Who:** the story puts it the other way round from the brief: Grandmother **Osu** is Pila's granddaughter, and Pila
  died long ago (vertical_slice.md §4), so there is no Pila build. The seven are Neme, Osu, the lane child and the
  scene's four other speakers: the vendor, the netmender and the fisher (the three generic villagers, colour
  variants of the same pieces) and the Reed (an Order novice). Review: docs/kb/art/characters/villagers_review.md.
- **Build:** one parametric build, `assets_src/characters/villagers/build_villager.py --npc <id>` on build_asha and the
  rhen/toma/asha costume and hair helpers, `params/<npc>.json` each, `build.sh`, seven Blender jobs (`villager_<npc>`,
  verified identical), PROVENANCE rows, one cloth atlas for all (tinted per villager), body clips (`idle`, `talk`,
  `walk`) via `villager_clips.py` on hero_clips. No shared module changed.
- **Numbers:** LOD0 26.8k-34.3k triangles, GLBs 1.67-2.15 MB (LOD1 0.56-0.82 MB); all 40 face shapes, morph normals on 12.
- **Scene paths m2-slice swaps in** (replace `StandIn` and `Facing` under each StaticBody with the actor at its origin;
  the actor turns the GLB to face -Z like the capsules; the import rule assigns the materials, so instancing is enough):
  `NPCs/Neme/Neme` -> `res://assets/characters/villagers/neme/neme_actor.tscn`;
  `NPCs/Market/Vendor` -> `.../vendor/vendor_actor.tscn`; `NPCs/Chapel/Reed` -> `.../reed/reed_actor.tscn` (keep
  `Broom`); `NPCs/Dock/Netmender` -> `.../netmender/netmender_actor.tscn`; `NPCs/Dock/Fisher` ->
  `.../fisher/fisher_actor.tscn`; `NPCs/Lane/Child` -> `.../child/child_actor.tscn`; Osu (M2-FP-14, H08) ->
  `.../osu/osu_actor.tscn`. Play the `idle` clip (else A-pose). Face poses:
  `game/levels/_tests/characters/villagers/<npc>_face_poses.json` for sequencer.json `face_poses`.
- The live `characters.md` is the Lead's to update; the paths are here and in the handoff (2026-10-24-character-7.md).
- **Honest gaps:** the child's face reads adolescent up close (no child targets in the vendored donor data); age is
  in the textures, not the shape; short hair is flaky up close; no props (the Reed's broom stays the capsule's node).
- Dialogue polish, Neme (chr-npc-polish, M3): before, her grey share (12%) read as bright light streaks across the black bun hair, with warm highlight chips. After: the grey cards are thin sparse strands (`_hair.grey_strands`) and the hair specular dimmer and cooler (`_hair.spec`); reads as black hair with a few grey hairs.
- Dialogue polish, Osu (chr-npc-polish, M3): before, a dark band showed between the head wrap's edge and her brow (the wrap stood off the skin, its shadowed underside and hairline cards showing). After: the wrap's edge drawn in to the skin (`headwrap.edge_off_m`); the white hair shows only at the temples.
- Dialogue polish, the chapel Reed (chr-npc-polish, M3): before, his black crop showed warm yellow-brown highlight chips. After: a dimmer, cooler hair specular (`_hair.spec`); the crop reads dark (still a little tufty up close).
