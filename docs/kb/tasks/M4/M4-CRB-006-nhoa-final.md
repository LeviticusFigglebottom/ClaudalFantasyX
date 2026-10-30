---
id: M4-CRB-006
title: "Nhoa, the Ice Vowbound, at final quality: audit, a clip per skill, every clip from idle, anchors, contacts"
role: character
status: review
owner_session: creatures-b
depends_on: [M3-CRE-642, M3-CRE-647, M3-CRB-015]
reviewer: combat
milestone: M4
---
## Goal
ADR 0205 starts Act II for creatures-b. Bring Nhoa (Ressa, Pell's clutch-sister, bound under Sunken Vey in Ch11;
docs/kb/plan/act2/bosses/nhoa.md, ADR 0204: her copy takes ordinary skills only) to the Act I Vowbound final bar
(ADR 0041 §3, M3-CRB-013's move pass): seen from the party side of the battle camera on the `vowbound_slot` and up
close. Ice is hers alone in Act II (ADR 0015), and nothing about her is frozen.

## Acceptance criteria
- [x] Audited from the battle camera (party Vowbound slot, an Act I arena) and up close; see the art sheet's "As
  built (M4-CRB-006)". Fixed: crystal-like faceted beads (ADR 0015), a glossy body (the sheet says dry), a smooth
  tube of a neck up close, and the KO lowering the crowns at the foes. In budget: 15,672 triangles of 16k, 30 bones.
- [x] The Vowbound contract clips (`idle`, `ready`, `rise`, `dismiss`, `attack`, `cast`, `hit`, `hit_b`, `defend`,
  `ko`, `victory`, `special`, the held form's `release`) plus one clip per skill on the sheet: `deep_well` (contact
  1.0 s) and `echo` (0.65 s). Every wind-up is ≥ 0.45 s. Farewell-Tide lifts her 0.2 m with the strands drawn up.
- [x] The look re-checked: portraits re-baked.
- [x] Every clip is played from idle's first frame (rise starts folded, as the call); nothing under the water (lowest
  0.05 m, the KO's strands; Deep Well 0.10 m).
- [x] Unweighted anchors `vfx_core` (chest, `spine_2`) and `vfx_keepsake` (the name-shell, `neck_0`).
- [x] creatures.json `contact` for `deep_well` and `echo` on `nhoa` and `nhoa_held`. No `clip_by_skill`: her skills
  aren't in skills.json yet (M4-A2P-024). The ready-to-paste map is in both sheets.
- [x] tests/unit/test_creature_vowbound_act2.gd (`test_nhoa_...`): the clip set on both forms, wind-ups, anchors,
  every clip from idle's first frame, the Tide's lift, Deep Well's sink and sweep, the echo's still pause and thrust.

## Notes
- The clip map for combat (paste into `nhoa` in creatures.json once the skills exist): `"clip_by_skill":
  {"silt_fall": "cast", "deep_well": "deep_well", "nhoa_echo": "echo", "farewell_tide": "special"}`. The basic attack
  plays `attack` by kind.
- The look changed (matte body, flat-shaded beads, denser neck and head), so `nhoa` and `nhoa_held` portraits are
  re-baked (assets/ui/portraits/creatures/). No new files, so no new PROVENANCE rows.
- Open: up close each bead still shows a triangular outline (a flat fleck, no longer a lit crystal). Rounder beads
  would roughly double the motes' 10.6k triangles; that needs a budget call.
- The rising column and the echo's double outline are battle-presentation's VFX; the bound-light exception for the
  column is rendering's call (the art sheet's open question still stands).

## Review log
