---
id: M4-A2P-1001
title: "Request: Act I read-through fixes, Ch4–Ch9 (as played on integration @ 4b1988109)"
role: cinematics
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters, the owners of `game/data/dialogue/ch04/**` onward, the Ch4–Ch9 flows and trigger placement. This is the
Lead's read-through of the as-played order (New Game → Ch9) for scenes out of order, repeats and references to the
unseen. The flows play in each sheet's §1 order, and every one-shot story beat has its `unset` gate. These are content
findings; the dialogue ones were re-read line by line.

| # | Kind | Sev | Where | What the player gets | Suggested fix |
|---|---|---|---|---|---|
| C1 | premature reveal | **med-high** | `dialogue/ch09/ch09_bark_hobb.dlg:6` "Jory Sallow. Mag Sallow. Anni Tesk, nine years." | Two **Sallows** among Corrow's drowned. That is Rhen's surname, tied to Corrow, which is Dace's withheld secret (ADR 0022; Ch15/Ch17), and Rhen doesn't react. "**Tesk**" is also a founder's name (Orin Tesk, the Cage, Ch20) | Replace both surnames with names no cast member or founder uses |
| C2 | unseen | med | `ch07/ch07_empty_moorings.dlg:35, 40, 49` (Brann, Mae, Dovic) | Relatives of Oruvel teammates the player never met; the match roster was Tavi, Rhen, Noa and Old Ama (`reefball/sides.json`) | Rename the roster, or rewrite the lines around Noa and Old Ama |
| C3 | order | med | `ch07/ch07_bark_gantry_after.dlg:6` "Oruvel's boat went out the river mouth an hour ago." | Plays as soon as `ch07_tavi_withdrew` is set, while Tavi is still at his boat for the moorings scene | Gate it on `ch07_blessed_moorings`, or "getting ready to go" |
| C4 | order | med | `levels/ch08/coilspire/coilspire_layout.json` hearth trigger | B03 can play after the binding and the storm-against-wind: "Third time's coming. I can smell it." with the storm wall in view | Also block on `ch08_entered_coilspire` (or `ch08_virel_bound`) |
| B1 | unseen | med | `ch04/ch04_the_ink.dlg:19-39` (`Ysolde [..]`); `ch05/ch05_lanternfall_weir.dlg:39` (`Kerrid`) | Their nameplates show their names before they introduce themselves (act1_ch04: she doesn't give her name at the wall) | `Ysolde as "The stranger"`; `Kerrid as "???"` (dialogue_format "Speaker alias") |
| B2 | order | med | `ch04/ch04_seventh_terrace.dlg:23`; `ch04_spar_wraith.dlg:14-15` | The derelict's motes already slide seaward at first sight, and the sails fall before the fight: the Canticle's payoff (`ch04_name_board.dlg:25, 28`) is spent early (act1_ch04: they "hang… like spray that won't fall") | Hold or no-drift glimmer in both; drop the sails sound before the fight |
| C5 | name clash | low-med | `ch07/ch07_naming.dlg:25` "Aldo Sabe." | "Sabe" is Oruvel's old diver from Ch1 | Give Ione and Aldo another family name |
| B3 | continuity | med-low | `flow/chapters/ch04.json:79` gives `name_board_seventh_terrace`; `ch05_ferry_comes_in.dlg:13-14` | The board is carried ashore but stays in key items; and it's the harbour ferryman who carries it, not Imbe (act1_ch05 B01) | A take step after the ferry scene and an Imbe actor; or keep the board with Rhen |
| C6 | order | low | `flow/chapters/ch08.json:98`, `ch09.json:6` reserves | Kerrid is in the reserve all through the night strand, while the story says he's gone ("Not since the stair.") | Leave him out until `ch09_kerrid_on_road` |
| C7 | unseen | low | `ch09/ch09_the_ebbing.dlg:167` "The Choir. Yes." | The first time "the Choir" is named in play | "The Drowned Choir" in full, or plant it in Ch3's Cantor talk |
| C9 | order | low | `ch09_the_road_out.dlg:95` card, then the end card "The end of Act I" | "Act II: The Truth", then "The end of Act I" | Hold the Act II card while Act II is unbuilt, or retitle the end card |
| B4 | unseen | low | `ch05/ch05_kahre.dlg:43` "Three hundred years…" | Never said in play (only a comment) | The forge child or Ysolde says it |
| B5 | contradiction | low | `ch06/ch06_bark_asha_day.dlg:6-8` "You always ask me that." / "Then answer it one day." | She asked once, only on the `ch03_rhen_asked_after` path, and he answered | Reword, or branch on the flag |
| B6 | contradiction | low | `ch04/ch04_bark_hourglass.dlg:6` "a little after eight" | Ch1 has the crew alive at 10:15 and casting off at 11:10 | "a little after eleven" |
| B7 | repeat | low | `levels/ch06/brine_shoals/brine_shoals_layout.json` `banter_brass`; the Ashcrown stair banters | `once` with no `sets_flag` re-arms after a battle reload (the brass banter replays with Liss in the party) | `blocked_by_flag` (`ch06_sheltered_liss`; `ch05_trial_begun`) or a `sets_flag` |
| C8 | repeat | low | `levels/ch09/corrow_night/corrow_night_layout.json:152-153` | `hobb_overheard` and `stillguard_overheard` have no `once`: they replay on every pass | `"once": true` (as Ch8's) |
| C10 | stale bark | low | `ch07/ch07_bark_board.dlg:7-8` | Still announces Oruvel's match after Oruvel has withdrawn | A `ch07_bark_board_after` variant in the barks map |
| — | doc | — | `flow/chapters/ch04.json:2` doc | Says Ch4 hands on to the end card; the flow goes to Ch5 | Update the doc |

Also filed: **M4-A2P-1002** (was 117) (Progression), the Brine Shoals vendor showing "The Purser's Chest".

## Acceptance criteria
- [ ] Each row fixed, or answered on this task with a reason.

- **act1-chapters, 2026-10-30:** all 17 rows are fixed, as act2-plan's M4-A2P-116 @ 9be201224 (the same table, since renumbered to 1001). Each row's answer is in docs/kb/handoffs/live/act1-chapters.md, "The Lead's 17:44 FAST-TRACK" (MERGE-READY @ c17b7c953). The vendor is M4-A2P-1002: `brine_shoals_vendor`, "The Ridge-Boat Vendor".

## Review log

## Gate note
- Renumbered from M4-A2P-116 by the big27 gate: that id was already taken on the integration branch; then into the filer's own range (TRACK-RULES "FROM 2026-10-30 18:05"). The owner's live log may still say 116.
