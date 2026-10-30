---
id: M4-CRB-007
title: "Hesk, the Holy Vowbound, at the Act I bar: soft cords and tied knots, her own Cord-Lift and Mending clips, anchors"
role: character
status: review
owner_session: "creatures-b"
depends_on: [M3-CRE-643, M3-CRE-647]
reviewer: combat
milestone: M4
request-from: ""
---
## Goal
ADR 0041 §3 and ADR 0205 (Act II starts for creatures-b): bring Hesk (Ch12, bound at Cloudloom; Holy, cleanse,
Mending; Swell Pass-Cord) to the Act I Vowbound bar (Ilun, Kahre, Virel, and the M3-CRB-013 move-pass lessons) from
her design sheet, [hesk.md](../../plan/act2/bosses/hesk.md), and her art sheet,
[vowbound/hesk.md](../../art/creatures/vowbound/hesk.md).

## Acceptance criteria
- [x] Audited from the party side of the battle camera (the `vowbound_slot`) and up close. What read as primitive is
      fixed within the Act I Vowbound budget (≤ 18k; now 17,930): the cords hang as soft rope with unlaid tufts, the
      knots are tied (a crossing strand, helical wraps) and lit by their form, the ruff is a fringe of cord loops, the
      neck is lean and folded, and each eye has a brow.
- [x] Clips: the Vowbound contract (`idle`, `ready`, `rise`, `dismiss`, `attack`, `cast`, `hit`, `hit_b`, `defend`,
      `ko`, `victory`, `special`), `release` (the held form), and one clip per skill on the sheet: `cast` (Knot-Light),
      `cleanse` (Cord-Lift, new), `mending` (her Mending, new, ADR 0204) and `special` (Pass-Cord). Every wind-up is at
      least 0.45 s before contact, every one-shot starts from idle's first frame, and nothing goes under the water
      (GroundedClipsTest).
- [x] Anchors `vfx_core` (the breast, on `body`) and `vfx_keepsake` (the keth bundle, on `bundle_1`), both unweighted.
- [x] creatures.json `contact`: added `cleanse` 0.9 and `mending` 0.8 (kept attack 0.55, cast 0.8, special 1.45). No
      `clip_by_skill` yet, because her skills are not in skills.json (M4-A2P-024). The ready-to-paste map is in both
      sheets.
- [x] Test: tests/unit/test_creature_vowbound_act2.gd `test_hesk_*` covers the clip set, the wind-ups, the anchors,
      the starts from idle, Cord-Lift's gather and lift, and the Mending's raised bundle and bow.
- [x] Sheets updated. Portraits `hesk.png` and `hesk_held.png` re-baked and viewed. No new .tres: the materials are
      unchanged and byte-identical.

## For combat (review)
When M4-A2P-024 adds her row and skills, paste this into creatures.json `hesk` and drop `vowbound_pending`:
`"clip_by_skill": {"knot_light": "cast", "cord_lift": "cleanse", "hesk_mending": "mending", "pass_cord": "special"}`.
Contacts for battle-presentation's VFX timing: attack 0.55, cast 0.8, cleanse 0.9, mending 0.8, special 1.45 s.
Anchors: `vfx_core`, `vfx_keepsake`.

## Review log
