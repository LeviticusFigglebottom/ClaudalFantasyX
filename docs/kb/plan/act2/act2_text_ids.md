# Act II text ids: what the story track wrote, and where its data rows go (M4-A2P-109)

The story track wrote the text below on `claude/act2-plan` (2026-10-30, the Lead's request). The loc rows are in each
chapter's csv. Where a **data** row is someone else's, the id is given here so their row can use it unchanged. Rename
an id here and in the csv together, or tell the story track.

## Objective lines: done, data included
`game/data/flow/objectives.json` gets 13 Act II `side` errand rows, with text `OBJ_CH1N_SIDE_*`. **The main path is integration's**
zone-level rows (8287ca8b3). The story track's 30 beat-level main rows were dropped at the big22 merge and are kept in
git history (1a3aa7b9a) for a later pass.
They use the story flags the scripts set, plus the flow's own arrival and victory flags (`ch10_drowner_defeated`,
`ch14_steps_held`). Every target is an existing `zone_maps.json` POI; Ch15's Hollowmere is `ch17/hollowmere`.
- **chapters (act1-chapters):** the greybox flows set only the arrival flags. The scripts set the others when they
  play. If a flow names its own victory flag for a fight, keep the one the row reads: `ch12_ram_felled`,
  `ch14_steps_held`, `ch16_kesh_bound`, `ch16_act_two_complete`. Otherwise a line will hang.

## Battle prompts (encounters.json `prompt_key` / `turn_prompt_key`): owned by combat and chapters
These are the ids from `docs/kb/plan/act2/ui/tutorials.md`, now written:
- `TUT_CH10_ROOTED` (`ch10_fen_roots`)
- `TUT_CH10_DRAIN` (`ch10_fen_leeches`)
- `TUT_CH10_LISTEN` (`ch10_fen_archers`, turn prompt, `pell`)
- `TUT_DROWNER_ROOTS`
- `TUT_LAMP_ENGINE_CRAWLERS`
- `TUT_CH12_UNRAVEL` (`ch12_pass_moths`)
- `TUT_RAM_FIELD`
- `TUT_CH14_HOLD_STEPS`
- `TUT_MALCOR_ENGINE` (turn prompt, `liss`)
- `TUT_WAKEFIN_DARK`
- `TUT_CH16_CYCLE`
- `TUT_CH16_HOLD_LINE`

## Field tips and HUD lines (tutorial_tips.json, battle HUD, formation): owned by ui-menus
- **Tips:** `TIP_RECORDS_*` (on `ch13_archive_read`), `TIP_DARK_SHRINE_*` (near `shrine`, after `ch14_declared_heretics`), `TIP_SWELL_MODE_*`.
- **Set-piece HUD:**
  - `OBJ_CH14_HOLD_STEPS_FMT` and `OBJ_CH16_HOLD_LINE_FMT`, with `{count}` and `{quota}` as in `HUD_OBJECTIVE_COUNT_FMT`;
  - `_DONE` lines;
  - `HUD_LOCKED_KERRID_STEPS` and `HUD_LOCKED_KERRID_LINE`.
- **Formation:** `FORMATION_AWAY_PELL_FEN`.
- The tutorial_tips.json rows and their `tut_*_seen` flags are ui-menus'.

## Items, key items, gear, inns: owned by progression (M4-A2P-031) and chapters
Names (`ITEM_<ID>`, `EQUIP_<ID>`) and descriptions (`_DESC`) are written. Ids are lower-case. **No numbers are in the text.**
Act I's consumables state their amounts ("Restores 200 HP"); progression adds the amount when it sets the effect.

| Kind | Id | Ch | Note |
|---|---|---|---|
| material | `tannin_bark` | 10 | fen drop (`root_crab` / `tannin_archer`) |
| consumable | `reed_salve` | 10 | Kirru; Reedhollow trade if any |
| material | `conduit_glass` | 11 | empty salt-glass; Lowlight drop |
| material | `woolback_felt` | 12 | pass drop |
| consumable | `butter_tea` | 12 | Quellan trader |
| key | `torn_ledger_line` | 13 | ADR 0204 §15, the Archive's torn page |
| material | `red_lacquer_chip` | 14 | court fight drop |
| key | `tobins_cracked_lamp` | 14 | ADR 0204 §13: Liss carries it from Ch14 and leaves it on the ship in Ch16 |
| material | `seaglow_scale` | 15 | Wakefin and sea drops |
| consumable | `current_broth` | 15 | Hollowmere chandler |
| material | `rim_salt` | 16 | Pale Rim drop |

**Gear** (Act II tier; the gear types exist):
| Hero | Ch | Weapon | Armour |
|---|---|---|---|
| Rhen | 10, 15 | `rhen_fenroot_hooks` | `rhen_current_harness` |
| Asha | 11, 12 | `asha_conduit_staff` | `asha_keth_bangle` |
| Toma | 15, 12 | `toma_hollowmere_pike` | `toma_felt_shield` |
| Ysolde | 13, 14 | `ysolde_archive_copybook` | `ysolde_red_lacquer_guards` |
| Kerrid | 15, 16 | `kerrid_hull_iron_cleaver` | `kerrid_rim_wraps` |
| Liss | 15, 11 | `liss_tidewheel_launcher` | `liss_lowlight_sleeve` |

Pell has no gear types yet (characters and progression).

**Inns** (shops.json `inns`; Quellan and Hollowmere exist):
- `INN_REEDHOLLOW` and `_DESC`: the Kirru guest lodge.
- `INN_ANSEDRA` and `_DESC`: the Pilgrims' Hostel. It's an Order house, so it closes to heretics like the purveyor.

## Save-shrine flavour: done as dialogue
`ch10_shrine_reedhollow`, `ch11_shrine_lowlight`, `ch12_shrine_quellan`, `ch13_shrine_ansedra`, `ch15_shrine_hollowmere`
and `ch16_shrine_pale_rim` are narration lines for each shrine's interact. The Order's shrines (Lowlight, Quellan,
Ansedra) have a dark variant from `ch14_declared_heretics`. The Kirru, Saltwright and waders' shrines answer in every
state. The shrine rows themselves (`locations.json` `shrines`) are chapters'.

## Found while doing this: owner's call
- `ITEM_RIME_SHARD_DESC` reads "Highland ice that does not melt in the sun." ADR 0015 puts no ice in Ch12–Ch15, and the
  Heights are Ch12. If it drops in Act II, it needs another material or another line. Owner: progression or ui.
