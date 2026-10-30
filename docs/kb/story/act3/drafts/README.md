---
draft: pre-gate
---
# Act III draft scripts: Ch17 and Ch18 (planning only)

**Not wired into the game.** These are draft `.dlg` scripts written from the Act III beat sheets
([act3_ch17.md](../act3_ch17.md), [act3_ch18.md](../act3_ch18.md)) at the Lead's request, 2026-10-30. Act III
production stays paused (ADR 0203/0205). Nothing under `game/` reads them: dlgc compiles only
`game/data/dialogue/`, and no flag, loc row, shot, mark or music cue they name has been added to the game.

They use the Act II format: a header comment with the beat, the sheet section and the rules; one scene per file, whose
first node title is the file name; line ids `chNN_<scene>_NNN`; British spelling with Oxford -ize (ADR 0206).

## Checks
`python3 docs/kb/story/act3/drafts/check_drafts.py` runs the Act II checks without touching the game.
1. **dlgc**, on a temporary copy of `game/data` with the drafts added: syntax, cues and arguments, events, speakers,
   emotions, choices, conditions, line ids unique across the whole game, and words per line.
2. **The Act II runtime rules, checked statically:** the letterbox is off wherever a node ends; glimmer light (released
   rises, held never rises, bound is still).
3. **The Act III rules** ([../README.md](../README.md)):
   - nothing rises before H09 except the one Kirru-way lifting (`ch18_backs_to_the_water`);
   - no line in Dace's voice;
   - no "revenant" before Ch19;
   - no Eighth Verse sung;
   - every flag is declared in `flags.tres` or in the table below.
4. **Banned terms:** `tools/validate_data.py` already scans `docs/kb/story/` and every `.dlg` file.

**Result (2026-10-30):** 27 files, 0 errors, 0 warnings. validate_data 0/0. A planted bad file (a rising mote, a
letterbox left on, a line for Dace, an undeclared flag) trips all five rules.

## Files by beat
| Beat | File | Mode | Notes |
|---|---|---|---|
| Ch17 B01 | `ch17/ch17_pulled_from_the_sea.dlg` | C | Kerrid hauled up last; the captain hands back Tobin's lamp ("Kept it dry.") |
| Ch17 B03 | `ch17/ch17_dock_master_points.dlg` | C | the dock-master never speaks |
| Ch17 B04 | `ch17/ch17_hull_sails.dlg` | P | three interactables, one node each: sails, tool rack, chart wall |
| Ch17 B05 | `ch17/ch17_the_ledger.dlg` | E | 17 page captions (read, never voiced); Rhen's name on every page; three blank pages |
| Ch17 B06 | `ch17/ch17_after_the_blank_page.dlg` | C | Kerrid's one line; Rhen silent |
| Ch17 B07 | `ch17/ch17_first_berth.dlg` | E (optional) | the dock-master's first words; a choice if `ch14_spoke_with_tobin` |
| Ch17 B08 | `ch17/ch17_the_choice.dlg` | C | Asha chooses; one line each; Liss last |
| Ch17 B09 | `ch17/ch17_bark_kesh_chosen.dlg` | bark | Kesh's call bark changes (T-13) |
| Ch17 B10 | `ch17/ch17_the_first_lamp.dlg` | E | three held inputs; the lamp is bound light, said once |
| Ch17 B11 | `ch17/ch17_ysoldes_table.dlg` | C | the count, the stones, a blank page for the tune (T-04) |
| Ch17 B02, B12 | `ch17/ch17_bark_lookout.dlg` | barks | five nodes: lookout, record-keeper, chandler, Pell, Liss |
| Ch18 K01 | `ch18/ch18_maiden_flight.dlg` | C → P | three held inputs; "He'd have hated the trim." |
| Ch18 K02 | `ch18/ch18_the_chart_table.dlg` | E | the world opens |
| Ch18 K03–K04 | `ch18/ch18_through_the_gate.dlg` | C | Pell in first; the new shell; his back to the old one |
| Ch18 K05 | `ch18/ch18_farewell_tide_taught.dlg` | E | wordless; held input on the turn; "That's the Letting."; Asha's lullaby back |
| Ch18 K06 | `ch18/ch18_child_older.dlg` | E (optional) | needs `ch10_child_asked` |
| Ch18 K07 | `ch18/ch18_night_aboard.dlg` | E | one follow-up per camp pair seen; generic if none |
| Ch18 K08 | `ch18/ch18_iskarra.dlg` | C | Kerrid's finger on the city |
| Ch18 §4 | `ch18/ch18_backs_to_the_water.dlg` | C (optional, flagged) | Haluna lifts its own; a few motes rise, most stay held |
| Ch18 §4 | `ch18/ch18_revisit_{oruvel,pemakar,tamsule,corrow,quellan,ansedra,hollowmere}.dlg` | E (offered) | one short scene each; Ansedra from the air |
| Ch18 §5 | `ch18/ch18_heirloom_rhen.dlg` | E (offered) | seven nodes, one per hero |

## Decisions made while drafting (for review)
1. **Shot ids:**
   - Ch17's sheet proposed H01–H09, but `ch17/hollowmere` already uses H-ids: the greybox's H01–H04, and Ch15's
     H04–H16 in the same zone. The drafts use **D01–D18** instead.
   - Ch18 uses K01–K23 in `ch18/kite` (a new zone) and `ch10/reedhollow`, which has no K-ids.
2. **"Twenty years":** Ch17 §4's sample has Dace building his first hull at Hollowmere "thirty years ago". Shipped Ch15
   (`ch15_two_daces`) has him "twenty years ago trading salvage", so the drafts say "his first boat here" and keep Ch15's
   twenty.
3. **The ledger's dates** follow rhen_sallow.md:
   - Rhen was eight when Dace went to Corrow, eleven years ago;
   - the news of Kell came "a season later, from a Hollowmere trader";
   - the one message Rhen got ("helping a friend on a long trip") is in the ledger in Dace's hand, as his own verdict
     on it.
   - Dace went in "when it went down to sleep", not when it was at the Rim.
4. **Ama's count** is 47 knots over seven houses, with the lone question-knot as the eighth place (Ch12
   `ch12_voices_003`/`007`).
5. **The tally hull's keeper** is Ch15's record-keeper (`Clerk as "Record-keeper"`), and the tally is written, not
   knotted.
6. **B09 (Kesh's call bark)** has no hook in the game yet. Combat/UI would play the scene from the Vowbound menu.
7. **`ch17_complete`** is set by the flow when the player boards the hull (B12). No scene sets it.
8. **Ch18 revisits:** Merel's red thread is "her wedding colour" (Ch14's red is the Warden house's, not Tobin's).
   Kerrid doesn't land at Corrow except for his heirloom.
9. **Word counts are under the sheets' §8 budgets:**
   - **Ch17:** about 460 spoken words (the sheet budgets ~1,200; SPEC band 880–1,300), and about 245 read in the
     ledger (~450 budgeted).
   - **Ch18:** about 265 on the critical path (~650 budgeted), and about 345 in the revisits and heirlooms (~1,760
     budgeted).
   - The hinge scenes (the ledger, the choice, the gate, the farewell-tide) are spare on purpose: silence and held
     shots carry them, as in Act II.
   - Where words can be added without touching the hinges: Ch17 B02/B12 field barks, the B04 interactables, the B07
     side scene; Ch18 revisits (~150 each budgeted) and heirlooms (~80 each).
   - **Lead's call:** grow those to the band, or keep the drafts spare and revise the §8 budgets.

## When the Act III gate opens (to wire them)
- Move each file to `game/data/dialogue/ch17/` and `ch18/`.
- Declare the flags below in `flags.tres`.
- Add the staging (the D and K shots, new marks), the music cues, and the flow steps that play each scene.
- Ask Audio for the new sounds: `sea_flat_lap`, `sails_fill`, `clutch_hum`, `velamir_lullaby_hum`, `shell_into_water`,
  `names_murmured`.

### Music cues the drafts name (Act III requests; none exist except `farewell_tide`)
`hollowmere_morning`, `dace_ledger` (stops on the blank page: the stop is the cue), `the_choice` (never resolves),
`kite_first_lamp`, `kite_theme`, `reedhollow_return`, `farewell_tide` (exists: Ch10's; the sheet asks for a version
with Asha's hum), `haluna_lifting`, `kite_night`.

## Flags to declare
| Flag | Set in | Read by |
|---|---|---|
| `ch17_started` | ch17_pulled_from_the_sea | flow |
| `ch17_saw_the_hull` | ch17_dock_master_points | objectives |
| `ch17_read_the_ledger` | ch17_the_ledger | Ch18, Ch19, H02, E2 |
| `ch17_first_berth` | ch17_first_berth | ch18_maiden_flight, ch18_revisit_hollowmere, ch18_heirloom_rhen |
| `ch17_chose_the_unbinding` | ch17_the_choice | every Act III chapter; ch17_bark_kesh_chosen |
| `ch17_first_lamp_lit` | ch17_the_first_lamp | Ch18 |
| `ch17_verse_begun` | ch17_ysoldes_table | Ch18, Ch19 |
| `ch17_complete` | the flow (boarding the hull) | flow |
| `ch18_started` | ch18_maiden_flight | flow |
| `ch18_world_open` | ch18_the_chart_table | flow, map |
| `ch18_pell_named` | ch18_through_the_gate | Ch20 Nhoa, codex, costume; ch18_heirloom_pell |
| `ch18_learned_farewell_tide` | ch18_farewell_tide_taught | Ch19, H07 |
| `ch18_child_answered` | ch18_child_older | — |
| `ch18_night_aboard` | ch18_night_aboard | — |
| `ch18_haluna_lifted` | ch18_backs_to_the_water | Ch20 Ilun, the Ending (Toma's beach) |
| `ch18_heirloom_rhen` | ch18_heirloom_rhen | Ch20/21 |
| `ch18_heirloom_asha` | ch18_heirloom_rhen (node ch18_heirloom_asha) | Ch20/21 |
| `ch18_heirloom_toma` | ch18_heirloom_rhen (node ch18_heirloom_toma) | Ch20/21 |
| `ch18_heirloom_ysolde` | ch18_heirloom_rhen (node ch18_heirloom_ysolde) | Ch20/21 |
| `ch18_heirloom_liss` | ch18_heirloom_rhen (node ch18_heirloom_liss) | Ch20/21 |
| `ch18_heirloom_kerrid` | ch18_heirloom_rhen (node ch18_heirloom_kerrid) | Ch20/21 |
| `ch18_heirloom_pell` | ch18_heirloom_rhen (node ch18_heirloom_pell) | Ch20/21 |
| `ch18_complete` | ch18_iskarra | flow |
