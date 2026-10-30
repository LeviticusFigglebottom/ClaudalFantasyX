# Ch6 Beat Sheet: "Salt Edict" (the Brine Shoals)

Owner: Narrative (M3-C06-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch6](act_outline.md), [bible §4 and §7](../bible.md), [voice guide](../voice_guide.md), [sefir_aurane.md](../characters/sefir_aurane.md), [liss_varrow.md](../characters/liss_varrow.md), [toma_okeru.md](../characters/toma_okeru.md), [kerrid.md](../characters/kerrid.md), [color script `ch06`](../../art/color_script.md), [ADR 0017](../../decisions/0017-act-one-restaging.md) (a), [ADR 0020](../../decisions/0020-kerrid-restaging.md) (i), [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (Ch6 and the lantern watches), [decisions_log N-02, N-24, N-25, N-26](../decisions_log.md). Format: [vertical_slice.md](vertical_slice.md).

Scripts: not written yet (M3-C06-02). Sample lines set the voice; the **Sefir lines in B05 are written in full** because his first appearance is staged line by line in ADR 0017 (a) and must be reviewed as text.

Seams: Ch5 (act1_ch05.md) ends at Pemakar's harbour road at dawn on day 3, with Kerrid falling in last. Ch7 (act1_ch07.md) opens with the party coming in to Tamsule on the morning of day 4.

---

## 0. The chapter in one paragraph

On the road to Tamsule the party crosses a drowned country of mud and wrecks, and comes over the last hull to find the Order burning a Saltwright salvage camp in broad daylight, while its Stillguard hum the Canticle and a clerk heats the brine-irons. Toma, who stood on a line exactly like this one at twenty-two, can't move. A girl with a crate of bound parts runs straight into Rhen, and Asha hides her. When the Inquisitor's hound comes for them, Toma steps in front of Asha with his shield and will not strike back. Then, through the smoke, a white barge comes up the channel without leaving a wake, and the head of the whole Order puts the irons out with one sentence, speaks tenderly of Asha's mother, and lets the girl go. The player should finish the chapter **trusting Sefir** and loving him a little, with Toma. On a replay every one of his kindnesses will be visible as a thing that cost him nothing, and every tell will be in plain sight. Liss's line is the only one that says so, and nobody answers it.

**Emotional line:** a hard, dull road → dread (the smoke, and Toma knowing the smell) → horror held at a distance (the hum, the irons) → a freeze → protection without violence → relief, almost joy (the barge) → a sour note nobody answers ("once it had finished") → friction with a new voice → a quiet grave at the tideline.

**What the chapter must deliver** (act_outline Ch6, ADR 0017 (a), ADR 0020 (i)): the Brine Shoals route; the raid; Toma freezing; sheltering Liss; the Stillguard Inquisitor and raid-hound, with Toma refusing to strike to kill; Sefir's first appearance, staged exactly as given; Liss joining on Toma's papers and clocking the lantern; the burned-lamp side scene.

---

## 1. Running order

One afternoon and a night. Minutes are the player's, at a first-time pace. **P** = playable, **C** = letterboxed cutscene, **E** = in-engine scene. Shot ids are proposals (§7, §9).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The Brine Shoals** | `ch06/brine_shoals` mud-flats and wreck-ridges | day 3, 12:30 | P | 6.0 | W01, W02, W03 | `brine_shoals`, `battle_standard` | A drowned country nobody owns. Old marks on the hulls, and Toma going quiet at one of them. | — |
| B02 | The smoke | `ch06/brine_shoals` the last wreck-ridge | 15:20 | E | 1.0 | W04 | `brine_shoals` → `silence` | Dread. Toma stops walking before anyone else has seen the fire. | — |
| B03 | **The raid** | `ch06/brine_shoals` the salvage camp | 15:30 | C | 3.5 | W05, W06, W07, W08 | `raid` (with the diegetic Stillguard hum) | Horror at a distance, then a freeze. A girl with a crate, a hiding place, and a Cantor who says "No." | `ch06_sheltered_liss` |
| B04 | **Boss: the Stillguard Inquisitor and raid-hound** | `ch06/brine_shoals` the camp, by the burning hulk | 15:40 | P | 6.0 | W08, W09 | `stillguard_inquisitor` (2 stems) | Protection without violence. The party fights the Order's own for the first time, and nobody dies. | `ch06_inquisitor_yielded` (battle result) |
| B05 | **The barge leaves no wake** (Sefir's first appearance) | `ch06/brine_shoals` the shoal channel and waterline | 15:50 | C | 5.0 | W10, W11, W12, W13, W10 | `silence` → `sefir_theme` (first statement) | Relief, and grace. The kindest man in the world arrives at the edge of a fire his law lit. | `ch06_met_sefir`, `ch06_rhen_greeted_sefir` (choice) |
| B06 | After the barge | `ch06/brine_shoals` the camp | 16:10 | E | 1.5 | W06 | `liss_theme` (first statement) | One sour sentence that nobody answers, and a practical new guardian. | `ch06_liss_joined` |
| B07 | Liss and the lantern | `ch06/brine_shoals` the camp | 16:20 | E | 1.0 | W14 | `liss_theme` | Friction. She reads his father's work in a glance. He deflects. | `ch06_liss_read_lantern` |
| B08 | Camp on the wreck-ridge | `ch06/brine_shoals` the ridge camp | 18:30 | P | 2.0 | W15 | `shoals_dusk` | Rest after a bad day. A save point, a man standing watch facing the sea, and one guardian missing from the fire. | — |
| B09 | *Side scene: The Burned Lamp* (optional) | `ch06/brine_shoals` the tideline | 18:45 | E | 3.5 | W16 | none (tide ambience) | A Saltwright burying one of her dead. She won't say whose name was on it. | `ch06_saw_lamp_buried`, `ch06_dug_without_asking` (choice) |
| B10 | The channel at dawn | `ch06/brine_shoals` the shoal channel | day 4, 06:00 | E | 0.5 | W10 (dawn) | `brine_shoals` (dawn) | Ash lying flat on water no barge has stirred. Tamsule's gilt on the horizon. | — |

**Totals:** critical path **26.5 min** (B01–B08, B10). With the side scene, **30 min**. Split: **14 min playable (53%)**, 8.5 min cutscene, 4 min in-engine. Ch6 is a route chapter with one set-piece; it is short by design, and Ch7 is a town.

**Cut order if the chapter runs long:** B10 folds into Ch7 B01 as its first shot. B01 loses one banter (keep the old marks). B07 merges into B06's end. **Never cut** Toma's freeze in B03, his refusal in B04, any line or look in B05, or Liss's "once it had finished".

---

## 2. Beat detail

### B01. The Brine Shoals (P, 6 min)
Low water over a drowned country: grey-green silted flats (`silted_flats` water look), wreck-ridges of black Lit Age hull plating and wooden hulks, gulls, and the tide-channels between. The route goes from ridge to ridge, with the flats as a slower, riskier short-cut.
- **Encounters** (creatures track ids): `shoal_skipper` (quick strikers, low HP), `wreck_crab` (defenders), and a reused `gull_harrier` (flier). See §9. Music: `battle_standard`.
- **Saltwright chalk marks** on the hulls: a circle with fine parallel lines (a camp-sign, "wrights work here"). They thicken as the party nears the camp. They are the player's first sight of Liss's people before Liss.
- **Three walking banters** (~90 words in total):
  1. *A Lit Age wreck (W01):* Rhen prices its brass aloud. Ysolde: "Everything on these shoals is under the Edict, Master Sallow." Rhen: "Everything everywhere's under something."
  2. *The midday stop (W02):* everyone eats on a hull, and Kerrid doesn't. Camera insert: his share untouched beside him. No line from him. Rhen takes it after a while: "...Seems a shame." (Second clue after Ch5's bowl.)
  3. *The chalk marks (W03):* Toma stops at one and looks at it too long. Asha: "Toma?" Toma: "It is nothing. Old marks." *(Do not surface: he was on a Brine Shoals raid out of Corrow at twenty-two, in 1003. He has been here before. This pays off in his Ch15 confession to Liss.)*

### B02. The smoke (E, 1 min)
On the last wreck-ridge (W04), Toma stops walking first, before the smoke is in frame: he knows the smell. Then the camera finds the column behind the next hull. ~15 words. Rhen: "Somebody's cookfire." Toma: "No." The music drops out (`silence`) under the crackle.

### B03. The raid (C, 3.5 min)
- **W05:** the camp from the ridge: a Saltwright salvage camp of lashed hulls, tide-wheels and windmills, and racks of lamps, all burning. Stillguard in red-lacquered shell armour move through it with torches, unhurried. **They hum while they work**: the Order's congregational hum, the Canticle's tune with no words (bible §4, "the Order hums"). It is the most frightening sound in Act I because it is calm.
- **W06:** at the waterline, a dozen wrights kneel with their sleeves pushed up. An Order clerk heats **brine-irons** in a brazier of coarse salt. A Stillguard holds a girl's arm out over the brazier, her line-marks toward the iron.
- **W07, Toma:** close on his face. `@face toma afraid 0.6`, then nothing: he doesn't move. *(Do not surface: this is the picture he has dreamed about for nine years, a girl's line-marks under a brine-brand, toma_okeru.md.)* Asha: "Toma." He doesn't hear her. Asha, again, softer: "Toma." Nothing. The camera holds on him 2 s longer than is comfortable.
- **Liss.** A burning hull's hatch bursts open and a small, fast girl with a crate in her arms (its seams leaking bound teal light, `glimmer_bound`) runs flat out along the ridge and straight into Rhen. A hound bays behind her. Her first line, mid-thought (voice guide):
  > **Liss:** Move or hide me, pick one.

  Asha decides before anyone else: "Here." She takes Liss by the wrist into the hold of the wreck they're standing on. Rhen throws a sail over the hatch. (Asha's unbending underneath, voice guide: the decision is hers.) Sets `ch06_sheltered_liss`.
- **In the hold** (W08, dark, smoke through the planks): Liss's face is a foot from the lantern on Rhen's shoulder, and even now she looks at it. A whisper:
  > **Liss:** That's wright work.
  > **Rhen:** Not *now*.

  ("She clocks Rhen's lantern as a Saltwright make immediately," act_outline. The full exchange is B07.)
- **The Inquisitor.** The hatch-sail is pulled away. **Inquisitor Hadric Moll** (new speaker: a living officer of the Stillguard, sincere, tired, with a brine-iron on a long haft) and the raid-hound. ~60 words:
  > **Inquisitor:** Lady Cantor. Step away from the hold.
  > **Asha:** No.
  > **Inquisitor:** The Edict—
  > **Ysolde:** —does not give you a Cantor's party, Inquisitor.
  > **Inquisitor:** *(a beat; then, to the hound)* Loose.

  The hound goes for the hold. **Toma moves at last**: he steps in front of Asha with the tide-shield up. "On my shield." (The slice's line, now aimed at his own order.) `start_battle ch06_inquisitor`.

### B04. Boss: the Stillguard Inquisitor and raid-hound (P, 6 min) — see §5

### B05. The barge leaves no wake (C, 5 min) — *Sefir's first appearance*
**Staging contract (ADR 0017 (a), unchanged):** the barge leaves no wake; one sentence stops the branding; the gentle rebuke; he doesn't ask who struck his Stillguard; "I knelt beside your mother"; Liss let go on Toma's papers, by the custom that a Cantor may take any guardian she chooses; the look at the crate; Kerrid's back; Rhen treated as an amusing young man; Toma overjoyed; Liss's line after. Every item below is one of those, in order.

1. **W10, the impasse:** the Inquisitor on one knee in the mud, the hound gone. A dozen more Stillguard arrive at a run and level their spears at the party. Toma stands between, shield up, shaking, not striking. Nobody moves.
2. **W11, the barge:** the smoke on the channel thins, and a long **white barge** comes up through it, poled by four Reeds. **It leaves no wake.** The water behind it is as flat as the water ahead. The poles go into the water without a sound: Audio carries the poles' wood creak and nothing from the water (§6). The Stillguard kneel, palms flat. The wrights at the waterline look up. The camera holds the barge's stern and the unbroken water behind it for a full 3 s.
3. **Kerrid** has his back to the barge for the whole scene. Before it arrives he has gone to a burning hulk and is holding up a smouldering hull-rib on his shoulder so two wright children can crawl out from under it. That's why his back is turned, and it's a practical reason (ADR 0022 (f)'s rule for his absences). Sefir doesn't know his face. When his eyes cross the party they **rest on Kerrid's back for half a beat** (`@wait 0.5`) and move on. Nobody sees it but the camera.
4. **High Warden Sefir Aurane** stands at the barge's bow and stays aboard throughout. He never steps onto the mud, and his hem stays clean (a tell). He speaks first to the clerk at the brazier, without raising his voice. **The one sentence:**
   > **Sefir:** Put the iron in the water, please.

   The clerk does. The iron hisses in the shallows: it is the only sound of water in the scene. The Stillguard holding the girl lets go of her arm.
5. **The rebuke** (voice guide sample, kept verbatim):
   > **Inquisitor:** High Warden. They struck the Stillguard. The Cantor's own—
   > **Sefir:** Be level, Inquisitor. The Edict burns things. It has never needed to burn people.
   > **Sefir:** The Edict was written by frightened people. We need not be frightened today.

   That second line is how he **doesn't ask who struck his Stillguard**: he declines the question. *(Replay tell: he wrote the Edict in 212 AL. He is describing himself.)* He turns to the wrights: "Take them up to Corrow. See that they are fed." *(First play: mercy. Replay: they are still captives, and he has spent nothing. Ch8 seam, §9.)*
6. **W12, Asha.** She bows, palms flat, formal. He bows back, lower than he needs to.
   > **Sefir:** Lady Cantor. I knelt beside your mother once, on a day very like this one.
   > **Asha:** It would honour me to hear of her, High Warden.
   > **Sefir:** And you shall. Come to Ansedra, and we will sit, and I will tell you everything I can.

   (ADR 0020 (i): spoken at a burning, unasked, as a mercy that costs him nothing; true, and turned in Ch16, where he knelt beside Imra at the Choir as she became the heart; and Kerrid, who got her up the stair so she could get there, has his back to the barge while he says it.) *Facial beat:* Asha's face holds formal, and only her eyes go bright. She doesn't cry.
7. **Liss and the papers.**
   > **Inquisitor:** And the wright with the crate.
   > **Sefir:** *(to Asha, not the Inquisitor)* Is she one of yours?
   > **Asha:** She's my guardian.

   A beat. Liss's face (she didn't know she was). Sefir is pleased, as if at a good answer from a student:
   > **Sefir:** Then she is. A Cantor may take any guardian she chooses. It is the oldest custom we keep. Toma Okeru, your papers will carry her?
   > **Toma:** ...They will, High Warden.

   *(He knows Toma's name without being told. Replay tell.)* Then **his eyes go to the crate** in Liss's arms, its seams leaking bound teal light, and rest there **a moment too long**: `@wait 1.5`, no line, no change of face. He lets it go with her.
8. **Ysolde** (~20 words): "Scholar Ysel. You will come to the Sanctum this year?" "As every year, High Warden." "He will be glad of you." *(First play: a kind man and a widow's yearly visit to her husband's Saint. Replay: he knows Corran hears every visit.)*
9. **W13, Rhen.** Sefir's eyes find the diver with the lantern, who is standing up when everyone else is kneeling, and he is visibly amused. **Choice:**
   - Rhen tries the greeting and gets it backwards: "Be... still?" (sets `ch06_rhen_greeted_sefir`)
     > **Sefir:** That is the answer, young man, not the greeting. But I will take it gladly.
   - "Does that barge ever make a wake?"
     > **Sefir:** Not if it is poled well. There is very little in the world that needs to hurry.

   Both are said with warmth, as to a likeable boy. Neither treats Rhen as anything that matters (sefir_aurane.md).
10. **Toma.** Sefir looks at him last. Toma kneels, palms flat, and his voice goes:
    > **Toma:** Be level, High Warden.
    > **Sefir:** And still, Toma Okeru.

    `@face toma tender`, close: a man being handed his faith back in the same hour he lost his nerve. Play it as joy, not relief.
11. **W10, the going.** "Go gently, Lady Cantor." The Reeds pole the barge back into the smoke. Still no wake. The smoke closes behind it. `sefir_theme` resolves on the cut, the first melody in the game that resolves completely (§6).

**Rules for this scene.** He never raises his voice, never hurries, and never uses a contraction. Each line is a small, complete paragraph (voice guide). He answers no grief in this scene, because nobody here grieves at him; that tell is saved. **He must read as kind and trustworthy on a first play.** No reaction shot may undercut him: no Liss glare, no Kerrid flinch, no ominous sting. The only dissent in the chapter is B06's one line, after he has gone.
**Words:** Sefir ~125, all others ~85. **Tells for the replay**, all present and none pointed at: §5a.

### B06. After the barge (E, 1.5 min)
- **W06:** the wrights are led away up the shoals toward the Corrow road under escort, unbranded, their camp still burning behind them. Toma is radiant; there are tears on his face and he doesn't wipe them.
  > **Toma:** You saw him. That is the Order. That is what it is for.

  Liss is watching the wrights go.
  > **Liss:** He put the fire out once it had finished.

  Silence. Nobody answers. Toma's smile holds, and then it doesn't quite. (act_outline; liss_varrow.md: she never forgives Sefir for being kind about it.)
- **Joining** (~60 words). Liss, practical: "Your papers get me past the Corrow checkpoints. I'll pull my weight, and I'll stop when we're square." Toma, the most uncomfortable and the most polite: "You are written in, Mistress Varrow. You are under my papers now." Liss: "Lucky me." Ysolde: "Welcome to the Lady Cantor's party." Asha, to Toma, quietly, apart (her tell, voice guide: when hurting, ask about the other's day): "Are you all right?" Toma: "I am better than all right." She lets him have it. Sets `ch06_liss_joined`.

### B07. Liss and the lantern (E, 1 min)
**W14:** Rhen and Liss alone by the burning tide-wheel while Toma writes her into his papers (**Asha is off-frame, with Toma**; ADR 0022 sweep-G/I watch: no Act I line, bark or reaction has Asha connect the lantern to anyone, so she isn't in this scene).
> **Liss:** Hold still. That's a wright's housing. Pair-built: see the second seat, for the hook? And an oil burner in salt-glass. Who fits an oil burner in salt-glass?

- If `ch02_rhen_named_lantern`: **Rhen:** "It was my father's." **Liss:** "Then your father bought from a wright. Or knew one." **Rhen:** "He knew a lot of people."
- Otherwise: **Rhen:** "Somebody who liked oil. Good trade." **Liss:** "Nobody trades wright work that good. Somebody gave it up."

Then she sees him eyeing her crate's bound parts the way he eyed the wrecks:
> **Liss:** You sell the dead by the pound, diver. At least I put them back to work.

(voice guide sample.) Sets `ch06_liss_read_lantern`. *Do not surface:* Rhen's Saltwright blood is seeded here and admitted only at Lowlight in Ch11 (rhen_sallow.md). He never says "my father was a wright" in Act I. The pair seat is true to ADR 0022's sweep-H note: Dace built his lanterns as a pair.

### B08. Camp on the wreck-ridge (P, 2 min)
**W15, 18:30:** a camp on a high hull out of the tide's reach. A wayside save shrine (an Order Level-stone set in a wreck's bow, chipped, still tended), and a travelling vendor's boat (the shop). The party sits round a small oil fire. **Kerrid stands** at the ridge's seaward end, facing the water (he never sits in Act I). Talk-to barks, ~40 words: Ysolde reading; Toma re-reading his papers with Liss's name in them; Asha asking Rhen about his day (he notices she does that). **Liss isn't at the fire.** A marker on the tideline below opens B09.

### B09. Side scene (optional): "The Burned Lamp" (E, 3.5 min) — see §4

### B10. The channel at dawn (E, 0.5 min)
**W10, dawn:** the party wades the shoal channel the barge came up. Ash from yesterday lies on the water in a flat grey skin, unbroken; nothing has stirred it. Tamsule's gilded signboards catch the sun on the horizon. ~30 words. Rhen: "Tamsule. The Tidecup's on." Liss: "You play?" Rhen: "Everyone from the Reaches plays." (It sets up Ch7 without promising anything.)

---

## 3. Flags

To be declared in `game/data/flags.tres` by M3-C06-02, with these descriptions.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch06_sheltered_liss` | B03 | B04 setup | — |
| `ch06_inquisitor_yielded` | B04 battle result | B05 trigger | Ch14: Inquisitor Moll may reappear among the Conclave's Stillguard at the wedding and stand aside for Toma (offered to the Ch14 owner). |
| `ch06_met_sefir` | B05 (end) | Ch13 | Sefir greets the party at Ansedra as acquaintances. |
| `ch06_rhen_greeted_sefir` | B05 choice | Ch13, Ch16 | Ch13: "The young man who gives the answer before the greeting." Ch16 (offered): he uses it once at the Choir, gently, as the last courtesy before the truth. If unset, he recalls the wake question instead. |
| `ch06_liss_joined` | B06 | party roster, zone gating | Liss in the party from here on. |
| `ch06_liss_read_lantern` | B07 | Ch11 | At Lowlight: "I told you on the shoals it was wright work." |
| `ch06_saw_lamp_buried` | B09 | Ch11 | Lowlight's lamp-repair side scene (the truce) opens with a line about the shoals. |
| `ch06_dug_without_asking` | B09 choice | Ch11 | Liss, at the repair: "You dug. You didn't ask." She hands him the tool first. |

---

## 4. The optional side scene: "The Burned Lamp" (B09)

**Where:** the tideline below the camp at dusk (W16: the low sun through smoke, wet sand, the tide coming in). **When:** B08, through a marker on the tideline. **Length:** 3.5 min, ~150 words. Speakers: `liss`, `rhen`.

**Beats:**
1. Liss is digging a hole in the wet sand with a hull-scraper. Beside her is a lamp housing, scorched black, its salt-glass crazed. A name is scratched on its collar, under her thumb; the camera never reads it. She doesn't look up. "Don't touch that."
2. **Choice:**
   - "Whose was it?" She: "Don't." He doesn't ask again. He sits down a little way off.
   - He kneels and digs with his hands, saying nothing. After a while she hands him the scraper. (sets `ch06_dug_without_asking`)
3. **Her grief tell** (voice guide: she narrates repairs instead of talking about it): "Housing's cracked at the seam. Burner side's fused. Seals gone. She'd not hold." A pause. "She'd never hold again."
4. She sets it in the hole and they cover it. She flattens the sand with her palm. The tide will have it by midnight. **VFX:** one faint `glimmer_held` mote slips out of the sand and drifts seaward, down the beach, into the water. Neither of them looks at it. (Bible §2: the light was already broken loose by the fire; it goes down because she is holding on. Saltwrights hold their dead too: bible §7's blind spot, shown and never said.)
5. Rhen, sincere and short: "In Oruvel we'd hang a lamp on a mooring line. For the ones who didn't come up." Liss: "We put them to work. That's how we keep them." Rhen: "And when they break?" Liss: "Then you dig."
6. She stands and brushes off her knees. "You didn't see this, diver." Rhen: "See what." She almost smiles.

**Rules:** Rhen doesn't joke and says nothing about his father or his lantern. Liss never says whose name it was. No more than four lines from Liss in a row.
**Whose name (design truth, proposed, not game text):** the lamp held **Old Pirran**, the camp wright who taught Liss to seat her first housing at nine and asked, dying, to be bound into a camp lamp so he could keep working. She carried him from camp to camp for six years. The game never says it in Act I. It is available to the Ch11 truce scene or to Ch17 at Hollowmere, if those owners want it; otherwise it stays unspoken for good. *(Flagged to the Lead: this adds a named dead person to Liss's history, so it wants a decisions_log entry before any line uses it.)*
**Payoff:** `ch06_saw_lamp_buried` and `ch06_dug_without_asking` open the Ch11 lamp-repair truce (Rhen and Liss repair a lamp together in silence).

---

## 5. The Stillguard Inquisitor and raid-hound (B04): placement, phases, and what it teaches

**Placement:** straight out of B03, at the burning camp's waterline beside the hulk where the party hid Liss, with the camp burning behind (W08, W09). It is the first time the party fights the Order's own, and **nobody dies in it**: the Inquisitor yields, and the hound is driven off.

**Toma refuses to strike to kill.** This is the fight's rule, and it must be clear on the screen (pillar 4):
- For this encounter Toma's offensive commands are unavailable against the Stillguard. They show greyed with the tooltip *"Toma will not strike the Stillguard."* The first time the player selects one, Toma barks: "No. Not them." His defensive kit is all there: Brace, Cover, Provoke, Protect (shield_wall), and counters that **shove** rather than wound (his counter is replaced by a non-damaging push back on the timeline for this fight).
- The battle's end condition is a **yield**, not a kill: at 0 HP the Inquisitor goes to one knee and yields, and the hound, at 0 HP, breaks off and runs. The victory banner reads *"The Inquisitor yields."* (UI, §9.)

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: the Hound's Watch** | The Inquisitor and the hound side by side at the waterline (W08). | The **hound protects the Inquisitor** (creatures track spec): while it stands, it intercepts single-target attacks on him, and when he is struck it **pounces on the striker**, with its turn jumping forward on the timeline (the preview shows it). The Inquisitor's **Brine Iron** (fire damage plus Weakened, the salt-burn across the arm) and his **Shell Wall** (Protect on himself; red-lacquered shell armour). | Read who is guarding whom. Draw the guard off first: **Toma's Provoke** pulls the hound's pounces onto his shield, and Rhen's push-backs (Kick Off the Wall) shove the hound down the timeline so the Inquisitor is exposed. Kerrid's sundering blow answers the shell armour. | Toma's whole faith in one fight: he guards, he will not wound. The party's protector is the answer to the Order's protector. |
| **2: Torch the Hulk** (at 50% of the Inquisitor's HP, or when the hound is driven off) | He calls for the hulk to be fired. The burning wreck becomes a **Smoke** field (W09). | Smoke inflicts Darkness on the whole party each round while it holds. **Ysolde's magic doesn't miss in it**, and Asha's cleanse lifts the Darkness. If the hound is still up, it fights blind too. | Fields have answers in the party; swap to the caster when your strikers can't see. | The Order burns what it can't own. Even its officer coughs in it. |

**Tutorial text** (UI loc keys), one per phase, no more. Phase 1: *"The hound guards the Inquisitor. Draw it off."* Phase 2: *"Smoke blinds blades. Magic still finds its mark."* Plus Toma's greyed-command tooltip (above).
**Battle barks** (≤ 35 words): Toma, "No. Not them." (the first refused command); Ysolde on the field, "They have raised a hand to a Cantor. The Edict does not cover that."; the Inquisitor at the yield, "...Enough. Enough." **Kerrid has no lines.** (His first-ever words to the party were in Ch5; he stays silent in combat in Act I.)
**Light:** Liss's crate is the only glimmer on the field (`glimmer_bound` teal through the seams, color script `ch06`). No mote rises or sinks in the fight: nobody dies.
**Combat band** (Ch4–Ch9 boss): naive ≤ 5%, role_answer 65–85%, smart 75–92%, p90 ≤ 70. Party: Rhen, Asha, Toma, Ysolde, Kerrid (Liss is not in the party until B06). Loadout `ch06_inquisitor`: Pemakar's tier plus `ch03_ilun_bound` and `ch05_kahre_bound`. The sim must model Toma's forbidden commands (a per-encounter `forbidden_skills` list for `toma`).

### 5a. Sefir's tells (for Cinematics and the replay)

Each is in the scene, played flat, never framed as a clue. A first-time player should see only grace.

| Tell | Where | What it means on a replay |
|---|---|---|
| The barge leaves no wake, and the poles make no water sound | B05 (2) | Ansedra's held water and the machines under it (Ch13–14). |
| He never steps onto the mud; his hem stays clean | B05 (4) | He touches nothing he doesn't have to. |
| His breathing is absent (anim: no breath cycle) | the whole scene | sefir_aurane.md: the revenant's stillness. |
| His reflection in the shallows doesn't ripple when the iron hisses | B05 (4), one frame | sefir_aurane.md revenant tell. |
| "The Edict was written by frightened people." | B05 (5) | He wrote it. |
| "Take them up to Corrow. See that they are fed." | B05 (5) | They stay captives; the mercy cost him nothing. |
| "On a day very like this one." | B05 (6) | The day he knelt beside Imra at the Choir as she became the heart (ADR 0020 (i)). |
| "I will tell you everything I can." | B05 (6) | He does, at the Choir. |
| He knows Toma's name unasked | B05 (7) | He watches everyone near a Cantor. |
| The crate, a moment too long | B05 (7) | Bound light is what he lives on; he can afford to let it go. |
| "He will be glad of you." | B05 (8) | He knows Corran hears every visit. |
| His eyes rest on Kerrid's back for half a beat | B05 (3) | He doesn't know the face; he sees what Kerrid is (ADR 0022). |
| "Very little in the world needs to hurry." / "the answer, not the greeting" | B05 (9) | The Long Stillness in a pleasantry. |

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `brine_shoals` | B01, B02, B10 | Field bed, loop | Low reeds, mud-suck percussion, a creaking tide-wheel far off, long silences. A dawn variant for B10. |
| `battle_standard` | B01 | Battle loop | The standing battle cue. |
| `raid` | B03 | Cutscene score | Almost no score: fire crackle, a low frame drum, and **the diegetic Stillguard hum** (the Order's congregational tune, hummed calmly by a dozen men's voices) as the melody. The hum must be the Order's existing hummed tune from the temple ambience, so the player knows it. |
| `stillguard_inquisitor` | B04 | Boss, two stems | Stem 1: shield-rim percussion and the hum motif in low strings, made martial. Stem 2: adds fire crackle and a choked, smoky brass. |
| `sefir_theme` | B05 | Character theme, first statement | Warm, unhurried strings and a hummed choir, entering only after his first line. It is beautiful and consonant, and it **resolves completely**, the first melody in the game that does (Haluna's never resolves). On a replay that perfect rest is the tell. Original melody, never an echo of the Hush. |
| `liss_theme` | B06, B07 | Character theme, first statement | Plucked strings over a tide-wheel ostinato that's a little off the beat, bright and guarded. |
| `shoals_dusk` | B08, B09 | Night bed | The field bed thinned to one reed and the tide. B09 drops even that to tide ambience. |

**SFX** (requested): `brine_iron_hiss` (the iron in the water; the only water sound in B05), `barge_pole` (wood creak and Reed footfalls only, **no water sound**: the absence is the effect), `raid_hound_bay`, `hatch_burst`, `camp_burn` (layered fire, tide-wheel collapse), `stillguard_hum` (if not part of `raid`).

---

## 7. Camera shots by beat

Shot ids are proposals for Environment's `brine_shoals.md` (§9). Every change of setup is a cut unless it's a same-axis move.

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | W01, W02, W03 | Rail cameras. W02 holds the midday stop with Kerrid's untouched share in the foreground. |
| B02 | W04 | Toma stops before the smoke enters frame. Pan only after he stops. |
| B03 | W05 → W06 → W07 → W05 → W08 | W05 wide from the ridge; W06 tight at the brazier (the girl's arm, the iron); W07 a close on Toma, held 2 s past comfort; back to W05 for Liss's run; W08 inside the dark hold (the lantern is the only key light on Liss's face). |
| B04 | W08, W09 | W09 is the smoke field. |
| B05 | W10 → W11 → W10 → W12 → W13 → W10 | W10 wide on the impasse, low over the mud. W11 is the barge from water level, its stern and the flat water behind it held 3 s. **No close-up on Sefir before his first line**: we see him small at the bow first. W12 a two-shot of Sefir on the bow and Asha on the mud, the barge higher than her (he looks down kindly; she looks up). W13 is Sefir's eyeline over the party: it passes Kerrid's back (half a beat) and finds Rhen standing. Toma's kneel is a cut back to W12's axis. The crate look is an insert inside W12 (the teal seams). |
| B06 | W06 | The wrights led away in the background while Toma speaks; Liss in profile, watching them. |
| B07 | W14 | A two-shot by the burning tide-wheel. Asha out of frame. |
| B08 | W15 | Kerrid's standing shape at the seaward end. |
| B09 | W16 | One locked shot at dusk plus inserts on hands and sand. Never an insert that could read the collar's name. |
| B10 | W10 (dawn) | The ash skin on the water fills the lower third. |

---

## 8. Word counts

| Beat | Words (budget) |
|---|---|
| B01 banters | 90 |
| B02 | 15 |
| B03 | 140 |
| B04 tutorial and barks | 55 |
| B05 | 210 (Sefir ~125) |
| B06 | 90 |
| B07 | 90 |
| B08 barks | 40 |
| B09 side scene | 150 |
| B10 | 30 |
| **Total** | **~910 written, ~760 on a typical path without the side scene** |

At 26.5 critical minutes, Ch6 is about 1.5% of a 30 h main story, so its fair share is **590–880 words**. It's at the top of the band because of B05, which carries the antagonist's introduction and is staged line by line by ADR 0017. Hold everything else to budget.

---

## 9. Requests to other roles

### Environment
1. **`ch06/brine_shoals` zone and `brine_shoals.md` mood brief.** Kit "Brine Shoals": silted mud-flats (`silted_flats` water look, validated), wreck-ridges built from Lit Age hull plating and wooden hulks, tide-channels, Saltwright chalk camp-signs (a decal set), and a wayside Level-stone shrine set in a wreck's bow. **The shoal channel must be wide enough for the Warden's barge** (ADR 0017 Environment). Shots W01–W16 as in §7.
2. **Saltwright camp kit** (scrap-tech, SPEC §7.4): lashed tent-hulls, tide-wheels, windmills, lamp racks, salvage crates, a burnable hulk with a hold the party can stand in. **Two states:** intact (reusable for Hollowmere's look in Act II–III) and burning (B03–B06, with fire, smoke, and a collapsing tide-wheel).
3. **Order props:** the salt brazier and brine-irons on long hafts; Stillguard torches.
4. **Sefir's white barge** (hero prop): long, low, white-lacquered, gold Level symbols at the bow, four Reed poler positions, a bow platform for Sefir. Order marble-and-gold kit. **The water material under and behind it must show no wake** (with Rendering, item 6).
5. The tideline at dusk for B09: wet sand that takes a hand-print, a diggable patch (a two-state mesh: open hole, covered).

### Art and Rendering
6. **No wake** behind the barge: the water shader's wake and ripple response is suppressed in a volume that moves with the barge, and the iron's hiss (B05 (4)) is the one ripple. This is also Ansedra's technique (Ch13–14), so build it once.
7. **Color script `ch06`:** confirm the frame (15:30). Requests: a `ch06_hold` interior sub-frame (the dark hold, keyed only by Rhen's `oil_lamp`), a `ch06_dusk` sub-frame for B08–B09 (sun about 2°, smoke-red), and a `ch06_dawn` sub-frame for B10. The barge is "the only clean white in the frame".
8. **Sefir's revenant tells** (sefir_aurane.md): no breath cycle; his reflection doesn't ripple. Both must be on from his first appearance.
9. One `glimmer_held` mote out of the sand in B09, seaward, about 3 s.

### Character Art
10. **Sefir Aurane** must exist for Ch6 (sefir_aurane.md silhouette: the right-shoulder gold half-mantle, the bowl halo-crown, the pale-blue silk, no idle motion).
11. **Liss Varrow** must exist for Ch6 (line-marks on the right arm, collarbone and neck; the copper mesh work-sleeve on the left; the launcher; the bead-tail).
12. **The Stillguard Inquisitor is a person, so the character track builds him** (confirmed): Inquisitor Hadric Moll, forties, red-lacquered shell armour with an Inquisitor's white sash, a round shield, a long-hafted brine-iron. Silhouette: the standard Stillguard plus the long iron held upright like a standard.
13. **NPCs:** Stillguard (a set of six variants, if the existing set is short), an Order clerk, four Reeds (the polers), and Saltwright wrights (a set with visible line-marks on their pushed-up sleeves, including the girl at the brazier and two children).

### Creatures and enemies (ids from the creatures track, 2026-10-24)
14. **`shoal_skipper`** (kept): a dog-sized mudskipper, a quick striker with low HP, that skims the flats in bursts. Answer: Rhen (fast, evasive foes are his, SPEC §6.1 and rhen_sallow.md). Silhouette: a blunt head with goggle eyes on top and a long, low body propped on fins.
15. **`wreck_crab`** (kept): a reef-crab variant and a defender with a new skill. *Story dressing request:* it lives in **broken Lit Age lamp housings** the way a hermit crab lives in a shell, so its back glows faint `glimmer_bound` teal. It puts the bound dead into the shoals' ecology before the crate. Answer: Kerrid or Toma's Shell Breaker.
16. **`gull_harrier` (reuse, no new asset)**: the existing flier, so the shoals have a flier and Rhen's niche keeps coming up. If the creatures track prefers a palette variant ("wreck gull"), fine.
17. **`raid_hound`** (kept): an Order shoal-hound, lean, long-legged and barrel-chested, mud-coloured, with a red-lacquered muzzle cage. It **protects the Inquisitor** (it intercepts single-target attacks on him and pounces on whoever strikes him; §5). It is driven off at 0 HP and never killed. Silhouette: a greyhound's legs under a mastiff's chest.
18. **Foes on screen per encounter:**
    - `ch06/brine_shoals` wreck-ridges: **2–3** (e.g. 2 `shoal_skipper`; 1 `wreck_crab` + 1 `shoal_skipper`; 2 `gull_harrier`).
    - `ch06/brine_shoals` mud-flats (the short-cut): **3–4** (e.g. 3 `shoal_skipper`; 2 `wreck_crab` + 1 `shoal_skipper`; 2 `shoal_skipper` + 2 `gull_harrier`). Riskier ground, bigger groups.
    - The camp (B03–B09): **none** apart from the boss, **2** (the Inquisitor and the hound).
19. **Encounter tables** for the ridges and the flats, using these groups.

### Combat
20. **The Inquisitor encounter** (§5): `forbidden_skills` for Toma in this encounter, the greyed-command tooltip, Toma's non-damaging counter for this fight, the **yield** end condition (the Inquisitor at 0 HP yields, the hound flees), the hound's intercept and pounce, Brine Iron (damage plus Weakened), Shell Wall, and the Smoke field (Darkness each round). Band and loadout as in §5. No escape (scripted).
21. **Liss's character data** in `characters.json`: item specialist (steal, combine, gadgets that apply statuses or alter turn order), her Swell (the *reel-stop*), her Lattice start. She joins at B06, with her first fight in Ch8 (Ch7 has no foes).

### UI
22. The greyed-command state and its tooltip ("Toma will not strike the Stillguard."); the yield banner ("The Inquisitor yields." in place of the victory banner); the two tutorial prompts in §5.

### Audio
23. The cues and SFX in §6. The two that matter most: the **Stillguard hum** in `raid` (calm, unaccompanied men's voices, the Order's own tune), and the **silent poles** in `barge_pole`. And `sefir_theme` is the first full resolution in the score.

### Cinematics (reviewer)
24. B05 against ADR 0017 (a), item by item. **He must read as kind on a first play**: no reaction shot that undercuts him, no ominous sting, no glare. Liss's line comes only after the barge has gone.
25. B03: Toma's freeze held past comfort, and Asha's two "Toma"s. B07: Asha out of frame.
26. Marks and anim clips (proposals): `kneel_palms_flat`, `hold_rib_on_shoulder`, `bow_from_barge`, `pole_barge`, `iron_into_water`, `dig_sand`, `flatten_sand`, `stand_watch_seaward`.

### Systems and Tech
27. **New speakers:** `inquisitor` (CHAR_INQUISITOR, name key for "Inquisitor Moll"), `clerk` (CHAR_CLERK), and `wright` (CHAR_WRIGHT) for any Saltwright barks.
28. **Grades** for `cues.json`: `ch06`, `ch06_hold`, `ch06_dusk`, `ch06_dawn`.

### Ch8 owner (M3-C08-01)
29. **Seam:** the wrights Sefir sends "up to Corrow" in B05 are at Corrow in Ch8. Some of them can be among the low town on the Fisher Stair, or on the wall-work gangs, still unbranded and still not free. Offered, not required.

### Lead
30. **Glossary rows:** brine-iron, Inquisitor (a Stillguard officer who enforces the Edicts), raid-hound, camp-sign (the Saltwright chalk mark), Inquisitor Hadric Moll.
31. **A decisions_log entry** for the burned lamp's design truth (§4), if Narrative is to use it later.
