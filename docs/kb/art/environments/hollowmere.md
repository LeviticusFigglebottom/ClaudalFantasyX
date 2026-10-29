# Hollowmere, the Saltwright Flotilla (Ch17): Design Notes

Owner: Environment Artist (M3-ENV-723: the sheet, the kit and the grade). Lighting review: Rendering.
- **Story:** [act_outline Ch17](../../story/beats/act_outline.md); bible §7 (the Saltwrights) and §5.9.
- **Grade target:** [color script](../color_script.md) `ch17`.
- **Zone:** `ch17/hollowmere`. No battle is staged here.
- **Kit:** in the Haluna kit as `hollowmere.py`.
- **Grade files:** `assets/environments/zones/ch17/` (`hollowmere_grades.py`).

**The feeling in one line:** warmth returns, low and long. Gold light on people who will lose every machine they own.

**What the place is** (bible §7):
- **The raft-city.** Some four thousand Saltwrights live on lashed hulls, some patched with Lit Age hull plating.
  Windmills and tide-wheels stand among them. The city moves with the seasons among the outer shoals.
- **Their machines.** Salvaged bound glimmer is put back to work in pumps, signal lamps and medicine-warmers.
  The signal lamps are the frame's teal: bound light in salt-glass, `glimmer_bound`.
- **Dace's dry-dock** is the chapter's heart. His unfinished hull stands on a floating dry-dock: the keel, the
  ribs, five strakes on one side, staging and a workbench. Nothing on it is finished. The ledger Rhen reads is a
  prop for the chapter's staging, not geometry here.
- **Influences** (transformed; SPEC §2): Pacific outrigger and lashed-hull rafting, salvage yards, and windpumps.
  These are combined into an original plan: double hulls under one deck, with the mark of the Saltwrights (the
  housing-mark, `lowlight.py`) on their machines.

## 0. Lighting
- **`ch17`:** dusk at 18:10.
  - Sun 8° at 280°: key `#FFB16E` 2.4, fill `#5A7FA8` 0.45, rim `#F2A64A`.
  - Sky `#3E5A86` over a `#F2A64A` horizon, with thin warm fog (albedo `#C8986A`, 0.008).
  - Exposure 0.85, S-curve 0.5, saturation ×1.05.
- **The LUT is `lut_act3_dusk`, the Act III base grade.** The gold gain returns, but the highlights are held under
  0.92 (zone_lut's `white_cap`), so it reads as evening.
- **The water** is `lagoon_low_sun` at absorption ×1.5.
- **The only cool light** is the signal lamps' bound teal.

## 1. Kit pieces (metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `hm_lashed_hulls` | A Hollowmere home: two old double-ended hulls (10 m) lashed under one deck (y 0.9). The near hull is patched with Lit Age plating. A woven deckhouse under thatch, lashing bands, deck clutter | 10 × 8.8 | 9k / 700 |
| `hm_windmill` | A windmill on its log float: a four-legged mast (9 m), a six-armed rotor of sand-cloth sails on a copper hub facing +Z, a tail vane | 7 × 12.5 | 5k / 400 |
| `hm_tide_wheel` | A paddle wheel (3 m) between two log pontoons, its frame and axle, and the copper gear housing carrying the Saltwright mark | 5.2 × 4.4 | 6k / 450 |
| `hm_signal_lamp` | A signal post (3.4 m): a salt-glass lantern round a bound core, with copper caps | 0.9 × 3.4 | 1.5k / 150 |
| `dace_hull_frame` | Dace's unfinished hull (12 m) on the floating dry-dock (16 × 7 m, top y 0.6): cradle, keel, stem and sternpost, 13 ribs, five strakes on the near (−Z) side only, staging, a ladder, his workbench with a rib-mould | 16 × 7 × 4.2 | 12k / 800 |
| `hm_far_flotilla` | The rest of the raft-city round the zone: lashed homes and windmills at 220–460 m | r 460 | 9k / 2.5k |

**Composition** (act1-chapters places it):
- The dry-dock is the zone's centre, with Dace's hull side-on to the arrival so the bare ribs read against the sky.
- The homes cluster round it in lanes of water 4–6 m wide, with windmills on the outer edge and tide-wheels in
  the channels.
- Signal lamps stand at the lane corners, lit (bound teal). They are the only cool light in the frame.

## Revisions
- 2026-10-27 (env-art, M3-ENV-723): first issue, with the kit and the grade.
