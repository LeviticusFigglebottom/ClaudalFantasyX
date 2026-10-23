# 0017 — Act I re-staging, with an echo check from the Prologue to Ch8

- **Status:** accepted (Lead sign-off 2026-10-23)
- **Date:** 2026-10-23
- **Roles affected:** Narrative, Cinematics (Prologue, Ch4, Ch6, Ch7 and Ch8 staging), Environment (`prologue/iskarra_dusk` loses its fire prop; `ch04/brightwater_ferry` gains a derelict hull alongside; `ch08/corrow` gains the Fisher Stair), Combat (the Spar-Wraith arena; the Ch8 set-piece; Tamsule's Reefball roster), Art and Rendering (color script `prologue`, `ch06` and `ch07` notes), Audio (the Ch7 naming rite)
- **Author role:** Narrative (M1-NAR-09)
- **Follows:** [0016](0016-act-two-restaging.md), which checked Ch9 to the ending and handed on two Act I residuals

## Context
ADR 0016 left two Act I beats for this task:
1. **Ch7.** High Warden Sefir is introduced at the Tidecup, the sport tournament, warm and gracious, mentioning Asha's mother. The inspiring game introduces its cleric antagonist at its own tournament, where its church's leader also opens the games.
2. **Ch8.** At the seawall, the Stillguard defend Corrow with Liss's forbidden Saltwright cannons. The inspiring game's coastal operation is an allied military assault on the monster using forbidden machine weapons, and it fails.

The rest of Act I had not been checked the same way. The inspiring game's opening acts, as beats rather than names, run:
- a glittering city destroyed during a sports match, its star player pulled through time by the monster, with a guide who means to take him;
- waking alone in cold, half-frozen ruins and being rescued by salvage divers;
- washing up on an island village; the heroine's first temple trial, the hero entering against the rule, and her exhausted emergence followed by a show of her first summon;
- the pilgrimage leaving the island, a boat ride, and the monster attacking the boat (a boss on deck);
- a ravaged island village, the heroine's dance for its dead, then a fire temple;
- the tournament in a port city: the cleric's arrival, the guardian-captain's last match with the hero as its star, monsters loosed on the stadium, and the dead swordsman who knew both fathers joining;
- the long travel road;
- the coastal military operation with forbidden machines, which fails;
- a roster of fixed archetypes, each with an introduction.

**What SPEC fixes (not open to change):**
- §3.5 Prologue: the party at the ruins of a dead city at dusk, and the line "Listen. This might be the last time I tell it."
- §3.5 Act I: Rhen survives an Undertow attack, washes up, meets Asha's group and joins as a guardian; they visit temples, attend festivals, and play the sport tournament; the Undertow attacks a coastal fortress, followed by the first great dance for the dead.
- §3.4: the seven archetypes and their arcs.
- §6.10: Reefball in a suspended sphere of water (N-12, the human's call, still open).

## Options
1. **Keep Sefir at the Tidecup but in the background** (no blessing, no speech). Rejected. He would still be the church's face at the tournament, and a background cameo by the antagonist at the games is the same beat played quieter.
2. **Move Sefir's first appearance to the Ch8 seawall** (0016's suggestion). Rejected. In the inspiring game the cleric also stands with the commanders at the coastal operation. Moving him there trades one echo for another.
3. **Move Sefir to the Ch5 Lanternfall** (0016's other suggestion). Workable, but Ch5 already introduces Kerrid. Two arrivals at one festival crowd both, and it would put Kerrid, his victim, in the same frame before the player knows either man.
4. **Move Sefir to the end of the Ch6 raid; strip the Order from the Tidecup; re-stage the seawall as an evacuation with no weapon; and fix three smaller echoes the audit found (chosen).** Details below.

## Decision

**(a) Sefir first appears at the Brine Shoals, at the end of the Ch6 raid.** The High Warden is on his once-a-Calm progress along the south coast to see the Salt Edict kept. His white barge is poled up the shoal channel through the smoke and leaves no wake. This plants Ansedra's stillness (Ch13–Ch14) eight chapters early.
- He stops the brine-branding of the captured wrights with one sentence. He rebukes his Inquisitor gently ("The Edict burns things. It has never needed to burn people."), and he doesn't ask who struck his Stillguard.
- He tells Asha he knelt beside her mother. He lets Liss go on Toma's papers, citing the custom that a Cantor may take any guardian she chooses, and he looks at her crate a moment too long.
- Toma is overjoyed: his faith is handed back to him in the same hour he froze. Kerrid keeps his back to the barge. Sefir's eyes rest on him for half a beat and move on.
- Liss, after the barge has gone: "He put the fire out once it had finished."
- *Why it serves the pillars:* Sefir is introduced by an act of mercy that costs him nothing, at the edge of a burning his own Edict lit. That is "charming and reasonable" (SPEC §3.4) and the corrupt church in one image (pillar 1, no wink). Letting Liss go rhymes with his giving her the Lamp Archive in Ch13: both times he lets her see, because he can afford to.

**(b) The Tidecup has no Order official, and Rhen dives for Oruvel (Ch7).**
- **Nobody from the Order blesses or opens the Tidecup.** It opens the way Reefball always has, as a Low Reaches rescue drill (N-12): each captain names one person the sea has taken. The Bell is "sanctified" glimmer-tech, and Liss says so aloud. Nobody answers. That line stays, because it is the Order's selective law, which is SPEC §3 material, voiced by an outlaw.
- **Toma no longer captains Haluna's side.** That was the inspiring game's guardian who is also the island team's captain, with the newcomer as his star. Instead, **Oruvel's side** came to Tamsule a week before the storm and has been waiting for news. Its captain, **Tavi Orse**, is Mother Kell's grandson. He finds Rhen in the crowd, and Rhen has to tell him that Kell couldn't swim. The side is a player short: their youngest went home to look and hasn't come back. Rhen dives for his drowned town.
- At the naming, Tavi names the whole town: "Oruvel." The match is played for the ones who didn't come up.
- **Nothing interrupts the match.** No spawn are loosed on the Bell, and there is no rescue in the galleries. Toma, who played here for Haluna as a boy, watches from the galleries beside Asha.
- **Side scene:** Tavi asks Asha to bless the empty moorings under the Bell, where Oruvel's boats always tied up to watch. It is the same rite as the old veteran's benches (N-12), now carried by a named person the player has met.
- *Why:* the tournament is mandated, but whose match it is isn't. Playing it for a town the player watched drown in Ch1 makes the brightest frame in Act I (saturation ×1.18) a festival held beside a graveyard (pillar 2). It also gives Rhen a beat of standing still for loss, which is his whole arc.

**(c) The seawall is a defence by evacuation, with no weapon (Ch8).**
- **Corrow has no weapon against the Undertow, and nobody pretends otherwise.** Its defence has been the same for nine hundred years: light the Coilspire beacon, and get the low town up the **Fisher Stair** onto the wall before the sea does. There is no operation, no allied assault, no cannon, and no forbidden machine anywhere on the wall.
- **Set-piece:** the party holds the wall-head over the Fisher Stair against waves of spawn while the low town climbs.
  - Liss rigs a rope-and-block hoist off the Watchers' carved faces to lift children and the old faster than the stair can take them. It is plain rope and iron, with nothing bound in it.
  - Pell is on the wall, imitating the storm's sounds to lure spawn away from the fishers on the stair.
  - Toma fights beside his old Stillguard comrades.
- **Boss:** *the Undertow's Reach* (multi-phase, scripted escape), unchanged. **The wall falls anyway.** The stair was not wide enough. That is SPEC's "coastal fortress attacked", and the hundreds of drowned are why Ch9's Ebbing exists.
- Rhen's freeze at the figure in the storm is unchanged.
- **After:** the Stillguard cut Liss's hoist down, because it was bolted into the Watchers. The Order thanks no one, which keeps her Act I beat and loses the weapon.
- *Why:* the inspiring game's beat is *going on the offensive* against the monster with forbidden weapons, and failing. Ours is *getting people up a stair*, and failing at the margin. Nobody in Act I believes the storm can be fought. That belief belongs to Act III, where it is earned, and the weapon is a song.

**(d) The Ch4 ferry is not attacked; the party boards a dead ship.** Mid-strait, the ferry comes on a trader lost in the same Rising that took Oruvel, drifting with its sails still set and nobody at the helm.
- Low Reaches sea-law says you don't pass a drowned hull without bringing its **name-board** home. The ferry-master won't send his crew aboard. Rhen, the diver, goes, and Asha won't let him go alone.
- **Boss:** the *Spar-Wraith* (a spawn tangled in the dead ship's rigging) is fought on the derelict's deck. Ysolde's magic is introduced there.
- They bring the name-board back to the ferry. Rhen, who has sold drowned brass his whole life, carries this one for nothing.
- *Why:* "the monster attacks the boat carrying the pilgrimage, boss on deck" is the inspiring game's first crossing. Choosing to board the dead is ours, and it is the first time Rhen salvages for someone else.

**(e) The Prologue has no campfire circle, and nobody walks away from the group (SPEC's setting and line are kept).**
- The seven are on the broken plaza at dusk, but **apart**. Each keeps a vigil at a distance: Kerrid standing (he never sits), Pell with his back to the sea, Ysolde with her book shut, and Asha on the steps.
- **The short walk (the controls tutorial) goes *among* them.** Rhen crosses from one to the next, and each gets a look or a gesture, with no words. He ends sitting beside Asha and trims his oil lantern's wick. It is the only flame in the frame (N-02: oil is the last light the game shows).
- The line comes as the wick catches. Then glimmer rises, and we cut.
- *Why:* the inspiring game opens on its party around a campfire in the ruined city, with the hero standing, walking away from them to the edge, and narrating over the ruins. SPEC fixes our place and our line, so the staging has to carry the difference. A man walking toward each of the people he is about to lose, and sitting down, is Rhen's arc ("stop running from loss") in one shot.
- Ch19's return to the frame uses the same vigil.

## Echo check: every Act I beat, Prologue to Ch8
"Analogue" means the nearest beat in the inspiring game. **Mandated** marks a beat SPEC requires. For those, the check is that our *staging* differs. **Accepted** marks a residual kept on purpose, with the reason.

| Ch | Our beat | Nearest analogue | Verdict |
|---|---|---|---|
| Pro | Iskarra at dusk: the seven apart, Rhen walks among them and sits by Asha, lights his oil lantern; the line | the party's campfire at the ruined city; the hero walks off alone to the edge and narrates | **Mandated** setting and line (SPEC §3.5). The line's sense, a story told perhaps for the last time, is close to the inspiring game's own opening line, and SPEC fixes it word for word: **accepted**, as the human's brief. Staging re-done (e): no fire circle, no walking away. Pass. |
| 1 | Oruvel: a poor raft-town over a drowned district, by day; Rhen's salvage dive; the storm out of a clear sky; Hullgnaw on a breaking raft; his father's song in the dark water | the gleaming metropolis destroyed at night during a sports match; the hero pulled into the monster, through time, by a guide | **Mandated** attack (SPEC §3.5). Ours has no sport, no night spectacle and no guide: **Kerrid is not at Oruvel** (watch). Rhen is taken by the sea and given back one night later, one island west (ch02 line 012–013). Nothing carries him through time or space. Pass. |
| 1 | The drowned-tower dive (Oruvel Underway) | waking alone in cold, half-frozen ruins, starving; rescued by salvage divers | Ours comes *before* the storm, in warm water, as the hero's own trade. The hero *is* the salvage diver, so that role is inverted. Nothing is frozen and nobody is rescued. Pass. |
| 1–8 | Rhen hears his father's current-song in the storm (Ch1) and freezes at a figure inside it (Ch8) | the hero's father is the monster, and the hero senses him in it | **Accepted.** SPEC §3.4 and §3.5 fix that Dace vanished into the Undertow and that Rhen says goodbye to him. ADR 0016 already made Dace **not** the storm and never fought: he is holding someone else's light together. The Ch8 figure turns *away* (abandonment, Rhen's own wound), and Rhen freezes rather than runs toward it. |
| 2 | Haluna: Rhen wakes in the shallows; Asha kneels over him first and Toma's spear is at his throat; he knows exactly who and where he is | washing up at an island village, found in the water by the guardian at sport practice; the hero is taken for one whose memory the monster's poison scrambled | **Mandated** wash-up and meeting (SPEC §3.5). He meets the heroine first, on the beach, because she heard the dead come ashore with him. No sport, no amnesia, no disguise. **Accepted residual:** the heroine's home is an island village, and the pilgrimage starts there with a local temple. A man washed up from a drowned raft-town lands at the nearest village, and the Low Reaches are a coral archipelago. Haluna's living funeral (Ch4) and tidal-islet shrine are ours. |
| 3 | The Saltgrass Causeway; the shell-basin water puzzle; Asha goes in alone by rite while Rhen and Toma wait and talk; she comes out at sunset with light lifting off her and sings the first verse, which is Rhen's father's lullaby; the Drownbell answers the verse | the first temple's trial; the hero breaks the rule and enters it; the heroine emerges exhausted, is caught, announces her success, and shows her first summon to the cheering village; a hymn sung in every temple | **Accepted residual:** a rite done alone while companions wait is the plain shape of a pilgrimage temple, and the vertical slice is scripted, staged and reviewed (sweeps B to D). Ours differs at each specific point. Rhen *keeps* the rule. The wait is the scene ("Do you know what a Cantor is?"). She walks out on her own feet with a joke. The meaning beat is a family lullaby he recognises, not a summon shown off. The first summon is in battle, as the tide floods. **Watch** (Cinematics): no stumble or catch at the door, and no summon display there. A note is added in `ch03_the_first_verse.dlg`. Pass with that noted. |
| 4 | Haluna's living funeral for Asha; Rhen learns the Cantor doesn't return, is angry, and Asha comforts him; the dawn ferry; Ysolde boards; the party boards a drifting dead trader to bring its name-board home and fights the Spar-Wraith in its rigging | the pilgrimage leaves the island; the monster attacks the boat, a boss on deck; the hero learns very late, in anger, what the pilgrimage ends in | Re-staged (d): **the ferry is never attacked.** The party chooses to board the dead. The wake is our rite. Rhen learns the cost at Ch4, early and from a village's grief, where the inspiring game's hero learns it near the end of its Act II. Pass. |
| 5 | Pemakar's Lanternfall among the terrace graves; Kerrid arrives unasked at the festival's edge, says one line to Asha and walks with them; Ashcrown (Lightning); the Cinder Matron | a ravaged island village, the heroine's dance for its dead on the water, then a fire temple; the legendary guardian joins at the tournament and asks to serve | Ours is a festival, not an aftermath, and no Cantor dances for anyone: the first great Ebbing waits for Ch9 (mandated there). Kerrid's archetype is **mandated** (SPEC §3.4). He joins at a festival, not the tournament. He asks nothing, and nobody hails him. **Watch:** no-one names him as a legend, and Toma does not recognise him until the Cold Road (Ch12). Pass. |
| 6 | The Brine Shoals: an Order raid burning a Saltwright camp; Toma freezes; Liss sheltered; the Inquisitor fight; **Sefir's first appearance** on his Edict progress | the outlawed people's home destroyed later in that game; the mechanic girl joins at a river crossing after a kidnap attempt | Persecution is SPEC §3.4 (Liss's people). The raid, the sheltering and the joining on Toma's papers are ours. Sefir's arrival (a) is at a burning, with no crowd, ceremony or games. Pass. |
| 7 | The Tidecup at Tamsule: opened by the captains' naming rite; **Rhen dives for Oruvel's side** under Tavi Orse; no Order official; nothing interrupts; Liss's line about the Bell | the tournament: the church's leader opens it, the cleric arrives, the guardian captains the island team with the hero as star, monsters are loosed on the stadium, the dead swordsman joins | **Mandated** tournament (SPEC §3.5, §6.10). Re-staged (b): no cleric, no church opening, no guardian-captain, no attack, no joining. The arena form is N-12, for the human. Pass. |
| 7–8 | Tamsule to Corrow by sea; no route zone between | the long travel road between the tournament and the coastal operation | No road chapter exists between the tournament and the fortress. Our two routes are a tidal causeway (Ch3) and mud-flat wrecks (Ch6), both before the tournament. Pass. |
| 8 | Coilspire (Fire): the beacon flues; Wenna's marks. The Undertow comes; **the defence is the evacuation up the Fisher Stair**; Liss's rope hoist; Pell on the wall; the Undertow's Reach; the wall falls; Rhen freezes; the hoist is cut down after | the allied military operation against the monster on the coast, using forbidden machine weapons, which fails; a lightning temple after it | **Mandated** fortress attack (SPEC §3.5). Re-staged (c): defensive, no operation, no weapon, no forbidden machine. The failure is that a stair was too narrow. Our fire temple comes *before* the attack. Pass. |
| 3–8 | The element order Water, Lightning, Fire | the inspiring game's early temples, fire then lightning | **Accepted** in [0015](0015-vowbound-element-temple-order.md): the same pair, swapped, with no shared setting or beat. Unchanged here. |
| I | The overall order: island village and temple, sea crossing, festival and temple, raid, tournament, fortress and temple, dance for the dead | the inspiring game's Act I order | **Accepted residual:** "temples and festivals, the tournament, then the fortress, then the first great dance for the dead" is SPEC §3.5's own order. Inside it, every beat that isn't mandated now differs: no attack on the crossing, no dance before the fortress, no cleric at the games, no assault on the coast. |

**The roster (SPEC §3.4 mandates every archetype).** The check here is each introduction and any trait beyond what SPEC fixes.

| Who | Nearest analogue | Verdict |
|---|---|---|
| Rhen | the displaced sport-star hero whose famous father became the monster | **Mandated** (a diver whose Saltwright father vanished into the storm). Ours is native, not displaced. He is a salvage diver, not a star, and his father is an absence, not a celebrity. Reefball is a match he plays once, for his dead (b). Pass. |
| Asha | the young heroine on a sacrificial pilgrimage, whose *father* was the last to make it | **Mandated** (her *mother* was the last Cantor, she smiles to protect others). She finds the hero, rather than the other way round. Pass. |
| Toma | the devout guardian and team captain whose faith breaks, who resents the mechanic's people | **Mandated** (former temple warrior, faith shattered). The Reefball captaincy is **removed** (b). **Accepted residual:** his guilt toward Saltwrights. It is guilt for an act he committed (the camp burning), not a creed of prejudice. Liss's people are known to him from her first scene, so there is no hidden identity to be revealed, and the reckoning is a confession in grief at Hollowmere (Ch15, ADR 0016). |
| Ysolde | the cold, elegant black mage guardian, grieving a fiancé killed fighting the monster | **Mandated** (cold elegant black mage, grieving widow). She is not a guardian from the village but an Order appointee who boards at the crossing. Her husband was a Cantor and is a Saint she visits, which is ours. Pass. |
| Kerrid | the dead swordsman who guarded both parents, joins at the tournament | **Mandated** (unrisen, knew both parents). His introduction, costume and confession are ours (Ch5; ADR 0016 Ch15). The kit has no coat, hat, eyewear or gourd (kerrid.md IP note). Pass, with the Ch5 watch above. |
| Liss | the outlawed people's thief and mechanic who rescues the hero | **Mandated** (Saltwright item specialist). Inverted: the party rescues her. Pass. |
| Pell | the quiet non-human outcast blue mage | **Mandated** (Kirru, blue mage, outcast). He is found on the seawall imitating the storm, not a guardian from the start, and his exile is about how he grieved. Pass. |
| Sefir | the cleric antagonist introduced at the tournament, later at the coastal operation | Moved to Ch6 (a), at neither. Pass. |

**Watches (for Cinematics and later Narrative work):**
- **Ch1:** no figure guides Rhen into the storm, and Kerrid is not at Oruvel.
- **Ch3:** no stumble or catch at the shrine door, and no summon is shown there.
- **Ch5:** nobody hails Kerrid as a legend, and Toma doesn't recognise him.
- **Ch7:** no spawn reach the Bell, and no Order official presides.
- **Ch8:** nothing bound or machine-made is used against the storm.

## Consequences
- **Narrative (done in M1-NAR-09):**
  - act_outline: Prologue, Ch4, Ch6, Ch7, Ch8 and Ch19;
  - bible §5.1 (sea-law, name-boards) and §5.4 (Corrow);
  - characters: Sefir, Toma, Liss, Rhen and Kerrid;
  - voice_guide (Sefir's samples; the Ch15 long-speech slot);
  - decisions_log N-20;
  - glossary (appended);
  - color script notes for `prologue`, `ch06`, `ch07` and `ch19`;
  - a staging comment in `ch03_the_first_verse.dlg` (no line changes).
- **Cinematics:** the Prologue vigil and walk; the Ch4 boarding; Sefir's barge in Ch6; the Ch7 naming rite; the Ch8 evacuation.
- **Environment:**
  - `prologue/iskarra_dusk`: no fire prop. The seven positions are spread across the plaza, and Rhen's lantern is the practical.
  - `ch04/brightwater_ferry`: a derelict trader moored alongside, with a boardable deck.
  - `ch06/brine_shoals`: a channel wide enough for the Warden's barge.
  - `ch08/corrow`: the Fisher Stair and the wall-head above it, plus Liss's hoist rigged off a Watcher.
  - The zone count is unchanged.
- **Combat:**
  - the Spar-Wraith is fought on the derelict's deck, not the ferry's;
  - the Ch8 set-piece is a hold-the-stair defence (Narrative suggests an evacuation counter on the timeline) with no cannon actions;
  - the Ch7 story match is Oruvel's side, so Rhen dives and Toma doesn't play.
- **Art and Rendering:**
  - `prologue`: the note now reads seven figures apart, and one oil lantern;
  - `ch06`: the white barge on smoke-still water;
  - `ch07`: Sefir is out of the frame's note.
  - No light values change.
- **Audio:** the naming rite before the match wants a beat of silence in the crowd. That is a proposal.
- **Supersedes:** in decisions_log, N-01's "survives the Spar-Wraith" wording (the band is still earned on the Ch4 crossing) and N-12's "veteran's empty benches" (the side scene is now Oruvel's moorings, the same rite). In ADR 0016, the Ch19 row's "campfire" analogue wording describes the old Prologue staging. The Ch19 frame now repeats the vigil.

- 2026-10-23 Lead sign-off: accepted, including the accepted risks as reasoned.
- 2026-10-23 (Narrative, review-sweep-E): [0020](0020-kerrid-restaging.md), proposed, amends this ADR:
  - **Prologue row:** the line is no longer accepted here. With the human's approval (relayed by the Lead), it is replaced by "Everyone I'm going to tell you about is still here tonight. Remember that, later." The SPEC amendment is the Lead's.
  - **Ch5 row:** Kerrid's line is now "I held a stair for your mother once."
  - **Ch7 row:** the island-side shape is added as an accepted residual, and Oruvel's side does not win the cup.
  - **Ch6 row:** "I knelt beside your mother" is added as accepted, with a reason.
  - **Kerrid roster row:** its "Pass" covered only his introduction and props. His backstory, bond, face and ending order are re-staged in 0020.
