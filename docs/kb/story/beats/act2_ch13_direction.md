# Ch13 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30 (Lead request). They pair with `game/data/dialogue/ch13/` (M4-A2P-004) and
[act2_ch13.md](act2_ch13.md) (§1, §7). The method is the same as [act2_ch12_direction.md](act2_ch12_direction.md):
every coordinate is in the greybox frame and every spoken line was checked against its shot.

## 0. Fixed in the scripts today (story's own files)
- **Kerrid and Tobin shared `outer_moorings`.** Kerrid now stands on the layout's `kerrid_moorings` (−6, 0, 14), and
  Tobin arrives at `outer_moorings`.
- **Merel and Tobin shared `guest_moorings`.** Merel walks to `guest_moorings_b`.
- **"Someone Else's House" had one locked shot for two places.** It now cuts between **A15b** (the street) and **A15**
  (the front room), and Rhen has his own `front_room_b` and `street_b`.
- act2_ch13 §7's A03 said Kerrid *sits* among the polers. ADR 0204 has him **stand** until Ch15: the row is corrected.

## 0b. Ids the greybox already uses for something else (replace in the staging file)
- **ansedra:**
  - **A03**: the greybox's is Sefir's door, but the script wants Kerrid stepping off at the moorings.
  - **A04**: the greybox's is far up by FromSanctum, but the script wants Sefir at his door. The greybox's A03 is
    actually that framing.
  - **A05**: the greybox's is at `pact_sefir`.
  - **A06**: the greybox's is Corran's house.
  - A01 and A02 fit: keep them.
- **sanctum:** **S02** must frame Liss at the rim; S01 fits.
- **lamp_archive:** R01–R03 fit (R02 and R03 are the reader UI anyway).
- **New ids:** A07, A08, A11–A15 and A15b; S03–S09; R04–R10.

## Pacing against §1
| Beat | §1 | Now | Where the time goes |
|---|---|---|---|
| B01–B02 still city, the house | 3.5 | 1.24 | A01 8 s with nothing moving on the water; **A05 is half a beat** (≈0.8 s), no longer |
| B03 Tobin | 3.0 | 0.62 | the lift and Liss's laugh play out (~5 s) before 002 |
| B05–B06 Sanctum, Ethren | 6.5 | 0.86 | **S02 holds past comfort (≥ 8 s)**; S05's rise without a ripple ≥ 6 s; S09 2 s before 002 |
| B07–B09 the Archive | 12.0 | 1.32 | the reader pages are read by the player (UI-paced); **R08 is slow** |
| B10–B11 the pact, the book | 3.0 | 1.23 | 2 s after 009 ("Somebody has to go first."); **R10 is one continuous shot, no gloat** |
| B12 the house | 4.0 | 0.76 | Ysolde's laugh at 006 is the first in the game: give it 2 s before the householder speaks |

## Per scene

#### `ch13_still_city`

B01–B02. The greybox's A01 (the long view from the moorings) and A02 fit: keep them. **Replace A03–A06**: the greybox's A03 is Sefir's door, its A04 is at the far end by FromSanctum, its A05 is at `pact_sefir` and its A06 is Corran's house. Kerrid's mark is now the layout's `kerrid_moorings`, so he and Tobin no longer share `outer_moorings` (fixed in the script). **Nothing on the water moves in any shot; A05 is half a beat.** The node `ch13_sefirs_house` starts with the party walked up to `hs_*` by the flow, or with a cut.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| A01 | 24 mm low over the water, domes doubled (greybox A01: keep); `[0.0, 2.5, 16.0]` → `[0.0, 6.0, -94.0]`, 60° | — | no line |
| A02 | 50 mm, the outer moorings, a poler's stroke leaving no wake (greybox A02: keep); `[6.5, 1.6, 3.5]` → `[20.0, 3.0, -60.0]`, 27° | rhen | `city_001` rhen off frame (intended) |
| A03 | 35 mm, Kerrid stepping off and **standing** among the polers; Asha looking back; `[-5.79, 1.6, 6.2]` → `[-3.5, 1.4, 12.5]`, 38° | kerrid_moorings, asha | no line |
| A04 | 50 mm, Sefir at his door, no idle motion; `[5.0, 1.6, -40.9]` → `[5.0, 1.4, -42.4]`, 27° | sefir_door | `house_001` sefir in frame; `house_002` sefir in frame; `house_003` sefir in frame; `house_004` sefir in frame; `house_005` sefir in frame; `house_006` sefir in frame |
| A05 | 85 mm, Sefir's half-beat glance toward the outer moorings; `[4.25, 1.6, -41.1]` → `[5.0, 1.4, -42.4]`, 16° | sefir_door | no line |
| A06 | 50 mm, Toma's bow: 'Be level' / 'And still' (both in frame); `[0.81, 1.6, -39.1]` → `[4.1, 1.4, -41.0]`, 27° | sefir_door, hs_toma | `house_007` sefir in frame; `house_008` toma in frame |

#### `ch13_tobin`

B03. Merel now walks to `guest_moorings_b`, beside Tobin rather than on his mark (fixed in the script).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| A07 | 35 mm, Tobin off the Hollowmere barge, lifting Liss; `[6.99, 1.6, 8.79]` → `[7.5, 1.4, 10.2]`, 38° | guest_moorings, liss_greet | `tobin_001` tobin in frame; `tobin_002` liss in frame; `tobin_003` tobin in frame |
| A08 | 85 mm insert, Merel's palm to Liss's, then **50 mm** on the four for the talk; `[5.82, 1.6, 6.05]` → `[7.5, 1.4, 10.65]`, 27° | guest_moorings, guest_moorings_b, liss_greet, rhen_greet | `tobin_004` merel in frame; `tobin_005` liss in frame; `tobin_006` tobin in frame; `tobin_008` tobin in frame; `tobin_010` tobin in frame |

#### `ch13_ethren`

B05–B06. The greybox's S01 (the basin from the nave) fits: keep. **Replace S02** so it frames Liss at `basin_rim` looking down. Ethren rises at the layout's `corran` mark (the basin before `basin_ysolde`). **S02 holds past comfort; the light rises off the mirror without a ripple.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| S01 | 24 mm high, the mirror lit from beneath, pilgrims kneeling (greybox S01: keep); `[0.0, 1.6, -16.0]` → `[0.0, 0.5, -40.0]`, 60° | — | no line |
| S02 | 50 mm then 85 mm, **Liss at the rim looking down at the light**, held; `[1.3, 1.6, -35.85]` → `[2.6, 1.4, -36.6]`, 27° | basin_rim | no line |
| S03 | 85 mm, Ysolde and Asha, hands; `[8.88, 1.4, -37.1]` → `[6.95, 1.4, -39.4]`, 16° | basin_ysolde, sa_asha | `ethren_001` ysolde in frame |
| S04 | 100 mm insert, the gilt line painted (as act1_ch09 N06); `[7.7, 1.2, -38.45]` → `[6.4, 1.4, -39.2]`, 14° | sa_asha | no line |
| S05 | 35 mm low over the basin, Ethren rising out of the mirror without a ripple; `[6.2, 0.4, -41.25]` → `[7.5, 1.4, -42.0]`, 38° | corran | no line |
| S06 | 85 mm, Ysolde before him, then insert on the ring; `[9.0, 1.6, -40.6]` → `[7.5, 1.4, -40.6]`, 16° | before_ethren | no line |
| S07 | 35 mm, the binding, the light rising to the staff; `[9.89, 1.6, -38.9]` → `[6.95, 1.4, -40.6]`, 38° | sa_asha, corran | no line |
| S08 | 85 mm, the veiled head turning to Ysolde; `[6.99, 2.0, -43.41]` → `[7.5, 1.4, -42.0]`, 16° | corran | no line |
| S09 | 85 mm, Ysolde, eyes shut; `[8.01, 1.6, -39.19]` → `[7.5, 1.4, -40.6]`, 16° | before_ethren | `ethren_002` ysolde in frame |

#### `ch13_archive_ledgers`

B07. R01 (greybox: keep) and R02, the document reader (UI). The record lines are narration on the reader. Spoken lines over the reader are voices on purpose; the reader is the shot.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| R01 | 24 mm, lacquer cases, red shelves, the lectern at the end (greybox R01: keep); `[0.0, 2.2, -4.0]` → `[0.0, 1.0, -24.0]`, 60° | — | no line |
| R02 | the document reader (UI) with a ledger spread; `[-2.91, 2.02, -12.0]` → `[-1.5, 0.9, -12.0]`, 35° | — | `ledgers_001` ysolde off frame (intended); `ledgers_002` liss off frame (intended); `ledgers_003` ysolde off frame (intended); `ledgers_004` liss off frame (intended) |

#### `ch13_archive_roll`

B08. **R04 is the chapter's key insert.** R05 is written as two 85 mm singles; if it stays one shot, it's the 50 mm two-shot below.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| R03 | the Cantor roll in the reader (UI); `[1.5, 3.45, -23.51]` → `[1.5, 0.9, -24.0]`, 40° | — | no line |
| R04 | 100 mm insert, Corran's line and the margin, from the reader into the page; `[3.2, 1.2, -22.5]` → `[3.2, 1.4, -24.0]`, 14° | cantor_roll | no line |
| R05 | Ysolde and Asha (85 mm singles, or this 50 mm two-shot); `[4.59, 1.5, -23.25]` → `[2.6, 1.4, -24.4]`, 27° | roll_ysolde, roll_asha | `roll_001` ysolde in frame; `roll_002` ysolde in frame; `roll_003` ysolde in frame; `roll_004` asha in frame; `roll_005` ysolde in frame |
| R06 | 50 mm, Ysolde's hands flat on the lectern, Liss beside her; `[4.45, 1.5, -23.4]` → `[3.7, 1.4, -24.7]`, 27° | roll_ysolde, beside_ysolde | no line |

#### `ch13_archive_hands`

B09. **R08 is slow: let the player read the hands.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| R07 | the reader: pages side by side, signatures marked (UI); `[-2.91, 2.02, -12.0]` → `[-1.5, 0.9, -12.0]`, 35° | — | no line |
| R08 | 35 mm pull-out from above, eight pages in a row, the same hand; `[-1.7, 4.9, -12.0]` → `[-3.2, 2.3, -12.0]`, 38° | table_pages | no line |
| R09 | 35 mm, the party round the table; `[-0.17, 1.7, -10.35]` → `[-2.85, 1.4, -11.9]`, 38° | ar_asha, ar_ysolde, ar_liss, ar_rhen | `hands_001` asha in frame; `hands_002` ysolde in frame; `hands_003` ysolde in frame |

#### `ch13_the_pact`

B10–B11. Kerrid is standing where he always stands (`kerrid_moorings`); he turns when they come. Tobin arrives at `outer_moorings`. **R10 is one continuous shot if it can be, with no gloat.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| A11 | 35 mm, the outer moorings at night, Kerrid standing as they come; `[-0.72, 1.7, 11.07]` → `[-4.2, 1.4, 12.33]`, 38° | kerrid_moorings, pact_rhen, pact_toma, pact_ysolde, pact_asha, pact_liss | `pact_001` liss in frame; `pact_002` toma in frame; `pact_003` rhen in frame; `pact_004` ysolde in frame; `pact_005` asha in frame |
| A12 | 50 mm, Tobin arriving; 'No.' (Liss in frame with him); `[-0.55, 1.6, 9.5]` → `[-2.8, 1.4, 10.8]`, 27° | outer_moorings, pact_liss | `pact_006` tobin in frame; `pact_007` tobin in frame; `pact_008` tobin in frame; `pact_009` tobin in frame; `pact_010` liss in frame; `pact_011` tobin in frame |
| A13 | 85 mm, Kerrid watching the still water; `[-4.7, 1.6, 14.75]` → `[-6.0, 1.4, 14.0]`, 16° | kerrid_moorings | no line |
| A14 | 18 mm wide, the party small on the moorings, the still city behind; `[-3.23, 3.0, 15.48]` → `[-4.5, 1.4, 12.0]`, 75° | kerrid_moorings, outer_moorings | no line |
| R10 | 50 mm then 35 mm, Sefir alone squaring the pages, closing the ledger, putting out the lamp; `[0.96, 1.6, -18.85]` → `[0.0, 1.4, -20.0]`, 27° | reading_table | no line |

#### `ch13_someone_elses_house`

B12 side scene. The script now cuts between **A15b** (the street, lines 001–005 and 009) and **A15** (the front room, locked, with an insert on the scorch mark). Rhen has his own marks (`front_room_b`, `street_b`).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| A15b | 50 mm on the street outside the house, the door in frame; `[-40.02, 1.6, -37.38]` → `[-42.33, 1.4, -40.13]`, 27° | street, street_b, door | `house_side_001` ysolde in frame; `house_side_002` ysolde in frame; `house_side_003` rhen in frame; `house_side_004` ysolde in frame; `house_side_005` ysolde in frame |
| A15 | 50 mm locked, the front room and the scorch mark (insert on the mark); `[-43.09, 1.6, -40.96]` → `[-44.25, 1.4, -44.15]`, 27° | front_room, front_room_b, door, scorch | `house_side_006` ysolde in frame; `house_side_007` householder in frame; `house_side_008` ysolde in frame |
| A15b | 50 mm on the street outside the house, the door in frame; `[-40.02, 1.6, -37.38]` → `[-42.33, 1.4, -40.13]`, 27° | street, street_b, door | `house_side_009` ysolde in frame |
