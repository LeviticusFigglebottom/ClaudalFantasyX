---
id: M4-CRE-670
title: "The Ch12 regulars without ice: the ridge lynx and the scree crawler swap frost for snow and grit (ADR 0015, ADR 0204 §2)"
role: character
status: review

owner_session: "creatures (session_01UPFyE7ob7hr4Skv4cw3rtN, claude/creatures)"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
ADR 0015 keeps ice out of Ch12–Ch15, and ADR 0204 §2 extends that to the Ch12 regulars for consistency (the Avalanche
Ram's own swap is M4-A2P-059). Two built foes still carry frost:
- **`ridge_lynx`** (Keth Pass): its "frosted ear tufts" and any rime in the coat's vertex colour become **snow** caught in
  the winter coat (clumped white on the back and tufts, dry, matte) and grit on the paws.
- **`scree_crawler`** (the Cloudloom approach, a variant of the slag tortoise): its "frost-split scree" becomes
  **snow-dusted, grit-packed scree**: dry slabs with snow in the seams, no ice sheen, no rime. Its art sheet's "frost
  counter" wording becomes a cold or grit counter in the encounter design's terms (combat's call, not this task's).

Plan sheets: docs/kb/plan/act2/creatures/ridge_lynx.md and scree_crawler.md (both `draft: pre-gate`).

## Acceptance criteria
- [ ] Neither model reads as ice or frost at close-up or battle distance: no specular rime, no blue-white ice tint.
      Snow is matte white and dry, and grit is a dark speckle.
- [ ] Both rebuild byte for byte (tools/dev/verify_blender_builds.py); portraits re-baked; review shots viewed.
- [ ] Their art sheets (docs/kb/art/creatures/act2/ridge_lynx.md, variants.md) say snow and grit, not frost.
- [ ] Do it together with the ridge lynx's planted-foot pin and pounce steps (its plan sheet's "Work at the gate"),
      so it is rebuilt once.

## Done (creatures, 2026-10-30)
- **ridge_lynx:** the `salt_glass` frost on the ruff, jaw, muzzle and whiskers is now dry snow (#E8E6DF, matte; changed 2026-10-30 to the `gauze_white` swatch, #EBE7DF, so the colour is on the palette), with
  snow settled in the coat's clumps along the back and scree grit speckled in the paws. In the same rebuild its paws
  are held planted (`grounding.pinned`, with the new opt-in hip `roll` for a leg the body twists sideways over, and a
  small pull toward the authored pose so a leg the clip returns to rest ends at rest). Slides: hit 21.8 → 5.0 cm,
  hit_b 29.3 → 7.0 cm. The pounce's 18.5 cm is the take-off frame's push-off; the tips hold through the crouch and the
  landing.
- **scree_crawler:** the rime in the splits and the frost on the crown are now dry packed snow and a snow dusting, with
  dark grit speckled between the stones.
- Verify identical (ridge_lynx, scree_crawler; raid_hound, tide_crawler and slag_tortoise unchanged by the solver's new
  path); portraits re-baked; review shots viewed (no ice read); test_creature_actor's lynx test passes (paws end
  where they stood); art sheets updated.
- Leg shaping (the plan sheet's note: plain rounded legs) is left for a separate pass.

## Review log
