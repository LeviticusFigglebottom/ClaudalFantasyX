---
id: M3-ENV-1000
title: "Brine Shoals (Ch6): Sefir's barge leaves no wake and his reflection never ripples"
role: environment
status: todo
owner_session: ""
depends_on: [M3-CHR-02, M3-RND-03]
milestone: M3
request-from: character
---
## Goal
Sefir first appears at the end of the Ch6 Brine Shoals raid on his white barge, poled through the smoke, which
**leaves no wake** (ADR 0017, `docs/kb/story/characters/sefir_aurane.md`). His reflection in the water never ripples
(act1_npcs.md §1.10). The barge and the water are Environment's; the layer and shadow feature is Rendering's
(M3-RND-03).

## Acceptance criteria
- [ ] The Brine Shoals water honours Rendering's still-reflection layer for Sefir (and for anything on the barge with
      him, if the beat wants it).
- [ ] The barge's hull moves through the water without a wake or ripple ring, while the Order's other boats leave one.
- [ ] Viewed in a shot with Sefir on the barge (his stage is `game/levels/_tests/characters/sefir/sefir_stage.tscn`;
      his `pivot` clip turns him 30 degrees in place on the barge, no step).

## Notes
- His actor: `assets/characters/sefir/sefir.glb`; clips in `assets/characters/sefir/anim/sefir_clips.tres`.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M3-ENV-01. M3-ENV-01 is env-art's Tamsule Bell kit (named in code); the characters track filed this request under the same id. Now M3-ENV-1000, from the Lead's id block (CONSOLIDATED §4).

## Review log
