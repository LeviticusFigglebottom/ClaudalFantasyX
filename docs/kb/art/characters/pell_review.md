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

## Second look-dev pass (2026-10-29, claude/characters @ 2c2acb54)
Self-rendered all 14 `pell_*` shots on cloud lavapipe and viewed them, with close crops of the eyes, the hand and the
nape. **No baselines written.** Against "What still does not read" above:

| # | Was | Now |
|---|---|---|
| 1 | Almond lids with a dark lid line: human eyes in an otter's head | The opening is rounder (`_kirru.otter_head.eye_round`: 0.72 along the fissure, 1.6 across it, scaled inside the warp so the blink and the expression units follow), a soft dark fur ring round each eye, and a dark wet margin (Pell's own `tear_line` colour; the shared one is a pink human lid). At dialogue range they read as small round dark eyes. |
| 2 | Small human ears | Drawn round and laid against the skull (`_kirru.ear_shape`). At this size they barely show, as an otter's do. |
| 3 | Uniform fur at full figure | A darker saddle (`#30241D`) against a lighter, greyer mid brown (`#6A5444`); stronger body clumps and relief. The back view now shows the saddle down the spine and the outer limbs. The cream throat stripe's edge is soft and broken (it read as a painted bib). Still no sheen lobe along the flow (§12 Q8, Rendering's). |
| 4 | The right hand open in storm_call | The fingers close together beside the middle finger with a slight curl, the thumb in along the index (`hero_clips` FLAT_HAND), in storm_call and in cast's call: a flat palm on the throat. |
| 5 | A ridge where the head meets the neck | The upper neck is thicker (`neck_scale` 1.3 -> 1.5), so the back of the skull no longer overhangs it. A small knob remains behind the ear line in profile. |

**Still open:** the head's skin reads smooth up close (the fur is in the maps, not in the silhouette, except the
outline cards); the face is a warm orange under the warm key; the profile's small knob at the back of the skull; the
body is still lean and smooth between the outline cards at full figure (more cards would pass the 5 MB GLB cap:
pell.glb is 4.79 MB). These are the next look-dev steps if the Lead or the human still reads them.
