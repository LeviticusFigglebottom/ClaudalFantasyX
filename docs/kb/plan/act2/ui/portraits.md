---
draft: pre-gate
---
# Act II portraits

Act I's pipeline holds:
- `tools/portraits/portraits.json` names each speaker's review stage, model, materials and face-pose table;
- `render.sh` bakes the five emotions (neutral, smile, determined, worried, grief) at 256 px on lavapipe;
- a speaker whose stage has no face-pose table gets neutral only;
- every bake has a PROVENANCE row;
- `test_dialogue_box` fails when an Act I speaker's model lands without a portrait. It extends to Act II at the gate.

Each bake waits on its model (the characters track). Order of need follows the chapters.

| Speaker (speakers.json id) | Ch | Model owner | Emotions | Notes |
|---|---|---|---|---|
| Kirru eldest (`kirru_eldest`) | 10 | characters (one Kirru base, Pell's rig) | 5 | Framed like Pell: closer camera, crest in frame |
| Kirru child (`kirru_child`) | 10 | characters | 5 | Smaller body: check the frame, as Act I's child |
| Kirru clutch (`kirru`) | 10 | characters | neutral | A crowd voice, if it speaks at all |
| Ullari woman (`ullari_woman`) | 12 | characters (crowd generator, Ullari costume) | 5 | The side scene |
| Quellan innkeeper, keth-reader | 12 | characters | neutral | Townsfolk |
| Tobin Varrow (`tobin`) | 13–14 | characters | 5 | Plus a menu portrait if he joins any menu (he doesn't) |
| Merel Dask (`merel`) | 13–14 | characters | 5 | **Wedding red** costume state from C1 of Ch14: a second set `merel_wedding_*` |
| Malcor Venn (`malcor_venn`) | 14 | characters (a person boss) | 5 | Also the bestiary and timeline portrait (people row) |
| Corran (`corran`) | 13 | characters | neutral | As Ethren's memory; the veil-fall is Act III |
| Sefir (`sefir`) | 13–16 | exists | 5 | Baked in Act I (M3-HER-1147). Check his Ansedra costume |
| Liss's father (`<name>`) | 15 | characters | 5 | Narrative names him |
| Hollowmere hull-captains | 15 | characters | neutral | Townsfolk |
| Abiding guard | 16 | characters | neutral | Battle and bestiary portrait only, if it doesn't speak |
| Tenders, pilgrims, barge-polers | 13 | crowd generator | neutral | Only those with lines |

**The Vowbound** speak through their callers or not at all. Their bestiary-style portraits exist (creature portraits:
`creature_nhoa`, `_hesk`, `_ethren`). Kesh needs its model first (act2_plan §2 Ch16: the only Vowbound without a sheet).

**Kerrid:** no new bake. His `grief` and `guilty` face rows are reserved for the reveal (art/characters/kerrid.md §face),
and `guilty` is not one of the five baked emotions. **At the gate, add `guilty` to Kerrid's portrait emotions** so the
dialogue box shows it during the reveal (kerrid.md §2).

**Loc keys (speaker names, ~12):** `CHAR_KIRRU_ELDEST`, `CHAR_KIRRU_CHILD`, `CHAR_KIRRU`, `CHAR_ULLARI_WOMAN`,
`CHAR_INNKEEPER_QUELLAN`, `CHAR_KETH_READER`, `CHAR_TOBIN`, `CHAR_MEREL`, `CHAR_MALCOR_VENN`, `CHAR_CORRAN`,
`CHAR_<LISS_FATHER>`, `CHAR_HULL_CAPTAIN`. Unnamed-until-named speakers use `character_names.json` (as Pell's
`CHAR_PELL_UNNAMED`).
