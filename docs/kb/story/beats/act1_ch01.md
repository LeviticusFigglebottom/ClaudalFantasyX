# Ch1 Beat Sheet: "Lamp-Diver" at Oruvel (M3)

Owner: Narrative (M3-C01-01). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Prologue and Ch1](act_outline.md), [the slice sheet](vertical_slice.md) (the format, and what Ch2–3 already teach), [bible §2, §5.1, §7, §9](../bible.md), [voice guide](../voice_guide.md), [Rhen](../characters/rhen_sallow.md), [ADR 0017](../../decisions/0017-act-one-restaging.md) (the Ch1 rows and the watch), [ADR 0020](../../decisions/0020-kerrid-restaging.md), [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (the sweep-H wick and lantern notes), [color script `ch01`](../../art/color_script.md), [underwater look](../../tech/underwater.md) (M2-RND-02), [Undertow preset `ch01_arrival`](../../tech/undertow.md), [first-playable flow](../../tech/first_playable_flow.md), [decisions_log N-02, N-25, N-26](../decisions_log.md).

Scripts (to be written in M3-C01-02, under `game/data/dialogue/ch01/`): `ch01_the_drop`, `ch01_bell_room`, `ch01_low_lights`, `ch01_scale_hull`, the town barks, `ch01_kell_stall` (the wick and the side scene in one file, with the stay branch), `ch01_gulls`, `ch01_the_rising`, `ch01_hullgnaw_rises`, `ch01_going_under`.

Beat ids are chapter-local: **C1-01** to **C1-15**. Elsewhere, cite them as "Ch1 C1-08".

---

## 0. The chapter in one paragraph

A nineteen-year-old salvage diver walks the floors of a drowned tower by lamplight, cuts out a brass wheel, and comes up into the brightest noon in the game to sell it for less than it's worth. The raft-town he lives on is poor, loud and fond of him. Mother Kell, the chandler who took him in when nobody else did, presses a wick into his hand for luck, the way she does for every diver going down. He never makes that second dive. The carved gulls on every roof cry at once, the sky stays clear, and the Undertow stands up out of the sea. He fights a spawn that has grown through a dead ship's ribs on a raft that is coming apart under him, and then the water takes everything. In the dark, with his town's light sinking all around him, he hears his father singing the currents. Then nothing. The player should finish Ch1 having **liked a place and lost it in an afternoon**, and with one song in their ear that they will hear again.

**Emotional line:** calm, competent solitude (the dive) → noise and warmth (the raft-town) → a small kindness he doesn't notice (the wick) → wrongness in a clear sky (the gulls) → panic held together by habit (the run) → a fight he can't win the war of (Hullgnaw) → silence and a song (going under).

**What Ch1 must prove:**
- the underwater look (M2-RND-02) as a playable dungeon, with the oil lantern as the light, and the light grammar's first lesson: **cyan light that sinks is wrong** (color script `ch01`);
- Rhen's voice before grief, so that Ch2's jokes on the beach read as a man holding himself together;
- a community worth the loss (pillar 2: gorgeous *and* doomed);
- the turn-order timeline, taught by Hullgnaw, cleanly enough that the Drownbell's toll in Ch3 can build on it (pillar 4);
- a clean hand-off from the Prologue and into Ch2's Cutscene A, with nothing in Ch2 changed.

---

## 1. Running order

Time is in-world: one morning, Day 0 (Ch2's beach is Day 1). Minutes are the player's, at a first-time pace. **P** = playable, **C** = letterboxed cutscene (`.dlg`, sequencer-driven), **E** = in-engine scene (no letterbox; `.dlg` without `@letterbox`).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| C1-01 | Title card: *One month earlier* | black | — | C | 0.3 | — | `silence` → `oruvel_underway` | The Prologue's vigil gives way to the boy before the man. | `ch01_started` |
| C1-02 | **The drop** | `ch01/oruvel_underway` crown | 08:40 | P | 2.0 | U01, U02 | `oruvel_underway` | Calm and competent. He is good at this, and he is alone down here. | — |
| C1-03 | The first bell-room | Underway, bell-room 1 | 08:45 | E | 1.0 | U03 | (ambience) | Rhen's voice, talking to nobody. | — |
| C1-04 | **The lamp galleries** | Underway, galleries | 08:50 | P | 4.0 | U04, U05 | `oruvel_underway`, `battle_underway` | Beauty in a dead place. Light draws things to it. | `ch01_found_old_tin` (optional) |
| C1-05 | The low lights | Underway, the stairwell lip | 09:10 | E | 1.5 | U06 | `oruvel_underway` (thinned) | The first held light. A rule he was taught and doesn't understand. | — |
| C1-06 | **The gauge-wheel** | Underway, gauge room and shaft | 09:15 | P | 3.0 | U07, U08 | `oruvel_underway`, `battle_underway`, `rhen_current_hum` | The job. Then the ride up a current, humming his father's chart. | `ch01_cut_gauge_wheel` |
| C1-07 | Surfacing | Underway → `ch01/oruvel` | 09:55 | E | 0.5 | U09 → O01 | `oruvel_raft` (up from under) | From the dark into the brightest frame so far. | `ch01_underway_done` |
| C1-08 | The scale-hull | `ch01/oruvel` scale-hull | 10:05 | E | 2.0 | O02 | `oruvel_raft` | His voice: patter, a bad bargain, the Order's stamp on everything. | — |
| C1-09 | **Oruvel by day** | `ch01/oruvel` | 10:15 | P | 6.0 | O03–O08 | `oruvel_raft` | A town that is noisy, poor and his. Every bark is someone about to drown. | — |
| C1-10 | **Kell's stall: the wick** (critical), with the optional side scene *"The Sea Owes Me a Favour"* | `ch01/oruvel` second mooring | 10:55 | E | 0.5 (+3.0) | O09 | `oruvel_raft` → none (ambience) | A trade habit, given to every diver. He pockets it without looking. | `ch01_has_kell_wick`, `ch01_kell_side_scene` (optional) |
| C1-11 | The lintel-gulls | `ch01/oruvel` dive mooring | 11:05 | E | 1.0 | O10 | `silence` | Every carved gull on every roof cries, and the sky is clear. | `ch01_gulls_cried` |
| C1-12 | **Cutscene: the Rising** | `ch01/oruvel` | 11:10 | C | 2.0 | O11, O12, O13 | `undertow_rising` | The storm stands up out of a blue sky. The town's drill starts. | — |
| C1-13 | **The breaking raft** | `ch01/oruvel` storm variant | 11:15 | P | 3.0 | O14, O15 | `undertow_rising` (stem 2), `battle_standard` | Habit holding panic together. Kell sends him the other way. | `ch01_ran_for_kell` (choice) |
| C1-14 | **Boss: Hullgnaw** (two phases) | `ch01/oruvel` storm variant, the net-pen hull | 11:20 | P | 6.0 | O16, O17 | `hullgnaw` (2 stems) | He wins the fight and loses the town. | `ch01_hullgnaw_defeated` (battle result) |
| C1-15 | **Cutscene: Going under** | `ch01/oruvel` → open water, underwater | 11:28 | C | 2.0 | O18, U10, U11 | `going_under` → `silence` | His town's light sinking around him. His father's current-song, far down. Then nothing. | `ch01_went_under` |

**Hand-off:** C1-15 ends on black and silence. After a 3 s hold, Ch2's Cutscene A fades in on its first line, *"The sea gave me back at dawn. Somebody was humming."* (`ch02_beach_001`). Song to song: Ch1 ends on Dace's current-song under the water, and Ch2 opens on Asha humming a star-path in the shallows, the current-song's Low Reaches cousin (bible §7). **No Ch2 line or cue changes.**

**Totals:** critical path **35.1 min** (every beat but the side scene's extra 3.0). With the side scene and the optional tin, **~39 min**. Split: **24 min playable (68%)**, 4.3 min cutscene, 6.8 min in-engine. That's more playable than the slice (61%), which is right for a tutorial chapter with one main speaker.

**Cut order if Ch1 runs long:** C1-03 folds into C1-02 (its two lines become barks on the drop). C1-08's haggle loses its choice and becomes a bark. C1-09 drops to four barks from six. **Never cut** C1-05 (the first held light), C1-10's wick (it lights the post-credits lamp, act3_ending E7, which is never cut), C1-11, Hullgnaw's timeline lesson, or C1-15.

---

## 2. Beat detail

### C1-01. Title card: *One month earlier* (C, 0.3 min)
The Prologue's last frame (glimmer rising round Rhen at the vigil) cuts to black. A plain card, centred, one loc key (`CH01_TITLE_CARD`): *One month earlier.* No chapter name on the card; the chapter's name appears on the pause menu only, as the slice does. Then black, the sound of a tether running through a block, and the fade up underwater. `Game.set_chapter(1)` runs at the card, so ADR 0018's chapter autosave is the save that a player who quits in Ch1 comes back to.
- **Flow request (Systems, M3-ARC-01):** the Prologue's `hand_off()` goes to `ch01/oruvel_underway` spawn `Drop`, not `ch02/haluna` `Beach` (first_playable_flow.md). It's one data value in the chapter flow. Ch1's own exit then goes to `ch02/haluna` `Beach` with Cutscene A, which is today's Prologue target, so nothing in Ch2 moves.
- *Open question, noted for the Lead:* the outline's card says "one month earlier", and the Prologue is Iskarra in Ch19. Ch1 to Ch4 alone take four days. The card stays as the outline writes it; if the M3 travel calendar can't fit Ch5–Ch19 in a month, the card should change, not the Prologue (§9, Narrative).

### C1-02. The drop (P, 2 min)
Fade up on U01: Rhen hanging on his tether in the crown of a drowned Lit Age tower, the hulls of Oruvel a dark lattice on the bright surface 6 m above, god rays slanting down through the gaps (`lagoon_clear` ×2.0, the underwater rig at full). His lantern is lit on his shoulder (`oil_lamp`, N-02).
- **How a lamp-diver moves** (a design call, §9 Design): Oruvel's divers go down **weighted**, so they walk the drowned floors. They don't swim. The field controller is the ordinary one with the underwater look on top; vertical moves are **tether points** (climb or drop, an interact). There is **no breath meter**. The tower's upper floors hold trapped air in **bell-rooms**, and the route runs from one to the next, so the fiction covers breathing and the player never races a timer (pillar 4, SPEC §6.1's "no real-time pressure" carried into the field).
- **Teaches:** movement on the rail camera, if the Prologue's walk hasn't (the outline's Prologue walk is the controls tutorial, but today's placeholder has no player; until it ships, the movement prompt lives here, and it is keyed by a seen-flag so it shows once whichever comes first). Then **tether points** (interact to drop to the next floor).
- No lines. One VO line from the older Rhen as he unclips: *"Oruvel sat on top of a drowned city. Most mornings I went down to take some of it home."* (~17 words)

### C1-03. The first bell-room (E, 1 min)
He climbs up through a still mirror of water (the air surface seen from below, `water_underside`) into a room of trapped air, and the sound changes: drips, his breathing, the lantern's hiss. This is the only place underwater where he speaks out loud. He talks to the room, to the lantern and to nobody, which is how a lonely, funny person talks.
- Sample (voice): *"Morning. Don't get up."* … *"Brass in the door hinges. Somebody in the Lit Age loved a hinge."*
- **Teaches: interact.** He cuts the first brass hinge with his reef-hooks (a salvage prop with a cut state; the item is `lit_age_brass`).
- The bell-room is a **rest point**: full heal on entry, no save (§9 Design: Ch2's shrine stays the game's first save, as `ch02_saved_once` teaches).
- ~45 words.

### C1-04. The lamp galleries (P, 4 min)
A long gallery of dead **lamp-columns**: white Lit Age ceramic gone green with coral, their housings empty and dark for four hundred years. Light comes only from his lantern and from the shafts above. It is beautiful and dead (pillar 2).
- **Teaches: the lantern** (the chapter's own mechanic, §9 Design for the numbers). The lantern has a **shutter**: narrow by default, or open with a held button.
  - *Open* widens the light. It shows salvage glints and side ways behind coral curtains, and it **draws wickfry**, the glass-shrimp shoals that swarm to lamplight (the danger meter climbs faster, with a visible ambience cue, SPEC §6.6).
  - *Narrow* is quiet, and the gallery stays half-seen.
  - It is a choice between seeing and being seen, with no fuel to manage. Prompt (loc key, UI): *"Hold to open the shutter. The more you light, the more you see, and the more that sees you."*
- **Encounter 1, scripted (`wickfry` ×1, one shoal fought as one combatant, solo Rhen).** **Teaches: the command menu and targeting.** One prompt only. The shoal is fast and frail, so it acts often, and the player *sees* who acts next on the timeline without being told yet; the prompt that names the timeline is Hullgnaw's (§5).
- **Random encounters** start here: `wickfry`, and `tower_limpet` (§9 Creatures), a slow wall on the route that delays. A limpet fight can be **skipped** (walked round, or fled), and when it is fought the timeline shows how long it will take. Rhen alone answers both: the shoal by speed, the limpet by patience or by leaving.
- **Hidden reward (optional):** behind a coral curtain that only the open shutter shows, an **old diver's tin** wedged in a column (two Salt Tonic and one accessory, §9 Design). Sets `ch01_found_old_tin`. No dialogue; the tin has a name scratched on the lid that's too worn to read.

### C1-05. The low lights (E, 1.5 min)
The gallery ends at a **stairwell** that goes down into the dark. Here the player sees the first glimmer in the game after the Prologue: **held** motes (`glimmer_held`, cyan, energy 1.5 per the color script), drifting sideways and **down** the stairwell, sinking past the lantern's reach. The stair is barred by a diver's knotted cord tied across it, a hundred knots, some new.
- Rhen stops. He doesn't go near them. He touches the cord. Sample: *"Nobody goes below the ninth floor. You don't follow the low lights."* Older-Rhen VO, once: *"Every diver in Oruvel was taught that. Nobody ever told us why."* (~30 words in total)
- *What this sets up:* the light grammar's first lesson, given wordlessly. This sinking cyan is the same light Asha's village keeps vigil for on the Ch2 beach, the same light that bleeds from the Drownbell, and the opposite of the gold that lifts off Asha at sunset in Ch3. **No bound light appears in Ch1** (teal, still). The slice keeps the first sight of it for the causeway ring (Ch3 B06) and the shrine.
- **Watch:** Rhen is never drawn toward the low lights, and nothing calls him. Ch1's only pull from the deep is the song in C1-15, and even that doesn't move him.

### C1-06. The gauge-wheel (P, 3 min)
The job: a Lit Age **tide-gauge**, a brass wheel two metres across in a sealed room off the stair, its teeth worth a month's oil.
- **Encounter 2, scripted: `oil_slug`** (§9 Creatures), a slug that lives on the lamp oil divers spill in the gauge room. It **eats light**: its cast dims Rhen's lantern (Darkness), and the field lantern dims with it for the fight's length, which is the chapter's mechanic turned against him. **Teaches: items.** One prompt points him to Items when he is first blinded (`brine_eyewash`), and a second use (`salt_tonic`) needs no prompt. It is weak to fire, which nobody in Ch1 has: the weakness is shown in the bestiary and pays off when `oil_slug` returns with Ysolde in the party (Ch4 onward). It drops `lit_age_brass` from the pipework it clings to, so the player learns that salvage and fighting overlap down here.
- He cuts the wheel's rim free (an interact with a short cut animation; it goes into the bag as a key item, `gauge_wheel_brass`, sold in C1-08). Sets `ch01_cut_gauge_wheel`.
- **The way up is a current**, a vertical shaft where the tower breathes with the tide. Rhen clips on and lets it take him. As he rides it, he **hums under his breath**, once through: the **current-song** his father taught him for reading water (`rhen_current_hum`). It is a working tune, a chart, not a lullaby, and **not** the Hush. This is the motif the player must recognise in C1-15, and again at Corrow (Ch8) and in act3_ending E2's `goodbye_dace`.
- **Teaches: escape**, in the shaft's one random encounter roll, if it fires: one prompt, *"A fight the story doesn't need can be fled."* If it doesn't fire, the escape prompt waits for the next non-scripted fight.

### C1-07. Surfacing (E, 0.5 min)
U09: up through the Snell window, the hull shadows rushing toward the lens, and then the break into noon on O01: the raft-town from the water at his eye level, hulls in every colour the sun has faded, laundry, gulls (living ones), children diving off a roof. **The brightest frame in the game so far** (color script `ch01`, exposure 0.65, saturation ×1.12). The music comes up from under the water into the open: `oruvel_raft`. Sets `ch01_underway_done`.

### C1-08. The scale-hull (E, 2 min)
Rhen sells the wheel to the **scale-man**, an Order-licensed dealer who weighs plain brass by the pound and stamps a chit for each lot: *Unbound, by the Level.* This is the Order's only presence in Oruvel, a stamp and a scale, and that is enough to show its reach.
- Rhen's patter, which the voice guide calls his haggling voice. He jokes harder when he is losing.
- **Choice (expression only, no flag):** "Haggle him up" / "Take his price". Haggling wins a few lume and costs a line where the scale-man says Rhen's father would have taken the first price. **Watch (ADR 0022):** the line is about a quiet man who didn't argue. It says nothing about where he went or why, and nothing about Kell or the lantern. Design sets the lume (§9).
- Sample: *"It's not scrap, it's history. History's heavier. Check your scale."* / *"Unbound, by the Level. You'd stamp the sea if it held still long enough."*
- ~120 words. **New speaker:** `scaleman` (`CHAR_SCALEMAN`).

### C1-09. Oruvel by day (P, 6 min)
The town loop across lashed hulls and plank bridges: the scale-hull, the cookboats, the net lanes, the empty Reefball pen, the outer mooring, the keel-hull (the oldest and biggest hull, where the town meets), and Kell's chandlery on the second mooring (C1-10). **Systems on show:** a shop (the cookboat's food and the net lane's gear) and the Lattice's first use, if Design puts it here (§9). **No inn and no save shrine:** Haluna's are the game's first (Ch2 B03), and Ch1 doesn't duplicate them.

**Six barks** (field barks, walk-past), each one a person the player will have watched drown. They are written warm, never as foreshadowing (pillar 1):
1. *Cookboat:* a cook who feeds Rhen on credit and keeps the tally in knots. *"That's nine knots, diver. I'm running out of rope."*
2. *Net lanes:* two net-menders arguing about whether the weather is too good. Nobody takes it seriously.
3. *Roof:* children diving off a cabin roof and daring Rhen to (a look-at; he declines with dignity, then does it, a short canned animation, if the player presses interact twice).
4. *The Reefball pen:* the practice net is empty, because **Oruvel's side went to Tamsule** a week ago. A girl practises alone and says the side's going to win the Tidecup this year. *(Seeds Ch7: the side is waiting at Tamsule, and Tavi is its captain.)*
5. *The outer mooring:* the **Seventh Terrace**, a red-lacquered Pemakar copper coaster, loading salvage. Its skipper, **Sadi Moru**, bought a lamp-housing off Rhen and paid short; they argue amiably. The camera holds once on the carved **name-board** on her stern (an insert, O07). *(Seeds Ch4: this is the derelict. See act1_ch04.md C4-11.)*
6. *The keel-hull:* an old diver, **Sabe**, sitting under the hull's carved lintel-gull, says the gulls have been quiet all morning, which they always are. It's a plain observation, not an omen. She gets it slightly wrong on purpose (the line is about the wind, which is what C1-11 pays off).

Budget: ~170 words. **New speakers:** `cook`, `sabe`, `skipper_sadi`; the menders and the girl reuse `netmender` and `child`.

**Watches:**
- **Kerrid is not at Oruvel** (ADR 0017's Ch1 watch). No stranger, no figure on a far hull, nobody watching Rhen.
- No bark mentions Dace by name. Oruvel thinks Dace drowned; nobody brings it up on a good morning.

### C1-10. Kell's stall: the wick, and *"The Sea Owes Me a Favour"* (E, 0.5 critical, +3.0 optional) — see §4
On his way to the dive mooring for the second dive of the day, Rhen passes **Mother Kell**'s chandlery stall, as every diver does. Every path plays the short version: she calls him over, presses a fresh wick from her own spool into his hand, *"For luck,"* and he pockets it in his tin without looking, the way every diver does. Sets `ch01_has_kell_wick` and gives the key item `kell_wick`. The optional side scene is staying to talk (§4).

**Why the wick is on the critical path (a decision, §9 Narrative):** the outline names the wick as Ch1's side scene, but act3_ending's E7 lights the post-credits lamp with it, and E7 is never cut. A wick that some players never received can't light it. So the **gift** is on every path, because it's her trade habit and every diver gets one on the way down, and the **side scene** is the optional time spent at her stall. That keeps ADR 0022's terms exactly: her own stock, given to every diver, with nothing said about Dace.

### C1-11. The lintel-gulls (E, 1 min)
At the dive mooring, Rhen clips on for the second dive and the **wind turns**. It comes from the sea, against the trade wind, which it never does (bible §9: the Undertow moves against the wind). Every carved **lintel-gull** on every ridge in Oruvel faces the sea, and their carved throats are hollow, so a wind off the sea goes *through* them. For the first time in eleven years, every roof in the town cries at once (SFX `lintel_gull_cry`, many voices, unpitched and awful, built from wind and wood).
- **The sky is clear.** O10: Rhen on the mooring, looking up at the nearest gull, sun high, not a cloud. Then everyone in the frame stops what they're doing.
- Rhen, quietly: *"...That's the gulls."* Sabe, from the keel-hull, much louder: *"Lines in! Everybody off the low hulls!"* (~15 words)
- The `rhen_current_hum`/`oruvel_raft` bed **cuts to silence** on the first cry, and stays silent until the wall appears.
- *This pays forward:* Ch2's lintel-gull look (`ch02_look_lintel_gull_001`, "Nobody carves a gull to watch the land") now lands as something he learned the hard way the day before. No Ch2 change is needed.

### C1-12. Cutscene: the Rising (C, 2 min)
- **O11:** the far horizon, under a clear blue sky. The sea draws back off the outer reef (the shallows go pale, towers' crowns show for the first time in years). Then the Undertow **stands up out of the sea**: a wall of dark water and cloud kilometres wide, lit from within by cyan wounds, rising into a sky that stays blue above it. Rendering preset `ch01_arrival` ("far off"), then a closer preset (§9 Rendering). The grade crosses from `lut_ch01_raft` to `lut_ch01_storm` over 4 s (color script).
- **O12:** the town's drill, as old as the town: low hulls cut loose, everyone to the **keel-hull**, children first. It is practiced and it is fast, and it's frightening *because* it's practiced. Kell is on her stall's roof, lighting the big chandler's beacon lamp so the divers in the water can find the keel-hull. That's her job in the drill.
- **O13:** the *Seventh Terrace* casting off and running for open water under full sail, the sailor's rule (sea room beats a mooring). It's the last time anyone sees her crewed.
- Rhen's lines are few and short (voice guide: a sudden short line when it matters). No VO.
- ~60 words.

### C1-13. The breaking raft (P, 3 min)
Rhen has to get from the dive mooring across the outer hulls to the keel-hull while the drill happens round him and the first swell lifts the raft. **There is no timer** (pillar 4). The storm advances by the player's progress, on scripted triggers, so a slow player sees the same sequence as a fast one.
- **Choice at the start (sets `ch01_ran_for_kell` or not):** Kell, on her roof, sees him and points away from herself: *"Not me, you fool! The net-pen! The little ones!"* The options are **"Go to the net-pen."** and **"Kell first."**
  - **Net-pen:** he does as he's told; the run goes by the Reefball pen, where the girl from C1-09 and two smaller children are clinging to the netting. He gets them onto a plank bridge toward the keel-hull (interact prompts).
  - **Kell first:** he runs for her stall; the bridge to the second mooring goes as he reaches it, and she's out of reach across open water, still shouting the same thing. He turns back to the net-pen anyway. Both paths end at the net-pen hull, and nobody is saved or lost by the choice; it says only who Rhen is (Ch7 pays it off with Tavi, §3).
- **Encounter, scripted: Scuttlers ×2** (§9 Creatures), the first **Undertow-spawn** the player sees, coming up over the hull edges ahead of the storm. Their wounds bleed held cyan, as every spawn's do. It's a short fight that shows the spawn's visual language before the boss. `battle_standard`.
- **Interacts:** cut two lashings so a low hull drifts clear (re-uses the C1-03 salvage cut).
- ~60 words of barks across the run.

### C1-14. Boss: Hullgnaw (P, 6 min) — see §5

### C1-15. Cutscene: Going under (C, 2 min)
- **O18:** Hullgnaw's last coil slides off the broken net-pen, and the children are on the bridge to the keel-hull. Rhen looks up, and the wall is **here**: it fills the frame, and the sky is still blue above it. Across the water, on the keel-hull, Kell's beacon lamp is **still lit**. The water comes over the frame before it goes out. **He never sees her go under, and neither does the player.** (Ch2's "Mother Kell *can't* swim", in the present tense, depends on this.)
- **U10:** under. The underwater look in the storm: no god rays, churned dark, and **all round him, lamps going out above and their light coming down**: held motes (`glimmer_held`) appearing in the water and sinking past him, dozens, then hundreds, sideways and down. His town's dead. He doesn't understand what he's seeing, and the camera doesn't explain it. His lantern is still burning on his shoulder (`oil_lamp`, the only warm light in the frame).
- **U11:** deep in the dark, far below him, a man's voice **singing the current-song** from C1-06, the whole phrase he only hummed. Rhen stops fighting the water. He listens. That's all. No figure, no face, no hand, no light coming toward him. The song isn't leading him anywhere. Then the lantern goes out of frame, and there's black.
- Older-Rhen VO, over black, plain: *"My father used to sing the currents. I hadn't heard it in eleven years. Then nothing."* (~16 words) `@music silence`. Sets `ch01_went_under`. Hold black 3 s → Ch2 Cutscene A.
- **Watches (ADR 0017, ADR 0022, act3_ending §0 rule 8):**
  - no figure guides Rhen into the storm or out of it, and nothing carries him through time or space: he is taken by the sea and given back one night later, one island west (`ch02_beach_012`/`013`);
  - the song is heard, never seen; Dace's voice is heard **only** here and in E2, and here it sings no words of Lamptongue and none to Rhen;
  - the current-song is **not** the Hush lullaby. Rhen recognises the lullaby in Ch3, and the two must never be mixed up by a cue;
  - the motes **sink** (held). Nothing lifts in Ch1.

---

## 3. Flags

All are to be declared in `game/data/flags.tres` (M3-C01-02). Read and write them only through `Game.get_flag` / `Game.set_flag` (the dialogue runner does this through `GameFlagAccess`).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch01_started` | C1-01 | chapter flow, autosave | — |
| `ch01_found_old_tin` | C1-04 optional cache | chest state | flavour only |
| `ch01_cut_gauge_wheel` | C1-06 | C1-08 trigger | — |
| `ch01_underway_done` | C1-07 | zone gating (the dive mooring's tether stays shut after it) | — |
| `ch01_has_kell_wick` | C1-10 (every path) | inventory (`kell_wick`, a key item that can't be used or sold); Ch7 | **E7**, the post-credits lamp. **Ch7** (proposal for the Ch7 sheet): Rhen can show Tavi the wick, "Same as every diver." |
| `ch01_kell_side_scene` | C1-10 optional stay branch | Ch2 B01 (no change: the "favour" line plays either way), Ch7 | Ch7: in Tavi's side scene at the empty moorings, Rhen can give him Kell's own line, "The sea owes me a favour." |
| `ch01_gulls_cried` | C1-11 | zone state (storm variant from here) | — |
| `ch01_ran_for_kell` | C1-13 choice | Ch7 | Ch7: when Rhen tells Tavi, he says either "I was running to her stall when the bridge went" or "She sent me to the net-pen. She was shouting at me." |
| `ch01_hullgnaw_defeated` | C1-14 battle result | C1-15 trigger | bestiary |
| `ch01_went_under` | C1-15 | chapter flow: the exit to `ch02/haluna` `Beach` | — |

Reads from earlier chapters: `prologue_seen` (set by the Prologue today). Nothing else. Ch1 reads no slice flag and sets none, so the slice still plays from a Ch2 start.

---

## 4. The optional side scene: "The Sea Owes Me a Favour" (C1-10)

**Where:** Kell's chandlery stall on Oruvel's **second mooring**: a cabin hull under an awning, lamp racks, oil jars, spools of wick, and the shelf where passing traders leave the raft-town's post (just a shelf; no letter is shown or mentioned). **When:** C1-10, before C1-11. The wick handover plays on every path; the side scene is the **"Stay a minute."** option that follows it (the alternative is **"Tide's turning, Kell."**, which goes straight to C1-11). **Length:** 3 min, ~170 words. **Speakers to add:** `kell` (`CHAR_KELL`).

**Beats:**
1. Kell is trimming wicks for the afternoon divers, the way she has every day for forty years. She never looks up from her hands. She can't swim and never learned; she has sold the sea's divers their light all her life from a hull she won't step off.
2. Rhen helps, badly. She takes the scissors back off him. *(He has been doing this since he was eight: she taught him to haggle on this stall, and he's still worse at wicks than she is.)*
3. He asks why she never learned to swim. She says the sea owes her a favour and she's never once collected, so it can't take her while it's in debt. She's joking, and she half means it. **This is the line Rhen repeats on Ch2's beach** (`ch02_beach_023`, "Said the sea owed her a favour"), so a player who stayed hears it twice: once from her and once from him, in the water. *(No Ch2 change: the line plays on that branch whether or not the player saw this.)*
4. She asks him, gruffly, why he didn't go to Tamsule with the side, "Tavi asked you twice". Rhen: someone has to keep her in brass. *(Seeds Ch7: her grandson Tavi, and the Tidecup Rhen will dive in for Oruvel.)*
5. She sends him off: *"Go on. The tide won't wait for a pretty face, and it won't wait for yours either."* He goes, laughing. It's the last thing she says to him in the game.

**Rules:**
- No more than four lines from Kell in a row, broken by Rhen's help and his questions (SPEC §3.6).
- **ADR 0022 watches, every one:** the wick is her own stock, given as to every diver; it is not a parting gift and not from or about Dace; nothing is said about Rhen's father; she never says anyone asked her to keep him; the wick is never fitted to the lantern, on screen or in a line. Kell is a neighbour who stepped in, never a mentor, and never in the party.
- Kell's voice: Low Reaches plain, fond through insults, a trader's arithmetic. *"Salt and stone"* when she means it.

**Payoff:** sets `ch01_kell_side_scene`. In Ch7, Rhen can give Kell's line to Tavi at the empty moorings, and Tavi laughs at it, because it's exactly her. E7 lights the first new lamp with the wick on every path.

---

## 5. Hullgnaw (C1-14): placement, phases, and what it teaches

**Placement:** directly after the run (C1-13), on the **net-pen hull**, a wide square raft of lashed decking around the Reefball practice net, with the children on the plank bridge behind Rhen and the storm wall growing over the town behind them. Hullgnaw comes up **through the deck**. It is the chapter's only boss, and it is fought **solo** (Rhen alone, the only one-hero boss in the game).
**Lore:** Undertow-spawn form from the storm's overflow and come ashore ahead of it (bible §9). This one formed in the wrecks under Oruvel and grew **through a drowned ship's rib-cage**, which it wears like a corset of black timbers. The ribs are why it's armoured, and why it breaks free when the raft does.

| Phase | Setup | Gimmick | What it teaches (pillar 4) | Story read |
|---|---|---|---|---|
| **1: the Ribs** | Hullgnaw coils in the ship's ribs through a hole in the deck (O16). The timeline shows its **Gnaw**, a heavy bite with a long delay, two Rhen turns out. | The ribs blunt any heavy strike. Light, low-rank strikes get between them. Choosing **Quick Hit** (rank 2) over **Undertow Cut** (rank 4) changes, in the preview, how many times Rhen acts before the Gnaw lands. | **The timeline itself:** who acts next, that every action has a cost in time, and that the preview shows the order shifting **before you commit** (SPEC §6.1). It's the base the Drownbell's telegraphed toll (Ch3) builds on. | A diver's fight: in, strike, out before the current turns. |
| **2: the Breaking Raft** | At half HP the lashings go and the deck splits into three sections that pitch with the swell. The ribs fall away, and Hullgnaw, free and faster, takes more turns. | Its turns crowd the timeline. Rhen's **Kick Off the Wall** (`kick_off`, rank 1) pushes it **back** down the timeline, buying him the turns to finish it. | **Turn manipulation:** pushing an enemy back is a tool, and Rhen is the character who does it (his niche, SPEC §3.4). The Swell's first fill is likely here; the existing HUD help line (`HUD_HELP_SWELL_FMT`) introduces Lamp Dive without an extra prompt. | He wins. It doesn't matter. The wall is already over the town. |

**Tutorial text** (UI, loc keys owned by UI/Combat), one prompt per phase, no more:
- Phase 1: *"Every action costs time. Watch the order shift before you choose: quick strikes bring your next turn sooner."*
- Phase 2: *"Kick Off the Wall pushes a foe back down the order."*

**Teaches, and doesn't:** this fight teaches the timeline and delay. It doesn't teach swapping (Rhen is alone; Ch4 teaches it, when Ysolde makes four), the Vowbound (Ch3), telegraphed party-wide delays or breaking a part (the Drownbell's rim, Ch3), or elements (Ch4).

**Battle barks** (≤ 25 words in total): Rhen only, short. Sample: *"I'm not scared. I'm busy."*
**Light:** Hullgnaw's wounds are `spawn_wound`, and every mote it sheds is **held** (cyan, sinking). When it dies its motes slide off the deck into the sea, never up (bible §2), the same quiet wrongness as the Drownbell's death in Ch3.
**Combat bands** (balance_targets.md, Ch1–Ch3 boss): naive ≤ 10%, role_answer 70–90%, smart 80–95%, p90 ≤ 60. Narrative asks Design to rule whether a solo tutorial boss takes the band as is or a logged exception (§9 Combat). Defeat offers **Fight again**, as every field battle does (first_playable_flow.md).

---

## 6. Music cues

The ids are the ones the `.dlg` files and the sequencer will use (`@music <id>`). `silence` is the reserved id that fades the bed out.

| Cue id | Beats | Kind | Brief | M3 final? |
|---|---|---|---|---|
| `oruvel_underway` | C1-01–C1-06 | Dungeon bed, loop | A low drone, struck glass, very slow, the lantern's hiss folded into the texture. Warm under the water, never menacing. Thins to the drone alone at the stairwell (C1-05). | sketch |
| `battle_underway` | C1-04, C1-06 | Battle loop | `battle_standard` heard through water: the same piece low-passed and slowed, so that Ch1's fights sound like they happen down there. | sketch (a variant of M1-AUD-02) |
| `rhen_current_hum` | C1-06 | **Diegetic**, one pass | Rhen humming the **current-song** under his breath as he rides the shaft. **This is the motif of the chapter, and of Dace.** It recurs in C1-15 sung whole, at Corrow in Ch8, and inside `goodbye_dace` (act3_ending E2, "Dace's current-song from Ch1 on plucked strings"). An **original** tune, a working chart in the Saltwright style, **distinct from the Hush lullaby** (`hush_first_verse`): Audio must be able to play the two side by side in E2 and have them heard as two songs. | **final** (it binds three later cues) |
| `oruvel_raft` | C1-07–C1-10 | Town bed, loop | Hand drums, a bowed string, plank-creak percussion, voices. Busier and rougher than `haluna_village`: a working town, not a festival. | **final** |
| `undertow_rising` | C1-12, C1-13 | Cutscene score, two stems | Stem 1: the town bed's melody stopping mid-phrase, then low brass and a held cluster as the wall rises. Stem 2 (the run): a pulse added, never a heroic one. | sketch |
| `hullgnaw` | C1-14 | Boss, two stems | Stem 1: creaking-timber percussion (ribs) and a low eel-glide figure. Stem 2: the swell, lashings snapping on the off-beats. | sketch |
| `going_under` | C1-15 | Cutscene score | Underwater roar falling away to near silence; then the **current-song sung whole** by a distant male voice (until SPEC §16 Q4/Q5 settle a voice, a vocalise-like solo instrument carries it, as `hush_first_verse` does), very far down, and nothing else. Ends in `silence`. | sketch |

**SFX cues** (requested): `lintel_gull_cry` (every carved gull at once, wind through hollow wood: the signature sound of the chapter), `tether_run` (C1-01's first sound), `lantern_shutter` (open and close), `salvage_cut`, `raft_lashing_snap`, `hullgnaw_ribs_creak`, `undertow_wall_roar`, `beacon_lamp_gutter` (Kell's lamp, C1-15, the last warm sound before the water).

**Recommendation to Audio:** the M3 final for Ch1 is **`rhen_current_hum`** (with `going_under` drawing on it) and **`oruvel_raft`**. Compose the current-song with E2 in mind now, because E2 sets it beside the lullaby for four bars.

---

## 7. Camera shots by beat

New shot ids for two new zones, to be defined in an `oruvel.md` environment sheet (§9 Art and Environment) the way haluna.md §5 does: **U** for the Underway, **O** for the raft-town. Lenses are proposals; Cinematics owns them.

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| C1-02 | U01 → U02 | **U01** (24 mm, below Rhen looking up): Rhen on the tether, the town's hulls a dark lattice on the bright surface, god rays. The opening frame of the playable game. **U02**: the default rail down the crown. |
| C1-03 | U03 | The bell-room from the water's surface level: the air pocket's mirror ceiling, Rhen's head and lantern breaking it. |
| C1-04 | U04, U05 | **U04** (18 mm): the gallery of dead lamp-columns receding into dark, the lantern's pool the only warm light. **U05**: the coral-curtain reveal (open shutter). |
| C1-05 | U06 | Locked, 50 mm, at the stairwell lip looking down: the knotted cord across the frame, held motes sinking below it, Rhen a silhouette at frame left. Held motes ≤ 5% of the frame. |
| C1-06 | U07, U08 | **U07**: the gauge-wheel room, the wheel as a ring of brass in the lantern light. **U08**: the shaft from above, Rhen rising up it toward the light. |
| C1-07 | U09 → O01 | **U09 → O01 is one continuous move** (a same-axis rise through the surface, so a blend is allowed): up through the Snell window into O01 (35 mm at the waterline, the raft-town at Rhen's eye). |
| C1-08 | O02 | The scale-hull: the scale, the chit stamp, the Level plaque, Rhen across the counter. |
| C1-09 | O03–O08 | Rail cameras. **O07** is the insert on the *Seventh Terrace*'s name-board (the plant for Ch4, held 1.5 s; the board's carving must match D06 exactly). **O08** is the keel-hull with its lintel-gull. |
| C1-10 | O09 | Kell's stall at 65 mm, shallow depth of field, her hands and the wick in focus; inserts on her hands for the side scene, as H08 does for Osu. |
| C1-11 | O10 | 85 mm, low, past Rhen's shoulder to the nearest lintel-gull against a cloudless sky. Hold through the first cry. |
| C1-12 | O11 → O12 → O13 | **O11**: the horizon wide, the sea drawing back, the wall standing up into blue (the `ch01_arrival` preset). **O12**: the drill on the hulls, Kell on her roof with the beacon lamp. **O13**: the *Seventh Terrace* under sail, running. All cuts. |
| C1-13 | O14, O15 | Rail cameras on the run. O15 is the net-pen hull approach with the wall over the town. |
| C1-14 | O16, O17 | **O16**: Hullgnaw bursting through the deck in its ribs. **O17**: the phase-2 split, the deck in three pieces. |
| C1-15 | O18 → U10 → U11 | **O18**: Rhen on the broken pen, the wall filling the frame, Kell's beacon lit on the keel-hull, the water over the lens. **U10**: under, the motes coming down around him. **U11**: looking down past his feet into the dark, the current-song rising from it. **Never** a figure in U11. Cut to black on the song's last note. |

**Watches for Cinematics:**
- **Kell's last frame** (O18): her lamp is lit when the water covers the lens. We never see it go out.
- **U11 shows no one.** If a shape appears in the dark in previs, cut it.
- The Prologue's last frame (rising glimmer) and U10's sinking glimmer are the first and second motes the player sees: up, then down. Keep them far enough apart (the card and two dungeon beats) that the contrast is felt, not explained.

---

## 8. Word counts

Estimates, before any `.dlg` exists. `tools/dialogue_stats.py` replaces them once M3-C01-02 writes the scripts.

| Beat | Words (written) | Notes |
|---|---|---|
| C1-01 card | 3 | loc key |
| C1-02 drop | 17 | VO |
| C1-03 bell-room | 45 | Rhen alone |
| C1-04 galleries | 15 | tutorial prompts are UI keys, counted separately |
| C1-05 low lights | 30 | Rhen + VO |
| C1-06 gauge-wheel | 20 | barks; the hum has no words |
| C1-08 scale-hull | 120 | both branches |
| C1-09 barks | 170 | six barks |
| C1-10 wick | 15 | every path |
| C1-10 side scene | 170 | optional |
| C1-11 gulls | 15 | |
| C1-12 Rising | 60 | |
| C1-13 run | 60 | both branches of the choice |
| C1-14 battle barks | 25 | |
| C1-15 going under | 16 | VO |
| **Total** | **~780** | **~600 on a typical path without the side scene** |

**Per speaker (estimate):** Rhen ~45% (including ~65 words of VO), Kell ~22%, the scale-man ~9%, villagers and Sabe ~24%.

**Against SPEC §3.6** (40–60k words, ceiling 80k): at ~35 min of a 30 h main story, Ch1 is **1.9%** of the game, so its fair share is **~780–1,170 words**. At ~780 it sits at the bottom of that, which is right for a chapter where the hero is alone underwater for a third of it. Tutorial prompts (about 8 UI strings, ~90 words) are UI text, not dialogue, and aren't counted here.
- **Rule:** hold C1-09 at or under 170 words. Barks that run long here cost the Kell scene its weight.

---

## 9. Requests to other roles

Each item is written to be filed as its own task.

### Environment Art (kits per zone)
1. **`ch01/oruvel` raft-town kit** (SPEC §7.4's "village timber"; Low Reaches, poorer than Haluna):
   - lashed **hull modules**: outrigger hulls, cabin hulls, three sizes, with sun-faded paint variants;
   - **plank bridges** between hulls, with visible lashings that read as tension;
   - cabin ridges with **lintel-gulls**: Haluna's gull mesh with an **open-throat variant** (the carved throat is hollow and visible, because C1-11 depends on it);
   - the **keel-hull** (hero: the oldest, three decks, the town's meeting place);
   - **Kell's chandlery** (hero: lamp racks, oil jars, wick spools, the post shelf, the roof beacon lamp);
   - the **scale-hull** (a brass scale, the chit stamp, a small Level plaque, the town's only Order mark);
   - the cookboats, the net lanes, the **Reefball practice pen** (a square raft round a netted pool), dive moorings with tether winches;
   - the drowned towers' crowns visible 3–6 m under the hulls (`lagoon_clear` ×2.0).
   - **The storm variant:** snapped lashings, separating raft sections (a rig for C1-13 and the boss arena's three-way split), capsized hull pieces, the sea drawn back off the reef (C1-12).
2. **`ch01/oruvel_underway` drowned-tower kit** (SPEC §7.4's "ruined-city concrete-and-coral"):
   - coral-crusted concrete floors and walls;
   - **dead lamp-columns** in white Lit Age ceramic (the same family as Iskarra's, darker and more overgrown);
   - **cuttable brass props** with a cut state (hinges, pipe runs, the gauge-wheel hero prop);
   - **bell-rooms**: a sealed room with an air pocket whose surface reads from below (the rig's `water_underside`);
   - **coral curtains** that the open shutter reveals;
   - the **stairwell** down into dark, with the knotted divers' cord across it;
   - the current **shaft**;
   - the tether line prop, running back up to the surface.
   - No bound light anywhere in the tower: every housing is empty and dark.
3. **`oruvel.md` environment sheet** with shots U01–U11 and O01–O18 (§7), on haluna.md §5's pattern, and the **post-credits rebuilt variant** of the town (act3_ending E7, `post_credits`): the same moorings rebuilt, not the same hulls.
4. **The *Seventh Terrace***: a Pemakar copper coaster, red-and-black lacquered, copper-sheathed, with a carved **name-board** on the stern in Pemakar terrace script. Build it once: it is moored at Oruvel in Ch1 (O07, O13) and drifts as the Ch4 derelict (act1_ch04.md §9), and **the name-board is the same hero prop in both chapters**.

### Art and Rendering
1. **Color script `ch01`:** add the storm sub-frame (`lut_ch01_storm`, 11:10–11:28) and an **underwater-in-storm** frame for C1-15 (no god rays, churned dark, the oil lantern the only warm light, held motes ≤ 15% of the frame at their densest).
2. **Undertow presets:** `ch01_arrival` exists ("far off"). Add **`ch01_landfall`**: the wall at the town in a clear sky (O18), which is a different read from Ch8's slate-sky landfall. Ch1's storm keeps a **blue sky above the wall**; that is the image.
3. **Underwater rig:** confirm `UnderwaterRig` handles a camera moving through a bell-room's air surface and up through the open sea (U09 → O01) in one move.
4. **Glimmer:** held motes in C1-05 (a few dozen, a slow sink down a stairwell) and C1-15 (hundreds, appearing from above as lamps go out). Both are `glimmer_held`. Nothing rises in Ch1.

### Creatures and enemies (Character Art and Combat; silhouettes)
| Id | Kind | Silhouette | Role and answer | Notes |
|---|---|---|---|---|
| `wickfry` | **new** regular (creatures track's id) | A shoal of glass shrimp, one combatant: a loose cloud of small clear bodies that catch the lantern light, so the shoal reads as a moving glitter, brightest where the lantern is | fast and frail; acts often, so it shows who acts next; **Rhen** | Drawn by the open shutter (C1-04). Scripted encounter 1. |
| `tower_limpet` | **new** regular (creatures track's id) | A limpet the size of a door, a low ribbed cone fixed to a gallery wall or across a passage; it barely moves | a slow wall that delays; skippable; the timeline shows how long it takes | On the route, so it can be walked round or fled; teaches that not every fight is worth its time. |
| `oil_slug` | **new** regular (creatures track's id), scripted once | A fat, soft slug, dark and glossy with lamp oil, a faint warm sheen where it has been feeding; it smothers light rather than strikes | a blinding caster (Darkness); **weak to fire** | Scripted encounter 2 (items). Its fire weakness is for later chapters. |
| `scuttler` | **new** regular, Undertow-spawn | A crab-shaped spawn with a hollow, wet black carapace and drifting cyan wounds along the seams; too many legs, moving wrong | the first spawn; Rhen | Shows the spawn language before the boss. A palette variant can serve Ch8's wall. |
| `hullgnaw` | **new** boss, Undertow-spawn, two phases | A long eel whose middle third is caged in a dead ship's black rib-timbers like a corset, wounds bleeding held cyan between the ribs; in phase 2 the ribs are gone and it's longer, thinner, and faster | §5 | Lore and phases in §5. |

**Answers to the creatures track's questions (2026-10-24):**
1. **Foes on screen per encounter** (this sets their triangle budget):

   | Zone | Encounter | Combatants | Bodies on screen |
   |---|---|---|---|
   | `ch01/oruvel_underway` | scripted 1 (C1-04) | 1 `wickfry` | one shoal of about 30–60 small bodies, drawn as a single instanced combatant |
   | `ch01/oruvel_underway` | random | 1–2: `wickfry` ×1–2, or `tower_limpet` ×1 with `wickfry` ×0–1 | at most 2 shoals, or 1 limpet and 1 shoal |
   | `ch01/oruvel_underway` | scripted 2 (C1-06) | 1 `oil_slug` | 1 |
   | `ch01/oruvel` storm | scripted (C1-13) | 2 `scuttler` | 2 |
   | `ch01/oruvel` storm | boss (C1-14) | 1 `hullgnaw` | 1, plus the rib-timbers in phase 1 |

   Rhen fights alone all chapter, so no Ch1 encounter has more than two foes. That keeps a one-hero timeline readable.
2. **Hullgnaw's breaking raft is the arena (environment), not the boss.** The net-pen hull and its three-way split are an environment rig owned by Environment Art, with the phase-2 split cued by the boss's half-HP phase change. The rib-timbers are the boss: they are part of `hullgnaw`'s phase-1 model, and they fall away as it changes phase.
3. **Keep, cut or rename:**
   - **Keep** `wickfry`, `tower_limpet`, `oil_slug` and `hullgnaw`, used as above. The slug's dimming of the lantern is the best fit in the chapter, because it turns Ch1's own mechanic against Rhen.
   - **Add `scuttler`** (Narrative's id): the story needs one **Undertow-spawn** before the boss, on the raft (C1-13). The three Underway creatures are ordinary sea life from before the storm, and the player should meet the spawn's visual language (wet black carapace, sinking cyan wounds) once before Hullgnaw. If the creatures track has a spawn regular for Act I, use its id here instead.
   - **Rename, suggested:** `wickfry` → something like `lampfry`. Since ADR 0022's sweep-J note, "wick" in the story belongs to Kell's gift alone, and `relighting_wick` already shares it. A shrimp named for the wick, in the same chapter Kell gives him one, blurs the one object that has to stay singular for E7. The id can stay if the display name avoids "wick". This is a suggestion; creatures decides.
   - **Cut** Narrative's first-draft ids `gutter_ray` and `brassmaw` (replaced by the above), and `lantern_eel` from Ch1 (it stays in Ch2–3 as built).

### Combat
1. **Solo battles:** confirm `BattleRequest` and the HUD handle a one-hero party (active `[rhen]`, no reserve) for C1-04, C1-06, C1-13 and C1-14.
2. **Hullgnaw** per §5: the ribs' heavy-strike resistance, the phase-2 split, its faster turns, and `kick_off` as the answer. Give the encounter `prompt_key`s as `drownbell` does.
3. **Bands:** Ch1 regulars on the Ch1–Ch3 regular band; Hullgnaw on the Ch1–Ch3 boss band, or a logged tutorial exception. Narrative's view: a masher should still lose to it, and the prompted player should win nearly always (role_answer near the top of 70–90%).
4. **A loadout `ch01_hullgnaw`:** Rhen alone, starting gear, the Salt Tonics and Brine Eyewash the Underway gives (two in the tin if found, plus drops).

### Design
1. **Underwater traversal:** weighted walking, tether points, no breath meter (C1-02). Bell-rooms are full-heal rest points with no save.
2. **The lantern shutter** (C1-04): the light radius open and narrow, the encounter-rate modifier, and the reveal of coral curtains. No fuel.
3. **Tutorial gating by seen-flags**, not by chapter, so the slice's Ch2 start and a Ch1 start both teach each thing once. Ch1 teaches: movement (if the Prologue doesn't), tether and interact, the lantern, the command menu, items, escape, the timeline, delay (Kick Off). **Ch2–3 keep:** the save shrine, shop and inn, the field camera in town, fliers as Rhen's niche with a party, the temple puzzle, a telegraphed party-wide delay and part-breaking (the Drownbell), and the Vowbound. **Ch4 adds:** swapping, Read, and elements.
4. **The Lattice's first use:** Ch1, after the Underway (C1-09), when Rhen has movement points to spend. Confirm or move it, and say where Ch2 shows it if Ch2 is the start.
5. **Economy:** the gauge-wheel's sale price, the haggle's few lume, the old tin's accessory.
6. **No save shrine in Ch1.** The chapter autosave at C1-01 and Fight again at Hullgnaw are the safety net for a 35-minute chapter. If playtests say that's too long unsaved, the fallback is a save at the scale-hull, and Ch2's save tutorial then moves to Ch1.

### UI
- Title card `CH01_TITLE_CARD`.
- Prompts: the shutter, tether points, salvage cut, the command menu, items, escape, the two Hullgnaw lines (§5).
- The key items `gauge_wheel_brass` and `kell_wick` (the wick can't be used, sold or dropped, and its description never mentions Dace or the lantern).
- The one-hero battle HUD.
- **Note:** `relighting_wick` (a consumable in `items.json`) and `kell_wick` must read as unrelated objects. The consumable's description should never evoke Kell.

### Audio
The cue list in §6, especially **`rhen_current_hum`** as an original working tune distinct from the Hush, composed now for its later use in Ch8 and E2. SFX list in §6, especially `lintel_gull_cry`.

### Systems / flow (M3-ARC-01)
- The Prologue hands off to `ch01/oruvel_underway` `Drop` (C1-01). Ch1's exit is `ch02/haluna` `Beach` with Cutscene A, after a 3 s black hold.
- New speakers: `kell` (`CHAR_KELL`), `scaleman` (`CHAR_SCALEMAN`), `cook` (`CHAR_COOK`), `sabe` (`CHAR_SABE`), `skipper_sadi` (`CHAR_SKIPPER_SADI`).
- `Game.set_chapter(1)` at the card.

### Cinematics (reviewer)
Check C1-12's drill staging, Kell's last frame in O18, U11's empty dark, and the U09 → O01 rise. Anim and mark names in future scripts are proposals.

### Narrative (later sheets)
- **Ch4 (act1_ch04.md):** the *Seventh Terrace* is the derelict; Rhen recognises her.
- **Ch5 (M3-C05-01), proposal:** the *Seventh Terrace* was a Pemakar coaster, so her name-board goes home to Pemakar's harbour in Ch5.
- **Ch7 (M3-C07-01), proposal:** the payoffs of `ch01_has_kell_wick`, `ch01_kell_side_scene` and `ch01_ran_for_kell` with Tavi (§3).
- **Ch8:** the current-song returns when Rhen sees the figure in the storm.
- **Ch18 (open):** Ch1 never shows whether anyone on the keel-hull lived. The post-credits town is rebuilt by *someone*. Ch18's revisit decides who.
- **Lead:** the "one month earlier" card against the travel calendar (C1-01).

---

## 10. Echo watches (ADR 0017's Ch1 rows, re-checked for this sheet)

| Beat | Nearest analogue in the inspiring game | Verdict |
|---|---|---|
| The dive (C1-02–C1-06) | the displaced hero waking in cold, half-frozen ruins underwater, then fighting a great fish in them and being rescued by salvage divers | Ours comes **before** the storm, in warm water, as the hero's own trade. He is the salvage diver. Nothing is frozen, nobody is rescued, and **the Underway has no boss** (the oil slug is a regular). Pass. |
| The Rising (C1-11–C1-12) | a gleaming metropolis destroyed at night during a sports match | A poor raft-town by day under a clear sky; no sport is on, and the town's side is away at Tamsule. Pass. |
| Hullgnaw (C1-14) | the opening city's fights on a collapsing structure, beside a mentor | Rhen fights alone. **No mentor, no guide and no companion** is on the raft (Kerrid is not at Oruvel). Pass. |
| Going under (C1-15) | the hero pulled into the monster and carried through time by a guide; hearing his father in it | Nobody takes him; the sea does. He is given back one night later, one island west. The father's voice is heard, never seen, and leads nowhere. **Accepted** (as in ADR 0017): SPEC fixes that Dace vanished into the Undertow, and the song is real (bible §9). |
| Kell's wick (C1-10) | the keeper hands the hero a gift from his father on the night the calamity opens the game | ADR 0022's sweep-H row: her own stock, her trade habit, given to every diver; nothing of Dace. Pass, with the watch. |
