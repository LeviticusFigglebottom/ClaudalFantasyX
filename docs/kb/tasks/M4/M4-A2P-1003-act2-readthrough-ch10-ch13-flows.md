---
id: M4-A2P-1000
title: "Request: Act II as-played read-through, Ch10–Ch13 flow fixes (lead/gate-big27 @ ce18caafa)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters, the owners of the Ch10–Ch16 flows, trigger placement and thread tests. This comes from the Lead's Act
II read-through of what the newly mounted Ch10–Ch13 actually play, looking for out-of-order beats, leaks and repeats.

**What's fine:**
- No Act II or III secret leaks in any Ch10–13 line, played or not.
- Every beat keeps its `unset` gate.
- The engine → twice → Nhoa gating is right.

The problems are the **mounting gaps**:
- the flows play only the scenes that set M4-A2P-114's objective flags;
- several of those assume setup in scenes that aren't mounted;
- no chapter hands off to the next.

**Story has already fixed its own lines** (commit on claude/act2-plan): D2's Ressa is now named at dawn_gate, and D6–D10, D13, D15 and E10–E13 are fixed.

**Corrections to my M4-A2P-114 table** (story's error, not yours):
- **E8:** the pact belongs at the moorings, not on arrival at `FromArchive`.
- **E9:** the roll belongs to day two, as an arrive row like `hands`, not straight after the ledgers.

| # | Sev | Where | Problem | Fix |
|---|---|---|---|---|
| D3/E1 | **high** | ch10.json, ch11.json, ch12.json, ch13.json | **No chapter hands off.** `ch10_dawn_gate`, `ch11_held_by_you`, `ch12_down_the_other_side` and `ch13_the_pact` set `chNN_complete`, then nothing. No `go` leads to the next chapter's entry, and Ansedra has no way to the Lacquer Court (ch14's `CourtEntry` row is unreachable). Ch9 ends on the end card, so nothing enters Ch10 either. | A `go` after each closing scene: → `ch11/sunken_vey` Landing; → `ch12/keth_pass` PassFoot; → `ch13/ansedra` Moorings; → `ch13/ansedra_lacquer_court` CourtEntry |
| E2 | **high** | ch13.json `lamp_archive` beats; `lamp_archive_layout.json` | The Archive and the pact can run **before Ethren is bound**: `ch13_archive_roll:21` "I have him. He's with me now." `objectives.json` `a_archive` already requires `ch13_ethren_bound` | Add `ch13_ethren_bound` to the `ledgers` beat's `when.set` and to the trigger's `requires_flag` |
| D1 | **high** | ch10.json reedhollow `arrive` | `ch10_causeway` (B06: Owa's "Not you.", Pell and Kerrid put outside on the root) never plays, but `ch10_farewell_tide:62-65` and `ch10_dawn_gate:10-12` cut to them standing "where B06 left him" | Play `ch10_causeway` in the reedhollow arrive row, before the set |
| E3 | **high** | ch13.json first `ansedra` arrive | `ch13_the_pact` runs on the wedding, Tobin, Hollowmere's captains and Sefir's key, all set up only in unplayed `ch13_still_city` (→ `sefirs_house`) and `ch13_tobin` (§1 never-cut). Ch14 carries it on (`ch14_the_vows:49` "You gave me the key.") | Play `ch13_still_city`, then `ch13_tobin`, in the first Ansedra arrive row |
| E4 | **high** | ch12.json; `keth_pass_layout.json` | `ch12_breath` (B03, never-cut) is never played, yet `ch15_the_shoal:102` "Your breath. In Ullar." plays unconditionally | A `cold_ledge` beat (set `ch12_started`, unset `ch12_toma_saw_breath`) playing `ch12_breath`, before the terrace |
| D2 | med | `reedhollow_layout.json` | `ch10_bark_kirru_ressa` (sets `ch10_heard_ressa`) has no trigger. Story now names Ressa at dawn_gate too, so this is no longer a gap, but the bark is the beat sheet's first naming | A trigger in Reedhollow before the Shore |
| D5 | med | ch11.json; `sunken_vey_layout.json` | `ch11_housing_mark` (B03, never-cut: "Dace Sallow. My father.") never plays, so `held_by_you`'s split line has no cause and `l_side_bench` can't open | A `conduit_mark` trigger (after `ch11_started`) playing it |
| E5 | med | ch12.json; Ch12–13 layouts | `ch12_cold_road` (B01: the pass-cord custom) isn't played, and **no Ch12 or Ch13 layout has a bark, NPC, shrine, camp or side trigger** | Play `ch12_cold_road` in the first `keth_pass` arrive row, and add the bark/side triggers |
| D4 | med | ch11.json `held_by_you` row | Places the party at `FromLowlight` (88, 0, −16); the scene is staged at the Vey's mouth (`landing_pell`, V08) | `"place": "Landing"` |
| E6 | med-low | ch12.json second `keth_pass` arrive row | `ch12_herd_cord` replays on every arrival until Quellan (no seen flag) | Gate on a new `ch12_herd_cord_seen` (as `ch11_twice_seen`) |
| E7 | low | ch12.json | B13 "down the other side" plays when walking *back* into Keth Pass from Quellan | Its own descent spawn, or play it on the Quellan exit toward Ch13 (with E1) |
| E8 | low | ch13.json | The pact plays on arrival at `FromArchive`; it's staged at `kerrid_moorings`, and `a_moorings` and `a_rest` never show | A trigger at the moorings point (corrects my M4-A2P-114 row 13–14) |
| E9 | low | ch13.json `roll` beat | The roll (day two) plays straight after the ledgers, in the same visit | An arrive row on the next visit, like `hands` (corrects row 11) |
| D11 | low | ch10.json | `ch10_what_went_up` (B05, the Drowner's release) isn't played after the battle; `ch11_twice`'s "That is twice." holds only by accident | An ossa_fen arrive row on `ch10_drowner_defeated` playing it |
| D12 | low | `ossa_fen_layout.json` | The nets side scene sets `ch10_returned_net` on the promise, with no pickup | A pickup in the dead channel. Story will split the flag (`ch10_net_promised`) when the pickup exists |
| E12 | low | ch12.json | `ch12_the_knot` isn't played, so `down_the_other_side:17`'s `ch12_rhen_tied_knot` branch can't fire. Pell is staged and voiced in Ch12 with no party row (waits on M3-C09-07) | Wire the knot side scene |
| D16 | low | Act II stages | The played scenes' cast (Asha, Toma, Ysolde, Liss, Kerrid, Nhoa) are missing from the stages, so `@mark`/`@anim` drop with warnings | Already tracked in M4-A2P-075 |

## Acceptance criteria
- [ ] Ch10 → Ch14 can be played through by flow alone (E1).
- [ ] Each row fixed, or answered here with a reason.

## Review log
