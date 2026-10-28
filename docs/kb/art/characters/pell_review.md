# Pell: Self-Render Review (M3-CHR-506)

**Render:** self-rendered in the characters worktree `chr-pell-wip` (cloud lavapipe, Forward+ on llvmpipe, 960×540,
`HYMN_SHOTS` limited to the 14 Pell shots), viewed 2026-10-28. **No baselines written**; the Lead or the PC renders and
approves them. Judged strictly against SPEC §14's first risk ("procedural characters look uncanny or low quality") and the
§1 pillars, pell.md §2 (echo watch) and §11 (acceptance).

**Verdict: not yet at final quality.** The build, rig, clips and guards are complete and reproducible, and the figure
reads as Pell in silhouette and motion. At dialogue range the face and the fur still read as a carved, furred human, not
as a Kirru. The work below is listed for the reviewer (Rendering) and the next look-dev pass; none of it blocks merging
the build, but the face and fur should not be approved as final art.

## What reads
- **Silhouette (pell_silhouette_lineup):** the tallest in the cast by a head and a neck, the long neck and the narrow
  shoulders unmistakable beside Asha, Rhen, Toma, Ysolde, Liss, Kerrid and Sefir. (The raw GLB's rest pose holds the
  staff near horizontal across the body, as Asha's does; every animated use stands it upright.)
- **The staff in the left fist** (front, back, three-quarter, battle_idle): upright beside the left foot, the fist
  closed on it (M2-CHR-515/544 grip), the foot on the floor, the barbed tip and the stone in its net visible.
- **Battle idiom (pell_battle_attack):** the dart reads as a downward, forward thrust of the barbed tip to knee height,
  both hands on the shaft, the knees given. Not a levelled lance, nothing twirled, both feet down.
- **The mantle, cords and gear:** the straw chevron plait reads at full figure; the mantle sits on the right shoulder
  and chest with its arm edge 12 cm under the joint; the toggle cord passes under the left arm; the bone line coil at
  the right hip and the pouch behind the left hip read; the tile wraps on both forearms read as small bright tiles.
- **Name-shell:** one state at a time (the blank one), on its throat cord, in front of the cream throat stripe.
- **Crest:** after this pass's denser vane, the crest reads as a white feather plume at the face distance
  (pell_face_stylized) and flattens under the wet `crest_flat` 1.0 in pell_storm_ch8.

## What does not read yet (strict)
1. **The face is a muzzled human face, not an otter-heron.** The warp gives the muzzle, the nose pad and the whisker
   pads (pell_head proof), but the brow, the eye sockets and the cheeks keep the donor's human planes, and the ears are
   small and set low. At dialogue range (pell_face) he reads as a man with a snout. Next: a stronger cranium and brow
   flattening in `pell_head.kirru_warp` (lower the brow ridge into the forehead slope, widen the zygomas back toward
   the ears), the ears raised and rounded, and a darker, glossier nose pad. This is the sheet's own warning (§9: an ADR
   for a non-donor head if the donor cannot carry the muzzle) and should be decided by the reviewer.
2. **The fur reads as wood grain at mid range.** This pass added strand streaks and clumps to the albedo, Asha's
   thread detail normal in place of the pore normal, and a rougher, less specular response; it now reads as fur up
   close (pell_face) but as a varnished carving at full figure. Next: Rendering's sheen lobe along the flow (pell.md
   §12 Q8), a softer silhouette fringe (the 8-14 mm cards hardly show at full figure), and a broken saddle edge.
3. **He reads unclothed.** The sheet's "no lower garment" (§4.2, carried with its default) plus a smooth groin and a
   skin-like fur makes the full-figure shots read as a nude mannequin, which undercuts the sincerity pillar. The fur
   fixes above carry most of it; if they do not, Narrative/Art should revisit §12 Q3 (a fur ruff or a hip wrap).
4. **The face poses are faint.** surprised and grief move the brows and lids, but on the warped face the change is
   small at the face shot's distance; the crest (which "speaks first") is out of the face camera's frame. Next: frame
   the face shot to include the crest, and raise the brow shapes' gain on the warped head.
5. **storm_call's hand** lands on the upper chest under the left collarbone more than on the throat, and the mantle's
   cap shows its underside at the right armpit when the arm crosses (the rig guard's Body allowance, 65 mm there). The
   elbow is now kept 22 cm under the shoulder (it was 2 cm, 93 mm through the cap).
6. **The whiskers** are thin silver lines at the face distance (now 2.6 mm cards); they read only against the dark
   background side.

## Rig guards and determinism
- `rig_probe --hero pell` passes with the allowances in `tools/dev/rig_checks.json` (`_allowances` there gives each one
  and its pose): the worst are the ko/revive squat (the neck bowed 125° to the floor) and the right arm across the chest
  (cast, storm_call). The idle, walk, talk and the story stands are inside the defaults except the shell cord's few mm.
- The build is byte-identical on three numpy paths (`verify_blender_builds.py --job pell`, see the task notes).

## Shots viewed
pell_front, pell_back, pell_three_quarter, pell_profile, pell_face, pell_face_stylized, pell_face_surprised,
pell_face_grief, pell_silhouette_lineup, pell_clip_storm_call, pell_clip_walk, pell_battle_idle, pell_battle_attack,
pell_storm_ch8 (three rounds: before and after the mantle/fur/crest fixes).
