---
id: M4-CRB-008
title: "Ethren, the Glimmer Vowbound, at final quality: audit, a clip per skill, every clip from idle, anchors, contacts"
role: character
status: review
owner_session: creatures-b
depends_on: [M3-CRE-644, M3-CRE-647, M3-CRB-015]
reviewer: combat
milestone: M4
---
## Goal
ADR 0205 starts Act II for creatures-b. Bring Ethren (Corran Ysel, the 60th Cantor, bound in Ansedra's Sanctum in
Ch13; docs/kb/plan/act2/bosses/ethren.md, ADR 0204: Still Water is Stop on every foe) to the Act I Vowbound final bar
(ADR 0041 §3, M3-CRB-013's move pass): seen from the party side of the battle camera on the `vowbound_slot` and up
close. ADR 0015: nothing about him is frozen; stillness is shown by not moving, never by ice. The veil stays (its fall
is Act III's).

## Acceptance criteria
- [x] Audited from the battle camera (party Vowbound slot, an Act I arena) and up close; see the art sheet's "As
  built (M4-CRB-008)". He read as a stack of plain cones under a white lampshade and a blank white plate. Fixed: the
  seams and halo show teal light (not white), the halo is a lit bowl with a red inner rim, the veil hangs from a red
  crown cap in soft pleats with the face dark behind thin gauze, the robe bells nest (the middle bell's hem stood
  through the bottom bell) with lacquer bands and gold panel rims, and each wing leaf carries a hard-edged inset
  panel on both faces. In budget: 15,546 triangles of 16k, 29 bones, the same seven slots.
- [x] The look re-checked: portraits `ethren` and `ethren_held` re-baked.
- [x] The Vowbound contract clips (`idle`, `ready`, `rise`, `dismiss`, `attack`, `cast`, `hit`, `hit_b`, `defend`,
  `ko`, `victory`, `special`, the held form's `release`) plus one clip per skill on the sheet: `stop` (Hold the Hour,
  contact 0.9 s) and `ward` (the lacquer screen, 0.8 s). Every wind-up is ≥ 0.45 s.
- [x] Every clip is played from idle's first frame (rise starts kneeling, as the call); nothing under the water.
- [x] Unweighted anchors `vfx_core` (the breastplate, `spine_2`) and `vfx_keepsake` (the copper ring, `finger_l1`).
- [x] creatures.json `contact` for `stop` and `ward` on `ethren` and `ethren_held`. No `clip_by_skill`: his skills
  aren't in skills.json yet (M4-A2P-024). The ready-to-paste map is in both sheets.
- [x] tests/unit/test_creature_vowbound_act2.gd (`test_ethren_...`): the clip set on both forms, wind-ups, anchors,
  every clip from idle's first frame, Hold the Hour's still hand and its closing, the screen swinging forward.

## Notes
- The clip map for combat (paste into `ethren` in creatures.json once the skills exist; the ids are the design
  sheet's proposals): `"clip_by_skill": {"level_hand": "cast", "hold_the_hour": "stop", "lacquer_screen": "ward",
  "still_water": "special"}`. The basic attack plays `attack` by kind.
- Still Water's whole-field stop at the contact (1.45 s) is battle-presentation's (the freeze read) and the battle's
  own (Stop on every foe, ADR 0204); Hold the Hour's foe freeze at 0.9 s is presentation too.
- Open: the veil's face shading reads only from the front (the party side sees it edge-on); `ward`'s near leaf
  crosses his robe toward the battle camera for 0.3 s (battle-presentation may frame it); Hold the Hour's closing hand
  is small at battle distance, so the foe's freeze VFX carries the read.

## Review log
- 2026-10-30, creatures-b: viewed every clip at five beats from the party side of the battle camera (the Cinder
  Matron's forge, `vowbound_slot`), the head close-ups, the `creature_ethren` and `creature_ethren_held` review shots
  and both portraits; `verify_blender_builds --job creature_ethren`: 15 identical. Ready for combat's review.
