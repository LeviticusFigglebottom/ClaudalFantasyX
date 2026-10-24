# Act I Beat Sheet: Ch8 "The Seawall" at Corrow (M3)

Owner: Narrative (M3-C08-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch8](act_outline.md), [bible §5.4 Corrow](../bible.md), [voice guide](../voice_guide.md), [Vowbound §3 Virel](../vowbound.md), [Kerrid](../characters/kerrid.md), [Pell](../characters/pell.md), [Liss](../characters/liss_varrow.md), [Toma](../characters/toma_okeru.md), [color script `ch08`](../../art/color_script.md), [battle_ctb.md](../../design/battle_ctb.md) (the engine this set-piece is built on), [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md), [0017](../../decisions/0017-act-one-restaging.md) (c), [0020](../../decisions/0020-kerrid-restaging.md), [0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (c) and its sweep-G note, [0027](../../decisions/0027-vowbound-battle-rules.md).
Next chapter: [act1_ch09.md](act1_ch09.md) ("The Ebbing", same zone at night).

Scripts: none yet. The `.dlg` files, flow, greybox and encounters are M3-C08-02 (Cinematics), built from this sheet. Sample lines below set the voice only; the full dialogue is that task's.

**The rules this chapter must keep** (each is an accepted ADR or watch; Cinematics, check them in review):
1. **Nothing bound or machine-made is used against the storm** (ADR 0017 (c) and its Ch8 watch). Corrow's defence is a beacon and a stair. Liss's hoist is plain rope and iron. Virel is called against spawn and to *light the wall*, never against the storm itself, and the Reach's last phase can't be damaged by anything (§5).
2. **Kerrid at the stair foot is staged exactly as ADR 0022 (c) pins it:** storm-dark at 16:40 with spray, Kerrid waist-deep at the stair foot, the climbers facing the climb, Toma and the Stillguard on the wall-head above and out of earshot in the storm, and the fishwife the only one who looks back down. **No rope-burn glow in any Ch8 shot** (ADR 0022 (g); color script `ch08`). Nobody at Corrow recognises him beyond her one word (ADR 0020 watch).
3. **Nothing stages Corrow as Kerrid's return** (ADR 0020 (d)). He has no line about the place, no look at a landmark that the camera lingers on, and nobody tells the 1001 captain's story in this chapter. The player must not learn here that the watch lost its captain at the stair foot. That belongs to Toma's Ch12 recollection and Kerrid's Ch15 confession.
4. **Rhen's freeze is a freeze, not a run** (ADR 0017 echo table, Ch1–8 row). The figure turns *away*.
5. **Asha's singing never brings the storm.** In Ch3 the verse called the Drownbell. Here the Undertow is already coming (it is why Kerrid walked to Corrow, and Fenn smells it at noon). Asha does not sing at Coilspire, so no player can read Corrow's drowned as her fault.
6. **The player never causes a death by playing badly.** Every death in Ch8 is the stair's width (the people still in the low town's lanes when the sea came over). The evacuation's quotas are what the party *can* save, and losing a wave is a retry, never a body count (§5a).

---

## 0. The chapter in one paragraph

The pilgrimage reaches Corrow on a bright noon, with kites flying off the wall for the Cantor. Toma comes back to the wall he served on and is hugged by the shield-mate he served beside. Asha climbs Coilspire, walks the beacon's fire up its copper flues and binds Virel, and Liss finds a wright's mark scratched in a temple's stone and keeps it to herself. From the spire's crown they see the Undertow coming against the wind, open the beacon, and run back to a town doing the only thing it has ever been able to do: climb. The party holds the head of the Fisher Stair through three waves of spawn while Liss's rope lifts the children, a stranger on the outer wall sounds like the storm to draw the spawn off, and Toma holds the stair without ever going forward. Far below, where nobody on the wall can see, a fishwife looks back down the stair at the big man pushing the last of them up and says one word. A limb of the storm comes over the wall. They get the last group up, and the wall falls anyway. At the broken edge Rhen sees someone in the storm and hears his father's song, and he can't move, and Kerrid comes up the drowned stair last and hauls him back by the collar. Afterwards the Stillguard cut the hoist down because it was bolted into the Watchers, and nobody thanks anyone.

**Emotional line:** arrival warmth (noon kites) → homecoming (Toma) → a hushed, hot, climbing temple → a discovery kept secret → dread (the storm against the wind) → effort (the stair) → one word in the dark → futility (the wall falls) → paralysis (the figure) → a hand on the collar → bitterness (the cut rope).

**What the chapter must prove** (act_outline Ch8, M3): one town by day plus its storm variant; one temple trial; one Vowbound (the third, and the first called to light a place rather than clear a field); the Act I set-piece; a three-phase boss with a scripted escape; and the set-up of everything Ch9 pays off (the drowned, Pell, Kerrid's absence, Toma's friend, the stair-law).

---

## 1. Running order

Time is in-world (one day). Minutes are a first-time player's. **P** = playable, **C** = letterboxed cutscene (`.dlg`, sequencer-driven), **E** = in-engine scene (no letterbox, the player keeps the rail camera). Shot ids are proposed in §7 (W = Corrow and the wall, F = Coilspire).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **Landfall under the kites** | `ch08/corrow` harbour mole | 10:40 | E | 1.5 | W01, W02 | `corrow_day` | The brightest wall in Act I, and its faces are humming with their eyes shut. Kerrid peels off: "Later." | `ch08_arrived_corrow` |
| B02 | **Corrow by day** | `ch08/corrow` Bastion, wall-head, low town | 11:00 | P (+E) | 8.0 | W03–W06 | `corrow_day` | A garrison town that knows exactly what it will do when the sea comes. Toma's homecoming. The stair, seen once in daylight. | `ch08_met_ivo` |
| B03 | *Side scene: "The Keeping Flame"* (optional) | `ch08/coilspire` keeper's hut | any, before B05 | E | 3.5 | F01 | none (wind, fire) | The last Cantor fed this fire too, and said her daughter would be braver than her. | `ch08_fed_the_beacon` |
| B04 | The wall-gate and the headland path | `ch08/corrow` → `ch08/coilspire` | 13:00 | P | 3.0 | W07, F02 | `corrow_day` → `coilspire_flues` | Out along the headland to where the storms always break. | — |
| B05 | **Coilspire: the flue trial** | `ch08/coilspire` interior | 13:30 | P | 8.0 (+1.5) | F03–F05 | `coilspire_flues` | Fire obeying a patient hand, tier by tier. Liss finds a wright's mark in a temple. | `ch08_liss_found_marks`, `ch08_found_sail_needle` (optional pickup) |
| B06 | **The binding of Virel** | `ch08/coilspire` crown chamber | 15:00 | C | 2.5 | F06, F07 | `coilspire_flues` → `virel_bound` | A kite made of fire, held perfectly still. The third band. | `ch08_virel_bound` |
| B07 | **The storm against the wind** | `ch08/coilspire` beacon gallery | 15:40 | C → P (one input) → C | 2.0 | F08, W08 | `silence` → `undertow_rising` | The thing every town on this coast is built to survive is coming, and it is wider than the sky. Open the beacon. | `ch08_beacon_opened` |
| B08 | The run back | `ch08/coilspire` → `ch08/corrow` wall-gate | 15:50 | E | 1.0 | F02 (storm grade), W07 | `undertow_rising` | The kites come down. The bells along the coast answer the beacon. The gate stands open; Kerrid is nowhere. | — |
| B09 | **The stair, first down** | `ch08/corrow` wall-head (storm) | 16:00 | E | 1.0 | W09, W10 | `undertow_rising` | The watch goes down the stair. Toma takes his place in the shield-line: "We hold the stair. That is all we do tonight." | — |
| B10 | **Wave 1: "Hold"** | wall-head arena | 16:05 | P | 4.0 | W11 (battle) | `seawall_hold` stem 1 | Learn the stair on the timeline: the climbers have turns too, and the spawn reach for them. | `ch08_wave1_held` (battle result) |
| B11 | **The hoist** | wall-head | 16:15 | E | 1.5 | W12 | `seawall_hold` stem 1 (under) | Liss drives iron into the Watchers' mouths and a basket of children goes up the wall's face. "Children first. Argue with the stone after." | `ch08_hoist_rigged` |
| B12 | **Wave 2: "The Rope"** | wall-head arena | 16:18 | P | 5.0 | W11 | `seawall_hold` stem 2 | Protect the thing that is saving people. Fight or haul. | `ch08_wave2_held` |
| B13 | **What Asha hears; the stranger on the wall** | wall-head | 16:28 | E | 1.5 | W13, W14 | `seawall_hold` stem 2 (under) → `pell_storm_note` (diegetic) | She can hear the low town's lamps going out. A tall shape on the outer parapet sounds like the storm, and the spawn turn their heads to it. | `ch08_pell_seen` |
| B14 | **Wave 3: "The Last of the Low Town"** | wall-head arena | 16:30 | P | 5.0 | W11 | `seawall_hold` stem 3 | Everything at once, and somebody else helping who isn't yours to command. | `ch08_wave3_held` |
| B15 | **"Captain?"** | `ch08/corrow` stair foot (storm) | 16:40 | C | 0.75 | W15, W16, W17, W10 | `seawall_hold` stem 3 → wind only | One word in the dark, that nobody on the wall hears. | `ch08_fishwife_called` |
| B16 | **Boss: the Undertow's Reach** (three phases, scripted escape) | wall-head arena | 16:42 | C 0.5 → P 8.0 | 8.5 | W18, W11, W19 | `undertow_reach` (3 stems), `virel_summon` sting | The storm itself puts a hand on the wall. Hold, then light the wall, then get the last of them up and go. | `ch08_reach_survived` (battle result) |
| B17 | **The wall falls** | wall-head, the breach | 16:55 | C | 3.0 | W20–W25 | `undertow_reach` stem 3 → `current_song` (diegetic) → `silence` | The stair was not wide enough. A figure in the storm turns away. A hand on the collar. | `ch08_wall_fell`, `ch08_rhen_froze`, `ch08_rhen_told_asha` (choice) |
| B18 | **The cut rope** | wall-head, rain easing | 18:30 | E | 2.0 | W26, W27 | `corrow_aftermath` | The Stillguard cut the hoist down. The Order thanks no one. Toma asks after a name, and nobody answers. | `ch08_hoist_cut_down` |

**Totals:** critical path **58.5 min** (B01–B02, B04–B18). With the side scene and the needle, **63.5 min**. Split: **42 min playable (72%)**, 9 min cutscene, 7.5 min in-engine. The set-piece (B09–B17) is **30 min**, half the chapter, which is right for Act I's climax. A slow reader lands near 70.

**Cut order if the chapter runs long:** B04 folds into B02's exit (the gate becomes a one-shot transition). B08 becomes 15 s inside B07's outro. B13's two halves merge into B14's intro. Then Wave 2 shrinks its quota from 4 to 3. **Never cut:** B06, B11 (the hoist is Liss's Act I beat), B15, B16's phase 3 (the escape is the wall falling), B17, or B18's cut rope.

---

## 2. Beat detail

### B01. Landfall under the kites (E, 1.5 min)
- **W01:** the trader that carried them from Tamsule comes in under the wall. The seawall fills the frame: grey laterite in a long curve, with row upon row of **Watchers**, carved faces with closed eyes and open mouths, as if humming. Over the wall-head, dozens of cloth kites. *Corrow custom (new):* the wall flies kites when a Cantor comes, "so the Watchers have something to look up at." Cloth only (bible §4, Vigil kites). This is Act I's last festival frame, and the kites are what the storm tears loose in B08.
- **W02**, on the mole: a few townsfolk come down to see the Cantor. Asha smiles first.
- **Kerrid peels off.** As the others start up the mole steps he says "Later." and walks off along the outer foot of the wall, the way he declines inns (kerrid.md tells). Toma: "He does that." Nobody follows. *Why (do not surface):* only Corrow's old watch knows his face (ADR 0022 (c)), and by day the low town is full of them. He is gone until B15. Cinematics: this is a plain exit, played as habit, with no look back at the wall.
- ~60 words.

### B02. Corrow by day (P, 8 min, with two E inserts)
The town loop: the Bastion's upper town (W03), the wall-head walk among the Watchers (W04), the head of the Fisher Stair (W05), and the low town under the wall's lee (W06). **Systems:** a smith (gear tier 4), a chandler, an inn (Kerrid's absence is noticed by nobody), a save shrine at the wall-gate.
- **E insert 1, "Okeru!" (1 min):** on the wall-head a Stillguard drops his shield and hugs Toma hard enough to lift him. **Ivo Brannick**, Toma's shield-mate for seven years on this wall (1002–1009). Warm and loud. Sample: *"Okeru. Level preserve us, they let you out of the village? You got fat on Haluna fish."* He kneels properly to Asha ("Lady Cantor"), takes to Rhen at once, and eyes Liss's line-marks, then Toma's papers, then shrugs. Toma laughs out loud for the first time in the game. Sets `ch08_met_ivo` (critical path; Ch9's side scene reads it). *Do not surface:* Ivo was on the line beside Toma at the 1003 Brine Shoals burning (toma_okeru.md). Nothing is said of it here.
- **E insert 2, the stair (20 s, wordless):** at W05 Asha stops at the head of the Fisher Stair and looks down it for a held beat (`@face asha neutral`, `@wait 1.0`). Then she walks on. *Why:* Kerrid told her in Ch5, "I held a stair for your mother once." A player who remembers can connect the stair to her mother and to 1001. That's what ADR 0020's Ch5 line was planted for. It does **not** say he died there. No line, no music sting.
- **Barks** (walk-past, ~150 words in total):
  1. The watch's captain now, **Hobb** (a fisher of fifty with the three-knot watch-red cord on his hip), drilling young fishers on the stair: *"First down, last up. Say it." "First down, last up."* This is the first time the game voices the stair-law. Cinematics: **never frame Hobb's cord and Kerrid's in one shot** (Kerrid is offscreen all day anyway).
  2. A Stillguard on the wall-head, bored: *"Beacon's been lit nine hundred years. Opened full maybe forty times. You'd think we'd get a better plan."* (A sincere grumble, not a wink: nobody here believes the storm can be fought.)
  3. Low town, a net-mender: *"Wall's been rebuilt after every Rising. You can count them in the stone. The pale blocks are the last one."* (The 1001 section reads paler. No one says 1001.)
  4. Children on the wall-head with kites, arguing whose kite the Watchers like best.
- **Old Marra** is in the low town, mending nets on a doorstep. She is an NPC with no bark in B02, just an old fishwife with a one-knot watch-red cord on her wrist. Cinematics: she is placed so the player can pass her, because B15 is her beat.
- **Random encounters:** none in town. Budget: B02 barks 150, Ivo 90.

### B03. Side scene (optional): "The Keeping Flame" (E, 3.5 min) — see §4

### B04. The wall-gate and the headland path (P, 3 min)
- The stair-watch's **wall-gate** (W07): timber and iron, painted watch-red, opening onto the headland path. A watch gatekeeper lets them through for the Cantor. (This is the gate Kerrid kept in 1001. Nothing marks it. It is just a gate.)
- The headland path (F02): wind-bent scrub, laterite steps, the sea loud on both sides, Coilspire ahead, a hollow stone spire with copper flue-pipes coiled up its outside like vines. **Encounters:** `stormgull` (Rhen), `wallcrab` (Toma). One forced encounter at the path's mid-point. Music `corrow_day` thinning to wind.
- At the spire's door, Coilspire's **Tender** looks at Liss's bare right arm, then at Toma's papers, and lets her in, tight-lipped: *"The Lady Cantor's guardians may attend her."* The custom that let Liss go in Ch6 is now a rule at a temple door (pillar 2: the faith's mercy has a shape).

### B05. Coilspire: the flue trial (P, 8 min, +1.5 optional)
**The idea:** Coilspire is a chimney. The keeping flame burns low in a hearth at its base, and the beacon basket at the crown is fed by the draught that copper flues pull up through the spire's walls. A Cantor's trial is to walk the fire up, tier by tier, until it reaches the crown, where Virel's chamber sits beside the beacon.
- **Four tiers.** Each tier has two to four **flue-keys** (copper wheels that open or close a damper). Open the right ones and the draught pulls the flame up into the next tier's brazier. Open too many and the draught splits, and the flame falls back one tier with a cough of soot. **No fail state and no timer** (SPEC §6.1's no-real-time-pressure spirit carries over to trials): a wrong setting only resets that tier. F03 is the overview shot, toggled by the player, as S03 was at the Shell Shrine.
- **Tier 3's stuck key** is Liss's: it has seized. The party can't turn it, and Liss can (an interact prompt that only she answers, with a party-swap prompt if she's in reserve). Sample: *"Don't. Don't force her. ...There. She wants oil, not muscle."*
- **The mark (E, 1 min, in place, F04):** behind the freed key, scratched into the stone where nobody would look, are fine parallel lines and node-dots, the same grammar as the marks on Liss's arm, in an old style no living wright uses. A small key-shaped glyph closes it. Liss goes still. She takes a charcoal rubbing onto her wrist. Rhen is the only one who sees. Sample:
  - Liss: *"Somebody seated this. A wright. In a temple."*
  - Rhen: *"I've seen marks like that on salvage. My—"* He stops himself.
  - Liss: *"Your what?"* Rhen: *"Nothing. Salvage."* Liss: *"Don't tell them."* Rhen: *"Wasn't going to."*
  That is Rhen keeping Liss's secret while keeping his own (the Ch11 reveal). It also starts the trail of **Wenna's marks** that Liss follows through Act II (vowbound.md §3). She doesn't know whose mark it is. Sets `ch08_liss_found_marks` (critical path).
- **Hidden reward (optional, +1.5 min):** a side flue on tier 2 that only draws when every other key on the tier is shut leads to a sealed lamp-niche. Inside is **a sailmaker's needle**, threaded with a fire-proof cord, wrapped in oilcloth. It is an accessory (Combat: Ember Guard, or a small fire ward). Sets `ch08_found_sail_needle`. *Payoff:* it is Wenna's, hidden on purpose like her marks. In Ch20, if Liss carries it, she gives Virel's sailcloth her needle back (§3).
- **No dialogue during the puzzle** beyond the stuck-key line, the mark scene, and one Asha hint bark after 90 s idle on a tier (*"It wants to climb. We keep letting it out the side."*). Encounters inside: `flue_moth` (Ysolde), two placed fights, no random ones.

### B06. The binding of Virel (C, 2.5 min) — *scripted*
- **F06:** Asha goes into the crown chamber alone, by rite (as at the Shell Shrine). The others wait on the crown stair, where the noise of the beacon is.
- **F07:** a single held frame of Virel: a long ribbon-serpent of sailcloth panels, coiled the height of the chamber, with fire along every seam, and **perfectly still** (N-05, color rule 2). A brass tuning key hangs at its throat. *Rendering note:* at rest in its chamber the seams read as steady `glimmer_bound`, never flickering. The fire *element* belongs to Virel's battle VFX. Don't animate the seams as live flame here (§9).
- Then fade. Virel does not speak (the Vowbound don't speak before their Act III releases).
- Asha comes out with the third verse and the **third band** on her sleeve (verse-sleeve S3, art `asha.md`). She does not sing it (rule 5). She is tired, and pleased in the way she lets people see: *"She's very warm. I think she was a kind person. Somewhere under all that fire."*
- No released light lifts off her this time (Ch3's was the first, and its weight should stay with Ilun). The moment is cut short by B07.
- Sets `ch08_virel_bound` (vowbound.json `bound_flag`; the sleeve's band 3).

### B07. The storm against the wind (C → one input → C, 2 min) — *scripted*
- **F08**, the beacon gallery at the crown: the sea to the south-west has gone the wrong colour. The wind is from the land, and the cloud is coming the other way (bible §9: it moves against the wind). A wall of dark water and cloud, lit from inside by wounds. `@music silence`. Nobody speaks for a long beat.
- The Tender, panicking, starts the Canticle and gets a line wrong. **Ysolde** quietly gives him the right words, and he steadies (her tell: a correction mid-crisis is her warmth). ~20 words.
- **The input (P):** the great flue-key that opens the beacon full. If `ch08_fed_the_beacon`, old **Fenn** has climbed after them and hands Asha the key: *"You know the way of her now."* Otherwise the Tender does. **The player opens it** (one interact). The beacon roars up out of its basket, and down the coast, one after another, the bells answer (W08, a long lens from the gallery).
- Toma: *"Down. Now. The stair."* Sets `ch08_beacon_opened`.

### B08. The run back (E, 1 min)
The headland path under a sky going slate (F02, `ch08_storm` grade blending in). The kites over the wall are coming down, and one is torn loose and goes out toward the storm wall (one shot, no comment). The wall-gate stands open. **No Kerrid** at it or near it. Rhen: *"Where's Kerrid?"* Toma: *"He will be where he is needed."* (Toma trusts him, and he is right, and that is the irony.) ~30 words.

### B09. The stair, first down (E, 1 min)
- **W09:** the wall-head over the Fisher Stair. Below, the low town is emptying into its lanes toward the stair foot. Hobb's voice: *"First down!"* and the stair-watch goes **down** the stair against the crowd coming up, to bring up the slow.
- **W10**, the Stillguard shield-line at the stair-head: Ivo is in it. Toma takes the place beside him without being asked.
  - Ivo: *"Your shield. My wall. Same as ever."*
  - Rhen: *"We're not going down after them?"*
  - Toma: *"We hold the stair. That is all we do tonight."*
  That last line is the set-piece's rule, said in the fiction (§5a: Toma doesn't go on the offensive).
- Autosave here (§9 Systems).

### B10. Wave 1: "Hold" (P, 4 min) — see §5a

### B11. The hoist (E, 1.5 min)
- Between waves (the spawn pull back down the wall face in a lull of the surge), **Liss** looks at the stair, at the crowd, and at two Watchers on the parapet with their stone mouths open. She drives iron pins into the Watchers' mouths, hangs her blocks off them, and runs a rope down the wall's inner face beside the stair, with a fish-basket on the end. Plain rope and iron, nothing bound (ADR 0017 (c)).
- A Stillguard shouts at her ("Those are the Watchers!"). **Ivo** waves him off: *"Children first. Argue with the stone after."*
- Liss, hauling, in her jargon (the tell is in reverse here: working means she's fine): *"Seat the pin. Seat it. She'll hold."* The first basket comes up with three children in it. Toma looks at the pins in the Watchers' mouths, then takes the rope's tail and hauls without a word. (His devotion is to the people. The Order's view of the stone comes in B18.)
- Sets `ch08_hoist_rigged` (unlocks Liss's *Haul*, §5a). ~70 words.

### B12. Wave 2: "The Rope" (P, 5 min) — see §5a

### B13. What Asha hears; the stranger on the wall (E, 1.5 min)
- **W13:** in the lull Asha has stopped with her hands half-raised, healing nobody. She is a hearer, and with the sea in the low town she can hear its lamps going out, one by one. *"They're going out. Toma. They're going out—"* Toma, not looking away from the stair: *"I know. Stay on my shield."* (~25 words.) This is the cost of hearing, and the reason for the Ebbing (Ch9).
- One climber, a small boy, has stopped dead at the stair-head and won't take the last step. Asha kneels and **hums** to him: the Velamir lullaby, the first verse's tune. He climbs. Rhen hears his father's tune at the top of a stair in a storm and doesn't know why it stops his breath. *Payoff (do not surface):* in 1001, Imra hummed the same tune to the children on this stair, and that is how Dace knew her (ADR 0022 (a)). Rhen reads that in Dace's ledger in Ch17 and remembers this. Humming is allowed (Cantors sing, and everyone hums), and it is not a verse.
- **W14:** out on the **outer** parapet, in the spray, a very tall figure is standing where nobody should be able to stand: a Kirru, long-necked, crest flat in the wind. He opens his throat and makes **the storm's own note**, low and huge, and the spawn on the wall face turn their heads toward him like dogs to a whistle. Rhen: *"Is he— is he singing to them?"* Asha: *"No. He's sounding like it."*
- **Pell says nothing in Ch8.** His first spoken words in the game are Ch9's "Beautiful. And pointing the wrong way." Sets `ch08_pell_seen` (the battle shows him as "The Kirru" until `ch09_pell_named`).

### B14. Wave 3: "The Last of the Low Town" (P, 5 min) — see §5a

### B15. "Captain?" (C, 0.75 min) — *scripted, staged exactly to ADR 0022 (c)*
- **W15**, low, at the stair foot, 16:40, near-night: the sea is in the low town to a man's waist, and spray is coming over the wall in sheets. The last climbers are on the bottom flights with their backs to camera, **facing the climb**, hands on the hand-line rings. Waist-deep in the black water at the foot, a big man in a sodden straw cape is pushing them up one by one: Kerrid. His **left arm** (the wrapped one) is toward the lens. No rope-burn glow. The light is the storm's (spawn-wound cyan, high above) and nothing on him.
- **W16:** one of the climbers, **Old Marra** (the fishwife from B02, one of the 1001 stair-watch), is the only one who looks back down. She stares at him. CU on her face: rain, disbelief, and something like hope.
- Marra: *"Captain?"*
- **W17:** Kerrid's face, seen clearly. Both eyes clear (kerrid.md). He looks at her for one beat, says nothing, and **goes down a step**, deeper into the water, back to the people still below her. She is pushed on up by the climber behind.
- **W10** (cut, wide, from below): the wall-head is far above, tiny, the shield-line and the party fighting in the spray. Out of earshot. The sound is all wind and surf.
- **Rules:** no music line on the word. No VO. No other climber turns. Toma and the Stillguard are never in a shot that also holds the stair foot. Kerrid gets no reaction close-up after the step. Sets `ch08_fishwife_called` (critical path: Ch12 and Ch15 read it).

### B16. Boss: the Undertow's Reach (C 0.5 → P 8) — see §5

### B17. The wall falls (C, 3 min) — *scripted*
- **W20:** the Reach's breach lands. The wall-head section to the stair's seaward side goes, the Watchers on it tipping out into the storm, and the sea comes through the gap into the low town in one long grey slide. The stair's lower half is under it. *The stair was not wide enough:* the shot shows the low town's far lanes, where people were still coming, going under. Wide, unlit except by the storm. No close-ups of the drowning (pillar 1: sorrow, not spectacle).
- **W21:** Rhen, nearest the new edge, is at the lip of the break, looking out into the storm's wall.
- **W22 (Rhen's POV):** inside the storm wall, in the dark water and cloud, **a single cyan silhouette**, a man's shape, standing in the storm as if on a deck (color script `ch08`: "the figure in the storm wall is a single cyan silhouette"). Diegetic, from Rhen's position only: **the current-song** (`current_song`, Dace's, the same one Rhen heard underwater in Ch1).
- **W23:** CU on Rhen. He can't move. *This is a freeze:* no step toward it, no reach, no word. The edge is crumbling at his toes.
- **W22:** the figure **turns away** into the dark and is gone. The song goes with it.
- **W24:** from behind Rhen, a hand takes his collar and hauls him back off the lip as it falls away: **Kerrid's left hand, wrapped in tarred hauling-cloth**, the hand that took the rope's full run in 1001. He has just come up the drowned stair, **the last man up it**. *E3 consistency:* in the Ending he fixes Rhen's collar "the way he grabbed it at Corrow". This is that grip, with the same hand.
- **Frame rule (Cinematics):** Kerrid never shares a frame with the figure. The figure has turned away and is gone before Kerrid's hand enters W24. This is the Ch8 form of act3_ending §0 rule 8.
- **W25:** Rhen on his back on the wet stone, Kerrid already turning away to look down the stair, which is now just sea. Kerrid gives no line. Gesture slot: he looks down the drowned stair for a long beat, the way a man counts.
- **Choice** (Asha reaches Rhen): *"Rhen. What did you see?"*
  - *"Someone. In the storm. Humming a current-song."* → sets `ch08_rhen_told_asha`. Asha, quietly: *"I heard them too. All of them."*
  - *"Storm. Just the storm."* → Asha lets it go, warmly: *"All right."* (Her patience, as in Ch3.)
- Sets `ch08_wall_fell`, `ch08_rhen_froze`. ~50 words.

### B18. The cut rope (E, 2 min)
- **W26**, 18:30: the storm has gone on along the coast, moving against the wind. The rain is easing, and the low town is a black lake to the eaves. On the surviving wall-head the Stillguard are counting.
- A Stillguard officer (`stillguard` speaker) comes to Liss's hoist with a hatchet. *"Cut it down. It is bolted into the Watchers."* Two blows. The rope goes slack and slides down the wall face. **Nobody thanks anyone** (ADR 0017 (c)). Toma opens his mouth and shuts it: it is his order's law, and his faith is intact (Act I).
- Liss coils what's left of the rope, narrating the work instead of the grief (her tell): *"Good rope. Seated true. She held."* Rhen: *"Liss—"* Liss: *"Don't."*
- **W27:** Toma goes along the shield-line asking after a name. *"Brannick? Has anyone seen Ivo Brannick?"* A Stillguard shakes his head. Toma keeps walking. (Ch9's side scene pays this off.)
- Kerrid stands at the head of the drowned stair, looking down. When Rhen looks back he is gone. (He has gone down into the low town to bring up the drowned at slack water: Ch9's cutaway.)
- Sets `ch08_hoist_cut_down`. Then the chapter ends on the black water and `corrow_aftermath`. ~90 words.

---

## 3. Flags

All are to be declared in `game/data/flags.tres` (M3-C08-02 adds them). Read and write them only through `Game.get_flag` / `Game.set_flag`.

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch08_arrived_corrow` | B01 (end) | zone gating, chapter flow (M3-ARC-01) | — |
| `ch08_met_ivo` | B02 insert 1 (critical) | Ch9 side scene trigger | Toma's Ch9 side scene needs the player to have met Ivo |
| `ch08_fed_the_beacon` | B03 side scene | B07 (Fenn hands Asha the key), Ch9 shore barks | Ch9: Fenn kneels at the Ebbing and has one line for Asha |
| `ch08_liss_found_marks` | B05 mark scene (critical) | Ch11 (Lowlight), Ch12 (Cloudloom), Ch13, Ch20 | Liss's trail of Wenna's marks across Act II; Rhen's stopped "My—" pays in Ch11 |
| `ch08_found_sail_needle` | B05 hidden pickup | Ch20 Virel release | If carried, Liss gives Wenna her needle back (one extra line in Liss's fight; vowbound.md §3) |
| `ch08_virel_bound` | B06 (end) | vowbound.json `bound_flag` for Virel; verse-sleeve state S3 | Virel callable from B16 on |
| `ch08_beacon_opened` | B07 input | B08 gate, chapter flow | — |
| `ch08_wave1_held`, `ch08_wave2_held`, `ch08_wave3_held` | B10, B12, B14 battle results | chapter flow, retry checkpoint | — |
| `ch08_stair_groups_up` (**numeric**) | each wave's objective (the carried stair meter, §5a) | the set-piece HUD, B11/B13 E beats | none in story. It is a play meter only (rule 6) |
| `ch08_hoist_rigged` | B11 | Liss's *Haul* (`requires_flag`) | — |
| `ch08_pell_seen` | B13 | Wave 3's guest entry label ("The Kirru") | Ch9: the party knows him as the stranger on the wall |
| `ch08_fishwife_called` | B15 (critical) | Ch12 (Toma's breath beat), Ch15 | Toma hears of Marra's word offscreen in Ch9 (act1_ch09.md B01), and in Ch12 the breath, the rope-burns and that word come together (toma_okeru.md) |
| `ch08_reach_survived` | B16 battle result (`scripted_escape`) | B17 trigger | — |
| `ch08_wall_fell` | B17 | Ch9 night variant of `ch08/corrow` | — |
| `ch08_rhen_froze` | B17 (critical) | Ch17, Ch21 H02 | the figure was Dace's lamp; at the Heart Rhen stands still for him on purpose ("I'm not running, Dad. Look. I'm standing right here." voice guide, Act III) |
| `ch08_rhen_told_asha` | B17 choice | Ch21 H02 | if told, Asha has one line at the two lamps: "Corrow. The one you saw." |
| `ch08_hoist_cut_down` | B18 | Ch9 (Liss's shore barks), Ch17 | at Hollowmere, rigging the Kite, Liss uses the same blocks and says so once |

---

## 4. The optional side scene: "The Keeping Flame" (B03)

**Where:** the keeper's hut at Coilspire's foot, by the hearth that feeds the spire. **When:** any time between B04's arrival at the spire and entering the trial (an NPC marker on Fenn). **Length:** 3.5 min, ~160 words. **Speakers to add:** `fenn`.

**Beats:**
1. **Old Fenn** has kept Coilspire's low flame for forty-one years and has never once let it go out. He is feeding it from a basket of driftwood when Asha comes in, and he doesn't get up.
2. He lets her feed it (one interact: a piece of driftwood into the hearth). He tells her to put it on "like you'd put a blanket on a sleeping child", and she does.
3. He looks at her properly. *"The last one fed her too. Eleven years back. Year of the last Rising."* Asha: *"My mother."* Fenn: *"Said she had a girl at home. Said the girl'd be braver than her."* Asha: *"...She said that?"* Fenn: *"Said it to a fire. Fires don't carry tales. I do."*
4. Asha smiles first, and it costs her something (`@face asha smile`, then a held `neutral`).
5. Fenn, almost cheerful: he has opened the beacon full twice in his life. *"Third time's coming. I can smell it."* Asha thinks he means one day. The player, a chapter's worth of noon later, learns he meant today.

**Rules:** no more than four Fenn lines in a row, broken by Asha's feeding and her questions (SPEC §3.6). Fenn's voice is plain and dry, an old man who talks to a fire more than to people. He says nothing about the 1001 stair, the watch or its captain (rule 3). He met Imra at the hearth, not at the gate.
**Payoff:** sets `ch08_fed_the_beacon`. In B07 Fenn climbs the spire after them and hands Asha the great key ("You know the way of her now."). In Ch9 he kneels at the Ebbing, and after it he tells Asha her mother danced for Corrow's drowned from the same harbour (ADR 0022 (a): "Imra danced the Ebbing for Corrow's drowned"). She did not know that.

---

## 5. The Undertow's Reach (B16): placement, phases, and what it teaches

**Placement:** straight after B15 (the last climbers are on the bottom flights), on the wall-head arena (W11), in near-night. It is Act I's climax fight, and its point is that **it can't be won**. The party can only hold, see, and leave. The storm is never beaten in Act I (ADR 0017 (c)): that belief belongs to Act III, where the weapon is a song.

**What it is:** a limb of the Undertow itself, not a spawn. A column of black water and cloud as thick as a tower comes over the parapet from the sea side and splays into a "hand" of spawn-crust that grips the wall-head. Its wounds bleed `spawn_wound` cyan. We only ever see the forearm and hand. The rest is the storm wall behind it.

**Party:** any three of Rhen, Asha, Toma, Ysolde and Liss (Kerrid is below until B17). Toma's slot stays locked at the stair-head (§5a). **The Climb** ward entry is on the timeline all fight, carried over from Wave 3.

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: the Grip** (100–60%) | The hand closes on the parapet beside the hoist (W18 intro, 0.5 min C). | It telegraphs **Close the Hand** (a `charge`, 2 of its turns) on **the Climb**: if it lands, the climb is pushed far back and the hoist's Haste is stripped. **Toma's *Hold the Stair*** (cover the ward for the next hit) takes it on his shield. Between charges it uses *Undertow Pull* (all foes, small damage, a delay push) and *Crust Slam*. | A telegraphed heavy blow aimed at a third party, and the defender who steps in front of it. That is Toma's whole character as a mechanic. | "We hold the stair. That is all we do tonight." |
| **2: the Dark** (60–30%) | The storm closes over the wall-head (W19). The field **`storm_dark`** rises. | While the field is up, every party member gains **Darkness** at their turn's start and the Climb is **Slowed** (the climbers can't see the stair). Two Squall Wings bound to the field harry the rope. **Asha calls Virel** (first call: full cinematic). Virel's fast fire hits push the Squall Wings back, and her finisher ***Flare Line*** carries `clears_field: storm_dark`: the whole kite-string burns at once over the wall-head, and for one long moment the stair is lit end to end. | Virel's identity (multi-hit fire that delays foes on the timeline), and a Vowbound used **to make a place visible**, not to strike the storm. | Dace saw Virel flown alight over this wall in 1001 and modelled the Kite's sails on her (ADR 0022 (a)). Nobody says so. Liss's reaction shot in the full summon cinematic: she sees the **brass tuning key** at Virel's throat, then looks at the charcoal glyph on her wrist. Wordless. |
| **3: the Breach** (30% →) | The hand lets go of the parapet and draws back over the sea (W11). | The Reach becomes **untargetable and damage-immune**: nothing in the party's kit can touch it, by design. It begins a long telegraph, ***Breach*** (a `charge`, 4 of its turns). The Surge summons Tide Crawlers (up to two) that grip the Climb. **Objective: two more groups up.** When the quota is met, the battle ends with the new outcome `scripted_escape` and cuts to B17. If Breach fires first, it is a heavy all-foes hit, the Climb is pushed back, and Breach re-charges. That is pressure, not a fail state. | The set-piece's lesson under a boss's clock: protect the climbers' turns, read two countdowns at once, and know when the only win is to leave. | The wall falls anyway. The party's success is the last group, not the wall. |

**Tutorial text** (UI, loc keys owned by UI/Combat), one prompt per phase: Phase 1: *"The storm's hand is closing on the stair. Hold it on a shield."* Phase 2: *"The climbers can't see the stair. Call on Virel to light it."* Phase 3: *"Nothing can touch it. Get the last of them up."*
**Battle barks** (≤ 40 words in total): Asha's call is one word, the name. Toma on Hold the Stair: *"Hold."* Liss on Haul: *"Pull!"* Nobody speaks on Flare Line. No line from Virel.
**Light:** everything off the Reach is `spawn_wound`/held cyan, sideways and down. Virel is **bound** (`glimmer_bound`, steady) with fire-element VFX on her attacks. The Flare Line is the one warm, bright frame of the set-piece. It is **fire light, not glimmer**, so it doesn't break color rule 1, and it is never gold mote-light.
**Balance target** (for Combat to confirm): set-piece fights are climactic, not walls. Proposed bands are in §9 Combat.

### 5a. The set-piece: how wave defence plays in the CTB (B10, B12, B14 and B16)

The ask is "waves of spawn while the low town climbs", **with no new real-time system** (SPEC §6.1: time stops while the player chooses). The shape proposed here:

**Shape: three chained scripted battles plus the boss, with a stair meter carried between them.** Each wave is its own `scripted: true` encounter. Between waves comes a short E beat (B11, B13, B15) that moves the story and resets the field. The stair meter (`ch08_stair_groups_up`) carries across all four fights and is shown on the HUD and in the E beats' framing.

*Options considered:*
1. **One long battle with reinforcements.** Rejected. It allows no E beats between waves (the hoist, Pell and the fishwife must land *between* fights), and a defeat at minute 18 throws away everything.
2. **A field-mode stair minigame** (escort NPCs on the field). Rejected. It is a new real-time system, which the brief rules out.
3. **Chained battles plus a carried meter (chosen).** Each wave teaches one thing, a retry costs one wave, and the story beats sit where the drama needs them.

**The one new primitive: the scripted timeline entry (a "ward" or "guest").** Everything below is built from it plus rules the engine already has (`charge`, `summon`, fields, `clears_field`, `requires_flag`, Haste and Slow, Provoke, delay pushes).

- **The Climb** (ward, party side). A timeline entry labelled **"The Fisher Stair"** with a stair glyph. It is not controlled by the player and has **no HP and can't be KO'd** (rule 6: nobody dies of a missed turn). On each of its turns, one group of climbers reaches the wall-head and the wave's counter goes up by 1. Its agility is fixed per wave, so the player can always read how many turns away the next group is (pillar 4).
- **What the spawn do to it.** Some spawn skills target the ward (`target: ward`). A grip is a **delay push** on the Climb (the climbers falter). A rope dive **strips Haste** from it. None of them do damage, because the ward has no HP.
- **What the party does for it:**
  - **Toma: *Hold the Stair*** (new). He covers the ward until his next turn, so the next enemy action that targets the Climb lands on him instead (he takes it as a physical hit, and the Climb isn't pushed). **Provoke** pulls single-target grips onto him anyway, through existing rules.
  - **Liss: *Haul*** (new, `requires_flag: ch08_hoist_rigged`, `target: ward`, rank 4). Haste on the Climb for N of its turns. The choice each turn is whether Liss fights or hauls.
  - **Rhen:** delay pushes on the spawn whose next action is a grip (turn manipulation is his niche). He is also the answer to the Squall Wings (fliers).
  - **Ysolde:** fire for the rooted `wall_polyp` that heals the crawlers. **Asha:** healing, and from B16 on, Virel.
- **The Tide** (an untargetable enemy-side entry). A timeline entry labelled **"The Surge"**. It can't be targeted, never blocks victory, and is `delay_immune`. On its turns it summons spawn from the wave's list (existing `summon` skill), up to a cap of standing spawn. It shows the player when the next spawn come.
- **Pell** (a guest, party side, Wave 3 only). A timeline entry labelled **"The Kirru"** (`ch08_pell_seen`; renamed "Pell" only once `ch09_pell_named` is set). Untargetable, because he is on the outer parapet. On his turns he plays ***Storm-Call***: telegraphed one turn ahead ("The Tide Crawler will follow the sound"), it **removes** one spawn from the field. That spawn leaves to chase the sound, so it gives no XP and isn't killed. He does what act_outline says, and the player can plan around him without commanding him.
- **Victory:** the wave's **quota** of Climb turns (a new encounter field `objective`), regardless of how many spawn still stand. They pull back down the wall face. XP counts only spawn felled. **Defeat:** the active party is KO'd. "Fight again" restarts **that wave** with the meter as it stood at the wave's start.
- **Toma never goes on the offensive** (act_outline Ch8). In the four set-piece encounters, Toma's slot is **locked active** at the stair-head (he can't be swapped out, and the swap menu says "Holding the stair"). His **Attack is replaced by *Stand Firm*** (a counter stance: Protect on himself until his next turn, and he counters physical hits). His only damage is what he returns. This is a deliberate character mechanic. Combat, please test it against the bands, and if it starves the party of damage, keep the rule and lower the waves' HP rather than give him Attack back.
- **Kerrid is unavailable** for the whole chapter (he left at B01). The formation menu shows him greyed: "Not with the party".

**The waves:**

| Wave | Encounter | Quota | Climb | Spawn (role answer) | Teaches |
|---|---|---|---|---|---|
| **1: "Hold"** (B10) | `ch08_stair_hold_1` | 3 groups | slow (agility low) | 2 **Tide Crawler** (Toma); the Surge adds one every 3rd of its turns, max 3 standing | The ward has turns. Grips push it back. Provoke and *Hold the Stair* protect it. |
| **2: "The Rope"** (B12) | `ch08_stair_hold_2` | 4 | medium; *Haul* available | 1 Tide Crawler, 2 **Squall Wing** (Rhen); Surge max 3 | Protect a buff. Fliers dive the rope and strip its Haste. Liss's choice, fight or haul. |
| **3: "The Last of the Low Town"** (B14) | `ch08_stair_hold_3` | 4 | medium | 2 Tide Crawler, 1 Squall Wing, 1 **`wall_polyp`** (Ysolde), rooted on the Watchers' stones, healing the crawlers; Pell's Storm-Call | Everything at once, plus an ally the player reads but doesn't command. Pell draws the movers off; only the party can burn the rooted healer. |
| **Boss: the Reach** (B16) | `undertows_reach` | 2 (phase 3 only) | carried | the Reach; phase 2 adds 2 Squall Wings bound to `storm_dark`; phase 3's Surge adds Tide Crawlers | §5 above. |

**Between waves:** HP and MP carry (carried vitals, M1-CMB-08). Each E beat restores the party to **at least 50% HP** (the Stillguard line rotates, and Ivo passes a water-skin), with no MP restore. No shop and no save inside the set-piece. The autosave is at B09, and each wave is its own retry checkpoint.

---

## 6. Music cues

Ids as the `.dlg` files and sequencer will use them (`@music <id>`). `silence` is reserved.

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `corrow_day` | B01, B02, B04 | Town bed, loop | The warmest bed after Tamsule, but heavier: low drums like stone being set, a bowed drone, a bright wind melody on top for the kites. It is a working town's music, steady rather than festive. |
| `coilspire_flues` | B04 (end), B05, B06 | Temple ambience | Air through copper: tuned flue-tones (pitched to the trial's tiers, so each tier's flame-up adds a note), crackle, and the Order's hum very far below. The third temple should sound hot. |
| `virel_bound` | B06 | Sting (≤ 8 s) | The Hush's first phrase on a high reed instrument over the flue drone. It is the first statement of the theme by a wind instrument. Original melody (SPEC §2). |
| `undertow_rising` | B07 (after the silence), B08, B09 | Cue, through-composed | Low brass and a slow pulse that is wrong against the wind's sound. The bells along the coast (diegetic SFX) fall on its downbeats. |
| `seawall_hold` | B10–B14 | Battle, three stems | One battle cue in three stems that stack across the waves: (1) taiko-like drums and a held-low string; (2) adds a driving rope-and-pulley rhythm (percussion that sounds like hauling); (3) adds the storm's own note as a sub-bass drone. It should feel like *effort*, not triumph. |
| `pell_storm_note` | B13, Wave 3 (Pell's turns) | Diegetic SFX/voice | Pell's imitation of the storm: one huge, low, rising-and-falling note from a throat. It must be clearly a *voice* doing a storm, not the storm. Audio: build it from a designed vocal source, never sampled weather. |
| `undertow_reach` | B16, B17 | Boss, three stems | (1) The Grip: `seawall_hold` stem 3's drone with a heavy, slow figure. (2) The Dark: the bed drops to drone and percussion so Virel's sting and Flare Line can bloom over it. (3) The Breach: a rising ostinato that never resolves, and it cuts on the scripted escape. |
| `virel_summon` | B16 phase 2 | Sting (≤ 6 s) | Sailcloth snapping, a hiss of fire, the Hush's first phrase on the reed. |
| `current_song` | B17 | **Diegetic** motif | Dace's current-song, the Saltwright sung chart Rhen heard underwater in Ch1. One unaccompanied low voice, heard from Rhen's position only, over the storm. It must be the **same melody** as Ch1's statement. Original, and distinct from the Hush theme: it is Dace's, not Imra's. |
| `corrow_aftermath` | B18 | Bed | Rain, a single plucked string, very slow. It is not yet grief, just counting. |

**SFX cues** referenced by the beats (requested): `beacon_roar` (the flue opening full), `coast_bells` (a chain of bells answering from far down the coast), `watchers_pin` (iron into stone), `hoist_block` (a creaking rope and block, loopable), `wall_breach` (a laterite section going, long and low), `hatchet_rope` (two blows and a slack rope sliding).

---

## 7. Camera shots by beat

New shot ids, for env-art's Corrow and Coilspire layouts (to be written as `docs/kb/art/environments/corrow.md` §5, as haluna.md does). **W** = Corrow and the wall; **F** = Coilspire.

| Id | Shot | Lens / note |
|---|---|---|
| W01 | From the sea: the whole curved wall, the Watchers in rows, kites over the wall-head, a trader coming in under it | 24 mm, low over the water, warm noon (`ch08_day`) |
| W02 | The harbour mole steps, townsfolk coming down | 35 mm, rail |
| W03 | Bastion upper town street, Stillguard barracks, the small Order chapel | rail |
| W04 | The wall-head walk among the Watchers' backs, kites | rail, 28 mm |
| W05 | The head of the Fisher Stair looking down its whole length into the low town | 35 mm, high; reused stormy for B09 |
| W06 | Low town lanes under the wall's lee, net racks, Marra's doorstep | rail |
| W07 | The wall-gate (watch-red), opening onto the headland | locked |
| W08 | Long lens from Coilspire's gallery: the beacon flaring, then the bells' lights coming on down the coast one by one | 135 mm |
| W09 | Storm: the stair from the wall-head, the low town pouring into its lanes, the watch going **down** against them | 35 mm, high, `ch08_storm` grade |
| W10 | The shield-line at the stair-head (Ivo, Toma). Also reused **from below** at B15's end as the far, tiny wall-head | 50 mm; the B15 reuse is a separate low setup |
| W11 | Battle arena: the wall-head over the stair, the hoist on the left, the outer parapet right | battle camera set |
| W12 | Liss at the Watchers' mouths, pins and blocks, the basket going down the inner face | 50 mm |
| W13 | Asha with her hands half-raised, the low town behind her | 85 mm |
| W14 | The outer parapet in spray: Pell, small, against the storm wall | 70 mm |
| W15 | **The stair foot**: low, waist-height on the water, the last climbers' backs, Kerrid pushing them up, his wrapped left arm toward lens | 28 mm, low; storm-dark; **no rope-burn glow** |
| W16 | CU Marra, looking back down | 85 mm |
| W17 | Kerrid's face, then his step down into the water | 50 mm; no reaction close-up after the step |
| W18 | The Reach comes over the parapet (boss intro) | 18 mm, low, looking up |
| W19 | The wall-head closing into storm-dark (phase 2 transition) | battle cut-in |
| W20 | The breach: the section and its Watchers going, the sea sliding into the low town | 24 mm, wide, high |
| W21 | Rhen at the new lip, his back to camera, facing the storm wall | 35 mm |
| W22 | Rhen's POV: the storm wall and the cyan silhouette | 85 mm; the figure is a single silhouette, faceless |
| W23 | CU Rhen, frozen | 85 mm, held ≥ 3 s |
| W24 | From behind Rhen: Kerrid's wrapped left hand on his collar, hauling | 50 mm; **the figure is already gone** |
| W25 | Rhen on the stone; Kerrid looking down the drowned stair | 35 mm |
| W26 | Aftermath wide: the black lake of the low town, the broken wall | 24 mm, `ch08_aftermath` grade |
| W27 | Toma walking the shield-line | rail |
| F01 | The keeper's hut and hearth (side scene) | locked, plus hand inserts |
| F02 | The headland path toward the spire (day; reused storm-graded in B08) | rail |
| F03 | Spire interior overview, all four tiers and their flue-keys (player toggle) | puzzle overview |
| F04 | The stuck key and the mark behind it (insert) | macro-ish 100 mm |
| F05 | Tier rails | rail |
| F06 | Crown chamber door: Asha going in alone | 50 mm |
| F07 | Virel, a single held frame | 24 mm; held still |
| F08 | The beacon gallery looking south-west at the storm wall | 24 mm |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | W01 → W02 | A cut. Kerrid exits frame along the wall foot in W02 with no look back. |
| B02 | W03, W04, W05, W06 | Rails. The E insert at W05 holds Asha ≥ 1 s with no music sting. |
| B03 | F01 | One locked shot plus inserts of the driftwood and Fenn's hands. |
| B05 | F03, F04, F05 | F04 is the mark: Liss's face goes still, then the charcoal rubbing. |
| B06 | F06 → F07 → fade | As S07 → S08 at the Shell Shrine: cut on a short fade, never a blend. Don't show Virel's face beyond F07's single frame (save it for the summon). |
| B07 | F08 → (input) → W08 | `@music silence` holds on F08 until the Tender speaks. |
| B09 | W09 → W10 | — |
| B15 | W15 → W16 → W17 → W10 (from below) | **All cuts.** No music on "Captain?". The last shot proves the wall-head is out of earshot. |
| B16 | W18 (intro), W11, W19 | The full Virel summon cinematic plays on the first call, with Liss's reaction shot. |
| B17 | W20 → W21 → W22 → W23 → W22 → W24 → W25 | **The figure never shares a frame with Kerrid.** W23 holds; the freeze is the length of the hold, not a gesture. |
| B18 | W26 → W27 | — |

---

## 8. Word counts

Budgets (no scripts exist yet; M3-C08-02 checks the result with `tools/dialogue_stats.py`).

| Beat | Words |
|---|---|
| B01 | 60 |
| B02 (barks 150, Ivo 90) | 240 |
| B03 side scene | 160 |
| B04 | 40 |
| B05 (stuck key 15, the mark 60, hint 15) | 90 |
| B06 | 40 |
| B07 | 80 |
| B08 | 30 |
| B09 | 50 |
| B10, B12, B14, B16 battle barks | 80 |
| B11 | 70 |
| B13 | 60 |
| B15 | 1 |
| B17 (with the choice) | 60 |
| B18 | 90 |
| **Total** | **~1,150 written** (~990 on a path without the side scene) |

**Against SPEC §3.6:** at ~60 min of a 30 h main story, Ch8 is 3.3% of the game, so its fair share is **1,330–2,000 words**. It comes in **under** that on purpose: the set-piece plays rather than talks, and the chapter's two strongest beats are one word (B15) and none (B17's freeze). Hold the battle barks at 80 words.

---

## 9. Requests to other roles

Each item is written to be filed as a task as it stands.

### Environment Art
1. **`ch08/corrow` kit (day).** *Laterite seawall* (Khmer-influenced masonry at military scale, bible §5.4): coarse porous grey laterite blocks in a long curve, with **visible rebuild strata**, each Rising's rebuild weathered differently and the newest (1001) section paler. *The Watchers:* rows of carved faces on the outer face and the parapet, closed eyes and open humming mouths, 3+ face variants with a weathering parameter (original designs, never a real temple's faces). *The wall-head walk:* parapet, Stillguard shield racks in red lacquer, kite posts. *The Fisher Stair:* broad, cut into the wall's inner face, treads worn hollow in the middle, iron hand-line rings every few steps with a hemp hand-line, the lowest rings below low water and green with weed. *The wall-gate:* timber and iron in watch-red. *The low town:* tight fisher houses of timber and laterite under the wall's lee, net racks, boat-sheds, lanes funnelling to the stair foot. *The Bastion:* barracks and a small Order chapel on higher ground. *The harbour mole* and a grey shingle strand outside the wall.
2. **`ch08/corrow` storm variant:** the same layout under `ch08_storm`, with rain and spray volumes, surf over the parapet, the low town flooding to waist height at the stair foot, Liss's hoist props (iron pins in two Watchers' mouths, blocks, rope, a fish-basket), and a **scripted breakable wall section** for B17 (a destruction rig: the section and its Watchers tip seaward, and the sea slides into the low town).
3. **`ch08/coilspire` kit:** the headland path (wind-bent scrub, laterite steps), the hollow spire exterior with verdigris copper flue-pipes coiling up the outside, the keeper's hut and hearth at its foot, and an interior of four tiers with braziers and rotating copper flue-keys (dampers). The tier-2 side flue and its sealed lamp-niche. The crown chamber, open to the sky on the seaward side, and the beacon gallery with its basket. Interior grade copper green-cyan (color script `ch08`).
4. **Write `docs/kb/art/environments/corrow.md`** with the mood brief and the W/F shot list in §7 (ids are proposals; rename them freely and tell Narrative).

### Art and Rendering (color script)
1. **New frames:** `ch08_day` (10:40–15:00, high warm noon on laterite, kites, Act I's last festival frame; SPEC §7.2 says Act I is warm, noon, festival), `ch08_storm` (the existing `ch08` 16:00 → 16:40 frame, named for the `.dlg` grade set), `ch08_coilspire_int` (copper green-cyan), and `ch08_aftermath` (18:30, rain easing, blue-black dusk with the sea-glow coming up on the flooded low town).
2. **Virel at rest** (B06, F07) is **bound** light: the sailcloth seams read as steady `glimmer_bound`, never flickering, with no shed motes (rule 2, N-05). Fire-coloured light belongs to her *attack* VFX and Flare Line, which are fire, not glimmer. Please confirm how the seams read so that bound and fire are never confused.
3. **The figure in the storm wall** (B17, W22): a single `glimmer_held` cyan silhouette, faceless, as the `ch08` emotional note says. It **turns away** and dissolves sideways and down into the storm, never up.
4. **No rope-burn glow on Kerrid in any Ch8 shot**, including the W24 hand on Rhen's collar (ADR 0022 (g)).
5. The Flare Line frame (B16 phase 2) is the set-piece's one warm burst: fire light lighting the stair, held for ~2 s, with no gold motes.

### Character Art
1. **Kerrid, soaked:** a wet-state straw cape (darker, heavier, hanging closer), used from B15 through Ch9's dawn road.
2. **Ivo Brannick** (new NPC): a Stillguard of the Corrow garrison, about 33, red-lacquered shell armour with the round shield, a broad grin, a broken front tooth. Same armour language as Toma's old pauldron, with the Level emblem intact.
3. **Old Marra** (new NPC): an old Corrow fishwife, about 70, wrapped skirt, netting shawl, and a faded watch-red cord with **one** knot on her wrist (she was of the 1001 watch).
4. **Hobb** (new NPC): the watch captain now, about 50, a fisher, with the **three-knot** watch-red captain's cord on his hip (the same cord as Kerrid's).
5. **Fenn** (new NPC, side scene): about 80, soot-dark hands, a keeper's leather apron.
6. **Pell's first appearance:** wet, crest flattened by the wind, the blank name-shell at his throat (visible but not featured until Ch9).
7. **Asha's verse-sleeve S3** (the third band, from B06).

### Creatures (Art and Combat)
Silhouettes follow SPEC §7.5's spawn language: dark wet carapaces and drifting glimmer wounds. **The ids are the creatures track's proposals** (relayed by the m2-slice parent, 2026-10-24), and this sheet uses them. The creatures track owns the silhouettes. The notes below are only what the story and the set-piece need from each.
1. **`tide_crawler`** (spawn, the set-piece's swarm; role answer Toma). **Story need:** it must visibly **climb the wall's inner face and grab at the climbers' hand-line** on its *Grip the Stair* turns (the ward delay push, §5a), and it must read at a glance as the thing going for the stair, not for the party. It comes in waves, so it should read in a group of three. Water absorb, fire weak (proposal). Pell's Storm-Call can draw it off.
2. **`squall_wing`** (spawn flier, "a gull-shaped hole in the rain"; role answer Rhen). **Story need:** it dives at **Liss's rope and basket** (*Rope Dive*, which strips the Climb's Haste), so its attack animation needs a target on the hoist, not only on a party member. High evasion. Pell's Storm-Call can draw it off.
3. **`wall_polyp`** (a spawn-polyp variant rooted on the wall's stones; a healer behind the crawlers; role answer Ysolde, fire weak). **Story need:** it is **rooted**, so Pell's Storm-Call can't move it, and that difference is the point of Wave 3: Pell draws the movers off, and the party must burn the healer. It heals the largest ally (the existing `largest_ally` selector, as the Drownbell's polyps do). It must read as clinging to the **Watchers'** stones, not to the parapet's plain blocks, so that burning it off the carved faces is a small cost of its own.
4. **`undertows_reach`** (boss). Mostly the storm itself (Rendering's Undertow), so the creatures track models only the limb's near part: a tower-thick forearm of black water and cloud splaying into a "hand" of spawn-crust that grips the parapet. Wounds bleed `spawn_wound` cyan. It needs three states: *gripping* (phase 1), *closing in the dark* (phase 2), and *drawn back over the sea* (phase 3, when it can't be touched and the Breach gathers).
5. **Field creatures** (not in the creatures track's list yet; proposals for it to accept, rename or replace): `stormgull` (a palette variant of `gull_harrier` with a lightning attack; Rhen; the headland path), `wallcrab` (a palette variant of `reef_crab`; Toma; the headland path), and `flue_moth` (not spawn: a huge soot-moth drawn to the fire, fire absorb, ice weak; Ysolde; Coilspire's two placed fights).
6. **Virel** (Vowbound): the sheet `docs/kb/art/vowbound/virel.md`, from vowbound.md §3 (a ribbon-serpent of sailcloth panels with fire along every seam, like a Saltwright signal kite flown alight, and a brass tuning key at its throat).

**Answers to the creatures track's two questions:**
1. **Foes on screen** (the Surge entry is an untargetable timeline entry and is never on screen):

   | Encounter | At the start | Most standing at once | Notes |
   |---|---|---|---|
   | Wave 1 `ch08_stair_hold_1` | 2 `tide_crawler` | **3** | The Surge adds a crawler every 3rd of its turns, up to 3 standing. |
   | Wave 2 `ch08_stair_hold_2` | 1 `tide_crawler`, 2 `squall_wing` | **3** | The Surge adds a crawler or a wing, up to 3 standing. |
   | Wave 3 `ch08_stair_hold_3` | 2 `tide_crawler`, 1 `squall_wing`, 1 `wall_polyp` | **4** | Pell removes a mover on each of his turns; the Surge refills up to 4. |
   | Boss `undertows_reach` | the Reach | **3** | Phase 2 adds 2 `squall_wing` bound to `storm_dark`; phase 3's Surge adds up to 2 `tide_crawler`. The Reach's limb fills the frame's right side, so the battle layout needs 2 small slots beside it, never 4. |
   | Headland path / Coilspire | 1–3 | 3 | Ordinary encounters. |
2. **Keep, cut or rename:**
   - **Keep** all four ids. This sheet's first draft had its own names (a door-sized sea-star "Tidegrip" and a flying-fish "Spraywing"). They are **renamed** to `tide_crawler` and `squall_wing`, and the sea-star and flying-fish silhouettes are withdrawn in favour of the creatures track's. The mechanics stay as §5a gives them.
   - **Cut:** this sheet's armoured "Lampshell" (a spawn living in a dead Lit Age lamp-column, for Ysolde) and its telegraphed *Batter*. `wall_polyp` does Wave 3's job (the target only fire answers), and the Reach's phase 1 already teaches the telegraph, so the Batter was a repeat. *Offered for later, not needed here:* a spawn wearing a dead city's lamp as a shell is a strong beauty-in-decline image for Ch11's Sunken Vey.
   - **One naming note:** the music cue for the boss stays `undertow_reach` and the encounter and enemy id is `undertows_reach`. Different tables, but Audio and Combat should know the two are one fight.

### Combat (the set-piece mechanics, §5a)
1. **Scripted timeline entries** (one primitive, three uses): a non-player-controlled entry with an id, `name_key`, side (`party` or `enemy`), fixed agility, `untargetable`, no HP (it can't be KO'd), and a data AI. Used for **the Climb** (ward), **the Surge** (an enemy-side entry that brings spawn in) and **Pell** (guest).
2. **Ward targeting:** skill `target: ward` (enemy grips and dives; Liss's Haul), and **cover** of a ward (Toma's *Hold the Stair*: the next enemy action on the ward lands on him).
3. **Objective victory:** encounter field `objective: {ward: <id>, quota: n}`, ending in victory when the ward has taken `quota` turns. Spawn left standing withdraw, and XP counts felled spawn only. Plus the new outcome **`scripted_escape`** for the Reach's phase 3 (not counted as an Escape and not offered as a command).
4. **Phase overrides:** `untargetable` and `damage_immune` on a phase row (the Reach's phase 3).
5. **Encounter party rules:** `locked_active: ["toma"]` (with a swap refusal reason), `unavailable: ["kerrid"]`, and an attack override (Toma's Attack → *Stand Firm* in these encounters). Data, not code, if possible.
6. **The carried stair meter:** `ch08_stair_groups_up` written after each wave and restored on "Fight again" to the wave's start.
7. **New skills:** `grip_the_stair` (ward delay push), `rope_dive` (strip Haste on the ward), `close_the_hand` (`charge` 2 on the ward), `undertow_pull`, `crust_slam`, `breach` (`charge` 4, re-charging), `storm_call` (Pell: telegraphed removal of one spawn), `hold_the_stair`, `stand_firm`, `haul` (`requires_flag: ch08_hoist_rigged`), and the field `storm_dark` (Darkness on the party each turn, Slow on the ward).
8. **Virel's vowbound.json row** (caller Asha, `bound_flag: ch08_virel_bound`): fast multi-hit fire that delays its targets one rank per hit (spawn only, since the Reach is delay-immune), Attack, and the finisher ***Flare Line*** (fire, delay to all foes, `clears_field: storm_dark`). `call_rank` 3 as for Ilun, unless the bands say otherwise.
9. **Bands** (`sim.py --check`, for the combat reviewer): Waves 1–3 at `role_answer` 85–95% and naive 40–60% (a climax, not a wall). The Reach at `role_answer` 75–85%, `smart` 85–92% and naive ≤ 10% (the Drownbell's shape). A new sim policy, **`ward_guard`** (Provoke or *Hold the Stair* when a grip is predicted on the ward within two entries; Haul when the Climb has no Haste).
10. **Dependencies:** Liss's and Kerrid's base kits (`characters.json` has neither yet) come from the Ch5 and Ch6 playable tasks. This set-piece needs Liss's kit at Ch8 level and Toma's counter rule (his niche: counters).
11. **Lore and bestiary keys** for every new enemy (Read must work on all of them: `check_read_openings`).

### UI
1. **Ward and guest chips on the timeline:** a party-side variant colour with a stair glyph for the Climb, a Kirru glyph for Pell, and an enemy-side variant for the Surge. Each telegraph says it plainly: "A group reaches the wall-head in 2 turns", "Pell's call: the Tide Crawler will follow the sound", "The Surge brings more in 3 turns".
2. **Intent on the ward:** when a spawn's committed next action targets the Climb, its chip reads "→ the Stair" (as the Drownbell's chip reads "The Toll").
3. **The objective strip** (in `BattleBossStatus`): "The Fisher Stair: 2 more groups" for the wave, plus the carried count "Up the stair: 7". There is never a fraction of the town and never a death count (rule 6).
4. **Locked slot and unavailable member:** Toma's portrait marked "Holding the stair" with the swap greyed and the reason named; Kerrid greyed in formation, "Not with the party".
5. **Phase 3 prompt:** no Escape command appears; the objective strip reads "Get the last of them up."
6. **Tutorial prompts:** one per wave (Wave 1: "The climbers have turns too. Keep the spawn off the stair."; Wave 2: "Liss can haul the rope. The fliers will go for it."; Wave 3: "The Kirru on the wall is drawing them off. Watch his call.") and one per Reach phase (§5).

### Audio
The cue list in §6 and the SFX list under it. Priority: **`current_song`** (it must match Ch1's statement exactly), **`seawall_hold`** (three stacking stems) and **`pell_storm_note`** (a voice imitating a storm, never weather).

### Systems (dialogue format and data)
1. **New speakers:** `ivo` (CHAR_IVO), `marra` (CHAR_MARRA), `hobb` (CHAR_HOBB), `fenn` (CHAR_FENN), `tender` (CHAR_TENDER, generic) and `stillguard` (CHAR_STILLGUARD, generic).
2. **New grade ids** in `cues.json` `sets.grades`: `ch08_day`, `ch08_storm`, `ch08_coilspire_int`, `ch08_aftermath`.
3. **A numeric flag** (`ch08_stair_groups_up`) in `flags.tres`. The registry already holds `test_counter`, so confirm numeric flags are supported for story content.
4. **Chapter flow** (M3-ARC-01): B09 → wave 1 → B11 → wave 2 → B13 → wave 3 → B15 → the Reach → B17 → B18, with each wave a checkpoint and an autosave at B09 (ADR 0018's policy).

### Cinematics (reviewer)
Check §0's rules 2–4 against every Ch8 shot, especially B15 (W15–W17 and the W10 reuse from below), B17's frame rule (Kerrid never with the figure) and W24's hand. The actor marks and anim clip names are left to M3-C08-02.
