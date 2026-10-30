# Ch16 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30 (Lead request). They pair with `game/data/dialogue/ch16/` and
[act2_ch16.md](act2_ch16.md) (§1, §7). The method is the same as [act2_ch12_direction.md](act2_ch12_direction.md):
every coordinate is in the greybox frame and every spoken line was checked against its shot (25 lines in frame, 4 deliberately off).
They are proposals: move anything, but keep **who is in frame** as written.

## 0. Fixed in the scripts today (story's own files)
- **`ch16_the_choir`:**
  - **Asha, Toma and Rhen all walked to `kesh`**, the Saint's own mark in the bowl, so they would have stood inside
    Kesh. Asha now walks to new **`dais_asha`** (0, 0, −17.4), and Toma and Rhen run to **`dais_toma`** and
    **`dais_rhen`**.
  - **Ysolde, Liss, Pell and Kerrid were never moved onto the dais**, yet Ysolde and Kerrid speak to Sefir there. In
    B06 they now walk to `dais_ysolde`, `dais_liss`, `dais_pell` and **`dais_kerrid` (behind)**.
  - Sefir's `015` ("You loved him.") cuts back to **C12**, so his answer to Ysolde is on his face.

## 0b. Ids
- **drowned_choir:** the greybox's D01–D07 aren't cued by any script, so there's no collision. They're usable
  references: D01 is the approach wide (C01 above uses its position), and D04, D06 and D07 frame `ring_asha`,
  `ring_ysolde` and `ring_kerrid`.
- **P04:** `ch16_swept_away` (zone drowned_choir) cues **P04, the Iskarra vigil** (the beat sheet's id). The
  **pale_rim** layout has its own, unrelated P04. Both are legal because ids are per zone, but name the vigil
  `P04_vigil` in the staging file if that helps, and change the cue to match.
- **pale_rim:** P01–P04 aren't cued by a script. **New ids:** W01, W02 (B01). W03–W06 are the play rail and montage
  cuts (B02).
- **New marks:** the ship's deck and rail (the layout has no ship), `wade_1`…`wade_7`, `ring_pell` (the layout's ring
  has six), `channel_edge`, the seven `dais_*` and `sefir_barge`.

## Pacing against §1
| Beat | §1 | Now | Where the time goes |
|---|---|---|---|
| B01 the ship waits | 1.0 | 0.22 | let the seven walk off in order, Kerrid last; hold W02 until he is in the water |
| B03–B07 ring, Kesh, the memory, "She's in it.", the High Warden | 11.5 | 3.61 | **C01 ≥ 6 s**; C05's rise in full; **K07's face must read**; C09 4 s with Kerrid looking south; **C13 ≥ 3 s on the smile**; reverses on Asha between Sefir's long lines |
| B10–B12 swept away, the act break, the card | 2.2 | 0.55 | **hard cuts, no slow motion**; the cut to P04 is hard, as in Ch9; 4 s after the voice-over |

## Per scene

#### `ch16_ship_waits`

B01. The layout has no ship: anchor it about 10 m west of the `Rim` spawn, deck at (−34, 1.2, 0). The wade marks `wade_1`…`wade_7` (new) run east in a line 1.8 m apart, in the script's order, **Kerrid last** (`wade_7`, nearest the ship).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| W01 | 24 mm wide, the ship at anchor where the sea goes pale; the captain at the rail, small; `[-32.75, 2.4, 1.8]` → `[-33.5, 2.6, 0.5]`, 60° | ship_deck, ship_rail | `ship_001` hull_captain in frame |
| W02 | 35 mm over the side: Liss handing down the lamp box, then the party going into the shallows; Kerrid last; `[-29.51, 1.6, 5.99]` → `[-31.67, 1.4, 0.07]`, 38° | liss_rail, ship_rail, wade_6 | `ship_002` liss in frame |

#### `ch16_the_choir`

B03–B07. The party enters on the layout's `ring_*` marks (add `ring_pell` (−0.6, 0, −4.4): the layout has six). **Asha walks to new `channel_edge` (0, 0, −8.5), then to new `dais_asha` (0, 0, −17.4)**: the script sent her, Toma and Rhen to `kesh`, the Saint's own mark in the bowl (fixed). In B06 Toma and Rhen run and the other four walk to new `dais_*` marks, so all seven are on the dais for Sefir; **Kerrid behind, at `dais_kerrid`**. Sefir walks from the new `sefir_barge` (9, 0, −22) to the layout's `sefir` (5, 0, −17), and back.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| C01 | 18 mm low on the water, the moon between two singers' heads; **hold ≥ 6 s**; `[0.0, 0.4, 22.0]` → `[0.0, 6.0, -26.0]`, 75° | — | no line |
| C02 | 24 mm tracking, walking in between two singers; `[-0.07, 1.6, -8.93]` → `[-0.75, 1.4, -7.05]`, 60° | ring_asha, channel_edge | no line |
| C03 | 85 mm, Asha at the channel's edge; `[-0.51, 1.6, -9.91]` → `[0.0, 1.4, -8.5]`, 16° | channel_edge | `choir_001` asha in frame |
| C04 | 35 mm, the guardians at the channel's edge, Kerrid last behind them, Asha walking on alone; `[-2.35, 1.8, -3.0]` → `[-0.6, 1.4, -6.03]`, 38° | ring_rhen, ring_kerrid, channel_edge | no line |
| C05 | 18 mm looking up, **Kesh rising** from the bowl; `[1.5, 0.6, -14.0]` → `[0.0, 6.0, -20.0]`, 75° | — | no line |
| C06 | 24 mm, ten mouths singing; then an insert on the sleeve at S7; `[5.78, 1.0, -36.58]` → `[0.0, 1.4, -20.7]`, 60° | dais_asha, singers | no line |
| C07 | 50 mm, Kesh's hand on Asha's forehead; white; `[1.5, 1.6, -17.4]` → `[0.0, 1.4, -17.4]`, 27° | dais_asha | no line |
| K01 | the memory (desaturated to white, soft edges, no UI): the sea a thousand years ago; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |
| K02 | the six Lamplighters, Kesh in the middle; the silver-haired man at her shoulder, unnamed; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |
| K03 | Kesh singing; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |
| K04 | inside the storm: held motes closing round her; **Kesh's voice only**; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | `memory_001` kesh off frame (intended) |
| K05 | forty years in seconds; her light pushed out and **lifting** (the chapter's only rising light); `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |
| K06 | a hand closes on it: Sefir, young, weeping (Kesh's voice over); `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | `memory_002` kesh off frame (intended) |
| K07 | **his face in his hands must read**: the thread runs in and his face goes smooth. Shown, never said; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 27° | — | no line |
| K08 | white (Kesh's voice over); `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | `memory_003` kesh off frame (intended) |
| C08 | 35 mm, Asha on her knees on the dais; the others crossing the channel; `[9.87, 1.6, -16.54]` → `[0.0, 1.4, -12.95]`, 38° | dais_asha, channel_edge | no line |
| C09 | 85 mm on Asha looking south, then 50 mm with Kerrid behind, looking south too; `[-1.94, 1.4, -19.85]` → `[-0.5, 1.4, -15.9]`, 27° | dais_asha, dais_kerrid | `inside_001` asha in frame; `inside_002` asha in frame |
| C10 | 24 mm low over the water, Sefir's white barge with no wake; `[10.3, 0.4, -21.25]` → `[9.0, 1.4, -22.0]`, 60° | sefir_barge | no line |
| C11 | 50 mm, Sefir on the dais over the party's shoulders (**no breathing idle**); Toma's back at the frame's edge for `004`; `[-5.45, 1.7, -19.27]` → `[1.6, 1.4, -16.7]`, 27° | sefir, dais_toma | `sefir_001` sefir in frame; `sefir_002` sefir in frame; `sefir_003` sefir in frame; `sefir_004` toma in frame; `sefir_005` sefir in frame |
| C12 | 85 mm Sefir single (the temptation); reverse on Asha between lines; used again for `015`; `[3.51, 1.6, -17.13]` → `[5.0, 1.4, -17.0]`, 16° | sefir | `sefir_006` sefir in frame; `sefir_007` sefir in frame |
| C13 | 85 mm, **Sefir's smile held ≥ 3 s**; Ysolde's line comes over it; `[3.51, 1.6, -16.87]` → `[5.0, 1.4, -17.0]`, 16° | sefir | `sefir_008` ysolde off frame (intended) |
| C14 | 85 mm, Asha's refusal; `[1.45, 1.6, -17.01]` → `[0.0, 1.4, -17.4]`, 16° | dais_asha | `sefir_009` asha in frame; `sefir_010` asha in frame; `sefir_011` asha in frame |
| C15 | 85 mm, Ysolde; `[2.89, 1.6, -15.87]` → `[1.4, 1.4, -16.0]`, 16° | dais_ysolde | `sefir_012` ysolde in frame; `sefir_013` ysolde in frame; `sefir_014` ysolde in frame |
| C12 | 85 mm Sefir single (the temptation); reverse on Asha between lines; used again for `015`; `[3.51, 1.6, -17.13]` → `[5.0, 1.4, -17.0]`, 16° | sefir | `sefir_015` sefir in frame |
| C16 | 50 mm from behind the party: Kerrid's line, **no hand near his weapon**; Sefir's look and 'Captain.'; `[-1.81, 1.7, -13.5]` → `[2.0, 1.4, -15.7]`, 27° | dais_kerrid, sefir | `sefir_016` kerrid in frame; `sefir_017` sefir in frame |
| C17 | 35 mm, Sefir lifting a hand, the guard coming into the water; `[2.24, 1.6, -16.75]` → `[7.0, 1.4, -19.5]`, 38° | sefir, sefir_barge | `sefir_018` sefir in frame |
| C18 | 50 mm, Asha standing up; `[1.48, 1.2, -17.14]` → `[0.0, 1.4, -17.4]`, 27° | dais_asha | no line |

#### `ch16_swept_away`

B10–B12. Hard cuts, no slow motion, no dialogue in the Choir. **P04 here is the Iskarra vigil** (as act1_ch09's P02, 10% tighter); it's staged in `ch16/drowned_choir`'s cutscene file and is **not** the pale_rim layout's P04. Name it `P04_vigil` in the staging file if the two would be confused.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| S01 | 18 mm, the storm wall over the edge of the world, swallowing the singers' heads; `[0.0, 1.0, -6.0]` → `[0.0, 8.0, -40.0]`, 75° | — | no line |
| S02 | 35 mm, **Kerrid on the line**; then an 85 mm insert, Rhen's hand on Asha's; `[2.0, 1.6, -17.26]` → `[-0.63, 1.4, -16.3]`, 38° | dais_kerrid, dais_asha, dais_rhen | no line |
| S03 | 24 mm, white water over the dais; `[0.75, 3.0, -16.1]` → `[0.0, 1.4, -17.4]`, 60° | dais_asha | no line |
| S04 | black; the sea (sound only); `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |
| P04 | the Iskarra vigil, deeper dusk, the burner lower; Rhen's voice-over; `[0.0, 1.6, -60.0]` → `[0.0, 1.6, -70.0]`, 38° | — | no line |

## Audio cues by shot (for audio)

Every `@music` and `@sfx` in the chapter's scenes, in script order, with the shot it lands on and what follows it
(the next line or hold). A music change marked `fade=0.0` is a hard cut. Barks, camps and shrines play in the field and
are left out. A shot of — means the cue plays before the node's first shot, over the fade.

| Scene | Shot | Cue | Then |
|---|---|---|---|
| `ch16_ship_waits` | W01 | `@music pale_rim fade=2.0` | hold 2.0 s |
| `ch16_swept_away` | S01 | `@music abiding_guard fade=0.0` | @sfx undertow_wall_roar |
| `ch16_swept_away` | S01 | `@sfx undertow_wall_roar` | hold 3.0 s |
| `ch16_swept_away` | S02 | `@sfx current_song at=storm vol=0.3` | hold 2.5 s |
| `ch16_swept_away` | S03 | `@music silence fade=0.0` | @fade out 0.5 |
| `ch16_swept_away` | P04 | `@music act2_break fade=2.0` | hold 3.0 s |
| `ch16_swept_away` | P04 | `@music silence fade=2.0` | <<set $ch16_act_two_complete = true>> |
| `ch16_the_choir` | C01 | `@music drowned_choir fade=3.0` | hold 6.0 s |
| `ch16_the_choir` | C05 | `@sfx kesh_rise` | hold 5.0 s |
| `ch16_the_choir` | C06 | `@music kesh_bound fade=0.0` | hold 8.0 s |
| `ch16_kesh_memory` | — | `@music kesh_memory fade=1.0` | @fade in 1.5 white |
| `ch16_kesh_memory` | K06 | `@music silence fade=0.0` | hold 3.0 s |
| `ch16_kesh_memory` | K07 | `@music kesh_memory fade=1.0` | cut to K08 |
| `ch16_shes_in_it` | — | `@music silence fade=0.0` | cut to C08 |
| `ch16_the_high_warden` | C10 | `@sfx barge_pole` | hold 4.0 s |
| `ch16_the_high_warden` | C11 | `@music sefir_go_home fade=3.0` | `ch16_sefir_001` Sefir |
| `ch16_the_high_warden` | C13 | `@music silence fade=0.0` | hold 4.0 s |
