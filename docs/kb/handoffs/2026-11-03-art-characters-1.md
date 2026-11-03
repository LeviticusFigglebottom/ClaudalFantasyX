# Handoff: characters (art), 2026-11-03, session 1

## Done (all pushed to claude/characters)
- Merged the integration branch claude/undertow-lead-handoff-ze8rrn (up to big46).
- **Row 56 (Asha's run skirt):** big45's reds are all green at this head, and the committed outputs rebuild byte for
  byte. test_hero_clips plus test_hero_battle_clips: 34 OK. test_hero_stage: 11/11. TestRigIntegrityAsha: 11 OK.
  Self-rendered asha_clip_run and asha_clip_walk (viewed): the skirt swings with the stride, and the feet and the
  underskirt show.
- **Row 55 (Fenn's and Sabe's white crop):** a darker base under denser, finer, lifted cards. Both read as cropped
  hair with a broken edge, not a cap (self-rendered and viewed).
- **Row 54 (Sefir's hair):** the front falls are denser (34 cards per group; LOD0 61,822 tris), and the hair material
  has alpha_boost 4.0, transmission 0.12 and stronger occlusion and per-strand value. The falls are solid now, but
  from the front they still read as flat ribbons.
- **FAST-TRACK 1 (the walk stops):** the clip side is clean. The walk and run loop, and the start/stop root-travel
  curves are monotonic and end at their distance_m. My suspect is HeroGaitClips' stop and start-by-distance logic
  (integration-qa's area); the notes are in the live log.

## In progress
Nothing is uncommitted.

## Exact next step
1. Row 54: rework Sefir's front-fall shading or geometry in assets_src/characters/sefir/sefir_hair.py: clumped
   strand groups with darker inner layers, not more cards (the LOD0 budget is 62k; it is at 61,822).
   Then run build.sh and verify_blender_builds --job sefir, self-render sefir_face, and view it.
2. Asha's verse-sleeve (asha_costume.py verse_sleeve) swings forward as a boxy dithered bag in asha_clip_run.
   After the fix, rebuild Asha and her clip library, and keep test_hero_clips and test_rig_integrity Asha byte-exact.
3. The PC (real GPU) should re-look at rows 54, 55 and 56.
4. Then Act II per ADR 0205.

## Known issues
- My test_rig_integrity runs of the whole file exceed 25 minutes under load. Run single classes.
- CONSOLIDATED §1 still lists "Pell's look", but no open QA row matches it (LEAD-ASK in the live log).

## Files touched
assets_src/characters/villagers/params/{fenn,sabe}.json; assets/characters/villagers/{fenn,sabe}/**;
assets_src/characters/sefir/{sefir_params.json,write_materials.py}; assets/characters/sefir/**;
docs/kb/handoffs/live/characters.md.
