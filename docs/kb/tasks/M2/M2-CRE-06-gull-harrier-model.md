---
id: M2-CRE-06
title: "Gull harrier: final battle model and clips"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M2
request-from: lead
---
## Goal
The gull harrier from its design sheet, through the creature pipeline.

## Acceptance criteria
- [x] See Goal; notes below record what shipped.

## Notes
**Shipped (2026-10-24):**
- `assets_src/creatures/gull_harrier/build_gull_harrier.py` + `materials.json` →
  `assets/creatures/gull_harrier/gull_harrier.glb` (0.70 MB, **8,878 triangles**, 17 bones) and four slots
  (`plumage`, `beak`, `eye`, `wrack`). Blender job `creature_gull_harrier` (`verify_blender_builds.py` identical),
  PROVENANCE rows, import rule folder, `game/creatures/gull_harrier/gull_harrier_battle.tscn`, creatures.json row,
  enemies.json `model`.
- **Size and hover.** The origin is the hover point (stand-in hover 1.05, height 0.45): the body sits from y 0.05
  to 0.43 (0.44 with the brow and scapulars), the beak's hook reaches z 0.72, the tail z −0.58, and the wings span
  2.49 m tip to tip.
- **Build.** A lofted body (tail to face, one piece; grey mantle, white head and underparts with winter nape streaks
  and an eye smudge, a salt stain under the vent). Wings on shoulder/elbow/wrist chains: an airfoil covert loft plus
  real-geometry two-sided feather blades (no alpha): 10 primaries, 7 primary coverts, 12 secondaries, 3 tertials,
  12 greater and 10 median coverts, 4 scapulars per wing. The crooked "M" is in the bind pose (arm up to the
  wrist, hand down). Primaries carry storm_slate tips (on both faces), white mirrors on P9/P10, sun-faded and
  cut ragged tips; the right (camera-side) wing has a broken P7. White trailing edge on the secondaries. Heavy
  hooked beak (upper mandible curls into a tortoiseshell hook; the lower mandible is the `beak` bone, with a gonys
  spot). Small black eye with a sun_gold ring under a brow ridge. Fanned 11-feather tail. Legs tucked, webbed
  feet with hooked claws. A hank of three net-twine strands, knots, two net ties and two wet kelp ribbons on the
  right foot (a 3-bone chain). The bone hook in the throat with its lashing and a line hanging out; the wound
  (spawn_wound, pulsing emission) is a lip mesh plus a soft emission falloff on the throat.
- **Clips** (all per the sheet): `idle` 1.6 s loop (top of the upstroke, a deep downstroke with the body rising
  6 cm, a glide in the "M", a flexed upstroke; the neck counter-moves so the head holds still; the twine lags),
  `attack` 1.4 s (two quick climbing beats to +0.6 m, half fold and tip over, drop forward and down, talons swing
  forward and rake at **0.75 s** with the wings flared and the beak snapping, swing back up), `cast` 1.2 s (rears
  38°, wings spread high and held, beak open), `hit` 0.6 s (the near wing buckles, the far one flails, drops 0.25 m
  and rolls, beats and recovers), `ko` 1.4 s (wings jerk up, fold and sweep up in the fall, root −1.05 m; lands on
  its breast with the beak on the sand, the far wing left spread and raised, the near wing crumpled on the ground,
  the twine laid out; holds). Measured with a numpy pose of the KO end: breast 1 cm and hook tip 2 cm into the
  ground, no wing below it.
- **Facing.** creatures.json `stand_in.yaw_deg` is **60**, not the default 90. From the battle camera at 90 the
  wingspan points almost straight at the lens and the glide reads as a body with a stub; at 60 the full "M" reads
  and the bird still faces and dives at the party. The design sheet's "Facing" line is corrected to match.
- **Mantle.** cumulus_shadow deepened 45% toward overcast_slate (sheet corrected): pure cumulus_shadow went
  near-white under the noon key and the grey-wing/white-body read was lost.
- Review sheets (scratch, not committed): battle-camera views at yaw 60 of idle, attack, hit, cast and KO, plus
  head, feet and fold close-ups.

**Honest weaknesses:**
- Feathers are rigid per bone, so a full fold splays the secondaries. The clips avoid a full fold (the dive and
  the fall use a swept-back half fold, and the KO crumples the near wing), but a review of a mid-fold frame from
  above will show the covert rows fanning.
- From above, the covert rows read slightly scaly (regular rows, hard shadow teeth on their trailing edges) up
  close. At battle distance they read as plumage.
- The head is a smooth loft. It is good at battle distance; up close the crown is a little blobby and the eye is
  a touch round and staring, even with the brow.
- The twine hank hangs fairly straight down in the idle. From some angles it can read as a dangling leg.
- **Kit finding (not fixed: `common/` is shared):** `creature_kit.ellipsoid` and `creature_kit.tube` wind their
  triangles inward. Their right-hand normals point into the shape, the opposite of the lofts, which render
  correctly. The gull's eyes rendered invisible (back-face culled) until this build wrapped both primitives with
  an outward re-wind (`_ellipsoid`, `_tube`). The reef crab uses both unwrapped (eyes, legs, claws, mouthparts), so
  those parts are probably rendering their inner faces with inverted lighting. A kit fix reruns every creature's
  job, so it needs its own task.

## Review log
