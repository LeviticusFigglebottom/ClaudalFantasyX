# Pell: Self-Render Review (M3-CHR-506)

**Render:** self-rendered in the characters worktree `chr-pell-wip` (cloud lavapipe, Forward+ on llvmpipe, 960×540,
`HYMN_SHOTS` limited to the 14 Pell shots), viewed 2026-10-28, before and after the look-dev pass that followed the
coordinator's review of the first build. **No baselines written**; the Lead or the PC renders and approves them. Judged
strictly against SPEC §14's first risk ("procedural characters look uncanny or low quality"), the §1 pillars, pell.md §2
(echo watch) and §11 (acceptance).

**Verdict: much closer, not yet final.** He now reads as a Kirru: an otter-like head on a long, thick neck, furred, in a
reed mantle and girdle. The face is the weakest part at dialogue range (below).

## Before and after the look-dev pass
| | Before (first build) | After |
|---|---|---|
| Head | A human skull and face with a muzzle pushed out of it: tall cranium, human brow, sockets and jaw | A broad, low skull (crown 7 cm lower) with small eyes set high and wide, a short broad muzzle out of the skull line with a dark nose pad and whisker pads, full jowls into a thick neck. Reads as otter/weasel in profile and three-quarter. |
| Fur | Long, high-contrast streaks: wood grain at full figure | Fine, soft, low-contrast fur; the outline (upper arms, back of the neck, hips, thighs, calves, left flank) broken by short standing fur cards |
| Lower body | Read as unclothed (a smooth human body, no garment) | The split reed girdle of pell.md §4.2's fallback (§12 Q3's default overridden on review) |
| Crest | Floated off the head in every clip (exported unskinned) | Rigid on the head; reads as a white plume, raised in surprise, flat in grief and in the Ch8 rain |
| Face poses | Faint | Brows, lids and cheeks scaled up on the Kirru head; the face shot frames the crest, which leads |
| storm_call | Hand on the upper chest; the arm through the mantle's cap (93 mm) | Palm up the throat, elbow tucked (the cap allowance 78 mm) |

## What reads
- **Silhouette (pell_silhouette_lineup):** the tallest in the cast, the long thick neck, the head's wedge and the crest
  unmistakable; the outline fur softens his edges.
- **The staff in the left fist**, upright beside the left foot; the battle dart thrusts the barbed tip down and forward,
  never levelled.
- **Costume:** the mantle on the right shoulder and chest, the toggle cord, the tile wraps, the belt with the pouch and
  the line coil, and now the girdle, which splits as the legs move (battle_attack, clip_walk).

## What still does not read (strict)
1. **The eyes keep the donor's almond lids** and a dark lid line, so at dialogue range they read as human eyes set in an
   otter's head. Next: round the lid contour (pell.md's `eye_roundness` 0.7 is not yet used by the shared eye frame) and
   darken the whole eye ring instead of the lid line.
2. **The ears are small human ears**, scaled and set back. An otter's ear is a small rounded flap. Next: flatten and
   round the donor ear in the warp, or replace it with a small rounded card.
3. **The fur is soft but still uniform at full figure**: the saddle-to-belly pattern of §5 barely shows under the warm
   key light, and the body reads smooth between the outline cards. Rendering's sheen lobe along the flow (§12 Q8) is
   still the missing piece.
4. **The right hand is open** in storm_call (no finger pose on the free hand), so the palm on the throat reads as a spread
   hand.
5. **The back of the head and the nape** keep a soft ridge where the reshaped head meets the thickened neck (profile).

## Rig guards and determinism
- `rig_probe --hero pell` passes with the allowances in `tools/dev/rig_checks.json` (`_allowances` gives each one and its
  pose): the worst are the ko/revive squat and the right arm across the chest (cast, storm_call).
- The build is byte-identical on three numpy paths (`verify_blender_builds.py --job pell`, see the task notes).

## Shots viewed
pell_front, pell_back, pell_three_quarter, pell_profile, pell_face, pell_face_stylized, pell_face_surprised,
pell_face_grief, pell_silhouette_lineup, pell_clip_storm_call, pell_clip_walk, pell_battle_idle, pell_battle_attack,
pell_storm_ch8 (the first build in three rounds; the look-dev pass after each of its four steps).
