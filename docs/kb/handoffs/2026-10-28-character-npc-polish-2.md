# Handoff — character (NPC dialogue polish 2, worktree `chr-npc-polish2`) — 2026-10-28 #2

## Done
The three items polish 1 left, each behind an optional key whose default leaves every other villager (and every hero)
byte-identical. Rendered before and after at dialogue range (`villager_<npc>_face`, and `_front` for the tops), viewed,
iterated; each changed job verifies identical on the three numpy paths, and the shared code verifies natively on every
job that imports it.

1. **The tank cut** (Sabe M3-CHR-526, Ione M3-CHR-534): `_costume.top.armhole_cut: "tank"` in villager_costume. The
   default sleeveless line rises front and back to points beside the neck with nothing over the shoulder (the halter).
   One TorsoChart line cannot hold a strap over the shoulder (the crest and the armpit lie on the same azimuths: that is
   why widening the chart's straps, as polish 1 tried, put cloth on the deltoid), so the tank cut is two pieces: the
   panel (104 columns) with a scoop neck, the default armhole floor, and a foot under each strap (as high as the strap's
   6th row at its inner edge, its 2nd at the outer, so no chart ray exits through the shoulder cap), plus `TopStrapL/R`,
   a grid cast over the shoulder crest in the side plane from the chest to the back (`tank_straps`; x 0.40-0.60 of the
   acromion's half-width; the sleeves' free atlas islands; build_villager weights them from the torso, TORSO_PIECES).
   Rig probe: Sabe Body 49.27 -> 0.56 mm, max_exposed 0 (ratchets back to the defaults, Costume 33/6 unchanged); Ione
   Body 58.11 -> 57.18 (59/5 -> 58/2), max_exposed 0. Both read as an ordinary sleeveless top at the face and front shots.
2. **The feathered hairline** (Sabe, Ione, Hobb M3-CHR-538): asha_textures `HAIRLINE_FEATHER` (0 = off, the heroes'
   default; the old branch is untouched), set by villager_textures from `_hair.hairline_feather` and restored after: the
   painted edge wanders by HAIRLINE_BREAK_AMP over a fine fbm (tufts and gaps), the ramp is longer, and the outermost
   strands are fewer and thinner. The blunt painted line is now a broken, strand-edged hairline.
3. **Old villagers' brows** (Fenn M3-CHR-536, Marra M3-CHR-539, Osu M3-CHR-519; Sabe too, same defect):
   `_skin.brow_strands` paints single wiry hairs on the brow skin in asha_eyes.brow's own frame (`brow_frame` builds the
   brow on a flat stand-in surface), a third dark among the grey, a few strays; `_hair.brow_params` (write_materials)
   lightens the brow cards (`alpha_boost` 1.0, `strand_value_jitter` 0.4) so the painted hairs show. A material-only
   pass (alpha and jitter) was tried first and was not enough: the band only faded.

Tests: tools/tests/test_villagers.py `TestDialoguePolish2` (opt-ins, the straps cross the crest inside the acromion and
the armhole floor is the default's, the feather is off for the heroes, the brow hairs paint only round the brows and are
deterministic, brow_params reach only the brow material).

## In progress
Nothing.

## Exact next step
The Lead merges `chr-npc-polish2` and renders the face and front shots of sabe, ione, hobb, fenn, marra and osu (no
baselines written here; those shots change).

## Known issues
- Ione's front shot: the panel's sides stand out under the arms like short cap sleeves (unchanged by this pass; the
  torso chart at the armhole floor on her build). The straps read correctly.
- The straps' lower ends lie over the panel with a faint visible edge in the front shot (reads as a sewn strap).
- Ione's fringe: the card tips still show as short dark dashes at the hairline (the cards, not the paint).
- Marra's and Sabe's brow cards zigzag in their geometry (asha_eyes.brow seated on the skin); at the lighter alpha the
  painted hairs carry the read, but the zigzag is still faintly there.

## Verification
- `verify_blender_builds.py` on villager_sabe, _ione, _hobb, _fenn, _marra, _osu: identical natively, with
  `NPY_DISABLE_CPU_FEATURES="X86_V4"` and with `"X86_V3 X86_V4"` (30-31 files each).
- Native verify of every other job that imports the touched shared code: the other 28 villager jobs and the heroes
  (asha, rhen, toma, sefir, ysolde, liss, kerrid, moll, stillguard, ivo): 38 jobs, all identical.
- `rig_probe` / `test_rig_integrity` for Sabe, Ione, Hobb, Fenn and Marra (Osu has no rig entry): pass at the lowered
  Sabe and Ione ratchets. `python3 -m unittest tools.tests.test_villagers` (45 tests), `tools/validate_data.py`,
  `tools/taskboard.py --check`. `tools/run_tool_tests.py -j 4`: 1841 tests, six units fail outside this diff
  (test_audio_loudness: ffmpeg cannot decode an act2 .ogg here; test_arenas, test_pemakar_kit, test_zone_dressing_ch01,
  test_zone_map_pois: kit and zone sources; test_screenshots: no baseline for villager_shopkeeper_front); none reads a
  villager source, rig_checks or asha_textures.
- Renders (lavapipe, scratch only, no baselines): villager_{sabe,ione}_{face,front}, villager_{hobb,fenn,marra,osu}_face,
  before and after. No Godot code changed, so no Godot test run; the .import files Godot rewrote were discarded.

## Files touched
assets_src/characters/asha/asha_textures.py (opt-in HAIRLINE_FEATHER), assets_src/characters/villagers/
{villager_costume,build_villager,villager_textures,write_materials}.py, params for sabe, ione, hobb, fenn, marra, osu,
their assets/characters/villagers/<npc>/ outputs, tools/dev/rig_checks.json (sabe, ione), tools/tests/test_villagers.py,
the task files M3-CHR-526/534/536/538/539.
