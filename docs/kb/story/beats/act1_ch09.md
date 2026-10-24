# Act I Beat Sheet: Ch9 "The Ebbing" at Corrow, night, and the end of Act I (M3)

Owner: Narrative (M3-C09-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch9 and the Prologue](act_outline.md), [bible §2 (glimmer), §4 (the Ebbing), §8 (the Kirru)](../bible.md), [voice guide](../voice_guide.md), [Pell](../characters/pell.md), [Kerrid](../characters/kerrid.md), [Toma](../characters/toma_okeru.md), [Asha](../characters/asha_velamir.md), [color script `ch09`, `prologue`](../../art/color_script.md), [tech/glimmer.md](../../tech/glimmer.md) (the mote system the Ebbing is built on), [ADR 0016](../../decisions/0016-act-two-restaging.md) (Ch9 row), [0017](../../decisions/0017-act-one-restaging.md) (e), [0020](../../decisions/0020-kerrid-restaging.md), [0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (e), (f) and the sweep-G note's S3 and S4, [N-04](../decisions_log.md) (the gilt line).
Previous chapter: [act1_ch08.md](act1_ch08.md). Next: Ch10 "Fen of the Kirru" (Act II).

Scripts: none yet (M3-C09-02). Sample lines set the voice only.

**The rules this chapter must keep:**
1. **Every mote in Ch9 is held.** They drift **down and seaward**, in `glimmer_held` cyan, and nothing in the chapter rises or turns gold. No `release()` is called anywhere in Ch9 (color script rule 1; `ch09`: "No gold gain: the light that should rise is being led down"). The act-break vigil (B09) is the one exception, because it is the Prologue's frame and keeps the Prologue's light.
2. **Kerrid is alone on the stair during the Ebbing,** exactly as ADR 0022 (f) and its sweep-G S4 note give it: one cutaway of a big man in a straw cape alone on the Fisher Stair, carrying a child's body up it while the motes go out to sea behind him. The old watch is on the shore at the Ebbing with the rest of Corrow, so nobody who knows his face sees him. **No mote drifts toward him** (that is Ch15's), and **no rope-burn glow** (it starts in Ch10).
3. **"Somebody's still below."** is said looking **south, out to sea, not at Asha** (sweep-G S3). "Below" is the sea: Imra under the storm and the held dead. It never means Asha. He is never framed or played as her guard, and he walks last behind the whole line, never at her side.
4. **No fire at the vigil** (ADR 0017 (e)). The only flame in the act-break frame is Rhen's lantern, which burns oil through a **burner** ("wick" is Mother Kell's alone; N-02 and ADR 0022 sweep-J).
5. **Nothing interrupts the Ebbing.** No spawn, no battle, no alarm. Ch9 has no fight at all.
6. **Pell's first spoken words in the game** are "Beautiful. And pointing the wrong way." (Ch8 gives him only the storm's note.)

---

## 0. The chapter in one paragraph

After the storm, Corrow lays its drowned out along the harbour strand under sailcloth, hundreds of them, and the low town is a black lake to the eaves behind the broken wall. The Tender paints a gold line on Asha's face "so the dead can find her", and Toma, among the shrouds, finds the friend who hugged him at noon. At the night's slack water Asha goes out alone on a raft with her lantern-staff and dances her first great Ebbing. The light of the dead comes up off the low town and off the kneeling mourners, follows her staff out across the harbour, and sinks into the sea. It is the most beautiful thing in Act I. Behind the wall, where nobody is looking, a big man in a straw cape carries a child up the Fisher Stair. Asha comes ashore radiant and spent, and quietly says the dead didn't want to go. The Kirru from the wall comes down the rocks, says it was beautiful and pointing the wrong way, and asks to walk where she is walking. At dawn Kerrid is waiting on the road out of Corrow, the place he said he was going, and when Rhen asks why he isn't staying, he looks out to sea and says somebody is still below. Seven of them walk out of Corrow. Then the Prologue's plaza at Iskarra again, all seven keeping their vigils apart, and an older Rhen says he didn't count them then.

**Emotional line:** numb aftermath (the shrouds) → private grief (Toma) → sacred hush (the gilt line, the raft) → awe (the Ebbing) → a cold undertone that nobody names (the motes that don't want to go; the man on the stair) → unease (Pell) → a quiet dawn and a sentence that doesn't explain itself → the frame, and a count.

**What the chapter must prove:** the game's mandated "first great dance for the dead" (SPEC §3.5) as Act I's most beautiful sequence, built so that it reads as quietly *wrong* in hindsight (bible §2); Pell joining; the party at seven; Kerrid's watch moving to the road; and a clean act break.

---

## 1. Running order

Time is in-world (one night and a dawn). Minutes are a first-time player's. **P**, **C** and **E** as in the [slice sheet](vertical_slice.md). Shot ids are proposed in §7 (N = Corrow at night, D = the dawn road, P02 = the Iskarra vigil).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **The strand of the drowned** | `ch08/corrow` night variant: the harbour strand, the broken wall-head | 21:00 | P | 6.0 | N01–N04 | `corrow_night` | A town counting. The player walks among the shrouds and the living, and hears what the stair-law means. | `ch09_heard_stair_clear` (optional bark) |
| B02 | *Side scene: "Shield-Mate"* (optional) | the strand, the Stillguard's row | any, before B03 | E | 4.0 | N05 | none (surf, distant hum) | Toma washes his friend's face. Rhen gives the Order's answer for the dead man. | `ch09_toma_knelt_with_ivo`, `ch09_rhen_answered_toma` (choice) |
| B03 | **The gilt line** | the strand, the raft's landing | 21:50 | E | 1.5 | N06, N07 | `corrow_night` → `silence` | The Order dresses her for its purpose, gently. Ysolde's warmth comes out as an instruction. | — |
| B04 | **The Ebbing, first movement: the gathering** | the harbour, the raft | 22:00 | C → E (held input) | 2.0 | N08, N09, N10 | `the_ebbing` (part 1) | The light comes up off the low town and off the mourners, and it hangs back. | — |
| B05 | **The Ebbing, second movement: the long line** | the harbour | 22:03 | E (held input) | 1.5 | N11, N12 | `the_ebbing` (part 2) | The whole harbour follows one lamp. The most beautiful frame in Act I. | — |
| B06 | **Cutaway: the stair** | `ch08/corrow` night, the Fisher Stair's landward foot | 22:05 | C | 0.25 | N13 | `the_ebbing` (continues, muffled by the wall) | A big man in a straw cape, alone, carrying a child up the stair while the motes go out to sea behind him. | — |
| B07 | **The Ebbing, third movement: letting down** | the harbour mouth | 22:06 | E (held input) → C | 1.5 | N14, N15 | `the_ebbing` (part 3) → `silence` | They sink into the sea glow. It is done, and it is lovely, and it is wrong. | `ch09_ebbing_danced` |
| B08 | **"Pointing the wrong way"** | the raft's landing | 22:15 | C | 3.0 | N16–N19 | `silence` → `corrow_night` (stripped) | Asha says the dead didn't want to go. A stranger agrees in a way nobody likes. He asks to walk with them. | `ch09_asha_said_they_hung_back`, `ch09_pell_joined` |
| B09 | **The road out** | `ch08/corrow` the landward gate and the coast road | 05:50 | E | 2.5 | D01, D02, D03 | `dawn_road` | "Somebody's still below." The line forms on the road, and Kerrid falls in last without being asked. | `ch09_kerrid_on_road`, `ch09_pell_named` |
| B10 | **Act break: the Iskarra vigil** | `prologue/iskarra_dusk` | (the frame's dusk) | C | 1.0 | P02, P03 | `hush_first_verse` (piano coda, as the slice's end card) → `silence` | The Prologue's plaza again. Seven, apart. A count. | `ch09_act_one_complete` |
| B11 | Act card | black | — | C | 0.2 | — | `silence` | "Act II: The Truth." | — |

**Totals:** critical path **19.5 min** (B01, B03–B11). With the side scene, **23.5 min**. Split: **6 min playable (31%)**, 6 min cutscene, 7.5 min in-engine. That is low on play on purpose. Ch9 is the act's exhale after Ch8's 30-minute set-piece, and its one P beat is a walk among the dead. The Ebbing's three held inputs keep the player's hands on it (§2 B04).

**Cut order if the chapter runs long:** B01 shortens to the strand alone (drop the broken wall-head loop). B03 folds into B04's opening (the gilt line is seen, not painted). Then B09's name exchange moves into B08. **Never cut:** the Ebbing (act_outline's cut notes: "never cut the Ebbing"), B06's cutaway, B08's Pell line, B09's "Somebody's still below.", or B10.

---

## 2. Beat detail

### B01. The strand of the drowned (P, 6 min)
- **N01:** the harbour strand outside the wall at 21:00, clear sky after the storm, a half moon low, sea-glow 0.15 (color script `ch09`). The drowned are laid out in rows along the shingle under sailcloth, hundreds of shapes, with oil lamps at intervals. **Faces are covered**; the only uncovered face in the chapter is Ivo's, in B02. Corrow's living move among the rows. People hum, low and broken (the Order hums: bible §4). Above, the motes of the drowned **hang** over the flooded low town behind the wall and over the strand: held, cyan, drifting very slowly sideways and down (rule 1). They haven't gone anywhere yet. They are waiting for the Ebbing (bible §9).
- **N02:** the broken wall-head walk, where the breach is a black gap and the low town is a lake of still water to the eaves, reflecting the motes.
- **Systems:** a save shrine on the wall-head, a chandler restocking on the strand (Act I's last shop), and **no random encounters** (rule 5).
- **Kerrid is nowhere.** If the player asks Toma (a talk prompt): *"Not since the stair."* Nobody looks for him. (He is bringing up the drowned, B06.)
- **Barks** (walk-past, ~140 words):
  1. **Old Marra** (optional, sets `ch09_heard_stair_clear`), to a child sitting beside a shroud: *"When the last one's up, the captain calls it. 'Stair's clear.' That's how you know you can come off the wall."* Child: *"Did he call it?"* Marra: *"Hobb? No. You don't. Not while there's anyone below."* This is the game's only explanation of the all-clear before the Ending's E3, where Kerrid finally says it. It names the living captain, Hobb, and says nothing of 1001 (Ch8 rule 3).
  2. Liss on the wall-head, sitting on the coil of her cut rope (if `ch08_hoist_cut_down`, always true on the critical path), to nobody: *"Thirty-one baskets. I counted. Don't ask me to count anything else."*
  3. Hobb on the strand, reading names off a slate in a flat voice.
  4. A Stillguard, low: *"Nine hundred years of this wall. You'd think we'd have learned to build a wider stair."*
  5. If `ch08_fed_the_beacon`: Fenn, kneeling in the front row, nods to Asha as she passes. No line yet (B08 has it).
- **Toma and Marra (background, no audio):** Cinematics, place one moment the player can see but not hear. Marra is holding Toma's hands at the end of a row and talking, and he is listening and nodding gently, the way you listen to the grieving. *What she is telling him (do not surface here):* that she saw her old captain on the stair in the storm. Toma takes it as what the old watch always sees after a Rising. **This is how the fishwife's word reaches Toma** (`ch08_fishwife_called`) without the player hearing the 1001 story here. Ch12's breath beat pays it off ("At Corrow one of the old watch told me she had seen her captain on the stair.").

### B02. Side scene (optional): "Shield-Mate" (E, 4 min) — see §4

### B03. The gilt line (E, 1.5 min)
- **N06:** at the raft's landing, Corrow's **Tender** paints the **gilt line** on Asha's face (N-04: "so the dead can find her"). This is its first appearance in the game. Asha holds still for it with her eyes shut. The gold is the Order dressing her for its purpose, and the camera is close enough that the player sees the brush.
- **Ysolde** adjusts Asha's grip on the lantern-staff (her warmth comes out as a technical instruction): *"Keep the lamp above your shoulder, not your head. They follow the light, not you. Let them."* (~20 words.) It is good advice for the rite, and in hindsight it is the instruction for leading the dead the wrong way. Played sincerely.
- **N07:** Asha steps onto the raft alone. Mourners all along the strand kneel **facing the water** (bible §4). Rhen kneels too: at the waterline if `ch02_rhen_stayed_with_dead` (he sat with his own dead at Haluna and knows how), otherwise at the back of the strand. Pell is not in the frame. `@music silence`.

### B04–B07. The Ebbing (C/E, 5.25 min) — the most beautiful sequence in Act I
**The dance.** On a lacquered raft poled out to the middle of the harbour, Asha dances with the lantern-staff: slow, wide, sweeping movements, the staff's bell-shells chiming, the open-cage lantern at its head. The motes come to the light. **Three movements**, each carried by **one held input** from the player: *"Hold to raise the staff"*. It is a single held button, with no timing, no score and no fail (precedent: act3_ending E4's "hold to take the strain with her"). Release and the dance waits, breathing. The player is not performing the dance. They are *letting it go on*. That's the point: in Act II, when the player learns which way the dead should go, they will remember holding the button.

- **B04, first movement, "the gathering" (C → E, 2 min).** N08 (a wide from the strand): the raft small on the black harbour, the broken wall behind it, the motes hanging over the low town. Asha raises the staff (input 1). The motes begin to come: up off the low town's still water, over the broken wall, and **off the mourners**. *The key image:* motes are **clinging** to the kneeling mourners (grief anchors: bible §2), hanging around them in slow orbits, and as Asha's staff sweeps past they leave them **reluctantly**, lagging and drifting back toward the shore before they are drawn on (§9 Rendering). N09: CU of a mourner's hand open on the shingle, the motes lifting off her fingers (lifting off, not rising up: they stay low). N10: Asha's face, the gilt line catching the lantern, eyes on the light.
- **B05, second movement, "the long line" (E, 1.5 min).** Input 2. N11: the hero frame. Thousands of motes stream after the staff in a long, curving river of cyan across the harbour, reflected in the still water, so the river runs in the sky and under it at once. Asha turns on the raft, and the river turns with her. Color script `ch09`: motes may bloom to 35% of the frame, and this is that frame. N12: from low on the water, the stream passing overhead and **sinking as it goes**, every mote sliding down and seaward.
- **B06, cutaway: the stair (C, 15 s).** **N13**, one shot, a cut: the landward side of the wall, the Fisher Stair rising out of the drowned low town at slack water. **A big man in a straw cape, alone, carrying a child's body up the stair**, climbing slowly, from a low wide angle with his back three-quarters to us, so the shot is a silhouette of the cape, the burden and the climb, never a face close-up. Over the wall-head behind and above him, the river of motes passes **seaward and down**, away from him. **Rules** (rule 2): he is alone, with no other figure on the stair; no mote turns toward him; no glow on his arms; the music is the Ebbing's, muffled by the wall between. The child's body is wrapped in sailcloth, its face covered. Then **cut** back to the harbour. Nobody in the party ever mentions it.
- **B07, third movement, "letting down" (E → C, 1.5 min).** Input 3. N14: Asha lowers the staff toward the harbour mouth, and the river of light goes out between the moles toward open sea and **sinks**. The motes slow as they pass under the surface and are absorbed into the sea's own faint glow, which brightens by a breath where they go in (§9 Rendering) and then settles. N15: the harbour dark again, the sea-glow a little brighter than before, Asha alone on the raft with the lantern. `@music silence`. Sets `ch09_ebbing_danced`.

### B08. "Pointing the wrong way" (C, 3 min) — *scripted*
- **N16:** the raft comes in. Asha steps off radiant and spent, the gilt line streaked with spray. Rhen is first to her.
  - Asha (when she is hurting she asks about your day; here it is about his night): *"Was it all right? From the shore?"*
  - Rhen, who has a joke for everything and doesn't have one now: *"It was the most— Yeah. It was."*
  - Asha, quieter, so that only he hears: *"They didn't want to go, Rhen. I had to keep asking them."* Sets `ch09_asha_said_they_hung_back` (the private notice in asha_velamir.md's Act I beats; it is paid off in Ch10, where she sees the dead lift and "can't unsee it").
- **N17:** a very tall shape has come down the rocks at the strand's end: the Kirru from the wall. Toma's hand goes to his spear and stays there. Pell stands still for a long time, the way the Kirru do, and then speaks his first words in the game:
  - Pell: *"Beautiful."* (a long gap) *"And pointing the wrong way."*
  - **Ysolde:** *"The rite has been danced the same way for nine hundred years."* Pell: *"Yes."* (That is the whole argument. He doesn't explain.)
  - Asha: *"Which way should they point?"* Pell doesn't answer. (He answers questions a scene later: the answer is Ch10's farewell-tide, where the motes lift straight up into the stars.)
  - Pell, to Asha: *"You go where it sleeps."* Asha: *"The Choir. Yes."* Pell: *"I will walk there too."*
  - Rhen: *"Who are you?"* No answer (B09 has it).
- **N18:** Toma. He has spent the night among his own dead (with or without the side scene), and the Order calls the Kirru soulless (bible §8). He looks at Pell a long beat, then:
  - Toma: *"...Walk behind me, then."* It is the same words he gave Rhen on Haluna's dock in Ch3 ("Then you walk behind me."). The player who remembers hears a man too tired to refuse, and kinder than his creed.
  - Asha: *"Thank you, Toma."* Sets `ch09_pell_joined`.
- **N19**, if `ch08_fed_the_beacon`: Fenn, getting up stiffly from the front row: *"Your mother danced for our drowned too. Same harbour."* Asha didn't know. She looks at the water. (ADR 0022 (a): Imra danced the Ebbing for Corrow in 1001.) Without the side scene, this line goes to Hobb, unprompted: *"The last Cantor danced it for us, the year of the last Rising. You did it well."*
- No line from Kerrid (absent). ~110 words.

### B09. The road out (E, 2.5 min)
- **D01**, 05:50, the coast road out of Corrow's landward gate. A washed, low gold dawn after the storm, the last warm light of Act I (§9 Art). The broken wall behind. **Kerrid is waiting at the milestone**, standing (he never sits), his straw cape still dark with seawater. The party comes up the road.
  - Rhen: *"Thought Corrow was where you were going."*
  - Kerrid: *"It was."*
  - Rhen: *"So?"*
- **D02**, Kerrid single: he looks **south, out to sea**, past the broken wall to the water. Asha is behind the camera, off frame, and is never in his eyeline in this beat (rule 3).
  - Kerrid: **"Somebody's still below."**
  - Rhen doesn't understand it, and for once doesn't joke. He lets it be. (Kerrid's Ch15 confession makes the line legible: a Cantor's road goes down to the Choir, and a captain doesn't come off the wall while anyone is still below. ADR 0022 (e).)
- **Pell and Kerrid:** Pell has stopped beside them. His crest lifts a little (the Kirru can smell anchored motes, and Pell knows what Kerrid is from the first day: pell.md). Kerrid meets his eye. Neither says anything. One held two-shot, no music change. (This is the only frame in Act I that holds both of the party's outsiders together. It is not a reveal; it is two men who know each other's kind.)
- **Pell answers last night's question** (his tell): to Rhen, unprompted:
  - Pell: *"Pell."*
  - Rhen: *"...Rhen."*
  - Pell: *"I know. You-people say names very often."*
  - Rhen sees the name-shell at Pell's throat is scraped blank. *"Your shell's blank."* Pell says nothing. (He answers in Ch10, outside Reedhollow, where he isn't allowed in.) Sets `ch09_pell_named` (the UI's "The Kirru" label becomes "Pell").
- **D03**, a high wide down the road: the line forms. Toma first, Pell behind him as he was told, then Asha, Ysolde, Liss and Rhen, and **Kerrid last**, as on a stair, without anyone telling him to. He walks behind the whole line, never at Asha's side (rule 3). Sets `ch09_kerrid_on_road`. ~70 words.

### B10. Act break: the Iskarra vigil (C, 1 min) — the Prologue frame recurs
- On D03's walking line, **cut** (no fade) to **P02**: the Prologue's broken plaza at Iskarra at dusk, the same seven keeping their separate vigils apart (Kerrid standing, Pell with his back to the sea, Ysolde with her book shut, Asha on the steps), and Rhen sitting beside Asha. The dusk is a little deeper than the Prologue's P01, and his lantern's flame is a little lower on its burner. Some time has passed on that plaza too. **No fire, no circle** (rule 4).
- **P03:** a slow push toward **Pell**, whose back is to the sea. The player has just learned what he thinks of the way the dead are led, and now sees him on the plaza, at the end of the road, turned away from the water. Nobody explains it. (In Act III he turns his back for Ressa. Here it reads only as strange.)
- **Rhen's VO** (older, plain fact, not foreboding, in the Prologue line's register, ADR 0022 (k)):

  > **"Seven of us walked out of Corrow that morning. I didn't count us then. I count us every night now."**

  *Why this line:* it states a plain fact (the party is seven from B09 on, the same seven on the plaza), and its weight comes only in hindsight. One of the seven was already dead when Rhen walked out of Corrow, and by the Ending he will have counted all of them going. It doesn't use "story", "last", "listen" or "chance", and it repeats nothing from the Prologue line. 19 words, in three short declaratives (voice guide: narration is "short, plain declaratives").
  *Alternate for Cinematics' review*, if the act break should name the Ebbing instead: **"That was the first time I watched her dance for the dead. It was the most beautiful thing I'd ever seen."** (21 words. It is still true at the Ending, which is why it hurts: beauty in decline.) Narrative recommends the first, because Act II begins with the second line's doubt (the farewell-tide), and the count is what the frame is about.
- Fade on the burner's flame. Sets `ch09_act_one_complete`.

### B11. Act card (C, 0.2 min)
Black. "Act II: The Truth" (loc key, UI's card). Then Ch10 opens.

---

## 3. Flags

All are to be declared in `game/data/flags.tres` (M3-C09-02 adds them).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch09_heard_stair_clear` | B01 Marra's bark (optional) | — (log only) | E3's "Stair's clear." lands for the player who heard what it means; the Ending doesn't branch on it |
| `ch09_toma_knelt_with_ivo` | B02 side scene | Ch15, Ch18 | **Ch15:** in Toma's confession to Liss, one extra line: "The man beside me at the shoals threw his. He is in the sea at Corrow now. I asked her to take him gently." **Ch18** (Toma's optional Haluna lifting): "I sent Ivo into the sea. I would like to do one of them right." |
| `ch09_rhen_answered_toma` | B02 choice | Ch15 | When Toma's faith breaks at Hollowmere and he stops saying "Be level", Rhen, who once gave him "And still" for a dead friend, is the one who sits with him |
| `ch09_ebbing_danced` | B07 (end) | Ch10 | Asha at the farewell-tide: she compares it aloud to her own dance (one line, different if `ch09_asha_said_they_hung_back`, always set on the critical path) |
| `ch09_asha_said_they_hung_back` | B08 (critical) | Ch10, Ch16 | the doubt she named privately to Rhen becomes the question she asks Pell in Act II ("Pell. Why would the dead want to go *down*?", voice guide) |
| `ch09_pell_joined` | B08 | party roster, the Act II chapter flow | Pell is in the party from Ch10 |
| `ch09_pell_named` | B09 | UI labels (Ch8's guest entry, the formation menu) | — |
| `ch09_kerrid_on_road` | B09 (critical) | Ch15 | the confession makes "Somebody's still below." legible |
| `ch09_act_one_complete` | B10 (end) | chapter flow (Ch10 gate), save summary | — |

---

## 4. The optional side scene: "Shield-Mate" (B02)

**Where:** the strand, at the row where the Corrow garrison has laid out its own dead with their round shields at their feet (N05). **When:** any time in B01 before B03, through a marker on Toma, who is kneeling. Requires `ch08_met_ivo` (always set on the critical path). **Length:** 4 min, ~170 words. **Speakers:** `toma`, `rhen`, `asha` (one line).

**Beats:**
1. Toma is kneeling at one shroud with the cloth folded back: **Ivo Brannick**, who lifted him off his feet at noon. His face is peaceful, washed by the sea, with the broken tooth showing a little. Toma is wiping the salt from it with the end of his own indigo sash, the way you'd wash a sleeping child's face. (A rhyme for attentive players: Grandmother Osu washing the wake-shells in Ch2.)
2. Rhen comes and stands near. Toma doesn't look up. Rhen doesn't joke.
3. Toma, of Ivo, fisher-boy warmth in his grief: *"He could not tie a hook knot. Seven years on this wall. I tied all of his."*
4. Rhen: *"You served with him long?"* Toma: *"Seven years. We stood on the same line once. At the shoals."* Rhen: *"Where we found Liss?"* A long pause. Toma: *"Another camp. Another year."* Rhen doesn't push. (He is learning to stand still.) *What this plants (do not surface):* the 1003 Brine Shoals burning (toma_okeru.md), with Ivo beside him on the line. Ivo was the only other man who knew what Toma did there, and now nobody does. Toma could carry it to his grave unasked. He confesses it anyway in Ch15, which makes the confession a choice. Liss is not in this scene.
5. Toma folds the cloth back over Ivo's face and says the Stillguard's words for their dead, the Order's greeting, waiting for the answer a living comrade would give: *"Be level."* Silence. The dead man can't answer it.
6. **Choice:**
   - *"And still."* Rhen gives the Order's answer for the dead man: Rhen, who in Ch3 joked about the rites. Sets `ch09_rhen_answered_toma`. Toma closes his eyes: *"Thank you."*
   - *(Say nothing.)* Toma waits, then says the answer himself, very quietly: *"And still."*
7. Asha comes down the strand with the lantern-staff, the gilt line fresh on her face, on her way to the raft. Toma, sincere and devout: *"Asha. Take him gently."* Asha: *"I'll take him first."* (He is asking for his friend to be led into the sea. That is love, and in hindsight it is wrong, and nobody here knows it. Pillar 2, played with no wink.)

**Rules:** no more than four Toma lines in a row (SPEC §3.6), broken by Rhen's presence and the choice. Toma keeps saying "Be level" (his faith is intact in Act I; voice guide). Nothing about the 1003 burning is said beyond "the same line, at the shoals". Ivo's face is the only uncovered dead face in Ch9, peaceful and never wounded.
**Payoff:** `ch09_toma_knelt_with_ivo` and `ch09_rhen_answered_toma` (§3).

---

## 5. No boss

Ch9 has **no battle of any kind** (rule 5): no boss, no random encounters, no forced fight. The template's boss slot is deliberately empty. Act I's climax fight was Ch8's Reach, and the "first great dance for the dead" must follow a disaster without being interrupted by one (ADR 0017 keeps the Ch7 match uninterrupted for the same reason). The chapter's mechanic, if it has one, is the Ebbing's held input, and what it teaches lands in Act II: **the player held the button that led the dead the wrong way.**

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `corrow_night` | B01, B03 (start), B08 (stripped) | Night bed | `corrow_day`'s wind melody slowed and alone over the surf, with the Order's congregational hum far off, broken, people humming while they do other things. |
| `the_ebbing` | B04–B07 | **Cutscene score, three parts**, Act I's centrepiece | The Order's choral hum (hummed, never sung with words: bible §4, §11) as the bed. The staff's bell-shells as a diegetic, pitched layer timed to the dance's sweeps. Low strings enter in part 2 and carry the long line. Part 3 descends, and the last chord sinks rather than resolves. **It must be gorgeous, and it must not rise.** The melodic line falls in every phrase (an original melody, not the Hush: the Ebbing is the Order's rite, and the Hush is the Cantor's song). Muffled through stone for B06's cutaway. **M3 final.** |
| `dawn_road` | B09 | Field bed, short | Sparse plucked strings and one wind instrument in open fifths: the Saltgrass Causeway's walking pulse (ch03) come back, slower and older. The pilgrimage resumes. |
| `hush_first_verse` (piano coda) | B10 | Reuse | The slice's end-card coda, piano alone. The act breaks share it, as the frame recurs. |

**SFX:** `staff_bell_shells` (the lantern-staff's chime, pitched in the cue's key), `raft_pole`, `harbour_lap` (slack-water ambience), `shingle_kneel` (a strand of people kneeling at once, used once at B03's end).

---

## 7. Camera shots by beat

New shot ids, for the `ch08/corrow` night variant (in `corrow.md` §5, with Ch8's W and F shots).

| Id | Shot | Lens / note |
|---|---|---|
| N01 | The strand of shrouds, lamps at intervals, motes hanging over the wall behind | 24 mm, rail |
| N02 | The broken wall-head walk; the low town a lake to the eaves | rail |
| N03 | Marra and the child beside a shroud (bark) | rail look-at |
| N04 | Toma and Marra in the background of the strand (silent) | rail; framed small, never closer than a mid-wide |
| N05 | The Stillguard row; Toma kneeling at Ivo (side scene) | locked 50 mm, plus inserts of the sash and of Ivo's face |
| N06 | CU, the Tender's brush painting the gilt line | 100 mm |
| N07 | Asha stepping onto the raft; the strand kneeling | 35 mm |
| N08 | The Ebbing wide, from the strand: the raft small, the broken wall behind | 24 mm, high |
| N09 | A mourner's open hand, motes leaving her fingers reluctantly | 85 mm, low |
| N10 | Asha's face, the gilt line in the lantern light | 85 mm |
| N11 | **The hero frame**: the river of motes across the harbour and its reflection | 18 mm, low over the water; motes ≤ 35% of frame |
| N12 | From the water's surface: the stream overhead, sinking as it passes | 24 mm, looking up |
| N13 | **The cutaway**: the landward foot of the Fisher Stair, Kerrid alone climbing with the child, the motes passing seaward over the wall-head | 28 mm, low wide; silhouette; **no face close-up, no glow** |
| N14 | The harbour mouth: the stream going out between the moles and sinking | 50 mm, from the raft's side |
| N15 | The harbour after: dark, Asha alone with the lantern | 35 mm, wide |
| N16 | The landing: Asha and Rhen | 50 mm two-shot, then singles |
| N17 | Pell on the rocks, the party turning | 35 mm, low on Pell (he's 2.3 m) |
| N18 | Toma, then Pell | singles, 85 mm |
| N19 | Fenn (or Hobb) getting up; Asha looking at the water | 50 mm |
| D01 | The road at the milestone, Kerrid waiting, the broken wall behind | 35 mm, `ch09_dawn` grade |
| D02 | Kerrid single looking south to sea | 85 mm; **Asha off-frame** |
| D03 | High wide: the line on the road, Kerrid last | 50 mm from a rise |
| P02 | The Iskarra plaza: the seven apart, Rhen beside Asha, the burner's flame lower | as P01, 10% tighter, dusk a little deeper |
| P03 | Slow push toward Pell, his back to the sea | 85 mm, `blend` push over ~8 s |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | N01, N02, N03, N04 | N04 must be readable but silent: no audio from the pair. |
| B02 | N05 | One locked shot plus inserts. Ivo's face only in the inserts. |
| B03 | N06 → N07 | A cut. |
| B04 | N08 → N09 → N10 | Cuts between, and the held input on N08. |
| B05 | N11 → N12 | N11 holds ≥ 6 s with the input. |
| B06 | N13 | **One shot, ~15 s, cut in and cut out.** No other figure on the stair; no mote toward him. |
| B07 | N14 → N15 | `@music silence` on N15. |
| B08 | N16 → N17 → N18 → N19 | Pell's two words are separated by ≥ 1.5 s of `@wait`. |
| B09 | D01 → D02 → D03 | D02 has no Asha in it, and the Pell–Kerrid two-shot is between D02 and D03. |
| B10 | (cut) P02 → P03 → fade | The cut from D03's walking line to P02 is hard, with no fade. |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 barks | 140 |
| B02 side scene | 170 |
| B03 | 30 |
| B04–B07 | 0 (the Ebbing has no dialogue) |
| B08 | 110 |
| B09 | 70 |
| B10 VO | 19 |
| B11 | 4 |
| **Total** | **~545 written** (~375 on a path without the side scene and optional barks) |

**Against SPEC §3.6:** at ~24 min, Ch9 is 1.3% of the game, so its fair share is **530–800 words**. It sits at the bottom of the band on purpose: the Act I centrepiece is wordless.

---

## 9. Requests to other roles

### Rendering (the Ebbing motes): file as one task, with a test scene
The Ebbing is built on `GlimmerField` (tech/glimmer.md). Everything here stays inside its meaning rules.
1. **Held only, the whole chapter.** Every field in Ch9 is in `HELD` mode: `glimmer_held` `#7FC6D9`, drifting **sideways and down toward `sea_direction`**, 0.05–0.2 m/s with a 15–30° downward bias, sinking through `water_height_m` and absorbed. **No `release()` call anywhere, no gold, nothing that rises.** Asha's warm rim (color script `ch09`: "slight warm lift on Asha only") is a character light on layer 2, never mote light.
2. **`sea_direction`** points out of the harbour mouth toward open sea (south-west in the Corrow layout, the same heading as the Ch8 storm's approach). The final movement must read unmistakably as the light **going down into the sea**, never up to the sky.
3. **The staff attractor:** one attractor on the lantern-staff head, following it each frame (`add_attractor(staff_head, ...)`; tech/glimmer.md's open item "the dance for the dead" is this). Tune the pull **low enough that the stream lags and sinks behind the staff**: when Asha raises the staff high, the motes must follow up toward it and then visibly fall away down and seaward again, so no still frame ever reads as light rising. Please add a test that a still at the staff's highest point has a downward median mote heading.
4. **Mourner attractors ("they didn't want to go"):** in the first movement, put small attractors on four to six kneeling mourners, holding motes in slow orbits around them (grief anchors). As the staff passes each, ramp that mourner's attractor strength down over ~4 s, so the motes leave **reluctantly**: they lag, drift back toward the shore for a moment, and are drawn on. That is the visual of Asha's line in B08 and of bible §2. The budget is 8 attractors per field (1 staff + up to 6 mourners + 1 spare). If more mourners are needed, use a second field.
5. **Density:** the hero frame (N11) wants **thousands** of motes, blooming to ≤ 35% of the frame (color script `ch09`). One field at ultra is 675. Propose a layout of several fields (the low town, the strand and the harbour stream), each tier-scaled, and measure the cost. The **low tier must still read as hundreds**. Use `height_bias` to pack the motes toward the water, not the sky.
6. **Reflection:** the harbour is at slack water and still, so `still_water_reflection` is on. The stream and its mirror should converge at the surface as the motes sink, so the river runs above and below the waterline at once.
7. **Absorption bloom (optional, if cheap):** where the stream sinks at the harbour mouth, a small local rise in sea-glow (≤ +0.03 over the frame's 0.15, easing back over ~10 s). The dead join the sea's glow, and that is exactly what the sea-glow is (bible §2). Rendering, say if it's feasible. If not, cut it, and the beat survives without it.
8. **The cutaway (N13):** a field over the wall-head moving seaward behind Kerrid. **No attractor on Kerrid, and no mote turns toward him** (that is Ch15's image), and no rope-burn glow (ADR 0022 (g)).
9. **The `.dlg` cue vocabulary** has no way to say "follow the staff" or "anchor on the mourners" yet (`cues.json` `vfx` takes `drift`, `motion`, `rate` and `count`). This is a joint request with Systems: a `follow=<actor|prop>` kwarg for an attractor host and a way to name anchor actors (for example `@vfx glimmer_held at=harbour drift=down_seaward follow=asha_staff anchors=mourners`), or a sequencer event that Cinematics drives.

### Art (color script)
1. **New frame `ch09_dawn`** (B09, 05:50): a washed, low gold dawn after the storm, the **last warm light of Act I** before Act II's overcast (SPEC §7.2). Low sun from the east, wet laterite road, and the sea to the south still faintly glowing in the dawn shadow.
2. **The act-break vigil (P02)** reuses `prologue`, a few minutes deeper into the dusk (sun ~1° lower) with the lantern flame's practical at ~0.85×. The motes in this frame are the Prologue's own, so the rule 1 exception in §0 is the Prologue's light, not Ch9's.
3. Confirm the gilt line's first appearance (N06) against N-04 and Asha's mask layer.

### Environment Art
1. **`ch08/corrow` night variant** (this chapter's zone): the breach in the wall (a black gap with rubble tipped seaward and two fallen Watchers face-up in the shallows), the low town flooded to the eaves at slack water, debris, the harbour strand with rows of shrouded dead under sailcloth (shapes only, **faces covered**: a set of shroud props with a variation parameter and oil lamps at intervals), the Stillguard row with round shields at the feet, the Ebbing raft (lacquered timber, poled, with a low rail-less deck), the cut hoist rope coiled on the wall-head, and the landward foot of the Fisher Stair rising out of still water for N13.
2. **The dawn road:** the coast road out of Corrow's landward gate, a milestone, wet laterite, scrub, with the broken wall behind and the sea to the south.

### Character Art
1. **Asha's gilt line** (N-04's mask layer), first worn at N06, and kept through B08 with spray streaks.
2. **Ivo, dead** (B02): the Ch8 NPC lying in state, face washed and peaceful, the broken tooth, never wounded on screen.
3. **Kerrid, soaked** (from Ch8): through B09. A child's sailcloth-wrapped body as a carried prop for N13 (face covered).
4. **Pell's blank name-shell** featured in B09 (a close insert).
5. **Corrow mourners:** a crowd variation set for kneeling, facing the water.
6. **Animation:** the Ebbing dance, three movements of slow, wide staff sweeps (a hand-keyed hero clip, about 4 min in total, looping per movement while the input is held), and the strand's kneel.

### Audio
The cue list in §6. **`the_ebbing` is the chapter's priority and an M3 final**: hummed, falling, gorgeous, never rising, original. Also the SFX list.

### UI
1. **The held input** for the Ebbing: one prompt, "Hold to raise the staff", with no meter, no score and no fail. Releasing it pauses the dance. It is the same widget as act3_ending E4's.
2. **The act card** for B11 ("Act II: The Truth"), a loc-keyed card. It may be the same widget as the Prologue's "one month earlier" title card.
3. **Pell's label:** "The Kirru" → "Pell" in every UI that shows him, once `ch09_pell_named` is set.

### Systems
1. **New speakers:** none beyond Ch8's (`marra`, `hobb`, `fenn`, `tender`, `stillguard`). Pell (`pell`) exists. Ivo has no lines in Ch9.
2. **New grade ids:** `ch09`, `ch09_dawn`, and `prologue` (the vigil; the Prologue's own `.dlg` notes "no grade cue exists for it yet").
3. **New events:** `act_card` (an int act number), and the Ebbing's held input as either an event or a new cue (shared with act3_ending E4).
4. **The `@vfx` extension** in Rendering item 9.

### Cinematics (reviewer)
Check §0's rules 1–3 against every shot, especially B06/N13 (alone, a silhouette, no mote toward him, no glow), D02 (Asha off-frame), D03 (Kerrid last, never at her side) and P02 (no fire). The Ebbing choreography and the hold-input pacing are yours.

---

## 10. What Act I hands to Act II

**The party at the act's end: all seven**, the Prologue's seven. Rhen, Asha, Toma, Ysolde (from Ch4), Kerrid (from Ch5), Liss (from Ch6) and Pell (from Ch9). Three active plus four in reserve from Ch10 (Pell is new to the formation menu).

**Asha:** three Vowbound (Ilun, Kahre, Virel), the verse-sleeve at **S3**, one reach-band (from the Ch4 crossing, N-01), the gilt line worn once. She has privately said the dead didn't want to go (`ch09_asha_said_they_hung_back`), and that doubt is Act II's door.

**What each thread carries in:**

| Thread | Where Act I leaves it | Act II pays it |
|---|---|---|
| The direction of the motes | Asha led thousands of them down and seaward and felt them hang back; Pell called it the wrong way and didn't explain | **Ch10:** the Kirru farewell-tide, where the motes lift straight up into the stars. Pell's answer to "Which way should they point?" |
| Pell | Joined, named, his shell blank, knows what Kerrid is | **Ch10:** not allowed into Reedhollow (the blank shell explained); **Ch11:** Nhoa is Ressa |
| Kerrid | "Somebody's still below."; walks last; was called "Captain?" by one fishwife; carried the drowned alone | **Ch10:** the rope-burns' held glow begins (ADR 0022 (g)); **Ch12:** Toma notices the breath and remembers Marra's word; **Ch15:** the confession |
| Toma | Ivo is in the sea; heard Marra's "captain on the stair" as grief; faith intact | **Ch12:** the breath beat; **Ch15:** the confession to Liss (with the Ivo line if `ch09_toma_knelt_with_ivo`) |
| Liss | One of Wenna's marks, kept secret, with Rhen's knowledge; her hoist cut down | **Ch11:** Rhen's stopped "My—" becomes the Dace reveal; more marks at Ch11–Ch13; **Ch20:** Virel |
| Rhen | Froze at a figure in the storm and heard his father's current-song | **Ch11:** admits he's Dace's son; **Ch17:** the ledger (including Imra humming on the Corrow stair, which Asha did too at Ch8 B13) |
| Wenna's needle | Found or not (`ch08_found_sail_needle`) | **Ch20:** Liss's Virel fight |

**Flags Act II reads from Ch8–9:** `ch08_liss_found_marks`, `ch08_fishwife_called`, `ch08_rhen_froze`, `ch08_rhen_told_asha`, `ch08_found_sail_needle`, `ch08_virel_bound`, `ch09_asha_said_they_hung_back`, `ch09_pell_joined`, `ch09_pell_named`, `ch09_kerrid_on_road`, `ch09_toma_knelt_with_ivo`, `ch09_rhen_answered_toma`, `ch09_act_one_complete`.

**Where Ch10 starts:** some days later, at the edge of **Ossa Fen** at dusk (`ch10/ossa_fen`), under Act II's overcast grade. The party has walked the coast road east from Corrow, and Pell has led them to the fen's mangrove channels, which are his people's and where he may not go in. The first image of Act II should be Pell stopping at the fen's edge while the others walk on. That is the act's first lesson in standing back.
