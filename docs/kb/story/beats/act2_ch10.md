# Act II Beat Sheet: Ch10 "Fen of the Kirru" at Ossa Fen and Reedhollow, dusk to dawn (M4)

**draft: pre-gate.** Written ahead of the Act I gate as ADR 0203 preparation (the Lead's assignment, 2026-10-30). Docs only: no `.dlg`, flag or data exists for anything below until the gate passes and M4-C10-01 is reviewed.

Owner: Narrative (M4-C10-01; drafted by the act2-plan track). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources:
- [act outline Ch10](act_outline.md) and [act1_ch09.md §10](act1_ch09.md) (what Act I hands over);
- [bible §2 (glimmer), §8 (the Kirru)](../bible.md), [voice guide](../voice_guide.md);
- the characters: [Pell](../characters/pell.md), [Asha](../characters/asha_velamir.md), [Kerrid](../characters/kerrid.md);
- art: [color script `ch10`](../../art/color_script.md), [ossa_fen.md](../../art/environments/ossa_fen.md) (the kit, the walks, shots F01–F04), [mangrove_drowner.md](../../art/creatures/act2/mangrove_drowner.md), [act2_roster.md](../../art/creatures/act2_roster.md);
- [act2_finals.md](../../audio/act2_finals.md);
- [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (g) (Kerrid's held glow starts here);
- the plan: [act2_plan.md §2 Ch10](../../plan/act2_plan.md).

Previous chapter: [act1_ch09.md](act1_ch09.md). Next: Ch11 "Lowlight".
Greybox: M4-C10-02 (`ch10/ossa_fen`: FenEdge with `pell_edge`, the root-walks, a side pocket, DrownerArena, `to_reedhollow`; `ch10/reedhollow`: the causeway Gate, the ring of platforms, the Shore with the `clutch` stone). Fights: M4-C10-03 (`tannin_archer`, `root_crab`, `fen_leech`).

Scripts: none yet (M4-A2P-001). Sample lines set the voice only.

**The rules this chapter must keep:**
1. **This is the chapter where the motes go up.** Everything Ch9 held down and seaward, Ch10 answers. The farewell-tide's motes rise straight up in slow vertical spirals, in `glimmer_lift`, and fade upward (bible §2's visual rule; color script `ch10`: "the only warm thing in the frame is release"). No mote in Reedhollow drifts sideways or down.
2. **The Kirru are a people.** They are never comic, never mystical props and never monsters (act2_roster). They speak the human tongue sparingly and literally (bible §8), with long silences. No human ritual forms are borrowed for them (ossa_fen.md).
3. **Pell does not enter Reedhollow.** He stops at the causeway and stays outside the whole time, as a scraped Kirru must (bible §8). He is never shown inside the ring.
4. **Kerrid's held glow begins, and nobody names it** (ADR 0022 (g)). In dim light his rope-burns leak the faintest `glimmer_held` cyan, one insert at most, never commented on. **No mote drifts toward him** (that is Ch15's image), and no Kirru says what he is.
5. **Nobody explains the truth.** The chapter shows which way the dead should go. It never says why the Order's way is wrong. Asha can't unsee it (asha_velamir.md), and that is enough.

---

## 0. The chapter in one paragraph

Some days east of Corrow, under the first grey sky of Act II, Pell leads the party to the edge of Ossa Fen and stops. The water is his people's and he is scraped, so he will walk the lashed roots behind them but never the water. Deep in the fen the Kirru's channel has been dead for a season: an Undertow-spawn has taken root in an old mangrove, and the light of three Kirru who drowned there is caught in its roots, held, neither sinking nor rising. The party cuts the roots, and when the first one breaks a few of those lights slip free and go *up*. At Reedhollow the clutch lets the humans in and keeps Pell out. At dusk the clutch gathers on the shore for the three who were held, sings a wordless rising song, and turns its back to the water, and the motes lift straight up through a gap in the cloud into the first stars. Asha, who led a whole harbour's dead down into the sea four nights ago, can't stop looking. Outside the causeway Pell has turned his back too, for strangers, and Kerrid stands beside him facing the water with a light on his arms that nobody sees. At dawn Asha asks Pell the question she has been carrying since Corrow, and he answers it.

**Emotional line:** the grey of a new act → unease (Pell stopping) → the fen's quiet wrongness (a dead channel) → effort (the Drowner) → a small, startling rise (the first freed lights) → welcome with a door shut (Reedhollow, Pell outside) → awe that hurts (the farewell-tide) → doubt that won't go back in its box (Asha) → a plain answer at dawn.

**What the chapter must prove:**
- the farewell-tide, Act II's first showpiece and the opposite of the Ebbing: the visual answer to "which way should they point?";
- Pell's exile made visible;
- Kerrid's held glow begun, unremarked;
- the Drowner as the act's first boss, teaching that breaking what holds the dead lets them rise.

---

## 1. Running order

Time is in-world (one late afternoon, a dusk and a dawn). Minutes are a first-time player's. Modes:
- **P**, play;
- **C**, cutscene;
- **E**, in-engine scene with player input.

Shot ids: F01–F04 are ossa_fen.md's composed shots; the rest are proposed in §7 (O = Ossa Fen, R = Reedhollow, T = the farewell-tide).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **Pell stops at the edge** | `ch10/ossa_fen` FenEdge | 16:40 | C | 1.5 | O01, O02 | `silence` → `ossa_fen` | Act II's first image: one of them standing back while the others walk on. | `ch10_started` (exists) |
| B02 | **The root-walks** | `ch10/ossa_fen` | 16:45 | P | 9.0 | F01, O03, O04 | `ossa_fen` | The fen as Kirru country: lashed roots, egrets, tea-dark water; random fights; the side pocket. | `ch10_found_scrape_mark` (optional) |
| B03 | **The dead channel** | `ch10/ossa_fen` DrownerArena approach | 17:30 | C | 1.0 | F03, O05 | `ossa_fen` → `silence` | Nothing green. Lights caught in the roots, held, unmoving. | — |
| B04 | **Boss: the Mangrove Drowner** | `ossa_fen_roots` (arena) | 17:35 | P | 7.0 | battle | `mangrove_drowner` (p1 → p2 `uprooted`) | The act's first boss; breaking a root frees a light, and it goes *up*. | `ch10_drowner_felled` |
| B05 | **What went up** | DrownerArena | 17:50 | E | 1.5 | O06, O07 | `silence` → `reedhollow` (distant) | The party saw something they've never seen. Nobody has a word for it yet. | — |
| B06 | **The causeway** | `ch10/reedhollow` Gate | 18:00 | C | 2.5 | R01, R02, R03 | `reedhollow` | Welcome with a door shut: the humans are let in, Pell is not. | `ch10_reached_reedhollow` (exists), `ch10_pell_kept_out` |
| B07 | **Reedhollow at evening** | `ch10/reedhollow` | 18:05 | P | 5.0 | F04, R04, R05 | `reedhollow` | A people who keep nothing of their dead. The name-shell cords; a gap where one hung. | — |
| B08 | *Side scene: "Why do they swim?"* (optional) | the ring, a platform | any, before B09 | E | 3.0 | R06 | `reedhollow` (stripped) | A child's question, and Asha with no Order answer to give. | `ch10_child_asked`, `ch10_asha_answered_child` (choice) |
| B09 | **The farewell-tide** | `ch10/reedhollow` Shore, the clutch's stone | 18:20 | C → E (held input) | 3.0 | F02, T01–T06 | `farewell_tide` | **The answer the game is built around.** The motes lift straight up into the stars. | `ch10_tide_witnessed` |
| B10 | **Outside the causeway** | `ch10/reedhollow` Gate (outside) | 18:35 | C | 1.5 | R07, R08 | `farewell_tide` (tail) → `silence` | Pell and Kerrid, the two outsiders, outside together; the first held glow. | — |
| B11 | **"Why would they want to go down?"** | the Gate at dawn | 05:40 | E | 2.0 | R09, R10 | `reedhollow` (dawn, sparse) | Asha asks the question she has carried from Corrow, and Pell answers it plainly. | `ch10_asha_asked_pell`, `ch10_complete` |

**Totals:** critical path **34.0 min** (B01–B07, B09–B11). With the side scene, **37.0 min**. Split: **21 min playable (62%)**, 7.0 min cutscene, 6.0 min in-engine. Play is high after Ch9's mostly cinematic exhale: the act opens with the player's hands on the party again. The farewell-tide is short and wordless, and the player holds it like the Ebbing (§2 B09).

**Cut order if the chapter runs long:**
1. B02 shortens: drop the side pocket.
2. B07 shortens to the shore walk.
3. B05 folds into the end of B04's victory.

**Never cut:** B01's image, B09 (act_outline's cut notes: "never cut the farewell-tide"), B10's two-shot, B11's answer.

---

## 2. Beat detail

### B01. Pell stops at the edge (C, 1.5 min)
- **O01:** the first frame of Act II. The overcast is total, a low pewter lid over grey-green mangroves, and the light is flat and cold after Ch9's gold dawn (color script `ch10`). The coast road ends in a mudbank where the fen's first channel opens, tea-dark and still. The party comes down the bank in its Ch9 line: Toma first, Pell behind him, then Asha, Ysolde, Liss, Rhen, and Kerrid last.
- **O02:** at the water's edge **Pell stops**. The camera does not stop with him. It keeps tracking with the line as the others walk on onto the first lashed root-walk, and Pell stays standing at the mudbank's lip, growing small and tall and still behind them, until Rhen notices and turns. (This is the act's first lesson in standing back: act1_ch09 §10.)
  - Rhen: *"You coming?"*
  - Pell (a long gap): *"The water is theirs. I walk on the roots. Not in."*
  - He steps onto the root-walk after them and takes his place behind Toma again, but from here on he never once steps off a lashed root into the water, even where the others wade (an animation rule for the whole chapter, §9 Character).
- ~30 words.

### B02. The root-walks (P, 9 min)
- **The zone:** Ossa Fen's root-walks per the greybox and ossa_fen.md §4: split poles lashed across mangrove prop-roots over tannin water, egrets on the roots, mudskippers on the banks (wildlife, never foes), reed beds in the slack.
- **Systems:**
  - random encounters (M4-C10-03's table: `tannin_archer`, `root_crab`, `fen_leech`, 30–50 m);
  - a save shrine at the first island (the Order's shrine, **old and unvisited**: lichen on the bowl, no Tender's mark since the last Calm; a shrine on Kirru land that the Kirru never use);
  - one chest in the side pocket.
- **The fights teach Act II's first lessons:**
  - the archer's jet delays (the timeline pushed back);
  - the root crab's root holds a hero in place (no swap);
  - the leech heals by what it takes.
  Each is a role answer the party already has.
- **Barks** (walk-past, ~110 words):
  1. Liss, to a lashed joint: *"Somebody knows knots. Three turns and a lock. She'll hold a cart."*
  2. Ysolde, of the egrets: *"Herons are sacred to nobody. It is restful."*
  3. Toma, quietly, to Asha: *"The Order calls this country empty. It is not empty."*
  4. Rhen, on a wobbling root: *"Love a walkway that moves. Really. Big fan."*
  5. Asha, stopping on a root to look at the water, to nobody: *"No glow."* (The fen's water has no sea-glow: the Kirru's dead lift, so none drift down into it. Nobody answers her. A clue for attentive players: Ch9's harbour glowed.)
- **Optional (side pocket):** a mangrove root with three deep **scratched lines** on it at standing height: the clutch's tally marks of where they stood to sing (the same three lines as the clutch's stone in B09). Liss, if `ch08_liss_found_marks`: *"Not ours. Not wright marks. Somebody counting."* Pell: *"Standing places."* Sets `ch10_found_scrape_mark`. A small bridge to Ch11's housing-mark and Ch12's keth (counting things).

### B03. The dead channel (C, 1 min)
- **F03:** the channel opens into a still pool under a great dead mangrove. Its crown is bare and bleached, its roots black and wet, nothing green over it (ossa_fen.md). The egrets are gone. No birds.
- **O05:** close on the roots. **A dozen small pale lights hang caught in them** like lanterns snagged in a net: held cyan, perfectly still, neither sinking nor rising. Pell, behind the line, softly hums the storm's note (his tell: overwhelmed).
  - Pell: *"Three of the clutch. Drowned here. At the full moon before last."* (He knows because he can hear them.)
  - Asha: *"They're still here."*
  - Pell: *"Held."*
- The roots move. ~25 words.

### B04. Boss: the Mangrove Drowner (P, ~7 min)
See §5.

### B05. What went up (E, 1.5 min)
- **O06:** the Drowner down, its root cage collapsed in the water. The snagged lights it held are loose. They do not drift down into the pool. **They hang a moment, then rise**: three slow vertical spirals going up past the dead crown into the overcast, in `glimmer_lift` gold (rule 1). The first time the player sees motes go up in the game (the Lamp Engine's in Ch11 is the second; the farewell-tide is the full statement).
- **O07:** the party watching. Nobody has a word for it.
  - Rhen (genuinely, no joke): *"...Huh."*
  - Ysolde (a long pause; corrects nothing): *"That is not the direction."*
  - Pell, already walking on along the roots toward Reedhollow: *"It is the direction."*
- ~20 words. The `reedhollow` cue comes in distant, from ahead.

### B06. The causeway (C, 2.5 min)
- **R01:** Reedhollow at the fen's heart. A ring of reed platforms round a dark lagoon, woven roost-shells on poles, and the shore with the clutch's stone (greybox; ossa_fen.md §4). The Kirru are already watching from the platforms: very tall, very still, crests half-lifted. They knew the party was coming, and they heard the Drowner fall.
- **R02:** at the causeway gate, **the eldest who still swims**: an old Kirru woman, grey at the muzzle, crest white. Her name is **Owa** (approved by ADR 0204 §4; banned-terms clean). The party learns it from the clutch, never from her. She looks at the humans one by one, long and plain.
  - At **Kerrid** her crest lifts a little, the way Pell's did on the Corrow road (act1_ch09 B09; Kirru can smell anchored motes: pell.md). She says nothing to him or of him. **Rule 4:** the beat is a look, never a line.
  - The eldest: *"You cut the roots. The three are lifted. Come in."*
  - **R03:** then she looks past them at Pell, at the blank shell on his throat.
    - The eldest: *"Not you."*
  - Pell doesn't argue. He steps back off the causeway onto the last root and stands.
  - Asha, Cantor-formal, kind: *"He brought us here. He walked behind us the whole way."*
  - The eldest: *"Yes. Behind. He is good at standing behind."* (Literal, not cruel. The Kirru have no idioms in the human tongue.)
  - She turns and goes in. Sets `ch10_pell_kept_out` (the flow's `party` step drops Pell for Reedhollow).
- **Kerrid stays outside too**, without being asked: he stands on the root beside Pell, facing the water. Nobody comments. (He never enters the place where the dead are tended: the same rule as the Sanctum in Ch13.) His `party` step is the flow's call; plan default: he leaves the walking party in Reedhollow and is shown at the gate in B10.
- ~70 words.

### B07. Reedhollow at evening (P, 5 min)
- **The zone:** the ring of platforms and roosts; the Kirru going about the evening, mending nets, carrying reed, swimming between platforms with only their heads above water; no shops (the Kirru don't trade coin); an inn-equivalent where the party may rest (a guest roost); **no fights** (act2_roster: the fen's foes stay out of Reedhollow's channels).
- **F04 and R04:** at the shore's edge, the **name-shell cords**: the living clutch's carved shells hung on cords between poles. The Kirru keep nothing of their dead (bible §8): these are the living's names. In one cord there is a **gap**, a knot with nothing on it. An attentive player can ask a Kirru about it.
  - Kirru net-mender: *"His."* (Looking out toward the causeway gate.)
- **Barks** (Kirru, sparse, literal, ~80 words):
  1. *"You-people carry heavy things. Your faces."*
  2. A mother, about her child: *"She asks too many questions. Good."*
  3. An old Kirru, watching Ysolde's book: *"You keep words in a box. We keep them in the throat."*
  4. Of the farewell-tide, asked by Toma: *"At dusk. You may watch. Do not stay watching."*
  5. Of Pell, asked by Rhen: *"Ressa's brother. She went to the sea. We sang. He watched."* That is all anyone will say about him. **"Ressa" is spoken here for the first time** (the payoff is Ch11, where Nhoa is Ressa). Nobody says she was a Cantor.
- **Toma, among the Kirru, if `ch09_toma_knelt_with_ivo`:** he is quiet, and at one point he stands watching a Kirru mother carry her child on her back through the water, and says, to Asha, *"They called them soulless. At the Bastion. Every morning, in the prayers."* No more. (The first crack Act II widens: toma_okeru.md.)

### B08. Side scene (optional): "Why do they swim?" (E, 3 min). See §4.

### B09. The farewell-tide (C → E, 3 min): the showpiece of Ch10
**The rite.** At dusk the clutch gathers at the tideline on the shore, round the clutch's stone (worn flat by their feet, three scratched lines where they stand). The three drowned the Drowner held are lifted already (B05). The clutch sings for them now anyway, because that is what is owed: the song isn't what lifts them, but the turning away is what lets them stay lifted. **One held input**, the same widget as the Ebbing's (act1_ch09 B04): *"Hold to watch."* Releasing it lets the song breathe; it doesn't stop the rite. This time **holding means watching, and the rite ends by letting go of the input**. At the song's peak the prompt changes to *"Release."* The player who held Asha's staff down into the sea now lets go so the dead can rise. That is the mechanic's whole meaning; there is no score and no fail.

- **T01 (C):** the clutch at the waterline, twenty or thirty Kirru standing very still in a long shallow arc, facing the lagoon. The cloud is still unbroken. The party stands back on the shore, with Asha in front. No Order hum anywhere (bible §4: the Order hums; the Kirru sing).
- **T02 (E, hold):** the song begins: wordless, rising, many voices finding one line (`farewell_tide`; it carries the Letting's first cell, act3_plan §4 Q2, and nobody in the game knows that yet). Over the lagoon the fen's own faint drifting motes, the season's ordinary Kirru dead who have been waiting for this dusk, begin to gather above the water. They gather **upward**, not toward the singers.
- **T03 (E, hold):** **the cloud breaks.** A gap opens straight overhead (color script `ch10`: "cloud breaks for the farewell-tide") and the first stars show in it. The motes rise toward the gap in slow vertical spirals and turn from held cyan to `glimmer_lift` gold as they climb (color rule 1's hue lerp, once each). The hero frame is **F02**: the clutch's backs to the camera, the cords of name-shells, the motes going straight up into the stars.
- **T04 (E, the prompt changes to "Release"):** the song reaches its top note and holds it. **The clutch turns its back to the water**, all at once, every Kirru, so the dead are not anchored by being watched (bible §8). On release the song ends. The motes go up into the gap and are gone.
- **T05 (C):** Asha. **She has not turned around.** She is facing the water with her hands open, and her face is the whole beat: she led thousands down four nights ago and called it right. Ysolde gently turns her by the shoulder, a technical instruction as always: *"Turn around. They asked us not to stay watching."* Asha turns. Rhen is already turned (he copies the Kirru: he always does what the room does). Toma turns last, slowly, a temple warrior turning his back on the dead for the first time in his life.
- **T06 (C):** the cloud closes. The shore is dark. Asha, very quietly (reads `ch09_ebbing_danced`; the one line act1_ch09 §3 promises): *"Mine went down."* Sets `ch10_tide_witnessed`.
- ~25 words. **Rule 1:** nothing in T02–T04 drifts sideways or down, and no mote goes toward the singers, the party or Kerrid (who isn't here: B10).

### B10. Outside the causeway (C, 1.5 min)
- **R07:** cut to the causeway gate, where the song carried. Outside on the last root, **Pell stands with his back to the water and to the whole rite**, turned away as the clutch turned, for three strangers. He is not allowed to sing, and he hasn't sung, but he turned. (pell.md: "The party sees the farewell-tide from a distance while Pell stands with his back to them." In Act III he turns his back for Ressa at last; here it is easy, because they aren't his.)
- **Kerrid** stands beside him facing the other way, **toward the water**, as he faced the sea on the Corrow road. He watches the gold go up. The two of them stand back to back, one held and one scraped, and neither speaks.
- **R08:** an insert, very close, in the last of the dusk: **Kerrid's forearm**, the rope-burns spiralling from palm to elbow, and in the dark of the scar the faintest cyan, like a coal you only see when the lamps are out (ADR 0022 (g); kerrid.md §Scars). **Rule 4:** no mote leaves him and none comes to him; no one sees it; the camera doesn't linger past two seconds; nothing in the score marks it.
- No dialogue.

### B11. "Why would they want to go down?" (E, 2 min)
- **R09:** dawn at the causeway gate, grey again. The party comes out. Pell and Kerrid are where they were, as if they hadn't moved all night. (Kerrid doesn't sleep. Pell, the Kirru way, stood.)
- Asha goes straight to Pell. She doesn't ask about his night (her tell is starting to stop: voice guide):
  - Asha: **"Pell. Why would the dead want to go *down*?"** (the voice guide's sample line; reads `ch09_asha_said_they_hung_back`, set on the critical path)
  - Pell (he answers a scene later, and this is the scene later; the question from Ch9 B08 too: "Which way should they point?"): *"They do not want to. You-people ask them."*
  - Asha: *"...And they come."*
  - Pell: *"You are very good at asking."*
- **R10:** Rhen, seeing the blank shell again, the question Ch9 left open (act1_ch09 B09):
  - Rhen: *"Your shell. They scraped it because of her. Ressa."* (if he heard the bark in B07; otherwise *"Your shell. Why's it blank?"*)
  - Pell: *"I did not turn around."* (a long gap) *"She went into the sea. I watched her go. Seventy years."* (The voice guide's "My neck is very tired" is held back for Act III.)
- Pell walks on first, on the roots, toward the way out of the fen. The party falls in. Kerrid last. Sets `ch10_asha_asked_pell`, `ch10_complete` (the flow hands off to Ch11).
- ~70 words.

---

## 3. Flags

Declared in `game/data/flags.tres` when the gate passes (M4-A2P-010 adds them). `ch10_started` and `ch10_reached_reedhollow` already exist (M4-C10-02).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch10_started` | B01 (exists) | flow | — |
| `ch10_found_scrape_mark` | B02 side pocket (optional) | Ch12 | At Cloudloom Liss compares Ama's keth to "the Kirru's standing marks": counting things the Order never read |
| `ch10_drowner_felled` | B04 | flow, Ch11 | The Lamp Engine's release (Ch11) is "the second time"; Ysolde: "That is twice." |
| `ch10_reached_reedhollow` | B06 (exists) | flow | — |
| `ch10_pell_kept_out` | B06 | flow (`party` steps), Ch18 | Pell's return to Reedhollow in Act III walks back through the same gate |
| `ch10_child_asked` | B08 side scene | Ch18 | The child is older at the Act III revisit and asks Asha a second question |
| `ch10_asha_answered_child` | B08 choice | Ch16 | At the Choir, Asha's refusal includes the child's question in her own words |
| `ch10_tide_witnessed` | B09 (critical) | Ch11, Ch16, Ch18 | Nhoa's Swell (*Farewell-Tide*) is named for what Asha saw; Act III's farewell-tide lesson |
| `ch10_asha_asked_pell` | B11 (critical) | Ch16 | The doubt becomes a refusal |
| `ch10_complete` | B11 (end) | flow (Ch11 gate) | — |

**Act I flags this chapter reads:** `ch09_pell_joined`, `ch09_pell_named`, `ch09_ebbing_danced`, `ch09_asha_said_they_hung_back`, `ch09_toma_knelt_with_ivo`, `ch08_liss_found_marks`.

---

## 4. The optional side scene: "Why do they swim?" (B08)

**Where:** a reed platform in the ring at evening (R06), where Kirru children are swimming. **When:** any time in B07 before the farewell-tide, through a marker on Asha, who has sat down at the platform's edge. **Length:** 3 min, ~150 words. **Speakers:** `asha`, `kirru_child`, `rhen` (one line).

**Beats:**
1. A Kirru child (young, perhaps twenty, which is a child for the Kirru, already taller than Rhen) climbs out of the water beside Asha, dripping, and looks at her lantern-staff for a long time.
2. Child: *"You are the one who makes the dead swim."* (The Kirru know the Ebbing; the Order's Cantors dance it on every coast.)
3. Asha, honest: *"I led them out to sea. At Corrow."*
4. Child: *"Why do they swim? Ours go up."*
5. Asha starts the Order's answer, the one she has known all her life, and stops partway: *"They go to rest in the sea, until the—"* She doesn't finish it.
6. **Choice:**
   - *"I don't know."* Sets `ch10_asha_answered_child`. The child accepts it completely, as the Kirru do: *"Then ask them."* The child slides back into the water.
   - *"Because we're afraid to let them go."* Also sets `ch10_asha_answered_child`. The child looks at her a long time: *"Yes. You-people hold everything."* The child slides back into the water.
7. Rhen has come and sat down a little way off. He doesn't joke. Asha, without looking at him: *"I didn't finish the sentence, Rhen. I've said it all my life."*

**Rules:** the child is curious, not wise. It is not a mystic, and it asks because it wants to know. Asha is not corrected or lectured: the answer she can't finish is the beat. No Kirru adult intervenes.
**Payoff:** `ch10_child_asked`, `ch10_asha_answered_child` (§3).

---

## 5. The boss: the Mangrove Drowner (B04)

**Lore justification (SPEC §6.7):** Undertow-spawn come up the estuary as a slick of black water, which took root in a mangrove's prop-roots (mangrove_drowner.md). It drags the dead down. The three Kirru who drowned in its channel couldn't lift: their light is snagged in its roots, held. It is the fen's version of what the Order does on every coast.

**Arena:** `ossa_fen_roots` (env-art, M3-ENV-718): the mudbank under the dead tree; `BossAnchor` in the water among its roots. Staged ids (M3-BPR-419): enemy `mangrove_drowner`, phase `uprooted`.

**Phases (two):**
1. **Rooted (100–50%).** It is a tree first, and its roots are the fight.
   - **The drag:** a telegraphed charge (its own skill, `drowner_haul` in the bosses lane; `root_drag` is the root crab's; one turn's warning on the timeline). The water rises along the roots and pulls the party's footing: the field rule gives **Slow** to the front hero for a turn, so the timeline visibly stretches.
   - **The snagged roots:** two **break parts**, the two root clusters with the most snagged lights (the sheet's proposal; M3-CRE-621's notes). Breaking one frees its lights: a short in-battle beat where three or four motes rise straight up past the dead crown (VFX, M4-A2P-058). This is **the first upward lift in the game**. Breaking both roots shortens phase 1.
   - **Weakness:** fire (dead wood), so Ysolde is the role answer. Kerrid's armour break works on the roots.
2. **Uprooted (below 50%).** It tears the trunk up and stands on three root-clusters. It reaches for the drag every other turn, and its crushing roots strike the back line. It is faster and less armoured, so Rhen's turn manipulation is the answer.
   - **Pell's lesson:** if Pell **Listens** to the drag (his kit, M3-C09-07), he learns it, and his version pulls an enemy's timeline back. The first time the player learns a boss's tool from the boss itself in Act II.

**What it teaches:** what holds the dead can be broken, and when it breaks they rise. That is the act's thesis in one mechanic, a chapter before anyone says it.

**Balance:** the Act II boss band (balance_targets.md): naive ≤ 3%, role_answer 55–80%, smart 70–90%, p90 ≤ 80 turns, on the Ch10 loadout (M4-A2P-019; seven heroes, Pell in). It is not `scripted`: Escape is allowed.

**Music:** `mangrove_drowner` (two stems; phase 2 `uprooted`), rendered (M3-AUD-844).

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `ossa_fen` | B01 (in), B02, B03 (out) | Zone loop (final exists, M3-AUD-840) | — |
| `mangrove_drowner` | B04 | Boss, two stems (exists, M3-AUD-844) | Phase 2 on `uprooted`. |
| `reedhollow` | B05 (distant), B06, B07, B11 (dawn, sparse) | Zone loop (final exists, M3-AUD-840) | Its clutch line carries the Letting's first cell. |
| `farewell_tide` | B09, B10 (tail) | **Cutscene score**, ~90 s (not yet written, act2_finals.md; M4-A2P-090) | Wordless Kirru voices (synthesised, as `act2_voices.py`), rising in every phrase: **the opposite of `the_ebbing`**, whose line falls in every phrase. No Order hum. One sustained top note held while the clutch turns, then it ends on the rise and does not resolve down. The **Letting's first cell** is in the melody (act3_plan §4 Q2). Built from `reedhollow`'s clutch line. It must be the most beautiful thing in Act II's first half, and it must go **up**. |

**SFX:**
- `root_creak` (the walks);
- `egret_lift` (birds leaving the dead channel in B03, heard, not seen);
- `kirru_whistle_click` (the clutch's speech among themselves, under barks);
- `reed_turn` (thirty Kirru turning at once on the shore, used once in T04).

---

## 7. Camera shots by beat

New shot ids for `ch10/ossa_fen` and `ch10/reedhollow` (to add to ossa_fen.md §3 beside F01–F04).

| Id | Shot | Lens / note |
|---|---|---|
| O01 | The fen's edge: the party coming down the bank under the pewter sky, the first channel | 28 mm, high wide |
| O02 | Tracking with the line onto the root-walk; Pell left at the lip, small and still behind | 35 mm, dolly; **the camera does not stop with Pell** |
| O03 | A root-walk through the mangroves, egrets on the roots | rail |
| O04 | The side pocket's scratched root (optional) | rail look-at |
| O05 | CU: lights snagged in black wet roots, unmoving | 85 mm |
| O06 | The freed lights rising past the dead crown | 24 mm, looking up; **every mote rises** |
| O07 | The party looking up | 50 mm, low |
| R01 | Reedhollow from the causeway: the ring, the roosts, the Kirru on the platforms | 24 mm |
| R02 | The eldest at the gate; her look at each of them; her crest at Kerrid | 50 mm singles; Kerrid's is a held look, no line |
| R03 | "Not you." Pell stepping back off the causeway | 85 mm on the eldest, reverse on Pell |
| R04 | The name-shell cords at the shore; the empty knot | insert, 100 mm |
| R05 | The ring at evening, Kirru swimming between platforms | rail |
| R06 | The platform's edge: Asha and the child (side scene) | 50 mm, locked |
| T01 | The clutch's arc at the waterline from behind the party | 35 mm |
| T02 | Low over the lagoon: the motes gathering above the water | 24 mm, low |
| T03 | The cloud gap opening; the first stars; motes climbing toward it | 18 mm, looking up |
| F02 | **The hero frame** (ossa_fen.md): the clutch's backs, the cords, the motes going straight up | 35 mm |
| T04 | The clutch turning all at once | 50 mm, wide enough to hold the whole arc |
| T05 | Asha, still facing the water; Ysolde's hand on her shoulder | 85 mm |
| T06 | The shore dark after the cloud closes | 35 mm |
| R07 | Outside the gate: Pell with his back to the rite, Kerrid facing the water, back to back | 50 mm two-shot, profile |
| R08 | **Insert:** Kerrid's forearm, the faint held cyan in the scar | 100 mm; **≤ 2 s; no mote; no music mark** |
| R09 | Dawn at the gate; Asha going straight to Pell | 35 mm |
| R10 | Pell single as he answers | 85 mm |

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | O01 → O02 | O02 is one continuous move. Pell's stop must be seen from the moving line, not cut to. |
| B03 | F03 → O05 | The egrets leave on the cut into F03 (sound only). |
| B05 | O06 → O07 | O06 holds until the last mote has left the top of frame. |
| B06 | R01 → R02 → R03 | The eldest's look at Kerrid is the same length as her look at the others; only the crest differs. |
| B09 | T01 → T02 → T03 → F02 → T04 → T05 → T06 | The held input runs from T02 to T04. F02 holds ≥ 6 s. |
| B10 | R07 → R08 → (cut back) R07 | Hard cuts. R08 is under two seconds. |
| B11 | R09 → R10 | — |

---

## 8. Word counts

| Beat | Words |
|---|---|
| B01 | 30 |
| B02 barks (incl. optional) | 130 |
| B03 | 25 |
| B05 | 20 |
| B06 | 70 |
| B07 barks | 100 |
| B08 side scene | 150 |
| B09 | 25 |
| B10 | 0 |
| B11 | 70 |
| **Total** | **~620 written** (~420 on a path without the side scene and optional barks) |

**Against SPEC §3.6:** at ~35 min, Ch10 is about 2% of the game, so its fair share is **800–1,200 words**. It sits under the band on purpose. It is the Kirru's chapter, and they speak little, and the showpiece is wordless. Ch11 (Rhen's admission) and Ch12 (Ysolde's confession) carry the act's early words.

---

## 9. Requests to other roles

### Rendering (the farewell-tide and the freed lights): one task, M4-A2P-049
1. **Lifted motes, first use in play.** `GlimmerField` in **LIFT** mode for B05 and B09: slow vertical spirals, `glimmer_held` cyan lerping once to `glimmer_lift` gold as each climbs (color rule 1), fading upward. **Nothing sideways or down** in Reedhollow (rule 1). Please add a test that a still at T03 has an upward median mote heading (the mirror of act1_ch09's Ebbing test).
2. **The cloud gap (T03):** an animated opening in the overcast straight over the lagoon, with the first stars behind it. It closes again by T06 (color script `ch10`).
3. **Snagged motes (B03, B04):** a held field anchored to the Drowner's root clusters, perfectly still, with a release on each break part that sends that cluster's motes up (the in-battle lift, with M4-A2P-058).
4. **Kerrid's held glow (R08):** the first use of his rope-burn emission (kerrid.md §9, M4-A2P-054): ≤ 0.15 in this shot, readable only against the dusk. No motes.
5. **No sea-glow in the fen** (B02's "No glow"): `tannin_fen`'s night sea-glow is 0.05 (color script); keep it at the floor in Reedhollow's lagoon too.

### Art (color script)
1. Confirm `ch10`'s **cloud-break** frame for T03 and F02, and a `ch10_dawn` variant (grey, flat) for B11.

### Environment Art (M4-A2P-040)
1. The kit exists (M3-ENV-718, M3-ENV-733). Place it per ossa_fen.md §4.
2. Add: the **old Order shrine** on the first island (lichened, unvisited); the side pocket's **scratched root**; the **empty knot** on the shore's name-shell cord (a gap, not a blank shell: the blank one is at Pell's throat); and a guest roost.
3. The dead tree's pool must be **bird-free**; the rest of the fen has egrets.

### Character Art
1. **The Kirru** (M4-A2P-053): the eldest (grey muzzle, white crest), a mother, a net-mender, children (a 20-year-old child is already ~1.9 m), and the clutch of twenty to thirty for the shore. The same base as Pell, with age and size variants and carved name-shells (Pell's is blank).
2. **Animation:**
   - the clutch's **turning away**, all at once (one hero clip, retimed per actor with small offsets so it reads as many people, not a copy);
   - Kirru **standing still** for long holds (crest idle only);
   - swimming between platforms with the head above water;
   - Pell's chapter-wide rule: **he never steps off a lashed root into the water** (pathing and wade animation off for him in Ch10).
3. **Kerrid:** the rope-burn emission mask (M4-A2P-054).

### Audio
1. `farewell_tide` (§6), the chapter's priority (M4-A2P-090).
2. The SFX list in §6.
3. Kirru voices for barks: soft, unhurried, whistle-click under the human tongue.

### UI
1. The held input reuses the Ebbing's widget with two prompts ("Hold to watch" → "Release"). The **change of prompt at the peak** is the new part: the player ends the rite by letting go.
2. The formation menu shows Pell (and Kerrid, by the flow's call) as "Outside the causeway" while in Reedhollow (`unavailable_key`).

### Combat (M4-A2P-010, M4-A2P-020)
The Drowner as §5: two break parts tied to the snagged-root clusters, the drag as a telegraphed Slow field rule, fire weakness, phase 2 `uprooted`. Pell's Listen learns the drag. The rooted status for `root_crab` (M4-A2P-020).

### Systems / Chapters (M4-A2P-010)
1. **Speakers:** `kirru_eldest`, `kirru_child`, `kirru` (generic). New grade ids `ch10_tide` (the cloud break), `ch10_dawn`.
2. **Party steps:** Pell out at the causeway (B06) and back at the gate (B11); Kerrid likewise by default.
3. Ch9's act card hands off to B01.

### Cinematics (reviewer)
Check §0's rules against every shot, especially:
- O02 (the camera doesn't stop with Pell);
- R02 (the eldest's look at Kerrid is a look, not a line);
- T02–T04 (every mote rises; none toward anyone);
- T05 (Asha still facing the water);
- R07 and R08 (back to back; the glow ≤ 2 s, unremarked).
The farewell-tide's choreography and the hold-then-release pacing are yours.

---

## 10. Open questions for review

1. ~~The eldest's name~~: **resolved by ADR 0204 §4: Owa.**
2. **Kerrid in Reedhollow:** the plan default keeps him outside with Pell (B06, B10). If the flow needs him walkable in the ring, he must still be absent from B09's frames.
3. **"Ressa" spoken in B07:** this sheet names her once, as Pell's sister, so Ch11's binding lands as a recognition. If Narrative wants Ch11's reveal colder, cut the name from the bark and let Pell name her first in Ch11.
