# Ch15 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30 (Lead request). They pair with `game/data/dialogue/ch15/` and
[act2_ch15.md](act2_ch15.md) (§1, §7). The method is the same as [act2_ch12_direction.md](act2_ch12_direction.md):
every coordinate is in the greybox frame and every spoken line was checked against its shot (72 lines in frame, 1 deliberately off).
They are proposals: move anything, but keep **who is in frame** as written.

## 0. Fixed in the scripts today (story's own files)
- **`ch15_current_song` played two zones in one scene.** B09 is at sea and B10 is in Hollowmere, but a `.dlg` has one
  `location:`. B10 is now its own scene, **`ch15_the_dock_master`** (`ch17/hollowmere`): it opens with the letterbox
  and a fade in, and sets `ch15_liss_told_father` as before. `ch15_current_song` ends on
  `ch15_hollowmere_answered` with a fade out. **The chapter flow must play `ch15_the_dock_master` on arrival**
  (one line for Chapters; noted in the live log).
- **`ch15_the_shoal`:**
  - the party now stands on the layout's `reveal_asha`, `reveal_toma` and `reveal_ysolde` (the script had made up
    new marks);
  - **K18b** is added, a three-shot so Rhen is in frame when he joins Toma's talk with Kerrid;
  - **K19b** is added, the group round the bier, for the talk after Asha sits.
- **`ch15_current_song`:** Liss walks to the layout's `bow_liss`.
- **`ch15_let_me_carry_him`:** Toma comes down to the layout's `confess_toma`, and the three walk to their own jetty
  ends (`jetty_end_toma`, `jetty_end_liss`, `jetty_end_rhen`: they shared one).
- **`ch15_the_ship`:** each boards to their own `ship_deck_1`…`ship_deck_5` (they shared one).
- **`ch15_two_daces`:** Liss sits at the layout's `supper`.

## 0b. Ids the greybox already uses for something else (replace in the staging file)
- **open_sea** (`game/data/cutscene/ch15/open_sea.json`): **replace U01–U07.** They are close deck views: the
  greybox's U05 and U06 look at Kerrid's seat, and its U07 looks forward from the bow. The beat sheet's U01–U07 are a
  high wide, inserts, the fin and the sleeping party.
- **hollowmere** (`game/data/cutscene/ch17/hollowmere.json`): **replace H01–H04.** The greybox's H01 is the dock wide,
  its H02 the jetty, its H03 the view toward the pyre and its H04 the supper table. The script's H01–H03 are at sea.
  Its H04 is the Hollowmere wide.
- **New ids:** K01–K20 with K18b and K19b, H05, H06, H09–H16. U04 (the deck rail, play) and H07–H08 (play) aren't
  cued by a script.

## Pacing against §1
| Beat | §1 | Now | Where the time goes |
|---|---|---|---|
| B01 unlamped | 1.5 | 0.23 | **U01 8 s**; U02's insert 3 s, the hand on the pouch **not striking** |
| B03 the fin | 1.0 | 0.09 | U05 lets the glow line move the length of the frame; U06 one full circle |
| B05–B08 after, the shoal, the confession, still below | 9.0 | 4.5 (every branch) | **K05: Kerrid sits, held**; **K11 ≥ 3 s on Rhen, no line**; K19 the emission eases over ~6 s; K20 runs into the fade |
| B09 the current-song | 2.0 | 0.38 | H02 gives Liss a full phrase into the fog before the answer; H03 holds until the windmills read |
| B10 the dock-master | 2.0 | 0.33 | **H06 ≥ 8 s from the barge: nothing they say is heard** |
| B12 "Let me carry him." | 3.0 | 1.51 | **H10: Liss's step back is one shot**; H11 tracks the whole jetty |
| B13 the pyre-raft | 2.0 | 0.47 | H13 until the raft is small; **Pell's turn is the last shot** |
| B14 "Two Daces" | 4.0 | 1.27 | locked, in-engine and player-paced |
| B15 the ship | 1.0 | 0.18 | let Kerrid's gangway walk run, as on a stair |

## Per scene

#### `ch15_unlamped`

B01, no dialogue. **No lamp is struck.** **Replace the greybox's U01–U07** in `game/data/cutscene/ch15/open_sea.json`: they are close deck views (the greybox's U05 and U06 look at Kerrid's seat, and its U07 looks forward from the bow), while the beat sheet's U01–U07 below are a high wide, inserts, the fin and the sleeping party.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| U01 | 18 mm high wide, the barge small on black water, Ansedra's gold smear going under the horizon; `[3.25, 12.0, -5.23]` → `[0.0, 1.4, 0.4]`, 75° | bow, kerrid_stern | no line |
| U02 | 85 mm insert, the empty lamp hook; Rhen's hand on his tinder pouch, not striking; `[1.5, 1.8, -3.0]` → `[0.0, 3.0, -3.0]`, 16° | hook | no line |
| U03 | 50 mm low, the bier under the bridal cloth, the motes clinging, Liss's hand; `[3.5, 0.6, 2.4]` → `[-0.3, 1.4, 2.4]`, 27° | tobin_bier, reveal_liss | no line |

#### `ch15_the_fin`

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| U05 | 24 mm low over the rail, the sea-glow line moving off the bow; `[1.61, 0.4, -9.68]` → `[4.0, 1.4, -3.1]`, 60° | bow, fin | no line |
| U06 | 35 mm, the fin rising and circling (Pell's line is his voice over it); `[6.59, 1.2, -2.51]` → `[8.0, 1.4, -2.0]`, 38° | fin | `fin_001` pell off frame (intended) |

#### `ch15_the_shoal`

B06–B08, the reveal. **Kerrid sits for the first time (K05)**; nobody enters frame faster than walking; **K11 is never cut short** (≥ 3 s on Rhen's face, no line). The script now adds **K18b** (Rhen joins Toma and Kerrid's two-shot when he speaks) and **K19b** (the group round the bier for the talk after Asha sits). The party stands on the layout's `reveal_*` marks (the script used new ones: fixed). **No mote rises in any shot; every mote moves sideways.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| U07 | 35 mm wide, the party asleep sitting up, Kerrid standing at the stern; `[4.87, 1.8, 2.73]` → `[-0.93, 1.4, 2.73]`, 38° | reveal_asha, reveal_toma, kerrid_stern | no line |
| K01 | 24 mm looking down over the rail, the shoal's held lights on the sand; `[2.0, 1.5, 2.0]` → `[3.5, -1.6, 2.0]`, 60° | shoal | no line |
| K02 | 24 mm at deck height, motes coming off the water and drifting across the deck toward the stern; `[-0.63, 0.4, 6.07]` → `[0.4, 1.4, 3.25]`, 60° | tobin_bier, kerrid_stern | no line |
| K03 | 50 mm, Kerrid at the stern, the first motes orbiting him; `[-0.51, 1.6, 3.59]` → `[0.0, 1.4, 5.0]`, 27° | kerrid_stern | no line |
| K04 | 100 mm insert, his forearms, the scars bright, motes leaving sideways (glow ≤ 0.6); `[0.51, 1.0, 3.59]` → `[0.0, 1.4, 5.0]`, 14° | kerrid_stern | no line |
| K05 | 35 mm held, **Kerrid sits**; the party gathering into frame; `[0.0, 1.6, -2.07]` → `[0.0, 1.4, 2.33]`, 38° | kerrid_sits, reveal_asha, reveal_ysolde | `conf_001` kerrid in frame |
| K06 | 50 mm Kerrid single, mid; **his mouth must read through the beard**; `[0.0, 1.2, 2.7]` → `[0.0, 1.4, 4.2]`, 27° | kerrid_sits | `conf_002` kerrid in frame; `conf_003` kerrid in frame |
| K07 | 85 mm Kerrid single (the gate, Imra); `[-0.75, 1.2, 2.9]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_004` kerrid in frame; `conf_005` kerrid in frame |
| K08 | 85 mm Kerrid single (the diver's line); `[0.51, 1.2, 2.79]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_006` kerrid in frame; `conf_007` kerrid in frame |
| K09 | 50 mm Kerrid single (they never met); `[-0.51, 1.2, 2.79]` → `[0.0, 1.4, 4.2]`, 27° | kerrid_sits | `conf_008` kerrid in frame; `conf_009` kerrid in frame |
| K10 | 85 mm Kerrid single (the eighth day); `[0.0, 1.2, 2.7]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_010` kerrid in frame; `conf_011` kerrid in frame |
| K11 | 85 mm, **Rhen's face on his name**, held ≥ 3 s, no cut away; `[0.51, 1.2, 3.81]` → `[0.0, 1.4, 2.4]`, 16° | kerrid_opposite | no line |
| K12 | 85 mm, Kerrid's hands turned in the light (he speaks over his hands); `[0.96, 0.8, 3.05]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_012` kerrid in frame; `conf_013` kerrid in frame |
| K13 | 85 mm, his hands (the hand-line); `[-0.96, 0.8, 3.05]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_014` kerrid in frame; `conf_015` kerrid in frame |
| K14 | 85 mm, Kerrid to Rhen, gaze down 15° then up; `[-0.26, 1.2, 2.72]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_016` kerrid in frame |
| K15 | 85 mm, Kerrid to Asha; `[-0.96, 1.2, 3.05]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_017` kerrid in frame; `conf_018` kerrid in frame |
| K16 | 85 mm, Kerrid to Asha (grief); `[-1.15, 1.2, 3.24]` → `[0.0, 1.4, 4.2]`, 16° | kerrid_sits | `conf_019` kerrid in frame |
| K17 | 85 mm, Asha's hand to the comb, her eyes on Rhen's lantern (then insert on the lantern); `[-2.7, 1.4, 1.75]` → `[-1.4, 1.4, 1.0]`, 16° | reveal_asha | `conf_020` asha in frame |
| K18 | 50 mm two-shot, Toma standing: 'Your breath. In Ullar.' / 'Yes.'; `[-4.4, 1.6, 3.2]` → `[-0.7, 1.4, 3.2]`, 27° | reveal_toma, kerrid_sits | `conf_021` toma in frame; `conf_022` kerrid in frame; `conf_023` toma in frame; `conf_024` kerrid in frame |
| K18b | 35 mm, Toma, Kerrid and Rhen (the rest of the talk); `[-3.13, 1.6, 3.4]` → `[-0.47, 1.4, 2.93]`, 38° | reveal_toma, kerrid_sits, kerrid_opposite | `conf_025` rhen in frame; `conf_026` kerrid in frame; `conf_027` kerrid in frame; `conf_028` kerrid in frame; `conf_029` kerrid in frame; `conf_030` rhen in frame; `conf_031` kerrid in frame; `conf_032` kerrid in frame |
| K19 | 50 mm, Asha sitting down beside him, the motes slowing, stopping (the emission eases over ~6 s); `[-0.91, 1.2, 2.89]` → `[-0.4, 1.4, 4.3]`, 27° | kerrid_beside, kerrid_sits | no line |
| K19b | 35 mm, the group round the bier for the talk; `[0.28, 1.8, -0.62]` → `[0.28, 1.4, 2.98]`, 38° | kerrid_sits, reveal_liss, pell_deck, reveal_ysolde, kerrid_opposite | `below_001` liss in frame; `below_002` pell in frame; `below_003` ysolde in frame; `below_004` rhen in frame; `below_005` kerrid in frame; `below_006` rhen in frame; `below_007` kerrid in frame; `below_008` kerrid in frame |
| K20 | 24 mm high wide, the barge drifting on, the shoal dark behind, seven round a bier; `[2.48, 8.0, 1.65]` → `[0.4, 1.4, 2.85]`, 60° | tobin_bier, kerrid_sits | no line |

#### `ch15_current_song`

B09, now the open sea only (split 2026-10-30; B10 is `ch15_the_dock_master`, staged in Hollowmere). Liss walks to the layout's `bow_liss`.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H01 | 35 mm, grey fog, no horizon, Liss going to the bow; `[1.8, 1.6, -5.68]` → `[0.25, 1.4, -3.0]`, 38° | bow_liss, rhen_deck | no line |
| H02 | 50 mm on Liss singing into the fog, then Rhen's single turning behind her; `[4.15, 1.6, -5.25]` → `[0.25, 1.4, -3.0]`, 27° | bow_liss, rhen_deck | no line |
| H03 | 24 mm past the bow: the answer, hulls coming out of the white, windmills turning; `[0.0, 2.0, -30.0]` → `[0.0, 1.4, -17.2]`, 60° | bow_liss, fog_ahead | no line |

#### `ch15_the_dock_master`

B10 in `ch17/hollowmere`. **Replace the greybox's H01–H04** in `game/data/cutscene/ch17/hollowmere.json`. The greybox's H01 is the dock wide, its H02 the jetty, its H03 the view toward the pyre and its H04 the supper table. Here **H06 is from the barge, at a distance: nothing Liss and her father say is heard.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H04 | 24 mm wide, Hollowmere at dawn, the first oil lamps lit; `[6.89, 3.0, -30.57]` → `[15.0, 1.4, -8.3]`, 60° | dock_barge, fathers_door | no line |
| H05 | 85 mm, the dock-master at his door, looking at the canopy; `[27.25, 1.6, -15.3]` → `[28.0, 1.4, -16.6]`, 16° | fathers_door | no line |
| H06 | 50 mm **from the barge, at a distance**: Liss telling him (unheard), his hand on her head; `[2.6, 1.6, 0.8]` → `[28.0, 1.4, -16.6]`, 27° | — | no line |

#### `ch15_let_me_carry_him`

B12. Toma comes down to the layout's `confess_toma`, and each of the three walks to their own jetty-end mark (they had shared one). **Liss's choice is a step back from the board, held in one shot (H10).**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H09 | 35 mm, the jetty; Liss washing Tobin's hand; Toma coming down; `[58.72, 1.6, 3.08]` → `[58.13, 1.4, -0.27]`, 38° | confess_liss, tobin_jetty, confess_toma | `carry_001` toma in frame; `carry_002` toma in frame; `carry_003` toma in frame; `carry_004` toma in frame; `carry_005` toma in frame; `carry_006` toma in frame |
| H10 | 85 mm, Liss single, then Toma single (cut on the speaker; written as one shot, so frame both at 50 mm if it stays one); `[58.66, 1.6, 2.73]` → `[57.7, 1.4, 0.1]`, 27° | confess_liss, confess_toma | `carry_007` liss in frame; `carry_008` liss in frame; `carry_009` toma in frame |
| H11 | 35 mm tracking, Toma carrying Tobin down the jetty, Liss beside, hand on the cloth; `[59.15, 1.6, 1.2]` → `[59.9, 1.4, -0.1]`, 38° | jetty_end_toma, jetty_end_liss | no line |

#### `ch15_pyre_raft`

B13. **Pell's turn is the last shot.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H12 | 24 mm wide, the pyre-raft at dusk, the flotilla on every hull; `[49.65, 4.0, 4.7]` → `[55.25, 1.4, -5.0]`, 60° | pyre_raft, flotilla | no line |
| H13 | 35 mm, the raft lit and going out on the tide; `[59.2, 1.6, 0.75]` → `[60.5, 1.4, 0.0]`, 38° | pyre_raft | no line |
| H14 | 85 mm, the lamp-housing closing on the light, Liss holding it; then Pell's single, turning away; `[58.7, 1.4, -1.35]` → `[60.0, 1.4, -0.6]`, 16° | jetty_end_liss | no line |

#### `ch15_two_daces`

B14 side scene, one locked shot. Liss sits at the layout's `supper` (the script had a new `supper_table`: fixed).

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H15 | 50 mm locked, the supper table and the lamp; `[43.08, 1.5, 1.65]` → `[40.4, 1.4, 0.1]`, 27° | supper_father, supper_rhen, supper | `daces_001` aldous_varrow in frame; `daces_002` aldous_varrow in frame; `daces_003` rhen in frame; `daces_004` aldous_varrow in frame; `daces_005` aldous_varrow in frame; `daces_006` aldous_varrow in frame; `daces_007` aldous_varrow in frame; `daces_008` rhen in frame; `daces_009` rhen in frame; `daces_010` rhen in frame; `daces_011` aldous_varrow in frame; `daces_012` aldous_varrow in frame |

#### `ch15_the_ship`

B15. Each boards to their own `ship_deck_n` (they had shared one). **Kerrid last up the gangway, as on a stair.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| H16 | 35 mm, the ship readied, Kerrid last up the gangway (the dock-master's line on the quay in frame); `[11.76, 1.8, 12.65]` → `[16.0, 1.4, 10.2]`, 38° | dockmaster_quay, ship_gangway, ship_deck_1 | `ship_001` aldous_varrow in frame |

## Audio cues by shot (for audio)

Every `@music` and `@sfx` in the chapter's scenes, in script order, with the shot it lands on and what follows it
(the next line or hold). A music change marked `fade=0.0` is a hard cut. Barks, camps and shrines play in the field and
are left out. A shot of — means the cue plays before the node's first shot, over the fade.

| Scene | Shot | Cue | Then |
|---|---|---|---|
| `ch15_current_song` | H02 | `@music hollowmere_answers fade=0.0` | hold 3.0 s |
| `ch15_pyre_raft` | H12 | `@music hush_first_verse fade=3.0` | hold 5.0 s |
| `ch15_pyre_raft` | H13 | `@sfx hearth_crackle` | hold 4.0 s |
| `ch15_pyre_raft` | H13 | `@sfx lamp_housing_close` | hold 2.0 s |
| `ch15_pyre_raft` | H13 | `@sfx lamp_crack` | hold 3.0 s |
| `ch15_pyre_raft` | H14 | `@music silence fade=4.0` | <<set $ch15_pyre_raft = true>> |
| `ch15_the_dock_master` | H06 | `@music silence fade=3.0` | <<set $ch15_liss_told_father = true>> |
| `ch15_the_fin` | — | `@music silence fade=0.5` | @sfx fin_cut |
| `ch15_the_fin` | — | `@sfx fin_cut` | cut to U05 |
| `ch15_the_shoal` | U07 | `@music unlamped fade=1.0` | hold 4.0 s |
| `ch15_the_shoal` | K01 | `@music silence fade=3.0` | hold 3.0 s |
| `ch15_the_shoal` | K04 | `@music kerrid_at_sea fade=4.0` | hold 3.0 s |
| `ch15_the_confession` | K05 | `@sfx kerrid_sits` | hold 3.0 s |
| `ch15_still_below` | K20 | `@music silence fade=6.0` | hold 6.0 s |
| `ch15_unlamped` | U01 | `@music unlamped fade=2.0` | hold 5.0 s |
