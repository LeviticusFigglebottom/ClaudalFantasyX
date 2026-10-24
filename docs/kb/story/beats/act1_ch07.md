# Ch7 Beat Sheet: "The Tidecup" (Tamsule), story half

Owner: Narrative (M3-C07-01, the story half). Reviewer: Cinematics (SPEC §12.3).
**Split:** Narrative owns the story beats and cutscenes around the match. **A separate Lead agent owns the Reefball match's gameplay** (rules, controls, AI, tuning, the arena's play space). The boundary is §5, "Hand-off to the Reefball match".
Sources: [act outline Ch7](act_outline.md), [bible §5.1 and §5.3](../bible.md), [decisions_log N-12](../decisions_log.md) (the Bell and the naming rite), [N-20, N-22](../decisions_log.md), [ADR 0017](../../decisions/0017-act-one-restaging.md) (b) and its Ch7 watch, [ADR 0020](../../decisions/0020-kerrid-restaging.md) (h), [rhen_sallow.md](../characters/rhen_sallow.md) (Mother Kell, Tavi), [toma_okeru.md](../characters/toma_okeru.md), [color script `ch07`](../../art/color_script.md), SPEC §6.10. Format: [vertical_slice.md](vertical_slice.md).

**Arena form:** written for the human's default (STATUS: keep the sphere, differentiated as N-12 proposes): the **Tamsule Bell** is a Lit Age bronze bell hung mouth-down from a lacquered timber gantry; the water hangs inside its mouth as a slightly flattened drop, held still by bound glimmer in its ribs; a thin column weeps from the drop's lowest point into a **catch-pool**; players enter by swimming *up* the column; the ball is a woven **float**; a score is bringing it up to the ring at the drop's surface. If the human chooses the **Weir** instead, every beat below survives with the place-words swapped (the catch-pool becomes the sluice-steps, "up the column" becomes "down from the rim"), and §9 notes the shots that change.

Scripts: not written yet. The `.dlg` scripts and flag declarations are the second acceptance item of M3-C07-01, and this sheet is what they are written against (see the task Notes).

Seams: Ch6 ends at the shoal channel at dawn on day 4 with Tamsule on the horizon. Ch8 (M3-C08-01) opens at sea, or on Corrow's approach.

---

## 0. The chapter in one paragraph

Tamsule is holding the brightest festival in the game, and Oruvel's Reefball side has been waiting there a week for news of a town that no longer exists. Its captain, Mother Kell's grandson Tavi, finds Rhen in the crowd, and Rhen has to tell him that Kell couldn't swim. The side is a player short, because their youngest went home to look and hasn't come back. So Rhen dives in his place. Before the first match the two captains each name one person the sea has taken, and the whole Bell answers. Tavi names the whole town. Oruvel plays its opening round, win or lose, and then withdraws to go home and search what's left. The cup goes on without them. The player should finish the chapter having played a game for the dead, and having seen Rhen stand still for a loss for the first time, without a joke.

**Emotional line:** dazzle (the port) → joy, knocked flat (Tavi's face, then "Gran?") → a decision made in the open (Rhen dives) → warmth with a crack in it (the galleries; Liss's line hangs) → hush (the naming) → play (the match) → a quiet withdrawal → an afternoon that goes on as if nothing happened → a blessing for empty rings.

**What the chapter must deliver** (act_outline Ch7, ADR 0017 (b), ADR 0020 (h), N-12): Tavi finds Rhen and hears that Kell couldn't swim; the opening rite, with no Order official and with Tavi naming "Oruvel"; the match as Oruvel's opening round, uninterrupted; Tavi withdrawing the side; the cup won offscreen by Tamsule and mentioned once; Toma and Asha in the galleries; Liss's glimmer-tech remark with nobody answering; the moorings side scene.

---

## 1. Running order

One day. Minutes are the player's. **P** = playable, **C** = letterboxed cutscene, **E** = in-engine scene. **R** = the Reefball match (P, owned by the Reefball agent). Shot ids are proposals (§8, §10).

| # | Beat | Zone | Time | Mode | Min | Shots | Music | Emotional purpose | Flags set |
|---|---|---|---|---|---|---|---|---|---|
| B01 | **Into Tamsule** | `ch07/tamsule` river mouth | day 4, 10:30 | E | 1.0 | T01, T02 | `tamsule_port` | Dazzle. Gilded signs, a hundred languages, and a bronze bell the size of a hill with the sea hanging in it. | `ch07_arrived` |
| B02 | **Tamsule port** | `ch07/tamsule` floating market, stilt lanes | 10:40 | P | 5.0 | T03, T04, T05 | `tamsule_port` | A festival at full noise. Under it, one rumour: "Oruvel's side is still here." | — |
| B03 | **Tavi** | `ch07/tamsule` market boats by the Bell's gantry | 11:20 | C | 4.0 | T06, T07, T06 | `tamsule_port` (diegetic, distant) → `silence` → `tavi_kell` | Joy knocked flat. "Gran?" "She couldn't swim, Tavi." Then a decision: Rhen takes the empty place. | `ch07_met_tavi`, `ch07_told_tavi` |
| B04 | **The galleries** | `ch07/tamsule_bell` stilt galleries | 11:50 | E | 1.5 | R01, R02 | `bell_hum` under `tidecup_crowd` | Warmth with a crack in it. Toma's boyhood seat; Liss says the thing nobody says; nobody answers. | — |
| B05 | **The naming** | `ch07/tamsule_bell` catch-pool rim | 12:10 | C | 2.0 | R03, R04, R05 | `silence` (true silence) → the crowd's answer | Hush. Two captains, two names, one word from ten thousand people. The match is for the ones who didn't come up. | — |
| B06 | **The match** (Oruvel's opening round) | `ch07/tamsule_bell` the drop | 12:15 | **R** | ~10 (Reefball agent's estimate) | Reefball cameras | `reefball_match` | Play, for the dead. Nothing interrupts it. | `ch07_tidecup_played`, `ch07_tidecup_won` (record only) — set by the match's return, §5 |
| B07 | **After the Bell** | `ch07/tamsule_bell` catch-pool | 12:40 | C | 2.5 | R06, R07 | `tidecup_after` | A quiet withdrawal. "Win or lose, she'd have yelled at us the same." | `ch07_tavi_withdrew` |
| B08 | Tamsule, afternoon | `ch07/tamsule` | 13:00 | P | 3.0 | T03, T04, T05 | `tamsule_port` (afternoon) | The festival goes on as if nothing happened, because for everyone else nothing did. | — |
| B09 | *Side scene: The Empty Moorings* (optional) | `ch07/tamsule_bell` Oruvel's moorings under the Bell | 14:30 | E | 4.0 | R08, R09 | `oruvel_theme` (Ch1 cue, stripped), over `bell_hum` | Naming the boats, and then a boy. A blessing for empty rings. | `ch07_blessed_moorings`, `ch07_set_leaf_boat` |
| B10 | Leaving Tamsule | `ch07/tamsule` harbour | 15:40 | E | 1.0 | T08 | `tamsule_port` → `tidecup_after` (reprise) | The cup is mentioned once. Rhen looks east, after a boat. | — |

**Totals:** critical path **~30 min** (B01–B08, B10, with the match at ~10). With the side scene, **~34 min**. Split: **~18 min playable including the match (60%)**, 8.5 min cutscene, 3.5 min in-engine.

**Cut order if the chapter runs long:** B08 shrinks to the walk to the harbour (its barks move to B02). B04 loses Toma's seat and keeps Liss's line. B10 becomes one shot plus the boatman's line. **Never cut** B03's "She couldn't swim, Tavi.", the naming in B05, the match, Tavi's withdrawal in B07, or Liss's line.

---

## 2. Beat detail

### B01. Into Tamsule (E, 1 min)
- **T01:** a hired sailing barge (out of the shoals) comes in at the river mouth under the stilt city. Gilded lacquer signboards on every house-front, floating markets jammed hull to hull, banners in every side's colours. Above it all, the **Tamsule Bell** on its gantry, the drop of seawater hanging in its mouth, lit from within by steady bound light. The camera holds the Bell 3 s. Nobody comments.
- **T02:** they tie up. ~30 words. Liss, already sour: "Tidecup week. Every purse-cutter on the coast is here." Ysolde: "Then hold on to yours, Mistress Varrow." Rhen, looking up at the Bell, very quietly, to himself: "...Oruvel always came up for this."

### B02. Tamsule port (P, 5 min)
The town loop: the floating market (T03), the stilt lanes (T04), the gantry foot under the Bell (T05). **Systems on show:** shops (a Reefball outfitter selling floats and side-bands as accessories, a general trader), the inn, a save shrine, and a **Reefball board** NPC who explains the Tidecup's draw (the Reefball agent may use this NPC for a pre-match tutorial: §5).
**Barks** (~120 words):
1. *Market:* "Sorrin's side swims like eels. You watch them."
2. *Stilt lane:* "Hot year. Fast water. Good for the atoll sides." (No bark before B10 predicts or names the cup's winner.)
3. *Gantry foot:* "Oruvel's side is still here. A week now. Nobody's had the heart to ask them."
4. *Market, a child:* "If you bring the float up you get to ring the little bell! The little one!"
5. *Stilt lane, an old woman:* "Reefball's a rescue drill, that's all it ever was. You bring the float up like you'd bring up a body. People forget."
6. *Gantry foot, Ysolde (if the player talks to her):* "The Order sanctified the Bell in the third century. I have read the decree. It is very short."

Bark 3 is the hook: talking to anyone at the gantry foot after hearing it starts B03, or B03 starts when the player walks to the market boats by the gantry.

### B03. Tavi (C, 4 min)
**Tavi Orse** (new speaker): Mother Kell's grandson, about twenty-four, Oruvel's Reefball captain, in the side's colours (oil-black and brass). He grew up running between his gran's stall and the moorings; Rhen was in and out of that stall from eight. They are not brothers, but they had the same person.
1. **T06:** across three moored boats, a shout: "Rhen! Salt and stone. *Rhen!*" Tavi comes over the boats at a run and nearly knocks him into the water.
2. **The joke, before.** Rhen's run-on nervous burst (voice guide), ~30 words: "Tavi. You've grown a beard, or something died on your face, either way I'm not kissing it, get off—" Tavi laughs, holding him by both shoulders. This is the last joke Rhen makes in this beat.
3. Tavi, all at once: "Nobody's come. A week. No boats, no word, nothing. Pio took the *Gull* back to look and he hasn't—" He stops. Then: "Gran?"
4. **T07, the line.** Rhen's sudden short line when it matters (voice guide). Everyone on the Reaches knew Kell couldn't swim; this is how you say it there:
   > **Rhen:** She couldn't swim, Tavi.

   Hold, `@wait 2.0`. Tavi's face (`@face tavi grief`, slow). No music. The market noise goes on around them, which is the cruelty of a festival. Asha, behind Rhen, takes one step back to give them room (Cinematics: she leaves the frame's middle without leaving the frame).
5. **Choice** (Rhen):
   - "I was there." → Tavi: "...Did she know? That it was coming?" Rhen: "She was handing out wicks." *(Ch1's side scene: her trade's habit, "for luck". It is the truest thing he can tell him.)*
   - "I'm sorry." → Tavi: "Don't. Not you. She'd clout you for it."
   - If `ch05_boat_for_kell`, either branch adds: **Rhen:** "I sent her a boat at Pemakar. Too much wick. She'd have said so." **Tavi:** *(something between a laugh and the other thing)* "She would."
   Sets `ch07_told_tavi`.
6. **The empty place.** Tavi, pulling himself together the way a captain does: "We're a player short. Pio's place. The naming's at noon." Rhen doesn't wait to be asked:
   > **Rhen:** Give me his band.

   Tavi unties a woven **side-band** (an arm-band in Oruvel's oil-black and brass) from his own wrist, where he has been keeping it, and ties it on Rhen's bare right arm above the half-finished reach-band. Key item: **Pio's side-band**. *(This is the beat of Rhen standing still for a loss, rhen_sallow.md: he isn't running from this one. **ADR 0020 (h):** he isn't the side's star or a newcomer to the game; he's filling the place of a boy who hasn't come back.)*
7. Tavi notices Asha's vestments. Asha: "Asha. I'm so sorry about your grandmother." Toma: "Rhen is the Lady Cantor's sworn guardian." Tavi looks at Rhen for a long moment: "...Gran would've liked that." No joke. ~210 words in all. Sets `ch07_met_tavi`.
- *Pio:* the side's youngest, sixteen, a diver's boy from Oruvel's third mooring. In-game his fate stays unknown. **ADR 0020 (h)** calls his place "a dead boy's place", so the design truth is that he is not found (Ch18 shows his name hung with Oruvel's drowned, if the Ch18 owner wants it).

### B04. The galleries (E, 1.5 min)
**R01:** the stilt galleries inside the gantry, tier on tier around the catch-pool, packed. **R02:** looking up from the galleries into the Bell's mouth: the drop hanging there, perfectly still, caustics clipping to white (color script `ch07`).
- Toma and Asha find seats in the third gallery. ~70 words:
  > **Toma:** Haluna sat there. That gallery. We lost every match for six years.
  > **Asha:** You never told me you played.
  > **Toma:** I was large. They put me in the ring and asked me not to move.

  Asha laughs. Toma watches the column, and for a moment he is a boy (toma_okeru.md: he hasn't played since the Stillguard oath).
- **Liss**, beside them, looking up at the Bell's ribs, where the bound light sits in the bronze:
  > **Liss:** Rust it, the Bell's glimmer-made. You're all just *not looking* at it.

  (voice guide sample, verbatim.) **Nobody answers.** Toma looks up at the Bell and says nothing (toma_okeru.md Act II: his cracks start here). Asha says nothing either; `@face asha neutral`, held 1.5 s. She is a hearer, and the Bell **hums** to her (the `bell_hum` drone in the mix rises a little under her close-up, a steady tone with no breath in it). Ysolde turns a page. 2 s of crowd noise. Then a hush spreads from the pool: the captains are at the rim.
- **Kerrid** isn't in the galleries. One cutaway (R02's reverse, through a salt-glass panel): a big shape in a straw cape standing knee-deep at the end of the river moorings outside, facing the sea, his back to the Bell. *(He doesn't go under bound light he can't account for. Played as a man who doesn't like crowds.)*
- **Watch (ADR 0017 Ch7):** no Order official in any gallery shot; no Stillguard on the gantry; no Level banners over the pool. The Bell's "sanctification" is a decree Ysolde has read, not a presence.

### B05. The naming (C, 2 min)
**The rite (N-12):** before each Tidecup match the two captains stand at the catch-pool's rim, under the weeping column, and each names one person the sea has taken. **No one presides.** No Order official blesses or opens anything. It opens the way Reefball always has.
1. **R03:** the two sides in the water at the rim, the captains standing on the rim stones. The crowd falls silent from the pool outward, gallery by gallery, until there is **real silence** (Audio: no music, no ambience bed, only the column's thin weep into the pool).
2. **Sorrin's captain** (Ione Sabe, new speaker, a stocky atoll woman with reach-bands to the elbow):
   > **Ione:** Aldo Sabe. My brother.

   The whole Bell answers with one word, ten thousand voices low and together:
   > **Crowd:** Up.

   *(The response is ours: Reefball is a rescue drill, and a score is bringing the float up. "Up" is what you call to a diver who should be surfacing. The game never points out that it is also the right direction for the dead (bible §2). Played completely straight.)*
3. **R04, Tavi:** he doesn't speak for a moment. Then:
   > **Tavi:** Oruvel.

   A long hold (`@wait 2.5`). The galleries and the moored boats outside answer, louder than for Aldo Sabe, and ragged at the edges, because some people are crying:
   > **Crowd:** Up.

   In the third gallery Asha says it with them, quietly. Toma says it too. In the water Rhen says it, and looks up the column at the drop. If `ch05_boat_for_oruvel`: Rhen says it a beat before anyone else (a face cue; no extra line).
4. **R05:** the two sides go under and swim up the falling column into the drop. `<<event start_reefball ch07_tidecup_oruvel_sorrin>>`. **Hand-off to the Reefball match: §5.**

### B06. The match (R, ~10 min) — the Reefball agent's. See §5.

### B07. After the Bell (C, 2.5 min) — **identical whatever the result**
1. **R06:** the catch-pool after the match. The players come down the column and surface in the pool. Rhen and Tavi hang on the rim stones, breathing hard. The crowd noise is warm either way.
2. **The withdrawal.** The **pool-keeper** (new speaker: an old Tamsule woman who keeps the cup roll and the rim stones; not Order, and no robe of office) comes along the rim with the draw-slate. ~90 words in all:
   > **Tavi:** Oruvel withdraws. We've somewhere to be.
   > **Pool-keeper:** *(chalking it)* Oruvel's name stays on the roll.

   Then to Rhen, still in the water:
   > **Tavi:** Win or lose, she'd have yelled at us the same.

   *(It works both ways, which is the point: the cutscene never reads the result.)*
3. Rhen starts to untie the side-band. Tavi stops his hand: "Keep it till he wants it back." Rhen: "If you find anyone—" Tavi: "I'll hang a lamp." *(The Low Reaches custom of a lamp on a mooring line for the ones who didn't come up; Rhen says it to Liss in Ch6 B09.)*
4. **R07:** Tavi climbs out and walks along the rim to his side, and they go, wet, carrying their floats, through a crowd that parts for them. Rhen stays in the pool a moment longer, the band on his arm. He doesn't go with them. He gets out on the other side, where Asha and Toma have come down from the gallery. Asha says nothing; she hands him his jacket. (He chooses the pilgrimage without anyone asking him to. No line says so.)
- Sets `ch07_tavi_withdrew`.
- **Hard rule: B07's script contains no `<<if $ch07_tidecup_won>>` and no line that names a score.** The test that walks the chapter's `.dlg` should assert that no story script reads `ch07_tidecup_won` (§10, Systems).

### B08. Tamsule, afternoon (P, 3 min)
The festival goes on. The matches go on in the Bell above (crowd swells drift down). Barks change to after-match talk (~60 words): "Oruvel's side played for their town. Whole gallery stood up." / "Where'd they go?" "Home." / "Sorrin's through." (or "Sorrin's out." if Oruvel won; **this is the only place a result-dependent line may appear**, as ambient bark flavour, and it is optional: §5). Shops and inn are open. The moorings side scene is available through a marker on Tavi's boat at Oruvel's empty moorings.

### B09. Side scene (optional): "The Empty Moorings" (E, 4 min) — see §4

### B10. Leaving Tamsule (E, 1 min)
- **T08, 15:40:** the party boards a coastal trader bound north for Corrow. A roar comes down from the Bell. A boatman casting off beside them, to nobody in particular:
  > **Boatman:** That'll be Tamsule's cup, then.

  **This is the only mention of the cup's winner in the game** (ADR 0020 (h): "mentioned once in passing"). Nobody in the party reacts to it.
- Rhen, at the stern, looks east, where Tavi's boat went. If `ch07_blessed_moorings`, the camera also finds the moorings under the Bell as they pull away: the rings, and on Oruvel's last ring, Pio's side-band, tied. (Otherwise the band is still on Rhen's arm.) No line. Ch8 begins at sea.

---

## 3. Flags

To be declared in `game/data/flags.tres` with the M3-C07-01 `.dlg` work (the task's second acceptance item).

| Flag | Set by | Read by | Payoff |
|---|---|---|---|
| `ch07_arrived` | B01 | zone gating | — |
| `ch07_met_tavi` | B03 (end) | B08–B09 marker | — |
| `ch07_told_tavi` | B03 choice point | — | Ch18 (offered): Tavi at rebuilt Oruvel. |
| `ch07_tidecup_played` | **the Reefball match's return** (§5), win or lose | B07 trigger | — |
| `ch07_tidecup_won` | **the Reefball match's return**, on a win only | **rewards, records and the Memories gallery only. No story script may read it.** | The win reward (§5). |
| `ch07_tavi_withdrew` | B07 (end) | B08 barks, B09 marker | — |
| `ch07_blessed_moorings` | B09 (end) | B10 shot; Ch18; Ch20 | Ch18 Tamsule revisit (offered): Oruvel's boats tied up under the Bell again. Ch20's Reefball-crowd layer (offered to the Ch20 owner): Oruvel's drowned watching from these moorings, with Kell among them. |
| `ch07_set_leaf_boat` | B09, if `ch05_kept_leaf_boat` | — | Consumes the Pemakar leaf-boat key item. |

---

## 4. The optional side scene: "The Empty Moorings" (B09)

**Where:** Oruvel's moorings, under the Bell's skirt on the river side, where Oruvel's boats always tied up to watch: six empty iron rings in the timber, in the Bell's shade, with the drop's bound light falling on the water around them (R08, R09). **When:** B08, through a marker on Tavi, who is loading his boat to leave. **Length:** 4 min, ~170 words. Speakers: `tavi`, `asha`, `rhen`.

**Beats:**
1. Tavi, to Asha, awkward: "Would you bless them? The moorings. Gran would want it done by somebody proper." Asha: "I'm not a priest, Tavi." Tavi: "You're the Cantor." Asha, gently: "Then I'll do it the way we do it at home."
2. **The naming again.** She asks them to name what tied up at each ring. Tavi names the boats (the *Gull*, the *Second Mooring*, Kell's *Wicklight*...). Rhen names the people who sailed them. Asha kneels at each ring, touches the iron, and says each name back, once. No song: Cantors sing only the Hush, and this isn't that.
3. **The last ring.** Tavi can't name it. It was the *Gull*'s, the boat Pio took home. Rhen says it for him: "Pio." A long beat. Tavi: "...Yes. Pio." Rhen unties the side-band and ties it to the ring. *(Naming him with the others is accepting what "hasn't come back" means. It is the scene's whole weight, and it is Rhen who does it.)*
4. Asha's blessing, in the Low Reaches words, spoken: "Salt and stone keep you. Come up when you can."
5. **If `ch05_kept_leaf_boat`:** Rhen takes out the folded Pemakar boat he has carried since Lanternfall and lights its own wick from his lantern's burner (never Kell's wick: ADR 0022 sweep-H watch). He sets it on the water at the *Wicklight*'s ring. It turns once in the eddy and drifts out, down the river mouth toward the sea. Asha watches it go and says nothing (it rhymes with Ch5 B04's motes following the boats down). Sets `ch07_set_leaf_boat`.
6. Tavi: "Thank you." He goes. **Kerrid** is knee-deep at the far end of the moorings, back to them, watching the river mouth; he doesn't turn. No line.

**Rules:** no jokes. Asha leads nothing but the naming, and the naming belongs to Reefball, not the Order. No more than four lines from anyone in a row.
**Payoff:** `ch07_blessed_moorings` (B10's shot of the band on the ring; Ch18, Ch20 offered).

---

## 5. Hand-off to the Reefball match

**This section is the contract between Narrative and the Reefball agent.** Everything inside the match is theirs. Everything outside it is Narrative's.

### 5.1 The beat that starts the match
- **B05 "The naming", its last line.** The cutscene ends on the two sides going under, with `<<event start_reefball ch07_tidecup_oruvel_sorrin>>` as its final event. (The event `start_reefball` doesn't exist yet; it is requested from Systems, modelled on `start_battle`, §10.)
- **Before B05:** the Reefball agent may run a **pre-match tutorial** through the Reefball board NPC in B02 (the "Reefball board" bark area), or as an optional prompt at the B04 → B05 transition. It must not sit *between* the naming and the match: the naming leads straight into play.
- **Save:** the game auto-saves (ADR 0018's policy) at the end of B04, so the naming is never replayed on a reload.

### 5.2 What the match receives
| Input | Value |
|---|---|
| Match id | `ch07_tidecup_oruvel_sorrin` |
| Kind | The **story match**: simplified, turn-paused and tactical (SPEC §6.10). Its round is Oruvel's opening round of the Tidecup. |
| Home side | **Oruvel**, captain **Tavi Orse**, with four Oruvel players (proposed names: Brann Ollo, Mae Ketter, Dovic Saan, Tull Arro) and **Rhen in Pio's place**. Side colours: oil-black and brass. Side size is the Reefball design's; if it is smaller than six, drop names from the end of the list, never Tavi or Rhen. |
| Rhen | The player's Rhen, mapped to Reefball attributes from his current battle stats and level (the mapping is the Reefball agent's). He wears Pio's side-band (cosmetic). |
| Party | **No other party member plays.** Toma doesn't play (ADR 0017 (b)). Asha, Toma, Liss and Ysolde are in the third gallery (crowd cameras may find them); Kerrid is outside. |
| Away side | **Sorrin**, an atoll side from the Low Reaches, captain **Ione Sabe**. Quick swimmers ("swims like eels", B02 bark). **Not Tamsule**: Tamsule must still be in the cup to win it offscreen. |
| Arena | `ch07/tamsule_bell`, the drop, under the `ch07` grade (inside the Bell, caustics may clip to white). |
| Story flags readable by the match | None needed. Optional: `ch05_boat_for_oruvel` for one crowd bark. |
| Difficulty intent | A first-time player should usually win (about 60–75%), and a loss must never feel like failure. The Reefball agent sets the real tuning; this is the story's intent, not a band. |

### 5.3 What happens during the match
- **Nothing interrupts it** (ADR 0017 Ch7 watch). No spawn, no story cutscene, no Order presence, no rescue in the galleries, no mid-match dialogue scene. A halftime break, if the rules have one, is the match's own and carries no story beat.
- **Barks Narrative supplies** (optional; the Reefball agent fires them on its own events; ~40 words, all neutral to the result):
  - Kick-off, Tavi: "For her. Go."
  - Oruvel brings the float up, crowd: "Up!" (the naming's word, as a cheer)
  - Sorrin scores, Tavi: "Again. Again."
  - Rhen's first score, Tavi: "Kell's boy!" (once only)
  - The final whistle, either way, Tavi: "That's it. That's us."
  - If `ch05_boat_for_oruvel`, a gallery voice at kick-off: "Oruvel! Oruvel!"
- No line in the match may mock the dead, Sorrin, or the rite.

### 5.4 What the match returns
| Output | Meaning |
|---|---|
| `result: win \| loss` (a draw, if the rules allow one, is reported as `loss` for rewards) | **A reward only.** It **never branches the story.** |
| Always: set `ch07_tidecup_played = true` | B07 can begin. |
| On a win only: set `ch07_tidecup_won = true` | Read by rewards, records and the Memories gallery. **No story script reads it** (enforced by a test, §10). |
| Reward on a win | The **Oruvel Float** accessory (proposal: a woven float charm in oil-black and brass; its flavour text: "Brought up, once, for the ones who didn't come up."), plus lume. |
| Reward on a loss | Lume only (a smaller amount). The Oruvel Float becomes available again in the Act III league, if it is built, so nothing is missable for good. |
| Either way | The Reefball codex entry and the Tidecup Memories scene unlock. |
| No retry | The story match is played once. A loss ends the round, as a win does (Tavi withdraws either way). There is no "play again" prompt. A player who wants the win reloads the B04 autosave, which is their choice and costs nothing in story. |

### 5.5 The beat that resumes
- **B07 "After the Bell"** starts on the match's end in both outcomes, opening on R06 (the catch-pool, players surfacing). Its text and staging are identical for a win and a loss (B07's hard rule).
- **The only result-aware story text** allowed anywhere in the chapter is one optional ambient bark in B08 ("Sorrin's through." / "Sorrin's out."). If the Reefball agent or Systems would rather keep even that out, cut it; nothing depends on it.

---

## 6. Music cues

| Cue id | Beats | Kind | Brief |
|---|---|---|---|
| `tamsule_port` | B01, B02, B08, B10 | Town bed, loop | The most festive bed in the game: gamelan-like percussion, brass band, crowd, a melody that keeps modulating up. An afternoon variant, a little tired, for B08. |
| `tavi_kell` | B03 (from "She couldn't swim") | Cutscene score | Solo piano, very sparse, entering only after the line's hold. It quotes Ch1's Oruvel town theme (`oruvel_theme`, M3-C01-01's id) in two notes and doesn't finish the phrase. |
| `tidecup_crowd` | B04 | Ambience | A packed bowl of people under a bronze roof, the column's weep, a drum somewhere. |
| `bell_hum` | B04, B09 | Ambience layer | **The sound of bound glimmer:** a steady tone with no breath and no beating. It should be the same family as Ilun's chamber (`shell_shrine_interior`'s bound element), so the player's ear links the Bell to the Saints without being told. It rises under Asha's close-up in B04. |
| `silence` | B05 | Reserved | **True silence** at the naming: only the column's thin weep into the pool. Then the crowd's "Up." (a diegetic crowd recording, low, together). |
| `reefball_match` | B06 | Minigame loop | The Reefball agent's, with Audio. SPEC §9 allows some rock and fusion here. |
| `tidecup_after` | B07, B10 | Cutscene score | Warm strings over the crowd, unresolved, ending on a held note. |
| `oruvel_theme` (reprise) | B09 | Reprise | Ch1's Oruvel town theme, stripped to one flute, over `bell_hum`. |

**SFX:** `column_weep` (the drop weeping into the pool), `float_ring_bell` (the little bell at the scoring ring), `crowd_up` (the naming's answer; and a cheering variant for the match), `mooring_ring` (iron, touched).

---

## 7. Who is where (for Cinematics and the crowd system)

| Beat | Rhen | Asha | Toma | Liss | Ysolde | Kerrid |
|---|---|---|---|---|---|---|
| B03 | with Tavi | behind Rhen, then a step back | beside Asha | at a stall, off-frame | off-frame | off-frame |
| B04 | going down to the pool | third gallery | third gallery | third gallery | third gallery, reading | outside, knee-deep at the river moorings |
| B05–B06 | in the water | third gallery | third gallery | third gallery | third gallery | outside |
| B07 | the pool | comes down to the rim | comes down to the rim | the rim | the rim | outside |
| B09 | the moorings | the moorings | at the boat, off-frame | off-frame | off-frame | knee-deep at the far end, back turned |

---

## 8. Camera shots by beat

Shot ids are proposals for Environment's `tamsule.md` (T: the port) and `tamsule_bell.md` (R: the Bell). Cuts between setups, blends on one axis only.

| Beat | Shots, in order | Notes for Cinematics |
|---|---|---|
| B01 | T01 → T02 | T01 from the water at the river mouth: signboards in the lower third, the Bell filling the top half, held 3 s. |
| B02 | T03, T04, T05 | Rail cameras. T05 looks up the gantry to the Bell's skirt. |
| B03 | T06 → T07 → T06 | T06 a wide across moored boats for Tavi's run. **T07 is the line**: a two-shot, Rhen frame-left in three-quarter back, Tavi frame-right facing camera, so his face carries the news; held through the wait. Back to T06 for the side-band, which is an insert. |
| B04 | R01 → R02 → R01 | R02 looks up into the drop; its reverse through a salt-glass panel is Kerrid's cutaway. Asha's 1.5 s close is inside R01's axis. |
| B05 | R03 → R04 → R05 | R03 wide on the pool and rim, both sides in the water, the galleries rising behind. R04 a close on Tavi for "Oruvel." with the column behind him. R05 from inside the column looking down as they swim up into it (the hand-off frame). |
| B07 | R06 → R07 | R06 at water level in the pool. R07 follows Tavi's side out through the crowd, then holds on Rhen in the water. |
| B09 | R08 → R09 | R08 a wide on the six empty rings in the Bell's shade, bound light on the water. R09 low at the rings for the naming, with inserts on Asha's hand on the iron and the band being tied. |
| B10 | T08 | From the trader's stern, looking back at Tamsule and the Bell. |

---

## 9. Word counts

| Beat | Words (budget) |
|---|---|
| B01 | 30 |
| B02 barks | 120 |
| B03 | 210 |
| B04 | 90 |
| B05 | 30 |
| B06 match barks (Narrative's) | 40 |
| B07 | 90 |
| B08 barks | 60 |
| B09 side scene | 170 |
| B10 | 20 |
| **Total** | **~860 written, ~700 on a typical path without the side scene** |

At ~30 critical minutes, Ch7 is about 1.7% of a 30 h main story: a fair share of **670–1,000 words**. In band.

---

## 10. Requests to other roles

### The Reefball agent (Lead)
1. **The hand-off in §5**, as a contract: the start event and match id, the inputs (sides, Rhen's mapping, no other party member, Sorrin not Tamsule), no interruption, the optional barks, the returns (`ch07_tidecup_played` always, `ch07_tidecup_won` on a win only, reward-only), no retry, and B07 resuming in both outcomes.
2. Please confirm the **side size** (so the Oruvel roster in §5.2 can be trimmed), whether the rules allow a **draw**, and where the **pre-match tutorial** sits (B02's board NPC, or the B04 → B05 transition, but never between the naming and the match).
3. The **arena's play space** is yours; the naming's rim and the catch-pool (R03, R06) are shared with the story cameras, so please keep the rim stones and pool where N-12 puts them.

### Environment
4. **`ch07/tamsule` and `tamsule.md`.** Kit "Tamsule stilt": timber stilt houses, woven awnings, **gilded lacquer signboards** (a decal and mesh set in a hundred scripts; no real-world script copied), floating-market boats packed hull to hull, stilt lanes, the river mouth, the harbour for B10. Shots T01–T08.
5. **`ch07/tamsule_bell` and `tamsule_bell.md`** (N-12 form): the Bell hung mouth-down from a lacquered timber gantry centuries in the building; the drop; the weeping column; the **catch-pool** with its rim stones; the stilt galleries (tiered, with a "third gallery" seat for Haluna's old side); salt-glass panels for views out; the scoring ring at the drop's surface with its little bell; **Oruvel's moorings** under the Bell's skirt on the river side (six iron rings in a timber staging, in shade). Shots R01–R09. **If the Weir form is chosen:** R02–R05 and R08 change (a bowl, sluice-steps, the rim galleries), and the beats keep their words.

### Art and Rendering
6. **Color script `ch07`:** confirm the noon frame for B01–B07. Requests: a `ch07_afternoon` sub-frame (about 15:00, for B08–B10) and a `ch07_bell_shade` sub-frame for B09 (the moorings in the Bell's shadow, keyed by bound light from the drop above and bounce off the water).
7. The **drop's bound light** (`glimmer_bound`, energy 1.8): perfectly still, moving only when bodies move the water (N-12). Nothing in the Bell drifts.

### Character Art
8. **Tavi Orse** needs a face rig (B03 and B07 are close-ups): mid-twenties, broad, sun-dark, reach-bands on both forearms, Oruvel's side colours (oil-black and brass), a captain's knot in his hair. **Ione Sabe** (Sorrin's captain), the **pool-keeper** (an old Tamsule woman with chalk on her fingers and the draw-slate), the **boatman**, the Oruvel side (four players), the Sorrin side, and a large mixed festival crowd (at least three regional dress sets).
9. **Pio's side-band** (prop and accessory mesh, on Rhen's right arm).

### Combat
10. **Ch7 has no foes** (confirmed). No encounter tables in `ch07/*`.

### UI
11. The Reefball result screen shows the result and the reward, then hands straight to B07, with no "retry" option (§5.4). Key items: `pio_side_band` (given in B03, removed in B09 if tied to the ring), and the Pemakar leaf-boat consumed in B09.

### Audio
12. The cues in §6, especially the **true silence** and the crowd's **"Up."** at the naming (ADR 0017 asked for a beat of silence in the crowd), and **`bell_hum`** as the shared sound of bound light.

### Cinematics (reviewer)
13. **Watches** (ADR 0017 Ch7, ADR 0020 (h)): no Order official, Stillguard or Level banner anywhere near the pool; no spawn reaches the Bell; nothing interrupts the match; Rhen isn't framed as a star (Tavi's side is the subject, and Rhen is one of five); B07 is identical in both outcomes; the cup's winner is mentioned once, in B10.
14. B03's T07 hold on Tavi's face, and Asha's step back. B04's silence after Liss's line. B05's silence.

### Systems and Tech
15. **A new dialogue event `start_reefball <match_id>`** in `events.json`, modelled on `start_battle`: hand off to the Reefball match once the scene ends, and resume the chapter flow at B07 on its return.
16. **A test** (with the `.dlg` work): no story `.dlg` reads `ch07_tidecup_won`.
17. **New speakers:** `tavi` (CHAR_TAVI), `ione` (CHAR_IONE), `poolkeeper` (CHAR_POOLKEEPER), `boatman` (CHAR_BOATMAN), and `crowd` (CHAR_CROWD, for the naming's answer: the name box shows nothing, or "The Bell").
18. **Grades:** `ch07`, `ch07_afternoon`, `ch07_bell_shade`.

### Ch1 owner (M3-C01-01)
19. **Seams:** Oruvel's side left for Tamsule a week before the storm, so Tavi and the four players aren't in Ch1's Oruvel. Pio was there, and went back. Kell's boat is the *Wicklight* (if Ch1 names it otherwise, use Ch1's name). `oruvel_theme` is the id this sheet assumes for Ch1's town cue.

### Lead
20. **Glossary rows:** the naming (the Tidecup's opening rite) and its answer "Up."; the side-band; the pool-keeper and the cup roll; Tavi Orse; Pio; Sorrin (an atoll side) and Ione Sabe; the *Wicklight*.
21. The cup's offscreen winner is Tamsule's own side (ADR 0020 (h)), mentioned once in B10.
