---
draft: pre-gate
---
# Act III Beat Sheet: Ch20 "Undertow" — six rooms of drowned memory, six goodbyes, the Cage (M5)

**draft: pre-gate.** Planning only (the Lead, 2026-10-30). No `.dlg`, flag or data until the Act III gate.

Owner: Narrative (story track). Reviewer: Cinematics; **Combat** reviews §5 (six Vowbound fights and the Cage).
Sources: [act outline Ch20](../beats/act_outline.md); SPEC §3.5 (the dive, the founders' bound spirits), §6.3 (the
Vowbound fought; released for good); [vowbound.md](../vowbound.md) §1–§6 (each final fight; release order); ADR
[0016](../../decisions/0016-act-two-restaging.md) (Ch20 row), [0015](../../decisions/0015-vowbound-element-temple-order.md);
glossary (the Cage: Orin Tesk, Halde Moor, Isse Varan, Cael Imbrey); characters (all seven); bible §9 (inside the
Undertow).

Previous: [act3_ch19.md](act3_ch19.md). Next: [act3_ending.md](../beats/act3_ending.md) (Ch21 "The Heart").
Zone: `ch20/undertow_layers` (a multi-room dungeon: six layers and the Cage's floor).

**The rules this chapter must keep:**
1. **One release per layer, in vowbound.md's order:** Ilun, Kahre, Virel, Hesk, Nhoa, Ethren. Each is a goodbye to a
   named person, led by the companion vowbound.md gives it. **Each leaves the roster for good** (SPEC §6.3); the player
   sees the Vowbound menu lose them one by one. Kesh stays for Ch21.
2. **A release is the only thing that rises.** When a Vowbound lets go, its light goes up through the dark water (the
   only `glimmer_lift` before H09, besides Nhoa's Swell). Everything else in the storm is held.
3. **Each layer is a remembered place of the drowned**, suspended in dark water (bible §9): solid enough to walk, with
   its edges fraying into motes. People in the memories are held motes in human shapes; they don't speak to the party.
4. **The founders thank them as they fall** (act outline). The Cage is four people who bound themselves and have wanted
   out for a thousand years; nothing about them is monstrous except what they're bound into.
5. **Imra and Dace are not seen in Ch20.** The heart is Ch21's (H02 withholds them until then).
6. **The Kite is spent getting them in.** Liss's dive rig takes the Kite down the eye on its last full charge; it waits
   at the top of the well, lamps dimmed. It flies again only dark, after H09 (act3_ending E4).

---

## 0. The chapter in one paragraph

The Kite goes down the eye on Liss's dive rig, through a well of black water lit by every held light the storm has
taken, and sets them on the first floor of the drowned. Each floor is a place someone remembered as they drowned: a
raft-town market at noon, a terrace on lantern-night, a Corrow kitchen, a Reefball crowd mid-roar, a drowned gallery, a
still square of gold. In each one a Saint is waiting, and in each one a friend asks Asha for the goodbye. A boy asks if
his sister had a good life. A smith asks to be hit harder. A wright asks what her people have built since. A
keth-reader asks if anyone read her cords. A Kirru sister is glad and sad to see her brother old, and he turns his back
and sings. A Tender's veil falls and it's just a man who heard every visit. At the bottom the four founders who made
the Cage wait in it, and when it breaks they thank them.

## 1. Running order

| # | Layer / beat | Memory | Release (companion) | Mode | Min | Flags |
|---|---|---|---|---|---|---|
| U00 | **Down the eye** | the well | — | C | 2.0 | `ch20_started` |
| U01 | Layer 1 | **an Oruvel market at noon** | **Ilun** (Asha; Pila's answer) | P → boss → C | 9.0 | `ch20_ilun_released` |
| U02 | Layer 2 | **a Pemakar terrace on lantern-night** | **Kahre** (Kerrid) | P → boss → C | 9.0 | `ch20_kahre_released` |
| U03 | Layer 3 | **a Corrow kitchen** | **Virel** (Liss; Wenna's marks; the Kite) | P → boss → C | 10.0 | `ch20_virel_released` |
| R1 | Rest: the party, fewer lights | a landing between floors | — | E | 1.5 | — |
| U04 | Layer 4 | **a Reefball crowd mid-roar** | **Hesk** (Toma; the cords) | P → boss → C | 9.0 | `ch20_hesk_released` |
| U05 | Layer 5 | **a drowned gallery** | **Nhoa** (Pell turns his back) | P → boss → C | 10.0 | `ch20_nhoa_released` |
| U06 | Layer 6 | **a still gold square** | **Ethren** (Ysolde; the veil) | P → boss → C | 11.0 | `ch20_ethren_released` |
| R2 | Rest: the Vowbound menu, one name left | a landing | — | E | 1.0 | — |
| U07 | **The Cage** | the founders' floor | — | P (boss) | 12.0 | `ch20_cage_broken` |
| U08 | "Thank you." | the Cage's floor | — | C | 2.0 | `ch20_complete` |
| | **Total** | | | | **~77** | |

## 2. Beat detail

### U00. Down the eye (C, 2 min)
- The Kite on the dive rig, sails furled, dropping down the well. Every held light the storm has taken hangs in the walls
  of water like a night sky turned inside out.
- **Liss spends Tobin's lamp** (ending_cost_audit §4): she stops trying to mend it and seats it in the engine socket;
  his held light is part of the last charge that takes them down. One line: *"He volunteered. So nobody'd have to be
  chosen."* Kerrid first off the Kite onto the first floor (ADR 0020: first down the
  stair).

### U01. Ilun — the Oruvel market (Asha)
- Memory: Oruvel's market hull at noon (Ch1), the cookboats, the scale-hull; held shapes buying and selling.
  Kell's stall stands with its back to the party (§10 Q2).
- **Ilun's fight** (vowbound §1): gentle, defensive; he puts himself between Asha and the dark out of habit.
- **The release:** in a boy's voice, he asks if Pila had a good life. If `ch02_heard_pila`: Asha tells him (ninety-one
  years; Osu is her granddaughter). If not: *"I don't know. I hope so."* He lifts either way. If `ch18_haluna_lifted`:
  Asha adds that Haluna lifts its own now. *It lands as: the first goodbye that doesn't hurt.*

### U02. Kahre — a Pemakar terrace on lantern-night (Kerrid)
- Memory: the terraces' boats coming down the channels (Ch5's Lanternfall), held light in every boat.
- **Kahre's fight** (vowbound §2): *"Finally. Hit harder, I'm old."* Mid-fight, to Kerrid, the dead to the dead:
  **"It doesn't hurt, son. It's like setting the tools down."** (vowbound.md: verbatim). Kerrid doesn't answer; he nods.
- If `ch05_told_the_smith`: Kahre recognises Garo's folding in a boat on the channel. One line.

### U03. Virel — a Corrow kitchen (Liss)
- Memory: a Corrow kitchen the night of the Ch8 wall-fall, a pot still on, a child's shoes by the door.
- **Virel's fight** (vowbound §3): Wenna, giddy and proud to meet a wright. If `ch08_liss_found_marks`: Liss names the
  marks she found (count by flags: Coilspire, + `ch11_found_wenna_mark`, + `ch13_found_wenna_mark`); if
  `ch08_found_sail_needle`: she shows Wenna her needle.
- **The release:** Wenna asks what they've built since. Liss names the Kite, and only now sees (rule: Ch17 planted it)
  that Dace cut its sails to Virel's shape: *"He flew your kite. We all did."* Wenna lifts laughing. *Liss gets her
  people's history back, moments before she gives up her machines.*

### R1. Rest (E, 1.5 min)
- A landing between floors. The party sits; Liss has the empty padded box in her lap (the lamp went into the Kite at
  U00). Nobody speaks. The Vowbound menu has three names left.

### U04. Hesk — a Reefball crowd (Toma)
- Memory: a Tidecup gallery mid-roar, every held face turned to a float that never surfaces.
- **Hesk's fight** (vowbound §4): Holy, cleansing, Regen.
- **The release:** Ama asks whether anyone read her cords. Toma: he did (with Ysolde, `ch12_ysolde_confessed`); they
  broke his faith; he thanks her for it. If `ch15_toma_confessed` and `ch14_toma_refused`: one more line, *"I stopped
  saying it. 'Be level.' I say your count instead."* *A believer honouring the believer who told the truth.*

### U05. Nhoa — a drowned gallery (Pell)
- Memory: a Lit Age gallery like the Vey's, lamps steady, silt-light falling (no ice: ADR 0015).
- **Nhoa's fight** (vowbound §5): she copies the last action. Pell fights her silently. If `ch15_pell_said_he_knew`,
  before the fight: **"I knew about him too. I did not say. I am learning when to say."** (act2_ch15 flag table).
- **The release:** she is glad to see him and sad that he is old. As she starts to lift, **Pell turns his back** and
  sings the farewell-tide (`ch18_learned_farewell_tide` taught Asha; this is Pell's own). Asha turns her back with him.
  Her name-shell (the keepsake) is the last thing to go up. If `ch18_pell_named`: she sees his new shell and touches it.
  *The most complete act of love in the game, done by looking away.*

### U06. Ethren — a still gold square (Ysolde)
- Memory: a square of Ansedra under the Level, water that has never moved, a Tender sweeping a step.
- **Ethren's fight** (vowbound §6): the hardest Vowbound fight; Slow, Stop, wards.
- **The release:** mid-fight the veil falls and it's Corran's face. He tells her he heard every visit. She tells him
  she's not coming back to the Sanctum any more. If `ch13_corran_house`: she tells him someone else lives in their house
  now, and that it's all right (act2_ch13 flag table). If `ch13_camp_talk`: Asha stands behind her, not beside. The
  copper ring is the last thing to fade. *The widow's goodbye she refused for twenty-four years.*

### R2. Rest (E, 1 min)
- The Vowbound menu: one name, Kesh. Asha's sleeve still full (S7); it unravels only in H07 (act3_ending §0 rule 5).

### U07. The Cage (P, 12 min). See §5.

### U08. "Thank you." (C, 2 min)
- The four founders fall one by one, each saying thank you (act outline). The last, Cael Imbrey, says it to Asha and
  then, looking past her down the well: *"She's waiting for you. Both of them are."* (Imra and Dace, unnamed: rule 5.)
- The Cage's bars are bound light; when it breaks they don't lift yet (only Vowbound release here: rule 2). They lie in
  the dark water, held, waiting for H09. Sets `ch20_complete`.

## 3. Flags
| Flag | Set at | Read by | Use |
|---|---|---|---|
| `ch20_started`, `ch20_complete` | U00, U08 | flow | — |
| `ch20_<vowbound>_released` ×6 | U01–U06 | vowbound.json (`released_flag`), the summon menu, codex | each leaves the roster |
| `ch20_cage_broken` | U07 | H01 | the last layer opens |

**Reads from Acts I–III:** `ch02_heard_pila` (U01), `ch18_haluna_lifted` (U01), `ch05_told_the_smith` (U02),
`ch08_liss_found_marks`, `ch08_found_sail_needle`, `ch11_found_wenna_mark`, `ch13_found_wenna_mark` (U03),
`ch12_ysolde_confessed`, `ch15_toma_confessed`, `ch14_toma_refused` (U04), `ch15_pell_said_he_knew`,
`ch18_pell_named`, `ch18_learned_farewell_tide`, `ch11_pell_knelt` (U05), `ch13_corran_house`, `ch13_read_cantor_roll`,
`ch13_camp_talk` (U06), `ch16_line_held` (U00, U07).

## 4. No side scene
The layers are the chapter. Optional content: each layer's memory has one examinable held figure with a caption
(a drowned person's last ordinary moment), ~6 captions.

## 5. The bosses (Combat's mechanics; Narrative's lines)
- **The six Vowbound** fight with the toolkits the player used (vowbound.md battle identities), and each fight's
  pressure is emotional, not numeric: each can be won at a moderate level (§10 Q4). The party's own Vowbound calls
  shrink as each is released (SPEC §6.3), so later fights are harder by subtraction.
- **The Cage: Orin Tesk, Halde Moor, Isse Varan, Cael Imbrey** (glossary), four bound founders fought as one
  multi-part boss (act outline). The cage itself is the boss's body: four seats of bound light round a well, each
  founder chained into one. Break a seat's chains and that founder stops fighting and thanks you; the rest grow
  stronger. **Toma holds the line** (toma_okeru.md: "holds the line against the Cage-Wardens"): a locked-active set
  piece like Ch8's stair and Ch16's line, with Toma locked (if `ch14_toma_refused`, his Swell is primed).
- **Lines (~60 words):** the founders speak only Lamptongue phrases Ysolde translates in the help line, except "thank
  you", said in the common tongue each time.

## 6. Music cues (requests)
`undertow_descent` (U00), one memory cue per layer built on that place's Act I/II cue, held and slowed (`oruvel_raft`,
`lanternfall`, `coilspire`, `tidecup`, `lowlight`, `ansedra`), each Vowbound's `<name>_summon` sting reversed at
release (`release_sting`, act3_ending H03 precedent), `the_cage` (U07), `thank_you` (U08: the four voices, one by one).

## 7. Camera shots (proposals)
U00 the Kite dropping down the well, inside-out night sky · per layer: the memory's establishing shot, then its edge
fraying into motes · per release: the keepsake last (net-float, hammer, tuning key, keth bundle, name-shell, ring) ·
U05 Pell's back in the foreground, Nhoa lifting out of focus behind him · U08 Cael Imbrey looking down the well.

## 8. Word counts
Six releases ~180 each = ~1,080; R1/R2 ~20; Cage ~120; U00/U08 ~80; captions ~150. **~1,300 spoken + ~150 read.**
Under SPEC §3.6's band for ~77 min (it's a fighting chapter), and every word is a goodbye.

## 9. Requests to other roles
- **Combat:** the six Vowbound as bosses (their roster kits), the Cage (four seats), Toma's locked line; vowbound.json
  `released_flag` per Vowbound.
- **Environment Art:** `ch20/undertow_layers`: six memory floors and the Cage floor, each fraying into motes.
- **Rendering/VFX:** each release's `glimmer_lift` (the only rising light before H09); the keepsake lingering last.
- **UI:** the Vowbound menu losing names (no animation that makes it a reward; a name greys and goes).
- **Audio:** §6.

## 10. Open questions and defaults
1. **Layer ↔ Vowbound pairing.** act_outline names three memories (an Oruvel market, a Corrow kitchen, a Reefball crowd)
   and six releases. **Default:** six layers as §1, the outline's three plus a Pemakar terrace, a drowned gallery and a
   still gold square, each fitting its Saint. Swap freely; the release order (rule 1) is fixed.
2. **Kell in the market.** **Default:** her stall is there with someone at it, back turned, trimming wicks; Rhen sees it
   and doesn't go over. No line. If the Lead thinks it pre-empts E7, cut the figure and leave the stall empty.
3. **"Cage-Wardens" vs "the Cage".** toma_okeru.md and vowbound.md say "the Cage-Wardens"; act_outline and the glossary
   say "the Cage" (four bound founders). **Default:** the boss is *the Cage*; "Cage-Wardens" is retired in favour of
   naming the four (act3_threads T-10).
4. **Difficulty.** **Default:** the Vowbound fights are tuned to be won by a party that kept its Vowbound (the toolkit
   shrinks as you go); Design owns numbers.
5. **Liss's dive rig.** **Default:** the Kite's last full charge takes it down; it waits at the well's top, dim, and
   flies dark only after H09 (act3_ending E4).
6. **What Cael Imbrey says** (U08) names nobody. If Cinematics wants silence instead, cut it; H02 still withholds them.
