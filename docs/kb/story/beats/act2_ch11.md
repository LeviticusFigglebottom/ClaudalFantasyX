# Act II Beat Sheet: Ch11 "Lowlight" in the Sunken Vey and its half-drowned temple, midday (M4)

**draft: pre-gate.** Written ahead of the Act I gate as ADR 0203 preparation (the Lead's assignment and order, 2026-10-30: Ch10, Ch14, Ch15, then Ch11–13 and Ch16). Docs only: no `.dlg`, flag or data exists for anything below until the gate passes and M4-C11-01 is reviewed.

Owner: Narrative (M4-C11-01; drafted by the act2-plan track). Reviewer: Cinematics (SPEC §12.3).
Sources:
- [act outline Ch11](act_outline.md);
- ADRs: [0015](../../decisions/0015-vowbound-element-temple-order.md) (nothing frozen), [0016](../../decisions/0016-act-two-restaging.md) (no founders' records here);
- [vowbound.md §5 (Nhoa)](../vowbound.md), [bible §7 (the Saltwrights), §8 (the Kirru)](../bible.md), [voice guide](../voice_guide.md);
- the characters: [Pell](../characters/pell.md), [Liss](../characters/liss_varrow.md), [Rhen](../characters/rhen_sallow.md);
- the Act I set-ups: [act1_ch06.md](act1_ch06.md) B07 (Liss reads the lantern), [act1_ch08.md](act1_ch08.md) B05 (Rhen's stopped "My—", Wenna's first mark);
- art: [color script `ch11`](../../art/color_script.md), [lowlight.md](../../art/environments/lowlight.md) (kit, shots L01–L05, the housing-mark), [lamp_engine.md](../../art/creatures/act2/lamp_engine.md), [conduit_crawler.md](../../art/creatures/act2/conduit_crawler.md), [vowbound/nhoa.md](../../art/creatures/vowbound/nhoa.md);
- tasks: M3-ENV-719 (the mark on Rhen's lantern);
- the plan: [act2_plan.md §2 Ch11](../../plan/act2_plan.md) (design default (a): the sanctum is walked to a ledge and seen underwater).

Previous chapter: [act2_ch10.md](act2_ch10.md). Next: Ch12 "The Cold Road".
Greybox: M4-C11-02:
- `ch11/sunken_vey`: the landing, gallery roofs, the conduit court with `conduit_mark`, the side gallery to `fig_end`, `to_lowlight`;
- `ch11/lowlight`: the atrium's `lamp_bench`, EngineHall, the well-shaft's two flights, the sanctum `nhoa`, `to_vey`.

Fights: M4-C11-03 (`gallery_ray`, `rime_urchin`). ADR 0204 (the Lead's answers, 2026-10-30) applies; §8 is used in §5.

Scripts: none yet (M4-A2P-002). Sample lines set the voice only.

**The rules this chapter must keep:**
1. **Nothing is frozen** (ADR 0015). The cold is the deep's: cold haze, colour and stillness. No ice, frost, snow imagery or frozen surface, in the zone, the fights or Nhoa.
2. **No truth of the ritual here** (ADR 0016). No founders' records, no ledgers and no Cantor roll: those are Ch13's Archive. Lowlight's revelation is personal: Rhen's father, and Pell's sister.
3. **Bound light is still** (color rule 2). The conduits, the Engine's lamps and Nhoa are `glimmer_bound`: steady, never flickering, never drifting. Only what is **released** from the Engine rises (the second upward lift, after Ch10's).
4. **Pell says nothing for a full scene** before his sister (act_outline). Not one line from the moment he kneels until the binding is over.
5. **Rhen admits it himself.** Liss reads the mark, and she asks. The admission is Rhen's, not something forced out of him.

---

## 0. The chapter in one paragraph

The Sunken Vey is a Lit Age gallery town drowned to its second storeys, standing in a still turquoise lagoon under a grey noon. Copper conduits still run along every cornice with bound light in them. In a conduit court Liss stops at a housing and reads a Saltwright mark stamped in its copper: a circle, three slanted lines, two seats side by side, pair-built. It's the same make as the lantern Rhen has carried since Oruvel. She told him on the Shoals it was wright work. Now she asks him straight, and he tells her: his father was Dace Sallow. To Liss, Dace is a legend of her people, the wright who went into the Undertow to fix it, and Rhen has been hiding his name in his sleeve for three chapters. She is furious. In Lowlight, the temple half underwater, a machine is still trimming its lamps for a congregation that drowned four hundred years ago: the Lamp Engine, full of bound dead. When the party breaks it open, the light in its core rises, the second time they have seen the dead go up. Down the well-shaft, where the deep's cold wells up and drowned light sifts down through it like silt, Asha finds the Vowbound she has come for, and Pell, behind her, sees whose name is carved on the shell at its throat. It's Ressa's. He kneels in the water and says nothing for the whole binding. Afterwards, at the lamp bench, Rhen and Liss repair a broken lamp together without a word, and that is the start of their truce.

**Emotional line:**
1. grey wonder (the drowned galleries);
2. recognition (the mark);
3. confession and anger (Rhen and Liss);
4. awe at a machine that keeps (the Engine);
5. a second rising, noticed now;
6. descent into cold;
7. the worst recognition (Pell);
8. silence;
9. a truce made with hands.

**What the chapter must prove:**
- Rhen's Saltwright blood admitted, paying Ch6 and Ch8;
- the fourth Vowbound, bound, with the verse-sleeve at **S4**;
- Nhoa as Ressa, and Pell's silence;
- the Engine's release as the second upward lift, linking the act's motif;
- the Rhen–Liss truce begun.

---

## 1. Running order

Time is in-world (one midday into the afternoon). Minutes are a first-time player's. Modes:
- **P**, play;
- **C**, cutscene;
- **E**, in-engine scene with player input.

Shot ids: L01–L05 are lowlight.md's composed shots; the rest are proposed in §7 (V = the Vey, T = the temple, N = the sanctum).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The drowned galleries** | `ch11/sunken_vey` landing | 12:00 | C | 1.0 | L01, V01 | `sunken_vey` | Silent, gorgeous, dead: a town of light nobody uses. | `ch11_started` (exists) |
| B02 | **The galleries** | `ch11/sunken_vey` | 12:05 | P | 8.0 | V02, V03 | `sunken_vey` | Gallery walks over still water; the fig-choked side gallery; fights. | `ch11_found_fig_cache` (optional) |
| B03 | **The housing-mark** | the conduit court (`conduit_mark`) | 12:40 | E | 3.0 | L03, V04–V07 | `sunken_vey` → `silence` | **Rhen admits he is Dace's son.** Liss is furious. | `ch11_rhen_admitted` |
| B04 | **Lowlight** | `ch11/lowlight` atrium and nave | 12:50 | P | 5.0 | L02, T01 | `lowlight` | A temple still kept by a machine: every lamp trimmed and dark. A second of Wenna's marks. | `ch11_found_wenna_mark` (optional) |
| B05 | **The Engine** | the engine hall's stair head | 13:15 | C | 1.0 | L05, T02 | `lowlight` → `lamp_engine` | A lamp-stand the size of a chapel, still trimming. | — |
| B06 | **Boss: the Lamp Engine** | `lowlight_engine_hall` (arena) | 13:16 | P | 8.0 | battle | `lamp_engine` (p1 → p2 `opened`) | Break what keeps them. | `ch11_engine_released` |
| B07 | **Twice** | the engine hall | 13:30 | C | 1.0 | T03, T04 | `silence` | The core's light rises. Someone says "twice". | — |
| B08 | **The well-shaft** | the shaft's two flights | 13:35 | P | 3.0 | L04, N01 | `lowlight` (stripped, deeper) | Descent into the deep's cold; silt-light sifting. | — |
| B09 | **Nhoa** | the drowned sanctum's ledge (`nhoa`) | 13:45 | C | 4.0 | N02–N09 | `nhoa_bound` (sting) inside a bed of `lowlight` | Pell sees his sister. The binding. Silence. | `ch11_nhoa_bound`, `ch11_pell_knelt` |
| B10 | *Side scene: "The Lamp Bench"* (optional) | the atrium (`lamp_bench`) | after B09 | E | 3.0 | T05 | `silence` (conduit hum) | A truce made with hands. | `ch11_lamp_repaired` |
| B11 | **"Held. By you now."** | the Vey's mouth, leaving | 16:00 | E | 1.5 | V08, V09 | `sunken_vey` (dusk, sparse) | Asha's question to Pell, answered a scene later. | `ch11_complete` |

**Totals:** critical path **36.5 min** (all but B10). With B10, **39.5 min**. Split: **24 min playable (66%)**, 7.0 min cutscene, 4.5 min in-engine.

**Cut order if the chapter runs long:**
1. B02 drops the side gallery.
2. B04 shortens to the nave walk.
3. B08 becomes one flight.

**Never cut:** B03, B07's "twice", B09 in full (the outline: Pell kneels "for a full scene"), B11.

---

## 2. Beat detail

### B01. The drowned galleries (C, 1 min)
- **L01:** the hero frame (lowlight.md): on the water at the Vey's mouth, the drowned arcades receding in perspective, white ceramic gone green at the waterline, strangler figs splitting the piers. Copper conduits run along every cornice, lit with steady bound teal (`glimmer_bound`), reflected long in water so still that no wind reaches it. At the end, the temple's broken vault. A grey noon (color script `ch11`).
- **V01:** the party on the landing. Liss is looking at the conduits the way other people look at a sunset.
  - Liss: *"Four hundred years and she's still lit. Nobody's touched her. Look at her."*
  - Pell: *"Many in there."* (He hears the bound dead. Nobody follows it up.)
- ~20 words.

### B02. The galleries (P, 8 min)
- **The zone:** gallery walks and bridges over still water between the arcades (the greybox's railed roofs; the kit's `vey_gallery_bridge`, `vey_gallery_walk_6m`), with drowned pillars below.
- **Systems:**
  - random encounters (M4-C11-03: `gallery_ray`, `rime_urchin`). The rays glide out of reach every other turn, and the urchins' rime spines punish melee (rule 1: the rime is the deep's cold on a spine, never frost on the world);
  - a save shrine on the landing (an Order shrine, old: Ch14's heresy hasn't happened);
  - one chest at the fig end.
- **Optional:** the side gallery to the **fig end**, a strangler fig that has split a gallery and holds a Lit Age lamp in its roots like a nest (a chest: `ch11_found_fig_cache`). Pell, if in the party, won't go near it: *"Held. In the roots. Like the fen."*
- **Barks** (~80 words):
  1. Ysolde, at a conduit: *"Lamptongue on the brackets. 'Kept for the gathering.' The gathering has been under water for some time."*
  2. Toma, at a drowned doorway: *"People lived here. The Order says the Lit Age were a wicked people."* (A pause.) *"They had window boxes."*
  3. Rhen, at a submerged stair, a diver's itch: *"I could have half this street up in a season. Good salvage."* Liss, not looking at him: *"You could have."*
  4. Asha, looking down into the water where conduit light lies on the drowned floor: *"Nobody comes to lift them."* (Since Ch10 she sees it.)

### B03. The housing-mark (E, 3 min)
- **L03:** the conduit court: a square of drowned arcades round a lit copper conduit at chest height, its housing green with verdigris. Liss stops dead at the housing and wipes the verdigris off it with her sleeve. **The mark** (lowlight.md §1; M3-ENV-719), stamped in relief in the copper: a circle crossed by three fine parallel lines slanted 30°, the Saltwrights' camp-sign, with two small round seats side by side under it. Pair-built.
- **V04:** Liss looks at it. Then she looks at **Rhen's lantern**, at the brass collar, where the same mark sits small (M3-ENV-719). She holds out her hand for it. Rhen hesitates, then gives it to her.
- **The scene** (~150 words; rule 5: Liss asks, Rhen answers):
  - Liss (reads `ch06_liss_read_lantern`): *"I told you on the shoals it was wright work."* She turns the collar to the conduit light. *"Same hand. Same seats. Pair-built. This mark's older than you. Whose is it?"*
  - Rhen, the old deflection, not quite working: *"Told you. Somebody who liked oil."*
  - Liss: *"Don't."*
  - (A beat. Rhen's short line when it matters: voice guide.)
  - Rhen: *"Dace Sallow. My father."* (Reads `ch08_liss_found_marks`, set on the critical path: the "My—" he stopped at Coilspire.) *"I nearly said it at Coilspire."*
- **V05:** Liss, very still. To her, Dace Sallow is a legend of her people, the wright who went into the Undertow "to fix it" (liss_varrow.md). Then the anger comes, fast and clipped:
  - Liss: **"Your father built a ship nobody can fly. You hid his name in your sleeve. Real proud family, Sallow."** (The voice guide's sample, fixed.)
  - Rhen: *"I didn't hide it. Nobody asked."* Liss: *"I asked. On the shoals. I asked you whose it was."*
  - Rhen (the true thing, under the joke he can't find): *"He left. That's what I know about him. He went up the coast and didn't come back. You lot got the legend. I got a lantern on a hook."*
- **V06:** Liss shoves the lantern back into his chest, hard, and walks off down the gallery. She stops at the court's edge without turning round: *"He was the best of us. Everybody says. And you're sitting on his name like it's a debt."* Then she goes.
- **V07:** the others, who heard it all. Nobody says anything. Asha looks at the lantern in Rhen's hands, and her hand moves to the comb in her hair and stops. (**Watch,** ADR 0022 sweep-G B3: no line or caption here connects the lantern to the man who brought her the comb. Ch15's K17 is the first time it's voiced. Here it's a hand that moves and stops, nothing more.)
- Sets `ch11_rhen_admitted`. `@music silence` on V06. ~150 words.

### B04. Lowlight (P, 5 min)
- **L02:** the temple's nave, knee-deep (the party wades; Pell wades too here, since this isn't Kirru water), lamp-niche tiers going up both walls, **every lamp trimmed and dark**, the bronze trim-arms all at the same angle (lowlight.md: they're the Engine's work). The sanctum's steps at the north end, and under the floor somewhere a slow mechanical tick.
- **The atrium** with the **lamp bench** (`lamp_bench`): a Lit Age lamp-maker's bench, tools laid out, one salt-glass lamp in pieces on it. Liss passes it without looking. (B10 returns to it.)
- **Systems:** no random encounters in the temple (the Engine keeps it); one shrine at the atrium; one chest.
- **Optional: Wenna's second mark.** Behind a fallen trim-arm in a lamp niche: the same old-style lines and node-dots as Coilspire's, and the small key-shaped glyph (act1_ch08 B05). Liss, if found (sets `ch11_found_wenna_mark`), still angry, and so to Toma rather than Rhen: *"Same hand as Coilspire. Somebody went through every temple and left her name for us. Nobody ever looked."* (Vowbound.md §3: Wenna's trail. Liss doesn't know the name yet.)
- **The tick** gets louder toward the engine hall's stair.

### B05. The Engine (C, 1 min)
- **L05:** the engine hall's stair head, looking down: a square hall under a collapsed vault bay where a grey shaft of daylight falls on the water (−0.6, knee-deep), and in the water the **Lamp Engine**. A 3.4 m bell-hooded tower of twelve salt-glass lamps on three gimballed rings, on four short jointed legs, with two long trimming arms ticking, every lamp lit with steady bound teal (lamp_engine.md). It is turning its lamps toward the empty stair, where a congregation used to come down.
- **T02:** it turns every lamp toward the party at once, and brightens them in sequence, a held breath (its `cast`: the gathering).
  - Pell (very low): *"Twelve. And one more. In the middle."*
  - Liss, despite herself, professionally: *"She's beautiful."* (Then, harder:) *"Break her."*

### B06. Boss: the Lamp Engine (P, ~8 min)
See §5.

### B07. Twice (C, 1 min)
- **T03:** the Engine on its knees in the water, its rings folded back, its core's salt-glass globe cracked open. The bound light in the core **goes still, and then goes up.** A small lift of motes rises out of the broken globe in slow vertical spirals, turning `glimmer_lift` gold as they climb (color rule 1), up through the collapsed vault bay into the grey (the color script's 3 s warm grade lift, `lut_ch11_vey`). Only the core's: the dark rings' lamps let theirs go too, a mote or two from each. (Rule 3: what is released rises.)
- **T04:** the party watching, as in Ch10's B05. This time somebody says it.
  - Ysolde (reads `ch10_drowner_defeated`): *"That is twice."*
  - Asha: *"They were waiting. Inside it. All this time."*
  - Liss stands looking at the dead frame with her jaw tight. Every lamp in her own gear is the same kind of light (liss_varrow.md; she sees it and doesn't say it). (Act III's "Every lamp on this ship is somebody" starts here, unspoken.)
- ~20 words.

### B08. The well-shaft (P, 3 min)
- **L04:** the sanctum's floor opens on the **well-shaft**: a ribbed Lit Age shaft with a spiral stair going down into teal. The water in it is colder (a cold haze rising off it, rule 1). Drowned glimmer **sifts down through it like silt**: motes falling slowly through the column of water, held, settling (vowbound.md: "drowned glimmer sifts down through it like silt"). It is the opposite of what the party has just seen go up.
- **The walk** (design default (a), accepted): the stair's two flights go down past the waterline, wading, then chest-deep, to a **dry ledge** (the greybox's second flight ends at y −2). From the ledge, the drowned sanctum is **seen below, underwater**, through still clear water, lit by the underwater shader (M2-RND-02). No swimming field mode.
- **No fights.** Pell walks behind Asha without being told. His crest is flat.
- One bark, Rhen (still raw from B03, so his joke doesn't land and he knows it): *"Cold. Down here. Really cold."* Nobody answers.

### B09. Nhoa (C, 4 min)
- **N02:** from the ledge, looking down through the water into the drowned sanctum: a round chamber at the shaft's foot where the deep's cold wells up through the floor, silt-light sifting. In the middle of it, standing in the water as if in air, **Nhoa**: a tall Kirru-like figure made of held motes like silt hanging in deep still water, antlers of mangrove root, a long heron neck, bound light, perfectly still (vowbound/nhoa.md; rule 3).
- **N03:** Pell, at the back of the line, **stops**. The camera finds him before anyone else sees why. His crest goes all the way up. He hums the storm's note, very softly, and stops himself.
- **N04:** close: **the name-shell at her throat**: a carved spiral shell, the only solid thing on her, and the carving on it is a name (vowbound.md: "her own, carved"). The insert is the player's only cue. Pell's own shell is blank.
- **N05:** Pell comes forward through the others to the ledge's edge.
  - Pell (the voice guide's sample, the only words he speaks in the beat): **"She is here. She is not lifted. Do not speak yet. Please."**
  - **He kneels**, in the water at the ledge's edge, and from here **he says nothing** (rule 4). His hands are flat on the water. He doesn't look away from her. (He watched Ressa go into the sea seventy years ago and never turned his back; now he finds she never lifted at all. He didn't know: pell.md.)
- **N06:** Asha looks from Pell to Nhoa. She understands, or nearly. She looks at Pell a long time. Then she goes on with what she came for, because Pell said "do not speak yet", and the binding is how Cantors speak to the Saints.
- **N07 (the binding, ~90 s; the bind cinematic, M4-A2P-071):** Asha raises her staff over the water and sings the verse she knows so far, and below her the Saint turns its head up toward the light. Then the **fourth verse** comes up out of the water to her, sung back in Lamptongue by a voice that is very old and quite young, a Kirru voice in a human tongue (Audio: the `nhoa_bound` sting; rule 1: cold colour, no frost anywhere). The silt-light around Nhoa rises to Asha's staff and settles into her **verse-sleeve**: the embroidery grows to **S4**. Nhoa is bound to Asha.
- **N08:** the last thing before the light settles: Nhoa's head turns, once, **toward Pell**, kneeling. Bound light can't change its expression (rule 3). It only turns. Then it's still again.
- **N09:** Pell, still kneeling, still silent, as the others start back up the stair. Kerrid stays on the ledge behind him without a word until Pell stands. (The two outsiders again: act1_ch09 B09, act2_ch10 B10.) Sets `ch11_nhoa_bound`, `ch11_pell_knelt`.
- ~15 words in the beat (Pell's four sentences). Asha sings, and nobody else speaks.

### B10. Side scene (optional): "The Lamp Bench" (E, 3 min). See §4.

### B11. "Held. By you now." (E, 1.5 min)
- **V08:** late afternoon at the Vey's mouth, the conduits brighter as the grey light goes. Asha stops beside Pell on the landing. She doesn't ask about his day (her tell is stopping: voice guide).
  - Asha (she asked this at the ledge with her eyes; now in words): *"I didn't know. Pell. If I'd known—"*
  - Pell (the scene later; literal): *"She is not lifted. She is held."* (Beat.) *"By you, now."*
  - Asha: *"...Do you want me to let her go?"*
  - Pell: *"You cannot. Not yet."* (Act III pays it: he fights her and turns his back.)
- **V09:** Rhen and Liss: if B10 was played, they're walking together at the back of the line, not talking, and Liss has her shoulder near his. If not, they walk at opposite ends of the line, and the truce waits for Ch12. Sets `ch11_complete`.
- ~40 words.

---

## 3. Flags

Declared in `game/data/flags.tres` when the gate passes (M4-A2P-011 adds them). `ch11_started` and `ch11_reached_lowlight` already exist (M4-C11-02).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch11_found_fig_cache` | B02 (optional) | — | loot only |
| `ch11_rhen_admitted` | B03 (critical) | Ch13, Ch15, Ch17 | Liss calls him "Sallow" from here, until B10 (or Ch12) softens it to "Rhen"; Ch15's dock-master knows ("Liss says you're Sallow's boy") |
| `ch11_found_wenna_mark` | B04 (optional) | Ch13, Ch20 | Wenna's trail (vowbound.md §3): Ch13 is the third mark; at Ch20 Liss names the marks to Virel |
| `ch11_engine_released` | B06 | Ch16 | At the Choir, Asha: "Three times now, they went up." (with Ch10 and the farewell-tide) |
| `ch11_nhoa_bound` | B09 (critical) | vowbound.json (`bound_flag`), the summon menu, verse-sleeve S4 | Nhoa in Asha's roster |
| `ch11_pell_knelt` | B09 (critical) | Ch18, Ch20 | Pell's return to Reedhollow and his Nhoa fight |
| `ch11_lamp_repaired` | B10 (optional) | Ch12, Ch15, Ch17 | **Ch12:** Liss calls him "Rhen" on the pass; **Ch15:** she lets him sit with her at the bier (B02); **Ch17:** they restore the Kite's first lamp the same way |
| `ch11_complete` | B11 (end) | flow (Ch12 gate) | — |

**Act I/II flags this chapter reads:** `ch06_liss_read_lantern`, `ch08_liss_found_marks`, `ch10_drowner_defeated`, `ch10_farewell_tide_seen`.

---

## 4. The optional side scene: "The Lamp Bench" (B10)

**Where:** the atrium's lamp-maker's bench (`lamp_bench`), after the binding, while the others rest. **When:** after B09, through a marker on Liss, who has stopped at the bench this time and is looking at the broken salt-glass lamp on it. **Length:** 3 min, **~25 words**. **Speakers:** `liss`, `rhen`.

**Beats** (act_outline: "Rhen and Liss repair a lamp together in silence"):
1. Liss picks up the broken lamp's housing. Rhen comes and stands at the other end of the bench.
2. Neither speaks. She holds out her hand without looking: he puts the burner seat in it. She seats it. He holds the chimney while she turns the collar. The player does it with them: three **held inputs** ("Hold steady" / "Turn" / "Seat it"), the same widget family as Ch9 and Ch10, with no fail. The player is the steady hand.
3. The lamp is a Lit Age salt-glass lamp **with no bound light in it**: it's empty. Rhen, without asking, takes the **oil burner** off his own lantern's spare kit and fits it. (His lantern burns oil: decisions_log N-02. A wright's lamp with a diver's flame.)
4. Liss lights it with his tinder. A small warm oil flame in Lit Age glass, the only warm light in the drowned temple.
5. The only words: Liss, looking at the flame: *"Pair-built."* Rhen: *"Yeah."* (Two lamps that work together; two people. Nobody explains it.)
6. She leaves the lamp burning on the bench. Sets `ch11_lamp_repaired`.

**Rules:** no apology from either of them. Liss does **not** narrate the repair (her narrating is her grief tell, and it belongs to Ch14–15). Silence is the scene.
**Payoff:** `ch11_lamp_repaired` (§3).

---

## 5. The boss: the Lamp Engine (B06)

**Lore justification (SPEC §6.7):** a still-running Lit Age machine for keeping light, full of bound dead (lamp_engine.md). It isn't cruel; it keeps, still trimming its lamps for a drowned congregation. The Order calls the Lit Age wicked for building such things, and the Order's own Saints are made the same way (Ch13 makes the parallel explicit; nobody says it here).

**Arena:** `lowlight_engine_hall` (env-art, M3-ENV-716): knee-deep water on a stepped floor, a ring of piers, the grey shaft of daylight from the collapsed vault, the Engine's trimming rail round the walls. Staged ids (M3-BPR-419; M3-BPR-408 has its opening camera): enemy `lamp_engine`, phase `opened`.

**Phases (two):**
1. **The lamps (100–50%).** Three gimballed rings, four lamps each.
   - **The gathering:** a telegraphed charge (one or two turns: every lamp swings to face the target and brightens in sequence). It lands a heavy Glimmer blow and pushes the target back on the timeline.
   - **The rings are break parts** (lamp_engine.md's proposal; M3-CRE-623's notes: a charge skill per ring, and `Ring0..2`/`Broken` meshes). Each broken ring darkens its lamps (a mote or two rises from each: B07's foreshadow begins in the fight) and **shortens the gathering's charge-up**: fewer lamps, less light.
   - **The conduit crawlers** (`conduit_crawler`, a repairing add, M4-A2P-022; **ADR 0204 §8: two at the start, dormant**): two salt-glass shells on brass feet sit on the dais edge in front of the Engine's knees from the first turn, lit and still. When a ring breaks they wake, walk to the Engine's leg (`crawler_mend`), and **repair it** in two turns unless they're stopped. They ignore the party until the Engine is struck. They're fragile and evasive, so Rhen's speed and Ysolde's magic are the answer.
   - **Liss's answer:** her steal unseats a lamp from a ring (a smaller break), and her gadget can jam a crawler's repair (a Delay).
2. **The core (`opened`, below 50%).** The rings fold back like petals, and the cracked salt-glass core shows. The trimming arms strike faster, and the core is the weak point: **Kerrid's armour break** opens it, and heavy blows end it.

**What it teaches:** kill the adds that undo your work, then commit. Pillar 4: the crawlers' repair is a telegraphed timeline action, so the player always sees which ring comes back when.

**Balance:** the Act II boss band (naive ≤ 3%, role_answer 55–80%, smart 70–90%, p90 ≤ 80) on the Ch11 loadout (M4-A2P-019). Not `scripted`; Escape allowed.

**Music:** `lamp_engine` (two stems, rendered: M3-AUD-844); stem 2 on `opened`.

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `sunken_vey` | B01, B02, B03 (out), B11 (dusk, sparse) | Zone loop (exists, M3-AUD-840) | — |
| `lowlight` | B04, B05 (in), B08 (stripped, lower), B09 (bed under the sting) | Zone loop (exists, M3-AUD-841) | B08 wants a stripped, lower variant (a stem mute is enough). |
| `lamp_engine` | B06 | Boss, two stems (exists, M3-AUD-844) | — |
| `nhoa_bound` | B09 (N07) | **Sting**, ≤ 8 s (not yet written: act2_finals.md; M4-A2P-091) | The fourth verse's first phrase, sung back from below in a voice that is Kirru, very old and very young. Cold colour (high, thin, glassy timbres) and **nothing that sounds like ice cracking** (rule 1). It ends unresolved, on *mir* (stay): bible §5. |
| `nhoa_summon` | (her first battle call, after this chapter) | Sting ≤ 6 s (not yet written; M4-A2P-091) | — |
| `silence` | B03 (end), B07, B10 | — | B10 has only the conduits' hum and the lamp's small hiss. |

**SFX:**
- `engine_tick` (the Engine's trimming, heard through the floor from B04);
- `ring_fold` (phase 2);
- `crawler_repair` (brass feet and a glass seating click);
- `silt_sift` (the well-shaft: a very faint granular hiss);
- `lamp_seat` (B10).

---

## 7. Camera shots by beat

New shot ids for `ch11/sunken_vey` and `ch11/lowlight` (to add to lowlight.md beside L01–L05).

| Id | Shot | Lens / note |
|---|---|---|
| V01 | The landing; Liss looking at the conduits | 35 mm |
| V02 | A gallery walk over still water | rail |
| V03 | The fig end: the lamp in the roots (optional) | rail look-at |
| V04 | Liss's hand on the housing; Rhen's lantern collar beside it | 85 mm, two inserts matched |
| V05 | Liss and Rhen, the argument | 50 mm two-shot, then singles |
| V06 | Liss walking off; stopping at the court's edge, back turned | 35 mm, held |
| V07 | Asha's hand going to the comb and stopping | 85 mm; **nothing said** |
| T01 | The nave's lamp tiers, every lamp dark, trim-arms aligned | 24 mm, looking up |
| T02 | The Engine turning all its lamps to the party | 35 mm, low from the water |
| T03 | The core's light rising through the vault bay | 24 mm, looking up; **every mote rises** |
| T04 | The party; Liss on the dead frame | 50 mm |
| N01 | The spiral stair going down into teal; silt-light falling | 18 mm, looking down |
| N02 | From the ledge into the drowned sanctum: Nhoa in the water | 35 mm, through the water (underwater shader) |
| N03 | **Pell stopping at the back of the line**, crest rising | 85 mm; the camera finds him first |
| N04 | **Insert:** the carved name-shell at her throat | 100 mm |
| N05 | Pell kneeling at the ledge's edge, hands on the water | 50 mm, then held |
| N06 | Asha looking from Pell to Nhoa | 85 mm |
| N07 | The binding: the staff, the light rising to it, the sleeve growing | 35 mm, then insert on the sleeve |
| N08 | Nhoa's head turning toward Pell | 85 mm, through the water |
| N09 | Pell still kneeling; Kerrid behind him on the ledge | 50 mm, wide enough for both |
| T05 | The lamp bench: two pairs of hands (side scene) | 50 mm, locked, then an insert on the flame |
| V08 | The landing at late afternoon: Asha and Pell | 50 mm |
| V09 | The line leaving the Vey; Rhen and Liss's places in it | 35 mm, from behind |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B03 | L03 → V04 → V05 → V06 → V07 | V07 is a hand, not a reaction shot of the face: the lantern isn't voiced until Ch15. |
| B07 | T03 → T04 | T03 holds until the last mote leaves the top of frame. |
| B09 | N02 → N03 → N04 → N05 → N06 → N07 → N08 → N09 | **From N05 to the end, Pell says nothing** (rule 4). N08 is a turn of the head and nothing else. |
| B10 | T05 | One locked shot plus the inserts. |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 | 20 |
| B02 barks | 80 |
| B03 | 150 |
| B04 (optional bark) | 30 |
| B05 | 15 |
| B07 | 20 |
| B08 | 6 |
| B09 | 15 |
| B10 side scene | 25 |
| B11 | 40 |
| **Total** | **~400 written** (~330 on a path without the optional barks and side scene) |

**Against SPEC §3.6:** at ~37 min, Ch11 is about 2.2% of the game, so its fair share is **880–1,300 words**. It sits well under the band on purpose: the chapter's two great beats (Pell's and the lamp bench) are silences. The words the act saves here are spent in Ch15. Narrative may add town-free barks to the galleries if the band matters.

---

## 9. Requests to other roles

### Rendering (M4-A2P-049, M4-A2P-058)
1. **The Engine's release (T03):** bound motes in the core going still, then switching to LIFT (released) and rising through the vault bay, `glimmer_lift` gold on the climb; the 3 s warm grade lift (color script `ch11`). A mote or two from each broken ring during the fight.
2. **Silt-light in the well-shaft (N01, N02):** held motes falling slowly through the water column and settling (sinking, not drifting seaward), the visual opposite of T03. They're distinct from Nhoa's own beads (geometry, bound, still: vowbound/nhoa.md).
3. **The binding (N07):** the silt-light rising to Asha's staff and into the verse-sleeve (M4-A2P-071 stages it).
4. **Cold without frost** (rule 1): a cold haze over the shaft's water, colour only.

### Art (color script)
1. `ch11` exists. Confirm the well-shaft's teal underwater view (N02) under the underwater shader, and the dusk at the Vey's mouth (B11, the conduits brighter than the sky).

### Environment Art (M4-A2P-041)
1. The kit exists (M3-ENV-716, M3-ENV-735). Place per lowlight.md §5:
   - the conduit court with the housing-mark at chest height;
   - the fig end with a lamp in the roots;
   - the atrium's lamp bench with a broken salt-glass lamp in pieces;
   - Wenna's mark behind a fallen trim-arm (lines, node-dots, the key glyph: act1_ch08 B05's grammar);
   - the well-shaft's two flights ending at a dry ledge over the drowned sanctum.

### Character Art
1. **Rhen's lantern carries the mark** (M3-ENV-719, `todo`): it's needed for V04's matched inserts.
2. **Nhoa** (built: M3-CRE-642) with a **readable carving** on her name-shell for N04 (the one carved word that matters; Kirru script, original).
3. **Animation:**
   - Pell's kneel in water, held for a long time (a hold pose with crest and breathing idles only);
   - Asha's binding gesture (as Ilun's, Kahre's and Virel's);
   - Liss shoving the lantern into Rhen's chest;
   - the lamp-bench hand work.

### Audio (M4-A2P-091)
`nhoa_bound` and `nhoa_summon` (§6), and a stripped `lowlight` for B08.

### UI
1. The verse-sleeve at **S4** after B09 (the status page's sleeve).
2. The lamp-bench held inputs (B10): the same widget family.

### Combat (M4-A2P-011, M4-A2P-022, M4-A2P-024)
§5: the Engine's ring break parts and charge skills, the gathering's telegraph, the conduit crawler as a repairing add (`restores_part`), the `opened` core. Nhoa's `vowbound.json` row (`bound_flag: ch11_nhoa_bound`); her echo copies **ordinary skills only**, never a boss's charge (ADR 0204 §8).

### Systems / Chapters (M4-A2P-011)
1. **Speakers:** none new beyond Nhoa's sung verse (a `nhoa` sung line, no portrait).
2. The well-shaft's ledge is walked (design default (a)).

### Cinematics (reviewer)
Check §0's rules against every shot, especially:
- V07 (a hand, no line);
- T03 (every mote rises);
- N05–N09 (Pell silent from the kneel on);
- N08 (a turn only).
The binding's staging and the lamp bench's held pace are yours.

---

## 10. Open questions for review

1. **The fourth verse:** this sheet has Nhoa teach the fourth verse at the binding, in order after Ilun (1), Kahre (2) and Virel (3), with the sleeve at S4. Confirm against vowbound.md's verse-per-Saint rule.
2. **Liss's anger (V05–V06):** "And you're sitting on his name like it's a debt" is this sheet's line. It's sharp, and it should land as hurt, not cruelty. Narrative may soften it. The voice guide's line before it is fixed.
3. **Nhoa's turn toward Pell (N08):** a bound Vowbound turning its head is the only sign that Ressa knows him. If that reads as too much agency for a bound light (color rule 2), cut N08 and let the name-shell insert (N04) carry it alone.
