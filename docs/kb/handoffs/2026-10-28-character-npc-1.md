# Handoff 2026-10-28, character (worktree `chr-npc-wip`, Act I villager and named-NPC builds)

## Done
- **Pipeline extensions** (all optional params keys; defaults leave every earlier villager byte-identical, verified on
  `villager_vendor` and `villager_reed` on the three numpy paths):
  `villager_costume` `top.cuff_roll_m`, `apron.over_trousers` / `flare` / `extra_m`, a fifth cloth slot `cloth_d`;
  `villager_textures` `_skin.body_size`, `_skin.line_marks` (liss_textures' generator); `write_materials` `_cloth_params`;
  `villager_clips` reads `villager_story_clips.json` (hero_clips' story vocabulary, a villager `kneel_both` and
  `all_fours` posture, a posture `path`); `build_villager.clear_teeth_strip` (a head skin pack that lands on the teeth's
  authored UV strip is scaled clear of it; it showed the teeth on the scale-man's temple).
- **Generic Act I villagers** (before the Lead's re-split; built, wired, committed): shopkeeper, smith, innkeeper (M3-CHR-512,
  516, 517), the Order clerk (509), four Reeds (510), the Saltwright girl and two children with line-marks (511). Tasks at
  `review` with a re-split note. M3-CHR-518 `blocked`: the Prologue's Vigil3..7 are the party (act_outline), not villagers.
- **Named Act I NPCs** (M3-CHR-526..539, `review`): sabe, scaleman, skipper_sadi, ferrymaster (Imbe), purser, elder, garo,
  tender (Ruwen), ione, poolkeeper, fenn, gatekeeper, hobb, marra. Each: params, a `villager_<id>` job, PROVENANCE rows, the
  import rule, a rig_checks entry with ratchets and a test_rig_integrity class, a stage scene, face poses, `_front` and
  `_face` shots (no baselines written). Ivo filed as M3-CHR-540 (a Stillguard variant; no armour on this pipeline).
- M3-CHR-519 notes list every actor scene for the level owners.

## In progress / next step
- The final three-path verify chain (scratch `verify_named.sh`) covered vendor, reed, reed_a, reed_c and the 14 named jobs;
  the 11 generic jobs passed native, X86_V4 and X86_V3+V4 earlier (reed_a and reed_c failed X86_V3+V4 only while the first,
  over-broad teeth check was in the tree, and are in the final chain). **Exact next step:** the Lead runs
  `tools/ci_local.sh` with the new shots on the integration branch and writes their baselines after viewing them.

## Known issues
- The smith's and Garo's rolled cuffs barely read (the sleeve tube's last row); Garo's forearm burn scars and the
  pool-keeper's chalky fingers are not painted; Marra's netting shawl and wrist cord, Hobb's cord knots are not modelled.
- Wright line-marks are sub-pixel in full-body shots (they need a close camera).
- Existing villagers at dialogue distance: Osu's (and Marra's) head wrap shows a dark band at the brow edge; Tavi's
  headband sits high and wide with hair poking above it; Neme's hair specular reads as light streaks.
- Rig-probe ratchets are linear-skinning limits recorded at their worst poses, not each viewed.

## Files
`assets_src/characters/villagers/**` (modules, params, villager_story_clips.json), `assets/characters/villagers/<35 ids>/`,
`assets/PROVENANCE.md`, `game/data/import/characters.json`, `game/levels/_tests/characters/villagers/`,
`tests/screenshots/shots.json`, `tools/dev/blender_builds.json`, `tools/dev/rig_checks.json`, `tools/tests/test_villagers.py`,
`tools/tests/test_rig_integrity.py`, `docs/kb/tasks/M3/M3-CHR-509..540`.
