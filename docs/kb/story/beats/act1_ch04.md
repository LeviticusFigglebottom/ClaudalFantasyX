# Ch4 Beat Sheet: "The Pilgrim's Wake" (M3)

Owner: Narrative (M3-C04-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch4](act_outline.md), [the slice sheet](vertical_slice.md) (the format, and B08–B12, which this chapter follows), [`ch03_dock_at_night.dlg`](../../../../game/data/dialogue/ch03/ch03_dock_at_night.dlg) (B11, reconciled in §0), [bible §4 the Pilgrim's Wake, §5.1 sea-law](../bible.md), [voice guide](../voice_guide.md), [Asha](../characters/asha_velamir.md), [Toma](../characters/toma_okeru.md), [Ysolde](../characters/ysolde.md), [ADR 0017](../../decisions/0017-act-one-restaging.md) (d) (the ferry is never attacked), [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (the lantern watch), [decisions_log N-01, N-03, N-04, N-14, N-17](../decisions_log.md), [color script `ch04`](../../art/color_script.md), [haluna.md](../../art/environments/haluna.md), [act1_ch01.md](act1_ch01.md) (the *Seventh Terrace*).

Scripts (to be written in M3-C04-02, under `game/data/dialogue/ch04/`): `ch04_lamps_to_the_wall`, the night barks, `ch04_the_wake` (feast tables), `ch04_shell_is_set`, `ch04_dock_in_the_dark`, `ch04_the_ink` (side scene), `ch04_long_way_round`, `ch04_gangplank`, the ferry banters, `ch04_seventh_terrace`, `ch04_name_board`, `ch04_under_way`.

Beat ids are chapter-local: **C4-01** to **C4-15**. Elsewhere, cite them as "Ch4 C4-06".

---

## 0. The chapter in one paragraph

Haluna holds a funeral for a girl who is still alive. Every lamp in the village is carried out to the wall at the causeway head, the eldest sets Asha's name-shell beside her mother's, the village says aloud what it will keep of her, and then it sings her the song you sing for a sailor's safe return. That is when Rhen understands, and he walks out of the feast. Asha leaves her own wake to sit with him on a dock lit only by the sea, and comforts *him*, and for one moment the player sees her smile drop and come back. In the night a tall stranger re-inks the shells by lamplight. At dawn the Cantor walks the causeway one last time, and the stranger is waiting at the ferry: Ysolde, appointed by the Order, cold and correct. Mid-strait they find a ship Rhen last saw tied up at Oruvel, drifting with her sails set and nobody at the helm. Sea-law says you bring a drowned hull's name home. Rhen goes aboard, Asha won't let him go alone, and they fight the thing in the rigging that has been keeping the dead ship sailing. Rhen, who has sold drowned brass his whole life, carries her name-board back for nothing.

**Emotional line:** a festival held for a death (dusk) → understanding, and anger (the shell) → being comforted by the person you were angry for (the dock) → a stranger's quiet care (the ink) → leaving home for good (dawn) → the open sea, and a cold new voice (the ferry) → his own loss, drifting (the derelict) → giving something up for nothing (the name-board).

**What Ch4 must prove:** the Pilgrim's Wake as our own rite (ADR 0017's Ch4 row); Asha's "smiles to protect" shown, not told; Ysolde's arrival and her magic; **the ferry is never attacked**; party swapping, Read and elements taught for the first time; the pilgrimage leaving Haluna (pillar 3).

### Reconciling with the slice's B11 (the dock at night)
`ch03_dock_at_night.dlg` has already played two nights earlier on the same dock. Ch4 must not repeat it.

| | B11 (Ch3, Day 1, 21:30) | Ch4 C4-06 (Day 2, 21:50) |
|---|---|---|
| What it is | A promise: Rhen asks to come; Asha says yes before Toma can object | A reckoning: Rhen is angry about what he promised to walk her toward; she comforts him |
| Light | Oil lamps in the village windows (H10), sea-glow 0.12 | **The village is dark**, because every lamp is at the wall; the dock is lit **only by the sea from below** (color script `ch04`) |
| Staging | Rhen standing; Asha at the dock end; Toma walks up the dock; H10 from the dock end toward the village | **Rhen sitting** on the edge, legs over the water; **Asha sits down beside him** (the Prologue's staging reversed: there he sits beside her); **Toma stops at the shore end** and sits there, guarding from a distance; a new low shot from the water side (H13) |
| Asha's tell | If `ch03_rhen_asked_after`, she asks about **his day** | She asks about **Oruvel**, his town, which is both her tell and the comfort |
| Lines | "Yes." / "Then you walk behind me." | No re-asking, no re-swearing; "Don't. Don't be kind about it." (voice guide) |
| What is said about the end | Nothing ("That's Ch4") | It has been said at the wake; on the dock nobody says it again |

Two more B11 lines are honoured, not repeated: **"At first tide. The causeway won't wait for me."** (C4-08 is that departure: the Cantor leaves by the causeway at the dawn low water, and the ferry waits at the islet's seaward landing) and **"Then you walk behind me."** (on the dawn causeway, Rhen walks behind Toma, without a word about it).

---

## 1. Running order

Time is in-world: Day 2 dusk to Day 3 morning (Ch1 is Day 0; Ch2–3 are Day 1). Minutes are the player's, at a first-time pace. **P** = playable, **C** = letterboxed cutscene, **E** = in-engine scene.

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| C4-01 | Lamps to the wall | `ch02/haluna` night variant | 19:40 | E | 1.0 | H02 (night), H12 | `haluna_night` | The village's light walks out of its houses. | `ch04_started` |
| C4-02 | **Haluna, wake night** | `ch02/haluna` night variant | 20:00 | P | 3.0 | H02, H04, H07, H09 (night) | `haluna_night` | An empty, dark village. Everyone is already at the wall. | — |
| C4-03 | **The wake feast** | `ch02/haluna` causeway head | 21:00 | P | 4.0 | H12, H08 | `haluna_wake` (diegetic) | Food and songs. People say goodbye to her face. | — |
| C4-04 | **Cutscene: the shell is set** | causeway head, the wake-shell wall | 21:30 | C | 3.5 | H08, H12, H16, H14 | `haluna_wake` → `the_long_way_round` (diegetic) | The village buries her alive, lovingly. He finally understands. | `ch04_shell_set` |
| C4-05 | Leaving the feast | causeway head | 21:45 | E | 0.5 | H12 | `the_long_way_round` (continues, behind) | He walks out. Asha stops Toma following. | — |
| C4-06 | **The dock in the dark** | `ch02/haluna` dock | 21:50 | E | 3.5 | H13, H14, H13 | `hearer_hum` (ambience) | He is comforted by the person he is grieving. Her smile drops once. | `ch04_rhen_named_kell` (choice), `ch04_dock_comforted` |
| C4-07 | *Side scene: "The Ink"* (optional) | the wake-shell wall | 23:30 | E | 3.0 | H15 | `ysolde_theme` (sketch) | A stranger making a name last. | `ch04_saw_ysolde_ink` |
| C4-08 | **Cutscene: the long way round** | causeway head → causeway | 05:30 | C | 3.0 | H08, C01 (dawn), C02 (dawn) | `haluna_dawn` (reprise) | Leaving home for good. Neme looks at her this time. | — |
| C4-09 | The gangplank | `ch04/brightwater_ferry` seaward landing | 06:00 | E | 1.5 | F01 | `ysolde_theme` | Ysolde: cold, correct, appointed. | `ch04_ysolde_joined` |
| C4-10 | **Brightwater Crossing** | `ch04/brightwater_ferry` deck | 06:15 | P | 4.0 | F02–F04 | `brightwater_crossing` | Open sea. A fourth voice. The pilgrimage is a journey now. | — |
| C4-11 | **Cutscene: the *Seventh Terrace*** | ferry deck | 07:30 | C | 2.0 | F05, D01 | `brightwater_crossing` → `silence` | A ship he knew, alive three days ago, sailing with no one aboard. | `ch04_boarded_derelict` |
| C4-12 | **The derelict's deck** | `ch04/brightwater_ferry` derelict | 07:40 | P | 5.0 | D02–D04 | `derelict` (ambience), `battle_standard` | A dead ship, its last meal on the table. | — |
| C4-13 | **Boss: the Spar-Wraith** (two phases) | derelict, the main deck under the mainmast | 08:10 | P | 6.0 | D05, D07 | `spar_wraith` (2 stems) | The thing that kept the dead ship sailing. | `ch04_spar_wraith_defeated` (battle result) |
| C4-14 | **Cutscene: the name-board** | derelict stern → ferry | 08:35 | C | 2.5 | D06, D08, F05 | `name_board_home` | He carries it for nothing. | `ch04_name_board_carried` |
| C4-15 | Under way again | ferry deck → Pemakar | 08:50 → 19:30 | E | 1.0 | F06 | `brightwater_crossing` (coda) | The board on the deck; Toma's ink kit; a fade. | — (chapter exit) |

**Totals:** critical path **40.5 min** (every beat but C4-07). With the side scene, **43.5 min**. Split: **22 min playable (54%)**, 11 min cutscene, 7.5 min in-engine. That's below the slice's 61% playable, which is right for the game's biggest rite chapter; the ferry and the derelict carry the play.

**Cut order if Ch4 runs long:** C4-02 shortens to a walk from Neme's door to the wall (two barks). C4-10's three banters go to two. C4-15 becomes the cut to Ch5 after a 2 s hold on the wrapped board. **Never cut** C4-04, C4-06, C4-08's causeway walk, the Spar-Wraith, or C4-14. **The zone cut** (act_outline's cut notes, first in line): if Brightwater Crossing is cut as a zone, C4-09 to C4-15 fold into one cutscene on the islet's landing, and the derelict fight moves to the islet's seaward rocks, where the dead ship has gone aground. The name-board beat survives the cut; the ferry deck's P time doesn't.

---

## 2. Beat detail

### C4-01. Lamps to the wall (E, 1 min)
Dusk, Day 2. In the Ch3 night variant the windows were lit. Now, house by house, people come out of their doors **carrying their lamps**, and the windows go dark behind them (a state change, one window at a time, on H02's lane at night). The lamps go to the wall at the causeway head, because at a Pilgrim's Wake the village brings its light to the Cantor. Rhen comes out of Neme's door carrying her table's other end, with Toma on the heavy end. Neme carries the food. There is far too much of it again (B02's tell, now with no one pretending).
- Two or three lines. Rhen: *"Where's everyone taking the lamps?"* Toma: *"To her."* (~20 words)
- The **first verse band** is on Asha's sleeve (`ch03_first_verse_sung`, sleeve state S1), so the wake shows it to the village for the first time.

### C4-02. Haluna, wake night (P, 3 min)
The town loop, **dark**: the lane, the market (shut, awnings rolled), the chapel court (the Reed's door open, the chapel lamp gone too), the dock (no lamps, the sea-glow on the water). Everyone the player met in Ch2 is already at the wall. The few people still in the lanes are on their way there. **Systems on show:** the save shrine (unchanged), the inn (closed tonight: a line on the door). No shop.
**Barks** (~80 words), each paying off a Ch2 or Ch3 line:
1. *Lane:* the **child** from Ch3's night bark ("Teach me tomorrow") teaches Rhen the end of the skipping rhyme, as promised: *"...three for the bell and four for the hush, and then you start again."* *"Start what again?"* *"The rhyme. Everybody knows that."* It's the same rhyme as Ch2's lane bark; tonight Rhen almost hears it.
2. *Dock:* the **netmender** who told Rhen "Bring her back the long way round" (Ch3's night bark), coiling a line in the dark, says she'll sing it with the rest at the wall. That's the song C4-04 ends on.
3. *Chapel court:* the **Reed**, carrying the chapel's lamp, has swept the steps for the wake and says so, proudly. (If the player stops: she says the Order's tutor came over at the evening ebb, and won't take a stool. That's Ysolde, unnamed.)

### C4-03. The wake feast (P, 4 min)
The causeway head (H12): trestle tables along the wake-shell wall, a hundred oil lamps on its top and in the saltgrass round it, leaf-wrapped food, brown sugar cake, smoked bonito, purple yam. The tide is in, so the causeway is under water, a dark line out to the islet. **The first full sea-glow of the game** is in the water beyond the lamps (color script `ch04`: sea-glow 0.12, lamp key 1.2, `lut_ch04_wake`). Villagers sing work songs and star-paths (folk songs; the Order hums, and nobody here is humming).
- **A walkable feast.** Asha moves table to table and the player follows, or wanders. At each table, people say things **to Asha, to her face**, that you say at a graveside: warm, specific, in the past tense more often than they mean to. She thanks each one. Rhen hears all of it. (~120 words across four tables, each optional except Neme's.)
  - *The market vendor* gives Asha the knot she taught him, tied, to keep. *"Your knots were always neater."*
  - *Osu* has washed every shell on the wall for tonight, Asha's mother's twice. If `ch02_heard_pila`, Osu tells Rhen quietly: *"You said hello to him. Teyo. She told me."*
  - *A fisher* says he'll name his next boat for her. His wife says he says that about everyone. It's the one laugh at the feast, and it's a true one (pillar 1: warmth between people, never against the sorrow).
  - *Neme* is clearing plates that are still full. She is **humming** while she works: the **Velamir lullaby**, the first verse's tune, the way the women of her line do (bible §6). If `ch03_rhen_named_lullaby`, Rhen **knows it**, and the camera holds on his face for a beat; he says nothing, and nobody explains it (a `@face` beat only, no line). Otherwise it's just a tune. **Watch (ADR 0022):** no line here, or anywhere in Act I, has anyone connect the tune to Dace or the lantern.
- **Ysolde is seen once**, at the edge of the lamplight beyond the last table: a tall figure in indigo-black, very straight, alone, not eating. A camera hold of 1.5 s on H12; nobody points her out. She has come to see a Cantor's wake, and she won't intrude on it.
- **Trigger:** when Asha reaches the wall, the eldest calls the village to the shell, and C4-04 starts.

### C4-04. Cutscene: the shell is set (C, 3.5 min)
- **H08 (night):** the wall, the clean gap at shoulder height that Ch2 showed (the Pila scene, N-03), and beside it, washed tonight, Imra's shell. Osu holds Asha's shell, new-cut and the whitest on the wall. The village stands with its lamps.
- **The setting.** Osu sets the shell in the gap with her thumbs, the way you'd close someone's eyes. The chapel's Reed recites one line of the Canticle (recited, never sung: bible §4). Osu says the four Velamir names on the wall, the oldest first, then **"Asha Velamir"**, with the others, in the same voice.
- **The speaking.** By custom each household says one thing it will keep of her. Most are short. **Neme can't.** She opens her mouth twice and nothing comes. Asha says it for her, smiling (voice guide: she finishes other people's comfort for them). Sample: *"She's going to keep my bad stool. The one that bites. Aren't you."* Neme laughs, and it breaks.
- **The song.** The village sings **"The Long Way Round"**, the Low Reaches farewell for a voyage: the one you sing so a sailor comes back the long way, safe. Unaccompanied, a hundred voices, plain words (diegetic; Narrative writes the lyric in the dialogue task; Audio writes an original tune). They sing it for her, and everyone singing knows she isn't coming back.
- **Rhen understands.** H16 (on Rhen, held): the song lands. He turns to Toma, low, and it is the voice guide's line: **"Everyone keeps saying she's going *on* a pilgrimage. Nobody says she's coming back from one."**
  - If `ch03_rhen_asked_after`: Toma: *"You asked me. On the steps."* Rhen: *"And you said ask her. I'm asking the whole village."* (the B08 payoff: he asked, and nobody answered)
  - Otherwise: Toma, after a pause: *"No. They do not."*
- **H14 (on Asha):** she has heard him. She keeps singing. Her face doesn't change.
- Sets `ch04_shell_set` (from here on the wall shows Asha's shell, in every later visit: Ch18, the Ending's Haluna).
- ~300 words, the chapter's longest scene. Words are spent here on purpose.

### C4-05. Leaving the feast (E, 0.5 min)
Rhen puts down the plate he's holding and walks out of the lamplight toward the dark village. Not storming: walking fast, the way he does everything when he's scared. Toma moves to follow. Asha, still in the song's last verse, touches his arm: *"Let me."* Toma: *"It is your wake."* Asha: *"Then I can leave it if I like."* She goes. Toma stays, then, after a beat, follows at a distance anyway. (~25 words)

### C4-06. The dock in the dark (E, 3.5 min)
The village is dark: every lamp is at the wall behind them, small and far. The dock is lit only by the sea-glow from below, cyan on the underside of everything (the color script's note: beautiful and wrong). Rhen sits at the dock's end with his legs over the water. Asha comes down the planks with **two pieces of brown sugar cake** on a leaf, and **sits down beside him**.
- **The beats:**
  1. Rhen, before she can speak: **"Don't. Don't be kind about it. Just let me be angry for a minute."** (voice guide)
  2. She doesn't speak. She sits. She holds out the cake and waits (a `@wait` of at least 5 s, no music). He takes it.
  3. He asks why nobody told him. She says that everyone did, in pieces, and that she let them. *"You looked at me on the beach like I was a person. I wanted two days of that."*
  4. **Her tell.** She doesn't talk about herself. She asks about **Oruvel**: what it sounded like in the morning. **Choice:**
     - **"Tell her about Oruvel."** Sets `ch04_rhen_named_kell`. He tells her about the raft-town and, before he means to, about Mother Kell. If `ch01_kell_side_scene`, he gives her Kell's line: *"She said the sea owed her a favour."* If `ch02_rhen_stayed_with_dead`, Asha already has the name: *"Mother Kell. You said it on the beach."*
     - **"Not tonight."** She lets him: *"Then another night. I'll still want to know."*
  5. **The smile (the required facial beat, H14).** Rhen looks out at the glowing water. While he isn't looking at her, **her smile goes** (`@face asha neutral`, held 0.8 s): it is the first time the player sees her face without it. Then he turns back, and it's there again before he sees (`@face asha soft_smile 0.3`). Rhen never sees it. **This is the outline's "first glimpse of her smiling to protect someone"**, and it is shown, never said. No VO.
  6. He says he's still coming. She says she knows: she said yes before Toma could stop her. She looks at the sea and says what she hears: **"I can hear them. It's like someone humming in the next room. All the time."** (voice guide). Rhen: *"Is Oruvel in there?"* She doesn't answer that, and asks him to eat his cake.
  7. Close: at the far end of the dock, Toma has **sat down** on the shore-end post, his back to them, guarding from where he can't hear. Asha: *"He'll sit there all night. He did it the night I was named."*
- Sets `ch04_dock_comforted`. ~260 words.
- **Watches:**
  - **No embrace and no kiss.** The love story stays nearly unspoken until Act III (Rhen's file). No hands are held. The cake is the only thing passed between them.
  - **Asha doesn't cry.** He's the one being comforted, and that's the inversion the outline asks for.
  - **The `ending_dock` axis is never used here.** No shot looks out to sea along the planks from behind her, and she never stands alone at the dock end. She sits; the camera is low on the water side, looking back toward the dark village (H13). The game's final image must be unspent.
  - **No line links the lantern, the comb or the lantern-man to Rhen or to Dace** (ADR 0022's sweep-G watch). Her comb is in her hair; nobody mentions it.

### C4-07. Side scene (optional): "The Ink" (E, 3 min) — see §4

### C4-08. Cutscene: the long way round (C, 3 min)
- **05:30, the dawn low water** (B11: "At first tide. The causeway won't wait for me."). The village is at the wall again, with its lamps guttering in the first light. **H08 (dawn grade):** Asha stops at the wall and touches her shell. **The ink on it, and on her mother's, is new and black and still glossy** (always: in the world, the re-inking happens whether or not the player watched it). She looks at her fingertip. She doesn't know who did it. If `ch04_saw_ysolde_ink`, Rhen does, and a look (no line) is enough.
- **Neme.** In Ch2 she never once looked at Asha's packed bag (B02). Now she looks at Asha the whole time, and doesn't look away when Asha turns. She says one thing. Sample: *"Eat when they feed you."* That's all she can manage.
- **The causeway (C01, C02 at dawn).** By custom, nobody walks past the wall with the Cantor but her guardians. Toma leads, Asha walks in the middle, and **Rhen walks behind**, as Toma told him to in B11. The path is the one the player walked in Ch3 at noon, now in the dawn grade, under a low gold sun, the islet small ahead. The shot holds long on C01 as the three get small (pillar 3: the line leading away). Nobody looks back except Rhen, once.
- `haluna_dawn` reprises (the piano and metallophone that opened Ch2). ~70 words.
- **Watch:** this is not a dock farewell. The village doesn't wave a boat away; she walks out of it on her own feet, along the path every Cantor of her line has walked.

### C4-09. The gangplank (E, 1.5 min)
The islet's **seaward landing** (the far side from the shrine door): stone steps down to deep water, where the reef drops off. The ferry can't cross Haluna's flats, so it calls here, the only deep water near the village. The Brightwater ferry, the *Kind Weather*, has lain here overnight, hired by the Order for the Cantor's crossing.
- **Ysolde is already standing at the foot of the gangplank**, alone, with a folded appointment under her hand, having walked the causeway ahead of them in the dark so as not to walk in the Cantor's procession uninvited. She presents herself to Asha formally: *"Lady Cantor. Ysolde Ysel. The Conclave has appointed me to teach you Lamptongue on the road."* Toma gives the greeting: *"Be level."* Ysolde: *"And still."* She explains, briefly and without warmth, why she didn't present herself at the wake: a wake belongs to the village.
- **Rhen.** Asha introduces him as her guardian. Rhen makes a joke (his voice: jokes harder when he's unsettled). Ysolde, the voice guide's line: **"You are very funny, Master Sallow. I have decided not to notice."**
  - If `ch04_saw_ysolde_ink`: Rhen, quietly, as she turns: *"You did the shells."* Ysolde: *"I am the Lady Cantor's tutor in Lamptongue."* She goes up the gangplank. That's all the scene gives it.
- Sets `ch04_ysolde_joined` (party: Rhen, Asha, Toma, Ysolde). ~110 words.

### C4-10. Brightwater Crossing (P, 4 min)
The ferry deck at sea, under way at dawn: a two-masted Low Reaches coastal ferry, a deckhouse with a small Order shrine (the **save point**), a passengers' awning, cargo lashed amidships, the ferry's skiff on its davits. Passengers bound for Pemakar's Lanternfall (Ch5): a family with a child who wants to see the Cantor and is too shy; two terrace traders; a Reed going home.
- **Systems on show:** the ferry's purser sells supplies (a shop); **the party formation menu** with four members for the first time (three active, one reserve). Ysolde's Lattice start. **No battles**: the ferry is never attacked (ADR 0017).
- **Three banters** (field barks, triggered by walking past; ~150 words):
  1. *Ysolde and Asha, at the rail:* Asha practises the first verse's opening under her breath, and Ysolde corrects her, the voice guide's line: **"It is pronounced *ennu*. Two syllables. You will want to sing it correctly when it matters."** Asha thanks her and does it again, correctly. Ysolde doesn't look surprised. (Asha's arc with Ysolde starts here: she refuses to be afraid of her.)
  2. *Toma and Ysolde:* two believers, formal and easy with each other in the Order's words. Toma asks, with real reverence, whether she has walked a pilgrimage before. *"Once."* She doesn't say whose. (Her husband Corran, the 60th Cantor; that's Ch13's.)
  3. *Rhen and the ferry-master, **Imbe**:* the ferry-master asks where he's from. *"The raft-town."* A pause. *"Salt and stone. I'm sorry, lad."* He's the first stranger to name the loss out loud.

### C4-11. Cutscene: the *Seventh Terrace* (C, 2 min)
- **07:30, mid-strait.** A lookout's call. **F05:** a ship off the bow, under full sail, red-and-black lacquer, copper sheathing, running before the wind with **nobody at the helm**: the wheel turning by itself. Held motes (`glimmer_held`, faint in daylight) hang in her rigging like spray that won't fall.
- **Rhen knows her.** *"That's the* Seventh Terrace. *She was tied up at Oruvel three days ago. Her skipper paid me short."* (act1_ch01.md C1-09: Sadi Moru's coaster at the outer mooring, which ran for open water when the gulls cried, C1-12.) It's the first proof, since the beach, that Oruvel was real and that it's gone.
- **Sea-law (bible §5.1).** Imbe: no hull drowned in a Rising is passed without someone bringing its name-board home. He'll lie alongside her, an oar's length off, with fenders and boathooks, because you **never lash a living hull to a drowned one**. **He won't send his crew aboard.** It's not cowardice; they're ferrymen with families, and the rigging is moving wrong.
- Rhen: he's a diver; he's been on more drowned hulls than anyone aboard. He goes. **Asha won't let him go alone:** *"You're my guardian. Guardians walk behind. So I'll go first."* Toma goes because she goes. Ysolde goes because someone should say the Canticle over a drowned hull correctly, and she is the only one aboard who may.
- **D01:** Rhen jumping the gap to her chain-plates. Sets `ch04_boarded_derelict`. ~120 words.

### C4-12. The derelict's deck (P, 5 min)
A dead ship, three days drowned, sailing. The main deck, the galley (**four bowls on the table, the meal half-eaten**: the crew were at their food when the gulls cried), the hold (Pemakar copper ingots, the salvage Rhen sold her skipper, a lamp-housing he recognises), the stern with the **name-board**, and above everything the rigging, where the held motes are. No bodies anywhere. The sea took them.
- **Encounter 1, scripted: `sail_leech` ×2**, dropping from the yards onto the party: an **ambush opening** (the foes act first). They're fragile once they've struck. No prompt; the opening banner says it (ADR 0023's openings).
- **Encounter 2, scripted: `bottle_hermit` ×1**, a hermit crab living in the ship's big lamp glass, which turns magic aside. The party starts **Rhen, Asha, Toma active, Ysolde in reserve** (she is not a front-line fighter, and it's her first fight with them).
  - **Teaches: swapping** (first prompt: *"Ysolde is in reserve. Swap her in on anyone's turn. It costs no time."*), then **Read** (second prompt, on her first turn: *"Read it to learn what the glass turns aside."*), then **elements**: the glass reflects fire and is cracked by ice, so the player picks the element from what Read showed. Two prompts in this fight, in sequence; no prompt in the leech fight.
  - This is the first fight with four party members, and the first that has a reserve at all (in the slice, the Drownbell party is three with no reserve). Ch2–3 never teach swapping, so nothing is duplicated.
- **Random encounters** on the derelict: `sail_leech` and `bottle_hermit` (§9 Creatures).
- **Barks** (~60 words): Toma at the galley table, quietly: he stacks the bowls, as you would in a house where someone has died. Ysolde notes the time on the galley's hourglass (she reads everything). Rhen in the hold: he finds the housing he sold the skipper and puts it back where it was.

### C4-13. Boss: the Spar-Wraith (P, 6 min) — see §5

### C4-14. Cutscene: the name-board (C, 2.5 min)
- **D06:** the stern. Rhen takes the **name-board** off with his reef-hooks: carved, lacquered, *Seventh Terrace* in Pemakar terrace script (the same hero prop as Ch1's O07 insert). He has taken a thousand things off drowned hulls, and he has never done one this carefully. He doesn't let it split.
- **The Canticle.** Ysolde recites over the hull: two or three short lines of the *Canticle of Level Water*, recited, never sung (bible §4). The held motes in the rigging **drift down and seaward**, off the yards and into the sea, as the Order's words send them. **D08:** Asha watches them go a beat too long, and says nothing. *(A seed, for Ch9's Ebbing and Ch10's farewell-tide: the player has seen held light sink three chapters running and may start to wonder. Nobody says it's wrong.)*
- **The sails come down.** With the Spar-Wraith dead, nothing holds the dead ship's lines: the sails luff and fall, and the *Seventh Terrace* stops sailing. She's only a hull now.
- **Back aboard the ferry (F05).** Imbe says the harbour pays a boarder for bringing a board home, by custom. Rhen: *"Tell them it's paid."* Imbe: *"Never heard a diver say that."* Older-Rhen VO, once: *"I'd sold drowned brass my whole life. That was the first thing I ever brought up for nothing."* (the outline's beat, said plainly) Sets `ch04_name_board_carried` (key item `name_board_seventh_terrace`).
- ~140 words.
- **Watch:** the ferry was never attacked, and nothing from the derelict comes aboard the ferry. The party chose to board the dead.

### C4-15. Under way again (E, 1 min)
The board lies on the ferry's deck, wrapped in sailcloth, and the passengers' child, too shy to speak to the Cantor, puts her leaf-boat on top of it. Toma unrolls Haluna's ink kit and sits beside Asha; she holds out her **left forearm**. **Fade before the needle.** (N-01: her first reach-band is earned on the Ch4 crossing and inked by Toma offscreen; Ch5 shows it, and her line there is "My first. Toma's hand shook.") Dusk title: Pemakar's terraces, a thousand small fires on the mountain. The chapter exits to `ch05/pemakar`.

---

## 3. Flags

All are to be declared in `game/data/flags.tres` (M3-C04-02). Read and write them only through `Game.get_flag` / `Game.set_flag`.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch04_started` | C4-01 | chapter flow, NPC state (wake-night variant) | — |
| `ch04_shell_set` | C4-04 | zone dressing (the wall shows Asha's shell from here on) | Ch18 Haluna revisit; the Ending's Haluna |
| `ch04_dock_comforted` | C4-06 | gating C4-07 and C4-08; Memories gallery | — |
| `ch04_rhen_named_kell` | C4-06 choice | Ch7 | **Ch7** (proposal for M3-C07-01): when Tavi finds Rhen, Asha already knows Kell's name and can use it when she blesses Oruvel's moorings; otherwise she learns it from Tavi there. |
| `ch04_saw_ysolde_ink` | C4-07 | C4-08 (Rhen's look), C4-09 (his line) | **Ch13** (proposal): Ysolde's side scene in the house she shared with Corran; Rhen can say "You'd done one before. The ink." Ch18 revisit: the ink is still black. |
| `ch04_ysolde_joined` | C4-09 | party roster, Lattice | — |
| `ch04_boarded_derelict` | C4-11 | zone state | — |
| `ch04_spar_wraith_defeated` | C4-13 battle result | C4-14 trigger | bestiary |
| `ch04_name_board_carried` | C4-14 | inventory (`name_board_seventh_terrace`, a key item that can't be sold or dropped); Ch5 | **Ch5** (proposal for M3-C05-01): the board goes home to Pemakar's harbour and is hung with its wake-shells. |

**Reads from earlier chapters:**

| Flag | Where | Effect |
|---|---|---|
| `ch02_heard_pila` | C4-03 (Osu's table) | Osu thanks Rhen for "saying hello" to Teyo. |
| `ch02_rhen_stayed_with_dead` | C4-06 | Asha already knows Kell's name. |
| `ch03_rhen_asked_after` | C4-04 | Toma: "You asked me. On the steps." (the B08 payoff the slice promised) |
| `ch03_rhen_named_lullaby` | C4-03 (Neme's humming) | Rhen's held recognition, face only. |
| `ch03_first_verse_sung` | C4-01 on | Sleeve state S1 shown at the wake. |
| `ch03_rhen_sworn_guardian` | C4-01 | Gating: Ch4 doesn't start without it. |
| `ch01_kell_side_scene` | C4-06 | Rhen gives Asha Kell's "favour" line. |

`ch01_*` flags are false in a slice-start game, and every line that reads one has a plain fallback.

---

## 4. The optional side scene: "The Ink" (C4-07)

**Where:** the wake-shell wall at the causeway head (H15), after the feast. The lamps have burned low, the tables are bare, and the village has gone home. **When:** after C4-06, on the walk back from the dock, through a marker on the wall (Ysolde, kneeling, is visible from the causeway-head path). If the player goes to Neme's door instead, the night ends and the scene is gone. **Length:** 3 min, ~130 words. **Speakers:** `ysolde` (exists).

**Beats:**
1. Ysolde kneels at the wall with a small oil lamp, a lacquer ink-stone and a fine brush, her **ink-guards** on her left hand. She is re-inking Asha's shell. She doesn't look up. *"Hold the lamp, if you are going to stand there."* (Her warmth comes out as an instruction: voice guide.) He holds it.
2. Rhen asks what's wrong with the ink. She tells him, exactly: the village cut the name well, and inked it with fishing-ink, soot and oil, which salt lifts in a season. Ansedran lacquer ink outlasts the stone it's in. One line of fact, not a lecture.
3. He jokes (his voice). She doesn't react. He stops joking.
4. **The true beat.** She finishes Asha's shell, and then, without a word, moves the lamp and **re-inks the shell beside it**: Imra's, its name faded to a ghost. Rhen: *"That's her mother's."* Ysolde: *"Yes."* She doesn't stop.
5. He asks whether she's done this before. *"Once."* (A widow's answer, which the player can't read yet: Corran's shell, at Ansedra, twenty-four years ago. Ch13 pays it.)
6. She caps the ink and stands. She doesn't give her name. *"Go to sleep. The tide will not wait for anyone tomorrow."* She goes.

**Rules:** no more than four lines from Ysolde in a row; her lines are complete sentences with no contractions, and she explains nothing about herself. She is cold because warmth would make it unbearable (ysolde.md). Nothing in the scene says she is the tutor; C4-09 does.
**In the world, this always happens.** The re-inking is real on every path (C4-08 shows the new ink), and the side scene is the player witnessing it. Sets `ch04_saw_ysolde_ink`.
**Payoff:** C4-09's line; a look in C4-08; Ch13's house scene (proposal).

---

## 5. The Spar-Wraith (C4-13): placement, phases, and what it teaches

**Placement:** the derelict's main deck under the mainmast, after the two scripted fights, at about 08:10 with a low sun through the set sails. It is the chapter's only boss, and it is fought on the **derelict's** deck, never the ferry's (ADR 0017 (d)). The party is four: three active, one reserve.
**Lore:** an Undertow-spawn born of the Rising that drowned the ship's crew, tangled in her rigging. It grew its own sail-membranes along her shrouds and has been **hauling her lines** ever since, which is why a ship with no one aboard is still sailing. It clings to the held dead in the rigging, and they to it.

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: Shrouded** | The wraith hangs in the rigging above the deck, wrapped in its own sail-membrane (D05). | The **shroud** turns physical blows aside, and its weak point is **Fire**, which Read shows. Burning the shroud brings it down onto the yards. | Read before you act; Ysolde is the answer to a magical foe (SPEC §6.1). Swap her in, as the bottle-hermit taught. | The thing in the sails is what keeps her sailing. |
| **2: Hauled Down** | The shroud burns away and it drops to the deck, dragging the sea up its lines: it is sheathed in water now. | **Its weak point has changed** to **Ice** (Read again). It **hauls** a party member's line, pushing that character back on the timeline. Ysolde's `slow_hex` slows it; Rhen's `kick_off` pushes it back. | **Weaknesses change, so read again**, and the timeline tools learned in Ch1 (delay) and Ch3 (telegraphs) work with a full party. | The dead ship's last fight is for its lines. When it dies, the sails come down (C4-14). |

**Tutorial text** (UI, loc keys owned by UI/Combat), one prompt per phase, no more:
- Phase 1: *"Blows slide off the shroud. Read it, and answer with the right element."*
- Phase 2: *"Its weakness has changed. Read it again."*

**Teaches, and doesn't:** it teaches reading and changing elemental weak points (the creatures track's design), with swapping as the means. It doesn't re-teach the timeline (Ch1), telegraphs or part-breaking (Ch3), or the Vowbound (Ilun can be called, but no prompt asks for him).
**Introducing Ysolde's magic:** her **Ember** burns the shroud in phase 1 and her **Frost** answers phase 2. Her first cast in the fight plays her **folding lacquer book** opening into its fan-arc (character-art cast animation; a full battle intro, once).
**Battle barks** (≤ 35 words): Ysolde, on her first cast, correcting nobody, *"Stand back from the rigging, please."* Toma: *"On my shield."* Asha says nothing aloud to the wraith.
**Light:** the wraith's wounds are `spawn_wound`, and its motes are **held**. When it dies, its motes and the rigging's slide into the sea. Nothing lifts.
**Combat bands** (balance_targets.md, Ch4–Ch9 boss): naive ≤ 5%, role_answer 65–85%, smart 75–92%, p90 ≤ 70.

---

## 6. Music cues

| Cue id | Beats | Kind | Brief | M3 final? |
|---|---|---|---|---|
| `haluna_night` | C4-01, C4-02 | Night bed | Exists (the slice's sketch): `haluna_village` stripped to flute and drone. | sketch (slice) |
| `haluna_wake` | C4-03, C4-04 | **Diegetic** feast music | Village instruments at the wall: hand drum, a reed flute, voices singing work songs and star-paths. The melody of `haluna_village` turns up in it once, played slower, as if the village were remembering its own festival. | sketch |
| `the_long_way_round` | C4-04, C4-05 | **Diegetic** song | The Low Reaches farewell song for a voyage, sung unaccompanied by the whole village. **An original folk tune** (SPEC §2), plain and singable, in a major mode that makes it worse. Until SPEC §16 Q4/Q5 settle voices, a small ensemble of solo instruments carries it. Narrative writes the lyric in the dialogue task. | **final** |
| `hearer_hum` | C4-06 | Ambience | Near silence: the sea, the far wake behind, and under it, very low, a held tone like "someone humming in the next room" (Asha's own words). Audible only in this scene and when Asha speaks of the dead later. | sketch |
| `ysolde_theme` | C4-07, C4-09 | Character theme, sketch | A cold, plucked zither-like line over a low reed drone; exact, unhurried, very little vibrato. Ansedran lacquer and gold, not the Low Reaches. | sketch |
| `haluna_dawn` | C4-08 | Reprise | The cue that opened Ch2's beach. Haluna said hello with it and says goodbye with it. | (exists, sketch) |
| `brightwater_crossing` | C4-10, C4-11, C4-15 | Field bed | Open sea: wide strings, sail-creak, a long melody that moves forward. The first music in the game that sounds like a journey. | **final** |
| `derelict` | C4-12 | Ambience | Wind in the shrouds, luffing canvas, lines creaking under no hand, a block knocking. No melody. | sketch |
| `spar_wraith` | C4-13 | Boss, two stems | Stem 1: block-and-tackle percussion, taut-line strings. Stem 2: adds a low water swell and lashing figures. | sketch |
| `name_board_home` | C4-14 | Cutscene score | Piano and metallophone; the star-path phrase Asha hummed on Ch2's beach, once, slowly (the homecoming lullaby, now for a ship that does go home). | sketch |

**SFX cues** (requested): `wake_lamps_out` (window lamps lifted off their hooks, one by one), `shell_set` (the shell pressed into mortar), `ink_brush`, `gangplank`, `lookout_call`, `derelict_wheel_turning`, `sails_luff_and_fall`, `name_board_prise`.

**Recommendation to Audio:** Ch4's M3 finals are **`the_long_way_round`** and **`brightwater_crossing`**: the rite and the road.

---

## 7. Camera shots by beat

Haluna's night shots extend haluna.md §5.1 (H12–H16 are new; H11 is already requested by the slice for B11). **F** for the ferry and **D** for the derelict are new, to be defined in a `brightwater_ferry.md` sheet (§9).

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| C4-01 | H02 (night), H12 | H02 at night: the windows going dark one at a time as the lamps leave. **H12** (24 mm, 2.5 m): the causeway head and the wall wide, lamps along its top and in the grass, the dark causeway leading out, the sea-glow beyond. |
| C4-02 | H02, H04, H07, H09 (night) | Rail cameras, night grade, no window lamps. |
| C4-03 | H12, H08 | Ysolde's 1.5 s hold is on H12, at the far edge of the lamplight. |
| C4-04 | H08 → H12 → H16 → H14 | **H08 at night** for the setting (Osu's thumbs on the shell, as H08 was framed for her hand in Ch2). **H16** (85 mm, on Rhen) holds through his line. **H14** (85 mm, on Asha) for her not reacting. Cuts. |
| C4-05 | H12 | One take: Rhen walking out of the lamplight, Asha's hand on Toma's arm. |
| C4-06 | H13 → H14 → H13 | **H13** (35 mm, 0.4 m above the water, from the water side of the dock, looking up and back toward the dark village): the two sitting on the dock edge, lit from below by the sea, the lamps at the wall small and far. **H14** (85 mm, Asha single) carries the facial beat: hold through the smile going and coming back. **Never the `ending_dock` axis.** |
| C4-07 | H15 | 85 mm, 1.0 m, shallow depth of field: Ysolde's ink-guarded hand and brush on the shell, the oil lamp's pool, Rhen's hand holding it in the edge of frame. Inserts on the two shells. |
| C4-08 | H08 (dawn) → C01 (dawn) → C02 (dawn) | Haluna's shots under the `ch02` dawn grade. Hold C01 long as the three get small on the path. |
| C4-09 | F01 | The seaward landing: stone steps down to deep water, the ferry, Ysolde at the gangplank's foot. |
| C4-10 | F02–F04 | Rail cameras on the ferry deck. |
| C4-11 | F05 → D01 | **F05** (50 mm, from the ferry's rail): the *Seventh Terrace* under full sail, nobody at the wheel, held motes in her rigging. **D01**: Rhen jumping the gap to her chain-plates. |
| C4-12 | D02–D04 | Rail cameras on the derelict: the main deck, the galley's four bowls, the hold. |
| C4-13 | D05, D07 | **D05**: the wraith in the rigging, tilted up through the sails against the low sun. **D07**: phase 2 on deck. |
| C4-14 | D06 → D08 → F05 | **D06**: the name-board at the stern under Rhen's hooks (**must match Ch1's O07 insert exactly**). **D08**: Asha watching the motes go down into the sea. Back to F05 for the ferry. |
| C4-15 | F06 | The wrapped board on the deck, Toma and Asha beside it; fade before the needle. |

**Requested coverage:** H12–H16 in haluna.md; F01–F06 and D01–D08 in a new sheet.

---

## 8. Word counts

Estimates, before any `.dlg` exists. `tools/dialogue_stats.py` replaces them in M3-C04-02.

| Beat | Words (written) | Notes |
|---|---|---|
| C4-01 lamps | 20 | |
| C4-02 barks | 80 | three barks |
| C4-03 feast | 120 | four tables, all branches |
| C4-04 shell set | 300 | not counting the song's lyric (~60, to be written) |
| C4-05 leaving | 25 | |
| C4-06 dock | 260 | both branches |
| C4-07 the ink | 130 | optional |
| C4-08 dawn | 70 | |
| C4-09 gangplank | 110 | |
| C4-10 banters | 150 | three |
| C4-11 sighting | 120 | |
| C4-12 barks | 60 | |
| C4-13 battle barks | 35 | |
| C4-14 name-board | 140 | |
| C4-15 | 0 | |
| **Total** | **~1,620** (+ ~60 of lyric) | **~1,300 on a typical path without the side scene** |

**Per speaker (estimate):** Asha ~27%, Rhen ~24%, Toma ~11%, Ysolde ~13%, the village (Osu, Neme, vendor, fisher, child, netmender, Reed) ~18%, Imbe ~7%.

**Against SPEC §3.6** (40–60k words, ceiling 80k): at ~41 min of a 30 h main story, Ch4 is **2.3%** of the game, so its fair share is **~910–1,370 words**. At ~1,620 written (~1,300 on a typical path) it runs about 18% over the top of its share. That's deliberate: the wake is the game's first full rite, and Ch4 introduces a principal (Ysolde). It's paid for by Ch1 (~780, at the bottom of its share), so **Ch1 and Ch4 together are ~2,400 words against a combined share of ~1,690–2,540**, inside the band.
- **Rule:** C4-04 and C4-06 keep their budgets; if Ch4 must lose words, they come out of C4-10's banters and C4-03's tables first. No line over 25 words.

---

## 9. Requests to other roles

Each item is written to be filed as its own task.

### Environment Art (kits per zone)
1. **`ch02/haluna`, wake-night dressing** (on M2-ENV-02's night lighting):
   - a window-lamp state with every window **unlit**, plus per-window toggles for C4-01;
   - the causeway head as a feast: trestle tables, leaf-wrapped food, sugar cake, **~100 oil lamps** on the wall top and in the saltgrass (a lamp-scatter tool, oil_lamp lights culled to the nearest ~12);
   - **Asha's shell set in the gap** (state `ch04_shell_set`), the cleanest and whitest on the wall, and Imra's beside it, with an ink state (faded / re-inked, the latter glossy);
   - Ysolde's ink kit (lacquer ink-stone, brush, small oil lamp);
   - the dock with no lamps (the sea-glow is its only light);
   - the dawn variant of the wall with guttering lamps.
2. **`ch04/brightwater_ferry`** (new zone; the outline's bracket):
   - the **islet's seaward landing** (stone steps to deep water on the far side of the Shell Shrine islet, the ferry's berth), the zone's entry;
   - the **ferry *Kind Weather***: two-masted Low Reaches coastal ferry, deckhouse with a small Order shrine (the save point), passenger awning, lashed cargo, the skiff on davits, a lookout's perch;
   - **the derelict alongside** (ADR 0017's consequence): the ***Seventh Terrace*** from Ch1 (act1_ch01.md §9: build the ship once), with a boardable deck, the galley (four bowls), the hold (copper ingots, a lamp-housing prop), the stern **name-board** (the Ch1 hero prop), **sails set** (wind-filled, slightly torn) with a **lowered** state for C4-14, rigging dressed with spawn membrane, fenders and boathooks between the hulls (never a lashing);
   - the open strait (no land but a far island line).
3. **A `brightwater_ferry.md` environment sheet** with shots F01–F06 and D01–D08 (§7), and **haluna.md §5.1 additions** H12–H16.

### Art and Rendering
1. **Color script:** add a **`ch04_derelict`** sub-frame (about 07:30–08:40, sun ~15°, warm low light through the set sails, open-sea water look, held motes faint in daylight, ≤ 5% of the frame), and confirm the dawn causeway (C4-08) under the existing `ch02` dawn grade.
2. **`lut_ch04_wake`** (already missing, per M2-ENV-02's handoff) is needed for C4-03 to C4-07.
3. **The dock lit from below** (C4-06): the sea-glow as the key on faces, with the wall's lamps as a distant rim. Check that faces read at sea-glow 0.12, or allow a local glow boost on the dock's water.
4. **Glimmer:** held motes in the derelict's rigging (daylight), and their seaward slide in C4-14. Nothing lifts in Ch4.
5. **Character art:** Asha's sleeve state **S1** at the wake (first band); Ysolde's cast animation (the folding book opening into its fan-arc); her ink-guards in close-up (H15).

### Creatures and enemies (Character Art and Combat; silhouettes)
The creatures track's ids, used as proposed:

| Id | Kind | Silhouette | Role and answer | Notes |
|---|---|---|---|---|
| `sail_leech` | regular | A long flat leech, dark and wet, hanging from the yards like a strip of wet canvas until it drops | **ambusher**: acts first (an ambush opening), then fragile; **Rhen** (precise, fast) | Scripted encounter 1 (C4-12), and random. |
| `bottle_hermit` | regular | A hermit crab living in the derelict's big ship's **lamp glass** (an oil-lamp chimney of thick glass, never a bound housing), legs out of the neck, the glass catching the light | **reflects or blocks magic** by element: the glass reflects fire and is cracked by ice; **Ysolde**, with Read | Scripted encounter 2: swap, Read and elements are taught on it. |
| `spar_wraith` | boss, Undertow-spawn, two phases | Phase 1: a gaunt, many-armed spawn spread through the rigging, its own sail-membranes wrapped round it like a shroud, wounds bleeding held cyan. Phase 2: shroud gone, dropped to the deck, sheathed in sea-water hauled up its lines | §5: **elemental weak points that change** (Fire, then Ice) | Lore in §5. |

**Answers to the creatures track's questions (2026-10-24):**
1. **Foes on screen per encounter:**

   | Zone | Encounter | Combatants | Bodies on screen |
   |---|---|---|---|
   | `ch02/haluna` (wake night) | none | — | No battles in Haluna in Ch4. |
   | `ch04/brightwater_ferry` ferry deck | none | — | **The ferry is never attacked** (ADR 0017): no encounter, random or scripted, on the ferry. |
   | `ch04/brightwater_ferry` derelict | scripted 1 (C4-12) | 2 `sail_leech` | 2 |
   | `ch04/brightwater_ferry` derelict | scripted 2 (C4-12) | 1 `bottle_hermit` | 1 |
   | `ch04/brightwater_ferry` derelict | random | 1–3: `sail_leech` ×1–3, or `bottle_hermit` ×1 with `sail_leech` ×0–2 | at most 3 |
   | `ch04/brightwater_ferry` derelict | boss (C4-13) | 1 `spar_wraith` | 1, in the rigging (phase 1), then on deck (phase 2) |
2. *(Hullgnaw's raft is answered in act1_ch01.md §9.)* For the **Spar-Wraith**, the rigging and sails are the **arena** (environment: the derelict's mast, yards and sails, with their lowered state for C4-14), and the **shroud** and the hauled water are the **boss** (part of `spar_wraith`'s two phase models).
3. **Keep, cut or rename:** **keep all three** as proposed. One constraint: the bottle-hermit's glass must read as an **oil-lamp glass**, plain and empty, never a Lit Age bound housing, so no bound light (teal, still) appears in Ch4 (the slice keeps that sight for the Ch3 ring and shrine). No renames.

### Combat
1. **The first four-member party** (Rhen, Asha, Toma, Ysolde): the `bottle_hermit` encounter starts with Ysolde in **reserve**, and carries the swap and Read prompts (C4-12).
2. **`sail_leech`'s ambush** uses ADR 0023's opening (the foes act first).
3. **The Spar-Wraith** per §5: phase-1 shroud (physical resistance, Fire weak point), phase-2 water sheath (Ice weak point), and the **haul** (pushes a party member back on the timeline).
4. **Bands:** derelict regulars on the Ch4–Ch9 regular band (naive 20–60%, role_answer ≥ 92%, smart ≥ 97%, p90 ≤ 35); the Spar-Wraith on the Ch4–Ch9 boss band (naive ≤ 5%, role_answer 65–85%, smart 75–92%, p90 ≤ 70). A loadout **`ch04_spar_wraith`**: the Haluna shops' tier-1 gear plus the ferry purser's stock, Ysolde's starting gear, and `ch03_ilun_bound`.

### Design
1. **The walkable wake** (C4-03): table-to-table optional talk, with C4-04 triggered at the wall. No shop.
2. **The party formation menu**, first shown on the ferry (C4-10), and **Ysolde's Lattice start**.
3. **The ferry purser's shop:** Pemakar-bound stock (an ember edge for Ysolde, eyewash for the slug if it returns).
4. **Tutorial order across Act I** (the Ch1 sheet's §9 Design item 3): Ch4 teaches **swapping, Read, elements and a changing weak point**. Nothing else.

### UI
- Prompts: swap, Read, the element answer, and the two Spar-Wraith lines (§5).
- The **party-join card** for Ysolde (as each later principal will have one).
- The key item `name_board_seventh_terrace` (can't be sold or dropped).
- The first **bestiary** entries from Read.

### Audio
The cue list in §6, especially **`the_long_way_round`** (diegetic, original, sung by a village) and **`brightwater_crossing`**. The SFX list in §6.

### Systems / flow (M3-ARC-01)
- **Chapter entry:** after B11 (`ch03_rhen_sworn_guardian`) and B12, which plays in the full game as **Ch3's chapter close** (the end card's VO line, "I didn't know yet what I was walking her toward", leads straight into the wake; for the M2 build it stays the slice's end card).
- The Haluna wake-night NPC state (`ch04_started`): barks, closed inn, dark windows.
- C4-08 ends at the islet's seaward landing (`ch04/brightwater_ferry`, spawn `Landing`); C4-15 exits to `ch05/pemakar`.
- New speakers: `ferrymaster` (Imbe, `CHAR_FERRYMASTER`), `passenger` (`CHAR_PASSENGER`); `ysolde`, `neme`, `osu`, `reed`, `vendor`, `fisher`, `netmender` and `child` exist.

### Cinematics (reviewer)
Check the C4-06 facial beat on H14 (the smile going and coming back while he isn't looking), the H13 axis against `ending_dock`, C4-04's song and Rhen's held reaction on H16, the long C01 hold at dawn, and the D06/O07 match.

### Narrative (later sheets)
- **Ch5 (M3-C05-01), proposal:** the *Seventh Terrace*'s name-board goes home to Pemakar's harbour and is hung with its wake-shells. Asha's first reach-band is shown (N-01).
- **Ch7 (M3-C07-01), proposal:** the payoff of `ch04_rhen_named_kell`.
- **Ch9:** C4-14's sinking motes are the third time in Act I that the player has watched held light go down into the sea after an Order rite. The Ebbing is the fourth.
- **Ch13, proposal:** the payoff of `ch04_saw_ysolde_ink`.

---

## 10. Echo watches (ADR 0017's Ch4 row, re-checked for this sheet)

| Beat | Nearest analogue in the inspiring game | Verdict |
|---|---|---|
| The wake (C4-01–C4-04) | (no close analogue: the inspiring game's departure from the island is a send-off at the dock) | A living funeral is ours (bible §4). The village sings a homecoming song **knowing**. Pass. |
| The dock (C4-06) | the heroine and hero alone by the water at night, with an embrace and her tears (that comes much later in the inspiring game) | Ours is early, the comfort runs the other way, nobody cries, and nobody touches but for the cake. **Watch:** no embrace, kiss or held hands; never the `ending_dock` framing. Pass. |
| The departure (C4-08) | the village waving the pilgrims' boat away from the dock | She **walks** the causeway at dawn, and nobody follows past the wall. Pass. |
| Ysolde (C4-09) | the cold black mage who is a guardian from the heroine's own village | An Order appointee from Ansedra, met at the gangplank, who kept away from the wake on purpose. ADR 0017's roster row. Pass. |
| The crossing (C4-10–C4-14) | the monster attacking the pilgrims' boat, a boss on deck, the hero diving into the sea to fight it | **The ferry is never attacked.** The party **chooses** to board a dead ship to honour a sea-law, the boss is on the derelict, and nobody fights in the water. Pass. |
| The hero learns the pilgrimage's cost (C4-04) | the hero learns very late, in anger, what the pilgrimage ends in | Ours is Ch4, early, from a village's grief, as ADR 0017 records. Pass. |
