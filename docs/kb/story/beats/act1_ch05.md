# Ch5 Beat Sheet: "Terraces of Ash" (Pemakar and Ashcrown)

Owner: Narrative (M3-C05-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch5](act_outline.md), [bible §5.2](../bible.md), [voice guide](../voice_guide.md), [Vowbound §2 Kahre](../vowbound.md), [kerrid.md](../characters/kerrid.md), [color script `ch05`](../../art/color_script.md), [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md), [ADR 0017](../../decisions/0017-act-one-restaging.md) (the Ch5 row and watch), [ADR 0020](../../decisions/0020-kerrid-restaging.md) (d), [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (no rope-burn glow in Ch5), [decisions_log N-01](../decisions_log.md) (Asha's first reach-band). Format: [vertical_slice.md](vertical_slice.md).

Scripts: not written yet. The `.dlg` files are the playable task's (M3-C05-02). Sample lines below are here to set the voice; the full dialogue is written against this sheet.

Seams: Ch4 (M3-C04-01) ends with the Brightwater ferry coming in to Pemakar's harbour with the drowned trader's name-board aboard. Ch6 (act1_ch06.md) opens on the road down to the Brine Shoals on the morning of day 3.

---

## 0. The chapter in one paragraph

The pilgrimage comes ashore on a mountain that floats its dead down to the sea every year, and the party arrives on the one night it does. A thousand leaf-boats go down the terrace channels past the graves, the whole town walks down beside them, and at the bottom, where the last weir spills the little fires into the sea, a big man in a straw cape catches a child by the collar before she falls in. He looks at Asha as if he has seen her face before, hears Rhen's surname, says one sentence to her about her mother, and walks behind them from then on without being asked. The next day Asha's guardians carry a lightning strike down the stair-mountain of Ashcrown on its own copper veins, quiet the old forge-keeper at its foot, and Asha binds a seventy-one-year-old smith who has been waiting three hundred years to put his hammer down. The player should finish the chapter warmed by the festival, and uneasy about two things nobody comments on: which way the dead go when you float them, and a stranger who never eats.

**Emotional line:** arrival with something earned (Asha's first band) → a market among the graves → wonder (the mountain alight) → a cold edge (the motes follow the boats down) → a held breath (the stranger at the weir) → a long climb in company → craft and effort (the strike walked down) → weight (the Matron) → a grumpy, joyful binding → a man who stands all night at the gate.

**What the chapter must deliver** (act_outline Ch5, ADR 0017 and 0020): Lanternfall among the graves (pillar 2); Kerrid joining at the festival's edge on his way to Corrow, with exactly one line to Asha and none to Rhen; the copper-vein trial; Kahre bound (Lightning); the Cinder Matron, two phases, armour-breaking, introducing Kerrid's niche; the smith's side scene.

---

## 1. Running order

Time is in-world (two days). Minutes are the player's, at a first-time pace. **P** = playable, **C** = letterboxed cutscene, **E** = in-engine scene (no letterbox, the player keeps the camera rail). Shot ids are proposals (§7, requested from Environment in §9).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The ferry comes in** | `ch05/pemakar` harbour | day 1, 19:10 | E | 1.0 | P01, P02 | `pemakar_terraces` | Arrival with something earned. Asha's first reach-band; the mountain above them already being dressed in small fires. | `ch05_arrived` |
| B02 | **Pemakar before the boats** | `ch05/pemakar` market terraces, forge lane, grave terraces | 19:15 | P | 6.0 | P03, P04, P05, P06 | `pemakar_terraces` | A market among the graves. Everyone is folding boats for someone. | `ch05_heard_straw_cape_tale` (optional bark) |
| B03 | *Side scene: The Smith's Question* (optional) | `ch05/pemakar` forge lane | any time in B02 (fallback in B11) | E | 4.0 | P07 | none (forge ambience) | A father asks what his son's town looked like. The truth, then a better version. | `ch05_told_the_smith` |
| B04 | **Lanternfall, part 1: the boats** | `ch05/pemakar` the crown channel and terraces | 20:00 | C | 3.0 | P08, P09, P10 | `lanternfall` (diegetic) | Wonder. The mountain becomes a waterfall of small fires. Then the cold edge: the held motes over the graves follow the boats down. | `ch05_boat_for_kell` / `ch05_boat_for_oruvel` / `ch05_kept_leaf_boat` (choice) |
| B05 | **Lanternfall, part 2: the weir** | `ch05/pemakar` the sea-cut weir | 20:25 | C | 3.0 | P11, P12, P11 | `lanternfall` → `kerrid_stair` (first statement) | A held breath. A stranger at the festival's edge, one sentence about a stair, and a man who simply falls in at the back. | `ch05_met_kerrid` |
| B06 | The inn gate | `ch05/pemakar` inn | 21:40 | E | 1.0 | P06 (night) | `lanternfall` (distant) | The first clue: he won't come in and he won't eat. | — |
| B07 | **The pilgrim stair** | `ch05/ashcrown` outer stair, tiers | day 2, 11:30 | P | 6.0 | A01, A02, A03 | `ashcrown_tiers`, `battle_standard` | A long climb in company, with the new man last in line. Kerrid's first fights. | — |
| B08 | **The Ashcrown trial: walking the strike down** | `ch05/ashcrown` crown to anvil court | 13:00 | P | 7.0 (+1.5) | A04, A05, A06, A07 | `ashcrown_trial` | Craft and effort. Lightning running down a mountain like water down the terraces. | `ch05_found_quench_charm` (optional) |
| B09 | **Boss: the Cinder Matron** (two phases) | `ch05/ashcrown` anvil court | 13:40 | P | 6.0 | A08, A09 | `cinder_matron` (2 stems) | Weight. Something old and tended, woken by the anvil's ring. Kerrid's niche. | `ch05_matron_quieted` (battle result) |
| B10 | **Kahre** (the binding and the second verse) | `ch05/ashcrown` Kahre's chamber, anvil court | 14:00 | C | 3.5 | A10, A11, A12, A08 | `ashcrown_trial` → `silence` → `hush_second_verse` | Grumpy joy. The oldest Cantor on the roll is impatient with her, and she likes him. The mountain answers the verse with thunder, and nothing comes. | `ch05_kahre_bound`, `ch05_second_verse_sung` |
| B11 | Pemakar after | `ch05/pemakar` | 16:30 → day 3, 06:30 | P → E | 2.0 | P04, P02 | `pemakar_terraces` (day) | Spent wicks in the sea-cut. A man still standing at the gate at dawn. | — |

**Totals:** critical path **38.5 min** (B01, B02, B04–B11). With the side scene and the trial's optional reward, **44 min**. Split: **21 min playable (55%)**, 9.5 min cutscene, 8 min in-engine. The higher cutscene share than the slice's is the festival, which is the chapter's reason for being; nothing else in the chapter runs long.

**Cut order if the chapter runs long:** B06 folds into B11 as one shot (the bowl on the gate post at dawn). B02 loses one bark area (the lacquer workshop). B07's three banters drop to two (keep Ysolde on Daro). Then B11 becomes a 0.5 min E beat on P02. **Never cut** B04's motes following the boats, B05 in full, the Matron's two phases, or Ysolde's "Lift your chin" in B10.

---

## 2. Beat detail

### B01. The ferry comes in (E, 1 min)
- P01: the Brightwater ferry noses into Pemakar's harbour at the mountain's foot. Above it, every terrace channel is already being dressed: people walking the tiers with lamps, setting out folded boats. The name-board from Ch4's dead trader goes ashore first, carried by the ferry-master to the harbour's wake-wall (the Low Reaches sea-law of [bible §5.1](../bible.md) is kept everywhere ships put in). One camera insert; no line.
- **N-01:** on the gangplank Rhen notices the new band on Asha's left forearm. ~30 words:
  > **Rhen:** That's new.
  > **Asha:** My first. Toma's hand shook.
  > **Toma:** It did not.
- Ysolde, with the Tenders' letter: the trial is at noon tomorrow, "when the plume is awake." Tonight is Lanternfall. *Grade:* a `ch05_harbour_dusk` sub-frame (sun about −3°) is requested from Art (§9); if it isn't built, B01 plays under the `ch05` night frame.

### B02. Pemakar before the boats (P, 6 min)
The town loop climbs: the harbour (P02), the market terraces (P03), the forge lane (P04), the grave terraces beside the paddies (P05), and the inn on the third tier (P06). **Systems on show:** an equipment shop (the first smith-made weapon tier, Kerrid's included), a lacquer-goods shop (accessories), the inn, and a save shrine set into an open-hand gate.

**Barks** (overheard as the player walks past, ~140 words in total):
1. *Grave terraces:* a woman sweeping a grave-step around a lacquer shrine-box: *"Mind the rice, love. That's my mother's."*
2. *Market:* two boat-folders: *"Fold toward you. Always toward you." "And for strangers?" "Away."* (This is the rule the B04 choice uses: Rhen launches at the strangers' channel.)
3. *Lacquer workshop:* *"The Cantor's in town. Gold leaf's doubled."*
4. *Forge lane:* a child, looking up at the crown as dry lightning flickers in the plume and the crack comes after: *"One... two... three. Daro's at his anvil."* Pemakar calls the plume's thunder "Daro's hammer" and has for three hundred years. Nobody here knows it is literally true. It plants Kahre before the binding.
5. *Grave terraces, a child:* *"Last year mine went all the way down to the sea. All the way!"*
6. *Harbour (optional, sets `ch05_heard_straw_cape_tale`):* an old ferryman to his mate: *"Big man in a straw cape. Pulled my nephew off the reef at Sennet, walked off before anyone could thank him. My sister swears to it."* **Watch (ADR 0017, 0020 (b)):** this is the anonymous fisher's tale of kerrid.md. It is heard *before* B05, never in Kerrid's sight, and nobody in the party connects it to him in Act I. Nobody calls the man a hero.

### B03. Side scene (optional): "The Smith's Question" (E, 4 min) — see §4

### B04. Lanternfall, part 1: the boats (C, 3 min)
- **P08, 20:00:** the bell at the crown pavilion rings once. Every household sets its boats on the water at once, at its own grave's channel, and the mountain goes from dark to a thousand small fires in about four seconds. (Rendering: the light-up is a wave down the terraces, top to bottom, not all at once.) This is the chapter's "gorgeous and doomed" frame (pillar 2).
- A Pemakar elder puts a folded boat into Asha's hands with a pinch of rice already in it. She floats it at the strangers' channel for her mother. No speech; she holds it a moment before she lets go. **Watch (ADR 0017 Ch5 row):** Asha leads no rite. She is a guest, given a boat like anyone else. No dance, no platform, no staff raised over the water.
- **Rhen's boat.** A boat-seller gives him one with its own wick. **Camera insert:** his hand goes to the tin at his belt where Kell's wick is, stays there a moment, and comes away; he uses the seller's wick. (ADR 0022 sweep-H watch: Kell's wick stays unburned until E7. This is the first time the player sees him decide that, and nothing names it.) **Choice:**
  - "For Mother Kell." sets `ch05_boat_for_kell`.
  - "For Oruvel." sets `ch05_boat_for_oruvel`.
  - "Not yet." (he keeps the boat, folded, unlit) sets `ch05_kept_leaf_boat`. Asha doesn't press him: "Then carry it till it's time."
- **P09, the procession:** the town walks *down* the terraces beside its boats, and the party with it. The camera rail follows the channel steps; the player holds a slow walk input (the only input in the beat).
- **P10, the cold edge:** over the grave terraces the faint held motes (`glimmer_held`, color script `ch05`, energy 0.8) come off the graves and drift sideways and down **after the boats**, toward the sea. Asha, a hearer, goes quiet. ~40 words:
  > **Rhen:** They're coming with us.
  > **Asha:** They follow the boats down. They always do.
  > **Rhen:** Is that good?
  > **Asha:** *(a held beat, `@wait 1.0`)* It's what they do.
  > **Toma:** Level preserve them.

  *Do not surface:* this is the Order's Ebbing in folk form, a custom it absorbed (bible §4, "Leaf-boats"). The player has seen released light go **up** off Asha in Ch3. This is the first time they see a whole town lovingly send its dead the other way. It must look beautiful on a first play and quietly wrong on a replay. Nobody comments.
- If `ch05_told_the_smith`: a camera insert of Garo's boat, too big and badly folded, going past in the forge-lane channel with its wick guttering, still afloat.

### B05. Lanternfall, part 2: the weir (C, 3 min) — *the Kerrid beat*
The bottom of the town is the **sea-cut weir**, a last stone lip where the channels spill over into the sea. The boats tip over it one after another and the sea-glow (0.08) takes them. It is the edge of the festival in both senses: the lamplight ends here, and past it is dark water.
1. **P11:** a child leans out over the weir after her snagged boat, and slips. A big hand in a wrapped sleeve takes her by the collar and sets her back on the step. She stares up. He is already looking out to sea. No line. *(This plants the Ch8 collar grab and the hand that fixes Rhen's collar in E3. Watch (ADR 0022 (g)): **no glow on his hands**, at all, in this or any Ch5 shot.)*
2. **P12, the look:** Asha, following her own boat down, is two steps away. He sees her face in the lamplight and goes completely still (gesture slot, `@wait 1.2`, no face change: he has seen this face before, younger, at a gate). She doesn't know why he's staring and doesn't mind.
3. Rhen arrives above them on the channel steps, slipping. Toma, by reflex: "Rhen Sallow, if you fall in that channel I am not coming in after you." **Kerrid's head turns at "Sallow."** Gesture slot: one look at Rhen, held 1.0 s, then away. *(He has just heard the name of the diver whose line he held. Nothing shows it but the look.)*
4. **The line.** He speaks to Asha, unprompted, and it is the only thing he says to her in Act I before Ch15 ([voice guide](../voice_guide.md), ADR 0020 (d)):
   > **Kerrid:** I held a stair for your mother once.

   Asha's stillness (`@face asha neutral 0.2`, `@wait 0.8`), then gently: "Where?" He doesn't answer. He looks out to sea. Asha, patient: "...Then another time." (asha_velamir.md: she knows that much and is patient about the rest.)
5. **Toma steps in**, courteous and wary, a guardian checking a stranger. ~40 words:
   > **Toma:** Your name, sir?
   > **Kerrid:** Kerrid.
   > **Toma:** And where are you bound?
   > **Kerrid:** Corrow.
   > **Toma:** The Lady Cantor's road goes by Corrow.

   Kerrid says nothing. **Watch (ADR 0017, 0022):** Toma served seven years on the Corrow wall and knows the stair-watch's story, but **he doesn't know the face** and nothing in his reading may suggest recognition. Play it as a guardian sizing up a big armed man, no more. Nobody names Corrow's dead captain. Nobody hails him.
6. Ysolde, dry: "Then he will be walking our way whether we like it or not." Asha: "He's going where we're going, Toma." She doesn't invite him and he doesn't ask (ADR 0020 (b): **he asks nothing**).
7. **P11, the close:** the party starts back up the terraces to the inn. Kerrid falls in **at the back of the line**, last, as on a stair (this is the line order the Pale Rim pays off in Ch16). `kerrid_stair` enters: a slow walking rhythm, the motif whose slowing to a stop is `goodbye_kerrid` in E3. Rhen, walking backwards to look at him:
   > **Rhen:** Does the old man come with the town, or did we just collect him?
   > **Asha:** Rhen.

   That is where the player's "Old Kerrid" comes from. **He says nothing to Rhen in this chapter** (ADR 0020 (d)); every Kerrid beat with Rhen in Ch5 is a gesture.
- Sets `ch05_met_kerrid`. Kerrid joins the party roster at the end of this beat (§9, Combat).
- *Story logic (do not surface):* he was walking to Corrow because the Undertow stirred early this year (ADR 0022 sweep-G S8). He walks with them because they are going where he is going, and because of a face and a surname. He is no guard on Asha.

### B06. The inn gate (E, 1 min)
The party takes rooms. Kerrid declines the inn with a shake of the head and stands at the gate. Rhen brings him a bowl from the kitchen. Kerrid takes it, sets it on the gate post untouched, and goes back to watching the dark toward the sea. **No line from Kerrid.** Rhen: "...Suit yourself." He takes the bowl back in and eats it himself on the step, keeping him company without meaning to. ~10 words. *Clues planted (kerrid.md):* he never eats, he declines inns. Both are played as a quiet man's habits.

### B07. The pilgrim stair (P, 6 min)
The outer pilgrim stair climbs the caldera lip tier by tier (A01, A02), through terrace graves and old Lit Age copper showing green through the stone (A03). The plume crackles at the crown. The camera rails favour A01 and A02 so the climb reads as a line going up into ash.
- **Encounters:** `ashwing` (fliers that put the party to sleep: Rhen, or Ysolde's fire), `slag_tortoise` (armoured: Kerrid's first answer; the first encounter after B05 is a scripted pair of slag tortoises so his sundering blow is introduced on something small), and one proposed caster, `vein_sparker` (Ysolde). See §9 Creatures. Music: `battle_standard`.
- **Three walking banters** (field barks at marker points, ~90 words in total):
  1. *The Tenders' gate (A01):* Ysolde reads the roll aloud. "Daro Pemakan. The thirty-sixth. Seventy-one years old. The roll records that he complained the whole way." Asha: "Good." Rhen: "Good?" Asha: "Somebody should." (Warmth, and a crack in her for the player who listens.)
  2. *The grave tier (A02):* Rhen asks why the graves are on the road up. Toma: Pemakar buries its dead where the water passes, so the channels visit them every day.
  3. *The copper tier (A03):* Rhen turns to Kerrid, last in line: "You're not even breathing hard." Kerrid looks at him and says nothing. Ysolde: "Some people are simply fit, Master Sallow." *(The clue: he doesn't breathe hard because he doesn't breathe. Ch12 spends the breath; this only plants it.)*

### B08. The Ashcrown trial: walking the strike down (P, 7 min, +1.5 optional)
Ashcrown is a stair-mountain built into the lip of a caldera that still breathes ash. The party climbs the *outer* stair to the crown, then the trial carries the strike down the *inner* tiers to the **anvil court** at the mountain's foot, where Kahre's chamber is. A Tender (Tender Ruwen, new speaker) opens the crown pavilion and gives the rite in two lines: the strike must reach the anvil "before it forgets where it was going". ~30 words.

**The puzzle (SPEC §6.6, "lighting channels"):**
- **Catch.** At the crown, the copper catch-spire draws a strike from the plume on a visible, regular rhythm (a crackle telegraphs it about 3 s ahead). The strike charges the crown's copper bowl, which glows white-violet. **Lightning is not glimmer:** its VFX is white-violet and never gold, cyan or teal (§9 Rendering), so it can't be misread in the mote language.
- **Fade.** A ring of copper studs around the bowl is the timer: one stud goes dark for every few metres the player walks, so the clock is counted in steps, not seconds (pillar 4, no twitch). The ring is diegetic; there is no HUD timer.
- **Carry.** Each inner tier has copper veins inlaid in its floor, broken by **vein-gates** (bronze discs that rotate in 90° steps, set by a floor lever). The player sets the gates to close a circuit from this tier's bowl to the downspout at the tier's edge, then pulls the release. The strike runs along the veins and pours over the edge to the next tier's bowl, like water down the terraces (bible §5.2), and the stud ring there starts its count. The player walks down after it.
  - *Tier 1 (crown):* one gate. Teaches the loop.
  - *Tier 2:* two gates and a dead-end vein that grounds into an ash drift. Routing into it loses the charge.
  - *Tier 3:* gates linked in pairs (turning one turns its twin), plus the sealed side vein to the quench-trough alcove (the optional reward, below).
  - *Tier 4:* the veins run under the grave-steps of past Tenders, and a gate opens only while someone stands on its plate. The party member on the plate is shown standing there (Toma, by default), and the player sets the rest.
- **Retry cost.** Every tier has its own catch-rod, so a lost charge is re-caught at the tier where it was lost, never back at the crown.
- **The landing.** The last run pours into the anvil court and strikes the anvil-stone at the mountain's foot: a white flash, and a beat later the crack of a hammer on an anvil (`anvil_crack` SFX, the Kahre motif of vowbound.md §2). The crack wakes the Matron. → B09.
- **No dialogue during the puzzle** beyond one Tender hint bark after 90 s idle on any tier ("Follow the copper, not the stair.").
- **Optional:** route the tier-3 charge into the sealed side vein first. It costs the charge (re-catch at tier 3) and opens the quench-trough alcove: the **Quench Charm**, an iron charm a smith dips in the trough before a big piece of work (accessory, Fire ward). Sets `ch05_found_quench_charm`. It is useful in B09, and B10 pays it off with one line.

### B09. Boss: the Cinder Matron (P, 6 min) — see §5

### B10. Kahre (C, 3.5 min) — *the binding and the second verse*
- **A10:** the Tender opens the chamber behind the anvil-stone. Asha goes in alone, by rite, as at the Shell Shrine. A short exchange at the threshold, ~25 words. Toma: "We will be here, Lady Cantor." Asha: "Toma." Toma: "...Asha." (Rung once, because Ch3 rang it; here it's already easy between them.) **Watch (ADR 0017 Ch3 row):** no stumble or catch at the door on her way out, and no summon shown at the door.
- **A11:** a single held frame of the chamber: Kahre is **bound** light (`glimmer_bound`: steady, never drifting) with white sparks running in his mane that never fall. The keepsake hammer is a dark shape in the casque. Don't show the full form: save it for the first call's cinematic. Fade.
- **A08, the wait:** the others in the anvil court. Rhen fills the silence and talks to the room. Kerrid stands at the court's sea-facing arch. **Gesture slot:** Kerrid's eyes go once to the lantern on Rhen's shoulder, and away (`@wait 0.8`). *(He worked eight low tides beside its twin at Corrow. Nobody sees him look except the camera.)* Rhen catches it and grins: "You've got a look like you're pricing it." Kerrid says nothing. Ysolde and Toma, ~40 words: Ysolde on what the roll says Daro did on his pilgrimage ("He repaired the hinges of every temple door he passed through. Unasked."), Toma's soft laugh.
- **A12, Asha comes out:** walking, smiling, a little scorched-looking around the eyes. Released light lifts off her skin in slow upward spirals (`glimmer_lift`, warm gold), less than in Ch3: the second time is not the first. **The second band** is on her verse-sleeve (sleeve state S2). ~30 words:
  > **Rhen:** Well?
  > **Asha:** He was impatient with me. *(a laugh)* I liked him very much.
  - If `ch05_found_quench_charm`: Asha sees it on Rhen's belt. "He'd have wanted that back, I think. He said nothing about it. Keep it." *(It's an Act I flavour line; the keepsake is the hammer.)*
- **The second verse.** Ysolde gives the custom in one line: "The first verse is sung toward home. The second is sung to the mountain that taught it." Asha faces the crown, up through the court's open roof into the plume. Four `#sung #lamptongue` lines over `hush_second_verse`: *Ish karra, ish karra, / vey hal ennu, / re ish, re ish... / ...mir.* (Constructed from the bible's roots: roughly "light gathers / water, shell, sleep / again light / stay". Audio sets the final text; the translation is never shown; it ends on *mir*, like every verse.)
- **The answer.** On *mir*, the plume flashes white over the crown, and a beat later the thunder comes. Rhen braces, hand on his hooks, looking at the floor:
  > **Rhen:** Is something going to come up out of the ground again?
  > **Toma:** *(gently)* Not this time, I think.

  Nothing comes. It is only Daro's hammer. *(This is a deliberate rhyme with Ch3, where the verse drew the Drownbell. The joke is Rhen's real fear, remembered, and it lands as relief, not a wink. Pillar 1: it is the only joke in B10.)*
- **Ysolde's warmth** (voice guide tell): as they leave the court, not looking at Asha: "Lift your chin when you sing. It is better for the breath." Asha: "Yes, Scholar." She is beaming.
- Sets `ch05_kahre_bound` (Kahre callable from here on) and `ch05_second_verse_sung` (sleeve band 2).
- *Not here:* Kahre has no voice in Act I (like Ilun, the Vowbound speak at their Ch20 releases). His line to Kerrid, "It doesn't hurt, son", is Ch20's. No look passes between Kahre and Kerrid in A11; Kerrid is outside.

### B11. Pemakar after (P → E, 2 min)
- **16:30, P04:** the town in afternoon light, wrung out after the festival. The barks change to after-festival talk: who's fishing burnt-out boats from the sea-cut, a grave-step swept clean, the Cantor's band ("Two, already!"). The smith's side scene is available here as a fallback if missed in B02, with one changed opening line (his boat has already gone down; he asks anyway).
- **Day 3, 06:30, P02 (E, 0.5 min):** the party comes down to the harbour road at dawn. The sea-cut is full of spent leaf-boats rocking in the shallows, every wick out. Kerrid is at the inn gate exactly where he was at 21:40; nobody saw him move. The bowl from B06 is gone from the post (the innkeeper took it in). He falls in last. No line. Ch6 opens on the road down to the Brine Shoals.

---

## 3. Flags

All new flags are to be declared in `game/data/flags.tres` by the playable task (M3-C05-02), with the descriptions given here. Read and write them only through `Game.get_flag` / `Game.set_flag`.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch05_arrived` | B01 (end) | zone gating, Pemakar barks | — |
| `ch05_heard_straw_cape_tale` | B02, harbour bark (optional) | Ch15 | In Kerrid's confession at sea, Rhen can say it: "The straw-cape man. The ferryman's nephew. That was you." Kerrid: "Probably." (Ch15 owner's call; offered.) |
| `ch05_told_the_smith` | B03 (end) | B04 camera insert; Ch18 Pemakar revisit | Ch18: Garo is forging mooring rings for rebuilt Oruvel and asks Rhen to carry the first one. (Proposed to the Ch18 owner.) |
| `ch05_boat_for_kell` | B04 choice | Ch7 B03 | Rhen to Tavi: "I sent her a boat at Pemakar. Too much wick. She'd have said so." |
| `ch05_boat_for_oruvel` | B04 choice | Ch7 B05 | At the naming, when Tavi names "Oruvel", Rhen says "Up" with the crowd a beat before anyone (a face cue, no extra line). |
| `ch05_kept_leaf_boat` | B04 choice ("Not yet") | Ch7 B09 | The folded boat becomes a key item ("A Pemakar leaf-boat, unlit"). At Oruvel's empty moorings Rhen lights it from his lantern and sets it on the water. |
| `ch05_met_kerrid` | B05 (end) | party roster, zone gating, every later Kerrid beat | Kerrid is in the party from here to the Ending. |
| `ch05_found_quench_charm` | B08 optional pickup | B10 | Asha's line about the charm; the accessory's flavour text. |
| `ch05_matron_quieted` | B09 battle result | B10 trigger | — |
| `ch05_kahre_bound` | B10 | battle setup (`vowbound.json` `bound_flag`) | Kahre callable from here on; his Ch20 release. |
| `ch05_second_verse_sung` | B10 (end) | sleeve state S2, Ch6 B01 | Asha's verse-sleeve band 2. |

The three boat flags are mutually exclusive (exactly one is set). Story beats read them; nothing else does.

---

## 4. The optional side scene: "The Smith's Question" (B03)

**Where:** the forge lane on Pemakar's second tier (P07: the forge mouth, a smith's back lit by the coals, a half-folded boat on the anvil beside a hammer). **When:** any time in B02, through an NPC marker on the smith; fallback in B11. **Length:** 4 min, ~160 words. **Speaker to add:** `garo` (Garo Tenmak, a Pemakar smith, sixties, burn-scarred forearms, a big careful voice).

**Beats:**
1. Garo is trying to fold a leaf-boat with hands made for tongs, and making a ruin of it. He sees Rhen's lantern. "Oruvel make, that. You're a diver."
2. Rhen offers to fold it. He is good at it: divers fold, and tether-knots are folds. (Vary from Ch2, where Rhen helps Osu badly; here he is competent, and that is the warmth.) Garo watches his hands.
3. Garo's son **Benet** went to Oruvel at sixteen to learn to dive ("Said copper's cheaper if you cut it yourself.") and stayed five years. A trader brought the news. Garo: "He wrote that it was the most beautiful place on the sea. He was a terrible liar. What did it look like?"
4. **The truth.** Rhen tells him, plainly: hulls lashed together and rotting from underneath, oil smoke, everyone owing everyone, no ground anywhere to stand on. Garo nods. He'd guessed.
5. **Then a better version.** Rhen keeps folding. **Choice** (flavour only; both are true):
   - "When the divers come up at dusk, you see their lamps coming up through the water before you see their heads. Like the sea handing them back one at a time."
   - "Second mooring, on race days. Everyone yelling. Your boy yelled loudest. He always lost."
6. Garo: "Did you know him?" Rhen: "Tall. Burned his thumb on every lamp I ever saw him light." Garo laughs, and it catches. He takes the finished boat. "Fold toward you, they say. For your own." He turns it in his hands. "He'd have folded it away. Never could keep the rule straight." He floats it tonight in the forge-lane channel (the B04 insert).

**Rules:** no more than four lines from Garo in a row, broken by Rhen's hands and his answers (SPEC §3.6). Rhen does not joke in this scene. The "better version" is kindness, not a lie: everything he says is true. Garo's voice: plain, practical, slow, with a smith's habit of saying a thing once.
**Payoff:** sets `ch05_told_the_smith`. B04's insert of the badly folded boat; Ch18's mooring rings (proposed). It also gives Rhen, a boy who has told his own story funny for years, his first chance to tell someone else's straight.

---

## 5. The Cinder Matron (B09): placement, phases, and what it teaches

**Lore:** a Lit Age forge-construct, the keeper of the anvil court from when Ashcrown's copper was a working forge-line. Centuries of caldera heat have crusted her copper frame in magma-rock. Her core is **bound glimmer** (`glimmer_bound`, a steady teal heart behind the slag). The Tenders call her the Matron and tend her like an old relative: by custom she wakes when the anvil rings, and "tests the Cantor's guardians, never the Cantor". She is not Undertow-spawn and isn't malicious; she is doing the last thing she was made to do.

**Placement:** directly after the trial's last run (B08), in the anvil court, before the binding. That keeps Kahre out of the fight, so the armour lesson belongs to Kerrid. The Tender, as the strike lands: "When the anvil rings, the Matron wakes. Be gentle with her if you can." That's the only setup line.

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: the Crust** | The Matron unfolds from her alcove in the court wall, slag-crusted, glowing at the seams (A08). | **Crust:** very high physical defence; ordinary blows glance off. Every third turn she **banks the fire** (Protect on herself, telegraphed on the timeline). Kerrid's **sundering blow** (the Sundered status) cracks the crust for a few turns, and the timeline shows how long. His heavy blows cost a lot of time (the rank shows as a long push back on the timeline preview) and hit very hard. | The first armoured boss. A slow, heavy action is worth its time when the timeline shows the window it buys. It distinguishes Kerrid's sundering blow from Toma's lighter Shell Breaker (Combat, §9). | The new man is the answer to the old thing. He doesn't speak; he works. |
| **2: the Pour** (at 50% HP) | The crust breaks open and the molten core shows (A09): orange slag around the steady teal heart. The court floor's channels fill with slag (a field). | She hits harder (fire to the whole party). **Re-crust** is telegraphed **two turns out** on the timeline. **Water and cold quench her** and re-crust her at once: Ysolde's frost and **calling Ilun** are the *wrong* answers here. Lightning is her weakness (the copper frame), but Kahre isn't bound yet. Fire is absorbed. | Read affinities before you act; a Vowbound isn't always the answer. Time Kerrid's sundering blow for just after each re-crust, then burst. The Quench Charm (Fire ward) makes the slag field survivable. | A forge-keeper who keeps re-forging herself. She doesn't stop because she was never told she could. |

**End:** at 0 HP she doesn't break. She settles back into her alcove and **banks**: the slag cools from orange to black in about four seconds. Her bound core goes on glowing teal behind it, steady. **No motes rise from her** (she's bound; bible §2). Tender Ruwen: "She'll sleep now. She always does." *Quietly wrong:* the Order's kindly Tenders are tending a bound person, and nobody thinks of it that way.

**Tutorial text** (UI loc keys owned by UI/Combat), one prompt per phase: Phase 1: *"The Matron's crust turns blows aside. Kerrid can break it."* Phase 2: *"Water and cold will harden her again."*
**Battle barks** (≤ 25 words in total): Toma on the phase change, "She's opening. Hold." Ysolde when the player quenches her (first time only), "That was instructive." **Kerrid has no battle lines in Ch5.** His first battle entrance is a gesture: he unslings the anchor-cleaver and steps to the front without a word.
**Light:** the Matron's core is `glimmer_bound`. The slag is incandescent (`fire` VFX, not glimmer). There is no held cyan anywhere in the fight.

**Combat band** (balance_targets.md, Ch4–Ch9 boss): naive ≤ 5%, role_answer 65–85%, smart 75–92%, p90 ≤ 70. Party: Rhen, Asha, Toma, Ysolde, Kerrid, with Kerrid active at the start (three active, two in reserve). Loadout: a `ch05_matron` loadout of Pemakar's shop tier plus `ch03_ilun_bound` (so the sim can test the Ilun mistake), and the Quench Charm in a variant suite only.

---

## 6. Music cues

`silence` is the reserved id (fade the bed out). Every melody is original (SPEC §2); every cue below is a request to Audio (§9).

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `pemakar_terraces` | B01, B02, B11 | Town bed, loop | Gamelan-like metallophones in interlocking patterns, a bamboo flute, water running under everything. Busier than Haluna's; the festival is for the dead, not a departure, so it resolves. A day variant for B11. |
| `lanternfall` | B04, B05, B06 | **Diegetic** festival music | Played by the town on the terraces: gongs, a slow processional drum, many flutes slightly out of tune with each other. It thins as the procession descends, and at the weir only one drum is left. |
| `kerrid_stair` | B05 (close), later chapters | Motif, first statement (≤ 20 s) | A slow walking rhythm: low frame drum and a bowed two-note figure, heavy, patient. This is the motif that slows to a stop as `goodbye_kerrid` (ADR 0020 Audio). Here it starts, steady, as he falls in. |
| `ashcrown_tiers` | B07 | Field bed, loop | Dry wind, ash hiss, a plucked zither, distant thunder on a slow irregular pulse. A climbing figure that keeps rising. |
| `battle_standard` | B07 | Battle loop | The standing battle cue. |
| `ashcrown_trial` | B08, B10 (wait) | Temple ambience | Copper hum, the crackle of the plume, a far-off hummed congregation (the Order hums; bible §4), and a struck-metal tone each time a run lands. |
| `cinder_matron` | B09 | Boss, two stems | Stem 1: a forge rhythm, hammer-on-anvil on the downbeat, slow and grinding. Stem 2: adds low brass and a boiling string tremolo for the pour. |
| `hush_second_verse` | B10 | **Diegetic** Hush, verse 2 | The Hush theme's second phrase, sung (or carried by the vocalise-like solo instrument until SPEC §16 Q4/Q5 settle a voice) over a drone. Thunder on *mir* is part of the cue (timed to the plume flash). |
| `kahre_summon` | first call (any later battle) | Sting (≤ 6 s) | Struck anvil, a white crack, the Hush's second phrase on low brass. |

**SFX** (`@sfx`, requested): `plume_crackle` (the 3 s strike warning), `vein_run` (charge along copper), `anvil_crack` (flash, then the crack a beat later), `matron_bank` (slag cooling), `weir_spill` (boats tipping over the lip into the sea), `crown_bell` (B04's single bell).

---

## 7. Camera shots by beat

All shot ids are **proposals** for Environment's `pemakar.md` and `ashcrown.md` (§9). Every setup change between unrelated shots is a cut (`blend=0.0`, N-13 grammar); blends only for same-axis moves.

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | P01 → P02 | P01: the ferry entering the harbour, from the water, with the dressed mountain above. P02: harbour road, eye level, for the band exchange. |
| B02 | P03, P04, P05, P06 | Rail cameras. P05 (the grave terraces) is the default for the grave barks. |
| B03 | P07 | One locked shot at the forge mouth plus inserts on Rhen's hands folding. The coal-light keys both faces. |
| B04 | P08 → P09 → P10 | P08 is the crown-down wide: the light-up wave. P09 rides the procession down the channel steps (a slow dolly, the one move in the chapter). P10 is the grave tier from the side, the motes drifting frame-left and down after the boats. The Kell's-wick insert sits inside P09. |
| B05 | P11 → P12 → P11 | P11: the weir from the sea side, low, with the boats tipping toward camera and the dark past the lamplight. P12: a two-shot on the weir step, Asha in lamplight, Kerrid half out of it. Kerrid's look at Rhen is a cut to Rhen on the steps above (inside P12's axis) and back. **No close-up on Kerrid's hands at any point** (no glow, and nothing to see yet). Kerrid falling in last is P11 again, the line of lamps going up the terraces with one big shape at its tail. |
| B06 | P06 (night variant) | — |
| B07 | A01, A02, A03 | A01 is the default rail; banters fire on A01, A02, A03. |
| B08 | A04, A05, A06, A07 | A04: the crown and catch-spire (the strike). A05: the tier overview, player-toggled, like S03. A06: a run pouring over a tier edge. A07: the anvil court from above as the last run lands. |
| B09 | A08, A09 | A09 is the phase 2 framing (core visible). |
| B10 | A10 → A11 → A08 → A12 → A08 | A10 → A11 cuts on a short fade, like S07 → S08. A11 is a single held frame. Kerrid's look at the lantern is inside A08: Rhen in the foreground, Kerrid at the arch behind him, and a rack focus is acceptable (same axis). A12 is Asha at the chamber door, with the open roof and plume above her for the verse. |
| B11 | P04, P02 | P02 at dawn: the spent boats in the sea-cut, the gate, the shape at the gate. |

---

## 8. Word counts

Estimates against the budget; actual counts come from `tools/dialogue_stats.py` once the `.dlg` exist.

| Beat | Words (budget) |
|---|---|
| B01 | 40 |
| B02 barks | 140 |
| B03 side scene | 160 |
| B04 | 120 |
| B05 | 140 |
| B06 | 10 |
| B07 banters | 90 |
| B08 Tender and hint | 45 |
| B09 tutorial and barks | 45 |
| B10 | 200 |
| B11 barks | 60 |
| **Total** | **~1,050 written, ~890 on a typical path without the side scene** |

At 38.5 critical minutes of a 30 h main story, Ch5 is about 2.1% of the game, so its fair share of SPEC §3.6's 40–60k is **860–1,280 words**. It sits in the band. Kerrid's share is **3 lines, 10 words** (B05), which is the point.

---

## 9. Requests to other roles

Each item is written to be filed as a task as it stands.

### Environment (kits, zones, shots)
1. **`ch05/pemakar` zone and `pemakar.md` mood brief.** Kit "Pemakar terrace stone": dark volcanic stone tiers on a 0.5 m grid; terrace channels with running water (a flow path the leaf-boats follow); rice and taro paddies; **terrace graves** (low grave-steps, each with a black-and-red lacquer shrine-box); **open-hand gates** (two carved stone forearms, palms cupped toward each other: a hero mesh, used for the save shrine and the Tenders' gate); market awnings; a forge lane with three working forges; lacquer workshops; the inn on the third tier; the harbour at the mountain's foot with a wake-wall for name-boards. **Hero mesh: the sea-cut weir** (the last stone lip where the channels spill into the sea). Night and day variants. Shots P01–P12 as in §7, with lens and height per haluna.md §5's table format.
2. **`ch05/ashcrown` zone and `ashcrown.md`.** A stair-mountain built into the caldera lip: an outer pilgrim stair (A01–A03); four inner tiers with **Lit Age copper veins** inlaid in the floors (green-oxidised where worn, bright where the strike runs); **vein-gates** (bronze discs that rotate in 90° steps on a floor lever; a pair-linked variant; a pressure-plate variant); a copper bowl and a stud ring on every tier; a catch-rod per tier; the crown pavilion in red lacquer with the **copper catch-spire**; the **anvil court** at the mountain's foot with the anvil-stone, the Matron's alcove, a sea-facing arch, an open roof up to the plume, and Kahre's chamber door; the tier-3 **quench-trough alcove** behind a sealed vein. The sky is an ash plume with dry lightning in it. Shots A01–A12.
3. **Leaf-boat prop:** folded palm leaf, a pinch of rice, a lit wick (an `oil_lamp`-class flame, never glimmer). Needs instancing for ~1,000 on the channels at once, a "spent" variant (wick out, waterlogged) for B11, and a large badly-folded variant (Garo's).

### Art and Rendering
4. **Color script:** a `ch05_harbour_dusk` sub-frame (sun about −3°, B01), and a `ch05_ashcrown_day` frame for 11:30–14:00 (the existing `ch05` row gives the temple time as 13:00 but its values are the festival night's). Please also confirm the `ch05` night glimmer (`glimmer_held` 0.8) is the B04 grave motes.
5. **Lightning VFX** for the trial and Kahre: white-violet, never gold, cyan or teal, so it can't be read as glimmer. A strike, a charged bowl, a vein run, a pour over an edge.
6. **The leaf-boat light-up wave** (B04): top to bottom over about 4 s, and the held motes leaving the graves to follow the boats (bible §2's held drift, sideways and down, toward the sea).
7. **No rope-burn glow on Kerrid in any Ch5 frame** (ADR 0022 (g)). Please add it to the `ch05` frame's notes.

### Character Art
8. **Kerrid** must be built for Ch5 (his first appearance): kerrid.md silhouette, face per ADR 0020 (c) (bare, both eyes clear), left forearm wrapped, watch cord in faded watch-red, anchor-cleaver. No glow material on the arms before Ch10.
9. **Asha:** sleeve state S2 (band 2) from B10; reach-band 1 on her left forearm from B01 (N-01).
10. **New NPCs:** Garo Tenmak (smith, sixties, burn-scarred forearms, leather apron); Tender Ruwen (Ashcrown Tender in Order robes, soot on the hems); the B05 child; Pemakar townsfolk (a crowd set for the procession, with terrace work clothes and lacquer hairpins); the old ferryman.

### Creatures and enemies (ids from the creatures track, 2026-10-24)
11. **`ashwing`** (flier; answers: Rhen's precise strikes, or Ysolde's fire, since it is fire-weak). A festival-light moth the size of a gull, soot-grey wings with ember eyespots that read like a leaf-boat's flame in the dark, trailing ash. Its wing-dust puts the party to Sleep. Silhouette: broad flat wings wider than its body is long; it hovers. *Story fit:* it is drawn to the Lanternfall lights, which is why the terraces are thick with them this week. Kept as proposed.
12. **`slag_tortoise`** (armoured; answer: Kerrid). A low tortoise with a cooled-lava shell flecked with copper; it pulls in when struck. Silhouette: a dome on stubby legs. High defence, low agility. It is Kerrid's tutorial target in B07 (a scripted pair, the first fight after B05). Kept as proposed.
13. **`vein_sparker`** (caster; answer: Ysolde). **A proposed addition**, not on the creatures track's list. A lean lizard with copper-green scales that stores charge from the Lit Age veins and spits lightning; weak to water. Silhouette: a long tail held up in a curl like a coil. *Why the story wants it:* SPEC §6.1 asks that each encounter make a specific member's niche the answer, and with only a flier and an armoured foe the B07 climb never asks for Ysolde. It also puts the veins' charge into a living thing before the trial, so the copper reads as dangerous. If the creatures track would rather not add a foe, cut it and give one `ashwing` group a caster role instead; the story doesn't depend on it.
14. **`cinder_matron`** (boss, §5). **Confirmed: a construct, so it belongs to the creatures track.** A tall forge-construct, broad-hipped and matronly in outline: a copper frame like a kiln with arms, slag-crusted, with a ladle-hand and a tong-hand, and a teal bound heart behind the slag. Silhouette: a kiln with shoulders. Two phases (crust, then pour: the crust breaks), the re-crust telegraph, the quench reaction to water and cold, Fire absorb, Lightning weak, and the bank-not-break end state. Keep the name.
15. **Foes on screen per encounter:**
    - `ch05/pemakar` (town and grave terraces): **none**. There are no random encounters in the town or on the festival night.
    - `ch05/ashcrown` outer pilgrim stair (B07): **2–3**. Typical groups: 2 `ashwing`; 2 `slag_tortoise` (the scripted first fight); 1 `slag_tortoise` + 1 `vein_sparker`; 2 `ashwing` + 1 `vein_sparker`. The stair is narrow, so never more than 3.
    - `ch05/ashcrown` inner tiers (B08, the trial): **none**. The puzzle has no encounters, the same as the Shell Shrine.
    - Anvil court (B09): the Matron alone, **1**.
16. **Encounter tables** for the outer pilgrim stair (B07), using the groups above.

### Combat and Progression
17. **Kerrid's character data** in `characters.json`: heavy hitter, low agility, high strength; **Sundered** and **Weakened**; heavy high-rank blows; his Swell (the *weighted swing*, kerrid.md). His Lattice start node. He joins at the end of B05 and starts B09 active.
18. **Distinguish Kerrid's sundering blow from Toma's Shell Breaker** (the sandbox's crab answer), so the Matron reads as Kerrid's fight: e.g. Shell Breaker lowers defence a little for a short time; Sundered applies the full status for longer.
19. **Kahre** in `vowbound.json`: `bound_flag: ch05_kahre_bound`, caller Asha; raw lightning damage that ignores defence; Swell *Last Strike* (vowbound.md §2). The first call plays the full cinematic, in whichever later battle the player first calls him.
20. **Cinder Matron** encounter and boss band (§5); loadout `ch05_matron`.
21. **Quench Charm** accessory (Fire ward) in `equipment.json`, and the Pemakar shop tier.

### Audio
22. The cues and SFX in §6, especially `lanternfall` (diegetic and thinning), `kerrid_stair` (its first statement, which E3 must be able to slow to a stop), and `hush_second_verse` with the thunder on *mir*.

### Cinematics (reviewer)
23. Check B05 as a whole: the collar catch, the look at Asha, the turn at "Sallow", the one line, and Kerrid falling in last. **Watches** (ADR 0017, 0020, 0022): nobody hails Kerrid or names him a legend; Toma shows no recognition; no glow on his hands; he says nothing to Rhen anywhere in the chapter; he asks to join nothing.
24. B04: Asha floats a boat like any guest; no Cantor rite. The Kell's-wick insert must read as a hand that decides, with no line.
25. B10: Kerrid's look at the lantern (a gesture slot), the A11 single frame, and no stumble or catch at the chamber door.
26. Actor marks and anim clip names are proposals: `fold_boat`, `float_boat`, `procession_walk`, `catch_collar`, `stand_at_gate`, `set_bowl_down`, `step_on_plate`, `chamber_threshold`, `face_crown_sing`.

### Systems and Tech
27. **New speakers** for the `.dlg` work: `garo` (CHAR_GARO), `tender` (CHAR_TENDER, used again at later temples), `ferryman` (CHAR_FERRYMAN), and a generic `townsfolk` if `child`, `vendor` and `fisher` don't cover the barks. The B01 band exchange and B05 use existing speakers.
28. **Grades** for `cues.json` once Art builds them: `ch05`, `ch05_harbour_dusk`, `ch05_ashcrown_day`.
29. **Key item** `pemakar_leaf_boat` (set by `ch05_kept_leaf_boat`, consumed in Ch7 B09).

### Lead
30. **Glossary rows** (append-only, the Lead's): Lanternfall's "fold toward you" rule; the sea-cut weir; "Daro's hammer" (Pemakar's name for the plume's thunder); vein-gate; the Cinder Matron; Tender Ruwen; Garo and Benet Tenmak; the Quench Charm.
