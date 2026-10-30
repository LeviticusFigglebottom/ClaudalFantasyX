---
draft: pre-gate
---
# Act II → Act III consistency pass: flags, companions' arcs, Vowbound (2026-10-30)

The story track checked every Act II thread that Act III picks up. Sources: the Act II beat sheets, scripts and
`flags.tres`; the Act III sheets in this folder; [act3_ending.md](../beats/act3_ending.md); act_outline; bible; vowbound.md;
the character sheets; ADRs 0015, 0016, 0017, 0020, 0022 and 0204. **Planning only:** Act III production is paused.

**Method:**
- Every Act I/II flag whose description or flag-table row names an Act III reader was listed, and each was traced to a
  beat in the Ch17–Ch20 sheets or act3_ending.
- Every companion's Act III arc in its character sheet was traced to a beat.
- Every Vowbound's binding was traced to its release.
- The 37 Act I/II flags the Act III sheets read are **all declared** in `flags.tres`; none is missing.

## 1. Mismatches found (with defaults)
| # | Where | Mismatch | Default (applied or proposed) | Owner |
|---|---|---|---|---|
| T-01 **(accepted, applied)** | act3_ending H03 vs Ch16 B04 | H03 "raises Kesh from the stones", but Ch16 binds Kesh to Asha (`ch16_kesh_bound`; ADR 0204 §16 put it on this backlog) | **Proposed:** H03 becomes Asha calling Kesh out of her sleeve one last time; Kesh fights at full strength (vowbound §7) and is released as the Ch20 six were; the roster ends empty. One-paragraph edit to H03 | Narrative (act3_ending) |
| T-02 | act2_ch14 flag table vs act_outline Ch19 | `ch14_venn_beaten` promised Venn "fought again, openly a revenant, in Ch19"; Ch19's bosses are Hesper Oan and Ilsabet Rue | **Applied:** act2_ch14's row is corrected. Venn isn't one of the Abiding and isn't refought (act3_ch19 §10 Q1) | done |
| T-03 | act_outline Ch17 vs act2_ch15 B14 / `ch15_two_daces` | "Liss's father hasn't spoken since Tobin's pyre-raft", but the scripted supper (8 dock-master lines) happens after the pyre, the same night | **Proposed:** act_outline Ch17 reads "since the night of the pyre-raft". act3_ch17 rule 4 already says so | Narrative (act_outline) |
| T-04 **(accepted, applied)** | vowbound §7 vs pell.md vs ysolde.md: the Eighth Verse's sources | vowbound: Kesh hid the **melody** in the Choir stones. pell.md: the farewell-tide is "the melody that holds the Eighth Verse". ysolde.md: words from "keth, Kirru song, and Choir stones" | **Proposed reconciliation:** the stones hold the melody in fragments, readable only once the farewell-tide is known (Ch18 K05: "That's the Letting"). The **words** are Lamptongue cut in the stones, completed by Ysolde. Ama's keth give the **count**: her lone question-knot (Ch12 `ch12_voices_007`) is the eighth place. Sung only at H07 (README rule 3) | Narrative (vowbound.md, pell.md, ysolde.md: one line each) |
| T-05 | toma_okeru.md and vowbound.md ("the Cage-Wardens") vs act_outline and the glossary ("the Cage") | two names for the four bound founders | **Proposed:** *the Cage* is the boss; name the four founders (glossary); retire "Cage-Wardens" in toma_okeru.md and vowbound.md's release order | Narrative |
| T-06 | glossary ("the Abiding: glimmer-sustained revenants") vs act2 consistency D6 ("the living Abiding guard", Ch16) | are Ch16's guards revenants? | **Proposed:** they are Abiding (revenants), "living-seeming". Nothing in Ch16 names what they are (bosses/abiding_guard.md). D6's "living" means "not yet shown dead". Ch19 is the first open fight (ADR 0016) | creatures-b, Narrative |
| T-07 **(accepted; docs applied; the cue is M4-A2P-111)** | act_outline Prologue ("Glimmer rises around him") vs bible §2 / README rule 1 | rising light before H09 means release; the Prologue's frame is Ch19's dusk | **Proposed:** the Prologue's motes **drift** (held), not rise. Ch19 I02 doesn't repeat it | Act I owner, Cinematics |
| T-08 | act3_ending E2, E3 vs the new Ch19 hitch | Ch19 I03 adds Dace's hitch (holds, then one pull and it lets go) | **Proposed:** one insert in H02 (Rhen ties it on Dace's lamp-line) and one in E3 (Kerrid sees it before he goes). Optional | Narrative (act3_ending), Cinematics |
| T-09 | ADR 0204 §13 (Tobin's lamp left on the ship in Ch16) vs Ch17 | does Liss have it in Act III? | **Applied:** the Hollowmere ship that waited at the Rim is the one that pulls them out (Ch17 B01), so she has it back. She can't mend it; at Ch20 U00 she spends it on the Kite's last charge (ending_cost_audit §4), and it is released at H09. **Proposed:** an insert of it going dark in E4 | Narrative, Cinematics |
| T-10 | act2_ch14 `ch14_merel_taken` ("Narrative's call") | Merel's fate | **Default:** she lives, kept in her father's house, seen once from the Kite (Ch18 Ansedra). No rescue | Narrative |
| T-11 | The heretic state in Act III | is Ansedra still closed? | **Default:** yes. The Kite can't land there; no shop; one scene from the air (Ch18 §4) | Design |
| T-12 | act2 lane flags (act2_consistency F1–F8) | Act III reads several flags whose lane names differ | **Applied:** Act III reads the names the scripts set (the lane names where code already uses them: `ch10_drowner_defeated`, `ch10_farewell_tide_seen`, `ch15_kerrid_revealed`). The rest of the F rows still stand for chapters | chapters |
| T-13 | Kesh's call bark after `ch17_chose_the_unbinding` (Ch17 B09) | Kesh is callable from Ch17 (`ch16_kesh_bound`) | **Default:** her call bark changes once Asha chooses (one line), and no other Vowbound bark changes until their release | Narrative, Combat |
| T-14 | "Lamplighters" | the glossary's proper noun (the six founders). The Act II wedding lamp-carriers were renamed **lamp-bearers** (proofread, 2026-10-30) | **Applied.** Act III uses "Lamplighters" only for the founders (Ch19's household rooms; Kesh's lamp-key) | done |

## 2. Companions' arcs: Act II plant → Act III payoff
| Who | Act II plant (flag) | Act III payoff | Sheet |
|---|---|---|---|
| **Asha** | learns what the Hush does (`ch16_learned_the_hush`), refuses Sefir (`ch16_refused_sefir`), binds Kesh (S7) | chooses the Unbinding (Ch17 B08); learns the tune (Ch18 K05) and the words (Ch19 I04); releases six (Ch20); sings the Letting (H07); loses her voice (E5) | ch17–20, ending |
| **Rhen** | admits Dace (`ch11_rhen_admitted`); ties a knot for him (`ch12_rhen_tied_knot`); the Ch15 confession; Kell's wick unlit (Ch10 camp) | the ledger (Ch17 B05); the hitch (Ch19 I03); Dace in the heart (H02, E2: says it back); the wick at E7 only | ch17, ch19, ending |
| **Kerrid** | confession (`ch15_kerrid_revealed`); holds the line (`ch16_line_held`); "a watch is for being relieved" (Ch15 camp) | "first down the stair" (Ch17 B08, Ch20 U00); teaches the hitch (Ch19); Kahre's "It doesn't hurt, son" (Ch20 U02); last off the wall (E3) | ch17, 19, 20, ending |
| **Liss** | Tobin killed (`ch14_tobin_killed`); his light in a cracked lamp (`ch15_pyre_raft`); Wenna's marks (`ch08_liss_found_marks`, `ch11_/ch13_found_wenna_mark`); "I want it to cost them" (Ch14 camp) | the Kite flies on the held dead (Ch17 B10); she builds the rig anyway; Virel (Ch20 U03); the lamp can't be mended (R1); brings the Kite down by hand (E4) | ch17, 20, ending |
| **Pell** | kept out (`ch10_pell_kept_out`); kneels to Nhoa (`ch11_pell_knelt`); "I knew" (`ch15_pell_said_he_knew`) | through the gate, named again (Ch18 K03–K04); teaches the farewell-tide (K05); turns his back for Nhoa (Ch20 U05) | ch18, 20 |
| **Ysolde** | lies, then confesses the count (`ch12_ysolde_lied`, `ch12_ysolde_confessed`); the roll (`ch13_read_cantor_roll`); Corran's house (`ch13_corran_house`); twenty-four years (Ch13 camp) | begins the words (Ch17 B11); has them whole (Ch19 I04); Ethren's veil (Ch20 U06); teaches words only, never the tune (epilogue) | ch17, 19, 20 |
| **Toma** | refuses Hale (`ch14_toma_refused`); confesses 1003 (`ch15_toma_confessed`); on the tally (`ch15_toma_on_the_tally`); "the end of the road" (Ch12 camp) | Haluna lifts its own (Ch18 §4, optional, flagged); thanks Ama (Ch20 U04); holds the line at the Cage (U07); the beach lifting (Ending) | ch18, 20, ending |

**Gaps found and filled by the Act III sheets:**
- Toma had no Act III beat between Ch18 and the Ending → Ch20 U04 (Hesk) and U07 (the Cage's line).
- Ysolde had no beat between Ch17 and Ch20 → Ch19 I04 (the words, spoken).
- Kerrid's "teaches Rhen the last of what Dace taught him" (kerrid.md) had no scene → Ch19 I03 (the hitch).

## 3. Vowbound: bound → released
| Vowbound | Bound | Bound flag | Released | Released flag (new) | Companion |
|---|---|---|---|---|---|
| Ilun | Ch3 | (Act I) | Ch20 U01 | `ch20_ilun_released` | Asha (`ch02_heard_pila`) |
| Kahre | Ch5 | (Act I) | Ch20 U02 | `ch20_kahre_released` | Kerrid |
| Virel | Ch8 | (Act I) | Ch20 U03 | `ch20_virel_released` | Liss |
| Nhoa | Ch11 | `ch11_nhoa_bound` | Ch20 U05 | `ch20_nhoa_released` | Pell |
| Hesk | Ch12 | `ch12_hesk_bound` | Ch20 U04 | `ch20_hesk_released` | Toma |
| Ethren | Ch13 | `ch13_ethren_bound` | Ch20 U06 | `ch20_ethren_released` | Ysolde |
| Kesh | Ch16 | `ch16_kesh_bound` | Ch21 H03 | (act3_ending) | — (Sefir watching); see T-01 |

- **Release order check:** act_outline and vowbound.md give Ilun, Kahre, Virel, Hesk, Nhoa, Ethren, then the Cage, then
  Kesh, then Sefir. act3_ch20 §1 follows it exactly. (Binding order is Hesk-before-Nhoa reversed: Nhoa Ch11, Hesk Ch12.
  The release order puts Hesk before Nhoa on purpose: Pell's goodbye is the more complete one and goes later.)
- **Every Vowbound has one companion and one keepsake**, and each keepsake is the last thing to fade (act3_ch20 §7).

## 4. Open for the Lead (answered 2026-10-30: T-01, T-04 and T-07 accepted)
1. **T-01 (Kesh at H03)** is the one structural change. Approve the proposal, or keep "raises Kesh from the stones" and
   un-bind her at the end of Ch16.
2. **T-04 (the Eighth Verse's sources)** fixes three docs at once. Approve and Narrative edits them.
3. **T-07 (the Prologue's rising glimmer)** touches a shipped Act I scene, if the Prologue is staged that way.
