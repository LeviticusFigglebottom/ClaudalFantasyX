---
id: M4-CRE-670
title: "The Ch12 regulars without ice: the ridge lynx and the scree crawler swap frost for snow and grit (ADR 0015, ADR 0204 §2)"
role: character
status: blocked
blocked-by: ADR 0203
owner_session: ""
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

## Review log
