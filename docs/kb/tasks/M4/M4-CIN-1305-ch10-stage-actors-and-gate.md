---
id: M4-CIN-1305
title: "Request (cinematics track → the chapters track): Ch10's stage actors, the hold gate and its two prompts, for the staged scenes"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-010]
milestone: M4
request-from: cinematics
---
## Goal
Ch10's cutscene shots and marks are staged (cinematics' `game/data/cutscene/ch10/*.json`, M4-CIN-1304). The scenes
also `@mark` and `@anim` people the layouts don't have yet, and the farewell-tide needs a hold gate. These are the
chapter's (layout actors, the zone's host wiring).

## Acceptance criteria
- [ ] **ossa_fen** stage actors (hero bodies or casts): `asha`, `toma`, `ysolde`, `liss`, `kerrid`, standing on the
      bank behind FenEdge in the Ch9 line (ch10_fen_edge walks them to `fen_line_*`, then onto the root-walk), and
      `mangrove_drowner` at the dead tree (`"cast": "creature:mangrove_drowner"` once creatures-b has the model;
      ch10_dead_channel's `@anim mangrove_drowner stir`).
- [ ] **reedhollow** stage actors: `owa` (the eldest; a Kirru cast, M4-A2P-053), inside the ring near the causeway's
      east end (she walks to `causeway_gate`); `asha`, `toma`, `ysolde`, `liss`, `kerrid` (the gate scenes and the
      shore). For the farewell-tide, the party stands on the shore behind the clutch: Asha at `shore_front`
      (66.6, 0, 0), the others 0.8–1.2 m behind her. The clutch (`clutch_0..7`) is shown by the beat (`show_block`), as
      Ch1's Hullgnaw is; `@anim clutch turn_back` plays on every `clutch_*` actor (CutsceneGroup).
- [ ] **The hold gate on Reedhollow's story sequencer** (as Ch09Zone's `hold_gate`), with prompts
      `hold_to_watch` ("Hold to watch") and `release_tide` ("Release") as loc keys: ch10_farewell_tide opens
      `<<event hold_input hold_to_watch>>`, then `<<event release_input release_tide>>` (the release gate,
      M4-CIN-1302).
- [ ] Optional, for the staging to read as written: the clutch nearer the waterline (x ≈ 61–62, not 64–65), so the
      party has room behind it on the shore; the T-shots are framed for either.

- [ ] **Ch11** (added 2026-10-30, staged from act2_ch11_direction.md): **sunken_vey** stage actors `asha`, `liss`,
      `pell`, `kerrid` (the scripts mark them to `liss_landing`, `pell_landing_back`, `rhen_court`, `asha_court`,
      `landing_pell`, `landing_asha`, `line_*`); **lowlight** `asha`, `liss`, `pell`, `ysolde`, `kerrid`, and `nhoa` as an
      actor at the `nhoa` mark (ch11_nhoa's `@anim nhoa turn_head pell`; a Saint body from creatures-b's Nhoa).
- [ ] Ch11's lamp bench holds its input three times (`hold_steady`, `turn_collar`, `seat_it`): the zone's hold gate
      with those prompts.

- [ ] **Ch12** (added 2026-10-30, from act2_ch12_direction.md): **keth_pass** `asha`, `toma`, `ysolde`, `liss`,
      `pell`, `kerrid`, `ullari_woman` (the knot), and `avalanche_ram` at the seep pool (creatures-b's Ram); **quellan**
      `asha`, `ysolde`, `toma` in the inn (Asha on the bench at about (34.6, 0, -7.4)); **cloudloom** `asha`, `ysolde`,
      `toma`, `rhen` and `hesk` on the dais (creatures-b's Hesk).

- [ ] **Ch13** (added 2026-10-30, from act2_ch13_direction.md; staged in M4-A2P-075): **ansedra** `sefir` (his door,
      `sefir_door`), `tobin`, `merel` (the guest moorings), `householder` (Corran's house), `asha`, `toma`, `rhen`,
      `ysolde`, `liss`, and the layout's `kerrid` shown (it is `hidden`); **sanctum** `liss`, `ysolde`, `asha`, and
      `ethren` at the `corran` mark (creatures-b's Saint body; ch13_ethren's rise and head turn); **lamp_archive**
      `ysolde`, `liss`, `asha`, `rhen`, and `sefir` (R10's reading table).

- [ ] **Ch14** (added 2026-10-30, from act2_ch14_direction.md; staged in `game/data/cutscene/ch13/ansedra_lacquer_court.json`):
      **ansedra_lacquer_court** `sefir` on the dais (`sefir_dais`, (0, 0.8, −20.2)), `tobin` and `merel` at `vows`,
      `malcor_venn` at the Conclave gallery's rail (`venn_rail`, (−10.2, 2.0, −21.2)) with three more Conclave figures
      beside him, `brannoc_hale`, `stillguard`, the hull captains, `kerrid` and the party on the court marks; the barge's
      `bier` (Tobin under the bridal cloth) for L01/L12; and Venn on his own dead barge beyond the water gate for L10
      (about (−3, 0, 22)).

- [ ] **Ch15** (added 2026-10-30, from act2_ch15_direction.md): **open_sea** (the barge) `kerrid` at `kerrid_sits` (standing
      at the stern until K05's `sit_down`), `asha`, `toma`, `liss`, `ysolde`, `rhen`, `pell`, and `tobin` on the bier
      under the bridal cloth; the fin and the shoal's lights for U05/U06 and K01. **hollowmere** `aldous_varrow` (the
      dock-master: his door, then the quay, `dockmaster_quay`), `liss`, `toma`, `rhen`, `asha`, `ysolde`, `pell`,
      `kerrid`, Tobin's body on the jetty, and the pyre-raft's flotilla for H12.

## Notes
- Cinematics' staging review (M4-C10-01) and M4-A2P-070. The stills wait on these actors.

## Review log
