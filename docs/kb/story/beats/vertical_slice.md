# Vertical Slice Beat Sheet: Ch2–3 at Haluna (M2)

Owner: Narrative Director (M1-NAR-02). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch2–3](act_outline.md), [voice guide](../voice_guide.md), [Vowbound §1 Ilun](../vowbound.md), [Haluna mood brief and shots](../../art/environments/haluna.md), [color script `ch02`/`ch03`](../../art/color_script.md), [`.dlg` format](../../tech/dialogue_format.md). Decisions made here are in [decisions_log.md](../decisions_log.md).

Scripts:
- **Cutscene A, "The Girl on the Beach":** [`game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg`](../../../../game/data/dialogue/ch02/ch02_girl_on_the_beach.dlg)
- **Cutscene B, "The First Verse":** [`game/data/dialogue/ch03/ch03_the_first_verse.dlg`](../../../../game/data/dialogue/ch03/ch03_the_first_verse.dlg)
- Every branch of both is tested in `tests/unit/test_dialogue_vs_scenes.gd`.

---

## 0. The slice in one paragraph

A boy who has just lost his whole town washes up on the most loved beach in the game, and the girl who finds him is two days from leaving it forever. Over one day (dawn to night) he learns her name, walks her to her first temple, hears her sing his dead father's lullaby, fights beside her when the tide turns, and asks to come along. He doesn't yet know what he is walking her toward. The player should finish the slice *liking* these three people, and uneasy about a word nobody will define: **Cantor**.

**Emotional line:** grief held at arm's length (dawn) → warmth (noon) → exposure (afternoon causeway) → a quiet sacred hush (shrine) → joy with a cold edge (sunset verse) → threat (rising tide) → a promise made in the dark (night dock).

**What the slice must prove for M2** (SPEC §10.2): one coastal village, one route, one small temple trial, one Vowbound, a two-phase boss, two cutscenes with facial animation, and three final music cues. All of these are placed below.

---

## 1. Running order

Time is in-world (one day). Minutes are the player's, at a first-time pace. **P** = playable, **C** = letterboxed cutscene (`.dlg`, sequencer-driven), **E** = in-engine scene (no letterbox, the player keeps the camera rail, `.dlg` without `@letterbox`).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **Cutscene A: The Girl on the Beach** | `ch02/haluna` beach | 06:20 | C | 4.0 | H05, H06, H01 | `haluna_dawn` | Waking into kindness. Grief arrives as cyan light in the water, and he can't look at it. | `ch02_met_asha`, `ch02_rhen_named_lantern`, `ch02_rhen_stayed_with_dead` |
| B02 | Neme's table | `ch02/haluna` Neme's house | 12:20 | E | 1.0 | H02 (exit) | `haluna_village` | Being fed by strangers. Neme's fear shows in how much food there is. | — |
| B03 | **Haluna by day** | `ch02/haluna` | 12:30 | P | 6.0 | H02, H03, H04, H07, H09 | `haluna_village` | A festival for a departure. Rhen hears "Cantor" in four pieces and misses what they add up to. | `ch02_saved_once` (gameplay) |
| B04 | *Side scene: Pila's Granddaughter* (optional) | `ch02/haluna` wake-shell wall | any, before B05 | E | 4.0 | H08 | none (ambience) | The names of the ones who went. A boy who went so his sister wouldn't have to. | `ch02_heard_pila` |
| B05 | Low tide | `ch02/haluna` causeway head | 14:20 | E | 1.0 | C01 | `haluna_village` → `saltgrass_causeway` | The pilgrimage begins, and nobody calls it that. Asha asks Rhen to come "to see it". | — |
| B06 | **Saltgrass Causeway** | `ch03/saltgrass_causeway` | 14:30 | P | 7.0 | C02–C07 | `saltgrass_causeway`, `battle_standard` | Three voices walking. The path leads somewhere that doesn't come back. | — |
| B07 | **Shell Shrine trial** | `ch03/shell_shrine` | 15:30 | P | 5.0 (+1.5) | S01–S05 | `shell_shrine_interior` | Water obeying a gentle hand. A tended, loved place. | `ch03_found_net_float` (optional pickup) |
| B08 | **Cutscene B, part 1: the steps** | `ch03/shell_shrine` | 16:00 → 18:00 | C | 3.0 | S07, S08, S06 | `shell_shrine_interior` → `silence` | "Do you know what a Cantor is?" Toma refuses to answer for her. | `ch03_rhen_asked_after` |
| B09 | **Cutscene B, part 2: the first verse** | `ch03/shell_shrine` door | 18:05 | C | 3.0 | S09, S10, C08 | `hush_first_verse` → `silence` | Joy with a cold undertone. The lullaby. Recognition. The bell answers. | `ch03_ilun_bound`, `ch03_rhen_named_lullaby`, `ch03_first_verse_sung` |
| B10 | **Boss: the Drownbell** (two phases) | `ch03/saltgrass_causeway` arena | 18:15 | P | 6.0 | C08, C09, C10 | `drownbell` (2 stems), `ilun_summon` sting | The tide takes the path. The dead step in front of the living. | `ch03_drownbell_defeated` (battle result) |
| B11 | The dock at night | `ch02/haluna` night | 21:30 | E | 2.0 | H10 | `haluna_night` | A promise made in the dark. Asha says yes before Toma can object. | `ch03_rhen_sworn_guardian` |
| B12 | Slice end card | black | — | C | 0.5 | — | `hush_first_verse` (piano coda) | *"I said yes to a girl I'd known for two days..."* | — |

**Totals:** critical path **39.5 min** (B01–B03, B05–B12). With the side scene and the side pool, **45 min**. That's inside SPEC §10.2's 30–45. Split: **24 min playable (61%)**, 10 min cutscene, 5.5 min in-engine. A slow player who reads every NPC lands near 50, which is fine; the slice should never *require* more than 40.

**Cut order if the slice runs long:** B02 folds into B03's opening (Neme's line becomes an NPC bark). B05 becomes a 3-line bark at the causeway gate. Then one of B06's three banters goes. **Never cut** B01, B08–B09, the Drownbell's Ilun phase, or B11.

---

## 2. Beat detail

### B01. Cutscene A, "The Girl on the Beach" (C, 4 min) — *scripted*
- **Open:** fade up on H05 (Rhen's eye-level in the shallows, dawn rim behind Asha). Rhen's older voice-over: *"The sea gave me back at dawn. Somebody was humming."* She's humming a **star-path**, a homecoming lullaby. That's the scene's quiet irony: she won't be coming home.
- **The required facial beat (H06):** she smiles first. Toma's spear comes into frame right. Rhen's first words are a joke ("That's a very big spear for a very small conversation."). Asha laughs, sees the brass lantern, and goes **still for half a beat** (`@face asha neutral 0.2`, `@wait 0.6`), then smiles again. *Why she goes still:* she saw this lantern on her mother's guardian when she was seven. She never says so. Cinematics: play it as recognition, not alarm.
- **Choice 1 (lantern):** "It was my father's" / "Good trade". Sets `ch02_rhen_named_lantern`, which changes the closing line and Cutscene B.
- **The grief turn:** Toma tells him the storm went east. Then, on H06, **held motes** (`glimmer_held`, cyan, drifting down and seaward) are in the water around Rhen. A lamp-diver knows what they are: *"Those are ours. Aren't they."* Asha heard them before dawn, which is the first hint that she is a hearer, given without explanation. Toma, gently: *"She woke the house before light. We came down so they would not come ashore alone."* The village keeps vigil for strangers' dead. That warmth is sincere, never a laugh, and it sets up the choice ([N-13](../decisions_log.md)).
- **Choice 2 (grief):** "Stay with them a minute" / "Don't look at them. Get up." Staying sets `ch02_rhen_stayed_with_dead`: Rhen sits in the water and names Mother Kell, and Toma says "Be level, Oruvel" by reflex. *Thematic note (do not surface):* staying is loving and it is also what anchors the dead. Pell will say so in Act II ("The diver's light is held. Gently. But held."). Neither choice is wrong. Getting up keeps him on his feet, leaning on Toma, for the rest of the scene: the closing H05 is taken at his standing eye-line, and Asha offers her hand only when he has stayed sitting in the water ([N-17](../decisions_log.md)).
- **Fragment 1 of "Cantor":** Toma starts "You are speaking to the Lady—" and Asha cuts him off with her name. Rhen: "Lady what?" Asha: "Later."
- **Close:** Asha's "Come up to the village" stays on H05, where her face reads. Then a **cut** to H01 (the whole beach from the sea, dawn grade) on the walk up. Every shot change in this scene is a cut, because the setups don't share an axis. Voice-over: *"She smiled first. Every time. It took me a long while to understand why."* `@letterbox off`, then the `zone_unlock haluna_village` event.

### B02. Neme's table (E, 1 min)
Rhen wakes at noon in Asha's aunt Neme's house, to far too much food. Neme talks to him the way she'd talk to a stray dog she's decided to keep, and never once looks at Asha's packed bag by the door (a camera insert). Two to four lines, ~40 words. **New speaker needed:** `neme`.

### B03. Haluna by day (P, 6 min)
The town loop: the lane (H02), the market (H09), the dock (H04), the chapel court (H07), the lintel-gulls (H03, a look-at prompt). **Systems on show:** the equipment shop, the inn, and the **first save shrine** (tutorial; `ch02_saved_once`).
**The four fragments** are overheard NPC barks, one per area, each triggered by walking past. Rhen hears all four and the player can piece them together. He doesn't.
1. Market: *"Two days. Two days, and she's still helping me wrap fish."*
2. Chapel court: a Reed sweeps the steps: *"The Lady Cantor's shell is cut. They'll set it at the wake."*
3. Dock: two fishers: *"Her mother went from this dock too. Same age near enough."*
4. Lane: a child singing a skipping rhyme that counts verses: *"one for the shell and two for the ash..."* (Audio: unaccompanied, diegetic).

Budget: ~140 words across all barks. NPC state changes after Ch3 (night variant): the barks become blessings for the guardian (`ch03_rhen_sworn_guardian`).

### B04. Side scene (optional): "Pila's Granddaughter" (E, 4 min) — see §4

### B05. Low tide (E, 1 min)
At the causeway head (C01), the tide is out. Toma: the Order's tide-readers set the day, and the causeway only opens this far twice a month. Asha asks Rhen to come "and see it. It's the most beautiful thing we have." Toma objects; Asha has already started walking. ~40 words.

### B06. Saltgrass Causeway (P, 7 min)
The first route, and the first stretch of pilgrimage (pillar 3). The camera rails favor C01, C02, and C06 so the path reads as a line leading away.
- **Encounters:** reef crabs, lantern-lure eels, and a palette-variant flier (C07) that teaches Rhen's niche: he is the answer to fliers (pillar 4). Music: `battle_standard`.
- **Three walking banters** (field barks, no letterbox, triggered by marker posts), ~90 words in total:
  1. *Marker posts (C04):* Rhen asks why one is broken. Toma says nobody fixes them, and doesn't say why.
  2. *Tidepool (C03):* Asha names every creature in the pool. Rhen, a diver, knows them all by what they sell for. Warmth, and the first time Asha teases him.
  3. *The Lit Age ring (C05):* Rhen clocks the faint teal glint (`glimmer_bound`) as salvage worth a month's food. Toma: "Leave it." Rhen leaves it. This is the slice's only sight of bound light outside the shrine.

### B07. Shell Shrine trial (P, 5 min, +1.5 optional)
Three rotating shell-basins redirect water until the inner pool fills and the chamber door floods open (S03 is the overview; S04 shows the water). **No dialogue during the puzzle** beyond one Toma hint bark after 90 s idle. **Optional:** drain the side pool to find the **net-float charm** (S05), which sets `ch03_found_net_float`. Cutscene B pays it off: Ilun's keepsake is a child's glass net-float.

### B08. Cutscene B, part 1: the steps (C, 3 min) — *scripted*
- **S07:** Asha walks into the chamber alone, by rite. "He's been in there a hundred and forty years. I think he'll be polite." Toma calls her Lady Cantor and she corrects him to her name. It's the second time the slice does this beat, now with Toma conceding it.
- **S08:** a single held frame of Ilun's chamber. Ilun is **bound light** (`glimmer_bound`: steady, never drifting, the same stillness as the Lit Age ring). Then fade.
- **S06:** Rhen and Toma on the outer steps, a gap of air between them. **The mandated exchange:** "Do you know what a Cantor is?" "...Someone who sings?" "Yes. Someone who sings."
- **Choice:** "And then she comes home?" (sets `ch03_rhen_asked_after`; Toma's non-answer: "No. It is not." That one is for the player, and it lands at the Ch4 wake) or "Seems like a lot of fuss for one song" (Toma's voice-guide line about mocking versus asking). Both end on **"Then ask her. Not me. She has earned the telling of it."**
- Toma on guarding her since she was nine (the net racks). If `ch02_rhen_stayed_with_dead`, Toma brings up the morning in the water: "Somebody should have." "Yes. I think so too."

### B09. Cutscene B, part 2: the first verse (C, 3 min) — *scripted*
- **S09, sunset:** Asha comes out with Ilun's light lifting off her skin in slow upward spirals (`glimmer_lift`, warm gold). **This is the first released light in the game.** Nobody names the rule. Rhen panics: "Is that normal? Toma, is that normal?"
- **Branches:** if `ch02_heard_pila`, Rhen asks whether it was Teyo ("He's still frightened. He was kind to me anyway."). If `ch03_found_net_float`, Rhen gives her the float ("He carries one just like it... I think he'd like it to stay with someone who goes home." Rhen misses what that means).
- **The rite:** the first verse is sung toward home first. The shrine faces west, toward Haluna and the sun.
- **The verse** (four `#sung #lamptongue` lines, `hush_first_verse`): *Vey ennu, vey ennu, / hal oan, ish karra. / Ennu re, ennu re... / ...mir.* Constructed from the bible's Lamptongue roots, roughly "water, sleep / shell-home, the light gathers / sleep again / stay." The translation is never shown. Like every verse, it ends on *mir* (stay).
- **S10, recognition:** he knows it from the first phrase, so the **cut** to S10 lands on the second sung line and holds through the rest of the verse and his question, at least 6 s, with Asha's voice over his face. The face is layered: surprise at 0.3 s, quick and light, then grief at 0.6 s settling under it. Never a full-weight "surprised", which reads as comic shock. Then "...where did you learn that?" before he can stop himself.
- **Choice:** "My father hummed that. Every night." (sets `ch03_rhen_named_lullaby`; "Every night until he didn't.") If he also named the lantern at dawn, Asha goes still again: "Your father. The one with the lantern." Then Asha: "My mother hummed it to me every night, and sang it from this door. I was seven. I'd forgotten it until he gave it back." A held look, then Rhen: "...He never said where he learned it." (It is a Velamir family lullaby, and Dace knew Imra years before she was named: [N-11](../decisions_log.md). Neither of them knows that yet.) Or he deflects ("Must have been the wind"), and she lets him, warmly: "That's twice you haven't answered me, Rhen Sallow. I'm patient." (or "Not today" if he did answer about the lantern).
- **The toll:** silence, then a bell tolls *under the water*. "The tide has turned." "Something heard that." Cut to C08 with the bell's hood breaking the surface, its wounds bleeding **held** cyan. Toma: "On my shield. Everyone, on my shield, now." The `start_battle drownbell` event follows.
- *Story logic:* Undertow-spawn reach for the living, and the Drownbell rises because the verse was sung. Beauty draws the danger.

### B10. Boss: the Drownbell (P, 6 min) — see §5

### B11. The dock at night (E, 2 min)
H10: oil lamps in windows, sea-glow at 0.12, stars. Rhen finds Asha on the dock (the dock of the game's last shot). He asks to come as a guardian. She says yes before Toma, arriving, can object. Toma's objection becomes a sigh and "Then you walk behind me." No talk of what the pilgrimage ends in. That's Ch4. Sets `ch03_rhen_sworn_guardian`. ~90 words. If `ch03_rhen_asked_after`, Rhen almost asks her, and Asha asks about *his* day first (her tell from the voice guide). He lets her.

### B12. Slice end card (C, 0.5 min)
Black. Rhen's voice-over (from act_outline): *"I said yes to a girl I'd known for two days. I didn't know yet what I was walking her toward."* `hush_first_verse` piano coda.

---

## 3. Flags

All are declared in `game/data/flags.tres`. Read and write them only through `Game.get_flag` / `Game.set_flag` (the dialogue runner does this through `GameFlagAccess`).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch02_met_asha` | B01 (end) | zone gating | — |
| `ch02_rhen_named_lantern` | B01 choice 1 | B01 close, B09 | Asha's second stillness; Ch6 (Liss clocks the lantern) |
| `ch02_rhen_stayed_with_dead` | B01 choice 2 | B08 | Pell, Act II ("held. Gently. But held.") |
| `ch02_saved_once` | B03, save shrine (gameplay) | tutorial gating | — |
| `ch02_heard_pila` | B04 | B09 | Ch20: Asha can tell Ilun that Pila lived to ninety-one |
| `ch03_found_net_float` | B07 pickup | B09 | the charm keeps its line of flavor text |
| `ch03_rhen_asked_after` | B08 choice | B11 | Ch4 wake: he asked, and nobody answered |
| `ch03_ilun_bound` | B09 | battle setup | Ilun summonable from B10 on |
| `ch03_rhen_named_lullaby` | B09 choice | Ch4, Ch17 | Dace's logs; Asha already knows the tune connects them |
| `ch03_first_verse_sung` | B09 (end) | sleeve state S1, Ch4 | verse-sleeve band 1 |
| `ch03_drownbell_defeated` | B10 battle result | B11 trigger | — |
| `ch03_rhen_sworn_guardian` | B11 | B03 night barks, Ch4 | — |

---

## 4. The optional side scene: "Pila's Granddaughter" (B04)

**Where:** the **wake-shell wall at the causeway head** (H08; the placement is confirmed in decisions_log.md). **When:** any time in B03 before B05, through an NPC marker on Grandmother Osu. **Length:** 4 min, ~150 words. **Speakers to add:** `osu`.

**Beats:**
1. Osu is cleaning the shells with a rag and a bowl of fresh water, the way you'd wash a face. Rhen offers to help, badly.
2. She shows him the newest gap in the wall, at shoulder height and clean-edged, waiting for Asha's shell at the wake. She doesn't explain the gap. He doesn't ask. (Fragment 5, for the attentive.)
3. She finds one old shell by touch: **Teyo Marrin**. Her grandmother Pila's big brother, who went as Cantor at sixteen so the Order would take him and not his sister, the stronger hearer. "He was frightened the whole way. Grandmother said he went anyway."
4. Pila lived to ninety-one, mended nets until the end, and "never once sang, not even to children, in case anyone was listening." Osu laughs at that, and her voice catches on it.
5. Osu: "You'll go up to the shrine with her? Say hello to him for us." Rhen, not understanding: "To who?" Osu just pats the shell.

**Rules:** no more than four lines from Osu in a row, broken by Rhen's help and his questions (§3.6). Osu's voice: plain, practical, and wry. A Low Reaches elder says "Salt and stone" and means it.
**Payoff:** sets `ch02_heard_pila`. In B09, Rhen can ask whether it was Teyo. In Ch20, Asha can answer Ilun's question ("Did Pila have a good life?"), and the first Vowbound release becomes *kindness repaid* (vowbound.md §1).

---

## 5. The Drownbell (B10): placement, phases, and what it teaches

**Placement:** directly after Cutscene B, on the causeway arena (the widened disc, C08) as the party crosses back at sunset with the tide coming in. It is the slice's climax, and it sits *after* the verse on purpose. The song draws it. The player has just seen the most beautiful thing in the slice, and it brings the danger.

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: the Toll** | The bell-hood stands in ankle-deep water at low light (C08). | Its **toll** pushes the whole party back on the timeline. The timeline preview shows the toll coming two turns out. **Breaking its rim** (Rhen's precise, low-delay strikes) silences it. | Read the timeline before you act, and use your fast striker to break a timed threat. Second lesson: Toma's shield covers the party while Rhen works. | Toma's "On my shield" is literal. |
| **2: the Flood** | The flood rig lifts the water from −0.7 to +0.6 m over 8 s (haluna.md §2.2). The bell submerges and **spawn-polyps** glow `spawn_wound` cyan below the surface (C09). | The polyps **heal** the bell every turn, faster than the party can kill them. **Summoning Ilun** (first use, full cinematic, C10) replaces the party and clears the water field with *Floodnet*. | The Vowbound mechanic: the party steps off the field and the summon takes the hits (SPEC §6.3). It is the slice's one Vowbound, and its first call is unmissable. | *"The dead stepping in front of the living."* Ilun puts himself between Asha and the dark, which is exactly what he does in his Ch20 release. |

**Tutorial text** (UI, loc keys owned by UI/Combat): one prompt per phase, no more. Phase 1: *"The Drownbell's toll is coming. Strike its rim to silence it."* Phase 2: *"The water is feeding it. Call on Ilun."* (Asha has the command from `ch03_ilun_bound`.)
**Battle barks** (≤ 35 words in total): Ilun's summon has no line. He's a frightened boy and he doesn't speak until Ch20. Asha's call is a single word, his name.
**Light:** every Drownbell VFX is **held** (cyan, sinking). Ilun's summon is **bound** (steady teal) until his Ch20 release. When the bell dies, its motes do *not* rise. They slide seaward. Quietly wrong (bible §2).

---

## 6. Music cues

The ids are the ones the `.dlg` files and the sequencer use (`@music <id>`). `silence` is a reserved id meaning "fade the music bed out" (a format request to Systems, §9).

| Cue id | Beats | Kind | Brief | M2 final? |
|---|---|---|---|---|
| `haluna_dawn` | B01 | Cutscene score | Solo piano and a low metallophone, very slow. It doesn't know yet whether it's sad. | sketch |
| `haluna_village` | B02, B03, B05 | Town bed, loop | Warm, gamelan-like percussion, a flute melody that never quite resolves. The festival is for a departure. | **final** |
| `saltgrass_causeway` | B06 | Field bed, loop | Wind, sparse plucked strings, open fifths, a walking pulse. | sketch |
| `battle_standard` | B06 | Battle loop | M1-AUD-02's standard battle. | sketch (M1-AUD-02) |
| `shell_shrine_interior` | B07, B08 | Temple ambience | Water drips tuned to a drone, a hummed congregation far off (the Order hums; bible §4). | sketch (M1-AUD-02 temple ambience) |
| `hush_first_verse` | B09, B12 | **Diegetic** Hush theme | The first diegetic statement of the Hush theme. A sung line (until SPEC §16 Q4/Q5 settle a voice, a vocalise-like solo instrument carries it) over a held drone, with the piano entering on *mir*. The B12 coda is piano alone. **Original melody** (SPEC §2): it is our Hush theme's first phrase. | **final** |
| `drownbell` | B10 | Boss, two stems | Stem 1 (phase 1) is built around a pitched bell toll on the downbeat. Stem 2 (phase 2) adds low strings and a rising-water swell. | **final** |
| `ilun_summon` | B10 | Sting (≤ 6 s) | Glass and water, the first phrase of the Hush, very high. | sketch |
| `haluna_night` | B11 | Night bed | `haluna_village` stripped back to flute and a drone, slower. | sketch |

**SFX cues referenced by the scripts** (`@sfx`, requested): `drownbell_toll` (heard first from under the water, far away).
**Recommendation to the Lead and Audio:** M2's "three final music cues" should be **`hush_first_verse`, `haluna_village`, and `drownbell`**: the theme, the place, and the climax. M1-AUD-02's three (Hush theme, standard battle, temple ambience) are the right *prototypes*, so only the slice's finals differ.

---

## 7. Camera shots by beat

The shot ids are those of [haluna.md §5](../../art/environments/haluna.md) and are used verbatim in `@camera`. The test asserts that every `@camera` in both scenes is one of them.

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | H05 → H06 → H05 → H06 → H05 → H01 | **All cuts** (`blend=0.0`): the setups don't share an axis. H06 carries the facial beat *and* the held motes around Rhen. Asha's closing line (014/015) stays on H05, and the cut to H01 lands on the walk. H01 runs under the `ch02` dawn grade (`grade=ch02` kwarg), not noon. |
| B03 | H02, H03, H04, H07, H09 | Rail cameras. H03 is a look-at point (the lintel-gull). |
| B04 | H08 | One locked shot plus inserts on Osu's hand. Shallow depth of field, as specified. |
| B05 | C01 | — |
| B06 | C01, C02, C03, C04, C05, C06, C07 | C02 is the default rail. The banters fire on C04, C03, and C05. |
| B07 | S01, S02, S03, S04, S05 | S03 is the puzzle overview, toggled by the player. |
| B08 | S07 → S08 → S06 | S07 → S08 cuts on a short fade, never a blend through the sinking door. S08 is a single held frame. Don't show Ilun's face (save it for C10). |
| B09 | S09 → S10 → S09 → S10 → S09 → C08 | **All cuts** (shot/reverse-shot across the axis). The second S10 starts on sung line 043 and holds through 046 (≥ 6 s of `@wait`, checked by the test). Cut to C08 on the second toll. |
| B10 | C08, C09, C10 | C10 is Ilun's summon cinematic. |
| B11 | H10 | — |

**Requested additional coverage** (Art and Cinematics, not used in the scripts yet): `H11`, an Asha close-up at 85 mm for B11's yes, and `S11`, a two-shot of Asha and Rhen in the doorway for the B09 choice, if S09/S10 alone feel like ping-pong in review.

---

## 8. Word counts

Generated by `python3 tools/dialogue_stats.py` (it counts every branch's words once, and options separately). "Per path" figures come from walking every branch and input combination, the same sweep the test runs.

| Scene | Lines | Words written | Words a player reads (one path) |
|---|---|---|---|
| `ch02_girl_on_the_beach` | 35 | 328 | 261–266 (mean 263) |
| `ch03_the_first_verse` | 60 | 424 | 266–368 (mean 316) |
| **Both cutscenes** | 95 | **752** | ~579 |

*(M1-NAR-05: +5 words on the beach from line 021, and +12 on the told path of the verse from lines 053 and 054. The rest of the slice's budget is unchanged.)*

**Per speaker** (both scenes): Asha 289 (38%), Toma 221 (29%), Rhen 156 (21%), player options 50 (7%), narration 36 (5%). Rhen reads light on purpose because he jokes in short bursts, and his options and voice-overs add another ~86 words.

**Against SPEC §3.6** (40–60k words, ceiling 80k): at 40 min of a 30 h main story, the slice is **2.22%** of the game, so its fair share is **889–1,333 words**. The rest of the slice is budgeted at: B02 40, B03 140, B04 150, B05 40, B06 90, B07 15, B10 35, B11 90, B12 25 = **625**, for a slice total of **~1,360 words written**, or ~1,050 on a typical path without the side scene.
- Projected to the full game at the slice's density: **~61k words**, just over the 60k target and well under the 80k ceiling. That's right for the opening chapters, which carry every introduction. Later dungeon chapters should run thinner.
- **Rule for the rest of the slice:** hold B03 and B06 at or under their budgets. `tools/dialogue_stats.py` flags any line over 25 words (none today).

---

## 9. Requests to other roles

- **Art (haluna.md / color_script.md):**
  1. Color script `ch02` says "glimmer: none on screen". Cutscene A needs **9 held motes** in the shallows around Rhen in H06 only (`glimmer_held`, energy ~0.6, under 1% of the frame). Please amend.
  2. `ch03_boss` is timed at 17:30, but the Drownbell comes *after* Cutscene B (18:05). Please re-time it to **~18:15** (sun at about 2°, afterglow), which also helps phase 2's cyan polyps read against dark water. If the gold must stay, compress Cutscene B's time instead and tell Narrative.
  3. Answers to your four open questions are in [decisions_log.md](../decisions_log.md).
- **Cinematics (reviewer):** check the S10 hold, the H06 facial beat, and Ilun's single frame in S08. *(M1-NAR-05: the review-sweep-B camera fixes are applied: all cuts, 014/015 on H05, and S10 from 043 held ≥ 6 s with a layered face. See [N-13](../decisions_log.md).)* Actor marks and anim clip names in the scripts (`kneel_over_rhen`, `sit_in_shallows`, `threshold_west`, `drownbell_arena`...) are proposals. Rename them freely in the `.dlg`.
- **Audio:** the cue list in §6, especially `hush_first_verse` as a sung line.
- **Combat:** the Drownbell spec in §5 (the timeline-preview toll and the polyp heal), plus `ch03_ilun_bound` as the summon gate.
- **Systems:** the format requests in the M1-NAR-02 task notes. New speakers for M2: `neme`, `osu`, and a generic `villager` (name keys `CHAR_NEME`, `CHAR_OSU`, `CHAR_VILLAGER`), to be added when those scenes are scripted.
