# Handoff — character (NPC dialogue polish, worktree `chr-npc-polish`) — 2026-10-28 #1

## Done
The named Act I villagers, polished at dialogue distance (the `villager_<npc>_face` shots), one commit per NPC in the
Lead's story order: hobb, fenn, marra, tavi, neme, ione, osu, sabe, garo, reed, skipper_sadi, ferrymaster, elder,
gatekeeper, poolkeeper, purser, scaleman. Each job verifies byte-identical on the three numpy paths (native,
`NPY_DISABLE_CPU_FEATURES="X86_V4"`, `"X86_V3 X86_V4"`). What changed is in each task file's notes (M3-CHR-526..539,
M3-CHR-03 for Tavi, M2-CHR-03 for Neme, Osu and the chapel Reed).

New optional keys (defaults leave every other villager byte-identical; a native verify of every villager job confirms it):
- `villager_hair`: `_hair.grey_strands` (true: grey cards on sparse atlas columns, `grey_width_k` as wide; `"all"`:
  every card, for thin white hair). Solid grey cards were the white chips on most greying villagers.
- `villager_textures`: `_skin.stubble_shadow` and `stubble_density` (a soft beard shadow under the stubble),
  `_skin.burn_scars` (Garo's healed forearm burns) and `_skin.fingertip_chalk` (the pool-keeper's chalky fingers).
- `villager_costume`: `sash.tail_w_k`, `knot_k` and `cord_knots` (Hobb's three-knot cord), `headwrap.edge_off_m` (a
  wrap's or headband's edge drawn in to the skin: the dark band under the wraps and the floating headbands), and
  `headwrap.press_hair` (build_villager presses the hair under a headband inside it), plus two pieces: `shawl` (twine
  netting) and `wrist_cord` (Marra's).
- Data only: `_hair.spec` dimmed on the black-haired villagers (the warm highlight chips), `_cloth_params` on Sadi's black
  band.

Also rebuilt: shopkeeper, smith, clerk and reed_d. Their committed head albedos were stale against M2-CHR-524's
beard-lens change in toma_hair (the jobs failed verify on the base commit too); a plain rebuild with no source change.

## In progress
Nothing.

## Exact next step
The Lead merges `chr-npc-polish` and runs the full screenshot manifest. No baselines were written here; the face and front
shots of these NPCs change.

## Known issues
- Sabe's and Ione's sleeveless tops still cut in like a halter. A cap sleeve and broader shoulder straps were both tried.
  Both broke the rig-integrity ratchets (holes at the shoulder, or the upper arm through the cloth in the walk), so the
  cut needs its own garment-fit pass.
- Short and cropped hair still ends in a fairly blunt line at the fringe (Ione, Sabe, Hobb). The hairline underpaint's
  hard edge is in asha_textures, which is shared with the heroes.
- Painted brows on the old villagers (Fenn, Marra, Osu) read as a flat smear up close.

## Files touched
assets_src/characters/villagers/{build_villager,villager_costume,villager_hair,villager_textures}.py, params for the 17
NPCs, their assets/characters/villagers/<npc>/ outputs, the four stale head albedos, tools/tests/test_villagers.py
(TestDialoguePolish), and the task files.
