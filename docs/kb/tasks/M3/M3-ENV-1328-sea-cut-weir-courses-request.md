---
id: M3-ENV-1328
title: "The sea-cut weir's courses read as rounded logs and its crest as a flat sheet (GPU QA row 62)"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
The PC's GPU QA (passes 3–5, row 62, `pemakar_p11_sea_cut_weir_day`) still reports that the weir slabs read as flat
grey boxes. env-art-b has done what its side allows:
- The weir wears `kit_weir_stone`, written by `tools/act1/ch05_pemakar_dressing.py`.
- That material gets per-block value, stronger relief, salt and algae bands, and soaked stone that keeps its relief.

The rest is in env-art's kit code, `assets_src/environments/kits/pemakar/pemakar_harbour.py` `weir()`:
- **The ogee courses are pills.** They're `rounded_block` with a 0.07 m radius on a 0.13 m half-height, so from
  P11's water-level camera they read as stacked logs or tyres, not dressed stone. A radius of about 0.025 with a
  chamfered arris, and some joint offset per course, would make them read as ashlar.
- **The crest reads as one smooth dark plane.** The water plane over the crest and bed (`water_plane`, y 0.06,
  z −3 to 0.25) wears the spill water and covers the crest stones, so the crest reads as one flat dark slab. It
  would read better if the water sat lower than the crest stones' tops (so they break the surface), or ran only in
  a channel between dry crest stones.

## Acceptance criteria
- [ ] The courses read as dressed stone blocks with tight arrises in `pemakar_p11_sea_cut_weir_day`.
- [ ] The crest's stones show through or beside the arriving water.
- [ ] `sea_cut_weir` is rebuilt (kit manifest and PROVENANCE row unchanged in shape), and env-art-b re-renders P11
      and `ch05_pemakar_weir`.

- 2026-10-30 (env-art): **done.** In `pemakar_harbour.weir()`:
  - The ogee courses and the crest stones take a tight 0.025 m arris (`WEIR_ARRIS_M`; it was 0.07 and 0.06).
  - Each course's joints break by a random offset.
  - The arriving water lies at −0.02, under the crest stones' tops, and stops at their upstream face, so the crest
    breaks it.

  `sea_cut_weir` rebuilt (4298/368 tris); the Pemakar kit rebuilt in full (34, the rest byte-identical); manifest
  updated. **Viewed** P11: the crest now reads as a row of stones over the water (it read as one pale slab before),
  and `ch05_pemakar_weir`. Both shots will drift. Reviewer: environment (env-art-b).

## Review log
