---
draft: pre-gate
---
# Act III draft scripts: Ch17 to the Ending (planning only)

**Not wired into the game.** These are draft `.dlg` scripts written from the Act III beat sheets
([act3_ch17.md](../act3_ch17.md), [act3_ch18.md](../act3_ch18.md), [act3_ch19.md](../act3_ch19.md),
[act3_ch20.md](../act3_ch20.md), [act3_ending.md](../../beats/act3_ending.md)) at the Lead's request, 2026-10-30. The Lead's
call on length: drafts stay lean; the expansion to the §8 budgets happens when Act III production opens. Act III
production stays paused (ADR 0203/0205). Nothing under `game/` reads them: dlgc compiles only
`game/data/dialogue/`, and no flag, loc row, shot, mark or music cue they name has been added to the game.

**In production (ADR 0207):** Ch17 moved into the game on 2026-10-30 (M5-A3P-1000): `game/data/dialogue/ch17/`, its flags in `flags.tres`. The Act III rules now live in `tools/act3_rules.py`, shared by this checker and `tools/tests/test_act3_rules.py` (which holds the production scripts to them). The `ch17/` rows below are kept as the record; the files are no longer here.

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
   - every flag is declared in `flags.tres` or in the table below;
   - light rises only in a Kirru-way lifting, a Vowbound's or Kesh's release, the Letting's sleeve, Sefir's lift, and
     from H09 on; nothing is held or bound after H09 (act3_ending §0 rules 3, 4, 7);
   - the no-Dace-voice rule is Ch17's (the ledger); Dace speaks in E2.
   Speakers the game doesn't have yet are in the table below; the checker adds them to its temporary copy only.
4. **Banned terms:** `tools/validate_data.py` already scans `docs/kb/story/` and every `.dlg` file.

**Result (2026-10-30):** 73 files (Ch17 11, Ch18 16, Ch19 7, Ch20 18, Ch21 and the Ending 21), 0 errors, 0 warnings. validate_data 0/0. A planted bad file (a rising mote, a
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
| Ch19 I01 | `ch19/ch19_the_kite_comes_down.dlg` | C | nobody says this is where they were |
| Ch19 I02 | `ch19/ch19_the_vigil.dlg` | P → C | the Prologue's P01/P02, shot for shot; the line verbatim (own id); no rising glimmer (T-07) |
| Ch19 I03 | `ch19/ch19_the_hitch.dlg` | E | three held inputs; "Somebody should have it."; no farewell |
| Ch19 I04 | `ch19/ch19_the_words.dlg` | E (optional) | spoken, not sung; **placeholder Lamptongue** (Audio owns the lyric) |
| Ch19 I07 | `ch19/ch19_the_signatures.dlg` | C | the duty roll's two hands |
| Ch19 I08 | `ch19/ch19_bark_abiding_wardens.dlg` | fight lines | four nodes by trigger (no mid-battle hook yet) |
| Ch19 I09–I10 | `ch19/ch19_the_engine_stops.dlg` | C | the hum stops; nothing rises; "There's the stair." |
| Ch20 U00 | `ch20/ch20_down_the_eye.dlg` | C | Liss seats Tobin's lamp: "He volunteered. So nobody'd have to be chosen." |
| Ch20 U01–U06 | `ch20/ch20_<vowbound>.dlg`, `ch20/ch20_<vowbound>_release.dlg` | C → P → C | six layers in vowbound.md's order; each keepsake rises last |
| Ch20 fights | `ch20/ch20_bark_vowbound_fights.dlg` | fight lines | Kahre's "It doesn't hurt, son." verbatim; the Cage's thanks |
| Ch20 R1, R2 | `ch20/ch20_rest_one.dlg`, `ch20/ch20_rest_two.dlg` | E | no line |
| Ch20 U07 | `ch20/ch20_the_cage.dlg` | C → P | Toma holds the line |
| Ch20 U08 | `ch20/ch20_thank_you.dlg` | C | four thank-yous; "She's waiting for you. Both of them are."; the founders stay held |
| Ch21 H01–H02 | `ending/ch21_the_last_layer.dlg`, `ending/ch21_two_lamps.dlg` | P, C | no goodbye; Kerrid's hand only in Rhen's single |
| Ch21 H03 | `ending/ch21_kesh.dlg`, `ending/ch21_kesh_release.dlg` | C → P → C | the camera stays on Sefir's face |
| Ch21 R1 | `ending/ch21_seven_bands.dlg` | E | one optional line each, under 10 words, no goodbyes |
| Ch21 H04, H06 | `ending/ch21_bark_sefir.dlg` | fight lines | warm, reasonable |
| Ch21 H05 | `ending/ch21_he_takes_the_heart.dlg` | C | Kerrid off-frame with the two lamps |
| Ch21 H07 | `ending/ch21_the_letting.dlg` | P | the lyric is Audio's; the sleeve rises over the last 6 s |
| Ch21 H08 | `ending/ch21_sefir_lets_go.dlg` | C | two lines; his reflection ripples |
| Ch21 H09 | `ending/ch21_great_unbinding.dlg` | C | six cutaways and the Kite; everything released at once |
| E1–E7 | `ending/ending_{imra,rest_hands,dace,rest_where_he_stood,kerrid,rest_empty_place,the_kite_comes_down,nothing_comes,the_dark_sea,beach_rite,first_lamp}.dlg` | C/E | one goodbye per scene, a rest between; "Goodbye, Dad."; "Stair's clear." |

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

10. **Ch19–Ending shot ids:**
    - I01–I09 in `prologue` and `ch19/iskarra_spire`; the vigil reuses the Prologue's own P01/P02.
    - U01–U30 in `ch20/undertow_layers`.
    - HT01–HT22 in `ch21/heart`: not H-ids, which read as the beat names.
    - E01–E13 for the Ending, on the Kite deck (`ch18/kite`), the Haluna dock and Oruvel. No collisions.
11. **The vigil's line** has its own id (`ch19_vigil_001`), and its translator note says it must match
    `prologue_dead_city_001` word for word.
12. **Lamptongue: Audio's final texts** ([docs/kb/audio/lamptongue.md](../../../audio/lamptongue.md) §2–§3; on
    `claude/audio` until it merges). These lines are tagged `#lamptongue #notr` (and `#sung` when sung), and are never
    translated on screen.
    - `ch19_words_001`: Ysolde reads verse 8 whole as cut in the stones, spoken.
    - `ch19_words_002`: Asha repeats its first line and its last word.
    - `ch20_fight_006`: kept as written ("Mir, mir. Tash.").
    - H07: `ch21_the_letting_verse` sings verse 8 whole, the only time.
    - `check_drafts.py` now holds every `#lamptongue` line to §1's 17 roots, and verse 8 to H07.
    - **Verses 1–7 in play** (2026-10-30): verse 1 (`ch03_verse_042`–`045`) and verse 2 (`ch05_kahre_014`–`017`)
      match §2 word for word. Ch4's "Vey enu" (`ch04_banter_ennu_001`) is Asha's deliberate mispronunciation, which
      Ysolde corrects on screen. Verses 3–7 have no sung text in play yet: the `*_bound` stings are instrumental (§2).
13. **Fight lines** (Ch19 I08, the Ch20 fights, Sefir's H04/H06) are bark files with one node per trigger. The game has
    no mid-battle line hook (only lead-in barks): **a request for Combat**. New encounters:
    - Ch19: `ch19_abiding_wardens`;
    - Ch20: `ch20_<vowbound>` ×6 and `ch20_the_cage`;
    - Ch21: `ch21_kesh`, `ch21_sefir_heart`, `ch21_sefir_letting` (and phase 1, `ch21_sefir_warden`, which the flow
      starts after R1).
14. **Release and ending light:**
    - every release ends on its keepsake rising alone (net-float, hammer, tuning key, keth bundle, name-shell, ring,
      lamp-key);
    - the founders stay held after the Cage (rule 2);
    - after H09 every cue is `glimmer_lift`, with no held or bound light; the sea-glow steps are Rendering's curve, not
      cues.
15. **Dace's voice** is heard only in E2 (six short lines; his apology is his, and nobody says the reasons excuse him).
    **Imra** has two lines. **Kerrid's** E3 lines are the sheet's, verbatim. Rhen's E6 voice-over has two lines (≤ 25
    words): the second answers the Prologue's "Remember that, later." without rewording it.
16. **T-08** (the hitch inserts in H02 and E3) and **T-09** (Tobin's lamp dark in E4) are drafted as optional inserts
    with no line. `ch21_unbound` (H09) is a new flag for the flow.

## When the Act III gate opens (to wire them)
- Move each file to `game/data/dialogue/ch17/` and `ch18/`.
- Declare the flags below in `flags.tres`.
- Add the staging (the D and K shots, new marks), the music cues, and the flow steps that play each scene.
- Ask Audio for the new sounds: `sea_flat_lap`, `sails_fill`, `clutch_hum`, `velamir_lullaby_hum`, `shell_into_water`,
  `names_murmured`, `kite_settles`, `rope_slips`, `engine_hum_stops`, `kite_engine_strains`, `kite_touches_floor`,
  `pell_farewell_tide`, `kite_engines_stop`, `wind_in_sails`, `rope_creak`, `hull_meets_water`, `match_struck`.
- Add the speakers below to `speakers.json`, with their name rows.

### Music cues the drafts name (Act III requests; none exist except `farewell_tide`)
`hollowmere_morning`, `dace_ledger` (stops on the blank page: the stop is the cue), `the_choice` (never resolves),
`kite_first_lamp`, `kite_theme`, `reedhollow_return`, `farewell_tide` (exists: Ch10's; the sheet asks for a version
with Asha's hum), `haluna_lifting`, `kite_night`, `kerrid_hitch`, `engine_down`, `the_eye`, `undertow_descent`,
`memory_oruvel`, `memory_lanternfall`, `memory_coilspire`, `memory_tidecup`, `memory_lowlight`, `memory_ansedra`,
`release_sting`, `the_cage`, `thank_you`, `heart_approach`, `kesh_first_voice`, `heart_rest`, `sefir_heart`,
`the_letting`, `unbinding_swell`, `goodbye_imra`, `ending_lift_bed`, `goodbye_dace`, `goodbye_kerrid`, `ending_dock`,
`credits_suite`, `post_credits_lamp`. `hesper_and_ilsabet` exists (M3-AUD-858) and is the encounter's, not a cue here.

## Speakers to add
| Id | Display name | Kind |
|---|---|---|
| `hesper_oan` | Warden Hesper Oan | speaker |
| `ilsabet_rue` | Ilsabet Rue | speaker |
| `ilun` | Ilun | speaker |
| `kahre` | Kahre | speaker |
| `virel` | Virel | speaker |
| `hesk` | Hesk | speaker |
| `nhoa` | Nhoa | speaker |
| `ethren` | Ethren | speaker |
| `orin_tesk` | Orin Tesk | speaker |
| `halde_moor` | Halde Moor | speaker |
| `isse_varan` | Isse Varan | speaker |
| `cael_imbrey` | Cael Imbrey | speaker |
| `imra` | Imra | speaker |
| `dace` | Dace | speaker |

The six Vowbound speak as the people they were, through an alias (`Ilun as "Teyo"`, `Kahre as "Daro"`, `Virel as
"Wenna"`, `Hesk as "Ama"`, `Nhoa as "Ressa"`, `Ethren as "Corran"`).

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
| `ch19_started` | ch19_the_kite_comes_down | flow |
| `ch19_vigil` | ch19_the_vigil | — |
| `ch19_learned_the_hitch` | ch19_the_hitch | ch21_two_lamps (H02), ending_kerrid (E3) |
| `ch19_words_whole` | ch19_the_words | H07 (Design's call: §10 Q4) |
| `ch19_abiding_beaten` | ch19_bark_abiding_wardens (end node; or the encounter's victory_flag) | Ch20, H04 |
| `ch19_engine_stopped` | ch19_the_engine_stops | Ch20 |
| `ch19_complete` | ch19_the_engine_stops | flow |
| `ch20_started` | ch20_down_the_eye | flow |
| `ch20_ilun_released` | ch20_ilun_release | vowbound.json `released_flag`, the summon menu, codex |
| `ch20_kahre_released` | ch20_kahre_release | as above |
| `ch20_virel_released` | ch20_virel_release | as above |
| `ch20_hesk_released` | ch20_hesk_release | as above |
| `ch20_nhoa_released` | ch20_nhoa_release | as above |
| `ch20_ethren_released` | ch20_ethren_release | as above |
| `ch20_cage_broken` | the Cage encounter's victory_flag (flow) | H01 |
| `ch20_complete` | ch20_thank_you | flow |
| `ch21_unbound` | ch21_great_unbinding | the Ending's flow |
