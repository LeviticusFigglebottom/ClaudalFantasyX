# Handoff — character (Pell, M3-CHR-506) — 2026-10-28 #1

Worktree `/home/user/pell-wt`, branch `chr-pell-wip` (from `claude/characters`). Not pushed (the characters session
merges it). Task status: `review`, reviewer `rendering`.

## Done
- **Head proof, then the build:** `pell_head.kirru_warp` on the MPFB2 donor head (landmarks re-read after the warp, the
  40 shapes on the warped face, the clay face and 15 poses viewed first). `build_pell.py` + `pell_costume.py`,
  `pell_fur.py`, `pell_props.py`, `pell_textures.py`, `write_materials.py`, `build.sh`; params in `pell_params.json`.
  LOD0 46,982 tris / 4.09 MB (4,086,316 B), LOD1 27,320 tris / 1.33 MB (crest baked at the battle `battle_raise` 0.3), 14 textures
  (largest 3.90 MB), 21 materials (fur, wet, crest, whisker, dialogue finish).
- **States:** `NameShellBlank` / `NameShellCarved` with `PellNameShell.apply(root, carved)`
  (`game/characters/heroes/pell_name_shell.gd`, `tests/unit/test_pell_name_shell.gd`); the Ch8 wet materials and the
  Crest's `crest_flat` key.
- **Clips:** the Pell block of `assets_src/characters/asha/hero_clips.py` (persona keys `neck_s`, `staff_side`,
  `staff_arm`; story clips; the battle contract with his own ko and revive; the left-hand grip). Every other hero's
  library rebuilds byte-identical.
- **Battle actor** `game/characters/heroes/pell_battle.tscn` (LOD1, the blank shell showing).
- **Review stages and 14 shots** under `game/levels/_tests/characters/pell/` (+ `hide_nodes` on `asha_stage.gd`),
  self-rendered and viewed (no baselines). `docs/kb/art/characters/pell_review.md` is the strict assessment.
- **Guards and data:** `rig_checks.json` `pell` with pinned allowances; `blender_builds.json` job `pell`;
  `tools/tests/test_pell.py`; `TestRigIntegrityPell`; Pell in `test_hero_clips` and `test_hero_battle_clips` (the
  yield test now names Moll only); PROVENANCE rows; request tasks M3-BPR-1340 (framing) and M3-CIN-1240 (crest-led
  face poses).

## In progress
- Nothing half-done in the tree. A look-dev pass followed the coordinator's review (head reshaped onto an otter-like
  Kirru head surface, soft fur with standing outline fur, the split reed girdle, the crest skinned, stronger face
  shapes, storm_call's palm on the throat); see the task notes and pell_review.md. The art is closer, not final.

## Exact next step
1. The characters session merges `chr-pell-wip` into `claude/characters` and asks the PC/Lead to render and view the
   14 `pell_*` shots (`HYMN_SHOTS=pell_front,pell_back,pell_three_quarter,pell_profile,pell_face,pell_face_stylized,
   pell_face_surprised,pell_face_grief,pell_silhouette_lineup,pell_clip_storm_call,pell_clip_walk,pell_battle_idle,
   pell_battle_attack,pell_storm_ch8`).
2. Rendering reviews `pell_review.md`'s "What does not read yet" and decides: (a) the face (a stronger brow and
   cranium warp in `pell_head.kirru_warp`, or the §9 ADR for a non-donor head), (b) the fur sheen lobe (pell.md §12 Q8).
   Then a look-dev pass on the face and fur, re-rendering the face and front shots.

## Known issues
- After the look-dev pass: the eyes keep the donor's almond lids, the ears are small human ears, the fur is soft but
  uniform at full figure, the right hand is open in storm_call, and the nape has a soft ridge (pell_review.md).
- Rig allowances are large in the ko/revive squat and with the right arm across the chest (cast, storm_call); see
  `_allowances` in `rig_checks.json`.
- The finisher's staff leans about 30° (staff_hold's wrist limit), so its sweep runs a hand above the floor, not at
  knee height.
- The raw GLB rest pose holds the staff near horizontal across his body (as Asha's); every animated use stands it up.

## Files touched
`assets_src/characters/pell/**`, `assets/characters/pell/**`, `assets_src/characters/asha/hero_clips.py`,
`game/data/characters/grips.json`, `game/data/import/characters.json`, `game/levels/_tests/characters/asha/asha_stage.gd`,
`game/levels/_tests/characters/pell/**`, `game/characters/heroes/pell_battle.tscn`,
`game/characters/heroes/pell_name_shell.gd(.uid)`, `tests/unit/test_pell_name_shell.gd(.uid)`,
`tests/screenshots/shots.json`, `tools/dev/blender_builds.json`, `tools/dev/rig_checks.json`, `tools/tests/test_pell.py`,
`tools/tests/test_hero_clips.py`, `tools/tests/test_hero_battle_clips.py`, `tools/tests/test_rig_integrity.py`,
`assets/PROVENANCE.md`, `docs/kb/tasks/M3/M3-CHR-506-pell-hero.md`, `docs/kb/tasks/M3/M3-BPR-1340-*.md`,
`docs/kb/tasks/M3/M3-CIN-1240-*.md`, `docs/kb/art/characters/pell_review.md`, `docs/kb/handoffs/live/characters.md`.
