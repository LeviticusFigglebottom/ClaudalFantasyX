# Act II Beat Sheet: Ch13 "Gold and Lacquer" in Ansedra, the Sanctum and the Lamp Archive, four days (M4)

**draft: pre-gate.** Written ahead of the Act I gate as ADR 0203 preparation (the Lead's assignment and order, 2026-10-30). Docs only: no `.dlg`, flag or data exists for anything below until the gate passes and M4-C13-01 is reviewed. **Written after Ch14:** the "What Ch13 hands this chapter" list in [act2_ch14.md](act2_ch14.md) is this sheet's contract, and the flags it proposed (`ch13_archive_read`, `ch13_pact_of_silence`) are declared here.

Owner: Narrative (M4-C13-01; drafted by the act2-plan track). Reviewer: Cinematics (SPEC §12.3). The Lead reviews the Archive beats (ADR 0016 (b)).
Sources:
- [act outline Ch13](act_outline.md);
- ADRs: [0016](../../decisions/0016-act-two-restaging.md) (b) (the founding truth on paper, before the wedding), [0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (c) (Sefir lets Kerrid be);
- [decisions_log N-04](../decisions_log.md) (the gilt line, worn at the Sanctum binding), N-18;
- [bible §2, §5.8 (Ansedra), §6 (the Order)](../bible.md), [vowbound.md §6 (Ethren)](../vowbound.md), [voice guide](../voice_guide.md);
- the characters: [Ysolde](../characters/ysolde.md), [Liss](../characters/liss_varrow.md), [Sefir](../characters/sefir_aurane.md), [Kerrid](../characters/kerrid.md);
- art: [color script `ch13`](../../art/color_script.md), [ansedra.md](../../art/environments/ansedra.md) (the kit: `sanctum_basin`, `archive_stacks`, `bowl_dome`), [vowbound/ethren.md](../../art/creatures/vowbound/ethren.md);
- the plan: [act2_plan.md §2 Ch13, §4.5](../../plan/act2_plan.md) (the document reader, M4-A2P-080).

Previous chapter: [act2_ch12.md](act2_ch12.md). Next: [act2_ch14.md](act2_ch14.md).
Greybox: M4-C13-02:
- `ch13/ansedra`: the outer moorings `kerrid_moorings`, the causeways, Sefir's house `sefir_door`, Corran's old house `corran_house`, the archive's isle, the Sanctum's isle;
- `ch13/sanctum`: the vestibule, the nave round the basin, `ethren`, `corran`, `pilgrims`;
- `ch13/lamp_archive`: the reading room, `ledgers`, `cantor_roll`.

Scripts: none yet (M4-A2P-004). Sample lines set the voice only.

**The rules this chapter must keep:**
1. **Nobody says "revenant".** The founding truth arrives as paperwork: ledgers, a roll, a margin, the same hands across four hundred years. Liss lays the pages side by side, and nobody names what it means (act_outline Ch13; ADR 0016 (b)).
2. **Asha is not the bride, and the wedding is not hers** (ADR 0016's Ch13 row). It's Tobin's and Merel's.
3. **Kerrid never enters the Sanctum,** never takes Sefir's hospitality, and sits out every night at the outer moorings among the barge-polers. Sefir knows what he is and lets him be (ADR 0022 (c)). Nothing is said about it.
4. **Ansedra is still.** No wind, no wake, no seabirds, no dogs, no children's games (bible §5.8). Every barge is poled. Nothing on the water moves until Ch14's escape.
5. **Gold is cold** (color script `ch13`): wealth, not warmth. The only warm notes are human: Tobin's laugh, an oil lamp at the moorings, Corran's old house.
6. **Sefir is warm, and he means it.** He is no sneering villain: he answers grief with logic, and his kindness to Asha is real in his own mind (sefir_aurane.md). The staging tells the player he knows what Liss read; no line does.

---

## 0. The chapter in one paragraph

Ansedra is a city of perfect stillness: gold bowl-domes doubled in a lagoon kept flat by something under the water, barges poled so they leave no wake, no seabirds, no dogs, no children playing. The High Warden himself meets the party, gracious and warm, and puts them up in his own house. Kerrid doesn't come in; he sits out the nights at the outer moorings with the barge-polers, and Sefir lets him. The peace wedding is announced: in four days Liss's brother Tobin will marry Merel Dask, a Warden's daughter, and Hollowmere's hull-captains have come to the holy city as guests for the first time in living memory. Liss campaigned for it for three years, and she lets herself hope. In the Sanctum of the Level, a basin of water so still it's a mirror, lit from beneath by a light that never moves, Asha binds the Saint Ethren, and Ysolde stands before her husband Corran with a Cantor beside her for the first time in twenty-four years. Liss looks at the light under the water for a long time and says nothing: it's bound glimmer, the thing her people are burned for. To show the Order has nothing to hide from a Saltwright, Sefir gives Liss the run of the Lamp Archive for the three days before the wedding. With Ysolde she finds what it keeps in plain sight: the founders' own lamp-ledgers, showing they were binders who bound themselves and the storm together; the Cantor roll with a column the public copies leave out, *kept* or *spent*; Corran's line, *kept, Sanctum*, and in the margin, in a hand Ysolde has seen on every Warden's seal all her life, *to be spent at the next Calm*; and the same few hands signing the ledgers across four hundred years. They agree to say nothing until Tobin is married and they can get him out. Tobin won't call it off. Sefir knows exactly what Liss read. He let her.

**Emotional line:**
1. airless beauty (the city);
2. welcome that's almost too kind (Sefir);
3. hope (Liss and Tobin);
4. reverence turning uneasy (the Sanctum);
5. a widow and her husband;
6. study (the Archive);
7. the column (*kept, spent*);
8. a margin;
9. hands that shouldn't match;
10. a pact made in fear;
11. a house where someone else lives now.

**What the chapter must prove:**
- the sixth Vowbound bound (verse-sleeve **S6**);
- **the founding truth on paper, before the wedding** (ADR 0016 (b)): the Lamplighters were binders; the Order forbids binding so only the Order binds; Saints are *kept* to be *spent*; the same hands for four centuries;
- Ysolde does the maths on Corran;
- Tobin and Merel met, so Ch14 costs what it should;
- the pact of silence;
- Sefir knowing.

---

## 1. Running order

Time is in-world (four days: arrival, the Sanctum, three days in the Archive, the eve of the wedding). Minutes are a first-time player's. Modes:
- **P**, play;
- **C**, cutscene;
- **E**, in-engine scene with player input.

Shot ids are proposed in §7 (A = Ansedra, S = the Sanctum, R = the Archive's reading room).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The still city** | `ch13/ansedra`, poled in from the outer moorings | day 1, 16:30 | C | 1.5 | A01–A03 | `ansedra` | Beautiful and airless. Kerrid stays at the moorings. | `ch13_started` (exists) |
| B02 | **The High Warden's house** | `sefir_door` | 16:45 | C | 2.0 | A04–A06 | `ansedra` (warm, stripped) | Hospitality that's almost too kind. The wedding announced; the two keys offered. | `ch13_wedding_announced` |
| B03 | **Tobin** | the guest moorings where Hollowmere's barge is tied | 17:10 | E | 3.0 | A07, A08 | `peace_wedding` (first statement, sparse) | Liss's sunlight. Meet Tobin and Merel. | `ch13_met_tobin` |
| B04 | **Ansedra** | `ch13/ansedra` | 17:30 | P | 7.0 | A09, A10 | `ansedra` | A city with no seabirds; Order shops; the moorings at dusk. | `ch13_sat_at_moorings` (optional) |
| B05 | **The Sanctum** | `ch13/sanctum`, the nave round the basin | day 2, 10:00 | P → C | 3.0 | S01–S03 | `sanctum_of_the_level` | A mirror lit from beneath. Pilgrims kneel. Liss looks at the light. | — |
| B06 | **Ethren** | the basin's edge (`ethren`, `corran`) | 10:15 | C | 3.5 | S04–S09 | `sanctum_of_the_level` → `ethren_bound` (sting) | Ysolde before her husband with a Cantor beside her. | `ch13_ethren_bound` |
| B07 | **The Archive, day one: the ledgers** | `ch13/lamp_archive` | day 2, 14:00 | P (document reader) | 5.0 | R01, R02 | `lamp_archive` | Study. The founders were binders. | `ch13_read_ledgers` |
| B08 | **Day two: the roll** | the reading room, the lectern (`cantor_roll`) | day 3, 11:00 | P (document reader) → C | 4.0 | R03–R06 | `lamp_archive` → `silence` | *Kept. Spent.* Corran's line, and the margin. Ysolde does the maths. | `ch13_read_cantor_roll` |
| B09 | **Day three: the hands** | the reading room | day 4, 15:00 | P (document reader) → C | 3.0 | R07–R09 | `silence` | Liss lays the pages side by side. Nobody names it. | `ch13_archive_read` |
| B10 | **The pact** | the moorings at night (`kerrid_moorings`) | day 4, 22:00 | C | 2.5 | A11–A14 | `ansedra` (night) | Say nothing until he's married. Tobin won't call it off. | `ch13_pact_of_silence` |
| B11 | **Sefir closes the book** | the Archive, empty | day 4, 23:00 | C | 0.5 | R10 | `silence` | He knows exactly what she read. He let her. | — |
| B12 | *Side scene: "Someone Else's House"* (optional) | `corran_house` | any, B04–B10 | E | 4.0 | A15 | `silence` → `ansedra` (far) | Ysolde shows Rhen the house she shared with Corran. | `ch13_corran_house` |

**Totals:** critical path **35.5 min** (all but B12). With B12, **39.5 min**. Split: **19 min playable (54%)**, 13.5 min cutscene, 3.0 min in-engine. There are **no fights** in Ch13 (act_outline: no boss); the play is the city walk and the three Archive days in the document reader (M4-A2P-080), which is the chapter's mechanic.

**Cut order if the chapter runs long:**
1. B04 shortens to the moorings walk.
2. B07 folds into B08 (the ledgers are read on day two too).
3. B03 shortens to one exchange.

**Never cut:** B06, B08, B09, B10, B11, and enough of B03 that the player has met Tobin and Merel and seen Liss happy.

---

## 2. Beat detail

### B01. The still city (C, 1.5 min)
- **A01:** day 1, 16:30, overcast, perfectly still air (color script `ch13`). From a poled barge at the lagoon's edge: **Ansedra**, gold bowl-domes on tiered red-lacquer bases on islands of white stone, every one doubled exactly in a lagoon so flat it's a mirror, so that you can't tell which way is up (ansedra.md). Gold everywhere, and it feels cold.
- **A02:** the outer moorings: lacquered barges, barge-polers in plain grey, oil lamps on poles (the only warm light: rule 5). The polers who meet the party push off with long careful strokes that leave **no wake** (rule 4). Rhen, quietly, a diver watching the water: *"They're not making ripples. How are they not making ripples? I make ripples in a bath."* (The joke is his fear: voice guide.) Nobody answers.
- **A03:** **Kerrid steps off at the outer moorings** and doesn't get into the city barge. He takes his place standing by a mooring post among the polers. ("Sits out the nights" in kerrid.md means stays out; **he never sits**, Prologue to Ch15, and Ch15's K05 is the first time anyone sees him sit. He stands among working men all night, and that's all anyone sees.) Asha looks back; he lifts a hand. The party goes in without him (rule 3; the flow's `party` step, as `chapters/ch13.json` already does).

### B02. The High Warden's house (C, 2 min)
- **A04:** Sefir's house on the central island (`sefir_door`): white stone, lacquer, a garden of raked white gravel where nothing grows. **Sefir** meets them himself, in pale still-water silk with the gold half-mantle and bowl-crown, unnaturally still, with no breathing idle (sefir_aurane.md). He is delighted to see them.
- **His welcome** (~120 words: "complete paragraphs in miniature"; voice guide):
  - Sefir, to Asha: *"Lady Cantor. You have come further than most, and faster. Ansedra is yours. Rest here. Nothing in this city will hurry you."*
  - **The wedding:** *"And you have come at a good time. In four days a Saltwright will marry a Warden's daughter, in the Lacquer Court, and I will say the words. Mistress Varrow's brother. I believe she had something to do with it."* Liss, despite herself, flushes. Sets `ch13_wedding_announced`.
  - **The two keys:** to Asha, *"The Sanctum is open to you tomorrow."* And then, to **Liss**, kindly, holding out a heavy bronze key: *"And to you, Mistress Varrow, the Lamp Archive, for as long as you are our guest. You were told for years the Order hides the Lit Age from your people. Read whatever you like. We have nothing to hide from a wright."*
  - Liss takes the key. She doesn't say thank you. (Act I: she never forgave him for being kind about the Shoals.)
- **A05:** Sefir glances past them toward the lagoon, toward the outer moorings where a big man stands among the polers. Half a beat. Then back to Asha, warm. (ADR 0022 (c): he knows what Kerrid is and lets him be. Rule 3.)
- **A06:** Toma bows to the High Warden as a former Stillguard does, deeply. Sefir: *"Be level, Okeru."* Toma: *"And still, High Warden."* (Toma's faith is cracked but still answering. Ch14 B04 is the first time he doesn't.)

### B03. Tobin (E, 3 min)
- **A07:** the guest moorings, where Hollowmere's delegation barge is tied: a lashed Saltwright hull, sea-stained, ridiculous among the lacquer. **Tobin Varrow** jumps off it before it's tied. He's charming, idealistic and loud in a quiet city (liss_varrow.md). He picks Liss up off her feet.
  - Tobin: *"You came. You actually came. Three years of letters telling me this was a terrible idea, and you came."*
  - Liss, upside down: *"Put me down. Put me down, you're making ripples."*
  - Tobin: *"Good."*
- **A08:** **Merel Dask** steps carefully off the same barge behind him, a Warden's daughter in plain good clothes, brave and sincere, a little overwhelmed (liss_varrow.md; she loves him). She bows to Asha, then hesitates, and offers Liss her hand, Saltwright fashion, palm to palm. Liss looks at it a long moment, then takes it.
  - Merel: *"He talks about you all the time. Mostly complaints."*
  - Liss: *"Good. Accurate."*
  - Tobin, to Rhen, a stranger he's decided is a friend: *"You're the diver. She mentioned you. She said, 'Don't trust the diver.' So I like you already."*
- The player can talk to each once more (optional, ~60 words in all). Tobin's line, if asked why: *"Somebody had to go first. I volunteered. Nobody had to be chosen."* (ADR 0020; Ch14's B01 echoes it.) Sets `ch13_met_tobin`. ~110 words.

### B04. Ansedra (P, 7 min)
- **The zone:** `ch13/ansedra`'s causeways with gold lamp-posts (unlit by day), the islands, the domes, the outer moorings. Stillness everywhere: walking pilgrims, Tenders, Stillguard at the bridges, polers. **No seabirds, no dogs, no children's games** (rule 4).
- **Systems:**
  - **the Ansedra purveyor** (M3-UI-209's `ansedra_purveyor`: the Act II tier-2 gear; marked an **Order shop** for Ch14's heresy rule: M4-A2P-031);
  - an inn (Sefir's house is the party's rest);
  - an Order shrine (it goes dark at Ch14's heresy: plan §4.2);
  - **no fights**.
- **The outer moorings at dusk** (optional, sets `ch13_sat_at_moorings`): Kerrid on his mooring stone among the polers, an oil lamp on a pole. Rhen can stand with him. Kerrid says nothing for a long time, then: *"They pole well here."* (Beat.) *"Too well."* (A stair-watch captain's eye on water that won't move.) A poler offers him a bowl of rice; he sets it down untouched (kerrid.md's clue list: he never eats).
- **Barks** (~100 words):
  1. A Tender, to Asha, rapt: *"Lady Cantor. The water has not moved in four hundred years. Isn't it peaceful?"*
  2. A pilgrim at a causeway, to her child, very low: *"Hush. You'll stir the water."* (There are children. They don't play.)
  3. Ysolde, crossing a causeway, not stopping: *"I grew up here. I used to think the quiet was holiness."*
  4. A Stillguard at a bridge, to Toma, recognising the chiselled pauldron: *"Okeru? From the Corrow wall?"* Toma: *"Once."*
  5. Liss, at the lagoon's edge, kneeling to look at the water, then **putting her palm flat on it**: *"It's pushing back. Something's holding it down."* (bible §5.8: forbidden machinery under the city. Day 2's ledgers confirm it.)

### B05. The Sanctum (P → C, 3 min)
- **Day 2, 10:00.** The Sanctum's isle. The party walks through the vestibule into the nave. **Kerrid isn't with them** (rule 3).
- **Optional: Wenna's third mark** (reads `ch11_found_wenna_mark`): in the vestibule, behind a pilgrims' kneeling rail, the old-style lines and node-dots and the key glyph (act1_ch08 B05). Liss finds it and goes white: *"In the Sanctum. She came here. She knelt here and scratched her name under their noses."* (Vowbound.md §3. Sets `ch13_found_wenna_mark`.)
- **S01:** the nave round **the basin**: 14 m of water held so still it is a **perfect mirror** (the still-water look, M4-A2P-047), white-rimmed with a gilt Level line, **lit from beneath** by a steady teal-white light through salt-glass tiles (`glimmer_bound`, `sanctum_basin`). It's the only light in the hall: no lamps, no windows (ansedra.md). Pilgrims kneel on the steps outside the rim, humming the Order's hum, very low.
- **S02:** **Liss looks at the light.** She stands at the rim for a long time, looking down through the mirror at the light under it. It's bound glimmer, the thing her people are branded and burned for (Ch6), lighting the Order's holiest place. **She says nothing** (act_outline). The camera stays on her until it's uncomfortable.
- **S03:** Ysolde beside Asha, very straight, the voice of twenty-four years (the voice guide's sample, fixed): **"The Saints are at peace. I visit my husband every year. He has never once been anything but at peace."** Asha takes her hand. Ysolde lets her.

### B06. Ethren (C, 3.5 min)
- **S04:** a Tender paints the **gilt line** on Asha's face before the binding, "so the dead can find her" (decisions_log N-04: worn at the Sanctum binding). Ysolde watches the brush.
- **S05:** above the basin, rising out of its mirror without disturbing it: **Ethren**, the Level Saint: an armoured winged figure of gold lacquer with a veiled face and a bowl-halo, lit from inside by a steady bound light that never drifts (vowbound/ethren.md). Beautiful and impersonal. **A plain copper wedding ring** on one gauntleted finger, the only thing about him that doesn't shine.
- **S06:** **Ysolde stands before Corran with a Cantor beside her** (act_outline): for eleven years, since he was placed here, she has stood here alone. She doesn't speak to him. She looks at the ring.
- **S07 (the binding, ~90 s; M4-A2P-071):** Asha sings the verses she has. **The sixth verse** comes out of the still light under the water, sung in a man's voice, patient and kind (Audio: `ethren_bound`): Corran's. Ysolde closes her eyes on the first word. The light rises from the mirror to Asha's staff without making a ripple (rule 4). The verse-sleeve grows to **S6**. Ethren is bound to Asha.
- **S08:** as it settles, the veiled head turns, once, toward **Ysolde** (as Nhoa toward Pell, Ch11 N08; Hesk to her cords, Ch12 C04). The veil doesn't fall: that's Act III's (vowbound.md §6).
- **S09:** Ysolde, eyes still shut: *"Thank you, Lady Cantor."* (She uses the title: formal, because the alternative is breaking.) Sets `ch13_ethren_bound`. ~10 words.

### B07. The Archive, day one: the ledgers (P, document reader, 5 min)
- **R01:** the **Lamp Archive**: a white vault over bays of black-lacquer ledger cases with red shelves of ledgers in cream and red spines, rolling ladders, and at the far end a lectern with the Cantor roll on it (`archive_stacks`). Empty. The Order keeps its truth in plain sight because nobody reads (ADR 0016 (b)).
- **The mechanic:** the **document reader** (M4-A2P-080). Liss (the player, with Liss) pulls ledgers. Each opens in the reader as a spread of Lit Age lamp-ledger pages (loc-keyed record texts: M4-A2P-004). The player can **lay two or three records side by side** and mark matches. Ysolde reads the Lamptongue aloud on request (her line per record). No fail state: the reader only records what's been found.
- **What day one finds** (three records the player must open; others optional):
  1. **A Lamplighter's lamp-ledger** of the First Rising: an engineer's log of binding glimmer into the anchor-engines at Iskarra, with the binders' names and marks, among them a **Saltwright-style line-mark** on a founder's signature line. Liss: *"That's a wright mark. On a founder."* (They were binders.)
  2. **The Binding Ledger:** an entry recording that the founders **bound themselves and the storm together**. The page is **torn** across: what's left reads only *"…the Cage made… …the heart sung in… …kept by one…"* (ADR 0204 §15: fragmentary, a torn line, not a statement). Ysolde translates the fragments flat and doesn't guess at the gaps. Asha reads over her shoulder and goes still.
  3. **The first Salt Edict's draft**, in the margin of a later ledger, in a clear hand: *"Forbid the binding, that the binding be kept."* Liss reads it twice. *"So only they bind."* (bible §6 creed: "The Order forbids binding so that only the Order binds.")
- Sets `ch13_read_ledgers`. **Rule 1:** nobody draws the conclusion about who's still alive. ~80 words of spoken lines, plus the record texts (M4-A2P-004 writes them, at about 300 words over the three days).

### B08. Day two: the roll (P → C, 4 min)
- **R03 (P, the reader):** the **Cantor roll** on its lectern: all sixty-one names, the public roll's columns (number, name, house, year), and one more column at the right that **the public copies leave out**: *kept* or *spent* (act_outline Ch13). The player reads down it with Ysolde. *Spent. Spent. Spent.* Seven are *kept*.
- **R04 (C):** Ysolde's finger stops at the sixtieth line. **Corran Ysel. Sixtieth. Tender, Ansedra. Kept, Sanctum.** And in the margin, small, in a hand she has seen **on every Warden's seal for her whole life**: *to be spent at the next Calm.*
- **R05:** **Ysolde does the maths** (ADR 0016 (b): here, not in Ch15). Very quietly, exactly, as she corrects pronunciation mid-crisis:
  - Ysolde: *"Kept, Sanctum. To be spent at the next Calm."* (Beat.) *"The next Calm is hers."* She looks at Asha. *"When you sing, Lady Cantor, they spend him."*
  - Asha (she bound him yesterday): *"...I have him. He's with me now."*
  - Ysolde: *"Then I would ask you to keep him a little longer."* (Her warmth as an instruction, at its most terrible.)
- **R06:** Ysolde puts both hands flat on the lectern and doesn't move. Liss, who has never been gentle with her, comes and stands beside her shoulder to shoulder and says nothing. `@music silence`. Sets `ch13_read_cantor_roll`. ~60 words.

### B09. Day three: the hands (P → C, 3 min)
- **R07 (P, the reader):** Liss's idea: she lays **ledgers from four centuries side by side** in the reader, page by page, and has the player mark the signatures. The same marks repeat: **the same few hands**, the same slant, the same pen-lift, signing in 600 AL and 800 AL and 1000 AL, under different names (act_outline; bible §6: Sefir "has held the High Warden seat under a dozen names").
- **R08 (C):** the reader's view pulls out: **eight pages in a row on the reading table, four hundred years apart, signed by the same hand**, and among them the margin hand from Corran's line. Ysolde recognises it, and so does the player: **the High Warden's**.
- **R09:** Nobody says it (rule 1). Liss just lays the last page down at the end of the row and steps back. Toma, who has said nothing for three days, says nothing now. Rhen opens his mouth to make a joke and doesn't. Asha looks at the row a long time.
  - Asha (the only line): *"These are all the same person."*
  - Ysolde: *"Yes."* (Beat.) *"Or they are all the same few people."*
  - That's as far as it goes. Sets `ch13_archive_read`. ~20 words.

### B10. The pact (C, 2.5 min)
- **A11:** day 4, 22:00, the outer moorings, lamps on poles over still black water. The party has come to Kerrid, out of the city, because it's the one place in Ansedra they don't feel watched. Kerrid is standing where he always stands. He turns when they come, and listens.
- **The pact** (~120 words):
  - Liss: *"Tobin's married tomorrow. Then we get him out. Then we say it. All of it. Not before."*
  - Toma: *"If we say it before, they will not let him marry. They will not let him leave."*
  - Rhen: *"So we smile at the wedding."* Ysolde: *"We have all smiled at worse."*
  - Asha: *"And the High Warden?"* A silence. Nobody answers.
- **A12:** Tobin has come out to the moorings after them, because his sister is out at night. He heard the end of it. Liss tells him, fast, in a whisper. He listens. Then:
  - Tobin: *"No."* (Sincere, and not stupid.) *"If I run, there's no peace. Hollowmere's captains are here, Liss. They came because I said it was safe. If I run the night before, they're all hostages. If I marry her, they go home as family."* (Beat.) *"Somebody has to go first."*
  - Liss: *"Tobin."*
  - Tobin: *"One day. Then you can get me out of whatever you like."*
- **A13:** Kerrid, at the edge of the lamplight, watching the still water. He says nothing. (He knows what it is to hold a gate past the hour for someone.)
- **A14:** wide: the party on the moorings, small, and the city behind them, gold domes doubled in black water, absolutely still. Sets `ch13_pact_of_silence`.

### B11. Sefir closes the book (C, 0.5 min)
- **R10:** the Archive at 23:00, empty, one lamp. The ledgers are back on their shelves, except the row of eight pages Liss left on the reading table. **Sefir** walks the aisle alone, unhurried. He looks down at the eight pages in their row, his own hand four hundred years apart. He gathers them, squares the edges, and closes the ledger. Then he puts out the lamp.
- No dialogue. **Rule 6:** it isn't a villain's gloat. It's a man tidying up, who expected this. (act_outline: "Sefir knows exactly what Liss read. He let her.")

### B12. Side scene (optional): "Someone Else's House" (E, 4 min). See §4.

**End of chapter:** the flow hands off to Ch14 on the wedding day (act2_ch14.md B01). Sets `ch13_complete` (flow).

---

## 3. Flags

Declared in `game/data/flags.tres` when the gate passes (M4-A2P-013 adds them). The greybox's three Ch13 flags (M4-C13-02) stay as they are.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch13_started` | B01 (exists) | flow | — |
| `ch13_wedding_announced` | B02 | Ch14 | — |
| `ch13_met_tobin` | B03 (critical) | Ch14, Ch15 | Ch14's B01 talk; Ch15's grief |
| `ch13_sat_at_moorings` | B04 (optional) | Ch15 | In the confession, Kerrid to Rhen: "You sat at the moorings with me. You didn't ask. I noticed." (Narrative may keep it) |
| `ch13_found_wenna_mark` | B05 (optional; needs `ch11_found_wenna_mark`) | Ch20 | Liss names Wenna's three marks to Virel |
| `ch13_ethren_bound` | B06 (critical) | vowbound.json, the summon menu, verse-sleeve S6 | Ethren in Asha's roster |
| `ch13_read_ledgers` | B07 | the codex | the ledgers as found records |
| `ch13_read_cantor_roll` | B08 (critical) | Ch16, Ch20 | **Ch16:** Ysolde to Sefir: "Do the sum, High Warden. I already have." **Ch20:** Ethren's fight |
| `ch13_archive_read` | B09 (critical) | Ch14 (B03's "You gave me the key"), Ch16 | — |
| `ch13_pact_of_silence` | B10 (critical) | Ch14 | the party smiles at the wedding |
| `ch13_corran_house` | B12 (optional) | Ch20 | Ysolde tells Corran someone else lives there now, and that it's all right |
| `ch13_complete` | end of B11 | flow (Ch14 gate) | — |

**Flags this chapter reads:** `ch06_met_sefir`, `ch06_rhen_greeted_sefir` (Sefir's greeting to Rhen), `ch11_found_wenna_mark`, `ch12_ysolde_confessed` (Ysolde reads the roll already suspecting, so her hands are steady).

---

## 4. The optional side scene: "Someone Else's House" (B12)

**Where:** Corran's old house (`corran_house`), a small lacquered house on a lesser island, with a family living in it now. **When:** any evening from B04 to B10, through a marker on Ysolde at a causeway's end. **Length:** 4 min, ~170 words. **Speakers:** `ysolde`, `rhen`, `householder` (one line).

**Beats** (act_outline Ch13):
1. Ysolde stops on a causeway and looks at a small house with a red door and a child's sandal on the step. Rhen stops with her.
2. Ysolde: *"That was our house. Corran's and mine. Eleven years."* (Beat.) *"The Order gave it to a Tender's family when he was raised. They have painted the door."*
3. Rhen: *"Do you want to go in?"* Ysolde: *"No."* (Beat.) *"Yes."*
4. They knock. A young mother opens the door. She recognises the Cantor's tutor and bows, flustered, and lets them stand in the front room for a minute. It's full of someone else's life: toys, laundry, a pot on the fire.
5. Ysolde looks at one thing only: a **scorch mark** on the wall by the stove, old and painted over, still showing through.
   - Ysolde: *"He was a terrible cook. That is from a fish."* (Corran: "patient, funny, and a terrible cook": vowbound.md §6.)
   - Rhen laughs, before he can stop himself. **Ysolde laughs too**, once, a real laugh. It's the first time in the game (pillar 1: warmth, never undercutting; here it *is* the grief).
6. The householder: *"Should we paint over it again, Mistress?"* Ysolde: *"No. Please. Leave it."*
7. Outside, Ysolde, to Rhen, exact: *"Thank you, Master Sallow. I have decided to notice."* (A turn on her voice-guide line, "I have decided not to notice.")

**Rules:** no Archive talk in the scene. Corran is spoken of in the past tense, as a man, not as a Saint. Ysolde cries at no point.
**Payoff:** `ch13_corran_house` (§3).

---

## 5. No boss

act_outline Ch13 has no boss and no fights: Ansedra is a town and the Archive is a library (act2_roster: "Ansedra and the Lamp Archive have no fights"). The chapter's play is the city walk and the document reader. Its tension is a pact and a key, and they pay off in Ch14.

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `ansedra` | B01, B02 (warm, stripped), B04, B10 (night) | Zone loop (exists, M3-AUD-842) | B10 wants a night mix. |
| `peace_wedding` | B03 (first statement, sparse) | Exists (M3-AUD-842) | Its melody's first statement, on one instrument, as Tobin jumps off the barge, so the player knows the tune before Ch14 breaks it. |
| `sanctum_of_the_level` | B05, B06 (bed) | **Zone loop**, ~120 s (not yet written: act2_finals.md; M4-A2P-091) | The still mirror: sustained, almost motionless, beautiful and wrong. The Order's hum (ORDER_HUM) at its most perfect. No pulse at all. |
| `ethren_bound` | B06 (S07) | **Sting**, ≤ 8 s (not yet written; M4-A2P-091) | The sixth verse in a patient, kind man's voice. Ends on *mir*. |
| `ethren_summon` | (his first battle call) | Sting ≤ 6 s (M4-A2P-091) | — |
| `lamp_archive` | B07, B08 (in) | Zone loop (exists, M3-AUD-842) | — |
| `silence` | B08 (end), B09, B11, B12 (start) | — | B11 has only the lamp being put out. |

**SFX:**
- `pole_no_wake` (a pole entering still water with no splash: a distinctive *absence*);
- `ledger_page` (heavy lacquered pages);
- `archive_key` (the bronze key);
- `basin_hum` (the bound light under the Sanctum's water, almost inaudible).

---

## 7. Camera shots by beat

New shot ids for `ch13/ansedra`, `ch13/sanctum` and `ch13/lamp_archive` (to add to ansedra.md).

| Id | Shot | Lens / note |
|---|---|---|
| A01 | Ansedra from the lagoon: domes doubled in the mirror | 24 mm, low over the water; **roughness 0** |
| A02 | The outer moorings; a poler's stroke leaving no wake | 50 mm |
| A03 | Kerrid stepping off and **standing** among the polers (ADR 0204: he never sits until Ch15); Asha looking back | 35 mm |
| A04 | Sefir at his door | 50 mm; **no idle motion** |
| A05 | Sefir's half-beat glance toward the outer moorings | 85 mm |
| A06 | Toma's bow; "Be level" / "And still" | 50 mm |
| A07 | Tobin jumping off the Hollowmere barge; lifting Liss | 35 mm |
| A08 | Merel's palm-to-palm with Liss | 85 mm insert |
| A09 | A causeway, gold lamp-posts, pilgrims, no birds | rail |
| A10 | Liss's palm flat on the lagoon | 85 mm insert |
| S01 | The basin: the mirror lit from beneath; pilgrims kneeling | 24 mm, high |
| S02 | **Liss at the rim looking down at the light**, held | 50 mm, then 85 mm; **hold past comfort** |
| S03 | Ysolde and Asha, hands | 85 mm |
| S04 | The gilt line painted | 100 mm (as act1_ch09 N06) |
| S05 | Ethren rising out of the mirror without a ripple | 35 mm, low over the basin |
| S06 | Ysolde before him, the ring | 85 mm, then insert on the ring |
| S07 | The binding: the light rising to the staff | 35 mm |
| S08 | The veiled head turning to Ysolde | 85 mm |
| S09 | Ysolde, eyes shut | 85 mm |
| R01 | The Archive: lacquer cases, red shelves, the lectern at the end | 24 mm |
| R02 | The document reader (UI) with a ledger spread | — (UI) |
| R03 | The Cantor roll in the reader; the hidden column | — (UI) |
| R04 | **Insert:** Corran's line and the margin | 100 mm, from the reader into the page |
| R05 | Ysolde to Asha: "When you sing, they spend him." | 85 mm singles |
| R06 | Ysolde's hands flat on the lectern; Liss beside her | 50 mm |
| R07 | The reader: pages side by side, signatures marked | — (UI) |
| R08 | **Pull-out:** eight pages in a row on the table, the same hand | 35 mm, from above, slow |
| R09 | The party round the table | 35 mm |
| A11 | The outer moorings at night; Kerrid standing as they come | 35 mm |
| A12 | Tobin arriving; "No." | 50 mm |
| A13 | Kerrid watching the still water | 85 mm |
| A14 | Wide: the party small on the moorings; the still city behind | 18 mm |
| R10 | **Sefir alone in the Archive:** squaring the pages, closing the ledger, putting out the lamp | 50 mm, then 35 mm; **no gloat** |
| A15 | Corran's house: the scorch mark; Ysolde laughing (side scene) | 50 mm, locked; insert on the mark |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | A01 → A02 → A03 | Nothing on the water moves in any shot. |
| B02 | A04 → A05 → A06 | A05 is half a beat. |
| B05 | S01 → S02 → S03 | S02 holds until it is uncomfortable. |
| B06 | S04 → S05 → S06 → S07 → S08 → S09 | The light rises off the mirror without a ripple. |
| B08 | R03 → R04 → R05 → R06 | R04 is the chapter's key insert. |
| B09 | R07 → R08 → R09 | R08 is slow: let the player read the hands. |
| B11 | R10 | One continuous shot if it can be. |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 | 15 |
| B02 | 120 |
| B03 (incl. optional) | 170 |
| B04 (barks, optional moorings) | 130 |
| B05 (incl. optional mark) | 50 |
| B06 | 10 |
| B07 (spoken; record texts separate) | 80 |
| B08 | 60 |
| B09 | 20 |
| B10 | 120 |
| B12 side scene | 170 |
| **Total** | **~945 spoken** (+ ~300 words of record texts in the reader; ~650 spoken on a path without the optional lines and side scene) |

**Against SPEC §3.6:** at ~37 min, Ch13 is about 2.2% of the game, so its fair share is **880–1,300 words**. It sits in the band, with the Archive's record texts on top. It's the act's most verbal chapter before Ch15, because it's the one where the truth is read, not shown.

---

## 9. Requests to other roles

### UI (M4-A2P-080): the chapter's mechanic
1. **The document reader:** open a record; lay two or three side by side; mark a matching hand or mark (the player's action, never auto); Ysolde's Lamptongue reading on request; no fail; found records go into the codex.
2. B09 needs **eight** pages in a row for its pull-out (R08). The reader can show three at once; the cutscene builds the eight on the table from the ones marked.
3. The verse-sleeve at **S6** after B06.

### Narrative (M4-A2P-004)
The **record texts**: three ledger records (day one), the Cantor roll with its hidden column and Corran's line and margin (day two), and eight signature pages across four centuries (day three). They're in Lamptongue with Ysolde's readings, about 300 words. **Rule 1:** the texts imply and never state.

### Rendering (M4-A2P-047)
1. **The still mirror** everywhere in Ansedra (A01, S01): roughness 0, exact reflections; poles entering without a ripple (A02).
2. **The Sanctum's under-light:** bound, steady, from beneath, the hall's only light (S01).
3. **Ethren rising out of the mirror without breaking it** (S05).

### Art (color script)
1. `ch13` exists. Confirm **the mirror** (a validated "enclosed or other light" case the color script lists as not yet validated) and the moorings at night (B10: oil lamps the only warm light).

### Environment Art (M4-A2P-043)
1. The kit exists (M3-ENV-721). Place:
   - the city, causeways and domes;
   - Sefir's house with its raked-gravel garden;
   - the guest moorings with the Hollowmere barge;
   - the outer moorings (lamps on poles, a mooring stone for Kerrid);
   - the Sanctum (vestibule with a kneeling rail and Wenna's mark behind it; the basin);
   - the Archive (bays, ladders, the lectern, the reading table);
   - Corran's house (red door, the scorch mark by the stove).
2. A swap map in ansedra.md first (M4-A2P-017 needs it).

### Character Art (M4-A2P-050, M4-A2P-052, M4-A2P-055)
1. **Tobin** (travelling clothes here; wedding dress in Ch14) and **Merel** (plain good clothes here).
2. **Sefir** at final quality for close framing (A04, R10).
3. Ansedran Tenders, pilgrims, polers and Stillguard (the Ansedran crowd set); the young householder.
4. Ysolde's laugh (a face row: she has none yet; the voice guide never samples one).

### Audio (M4-A2P-091)
`sanctum_of_the_level`, `ethren_bound`, `ethren_summon` (§6).

### Combat (M4-A2P-024)
Ethren's `vowbound.json` row (`bound_flag: ch13_ethren_bound`).

### Progression (M4-A2P-031)
The Ansedra purveyor's stock (Act II tier 2), priced against Ch12's lume (no fights here), and marked as an **Order shop** for the heresy.

### Systems / Chapters (M4-A2P-013)
1. **Speakers:** `tobin`, `merel`, `ansedra_tender`, `ansedra_pilgrim`, `ansedra_poler`, `householder`.
2. Kerrid's `party` steps: out at the outer moorings (B01), back on the wedding day (Ch14 B01, at the court's back among the polers).
3. The four-day structure: day changes at the house (rest), with the Archive open days 2–4.

### Cinematics (reviewer)
Check §0's rules against every shot, especially:
- the water (nothing moves);
- S02 (Liss, held);
- R08 (the hands, readable);
- R10 (Sefir tidying, not gloating);
- no line anywhere says "revenant".

---

## 10. Open questions for review

1. **The record texts' wording** (B07's three, B08's margin, B09's signatures) is M4-A2P-004's. This sheet fixes only what they must show. The Lead reviews them against ADR 0016 (b) for how much they say: the ledgers show binding, the roll shows *kept/spent*, the hands show continuity, and nothing names the Abiding.
2. ~~The Binding Ledger phrase~~: **resolved by ADR 0204 §15**: it stays, as a torn fragment (B07), and the Choir truth lands in Ch16.
3. **Sefir's "Be level, Okeru" / "And still" (A06)** makes Ch14's unanswered "Be level" land. Keep both or neither.
