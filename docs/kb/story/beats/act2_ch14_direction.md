# Ch14 cutscene direction notes: beats, blocking, who's in frame on each line (for cinematics)

The story track wrote these on 2026-10-30 (Lead request). They pair with `game/data/dialogue/ch14/` and
[act2_ch14.md](act2_ch14.md) (§1, §7). The method is the same as [act2_ch12_direction.md](act2_ch12_direction.md):
every coordinate is in the greybox frame and every spoken line was checked against its shot (25 lines in frame, none off).
They are proposals: move anything, but keep **who is in frame** as written.

## 0. Fixed in the scripts today (story's own files)
- **`ch14_first_ripple`:** Merel walked to a new `gate_footing`. She now walks to the layout's **`merel_gate`**, which
  is the same place.

## 0b. Ids the greybox already uses for something else (replace in the staging file)
- **ansedra_lacquer_court** (in `game/levels/ch13/`, staged in `game/data/cutscene/ch14/ansedra_lacquer_court.json`):
  **replace W03–W07.**
  - The greybox's W03 is a high side wide.
  - Its W04 sits on Sefir's own spot, looking out.
  - Its W05 is low by `tobin_falls`.
  - Its W06 and W07 look between the steps and the barge.
  - The script wants the low establishing wide, Sefir officiating, the couple, Liss, and the Conclave gallery.
- W01 and W02 belong to B01 (play) and aren't cued by a script.
- **New ids:** W08–W15, L01–L12.

## Pacing against §1
| Beat | §1 | Now | Where the time goes |
|---|---|---|---|
| B02–B05 the vows → Tobin | 7.5 | 1.80 | **W03 ≥ 5 s with nothing moving on the water**; W08 plain coverage, no push-in; after Toma's `aside_003` hold the silence 2 s; W14 lets him sit down in real time (no slow motion) |
| B07–B08 the first ripple, Merel | 4.0 | 0.79 | **L02 ≥ 6 s** (the hero image); L05 held until the far windows are lit; **L09 held from the barge**, nobody looks away |
| B10 left standing | 1.5 | 0.28 | L10 3 s, plain; L11 astern then ahead; L12 runs into the fade |

## Per scene

#### `ch14_the_vows`

B02–B05, one scene with a node per beat; **hard cuts, and the court never hands the camera back**. **Replace the greybox's W03–W07** in `game/data/cutscene/ch14/ansedra_lacquer_court.json` (the court is in ch13's level folder). The greybox's W03 is a high side wide, its W04 sits on Sefir's own spot looking out, its W05 is low by `tobin_falls`, and its W06 and W07 look between the steps and the barge.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| W03 | 24 mm low over the water: the court, the dais and the domes doubled; **nothing moves on the water; hold ≥ 5 s**; `[0.0, 0.4, -19.95]` → `[0.0, 1.4, -15.75]`, 60° | vows, court_rhen | no line |
| W04 | 50 mm, Sefir officiating, **no idle motion on him**; `[0.38, 1.6, -17.28]` → `[0.0, 1.4, -19.45]`, 27° | sefir_dais, vows | `vows_001` sefir in frame; `vows_002` sefir in frame |
| W05 | 85 mm two-shot, Tobin and Merel at the water's edge (insert on the cord); `[-0.63, 1.5, -14.95]` → `[0.0, 1.4, -18.5]`, 16° | merel_vows, tobin_vows | `vows_003` merel in frame; `vows_004` tobin in frame |
| W06 | 50 mm, Liss in the front row, Rhen bumping her shoulder; `[2.7, 1.5, -16.85]` → `[1.3, 1.4, -13.0]`, 27° | court_liss, court_rhen | no line |
| W07 | 35 mm low from the dais: the Conclave's gallery, four figures standing at once; `[-4.22, 3.0, -19.1]` → `[-6.3, 4.0, -20.3]`, 38° | conclave_gallery, venn_rail | no line |
| W08 | 85 mm, Venn at the rail reading; **plain coverage: no low angle, no strange light**; `[-4.19, 4.8, -19.09]` → `[-5.6, 4.0, -19.6]`, 16° | venn_rail | `decl_001` malcor_venn in frame; `decl_002` malcor_venn in frame; `decl_003` malcor_venn in frame |
| W09 | 85 mm, Liss turning to look at Sefir; `[2.09, 1.5, -14.41]` → `[2.6, 1.4, -13.0]`, 16° | court_liss | `decl_004` liss in frame |
| W10 | 50 mm over-shoulder pair, Sefir to Asha; Asha's 'No.' (both in frame); `[-4.35, 1.6, -11.42]` → `[-1.3, 1.4, -16.7]`, 27° | sefir_dais, court_asha | `decl_005` sefir in frame; `decl_006` asha in frame |
| W11 | 50 mm two-shot, the commander at the dais foot and Toma with his shield up (then Toma's single; hold the silence); `[-4.77, 1.6, -13.7]` → `[-2.0, 1.4, -15.3]`, 27° | dais_foot, before_asha | `aside_001` brannoc_hale in frame; `aside_002` toma in frame; `aside_003` toma in frame |
| W12 | 85 mm on Ysolde, then 100 mm insert on the pin on the slabs; `[1.81, 1.6, -14.01]` → `[1.3, 1.4, -12.6]`, 16° | court_ysolde | `aside_004` ysolde in frame |
| W13 | 35 mm handheld, Merel at the guards; `[6.75, 1.5, -16.3]` → `[6.0, 1.4, -15.0]`, 38° | hull_captains | `tobin_fall_001` merel in frame |
| W14 | 50 mm, Tobin sitting down on the slabs; **wound framed out, no slow motion**; `[2.8, 1.1, -18.75]` → `[1.5, 1.4, -18.0]`, 27° | tobin_falls | `tobin_fall_002` tobin in frame |
| W15 | 50 mm, Liss's hands on him; Toma lifting her away; `[2.86, 1.2, -18.95]` → `[1.9, 1.4, -17.8]`, 27° | tobin_falls, liss_tobin | `tobin_fall_003` liss in frame |

#### `ch14_first_ripple`

B07–B08. Merel now walks to the layout's `merel_gate` (the script had a new `gate_footing`: fixed). **L02 is the chapter's hero image: hold ≥ 6 s. L09 is the cost: hold it from the barge, at the barge's distance; nobody on the barge looks away.**

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| L01 | 35 mm, the barge off the bottom step, the bridal cloth laid over him, Kerrid last onto the deck; `[1.5, 1.0, 9.5]` → `[0.0, 0.8, 9.5]`, 38° | barge_deck, bier | no line |
| L02 | 24 mm low behind the stern, the wake opening, the domes' reflections breaking; `[0.0, -0.3, 8.5]` → `[0.0, 0.8, 10.0]`, 60° | barge_deck | no line |
| L03 | 35 mm from the bow looking aft: the player's three strokes; `[0.4, 0.8, 13.3]` → `[0.4, 0.8, 10.0]`, 38° | stern, rhen_pole | no line |
| L04 | 85 mm insert, a dome's bell swinging; `[-12.0, 6.0, -30.0]` → `[-14.0, 14.0, -40.0]`, 16° | — | no line |
| L05 | 18 mm high, the city at its windows, held until the far windows are lit; `[0.51, 11.4, 8.59]` → `[0.0, 0.8, 10.0]`, 75° | barge_deck | no line |
| L06 | 35 mm, the water-gate; Rhen taking the pole; `[-1.6, 1.0, 13.5]` → `[2.4, 0.8, 13.5]`, 38° | rhen_pole, merel_gate | no line |
| L07 | 50 mm, Merel on the gate's footing, the barge alongside (Rhen and Liss in the frame's near edge); `[-4.27, 1.0, 10.48]` → `[1.37, 0.8, 12.53]`, 27° | merel_gate, rhen_pole, liss_barge | `gate_001` rhen in frame; `gate_002` merel in frame; `gate_003` liss in frame; `gate_004` merel in frame |
| L08 | 24 mm, the gate dropping, the wave; `[3.49, 1.4, 13.19]` → `[4.0, 0.8, 14.6]`, 60° | merel_gate | no line |
| L09 | 85 mm held through the gate's slats **from the barge**: Merel taken, the sleeve; `[3.49, 1.0, 13.19]` → `[4.0, 0.8, 14.6]`, 16° | merel_gate | no line |

#### `ch14_left_standing`

B10, no dialogue.

| Shot | Frame (cam → look, fov) | Subjects | Lines and who is in frame |
|---|---|---|---|
| L10 | 50 mm at the barge's height, Venn standing on his dead barge in the ripples; **plain**; `[-1.5, 0.6, 22.0]` → `[-3.0, 0.8, 22.0]`, 27° | venn_barge | no line |
| L11 | 24 mm, out through the lagoon mouth's moles; the lit city behind, the dark sea ahead (from astern, then ahead); `[0.0, 1.9, 8.5]` → `[0.0, 0.8, 10.0]`, 60° | barge_deck | no line |
| L12 | 50 mm, the cloth with Liss's hand on it, Kerrid at the stern, then fade; `[2.1, 0.8, 8.3]` → `[0.0, 0.8, 8.3]`, 27° | bier, stern | no line |
