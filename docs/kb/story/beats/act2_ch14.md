# Act II Beat Sheet: Ch14 "The Peace Wedding" at the Lacquer Court and on the still lagoon, dusk to night (M4)

**draft: pre-gate.** Written ahead of the Act I gate as ADR 0203 preparation (the Lead's assignment, 2026-10-30). The Lead waived M4-C14-01's chained `depends_on` so this sheet can come before Ch11–13. Docs only: no `.dlg`, flag or data exists for anything below until the gate passes and the sheet is reviewed.

Owner: Narrative (M4-C14-01; drafted by the act2-plan track). Reviewer: Cinematics (SPEC §12.3). **The Lead reviews it too** (SPEC §12.3: tone-sensitive, and the act's highest IP-echo risk).
Sources:
- [act outline Ch13–Ch14](act_outline.md);
- [ADR 0016](../../decisions/0016-act-two-restaging.md) (a) and its echo check (Ch14 row), [decisions_log N-18](../decisions_log.md);
- [bible §5.8 (Ansedra), §6 (the Order: the Conclave, the Wardens, the Stillguard)](../bible.md), [voice guide](../voice_guide.md);
- the characters: [Liss](../characters/liss_varrow.md) (Tobin, Merel), [Toma](../characters/toma_okeru.md) (the former commander), [Sefir](../characters/sefir_aurane.md), [Kerrid](../characters/kerrid.md) (the water-steps), [Ysolde](../characters/ysolde.md) (the Level-pin);
- art: [color script `ch14`](../../art/color_script.md), [ansedra.md](../../art/environments/ansedra.md) (the court, the arena `ansedra_lagoon_escape`), [flat_engine.md](../../art/creatures/act2/flat_engine.md);
- [set_piece_battles.md](../../design/set_piece_battles.md) (ADR 0100's schema);
- the plan: [act2_plan.md §2 Ch14, §2a](../../plan/act2_plan.md) (design defaults (b) and (d), accepted by the Lead 2026-10-30).

Previous chapter: Ch13 "Gold and Lacquer" (not yet written: M4-C13-01). Next: [Ch15 "Unlamped"](act2_ch15.md).
Greybox: M4-C14-02 (`ch13/ansedra_lacquer_court`: the colonnade, the dais with `vows` and `tobin_falls`, the galleries, the Conclave's gallery, the water-steps `kerrid_steps`, the bridal barge `barge_deck` with its `barge` trigger, the water-gate `merel_gate`).

Scripts: none yet (M4-A2P-005). Sample lines set the voice only.

**What Ch13 hands this chapter** (to confirm when M4-C13-01 is written):
- The party has had three days in the Lamp Archive. Liss and Ysolde have read the founders' ledgers and the Cantor roll's *kept/spent* column. Ysolde has done the maths on Corran.
- They agreed to say nothing until Tobin is married and they can get him out. Tobin won't call the wedding off: it is his people's peace.
- Sefir knows exactly what Liss read; he let her.
- Ethren is bound (`ch13_ethren_bound`).
- Kerrid has sat out every night at the outer moorings.
- Tobin and Merel have each had at least one scene (Ch13's "the wedding announced"), so the player has met them before today.

**The rules this chapter must keep** (ADR 0016's echo check; plan §2a):
1. **The escape goes out across the water, never under the city.** No prison, no trial, no capture of the party, no sewer, cistern or under-passage. The party is never in the Order's hands for a single beat.
2. **Nothing is revealed about any Warden.** Malcor Venn fights as a living-seeming man. No revenant tell, no unmasking, no ageless line, and no rite performed on anyone. The Archive told the player what the Conclave is; this chapter never says it.
3. **No rite on Kerrid.** Nobody performs the Stilling, or anything like it, on him or near him. His glow isn't shown in this chapter at all: the court is lit, and the lagoon at night belongs to the escape.
4. **Asha is not the bride, and nobody marries her.** The wedding is Tobin's and Merel's. Sefir officiates and never proposes anything to anyone.
5. **The ally's cost is seen.** Merel stays, and the party watches her taken. No cutaway spares the player that, and no later scene undoes it in Act II.
6. **Sincerity.** The ceremony is beautiful and meant, by Tobin and by Merel. The trap is the Conclave's. Humour lives only before the trap, as warmth between Liss and Tobin, and nothing is funny after it.

---

## 0. The chapter in one paragraph

The peace wedding is held at dusk in the Lacquer Court on the still lagoon. It is Tobin Varrow, a Saltwright, marrying Merel Dask, a Warden's daughter, and Liss, who campaigned for it, lets herself hope for one afternoon. Sefir officiates, gracious and warm. Hollowmere's hull-captains stand in the court as guests of the Order for the first time in living memory. When the vows are spoken, the Conclave stands in its gallery. Warden Malcor Venn reads a declaration: the hull-captains are seized for binding, the Cantor's guardians are declared heretics for sheltering binders, and the Lady Cantor is to be taken into the Order's care. Sefir says he is sorry and means it, and does nothing. In the struggle on the dais a Stillguard's spear meant for Merel, who is trying to stop them taking her husband's people, finds Tobin, who stepped in front of it. Merel, widowed for a minute, cuts her own bridal barge loose and poles the party out onto the lagoon where no wake has been permitted for four hundred years, while Kerrid and Toma hold the water-steps. Every stroke is a ripple. The bells ring, and the whole city comes to its windows to watch the water move. Merel stays to drop the court's water-gate behind them, and the last thing they see is her father's Stillguard taking her, still in wedding red, with Tobin's blood on her sleeve. Out on the dark lagoon a black barge comes after them, and around it the water goes flat again. Liss breaks the engine that stills the water, and Warden Malcor Venn boards and is beaten. They leave him standing on his crippled barge in the middle of the ripples, and drift out of the lagoon mouth into the open sea with no lamp and a dead man under a bridal cloth.

**Emotional line:** hope, allowed for once (Liss) → beauty (the ceremony on still water) → the turn (the declaration) → horror, fast (Tobin) → resolve (the steps; Toma refuses) → the first ripple (release, made physical) → the cost, watched (Merel) → fury turned on a machine (Liss and the engine) → a living-seeming man left standing → silence, dark water, a body.

**What the chapter must prove:**
- **SPEC §3.5 / §10.2's mandated set piece:** "a wedding becomes a trap" and "the party is declared heretics", staged so it echoes nothing (rules 1–4);
- Tobin's death as Act II's real cost (liss_varrow.md);
- the first moving water in Ansedra as the chapter's hero image;
- Merel's sacrifice seen;
- Toma's first open refusal of the Order (toma_okeru.md: "ordered by a former commander to stand aside; he doesn't");
- the Venn fight's two phases (the still water, then the boarding).

---

## 1. Running order

Time is in-world (one dusk and the first hours of night). Minutes are a first-time player's. Modes:
- **P**, play;
- **C**, cutscene;
- **E**, in-engine scene with player input.

Shot ids are proposed in §7 (W = the wedding court, S = the water-steps, L = the lagoon).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **Before the vows** | `ch13/ansedra_lacquer_court` | 17:50 | P | 6.0 | W01, W02 | `peace_wedding` (the court's loop) | One afternoon of hope. Meet Tobin and Merel again, and see Liss happy. | `ch14_started`, `ch14_spoke_with_tobin` (optional) |
| B02 | **The vows on still water** | the dais (`vows`) | 18:20 | C | 3.0 | W03–W06 | `peace_wedding` (ceremony) | A real wedding, beautifully meant. | `ch14_vows_spoken` |
| B03 | **The declaration** | the dais, the Conclave's gallery | 18:26 | C | 2.5 | W07–W10 | `peace_wedding` → **the break** → `silence` | The trap. Heresy declared: for binding, by binders. | `ch14_declared_heretics` |
| B04 | **"Stand aside, Okeru."** | the dais | 18:28 | C | 1.0 | W11, W12 | `silence` | Toma's first refusal of the Order he served. Ysolde's pin. | `ch14_toma_refused` |
| B05 | **Tobin** | the dais (`tobin_falls`) | 18:29 | C | 1.0 | W13–W15 | `silence` (court noise only) | Act II's real cost, fast and unglamorous. | `ch14_tobin_killed` |
| B06 | **Set piece: the water-steps** | the water-steps (`kerrid_steps`), the bridal barge | 18:30 | P | 6.0 | battle (set piece) | `lagoon_escape` (part 1, under the fight) | Hold the steps while Merel cuts the barge loose. Kerrid holds a stair again. | `ch14_steps_held` |
| B07 | **The first ripple** | the lagoon from the barge | 18:40 | C → E | 2.5 | L01–L05 | `lagoon_escape` (part 2) | Every stroke is the first wake in four hundred years. The bells. The city at its windows. | — |
| B08 | **Merel at the gate** | the water-gate (`merel_gate`), seen from the barge | 18:45 | C | 1.5 | L06–L09 | `lagoon_escape` (part 3) → `silence` | The ally's cost, watched and paid. | `ch14_merel_taken` |
| B09 | **Boss: Warden Malcor Venn** | `ansedra_lagoon_escape` (arena) | 19:10 | P | 8.0 | battle | `malcor_venn` (stem 1 → stem 2 on the boarding) | The water goes flat again. Liss breaks the engine. A Warden fights like a man. | `ch14_engine_broken`, `ch14_venn_beaten` |
| B10 | **Left standing** | the lagoon mouth | 19:30 | C | 1.5 | L10–L12 | `silence` → `unlamped` (first bars) | Venn on his crippled barge in the ripples. No lamp. The open sea. | `ch14_complete` |

**Totals:** critical path **33.0 min** (B01 6.0 is part play, part talk; the optional Tobin scene sits inside it). Split: **20 min playable (61%)**, 11.5 min cutscene, 1.5 min in-engine. The cinema is dense but short-beated: no single cutscene runs over 3 minutes, and the player is back in control (B06, B09) twice after the trap.

**Cut order if the chapter runs long:**
1. B01 shortens to the walk to the dais (Tobin's optional talk stays).
2. B07's E portion (the poling input) becomes C.
3. B04 folds into B03's end.

**Never cut:** B03's declaration, B05, B06's last-onto-the-barge, B07's bells and windows, B08 in full, B10's last image.

---

## 2. Beat detail

### B01. Before the vows (P, 6 min)
- **W01:** the Lacquer Court at 17:50 under the `ch14` sky: overcast breaking to a thin red band low in the west. Red-lacquer halls on three sides of white slabs inlaid with the gilt Level line; the water-steps down into the mirror lagoon on the fourth side; the water-gate held up over them (ansedra.md). Bowl-domes doubled in the still water beyond. The court is filling: Order dignitaries in pale silk, Tenders, Stillguard at the colonnade in red lacquer and round shields, and, for the first time in living memory, **Hollowmere's hull-captains** standing as guests in their sea-coats, stiff and uneasy, among the people whose edicts burned their camps.
- **The party is free to walk the court.** No fights, no shops. The save shrine is the Order's, in the colonnade (it still works: the heresy isn't declared yet; plan §4.2).
- **Kerrid** is at the back of the court among the barge-polers by the water-steps, standing (kerrid.md). He doesn't come to the dais. **Pell** is with him (the Kirru are tolerated, not welcome).
- **Optional talk: Tobin** (sets `ch14_spoke_with_tobin`; ~90 words). Tobin is in a Saltwright wedding coat with a Warden's red sash over it, both families' colours, and he can't stop grinning. He is charming and idealistic (liss_varrow.md). He talks to Rhen as if they've been friends for years:
  - Tobin: *"She chose the sash. I chose the coat. We argued for a week. Best week of my life."*
  - Tobin, of Liss, lower: *"Look at her. She's pretending she isn't happy. She's terrible at it."*
  - Tobin, the line that carries the chapter, sincere: *"Nobody had to be chosen, Rhen. I volunteered. That's the whole point. Somebody has to go first."* (ADR 0020: Tobin volunteered so nobody would be chosen. That rhymes with every Cantor, and nobody in the scene hears it.)
- **Liss** at the dais steps, in a borrowed good coat she keeps tugging at. If talked to: *"Don't. Don't say anything nice. I'll fall apart and I've got to hand him the ring."* Then, because she can't help it: *"Three years I spent on this. Three years of being polite to Wardens."* (~40 words.)
- **Merel**, briefly, crossing to the dais in wedding red with her women: she stops for Asha. *"Lady Cantor. Thank you for coming. He talks about you all. He talks about everyone."* (Merel is sincere and brave, and she loves him. ~25 words.)
- **Barks** (~80 words):
  1. A hull-captain, to another: *"Sea-coat in a lacquer hall. I feel like a stain."*
  2. A Tender: *"Still water. Not a ripple. Look at the domes: you can't tell which way is up."*
  3. Ysolde, to Asha, very quietly (the Archive is in her face; she keeps the pact): *"Smile, Lady Cantor. It is a wedding."*
  4. Toma, at the colonnade, seeing a Stillguard officer: he stops. *"That is my old commander."* He doesn't go over.
- The walk ends at a marker on the dais. ~235 words in B01 with all optional lines.

### B02. The vows on still water (C, 3 min)
- **W03:** a high wide: the court, the dais at the water's edge, and the domes doubled in a lagoon so still the image is a perfect mirror (rendering: the still-water look, M4-A2P-047). Dusk light, red lacquer, white stone, gold. Not a breath of wind.
- **W04:** **Sefir** on the dais, officiating. Pale still-water silk and the gilded bowl-crown, unnaturally still, warm, unhurried (sefir_aurane.md). His homily is short and lovely, and the player who read the Archive hears every word of it twice:
  - Sefir: *"Ansedra has kept its water still for four hundred years, so that nothing we love is ever stirred away. Today two houses who have hurt each other promise to keep each other still. There is no better vow."* (~45 words; one of his "complete paragraphs in miniature".)
- **W05:** Tobin and Merel facing each other on the dais's edge over the water. Their vows are their own, short and plain, not the Order's (each family wrote one line):
  - Merel: *"I'll learn your knots."*
  - Tobin: *"I'll learn your quiet."*
  - They exchange cords, Saltwright fashion: a knotted line passed hand to hand (the ring Liss carried is threaded on it).
- **W06:** Liss in the front row with her jaw set, eyes full, absolutely not crying. Rhen beside her bumps her shoulder once. Asha is smiling, really smiling. Sets `ch14_vows_spoken`.
- ~70 words.

### B03. The declaration (C, 2.5 min)
- **W07:** in the Conclave's gallery above the dais, **four figures stand at once**: the Wardens of the Conclave in veils and gilt (bible §6). They don't hurry. The court goes quiet the way still water is quiet.
- **W08:** **Warden Malcor Venn** steps to the gallery rail with a lacquered scroll. A broad, hard, sober man in late middle age with a soldier's bearing and a magistrate's voice (characters sheet M4-A2P-051). He reads it plainly, as if he takes no pleasure in it. **Rule 2:** he is a man reading a decree; nothing about him is strange.
  - Venn: *"By the Conclave of Elders. The hull-captains of the flotilla called Hollowmere are taken for the crime of binding."*
  - Stillguard close on the hull-captains from the colonnade, quietly, with no violence yet. The captains look at each other. They knew this could happen and came anyway.
  - Venn: *"The guardians of the Lady Cantor, having sheltered binders and handled the sealed ledgers, are declared outside the Level."* (The Order's word for heresy; Narrative, keep it in our own idiom: "outside the Level" is this sheet's proposal.)
  - Venn: *"The Lady Cantor is taken into the Order's care until her pilgrimage is complete."*
- **W09:** Liss, white, understanding all at once: the Archive's three days were never a gift. They were evidence. *"You gave me the key."* She is looking at Sefir.
- **W10:** **Sefir**, on the dais, turns to Asha. His sorrow is real, and so is his calm (his tell: he answers grief with logic):
  - Sefir: *"I am so sorry, Lady Cantor. This is not the day I wanted for you. It will be quieter after. I promise you that."*
  - Asha, very short (her refusals are very short: voice guide): *"No."*
- The `peace_wedding` loop **breaks** on the declaration's first line: the ceremony's melody stops mid-phrase, and under it there is only the court's held breath (§6). Sets `ch14_declared_heretics`. ~110 words.

### B04. "Stand aside, Okeru." (C, 1 min)
- **W11:** Stillguard move toward Asha. Toma steps in front of her with his tide-shield up. His **old commander** (a Stillguard officer, grey-bearded, decent; name him in the script; this sheet proposes **Commander Brannoc Hale**, checked against the banned-terms list) comes to the foot of the dais and speaks to him as to a son:
  - Commander: *"Stand aside, Okeru. You know me. Stand aside, and be level."*
  - Toma (a long pause before the hard truth: voice guide): *"I know you, sir."* He does not move. *"I am on my shield."*
  - He doesn't answer "Be level." It's the first time in the game he lets the greeting go unanswered. **Cinematics:** hold on it; the player who knows the Ch9 side scene hears the silence (toma_okeru.md; his faith *breaks* in Ch15, and this is the crack opening).
  - Sets `ch14_toma_refused`.
- **W12:** **Ysolde**, beside Asha, reaches up and takes the silver Level-pin out of her hair. Her hair comes partly down (ysolde.md: "In Act II she removes it"). She drops the pin on the white slabs. It rings once. *"I will not be needing that."* (Her rage comes out quieter, not louder.)
- ~55 words.

### B05. Tobin (C, 1 min)
- **W13:** the Stillguard reach the hull-captains, and one of them, an old woman, is forced to her knees. **Merel** runs at the guards in her wedding red, crying *"They're his people, they're my people now, let her go"*, and grabs a Stillguard's arm. A second guard swings his spear's butt at her, then turns it point-first as she won't let go.
- **W14:** **Tobin steps between.** It is fast and ugly and not choreographed to be beautiful: the spear meant to put her down takes him under the ribs. He sits down on the white slabs at the edge of the dais, surprised, with one hand on the knotted cord. (`tobin_falls`.) **Rule 6:** no slow-motion, no last speech, no music. The court noise goes on. He says one thing, to Merel, and it is ordinary:
  - Tobin: *"...Your knots are terrible."*
  - and then he is gone.
- **W15:** Liss's face. She doesn't scream. She goes to him and puts both hands on the wound the way a wright seats a housing, and talks to it, low and fast (her tell: she narrates repairs when grieving): *"Hold it. Hold, hold, she'll hold, seat it, hold—"* It doesn't. Toma lifts her off him with one arm, still holding the shield with the other, and she fights him. Sets `ch14_tobin_killed`. ~30 words.
- **No blood on the slabs in close-up** beyond the sleeve: the wound is framed out. The mark the player remembers is on **Merel's sleeve** (B08).

### B06. Set piece: the water-steps (P, ~6 min)
See §5.

### B07. The first ripple (C → E, 2.5 min)
- **L01 (C):** the bridal barge, a long low lacquered hull with no lamp (wedding barges never carry one: act_outline Ch15), slides off the bottom of the water-steps. **Merel** is in the stern with the pole, in wedding red. **Tobin's body** is on the deck, and before she pushes off she pulls the bridal cloth from her shoulders and lays it over him, without a word (Ch15's "under Merel's bridal cloth"). Liss is beside him. Kerrid comes down the last step and onto the deck. **He is the last one on** (act_outline; kerrid.md).
- **L02 (C):** the hero image. Merel sets the pole and pushes, and **the barge moves on still water**. From low behind the stern: a wake opens, a V of ripples spreading across the mirror, and the bowl-domes' reflections **break apart** into wobbling gold (color script `ch14`: "the escape barge's wake is the first moving water in the city"). It is the first ripple in four hundred years, and it is beautiful.
- **L03 (E, input):** *"Hold to pole"*: the player takes three strokes with Merel (one held input per stroke, the same widget family as the Ebbing and the farewell-tide). It's no minigame: each stroke sends a new ring across the lagoon. The player makes the ripples.
- **L04 (C):** **the bells.** Somewhere in the city a bell starts, then another, then every bell in Ansedra: the stirring bells, hung on every dome to ring if the lagoon ever moved, and they haven't rung in four centuries. (Narrative: a line of lore for the codex, M4-A2P-008.)
- **L05 (C):** **the city at its windows.** Wide over the water: in every dome and house along the lagoon, windows light up one after another, and people come to them and look out at the water moving. They are not shouting or pointing. They just watch the water move as if it were weather from a story. (Rendering: window-light instancing, M4-A2P-044.)
- ~0 words (the bells and the water carry it).

### B08. Merel at the gate (C, 1.5 min)
- **L06:** the court's **water-gate** behind them, two red posts and a lintel with the lacquered drop-gate held up by a counterweight. The barge is through it. Merel steers the barge alongside the gate post, and Rhen, nearest, takes the pole from her without being asked (he poled every hull in Oruvel).
- **L07:** Merel steps off onto the gate's footing.
  - Rhen: *"Merel. Get on."*
  - Merel (looking at the cloth on the deck, not at them): *"If the gate stays up, they're on you before the mouth. I can drop it. You can't, from there."*
  - Liss, from beside Tobin, the only thing she says to her: *"Merel."*
  - Merel: *"I know. I know. Go."*
- **L08:** she knocks out the counterweight pin, and the lacquered gate drops into the water with a sound like a door in a temple, throwing up the biggest wave the city has ever seen. The barge rides it out onto the lagoon.
- **L09:** through the gate's slats, from the barge, at distance: Stillguard come down the water-steps. Merel stands at the gate post and doesn't run. Her **father's Stillguard** take her by the arms. (Warden Dask himself, a living Warden and no Conclave member (bible §6), is on the steps behind them; he never comes down to her. Narrative may give him one line or none.) She is still in wedding red, and in the last of the dusk the player sees the dark mark on her sleeve: Tobin's blood. **Rule 5:** the camera holds on it from the barge, and nobody on the barge looks away. Rhen keeps poling. He has to. Sets `ch14_merel_taken`. ~45 words.
- `@music silence` on L09's end. The bells go on, far off.

### B09. Boss: Warden Malcor Venn (P, ~8 min)
See §5.

### B10. Left standing (C, 1.5 min)
- **L10:** the pursuit barge dead in the water, its flat-engine split and dark, its paddles slack. **Malcor Venn** stands on its raised poop, alone among his fallen Stillguard (withdrawn and wounded, not dead: §5), as the bridal barge drifts away from him. **The water around his barge is moving now**, ripples from the fight and the gate's wave still crossing the lagoon. He watches them go. He doesn't call after them or curse. **Rule 2:** he is a man standing on a wrecked barge, nothing more.
- **L11:** the bridal barge slides out between the lagoon mouth's two white stone moles into the open sea. Behind it Ansedra's windows are still lit and the bells are still ringing. Ahead it is dark. No lamp may be struck (wedding barges carry none, and nobody dares light one now).
- **L12:** close on the deck: the bridal cloth over Tobin, red in the last light, and Liss sitting beside it with her knees up and one hand flat on the cloth. Kerrid stands at the stern behind them all, looking back at the city, last as always. Fade. `unlamped` (Ch15's loop) enters on its first bars. Sets `ch14_complete` (the flow hands off to Ch15).
- No dialogue.

---

## 3. Flags

Declared in `game/data/flags.tres` when the gate passes (M4-A2P-014 adds them). The greybox's flag for the court (M4-C14-02) stays as it is.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch14_started` | B01 | flow | — |
| `ch14_spoke_with_tobin` | B01 (optional) | Ch15, Ch17 | **Ch15:** at the supper (Ch15's side scene) Liss's father asks Rhen what Tobin said, and Rhen can tell him: *"He said nobody had to be chosen. He volunteered."* **Ch17:** the dock-master breaks his silence on that line |
| `ch14_vows_spoken` | B02 | Ch15 | Liss, on the barge, says the vows back to herself once ("I'll learn your quiet") |
| `ch14_declared_heretics` | B03 (critical) | shops, shrines, NPC barks, status menu (plan §4.2; M4-A2P-031, M4-A2P-082) | **The heresy state** for the rest of Act II: Order shops refuse, Order shrines go dark and refuse, the party's title reads "Outside the Level" |
| `ch14_toma_refused` | B04 (critical) | Ch15, Ch20 | **Ch15:** in his confession Toma says he didn't answer his commander's "Be level"; **Ch20:** the Cage-Wardens' fight, where Toma holds the line |
| `ch14_tobin_killed` | B05 (critical) | Ch15, Ch17, the codex | Tobin's codex page; Ch15's whole chapter |
| `ch14_steps_held` | B06 | Ch15, Ch21 | **Ch15:** Kerrid's confession: "I held a stair again. At a wedding." (one line, if Narrative keeps it); **Ch21:** the stair motif |
| `ch14_merel_taken` | B08 (critical) | Ch15, Ch18, the Ending | **Ch18:** an optional revisit of Ansedra learns what became of her (Narrative's call: she lives, held in her father's house) |
| `ch14_engine_broken` | B09 phase 1 | Ch17 | Liss asks the Kite's engines not to forgive her for breaking that one. Narrative, keep or cut |
| `ch14_venn_beaten` | B09 | Ch19 | Venn is fought again, openly a revenant, in Act III (ADR 0016: revenants are first fought openly in Ch19) |
| `ch14_complete` | B10 (end) | flow (Ch15 gate) | — |

**Act II flags this chapter reads** (Ch13 to confirm): `ch13_ethren_bound`, `ch13_archive_read` (proposed), `ch13_pact_of_silence` (proposed).

---

## 4. No side scene

act_outline Ch14: "No side scene; the chapter runs straight on." The only optional content is Tobin's talk in B01 and the court's barks. SPEC §3.6's side-scene rule applies to major towns, and Ansedra's is Ch13's (Ysolde shows Rhen Corran's house).

---

## 5. The fights

### 5a. Set piece: the water-steps (B06)
**The design default** (act2_plan §2 Ch14, design default (b), accepted by the Lead 2026-10-30): a short objective battle in ADR 0100's schema, before the barge escape. The party must hold the water-steps while Merel cuts the bridal barge's mooring lines and gets it off the bottom step.

**Why a fight here:** the trap has to cost the player something they *do*, not only something they watch. And Kerrid holds the water-steps (act_outline), so the player holds a stair with him, at the water, the shape he died in, without the player knowing that yet. In Ch15 it becomes legible.

| Key | Value |
|---|---|
| `id` | `ch14_water_steps` |
| `scripted` | true (no Escape) |
| `objective` | `{ward: "merels_knife", quota: 4, outcome: "scripted_escape"}` |
| `entries` | `merels_knife`: side party, role `ward`, agility 4, skill `cut_the_lines` (each acted turn is one line cut; four lines). `stillguard_reserve`: side enemy, role `tide`, agility 10, summons a Stillguard every 2nd turn, cap 3 |
| Opening foes | 2 `stillguard` (Act I's rig, re-skinned at court: red lacquer, round shields) and 1 `stillguard_officer` (a buffer: Bulwark on allies) |
| `locked_active` | `kerrid`, `toma` (`locked_key`: "Holding the steps") |
| `attack_override` | `kerrid` → `hold_the_steps` (a new party skill: covers the ward until his next turn, like Ch8's Hold the Stair; the rhyme is the point) |
| `unavailable` | `liss` (`unavailable_key`: "With Tobin") |
| Party lends | `stand_fast` (as Ch8; always a lawful action) |

**Rules:**
1. **The Stillguard are not killed.** Every Stillguard foe uses `withdraws` on its last HP band: it falls back up the steps wounded, never felled. These are Toma's old comrades and decent soldiers following orders. The battle log says "falls back", never "is defeated". It counts toward nothing but the field. The quota is the only win.
2. **Their grip skills target the ward** (`seize_the_bride`, telegraphed one turn, as Ch8's Reach for the Stair): they are trying to stop Merel, not kill the party. Kerrid's `hold_the_steps` and Toma's Provoke are the role answers.
3. **The commander doesn't fight.** He stands at the top of the steps and doesn't come down (B04's refusal stands between them).

**Balance:** the Ch8 set-piece curve (`scripted_escape` counts as a win): naive 20–60%, role_answer ≥ 92%, smart ≥ 97%. It is short (4 Merel turns), and it shouldn't be the hard fight. B09 is.
**Music:** `lagoon_escape` part 1 under the fight (the escape has begun; it isn't a boss).

### 5b. Boss: Warden Malcor Venn (B09)
**Lore justification (SPEC §6.7):** the Conclave's pursuit barge carries a bound Lit Age **flat-engine** that pulls the water level and still (ansedra.md; flat_engine.md): the same craft that keeps Ansedra's lagoon a mirror, turned on fugitives. It is bound glimmer, which the Order forbids, and it's the Archive's ledgers made into a weapon (the player can read the irony; nobody says it).

**Arena:** `ansedra_lagoon_escape` (env-art, M3-ENV-721). The party stands on Merel's bridal barge (deck at y 0), out on the dark lagoon. The pursuit barge lies alongside on the enemy side, with the flat-engine at its stern. Venn is at the near rail (`BossAnchor`). Behind: the domes and the city's lit windows; the bells far off.

**The design default (d)** (accepted): the flat-engine is a **breakable part** on the pursuit barge, not its own combatant, with an `entries` row for its slow pulse so the timeline shows it (pillar 4).

**Phases (two):**
1. **The still water (100%–60%; ends when the engine breaks).** Venn commands from the poop with two Stillguard archers on the pursuit barge's rail.
   - **The flat-engine's pulse:** an entry row `flat_engine_pulse` (side enemy, role `tide`, agility 6). Every pulse the paddles press down, the ripples round the bridal barge die, and the field rule gives **Slow** to the party side for a turn. The timeline visibly stretches; the water goes glassy in the shot.
   - **The engine is a part** (`break_parts`, M3-CRE-637's `EngineBroken` mesh). Only **Liss** can break it, with a lent skill `strip_the_drum` (a charge skill, one turn's telegraph on the timeline, which the part rule needs: M4-A2P-023). Others' hits on the drum do nothing but chip it.
   - **Liss's grief, in the fight:** she isn't `unavailable` here: she *wants* this machine. When her charge lands, the battle plays her bark over the hit: *"Drum seam. Left. Hinge pins, out. She's bound, she'll fight you—"* (her tell: narrating the work instead of the grief). On the break: the drum splits, the window goes dark, the paddles fall slack, the pulse row leaves the timeline, and **the water moves again**: ripples come back round both barges, and the domes' reflections break apart behind (the arena's water reacts: M4-A2P-047).
   - Breaking the engine ends phase 1 whatever Venn's HP.
2. **The boarding (to 0%).** Venn crosses to the bridal barge (stem 2 enters on the boarding). He fights as a living-seeming man: a heavy halberd, disciplined, with a tactician's buffs (he Slows a target with a "settle", a measured strike that pushes the struck hero back on the timeline) and a parry stance that punishes physical spam (Ysolde's magic and Pell's learned skills are the role answers).
   - **Rule 2:** he bleeds like a man, staggers like a man, and doesn't regenerate, glow or speak strangely.
   - Lines (combat barks, ~20 words): *"Lay down the pole."* / *"You were guests."* / at 25%: *"Enough."*
   - **At 0%** he doesn't die: he is driven back over the rail onto his own crippled barge, and the barges drift apart (a scripted end, the battle's `victory_key`: "The barges part"). That is B10.

**What it teaches:** a field that slows the whole party, and a part only one hero can break. Swap Liss in, protect her charge, and then the fight changes. Pillar 4 holds: the pulse is on the timeline, and the charge is telegraphed.

**Balance:** the Act II boss band (naive ≤ 3%, role_answer 55–80%, smart 70–90%, p90 ≤ 80) on the Ch14 loadout (M4-A2P-019). `scripted: true` (no Escape).

**Music:** `malcor_venn` (two stems; not yet written, M4-A2P-092): stem 1 still and pressing (the water flattening); stem 2 enters on the boarding, with percussion. Phase rows in music.json with the encounter.

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `peace_wedding` | B01 (court loop), B02 (ceremony) | Zone/ceremony loop (exists, M3-AUD-842: 130.9 s) | — |
| `peace_wedding` **break** | B03 | **Not yet written** (act2_finals.md: "the break at the trap is a later cue"; M4-A2P-090) | The ceremony's melody stops mid-phrase on Venn's first word, not on a cadence. Under it, a held low string at the edge of hearing for the length of the declaration, then nothing. The break must sound like a held breath, not a sting. |
| `silence` | B04, B05 | — | Court noise only: shuffling, a shield set down, the hull-captains, one cry. Tobin's death has **no music**. |
| `lagoon_escape` | B06 (part 1, under the set piece), B07 (part 2), B08 (part 3) | **Not yet written** (~2 min, M4-A2P-090) | Part 1: urgent but low; the Order's hum (ORDER_HUM) broken up and turned rhythmic. Part 2: **the first ripple**: the first open, moving music in Ansedra, a slow wide melody with a pulse like poling. The bells come in as a diegetic layer, pitched to the cue's key. Part 3: Merel at the gate; the melody thins to one line and stops when the gate drops. |
| `malcor_venn` | B09 | **Boss, two stems** (not yet written, M4-A2P-092) | Stem 1 (the still water): pressing, flat, metronomic, the engine's paddle-press as the pulse. Stem 2 (the boarding): percussion and low brass-like synth, a man's fight. |
| `unlamped` | B10 (first bars) | Zone loop (exists, M3-AUD-843) | It begins as Ch14 ends. |

**SFX:**
- `stirring_bells` (every bell in Ansedra at once, far and near, a new set: one hero recording synthesised at several pitches);
- `water_gate_drop` (the lacquered gate into the water: temple-door weight and a wave);
- `pole_stroke` (the bridal barge, each stroke's ripple audible on still water);
- `level_pin_ring` (one silver pin on stone);
- `flat_engine_press` (the paddles: creatures' SFX exist for the engine, M3-AUD-849: confirm the press and the break).

---

## 7. Camera shots by beat

New shot ids for `ch13/ansedra_lacquer_court` and the lagoon (to add to ansedra.md).

| Id | Shot | Lens / note |
|---|---|---|
| W01 | The court filling at dusk; the hull-captains among the silk | 24 mm, high wide |
| W02 | Rail through the court (the free walk) | rail |
| W03 | **The mirror:** the court, the dais and the domes doubled in still water | 24 mm, low over the water; roughness-0 mirror |
| W04 | Sefir officiating | 50 mm; **no idle motion on him** (his breathing is absent: sefir_aurane.md) |
| W05 | Tobin and Merel at the water's edge; the cord passed hand to hand | 85 mm two-shot, insert on the cord |
| W06 | Liss in the front row; Rhen bumping her shoulder | 50 mm |
| W07 | The Conclave's gallery: four figures standing at once | 35 mm, low from the dais |
| W08 | Venn at the rail reading | 85 mm; **plain coverage, no low angle, no strange light: rule 2** |
| W09 | Liss turning to look at Sefir | 85 mm |
| W10 | Sefir to Asha; Asha's "No." | 50 mm over-shoulder pair |
| W11 | The commander at the dais foot; Toma with his shield up | 50 mm two-shot, then Toma single (hold on the silence) |
| W12 | Ysolde's pin falling; insert on the pin on the slabs | 85 mm, then insert 100 mm |
| W13 | Merel at the guards | 35 mm, handheld energy |
| W14 | Tobin sitting down on the slabs | 50 mm; **wound framed out; no slow-motion** |
| W15 | Liss's hands on him; Toma lifting her away | 50 mm |
| L01 | The barge off the bottom step; the bridal cloth laid over him; Kerrid last onto the deck | 35 mm |
| L02 | **The hero frame:** low behind the stern, the wake opening, the domes' reflections breaking | 24 mm, low over the water |
| L03 | The player's three strokes | 35 mm from the bow looking aft |
| L04 | A dome's bell swinging | 85 mm insert |
| L05 | **The city at its windows:** wide over the water as windows light along the lagoon | 18 mm, high |
| L06 | The water-gate; Rhen taking the pole | 35 mm |
| L07 | Merel on the gate's footing; the barge alongside | 50 mm |
| L08 | The gate dropping, the wave | 24 mm |
| L09 | **Through the gate's slats from the barge:** Merel taken; the sleeve | 85 mm, held; **nobody on the barge looks away** |
| L10 | Venn standing on his dead barge in the ripples | 50 mm, at the barge's height; **plain** |
| L11 | Out through the lagoon mouth's moles; the lit city behind, dark sea ahead | 24 mm, from astern then ahead |
| L12 | The cloth, Liss's hand on it; Kerrid at the stern | 50 mm, then fade |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B02 | W03 → W04 → W05 → W06 | W03 holds ≥ 5 s. The mirror must be unbroken: nothing moves on the water. |
| B03 | W07 → W08 → W09 → W10 | The music breaks on Venn's first word. |
| B04 | W11 → W12 | The pin's ring is the only sound after Ysolde's line. |
| B05 | W13 → W14 → W15 | Fast cuts. No slow-motion anywhere in the chapter. |
| B07 | L01 → L02 → L03 → L04 → L05 | L02 is the chapter's hero image: hold ≥ 6 s. L05 holds until the far windows are lit. |
| B08 | L06 → L07 → L08 → L09 | L09 is the cost: hold it, from the barge, at the barge's distance. |
| B10 | L10 → L11 → L12 → fade | — |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 (talk, barks, optional) | 235 |
| B02 | 70 |
| B03 | 110 |
| B04 | 55 |
| B05 | 30 |
| B06 (set-piece barks) | 30 |
| B07 | 0 |
| B08 | 45 |
| B09 (combat barks) | 40 |
| B10 | 0 |
| **Total** | **~615 written** (~450 on a path without Tobin's talk and the optional barks) |

**Against SPEC §3.6:** at ~33 min, Ch14 is about 2% of the game, so its fair share is **800–1,200 words**. It sits under the band on purpose: the trap is fast, Tobin's death has one line, and the escape is wordless. Ch15 carries the act's longest speech.

---

## 9. Requests to other roles

### Rendering (M4-A2P-047, M4-A2P-044)
1. **The still mirror** (W03, B01–B05): the lagoon at roughness 0 with an exact reflection; not a single ripple until L02.
2. **The first ripple** (L02, L03): a wake V and stroke rings that propagate across the mirror and break the domes' reflections apart. Each pole stroke is a ripple source. The gate's drop (L08) is the biggest ring.
3. **The flat-engine's press** (B09): the ripples round the barges die on each pulse (the water re-flattens in a ring from the engine) and come back on the break.
4. **The city's windows** (L05): window lights coming on along the lagoon in a wave, instanced, warm, far.
5. **No revenant tell on Venn** anywhere in the chapter (rule 2): not the still-actor water branch (M3-RND-03), and no reflection rule. His reflection ripples like anyone's.

### Art (color script)
1. `ch14` is validated for the court; confirm the **lagoon at night** after the sun sets (B09, B10: the red band gone, the city's windows the only warm lights, `glimmer_held` sea-glow 0.08).

### Environment Art (M4-A2P-044)
1. The kit exists (M3-ENV-721). Place the court per ansedra.md's composition notes, plus:
   - the Conclave's gallery with a rail;
   - wedding dressing (cords, hangings in both families' colours);
   - the hull-captains' place;
   - the water-gate with a working drop (an animated prop);
   - the bridal barge at the bottom step;
   - the lagoon mouth's two white moles.
2. A bell on each dome (a swinging prop) and the windows (above).

### Character Art (M4-A2P-050, M4-A2P-051)
1. **Tobin and Merel** in wedding dress: Tobin's Saltwright coat with the Warden's red sash; Merel in wedding red. Merel needs a **bloodied-sleeve** variant for L09. The knotted wedding cord is a hand prop.
2. **Malcor Venn**: field, cutscene and battle actor. A living-seeming man (rule 2), with a halberd and a battle clip set.
3. **Stillguard at court** (Act I's rig re-dressed), the **old commander**, **Warden Dask** (no lines required), the hull-captains (Saltwright crowd set), Order dignitaries (Ansedran crowd set).
4. **Ysolde's hair** partly down from W12 on (ysolde.md: a costume state that persists).
5. **Animation:**
   - Tobin's sitting-down fall (simple, unheroic);
   - Liss's hands-on-the-wound and fighting Toma off;
   - Toma's one-armed lift;
   - Merel's poling and the gate pin;
   - the Stillguard's withdraw (falling back wounded, not dying).

### Audio (M4-A2P-090, M4-A2P-092)
The cues in §6: the break, `lagoon_escape`, `malcor_venn`; the bells; the gate.

### UI
1. The poling input (L03): the held-input widget, three strokes.
2. The set-piece HUD (M4-A2P-083): the ward's count of lines cut (4), the locked-swap reason "Holding the steps", Liss "With Tobin" in the formation.
3. The heresy state from B03 (M4-A2P-082): the status menu's party title, and the shops and shrines refusing.

### Combat (M4-A2P-014, M4-A2P-023)
§5 in full: the set piece's rows (`merels_knife`, `cut_the_lines`, `hold_the_steps`, `seize_the_bride`, `stillguard_reserve`, `withdraws` on every Stillguard); the Venn encounter with the flat-engine's part and pulse entry, Liss's `strip_the_drum`, and the boarding phase.

### Systems / Chapters (M4-A2P-014)
1. **Speakers:** `tobin`, `merel`, `malcor_venn`, `commander_hale` (or as named), `hull_captain`, `warden_dask` (if he speaks).
2. **Party steps:** Liss `unavailable` in B06 only; Merel a guest entry in B06.
3. The heresy flag's readers (plan §4.2).
4. The barge's `barge` trigger runs B07.

### Cinematics (reviewer)
Check §0's rules against every shot, especially:
- W08 and L10 (Venn plain, nothing strange);
- W14 (no slow-motion; wound framed out);
- L09 (held, from the barge, nobody looks away);
- the whole chapter: no capture, nothing underground, no rite on anyone.
The poling input's pacing and the bells' build are yours.

---

## 10. Open questions for review

1. **"Outside the Level"** as the heresy's formal words (B03) is a proposal in our own idiom. Narrative may coin a better one; check it against the banned-terms list (the inspiring game's words for its church's heretics must not be echoed).
2. **Names proposed here:** Commander **Brannoc Hale** (Toma's old commander) and Warden **Dask** (Merel's father, a living Warden). Both are checked against `tools/banned_terms.txt`. Narrative may rename them.
3. **The set piece (B06)** is design default (b). If Combat finds the chapter too fight-heavy with B09 behind it, the steps can become a cutscene with Kerrid's last-onto-the-barge kept. The rhyme with Ch8's stair is the reason to keep it.
4. **What happens to Merel** is left for Act III (`ch14_merel_taken`). Narrative decides; this sheet's suggestion is that she lives, held in her father's house, and the Ch18 revisit can find her.
