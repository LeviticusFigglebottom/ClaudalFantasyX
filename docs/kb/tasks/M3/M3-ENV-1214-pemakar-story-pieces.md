---
id: M3-ENV-1214
title: Pemakar's story pieces the kit lacks (the sea-cut weir, the wake-wall, the crown bell, a harbour quay) and a day grade
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-C05-1213]
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
act1-chapters dressed `ch05/pemakar` with the Pemakar kit (M3-C05-1213). act1_ch05.md §10 item 1 lists pieces the
kit doesn't have yet; the zone uses greybox stand-ins or kit modules for them:
- **The sea-cut weir** (the hero mesh: "the last stone lip where the channels spill into the sea"; B05's P11/P12).
  Stand-in: the greybox block `SeaCutWeir` in the water off the quay's east end (x 10, z 27.7).
- **The wake-wall** for name-boards at the harbour (greybox `WakeWall`, x 8, z 22.7, at the quay's back).
- **The crown bell** at the top tier (greybox `CrownBell`).
- **A harbour quay**: today a row of `terrace_wall_4m` / `terrace_tread_4m` modules at the shore (front z 27, top
  y 1.2), the slope behind meeting it at z 22.7.
- **A day grade** for B11 (the day after the binding): the zone uses `pemakar_dusk_environment.tres` as a stand-in.

Each piece can be dropped in by naming it in `tools/act1/ch05_pemakar_dressing.py` (the greybox block it replaces
is named above; give it `"block": <id>` so it follows the story).

## Acceptance criteria
- [x] The pieces exist in the Pemakar kit with PROVENANCE rows; the day grade exists.

## Notes (env-art)
- `pemakar_harbour.py` builds four pieces (all within budget, with LOD1). Every older Pemakar piece rebuilt
  byte-identical.
  - **`harbour_quay`:** 32 m.
    - Origin at the front edge's centre on the deck; place it at (0, 1.2, 27) for the zone's quay.
    - A fitted face to 1.2 m under the sea with a tide band, coping, a paved deck back 4.3 m.
    - Bollards, mooring rings and rubbing posts, and a sea stair at the west end.
  - **`sea_cut_weir`:** origin at the crest's centre, the crest's top; place it at sea + 0.4.
    - The cut arrives from −Z between two cheek walls, 3.2 m upstream of the crest, so it needs open ground or a
      gap behind it.
    - **Where to put it:** your stand-in (x 10, z 27.7) is in front of the 32 m quay (x −16..16), so its cut would
      run through the quay deck. Either shorten the quay so it ends at x ≤ 5.5, or move the weir. The kit preview
      puts it where the bottom tier's channel reaches the shore, at x −39.3, z 28.6, crest y 0.4.
    - The weir step (the child's step) is on the east cheek.
  - **`wake_wall`:** 5 × 2 × 0.6 m. Origin at its foot's centre, boards toward +Z; place it at (8, 1.2, 22.7).
  - **`crown_bell`:** origin at its foot's centre, front +Z; place it on tier 9 at (3, 29.68, −67.05).
- **Day grade:** `game/levels/_tests/pemakar_kit/pemakar_day_environment.tres` and the preview's `day` mood
  (16:30). It has a shadowing `Sun` (#FFD9B0 2.4 at 24° / 252°), sky fill `#8FB3D9` 0.35, and the lamps, festival
  far lights, sea lights and sea-glow all at 0. Copy it as you copy the dusk and night grades.
- Preview shots `pemakar_p04_harbour_day` and `pemakar_p11_sea_cut_weir_day` are requested from the PC.

## Review log
