# The Open Sea at Night (Ch15): Design Notes

Owner: Environment Artist (M3-ENV-720; the sheet first, then the arena). Lighting review: Rendering.
- **Story:** [act_outline Ch15](../../story/beats/act_outline.md).
- **Boss:** the creatures track's [wakefin.md](../creatures/act2/wakefin.md) (on `claude/creatures`).
- **Grade target:** [color script](../color_script.md) `ch15`.
- **Zone:** `ch15/open_sea`.
- **Kit:** in the Haluna kit as `bridal_barge.py`.
- **Arena:** `bridal_barge_night` (the Wakefin).

**The feeling in one line:** fugitives in the dark on a wedding barge, with a dead man under the bridal cloth. The
only light is the sea and the dead coming up out of it.

**What the place is.** Merel's bridal barge, cut loose from the court at Ansedra and drifting south:
- **The barge:** a long, low Ansedran barge, poled. Its hull is wedding-red lacquer with a gilt sheer band; its
  deck is plain timber.
- **The stern:** a canopy of red bridal cloth on four gilt posts. Under it, Tobin's body lies on a low bier, covered
  in Merel's bridal cloth.
- **The bow:** an empty lamp hook, because wedding barges never carry a lamp, so as not to trouble the still water.
  Nobody dares strike one.
- **Along the rails:** the punt poles, laid down.

## 0. Lighting

The colour script `ch15` (01:00):
- the moon `#D2DFFF` at 0.25 (rule 3b: no more than 2.5 × the sea-glow);
- fill `#0B1630` at 0.15, rim `#9DB4D9`;
- fog `#1C3A4A` at 0.004;
- the water is `night_sea` (deep `#061A2B`), with sea-glow 0.12;
- exposure 1.10, saturation ×0.85, `lut_ch15_unlamped`.

**No warm source anywhere:** no lamp, no fire, no flame on the barge. Skin takes only the moon and the sea.

## 1. Pieces

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `bridal_barge` | The barge as the arena's ground. The deck is level at y 0, 16 × 7.5 m, along X. Also: the hull in wedding-red lacquer down to the waterline at −0.6, with its gilt sheer band; a low rail, 0.35 m; the stern canopy with the bier; the bow's empty lamp hook; the punt poles laid down. | 17 × 8 | 16k / 1.2k |

## 2. The Wakefin arena (`bridal_barge_night`)

- **The battle floor** is the deck, level at y 0 over every slot's metre.
- **Low rail:** the near rail stays under the camera's rays to the slots.
- **The Wakefin's `BossAnchor`** stands in the sea off the enemy-side bow, at (−10, −0.6, −1.5), at the waterline.
  It circles there; its fin is the read.
- **Around the barge:** open water to the horizon, the sea-glow, the stars. No land and no other boat.
- **Hints:** `the_bier` (the canopy and the bridal cloth) and `the_dark_water` (low over the rail, out to sea).

## Revisions

- 2026-10-27 (env-art, M3-ENV-720): first issue, with the arena.
- 2026-10-30 (env-art, M4-A2P-045): the open sea dressed (`tools/act2/ch15_open_sea_dressing.py`).
  - **The barge.** The arena's 16 × 7.5 m barge doesn't fit the greybox's 4 × 10 m deck: scaled to the deck's length,
    its bier misses the Bier block by 2.4 m. So `open_sea_barge` is bridal_barge.py's builders at the greybox's size
    (`build_fitted`; the arena's barge is byte-identical). Its deck is the Deck block, its rail on the Rail blocks,
    and the canopy and Tobin's bier on the Bier block.
  - **The grade.** The Wakefin arena's unlamped grade and its night sea with the sea-glow. Nothing on the barge gives
    light.
  - **Open:**
    - the shoal's held dead under the water (rendering's held light);
    - the dawn fog at the bow (rendering);
    - Hollowmere's first visit, which has no greybox zone yet (chapters).

    All in M4-A2P-0451.

