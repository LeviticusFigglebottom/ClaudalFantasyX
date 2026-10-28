# The Kite (Ch18 to the Ending): Design Notes

Owner: Environment Artist (M3-ENV-725; the sheet and the kit). Review: Story (does it match the beats?), then Rendering.
- **Story:**
  - [act_outline Ch17–Ch18](../../story/beats/act_outline.md): Dace's hull, finished at Hollowmere; the maiden
    flight.
  - [act3_ending.md](../../story/beats/act3_ending.md): H09 (every bound light goes out), E1–E5 on its dark deck,
    E4 (Liss brings it down by hand on the sails Dace modelled on Virel).
  - [act1_ch08.md](../../story/beats/act1_ch08.md) `ch08_hoist_cut_down`: Liss rigs it with the hoist's blocks.
- **Zone:** `ch18/kite` (the hub). Its deck is also the Ending's stage.
- **Kit:** in the Haluna kit as `kite.py`, on `hollowmere.py`'s lines for Dace's hull.

**The feeling in one line:** the father's unfinished boat, finished by other hands and flown. It is small,
hand-made and patched, and it holds everyone.

## 1. What it is
- **The hull is Dace's**, exactly as Rhen found it in Ch17 (`dace_hull_frame`, 12 m), now planked on both sides,
  decked, railed, and fitted with a tiller. The ledger chest is lashed by the hatch.
- **The rig follows Virel** (vowbound.md §3: a ribbon-serpent of sailcloth panels). Two kite wings spread from an
  11 m mast. Each is a delta of battened panels in sand and keth red, on timber spars stayed to the deck. A ribbon
  tail of small panels streams from the sternpost. The seams are plain cloth: the fire is Virel's, not the Kite's.
- **The lift comes from two bound-light engines** on outriggers under the hull. Each is a bronze drum with a ring
  of vanes, a salt-glass band showing the bound core, and two timber arms. The engine and the two lanterns (bow and
  stern) share `kit_bound_core`, so H09's "every bound light goes out at once" is a single material swap. After H09
  the Kite glides on sail alone.

## 2. Kit pieces (metres; LOD0 / LOD1 triangle budgets)

| Piece | What it is | Size | Budget |
|---|---|---|---|
| `kite_hull` | The hull, planked and decked (deck at y 0, keel 3.3 m under it), stem and sternpost, a rail on posts, the hatch, the tiller, the ledger chest, two lamp posts with bound-light lanterns | 13.5 × 4 × 5 | 16k / 1.2k |
| `kite_rig` | The mast (11 m), two kite wings (span 17 m), the stays, the ribbon tail (9 m aft) | 17 × 17 × 11 | 10k / 800 |
| `kite_engine` | One lift engine on its outrigger arms (built on the +Z side; place it mirrored for −Z) | 2 × 2 × 3 | 4k / 300 |

**Placement:** all three share the hull's origin (the deck's centre). The engine goes in twice, the second
mirrored in Z.

## Revisions
- 2026-10-27 (env-art, M3-ENV-725): first issue.
