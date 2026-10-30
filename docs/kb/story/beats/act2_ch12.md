# Act II Beat Sheet: Ch12 "The Cold Road" over Keth Pass, Quellan and Cloudloom, two days (M4)

**draft: pre-gate.** Written ahead of the Act I gate as ADR 0203 preparation (the Lead's assignment and order, 2026-10-30). Docs only: no `.dlg`, flag or data exists for anything below until the gate passes and M4-C12-01 is reviewed.

Owner: Narrative (M4-C12-01; drafted by the act2-plan track). Reviewer: Cinematics (SPEC §12.3).
Sources:
- [act outline Ch12](act_outline.md);
- ADRs: [0015](../../decisions/0015-vowbound-element-temple-order.md) (Cloudloom is Holy and nothing in it is frozen), [0016](../../decisions/0016-act-two-restaging.md), [0020](../../decisions/0020-kerrid-restaging.md), [0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) ((d): Toma and the Corrow wall);
- [vowbound.md §4 (Hesk)](../vowbound.md), [bible §5.7 (the Ullar Heights)](../bible.md), [voice guide](../voice_guide.md);
- the characters: [Ysolde](../characters/ysolde.md), [Toma](../characters/toma_okeru.md), [Kerrid](../characters/kerrid.md), [Asha](../characters/asha_velamir.md);
- [act1_ch09.md](act1_ch09.md) B01 (Marra's word reaches Toma) and §3;
- art: [color script `ch12`](../../art/color_script.md), [keth_pass.md](../../art/environments/keth_pass.md) (shots K01–K07; K04 is the breath frame), [avalanche_ram.md](../../art/creatures/act2/avalanche_ram.md), [vowbound/hesk.md](../../art/creatures/vowbound/hesk.md);
- the plan: [act2_plan.md §2 Ch12](../../plan/act2_plan.md).

Previous chapter: [act2_ch11.md](act2_ch11.md). Next: Ch13 "Gold and Lacquer".
Greybox: M4-C12-02:
- `ch12/keth_pass`: three switchback flights, the pass-cords, `knot_post`, RamArena, `cold_ledge`;
- `ch12/quellan`: the street, the inn `inn_door`, the well;
- `ch12/cloudloom`: the stair, the open-roofed hall, the aisle, Hesk's dais `hesk`.

Fights: M4-C11-03 (`ridge_lynx`, `cord_moth`, `scree_crawler`).

Scripts: none yet (M4-A2P-003). Sample lines set the voice only.

**The rules this chapter must keep:**
1. **No ice, frost or frozen water in any temple or set piece** (ADR 0015; keth_pass.md). The pass's snow and wind are weather. Cloudloom is stone, cord and sky. The Ram's arena hazard is **stone and scree** off the wall's coping, not snow (keth_pass.md §2).
2. **Up here the dead lift quickly** (bible §5.7). The few motes in the heights rise fast, in `glimmer_lift`. The seep's light is held (it is drowned light coming out of the mountain); what the Ram's fall releases rises.
3. **Kerrid's breath doesn't fog,** and it is noticed by **Toma alone**, who says only what Act I set up (act1_ch09 B01): Marra's word, not the conclusion. **Toma is the first to suspect and the last to say it** (toma_okeru.md). Nobody names what Kerrid is. Ch15 pays it in two lines.
4. **Ysolde lies, then confesses.** The lie is small and plausible, and the confession is hers, unprompted, the same night.
5. **Nothing about the founding.** Ama's keth count Cantors against Saints. They don't explain why; the ledgers in Ch13 do (ADR 0016).

---

## 0. The chapter in one paragraph

The party climbs the Cold Road over Keth Pass in thin bright cold, under an enormous sky. Across every saddle the Ullari have strung pass-cords hung with thousands of knotted keth, each knot a name, tied for the dead by people who then walk on without looking back. In the shade of the crag Toma sees that everyone's breath is fogging except Kerrid's. He says one sentence to Kerrid about something an old woman told him at Corrow, and Kerrid says nothing, and Toma doesn't ask. Under the summit an ancient Lit Age terrace wall weeps cold light out of its joints, and a woolback that drank there has grown into the Avalanche Ram. In the highland town of Quellan they rest, and at noon the next day they climb to Cloudloom: an open-roofed weaving-hall cut into the summit rock, hung with thousands of keth that throw their shadows on the white stone floor like writing. Asha binds Hesk, the Cord-Keeper, who was Ama Quillo, a keth-reader who started counting. Ama's own keth hang among the thousands, and Ysolde, who can read them, tells the party they are a pilgrim's prayers. That night at the inn she comes to Asha and tells her the truth: they're arithmetic. Forty-seven voices, seven houses. Where did the rest go?

**Emotional line:**
1. exhilaration in the cold (the road, the sky);
2. a small wrongness, noticed and held (the breath);
3. a thing that drank the wrong water (the Ram);
4. warmth at an inn;
5. awe in white stone (Cloudloom);
6. a lie told kindly;
7. the lie undone at night;
8. a number nobody can unhear.

**What the chapter must prove:**
- the breath clue placed and held, for Ch15;
- the fifth Vowbound bound, with the verse-sleeve at **S5**;
- the first hard arithmetic against the Order: Saints are a fraction of the Cantors (asha_velamir.md), and that cracks Toma further (toma_okeru.md);
- Ysolde's turn begun, honestly;
- the Ullari way with grief, beside the Kirru's (Ch10) and the Order's (Ch9).

---

## 1. Running order

Time is in-world (two days and a night). Minutes are a first-time player's. Modes:
- **P**, play;
- **C**, cutscene;
- **E**, in-engine scene with player input.

Shot ids: K01–K07 are keth_pass.md's composed shots; the rest are proposed in §7 (P = the pass, Q = Quellan, C = Cloudloom).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The Cold Road** | `ch12/keth_pass`, the first switchback | 09:00 | C | 1.0 | K01, P01 | `keth_pass` | An enormous sky; cords of names across the saddle. | `ch12_started` (exists) |
| B02 | **The switchbacks** | `ch12/keth_pass` | 09:05 | P | 8.0 | K02, P02 | `keth_pass` | The climb; the pass-cords; fights. | — |
| B03 | **Breath** | the shaded flight (`cold_ledge` approach) | 09:40 | E | 1.5 | K04, P03, P04 | `keth_pass` (stripped) | Everyone's breath fogs but his. Toma sees. | `ch12_toma_saw_breath` |
| B04 | *Side scene: "The Knot"* (optional) | `knot_post` | any, before B05 | E | 3.0 | P05 | `silence` (wind) | "I carry the knot. He doesn't have to." | `ch12_heard_the_knot`, `ch12_rhen_tied_knot` (choice) |
| B05 | **The weeping wall** | under the terrace | 10:20 | C | 1.0 | K03, P06 | `keth_pass` → `avalanche_ram` | Drowned light running out of a mountain. A herd-cord on a monster's neck. | — |
| B06 | **Boss: the Avalanche Ram** | `keth_seep_terrace` (arena) | 10:21 | P | 7.0 | battle | `avalanche_ram` (stem 2 under 50%) | Mind the field. | `ch12_ram_felled` |
| B07 | **The herd-cord** | the terrace | 10:35 | E | 1.0 | P07 | `silence` | Somebody owned this animal. | — |
| B08 | **Quellan** | `ch12/quellan` | 15:00 | P | 6.0 | K07, Q01, Q02 | `quellan` | A highland town of stone and woven awnings; warmth; an inn. | `ch12_reached_quellan` (exists) |
| B09 | **Cloudloom** | `ch12/cloudloom`, the stair and the hall | 11:50 (day 2) | P → C | 3.0 | K05, C01 | `cloudloom` | White stone under open sky; thousands of keth. | `ch12_reached_cloudloom` (exists) |
| B10 | **Hesk** | Hesk's dais (`hesk`), noon | 12:00 | C | 3.5 | K06, C02–C06 | `cloudloom` → `hesk_bound` (sting) | The binding at noon, the cords' shadows writing on the floor. | `ch12_hesk_bound` |
| B11 | **"Prayers."** | the hall's aisle | 12:10 | C | 1.0 | C07, C08 | `cloudloom` (stripped) | Ysolde reads Ama's keth and lies. | `ch12_ysolde_lied` |
| B12 | **Forty-seven voices** | the Quellan inn (`inn_door`), night | 22:00 | E | 3.0 | Q03–Q06 | `silence` → `quellan` (night, fire-side) | The confession. A number. | `ch12_ysolde_confessed` |
| B13 | **Down the other side** | `ch12/keth_pass` north descent | 07:30 (day 3) | E | 1.0 | P08 | `keth_pass` (morning) | They walk on without looking back, Ullari-fashion. Toma last but one. | `ch12_complete` |

**Totals:** critical path **37.0 min** (all but B04). With B04, **40.0 min**. Split: **24 min playable (65%)**, 7.0 min cutscene, 9.0 min in-engine.

**Cut order if the chapter runs long:**
1. B02 loses one switchback flight.
2. B08 shortens to the inn.
3. B07 folds into B06's victory.

**Never cut:** B03, B10, B11, B12. Keth Pass itself is first on act_outline's cut notes (fold it into Quellan). If that cut is ever taken, B03 and B05–B06 move to Quellan's upper road, and **B03 must survive** (Ch15 depends on it).

---

## 2. Beat detail

### B01. The Cold Road (C, 1 min)
- **K01:** the hero frame (keth_pass.md): on a switchback looking up the pass, the road's laid-stone zigzag climbing scree under grey crags, and across the saddle a **pass-cord** sagging cairn to cairn, hung with a hundred keth in undyed wool and red, moving in the wind against an enormous sky (color script `ch12`: cold 09:00, hard sun between cloud banks, the red the only warm note).
- **P01:** the party on the first switchback, small. The few motes up here **rise fast**, straight up and gone (rule 2). Pell watches one go: *"Quick. Up here."*

### B02. The switchbacks (P, 8 min)
- **The zone:** three switchback flights along the cliff (the greybox ramps; the kit's `keth_road_switchback`, `keth_scree_slope`), with pass-cords on the drop side and cairns with cords tied round them. Snow in the air in gusts (weather only, rule 1).
- **Systems:**
  - random encounters (M4-C11-03: `ridge_lynx` pounces on the weakest, `cord_moth` unravels a buff, `scree_crawler` is armoured, so Kerrid is the answer);
  - a save shrine at the second saddle (an Order shrine, an old one);
  - one chest.
- **Barks** (~110 words):
  1. Ysolde, at a pass-cord, touching a knot without meaning to: *"Each knot is a name. They are read by touch."* She takes her hand away quickly.
  2. Liss (reads `ch11_lamp_repaired`: "Rhen"; otherwise "Sallow"): *"Rhen. If I fall off this mountain, the launcher goes to Tobin."* (Tobin is alive. The line is a joke, and in hindsight it isn't.)
  3. Toma, at a cairn: *"They tie a knot and walk on. In Haluna we would sit with them for three days."*
  4. Liss, at the cords (reads `ch10_found_scrape_mark`): *"Like the Kirru's standing marks. Everybody up here counts things. Nobody down there reads them."*
  5. Asha, watching a mote go straight up: *"Even here."*

### B03. Breath (E, 1.5 min)
- **K04** (keth_pass.md's breath frame): the third flight runs in the crag's shade, and the cold bites. The party stops to rest at the ledge. **Every breath fogs**: Rhen's in quick puffs, Toma's in long plumes, the Kirru's in two thin jets, Asha's, Liss's, Ysolde's. **Kerrid's doesn't.** He stands against the dark crag (composed for it: keth_pass.md), and the air in front of his face stays clear.
- **P03:** the camera doesn't point at it. It's a wide two-shot of Toma and Kerrid, and the player who's looking will see it. Then **Toma sees it**: he stops mid-breath, and his own plume hangs in front of him.
- **P04:** Toma waits until the others have moved on up the road. Then, quietly, to Kerrid, without accusation (the line act1_ch09 B01 set up; reads `ch08_fishwife_called`, set on the critical path):
  - Toma: *"At Corrow, one of the old watch told me she had seen her captain on the stair."*
  - Kerrid looks at him. A long time. Then he walks on up the road.
  - Toma doesn't follow it up. He stands one more breath, then walks on behind him.
- Sets `ch12_toma_saw_breath` (Ch15's "Your breath. In Ullar." / "Yes." pays it). **Rule 3:** no other character sees it; no music sting; nobody says "dead", "breath" or "captain" again in this chapter. ~20 words.

### B04. Side scene (optional): "The Knot" (E, 3 min). See §4.

### B05. The weeping wall (C, 1 min)
- **K03:** under the summit, the old road's terrace: a **Lit Age retaining wall** of huge fitted white-grey ceramic blocks, far older than the pass, broken at the coping. **Drowned glimmer seeps out of its joints** and runs down its face in thin sheets of cold held light, like water but not water (keth_pass.md; rule 1: never frozen). The grass at its foot round a pale pool is too long and too pale.
- **P06:** by the pool, drinking, **the Avalanche Ram**: an Ullari woolback, still unmistakably one (long neck, soft camelid muzzle), stands three metres at the head, its fleece matted into heavy locks, with the seep's cold light showing through where the fleece parts. Round its neck, **a frayed red herd-cord with a few knots** (avalanche_ram.md). It lifts its head and looks at them.
- Ysolde: *"It drank the wrong water."*

### B06. Boss: the Avalanche Ram (P, ~7 min)
See §5.

### B07. The herd-cord (E, 1 min)
- **P07:** the Ram down by the pool. The seep's light that soaked it **leaves it and rises**, quick, as everything up here does (rule 2). The player can interact with the herd-cord on its neck. Kerrid kneels and unties it (he doesn't kneel often; animals shied from him all game: kerrid.md, but this one is past shying). He hands it to Pell, who reads the knots by touch, the way the Ullari do:
  - Pell: *"Three names. The herder's family."* (Beat.) *"Somebody loved this animal."*
- Pell ties the herd-cord onto the nearest pass-cord, and they walk on without looking back. (Optional; skipping it leaves the cord on the Ram.)
- ~10 words.

### B08. Quellan (P, 6 min)
- **K07, Q01:** the highland town at 15:00: stepped stone lanes, mortarless many-sided walls, woven awnings in dense patterns (tide patterns, oddly, so far from the sea: bible §5.7), woolbacks in pens, a pass-cord across the main lane. The Ullari are courteous and spare, and to coastal eyes cold.
- **Systems:**
  - **the Quellan trader** (M3-UI-209's `quellan_trader`: Act II gear tier);
  - **the inn** (`inn_door`, with the red banner);
  - a shrine (Order: it's before the heresy);
  - **no fights**.
- **Barks** (Ullari, ~90 words):
  1. A weaver: *"Tide patterns. My grandmother's. Nobody here has seen the sea. We weave it anyway."*
  2. The innkeeper, of the dead: *"You tie the knot. You walk on. They go up quick here, the dead. It's the air."*
  3. A herder, if the party carries word of the Ram (`ch12_ram_felled`): *"The big one? That was Dorro's. Dorro's gone. Last winter."* (The cord's three names.)
  4. A keth-reader at a doorway, reading a cord by touch with her eyes closed. If Ysolde passes, the two look at each other: two readers.
  5. Toma, with Asha, looking at the pass-cords: *"Three days, in Haluna. Sitting with them."* (Beat.) *"I do not know anymore which is kinder."*

### B09. Cloudloom (P → C, 3 min)
- **Day 2, 11:50.** The stair up from Quellan to the summit, cut into the rock. At the top, **Cloudloom** (K05): a weaving-hall cut into the summit rock, its roof **open to the sky** under a lattice of beams, hung with **thousands of keth** that stir in the thin wind. The floor is white stone. It's cold, and it's stone, cord and sky, never ice (rule 1; bible §5.7). An aisle runs through the cords to Hesk's dais.
- **C01:** the party walking the aisle between hanging cords, which brush their shoulders. Ysolde walks slowest. She can't stop reading by touch as she passes.

### B10. Hesk (C, 3.5 min)
- **K06:** **noon.** The sun comes straight down through the open roof, and the cords' shadows fall on the white floor **like writing** (bible §5.7). The whole floor is a page.
- **C02:** at the dais, **Hesk**: a great condor whose wing feathers are knotted cords patterned like Ullari weaving, lit from inside with clean white light (vowbound/hesk.md). She holds a **keth bundle** in one talon (the keepsake). Bound light, still (color rule 2).
- **C03 (the binding, ~90 s; M4-A2P-071):** Asha sings the verses she has. Hesk spreads her cord-wings, and **the fifth verse** comes down out of the open sky to her: a woman's voice, plain and steady, a reader's (Audio: `hesk_bound`). The light runs along the cords overhead, and their shadows on the floor move as if the writing were being rewritten. The verse-sleeve grows to **S5**. Hesk is bound to Asha.
- **C04:** as the light settles, Hesk's head turns: not to Asha, but **to the cords above the dais**, to one particular bundle hanging among the thousands, darker and older than the rest. Then she's still. (The only hint, as Nhoa's turn was in Ch11: a bound Saint can only turn.)
- **C05:** Ysolde follows the look. She goes to that bundle and puts her ink-guarded hand into the cords and reads them by touch. Her face doesn't change. That's how the player knows something is very wrong: Ysolde's face not changing is the tell.
- **C06:** Toma, beside the dais, watching her. He served the Order for twelve years, and he knows the face of someone reading something they weren't supposed to.
- Sets `ch12_hesk_bound`.

### B11. "Prayers." (C, 1 min)
- **C07:** Asha comes to Ysolde at the cords.
  - Asha: *"What do they say?"*
  - Ysolde (perfectly, a scholar's answer): *"Prayers. A pilgrim's devotions. The Cantor who stayed here was Ullari: they tie everything." She lets the cords fall. "It is very old wool."*
- **C08:** Ysolde walks away down the aisle first, faster than she climbed it. Rhen watches her go. Toma watches her go. Nobody says anything. The player has seen her face not change. Sets `ch12_ysolde_lied`. ~35 words.

### B12. Forty-seven voices (E, 3 min)
- **Q03:** the Quellan inn at night, by the fire. The others are asleep or nearly. Asha is awake on a bench. Ysolde comes down the stair, her hair half down as if she has been lying awake (the Level-pin is still in it: she drops it in Ch14).
- **The confession** (unprompted: rule 4; ~110 words):
  - Ysolde: **"I read the cords. I lied to you about them. I would like to stop doing that now."** (The voice guide's sample, fixed.)
  - Asha waits. She doesn't ask what Ysolde's day was like. She asks the question:
  - Asha: *"What do they say?"*
  - Ysolde: *"They are a count. Hers. Ama Quillo's. Every Cantor on the roll up to her own name, one knot each. Forty-seven."* (Beat.) *"And then the Saints. The houses that keep one. One knot each."* (Beat.) **"Forty-seven voices. Seven houses."** (asha_velamir.md: the Saints are a fraction of the Cantors.)
  - Asha: *"...Where did the rest go?"*
  - Ysolde: *"She tied that too. A question-knot. Hanging at the end of the count, by itself."* (Beat.) *"She sang anyway. She believed faith could hold a question."* (vowbound.md §4.)
  - Asha, very quietly: *"Could it?"*
  - Ysolde: *"I have visited my husband every year for twenty-four years, Lady Cantor. I would very much like it to."* (She doesn't do the maths on Corran here; that's the Archive's, Ch13: ADR 0016.)
- **Q05:** Toma is on the stair. He has heard. He comes down and sits on the hearth step with his back to them both, not intruding, a guard's place. Without turning:
  - Toma: *"Seven houses."* (A long pause before the hard truth.) *"I stood guard at four of them."*
- **Q06:** the fire. Nobody says anything else. Sets `ch12_ysolde_confessed`.
- ~140 words.

### B13. Down the other side (E, 1 min)
- **P08:** day 3, morning. The north descent from the saddle. The party passes under the last pass-cord, and, Ullari-fashion, **nobody looks back**. The player can't turn the camera back (a rail shot looking ahead only, the one directed field moment in the chapter).
- If `ch12_rhen_tied_knot`: Rhen's hand goes up to the cord as he passes under it, and he doesn't look. Line order: Toma first, Pell behind him, Asha, Ysolde, Liss, Rhen, and Kerrid last. Toma glances back at the line once, at Kerrid, and then faces forward. Sets `ch12_complete`.
- No dialogue.

---

## 3. Flags

Declared in `game/data/flags.tres` when the gate passes (M4-A2P-012 adds them). `ch12_started`, `ch12_reached_quellan` and `ch12_reached_cloudloom` already exist (M4-C12-02).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch12_toma_saw_breath` | B03 (critical) | Ch15 | **"Your breath. In Ullar." / "Yes."** (act2_ch15.md K18) |
| `ch12_heard_the_knot` | B04 (optional) | Ch17, the Ending | Rhen at the Heart: "I carry the knot. You don't have to." (Narrative, consider it for H02) |
| `ch12_rhen_tied_knot` | B04 choice | B13, Ch21 | He tied a knot for Dace, believing him dead; Ch17's ledger and Ch21's meeting turn it over |
| `ch12_ram_felled` | B06 | B08 herder bark | — |
| `ch12_hesk_bound` | B10 (critical) | vowbound.json, the summon menu, verse-sleeve S5 | Hesk in Asha's roster |
| `ch12_ysolde_lied` | B11 (critical) | Ch16 | At the Choir, Ysolde to Sefir: "I lied once this year, for your sake. I am done." |
| `ch12_ysolde_confessed` | B12 (critical) | Ch13, Ch16, Ch20 | **Ch13:** she reads the Cantor roll knowing what she's looking for; **Ch20:** Hesk's release: Toma tells Ama he read her cords |
| `ch12_complete` | B13 (end) | flow (Ch13 gate) | — |

**Flags this chapter reads:** `ch08_fishwife_called`, `ch10_found_scrape_mark`, `ch11_lamp_repaired`.

---

## 4. The optional side scene: "The Knot" (B04)

**Where:** the knotted post (`knot_post`) at a saddle, where a pass-cord is tied off. **When:** any time in B02 before B05, through a marker on the Ullari woman. **Length:** 3 min, ~90 words. **Speakers:** `ullari_woman`, `rhen`.

**Beats** (act_outline Ch12):
1. An Ullari woman in layered weaving, middle-aged, plain, ties a knot onto the pass-cord: careful, practised, quick. She touches it once.
2. Then she **walks on without looking back.** Rhen, who has been watching, can't help it: he catches her up.
3. Rhen: *"How do you do that? Just walk."*
4. She stops. She considers him, a coastal boy.
   - Ullari woman: *"My son. Last spring. On this road."*
   - Rhen: *"And you just walk on?"*
   - **Ullari woman: "I carry the knot. He doesn't have to."** (act_outline's fixed line.)
5. She goes on down the road. Sets `ch12_heard_the_knot`.
6. **Choice** (Rhen at the cord):
   - *Tie a knot.* Rhen takes a length of the spare cord the Ullari leave at every post and ties a knot, clumsily (he's a diver, not a weaver), for his father, whom he believes dead (rhen_sallow.md). He doesn't say who it's for, and he walks on without looking back, almost. Sets `ch12_rhen_tied_knot`.
   - *Walk on.* He looks at the cord a long time and doesn't.

**Rules:** she isn't wise, she's tired, and practical. No music. Nobody else from the party is in the scene. The knot is never named on screen.
**Payoff:** `ch12_heard_the_knot`, `ch12_rhen_tied_knot` (§3).

---

## 5. The boss: the Avalanche Ram (B06)

**Lore justification (SPEC §6.7):** an Ullari woolback that drank where drowned glimmer seeps out of a Lit Age terrace wall and grew (avalanche_ram.md). It isn't a spawn of the storm. It's an animal ruined by the old world's held light, someone's animal (the herd-cord).

**Arena:** `keth_seep_terrace` (env-art, M3-ENV-717): the old road's paved top, the seeping wall behind the Ram, the drop to the switchback behind the camera. Staged ids (M3-BPR-419; M3-BPR-408 has its charge camera): enemy `avalanche_ram`; no phases (act2_finals.md: stem 2 is the bellow's rage under 50% HP).

**The fight** (one phase, two moods):
- **The charge:** telegraphed (one turn: it lowers its head, `charge_side` camera, M3-BPR-408), a heavy blow on the front line. Each charge that lands against the wall **brings down stone and scree** off the broken coping: a **field hazard** (rule 1: never snow). It is a `field_rules` row: the party side gains a stacking **Slow** (or a flat hit each turn) while the scree field is up, round by round, until cleared. Ysolde's fire burns the seep-soaked grass and **clears the field** (`clears_field`), as Virel cleared Ch8's dark.
- **The rage (under 50%):** stem 2. It bellows (a cast) and gains Haste for two turns. Toma's Provoke and counters keep it off the back line, and Kerrid's armour break on the matted fleece opens the seep-lit partings (weak points: `spawn_wound`).
- **Hesk isn't bound yet** (B10 comes after), so the fight uses the party and the first four Vowbound.

**What it teaches:** mind the field. The longer the fight, the worse the ground. Clear it or end it.

**Balance:** the Act II boss band (naive ≤ 3%, role_answer 55–80%, smart 70–90%, p90 ≤ 80) on the Ch12 loadout (M4-A2P-019). Not `scripted`; Escape allowed.

**Music:** `avalanche_ram` (two stems, rendered: M3-AUD-845); stem 2 at 50%. The charge's run sound is M3-AUD-838 (in review).

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `keth_pass` | B01, B02, B03 (stripped), B05 (in), B13 | Zone loop (exists, M3-AUD-841) | — |
| `avalanche_ram` | B06 | Boss, two stems (exists, M3-AUD-845) | — |
| `quellan` | B08, B12 (night, fire-side) | Zone loop (exists, M3-AUD-841) | B12 wants a sparse night mix (a stem mute). |
| `cloudloom` | B09, B10 (bed), B11 (stripped) | **Zone loop**, ~120 s (not yet written: act2_finals.md; M4-A2P-091) | The open-roofed weaving-hall: wind through cords as a texture, a plain sung line (Ullari timbre), high and clear. Holy without being churchly: no Order hum, no organ-like pad. Cold colour, nothing icy. |
| `hesk_bound` | B10 (C03) | **Sting**, ≤ 8 s (not yet written; M4-A2P-091) | The fifth verse's first phrase in a plain, steady woman's voice, a reader's. Ends on *mir*. |
| `hesk_summon` | (her first battle call) | Sting ≤ 6 s (M4-A2P-091) | — |
| `silence` | B04 (wind only), B07, B12 (start) | — | — |

**SFX:**
- `cord_wind` (thousands of keth stirring: Cloudloom's bed, and the pass-cords);
- `knot_tie` (B04);
- `scree_fall` (the field hazard);
- `woolback_bellow` (the rage);
- `breath_fog` (no sound, a visual only: listed so nobody adds one to Kerrid).

---

## 7. Camera shots by beat

New shot ids for `ch12/keth_pass`, `ch12/quellan` and `ch12/cloudloom` (to add to keth_pass.md beside K01–K07).

| Id | Shot | Lens / note |
|---|---|---|
| P01 | The party on the first switchback; a mote going straight up | 35 mm |
| P02 | A pass-cord across the road at a saddle, the party passing under | rail |
| P03 | **Wide two-shot:** Toma and Kerrid against the dark crag, breath fogging from Toma, none from Kerrid | 50 mm; **the camera does not push in on Kerrid's face** |
| P04 | Toma to Kerrid, low; Kerrid's look; Kerrid walking on | 85 mm singles |
| P05 | The knotted post: the woman tying; Rhen (side scene) | 50 mm, locked |
| P06 | The Ram at the pool, lifting its head; the herd-cord | 50 mm, then insert |
| P07 | Kerrid untying the herd-cord; Pell reading it by touch | 85 mm |
| Q01 | A Quellan lane, woolbacks, tide-pattern awnings | rail |
| Q02 | The inn's red banner | rail look-at |
| Q03 | The inn at night: the fire, Asha on the bench, Ysolde on the stair | 35 mm |
| Q04 | Ysolde and Asha by the fire | 50 mm two-shot, then 85 mm singles |
| Q05 | Toma sitting on the hearth step, back to them | 50 mm |
| Q06 | The fire | 85 mm insert |
| C01 | The aisle between hanging cords, cords brushing shoulders | 35 mm, tracking |
| C02 | Hesk on her dais at noon | 35 mm, low |
| C03 | The binding: the cords' shadows moving on the floor like writing being rewritten | 18 mm, from above (the open roof) |
| C04 | Hesk's head turning to one dark bundle above the dais | 85 mm |
| C05 | Ysolde's hand in the cords; her face not changing | 85 mm, held |
| C06 | Toma watching her | 85 mm |
| C07 | Asha and Ysolde at the cords: "Prayers." | 50 mm two-shot |
| C08 | Ysolde walking away down the aisle; Rhen and Toma watching | 35 mm |
| P08 | The north descent under the last pass-cord, looking ahead only | 35 mm rail, forward only |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B03 | K04 → P03 → P04 | **P03 is the clue:** a wide that a watching player can read. Never a close-up of Kerrid's mouth, and no music cue. |
| B10 | K06 → C02 → C03 → C04 → C05 → C06 | K06 holds ≥ 5 s: the floor as a page. C05 holds on a face that doesn't change. |
| B11 | C07 → C08 | — |
| B12 | Q03 → Q04 → Q05 → Q06 | Q05: Toma's back is to the camera and to them. |
| B13 | P08 | Forward only. |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 | 5 |
| B02 barks | 110 |
| B03 | 20 |
| B04 side scene | 90 |
| B05 | 5 |
| B07 | 10 |
| B08 barks | 90 |
| B11 | 35 |
| B12 | 140 |
| **Total** | **~505 written** (~310 on a path without the optional barks and side scene) |

**Against SPEC §3.6:** at ~38 min, Ch12 is about 2.2% of the game, so its fair share is **880–1,300 words**. It is under the band; Quellan and the pass can take more Ullari barks (state-changing NPC lines, SPEC §6.6) when the script is written. The chapter's key beats are short by design.

---

## 9. Requests to other roles

### Rendering (M4-A2P-049)
1. **Breath fog** (B03; everywhere outdoors in Ch12): a per-actor breath VFX on every living character in cold zones, **never on Kerrid**, in cutscenes and in the field. A data flag per actor (`breathes: false` on Kerrid), so no later chapter forgets it.
2. **The seep** (B05): emissive held light running down the wall's face (the kit's `kp_seep`), never frozen; and its release rising fast off the Ram at B07 (rule 2).
3. **Cloudloom's noon** (K06, C03): the cords' shadows on white stone, crisp, from a near-vertical sun through the open roof; in C03, the shadows shift as the light runs along the cords.

### Art (color script)
1. `ch12` exists. Confirm Cloudloom's noon (a near-vertical key through the open roof) and the inn at night (fire-lit, the only warm interior of the chapter).

### Environment Art (M4-A2P-042)
1. The kit exists (M3-ENV-717, M3-ENV-734). Place it per keth_pass.md §6:
   - the shaded ledge composed for P03 (a dark crag behind Kerrid's mark);
   - the knotted post with spare cord;
   - the seep pool and the pale grass;
   - Quellan's lanes, inn and pens;
   - Cloudloom's hall with **thousands of instanced keth** and a darker old bundle over the dais.
2. The scree field's fall (an arena VFX hook, B06).

### Character Art (M4-A2P-053)
1. **The Ullari woman** (side scene) and Quellan's townsfolk (the Ullari costume set on the crowd generator); a keth-reader; the innkeeper; the herder.
2. **Ysolde's ink-guarded hand in the cords** (C05): a hand pose reading by touch.
3. **Kerrid:** `breathes: false` (with Rendering).

### Audio (M4-A2P-091)
`cloudloom`, `hesk_bound`, `hesk_summon` (§6), and the SFX list.

### UI
1. The verse-sleeve at **S5** after B10.
2. The field camera's forward-only rail in B13 (a one-off).

### Combat (M4-A2P-012, M4-A2P-024)
§5: the Ram's charge, the scree field as `field_rules` with `clears_field` on fire, the rage under 50%. Hesk's `vowbound.json` row (`bound_flag: ch12_hesk_bound`).

### Systems / Chapters (M4-A2P-012)
1. **Speakers:** `ullari_woman`, `quellan_innkeeper`, `quellan_weaver`, `quellan_herder`, `keth_reader`.
2. The day-2 climb to Cloudloom starts from the inn (rest), and the night scene runs from the inn on return.

### Cinematics (reviewer)
Check §0's rules against every shot, especially:
- P03 (the clue is readable but not pointed at);
- C05 (a face that doesn't change);
- Q05 (Toma's back);
- the whole chapter: no ice in Cloudloom or the arena.

---

## 10. Open questions for review

1. **The Avalanche Ram's ice.** avalanche_ram.md (built: M3-CRE-624) gives the Ram "plates of ice and wool" and icicles on its locks, but ADR 0015 and keth_pass.md say no ice in any temple **or set-piece** from Ch12 to Ch15, and the arena keeps none. A boss fight on the terrace is arguably a set piece. **For the Lead:** either rule that a creature's own frosted fleece on an open mountain is weather, not a frozen temple (ADR 0015 was about the inspiring game's frozen-lake temple), or ask creatures-b to swap the ice for wet, matted, seep-lit wool (a materials change, not a rebuild). This sheet assumes the second is safer.
2. **"Seven houses"**: this sheet reads Ama's seven as the seven Saint-houses she could count in her time. Vowbound.md has seven Vowbound in all, but Hesk herself (the 47th) wasn't a Saint yet when she counted, and Corran (60th) and Nhoa (56th) came later. **Narrative: reconcile the count** (Ama counted the houses that kept a Saint in her day; the number seven is the bible's and is fixed).
3. **Rhen's knot (B04)** for Dace is this sheet's addition. It's optional and never named. If Narrative thinks it spends Ch17's ledger early, cut the choice and keep the woman's line.
