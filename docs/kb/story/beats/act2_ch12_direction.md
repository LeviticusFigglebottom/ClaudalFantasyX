# Ch12 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30, at the Lead's request, so slice-polish can stage Ch12 straight from them.
They pair with `game/data/dialogue/ch12/` (M4-A2P-003) and [act2_ch12.md](act2_ch12.md) (§1, §7). Their format matches
[act2_ch11_direction.md](act2_ch11_direction.md).

**How the tables were made:** a script framed each shot on its subjects (lens, side, height) in the greybox frame, ran
each scene's cues in order, and checked every spoken line's speaker against the active shot. Every coordinate below
passed that check. Marks are in each zone's layout frame (`game/levels/ch12/<zone>/<zone>_layout.json`). Move anything,
but keep **who is in frame**.

## 0. Ids the greybox already uses for something else (replace them in the staging file)
The greybox layouts' shot ids came before the beat sheet, so some names collide with a different picture. Do what Ch10
did with R03 and R06: put the beat sheet's framing in `game/data/cutscene/ch12/<zone>.json` with `"replace": [...]`.
- **keth_pass:**
  - **K01**: the greybox frames the saddle at `cold_ledge`; the script wants keth_pass.md's K01, the switchback looking up the pass.
  - **K04**: the greybox frames the Ram's terrace; the script wants the breath frame at `cold_ledge`.
- **cloudloom:**
  - **C02**: the greybox's is a high wide; the script wants low on Hesk.
  - **C03**: the greybox's is a close side-on dais shot; the script wants the view from above through the open roof.
  - C01, the aisle, fits: keep it.
- **New ids** (in no layout): P01–P08, K03, K05 and K06 in cloudloom, Q03–Q06.
- **New marks** (all listed in the tables): `pass_foot_1..7`, `switchback_1`, `toma_ledge`, `flight_3_up`, `road_down`, `road_down_catch`,
  `road_away`, `road_on`, `terrace_party`, `ysolde_terrace`, `ram`, `wall_pool`, `ram_fallen`, `kerrid_cord`, `pell_cord`,
  `descent_1..7`, `inn_stair`, `inn_hearth`, `asha_bench`, `hearth_step`, `fire`, `aisle_mid`, `hesk_dais`,
  `old_bundle`, `aisle_out`, and the party's `*_hall` places.

## Pacing against §1
| Beat | §1 | Now (waits plus talk) | Where the time goes |
|---|---|---|---|
| B01 cold road | 1.0 | 0.17 | K01 holds 6–8 s on the sky; P01 lets the mote reach the top of frame |
| B03 breath | 1.5 | 0.54 | **P03 is the clue: hold the wide 6 s** before P04, with no music cue |
| B04 the knot | 3.0 | 0.46 | the woman ties her knot in real time (~8 s) before line 002; 3 s after 004 |
| B05 weeping wall | 1.0 | 0.09 | K03 holds 5 s on the seep before the Ram lifts its head |
| B07 herd-cord | 1.0 | 0.21 | Pell reads the knots by touch, 4 s, before 001 |
| B10–B11 Hesk, "Prayers." | 4.5 | 0.83 | **K06 ≥ 5 s**; **C05 holds on a face that doesn't change**, 4 s |
| B12 forty-seven voices | 3.0 | 1.28 | 2 s after 005 ("Seven houses."); Q05 holds Toma's back 3 s before 011 |
| B13 down the other side | 1.0 | 0.12 | the whole beat is the rail; nobody looks back (≥ 40 s) |

## Per scene

#### `ch12_cold_road`

B01. K01 is the art doc's switchback (keth_pass.md K01): **replace** the greybox's K01, which frames the saddle at `cold_ledge`.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| K01 | 24 mm, the zigzag up the pass, a pass-cord across the saddle against the sky; `[3.83, 3.5, -4.22]` → `[0.2, 2.9, -24.8]`, 60° | switchback_1, knot_post | no line |
| P01 | 35 mm, the party on the first switchback, a mote going straight up; `[-0.94, 1.6, 0.04]` → `[0.15, 1.4, 3.05]`, 38° | pell, toma, asha, rhen | `road_001` pell in frame |

#### `ch12_breath`

B03, the clue. K04 is the art doc's breath frame (keth_pass.md K04), the road in shade at `cold_ledge`: **replace** the greybox's K04, which frames the Ram's terrace. **P03 never pushes in on Kerrid's face; no music cue.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| K04 | 85 mm, the road in shade, a figure against the dark crag, the others' breath fogging; `[97.74, 19.6, -42.22]` → `[94.2, 19.4, -46.3]`, 16° | kerrid, toma | no line |
| P03 | 50 mm wide two-shot against the crag, Toma's breath fogging, none from Kerrid; `[96.3, 19.6, -43.88]` → `[94.2, 19.4, -46.3]`, 27° | toma, kerrid | no line |
| P04 | 85 mm, Toma to Kerrid, low (Toma's single; Kerrid's look is the next cut); `[94.36, 19.2, -44.45]` → `[93.4, 19.4, -45.6]`, 16° | toma | `breath_001` toma in frame; `breath_002` toma in frame |

#### `ch12_the_knot`

B04 side scene. One locked 50 mm frame at the post: everyone speaks inside it.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| P05 | 50 mm locked on the knotted post; `[3.84, 7.5, -43.13]` → `[0.1, 7.4, -42.47]`, 27° | knot_post, road_down, road_down_catch | `knot_001` rhen in frame; `knot_002` ullari_woman in frame; `knot_003` rhen in frame; `knot_004` ullari_woman in frame |

#### `ch12_weeping_wall`

B05. K03 isn't in the greybox: add it (keth_pass.md K03, below the terrace).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| K03 | 35 mm below the terrace: the Lit Age wall, its seep running down in cold light; `[38.55, 12.8, -38.76]` → `[41.0, 13.4, -43.0]`, 38° | wall_pool, ram | no line |
| P06 | 50 mm, the Ram at the pool lifting its head (insert on the herd-cord next); `[38.7, 13.2, -39.25]` → `[40.0, 13.4, -40.0]`, 27° | ram | `wall_001` ysolde off frame (intended) |

#### `ch12_herd_cord`

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| P07 | 85 mm, Kerrid untying the cord; Pell reading it by touch; `[39.63, 13.2, -44.66]` → `[41.0, 13.4, -40.9]`, 16° | kerrid, pell | `cord_001` pell in frame; `cord_002` pell in frame |

#### `ch12_down_the_other_side`

B13. Forward only: the rail never looks back (rule: nobody looks back).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| P08 | 35 mm rail, ahead of the line, looking down the road ahead (never back); `[105.2, 18.2, -40.0]` → `[110.0, 17.8, -40.0]`, 38° | descent_3, descent_5 | no line |

#### `ch12_forty_seven_voices`

B12, the inn at night (the greybox has only `inn_door`; the room is new, behind it).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| Q03 | 35 mm, the fire, Asha on the bench, Ysolde on the stair; `[35.64, 1.6, -6.7]` → `[32.7, 1.4, -8.4]`, 38° | asha, ysolde | no line |
| Q04 | 50 mm two-shot by the fire (85 mm singles may cut in: keep both in frame here); `[35.33, 1.4, -6.77]` → `[34.3, 1.4, -8.0]`, 27° | inn_hearth, asha_bench | `voices_001` ysolde in frame; `voices_002` asha in frame; `voices_003` ysolde in frame; `voices_004` ysolde in frame; `voices_005` ysolde in frame; `voices_006` asha in frame; `voices_007` ysolde in frame; `voices_008` ysolde in frame; `voices_009` asha in frame; `voices_010` ysolde in frame |
| Q05 | 50 mm, Toma on the hearth step, **back to camera and to them**; `[33.66, 1.2, -8.12]` → `[33.4, 1.4, -9.6]`, 27° | hearth_step | `voices_011` toma in frame; `voices_012` toma in frame |
| Q06 | 85 mm insert, the fire; `[34.0, 0.6, -8.7]` → `[34.0, 1.4, -10.2]`, 16° | fire | no line |

#### `ch12_hesk`

B10–B11. **Replace** the greybox's C02 and C03: the greybox's C02 is a high wide and its C03 a close side-on dais shot, while the beat sheet wants C02 low on Hesk and C03 from above. K05 and K06 are new in this zone (keth_pass.md's Cloudloom shots). **K06 holds ≥ 5 s; C05 holds on a face that doesn't change.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| K05 | 24 mm, the floor looking up: beam lattice and keth against the sky; `[0.0, 6.4, -52.45]` → `[0.0, 7.4, -43.25]`, 60° | aisle_mid, hesk_dais | no line |
| C01 | 35 mm tracking down the aisle, cords brushing shoulders (the greybox C01 fits: keep); `[0.0, 7.6, -34.5]` → `[0.0, 7.4, -36.0]`, 38° | aisle_mid | no line |
| K06 | 35 mm, the floor at noon, the cords' shadows written on white stone, a figure reading them; `[2.26, 8.4, -46.64]` → `[1.2, 7.4, -49.55]`, 38° | hesk_dais, old_bundle | no line |
| C02 | 35 mm low, Hesk on her dais at noon; `[0.0, 6.5, -52.5]` → `[0.0, 7.4, -54.0]`, 38° | hesk | no line |
| C03 | 18 mm from above (the open roof), the cords' shadows moving like writing; `[0.0, 20.0, -49.0]` → `[0.0, 7.4, -50.5]`, 75° | hesk_dais | no line |
| C04 | 85 mm, Hesk's head turning to one dark bundle above the dais; `[5.7, 7.6, -45.94]` → `[1.2, 7.4, -51.3]`, 16° | old_bundle, hesk | no line |
| C05 | 85 mm held, Ysolde's hand in the cords, her face not changing; `[3.7, 7.4, -47.85]` → `[2.4, 7.4, -48.6]`, 16° | old_bundle | no line |
| C06 | 85 mm, Toma watching her; `[-2.9, 7.4, -46.05]` → `[-1.6, 7.4, -46.8]`, 16° | toma | no line |
| C07 | 50 mm two-shot, Asha and Ysolde at the cords; `[3.88, 7.4, -48.34]` → `[2.4, 7.4, -48.6]`, 27° | old_bundle | `prayers_001` asha in frame; `prayers_002` ysolde in frame; `prayers_003` ysolde in frame |
| C08 | 35 mm, Ysolde walking away down the aisle, Rhen and Toma watching; `[-4.65, 7.6, -49.86]` → `[-1.4, 7.4, -40.93]`, 38° | aisle_out, rhen, toma | no line |

## Audio cues by shot (for audio)

Every `@music` and `@sfx` in the chapter's scenes, in script order, with the shot it lands on and what follows it
(the next line or hold). A music change marked `fade=0.0` is a hard cut. Barks, camps and shrines play in the field and
are left out. A shot of — means the cue plays before the node's first shot, over the fade.

| Scene | Shot | Cue | Then |
|---|---|---|---|
| `ch12_cold_road` | K01 | `@music keth_pass fade=2.0` | hold 5.0 s |
| `ch12_down_the_other_side` | P08 | `@music keth_pass fade=2.0` | <<if $ch12_rhen_tied_knot>> |
| `ch12_forty_seven_voices` | Q03 | `@music silence fade=2.0` | hold 3.0 s |
| `ch12_forty_seven_voices` | Q04 | `@music ysolde_theme fade=3.0` | `ch12_voices_001` Ysolde |
| `ch12_forty_seven_voices` | Q06 | `@music silence fade=4.0` | @letterbox off |
| `ch12_hesk` | K05 | `@music cloudloom fade=2.0` | hold 4.0 s |
| `ch12_hesk` | C03 | `@music hesk_bound fade=0.0` | hold 8.0 s |
| `ch12_hesk` | C06 | `@music cloudloom fade=2.0` | cut to C07 |
| `ch12_the_knot` | P05 | `@music silence fade=1.0` | hold 3.0 s |
| `ch12_weeping_wall` | P06 | `@music avalanche_ram fade=0.5` | `ch12_wall_001` Ysolde |
