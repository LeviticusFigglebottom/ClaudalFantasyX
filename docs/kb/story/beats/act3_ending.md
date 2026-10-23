# Act III Ending Beat Sheet: Ch21 "The Heart" and the Ending

Owner: Narrative Director (M1-NAR-05). Reviewer: Cinematics (SPEC §12.3: does the staging serve the beat?).
Sources: [act outline Ch21 and Ending](act_outline.md), [N-16, N-17](../decisions_log.md) (M1-NAR-08), [bible §10](../bible.md) (the locked ending shape), [Vowbound §7 Kesh](../vowbound.md), [Sefir](../characters/sefir_aurane.md), [color script `ch21`, `ending_unbinding`, `ending_dock`, `post_credits`](../../art/color_script.md), [decisions_log](../decisions_log.md) N-01, N-04, N-11, N-14.

Written for the review-sweep-B finding that Ch21 and the Ending stack Kesh's release, a three-phase final boss, the Letting countdown, three goodbyes, the Kite landing, and Asha's failed song. Without a sheet, those would blur into one montage.

---

## 0. Rules for this sequence

1. **One goodbye per scene.** Each scene below says goodbye to exactly one person (or to one thing), or to nobody. No scene shares a goodbye, and no goodbye is cut against another.
2. **A rest beat between goodbyes.** Between the three family goodbyes (Kerrid, Imra, Dace) there is a short in-engine rest with no dialogue, so the player can breathe and each loss stays its own.
3. **The light tells the time.** After the Letting every mote rises (`glimmer_lift`, slow upward spirals). Every bound light in the world goes out in the same instant at H09, **the Kite's lamps and engines included** (SPEC §3.5, [N-16](../decisions_log.md)): the Kite flies the whole Ending dark, gliding on sail alone. The countdown needs no UI, and it is carried by three things: the sea-glow stepping down scene by scene (rule 4), the dead rising off the sea more thinly in each scene, and the Kite's slow descent toward the dark water.
4. **Light grammar is never broken here.** Up = released. Nothing drifts down or seaward after H09. The `sea_glow` ramps from 0.15 to 0.0 across E1–E5, in steps: **E1 0.15 → E2 0.11 → E3 0.08 → E4 0.04 → 0.0 during E5**, eased linearly through the rests between them (color script `ending_unbinding`). It is exactly 0.0 in E6.
5. **No gilt line** in Act III ([N-04](../decisions_log.md)). Asha's verse-sleeve unravels into rising motes during the Letting (art `asha.md` state S8), so it is gone in every Ending scene.
6. **SPEC §3.5 is locked:** the Undertow ends forever; every glimmer-light and lingering soul is released in the same instant, including Kerrid and Asha's mother (one last scene); Asha lives without her singing voice; Rhen loses his father for real and gets to say goodbye; the final image is Asha on a dock at night with the sea dark and the stars in it; post-credits, the first new oil lamp in a rebuilt city.

**Modes** (as in the [slice sheet](vertical_slice.md)): **P** playable, **C** letterboxed cutscene, **E** in-engine (no letterbox, minimal input). Minutes are a first-time player's.

---

## 1. Running order

| # | Scene | Mode | Min | Goodbye | Music cue | Grade |
|---|---|---|---|---|---|---|
| **Ch21** | | | | | | |
| H01 | The last layer opens | P | 4.0 | — | `heart_approach` | `ch21` (abyss) |
| H02 | Two lamps | C | 2.5 | — (withheld) | `heart_approach` → `silence` | `ch21` |
| H03 | Kesh | C 1.0 → P 6.0 → C 1.5 | 8.5 | **Kesh** | `kesh_first_voice` → `release_sting` | `ch21` |
| R1 | Seven bands | E | 1.0 | — | `heart_rest` | `ch21` |
| H04 | Sefir, phase 1: the Warden | P | 6.0 | — | `sefir_warden` | `ch21` |
| H05 | He takes the heart | C | 1.0 | — | `sefir_warden` → `sefir_heart` | `ch21` |
| H06 | Sefir, phase 2: the Undertow-heart | P | 7.0 | — | `sefir_heart` | `ch21` |
| H07 | Sefir, phase 3: the Letting | P | 5.0 | — | `the_letting` (diegetic) | `ch21` cross-fade to gold |
| H08 | Sefir lets go | C | 2.0 | **Sefir** (of Kesh) | `the_letting` (thinning) | `ch21` gold |
| H09 | The Great Unbinding | C | 2.0 | — (the world) | `the_letting` last phrase → `unbinding_swell` | `ch21` → `ending_unbinding` |
| **Ending** | | | | | | |
| E1 | Kerrid | C | 2.0 | **Kerrid** | `goodbye_kerrid` | `ending_unbinding` |
| R2 | Rest: the empty place | E | 0.75 | — | bed only (`ending_lift_bed`) | `ending_unbinding` |
| E2 | Imra | C | 2.5 | **Imra** | `goodbye_imra` | `ending_unbinding` |
| R3 | Rest: hands | E | 0.75 | — | bed only (`ending_lift_bed`) | `ending_unbinding` |
| E3 | Dace | C | 3.0 | **Dace** | `goodbye_dace` | `ending_unbinding` |
| R4 | Rest: the last motes | E | 0.5 | — | bed thins to nothing | `ending_unbinding` |
| E4 | The Kite comes down | E | 2.0 | — (the machines) | `silence` (wind, rope, water) | `ending_unbinding` |
| E5 | Nothing comes | C | 1.5 | **her voice** | `silence` | `ending_unbinding` (sea_glow → 0) |
| E6 | Final image: the dark sea | C | 1.5 | — | `ending_dock` | `ending_dock` |
| CR | Credits | — | 7.0 | — | `credits_suite` | black |
| E7 | Post-credits: the first lamp | C | 1.0 | — | `post_credits_lamp` | `post_credits` |

**Totals:** Ch21 **39.0 min** (28.0 playable, 11.0 cutscene/in-engine). Ending **14.5 min** before credits, plus 7 min of credits and the 1 min post-credits. From the last layer to the lamp is about **61.5 min**. The three family goodbyes take 7.5 min of it, with 2 min of rest around them (R2–R4).

**Cut order if it runs long:** shorten H01 to 2.5 (one corridor), trim H06 by a phase-2 sub-wave, compress H05 into H06's opening. **Never cut:** a rest beat, any goodbye, E5, E6, or E7.

---

## 2. Scene detail

### Ch21 "The Heart"

**H01. The last layer opens (P, 4 min).** After the Cage falls (Ch20), the last remembered room dissolves and the party walks a floor of held light toward the centre. *Staging intent:* everything in the frame drifts down and inward, toward the heart, and the party are the only things moving forward. One rail, no encounters: the walk is the threat. Far ahead, two lights stand close together. *Music:* `heart_approach`, a low drone with the Hush theme's first phrase played backwards, very slow.

**H02. Two lamps (C, 2.5 min).** Imra at the centre, her light holding the storm together, and Dace beside her, his hands in her light, keeping it whole. Dace can't turn or speak while he holds her. Rhen sees his father. *He walks, he doesn't run* (an answer to his Ch8 freeze). He stops an arm's length away because Kerrid's hand is on his shoulder. Sefir is already there, waiting, unhurried. **No goodbye here:** this is the withheld one, and the player should feel it held back. *Music:* `heart_approach` thins to `@music silence` on Sefir's first word. *Staging:* wide, then Rhen's face, then Dace's back (we don't see Dace's face until E3).

**H03. Kesh (C 1 → P 6 → C 1.5).** Sefir raises Kesh from the stones to stop them. The fight is as written in [vowbound.md §7](../vowbound.md): she fights at full strength because she wants them strong enough. **Goodbye: Kesh.** She lifts and doesn't look at him. *Staging intent:* in the release cutscene the camera stays on **Sefir's face**, which doesn't move, while her light rises out of the top of frame. We never cut to her. *Music:* `kesh_first_voice` (boss, all seven verse phrases in turn, one per element phase), then `release_sting`, the Vowbound release sting from Ch20, last and longest.

**R1. Seven bands (E, 1 min).** A save point (a dark Choir-stone). The party stands in silence. Asha looks at her full sleeve for the last time. One optional line per party member if the player talks to them, each under 10 words, none of them a goodbye. *Music:* `heart_rest`, the drone only.

**H04. Phase 1, the Warden (P, 6 min).** Sefir buffs, delays, and "settles" the timeline (freezes turn order: [sefir_aurane.md](../characters/sefir_aurane.md) battle notes). He talks during the fight, warmly and reasonably. *Staging:* he never moves his feet. *Music:* `sefir_warden`, a hummed congregation over strings, beautiful and airless (the Order hums).

**H05. He takes the heart (C, 1 min).** Sefir reaches past Dace into Imra's light and begins drawing the heart into himself. Dace holds on. *Staging:* the held motes reverse direction around Sefir, inward and down, the wrong way, faster. *Music:* `sefir_warden` breaks into `sefir_heart`.

**H06. Phase 2, the Undertow-heart (P, 7 min).** He draws on the party's Vowbound-adjacent glimmer (none is left to summon, since every Vowbound has been released). *Music:* `sefir_heart`, the storm's own note under rock-fusion percussion.

**H07. Phase 3, the Letting (P, 5 min).** Asha steps off the battle timeline and sings the Eighth Verse. Her verse is a countdown icon the party must protect. *Staging intent:* her voice is the music, and the score follows her. Over the countdown the palette rotates from cool held to warm released (color script `ch21` phase 3). The sleeve unravels from the cuff upward over the last 6 s. The verse ends on *tash* (let go). *Music:* `the_letting`, diegetic, Asha's voice leading. **Original melody** (SPEC §2): the first verse's phrase turned upward.

**H08. Sefir lets go (C, 2 min).** **Goodbye: Sefir's, to Kesh.** Kesh, already lifting, doesn't take his hand. He finally watches her go, and he lets her. Then he lifts too, and his last expression is relief. No speech longer than two lines. *Staging:* his reflection in the water ripples for the first time in the game (his revenant tell, undone). *Music:* `the_letting` thinning to a single held note.

**H09. The Great Unbinding (C, 2 min).** The last *tash*. Every mote in Maresh lifts at once. Six cutaways, each 3 to 4 s, no people in close-up and no goodbyes: Iskarra's lamp-columns go dark; a Hollowmere tide-wheel stops; the Tamsule Bell's light leaves it; the Sanctum's mirror basin goes dark and ripples for the first time in four hundred years; Lowlight's conduits empty upward; the storm wall comes apart into rising light. Then the Kite, in a last wide shot: its lamps go dark in the same instant as everything else, its engines stop, and it rides the storm's last updraft out into open night on sail alone, unlit. *Music:* `the_letting`'s last phrase, then `unbinding_swell`: full choir and orchestra for the only time in the game, and the Hush theme finally resolves upward.

### Ending

Staged on the Kite's dark deck as it glides in a long, slow, descending spiral over the open sea at night. Liss holds it aloft on sail alone, while the sea gives up its dead in slow spirals (color script `ending_unbinding`). The dead who were held come up with the light, and the three who matter come aboard. **Each farewell scene is lit only by the rising motes of the person leaving.** The Kite's lamps have been dark since H09. Other dead rise far off the rail and stay out of the key, and the sea-glow below is a background value that never lights a face.

**E1. Kerrid (C, 2 min). Goodbye: Kerrid.** He goes first, as the outline says: "Stand up straight. Your father slouched." *Staging intent:* a dry, plain goodbye, with gallows humour and no speech (voice guide). He fixes Rhen's collar the way he grabbed it at Corrow. As his motes lift, his own light throws **his shadow** across the deck and onto Rhen's feet, and for a moment the shadow is clearer than the man. He is there, for a moment, on the way out. The camera stays at Rhen's height. *Music:* `goodbye_kerrid`, a solo low string with a gamelan pulse, the walking rhythm of the pilgrimage, slowing to a stop.

**R2. Rest: the empty place (E, 0.75 min).** No dialogue. Rhen sits where Kerrid stood. Toma sits beside him, not touching. The player can only turn the camera. *Music:* `ending_lift_bed`, the drone and a faint high shimmer, no melody.

**E2. Imra (C, 2.5 min). Goodbye: Imra.** Imra, free of the heart, kneels in front of Asha. Hands and silence: almost no words (two lines at most, Imra's). Imra hums the first phrase of the **Velamir lullaby** ([N-11](../decisions_log.md)), the one she hummed every night, once, for her daughter. Asha doesn't try to join her. She listens, and holds on. (The failed song is E5's, and it must not be spent here.) *Staging intent:* a tight two-shot, mostly hands. Imra's face is lit by her own lift and Asha's by her mother's. We hold on their joined hands after Imra's light has gone out of them. *Music:* `goodbye_imra`. The score drops out completely, and Imra's unaccompanied hum is the cue. A single piano note enters only after she is gone.

**R3. Rest: hands (E, 0.75 min).** Asha's hands, still held out. Ysolde comes and takes them, the mother-in-all-but-name beat (asha_velamir.md), wordless. *Music:* `ending_lift_bed`.

**E3. Dace (C, 3 min). Goodbye: Dace.** With Imra gone, Dace's hands are free for the first time in eleven years, and he turns around. We see his face for the first time. He knows Rhen at once. The scene is the voice guide's Rhen with the jokes gone: Dace says goodbye, and **this time Rhen says it back**. That is the payoff of his whole arc, so it must be said aloud, plainly, and not cut away from. Dace sees the oil wick in his old lantern on Rhen's shoulder and is glad (N-02). *Staging intent:* a single slow push-in on the pair (a same-axis move, so a blend is allowed), then one reverse at the line "Goodbye, Dad." No other cuts. *Music:* `goodbye_dace`. Dace's current-song from Ch1 on plucked strings, and inside it, for four bars, the lullaby tune, the thing that tied two families together without either child knowing.

**R4. Rest: the last motes (E, 0.5 min).** The deck is empty of the dead. Only a few motes still rise off the sea, far below and much nearer than before. *Music:* the bed thins to nothing.

**E4. The Kite comes down (E, 2 min). No person's goodbye:** this is the cost to the Saltwrights. The Kite has been gliding dark since H09, and now the glide runs out. Liss, who has already said goodbye to Wenna (Ch20), brings it down onto the water by hand, with ropes and the sails Dace modelled on Virel. One player input: hold to take the strain with her. *Staging intent:* sweat, rope, and darkness, and a hard landing that everyone survives. Liss doesn't cry until it's down. *Music:* `@music silence`. Only wind, rope creak, and the hull meeting water.

**E5. Nothing comes (C, 1.5 min). Goodbye: her voice.** On the dark, floating Kite, Asha tries to sing, properly, for the first time since the Letting. She draws breath and **nothing comes**. Rhen doesn't comfort her with words. He sits beside her. The `sea_glow` reaches 0.0 during this scene, so the sea around them goes fully dark for the first time. *Music:* `silence`. This is the quietest scene in the game.

**E6. Final image: the dark sea (C, 1.5 min).** Haluna's dock at night (color script `ending_dock`; haluna.md H10 reversed). Asha at the end of the dock, alive, with a **second reach-band** on her forearm for the voyage she wasn't meant to come back from (N-01). The sea is completely dark, and the stars are reflected in it. **She draws breath for the tune, lets it go unsung, and smiles** ([N-14](../decisions_log.md)). She never sings or hums again, and the smile isn't for anyone else this time. Rhen's older voice-over returns from the dock: one or two lines, gentle, still a little funny (rhen_sallow.md Ending), ≤ 25 words each. *Staging intent:* one locked shot in **three-quarter profile from the dock's side** ([N-17](../decisions_log.md)), at her eye height (about 1.5 m) and about 3 m off her right shoulder. Her face is against the star-filled sea, so the breath, the unsung tune and the smile all read. No cut, no push. The stars do the work. *Music:* `ending_dock`, solo piano: the Hush theme's first phrase, which resolves at last. The instrument carries it, never a voice.

**CR. Credits (7 min).** *Music:* `credits_suite`, a suite of the game's themes, ending on the lullaby phrase on piano.

**E7. Post-credits: the first lamp (C, 1 min).** Oruvel rebuilt, pre-dawn blue hour. Someone uses **Mother Kell's wick** (Ch1) to light the first new oil lamp. It is the only warm light in frame (color script `post_credits`). No dialogue. *Music:* `post_credits_lamp`, a single low metallophone phrase from `haluna_dawn` and one struck match.

---

## 3. Requests to other roles

- **Cinematics (reviewer):** E1–E3 are each a single scene with one goodbye and a rest beat after it. Please check that the rests read as rests and not as dead air. They depend on the camera being free in E-mode.
- **Audio:** the cue ids above are proposals: `heart_approach`, `heart_rest`, `kesh_first_voice`, `release_sting` (shared with Ch20), `sefir_warden`, `sefir_heart`, `the_letting`, `unbinding_swell`, `goodbye_kerrid`, `goodbye_imra` (mostly silence plus a hummed phrase), `goodbye_dace`, `ending_lift_bed`, `ending_dock`, `credits_suite`, `post_credits_lamp`. Every melody is original (SPEC §2). `the_letting` and Imra's hum both need a voice decision (SPEC §16 Q4/Q5).
- **Combat:** H07's countdown (the Letting as a protected timeline entry); H06 runs with zero Vowbound available.
- **Art and Rendering:** the Kite's lamps going dark in H09 with everything else (§0 rule 3; there is no dimming curve); the stepped `sea_glow` (§0 rule 4) reaching 0.0 in E5, before E6; Kerrid's shadow from his own rising light in E1; the farewells keyed only by the leaving person's motes; Sefir's reflection rippling in H08; the E6 three-quarter frame on the dock.
- **Systems:** E4 needs one hold input inside an in-engine scene.
