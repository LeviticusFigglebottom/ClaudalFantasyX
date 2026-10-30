# Ch11 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30, at the Lead's request, so slice-polish can stage Ch11 straight from them.
They pair with the scripts in `game/data/dialogue/ch11/` (M4-A2P-002) and the beat sheet
[act2_ch11.md](act2_ch11.md) (§1 running order, §7 shots). The coordinates are in each zone's greybox layout frame
(`game/levels/ch11/<zone>/<zone>_layout.json`) and every one was checked with the same frustum test as the Ch10 review
(M4-A2P-112). They are proposals: move anything, but keep **who is in frame** as written.

## 0. Before staging: id collisions (fixed in the scripts today)
- **The greybox layouts number their own shots L01–L07, and those aren't lowlight.md's composed shots.** For example,
  the layout's L05 is a view of the drowned sanctum, while lowlight.md's L05 is the engine hall from the stair head. So
  `@camera L05` in the engine scene would have played in the wrong place with no error.
- The scripts now use new ids for the art doc's three shots:
  - **V00** = lowlight.md L01, the Vey hero frame (`ch11_drowned_galleries`);
  - **V10** = lowlight.md L03, the conduit court (`ch11_housing_mark`);
  - **T00** = lowlight.md L05, the engine hall from the stair head (`ch11_the_engine`).
- Stage them in a `game/data/cutscene/ch11/<zone>.json`, as in Ch10. Leave the layouts' L-ids to chapters.
- Pell's kneel now uses the layout's existing mark **`pell_kneel`** (65, −8, 6) rather than a new `ledge_edge`.

## 1. Sunken Vey (`ch11/sunken_vey`)
Anchors from the layout:
- spawn `Landing` (−4, 0, 0);
- `conduit_mark` (34, 0, −27.8), the housing on the conduit;
- `fig_end` (38, 0, −54);
- shots V01–V04 (V01 is the landing wide).

### B01 `ch11_drowned_galleries` (C; §1 1.0 min, staged ~0.3: hold V00 longer)
| Cue | Shot / blocking | In frame |
|---|---|---|
| V00 | The Vey hero frame (lowlight.md L01): on the water at the Vey's mouth, the arcades receding; 24 mm. Hold **8–10 s** (5 now) with the bound teal steady along the cornices (`cornice_conduits`: a mark on the nearest cornice, about (6, 3.5, −4)). | nobody needed |
| V01 (layout) | Party at the landing. New marks: `liss_landing` (2.0, 0, −1.5), a step ahead and looking at the conduits; `pell_landing_back` (−1.5, 0, 1.0), at the back. | `ch11_vey_001` **Liss, in frame** (6° off axis) · `ch11_vey_002` **Pell, in frame, small, at the back** (10°): he speaks from behind the group, not as a cutaway |

### B03 `ch11_housing_mark` (E; §1 3.0 min, staged ~1.1: the argument needs air)
**Blocking:**
- Liss at `conduit_mark`;
- Rhen at new `rhen_court` (35.5, 0, −26.5), 1.9 m off her shoulder;
- new `court_edge` (30.5, 0, −24.0), where she stops with her back turned;
- new `gallery_away` (26, 0, −21);
- the rest of the party a few metres back, out of the singles.

| Cue | Shot | Lines and who is in frame |
|---|---|---|
| V10 | The conduit court (lowlight.md L03): drowned arcades round the lit conduit at chest height, verdigris; 35 mm | Liss wipes the mark; no line |
| V04 (layout) | **Insert pair** (85 mm): Liss's hand on the housing, then Rhen's lantern collar beside it, matched | `001`–`004` play over the inserts, Liss's voice on her own hands (intended) |
| **cut to V05_rhen** *(add)* | Rhen single, 85 mm: cam (33.0, 1.55, −26.0) → `rhen_court`, fov 18 | **`005` "Dace Sallow. My father." on Rhen's face.** It's the admission; don't leave it on an insert. `006` (if Coilspire) the same |
| V05 | Two-shot, 50 mm: cam (37.5, 1.5, −24.5) → (34.7, 1.4, −27.2), fov 27; both in frame (1° each) | `007` Liss, `008` Rhen. Then alternate singles: **V05_liss** (cam (36.2, 1.55, −29.0) → `conduit_mark`, fov 18) for `009`; V05_rhen for `010`, `011` |
| V06 | 35 mm held: cam (36.5, 1.6, −28.5) → `court_edge`, fov 38. She shoves the lantern back, walks to `court_edge` and stops, **back to camera** | `012` **Liss in frame from behind** (1°). Rhen at the frame's edge (27°), not looking at her. Then she walks to `gallery_away` and out |
| V07 | Insert, 85 mm: Asha's hand going to her comb and stopping | **no line, no face** (§7: the lantern isn't voiced until Ch15). Hold **3 s** |

**Pauses:** hold 2 s after `004` (the "Don't." lands); 2 s of silence on V06 before `012`; let the music cut to silence on the walk away (it does).

### B11 `ch11_held_by_you` (E; §1 1.5 min, staged ~0.7)
**Blocking:** new `landing_pell` (−2.5, 0, 1.5), Pell at the landing's edge looking at the water; new `landing_asha` (−1.6, 0, 0.4), where Asha walks to.

| Cue | Shot | In frame |
|---|---|---|
| V08 | Two-shot, 50 mm: cam (1.5, 1.5, 3.5) → (−2.3, 1.4, 0.9), fov 27 | both, all five lines (8° and 11°). Pell doesn't turn to her until `003` "By you, now." |
| V09 | The line leaving, from behind, 35 mm | Rhen and Liss's places in it (the `<<if>>` marks): **no line**. Hold 4 s |

**Pause:** 2 s after `002`, then `003` (it's written; keep it). After `005`, 1.5 s before the cut.

## 2. Lowlight (`ch11/lowlight`)
Anchors from the layout:
- spawns `Gate` (2, 0, 0), `EngineHall` (10, 0, −20), `Sanctum` (60, −8, 4);
- marks `lamp_bench` (4, 0, 6.4), `nhoa` (68, −8, 4), `pell_kneel` (65, −8, 6);
- the layout's L07 frames the bench.

### B05 `ch11_the_engine` (C; §1 1.0 min)
| Cue | Shot | In frame |
|---|---|---|
| T00 | The engine hall from the stair head (lowlight.md L05), 35 mm: cam (14, 3.5, −14) → (10, 3, −27), fov 38. The party arrives at the stair foot (about (11, 0, −19.5)) | party (20°) and the engine (2°) together; hold **3 s** |
| T02 | Low from the water, 35 mm: cam (12, 0.4, −21) → (10, 3.5, −27.5): the Engine turning all its lamps to them | the Engine. **`001` Pell, `002`/`003` Liss are off frame on purpose**: voices over the machine. Don't cut away to faces; the machine answering them is the shot |

### B07 `ch11_twice` (C; §1 1.0 min)
**New marks:**
- `engine_core` (10, 3.0, −27.5), the vfx anchor where the core's light rises from;
- `liss_engine_frame` (10.8, 0, −22.0), Liss standing at the dead frame.

| Cue | Shot | In frame |
|---|---|---|
| T03 | 24 mm, looking up the vault bay from about (11, 1, −22): **every mote rises** (`glimmer_lift motion=spiral_up`) | no one. **Hold until the last mote leaves the top of frame** (§7); the 5 s now is a floor |
| T04 | 50 mm: cam (13.5, 1.5, −23) → (10.5, 1.3, −20.5), fov 27 | party (15°) with Liss at the frame (20°). `001` Ysolde (only if the Drowner fell): **Ysolde in the group, in frame**. `002` Asha, in frame. Then Liss's look at the engine, no line, 3 s |

### B09 `ch11_nhoa` (C; §1 4.0 min, staged ~1.3: the binding needs its length)
**Blocking:**
- the party enters from `Sanctum` (60, −8, 4);
- new `pell_back` (58.5, −8, 4.5), Pell last in the line;
- new `asha_ledge` (64.5, −8, 4.0);
- `pell_kneel` (65, −8, 6), from the layout;
- new `ledge_behind_pell` (63.6, −8, 6.4), Kerrid;
- `nhoa` (68, −8, 4) is the Saint in the water.
- `asha_sleeve` in the vfx cue is an actor attachment (use `follow=asha_staff`, or a sleeve socket if characters add one), not a mark.

| Cue | Shot | Lines and who is in frame |
|---|---|---|
| N02 | Through the water (underwater shader), 35 mm: cam (63, −7.0, 3.5) → (68, −8.5, 4) | Nhoa (5°), held bound light. Hold 4 s |
| N03 | 85 mm, **the camera finds Pell first**: cam (60.5, −6.6, 2.2) → `pell_back` | Pell stops; his crest rises (0°). No line. 2.5 s |
| N04 | Insert, 100 mm: the carved name-shell at Nhoa's throat | — 2.5 s |
| N05 | 50 mm: cam (62.5, −7.0, 8.5) → (65, −7.6, 6), fov 27. Pell walks to `pell_kneel` | `ch11_nhoa_001` **Pell in frame** (2°) as he reaches the edge, *then* kneels. **From here to the end Pell says nothing** (rule 4). Hold the kneel **6–8 s** (4 now) |
| N06 | 85 mm on Asha: cam (66.5, −6.6, 2.0) → `asha_ledge` | Asha (0°), looking from Pell to Nhoa: two 2 s looks. No line |
| N07 | 35 mm, then an insert on the sleeve | Asha raises the staff; the light comes to it; the sleeve grows a band. `nhoa_bound` sting. The 8 s + 3 s as written; let the sting decide |
| N08 | 85 mm, through the water | Nhoa's head turns toward Pell, **and nothing else** (§7). 3 s |
| N09 | 50 mm wide enough for both: cam (61.0, −6.8, 9.0) → (64.4, −7.4, 6.2), fov 38 | Pell still kneeling (3°); Kerrid walks to `ledge_behind_pell` (12°) and stands. **No line.** Hold **8 s** (6 now) |

### B10 `ch11_lamp_bench` (E, optional; §1 3.0 min)
**Blocking:** Liss at `lamp_bench` (4, 0, 6.4); Rhen walks to new `bench_end` (5.0, 0, 7.6).

| Cue | Shot | In frame |
|---|---|---|
| T05 | Locked, 50 mm, two pairs of hands: cam (6.2, 1.4, 4.6) → (4.5, 0.7, 7.0), fov 35. The layout's L07 frames Liss's side only (26°, at the edge), so use this framing | both at the bench (15°, 14°). The three held inputs, then the flame insert. `ch11_bench_001` Liss and `002` Rhen, both in frame. 3 s hold after |

## 3. Pacing summary (§1 against the scripts' waits)
B01 0.3 of 1.0 min · B03 1.1 of 3.0 · B05 0.4 of 1.0 · B07 0.3 of 1.0 · B09 1.3 of 4.0 · B10 0.6 of 3.0 · B11 0.7 of 1.5.
Ch10 came out the same way. The holds above are where the missing time goes: let the long ones run (V00, T03, N05,
N09), and never fill a silence with a line.

## 4. What the scripts already guarantee (no staging needed)
- Every glimmer cue obeys the light rules: the core's light rises; Nhoa and the conduits are bound and still
  (`test_act2_dialogue`).
- Every spoken line has a speaker and an emotion, and every flag branch runs to END.
