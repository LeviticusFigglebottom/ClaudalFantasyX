# Narrative Decisions Log

Small canon calls that Narrative owns: answers to other roles' open questions and staging rules for story content. They are too small for an ADR, or they don't change the spec. Anything that binds more than one role's *work* is flagged for the Lead to fold into an ADR (CLAUDE.md §6). Entries are append-only. To change an answer, add a new dated entry that supersedes it.

---

## 2026-10-22 (narrative-stream-2, M1-NAR-02): Art's open questions (docs/kb/art/README.md)

### N-01. Asha's first reach-band: yes, earned on the Ch4 crossing and shown from Ch5
- **Answer:** approve Art's proposal. Asha earns **one** band, on her left forearm, offscreen after the Brightwater ferry survives the Spar-Wraith. Toma inks it, since he carries Haluna's ink, and it's shown from Ch5. In Ch5, one line acknowledges it (Rhen notices; Asha: "My first. Toma's hand shook."). She earns **a second band only in the ending** (the dock shot), for the voyage she wasn't meant to come back from.
- **Why:** reach-bands count voyages *survived* (bible §5.1), and a Cantor's pilgrimage is the voyage nobody expects her to survive. One band all game says so without a word. The second band in the last shot is visible growth (pillar 5) that pays off pillar 6: she lost her voice but kept her life, and her arm records it. Art's generator already takes a band count, so this costs two parameter values.

### N-02. Rhen's lantern burns oil, not bound glimmer
- **Answer:** **oil.** It is a Saltwright-made brass and salt-glass housing that Dace deliberately fitted with an ~~oil wick~~ (**corrected 2026-10-23 by M1-NIT-01**, ADR 0022 sweep-J note: **oil burner**; "wick" is Kell's gift alone). The flame uses `oil_lamp`, never `glimmer_bound`, and it does **not** go dark at the Unbinding.
- **Why:**
  1. In Ch1 the lantern is the right light in the drowned tower against the held cyan motes, which is the player's first lesson in the color language (color script Ch1). If it were bound, that lesson would invert.
  2. Oil is the last light the game shows (color script rule 4, the post-credits lamp). Rhen carrying honest light all game is what that ending rhymes with.
  3. It gives Dace a wordless character note: a wright who could have bound his own lamp and chose not to. Liss reads the housing as Saltwright work in Ch6 and will notice the ~~wick~~ (**corrected 2026-10-23 by M1-NIT-01:** oil burner). That's a scene seed.
  4. Asha's stillness at the lantern in Cutscene A is *recognition* (she saw ~~it~~ ~~on her mother's guardian~~ when she was seven; **corrected 2026-10-23 by N-23:** on the stranger who brought her mother's comb home to Haluna; **corrected again 2026-10-23 by N-25:** what she saw was its **twin**, the second lamp of Dace's pair, so she recognises the make, not this lamp), not her hearing someone inside it. That keeps the Dace mystery human.

### N-03. The wake-shell wall stands at the causeway head: confirmed
- **Answer:** approve Art's placement. The wall at the Haluna end of the Saltgrass Causeway **is** "the shrine wall" of bible §4 (the Pilgrim's Wake). In canon it is the Shell Shrine's *outer wall*, begun on the village side so the names can be visited and washed at any tide (the islet is reachable only at low water). Asha's shell is set there at the Ch4 wake. The Ch2 side scene happens there (H08).
- **Why:** every Cantor's name sits where the pilgrimage begins and faces the path she walked away on (pillar 3). Keeping it in the Haluna zone lets the optional side scene stay optional without a tide gate, and Ch18's Haluna revisit can show the wall as the village's first open grief-site. No bible text changes; the bible never located the wall.

### N-04. The gold lash stroke: approved, as an Order mark, never worn in Act III
- **Answer:** approve, with a meaning attached. In-world it is the **gilt line**: a Tender paints it on a Cantor before an **Order** rite "so the dead can find her". It is worn at the Ch9 Ebbing, the Ch13 Sanctum binding, the Ch14 wedding, and the Ch16 Choir. It is **not** worn in the vertical slice (the Shell Shrine is a village temple with no gold; haluna.md §3.3). At the Choir, after she refuses Sefir, Asha wipes it off with the heel of her hand (a Cinematics beat), and it never appears in Act III, at the Letting, or in the ending.
- **Why:** gold is the Order's color (no Order gold outside the chapel; gold under 5% of the frame), so gold on her face is the Order dressing her for its purpose. Wiping it off is a silent, visible version of "No, High Warden. I won't." It costs Character Art nothing new (it's already a mask layer) and gives Cinematics one strong gesture. *New glossary term:* **gilt line**.

---

## 2026-10-22 (narrative-stream-2, M1-NAR-02): slice staging calls

### N-05. The Vowbound in their temples read as bound light
- **Answer:** Ilun in his chamber (S08), and when summoned (C10), uses the **bound** treatment: `glimmer_bound`, steady, never drifting. He turns to rising `glimmer_lift` only at his Ch20 release. The same applies to every Vowbound.
- **Why:** they *are* bound dead (vowbound.md). If the player's own summons share the stillness of the Lit Age machines, the Act II truth is something they have been looking at since Ch3, which is what "learned, never told" means (color script rule 1). *Cross-role:* Art and Rendering should confirm, and the Lead may fold it into the glimmer-meaning ADR suggested in art/README.md.

### N-06. The light off Asha at sunset is released light
- **Answer:** the motes that lift off Asha's skin after the binding (S09) are a little of Ilun's light that touched her and lets go. They use `glimmer_lift` in slow upward spirals, as color script `ch03` says. Nobody comments on why they rise. It is the game's first released light.
- **Why:** it plants, at the slice's emotional peak, that light leaving Asha goes *up*. That is exactly what her Letting does to the whole world in Ch21.

### N-07. The Drownbell comes after the verse, not before
- **Answer:** the beat order follows act_outline: Cutscene B at sunset (18:05), then the Drownbell on the causeway at about 18:15 as the tide comes in. The verse's toll is what calls it.
- **Why:** the most beautiful moment in the slice draws its danger (pillar 2), and the boss's Ilun phase only makes sense after the binding. *Cross-role:* haluna.md times `ch03_boss` at 17:30. Narrative asks Art to re-time it to ~18:15 (vertical_slice.md §9).

### N-08. Imra sang the first verse from the Shell Shrine door when Asha was seven
- **Answer:** Asha heard her mother sing the first verse toward home from the shrine door, and hum it the night before she left. She had forgotten it until Ilun "gave it back". ~~Dace learned it from Imra on the pilgrimage, so both children were sung to sleep by the same verse.~~ **Corrected 2026-10-23 by N-11 (below):** Dace never came home from that pilgrimage, so he can't have learned it there. It is a Velamir family lullaby that Imra hummed long before she was named, and Dace heard it from her years earlier at Haluna. Both children were still sung to sleep by the same verse.
- **Why:** it gives Asha her own recognition in Cutscene B, so the scene is a meeting of two griefs, not just Rhen's. It is consistent with rhen_sallow.md (as corrected by N-11) and with the custom that Cantors sing and everyone else hums.

---

## 2026-10-23 (narrative-stream-3, M1-NAR-05): review-sweep-B fixes

### N-09. The Vowbound element order no longer follows the inspiring game's temple sequence
- **Answer:** the elements are reassigned, and the temples, chapters, and the Cantors' stories stay where they were.

  | Ch | Vowbound | Temple | Was | Now |
  |---|---|---|---|---|
  | 3 | Ilun | Shell Shrine, Haluna | Water | Water (slice, unchanged) |
  | 5 | Kahre | **Ashcrown**, Pemakar (was Ember Terrace) | Fire | **Lightning** |
  | 8 | Virel | Coilspire, Corrow | Lightning | **Fire** |
  | 11 | Nhoa | Lowlight, Sunken Vey | Glimmer | Glimmer |
  | 12 | Hesk | Cloudloom, Ullar Heights | Ice | **Holy** |
  | 13 | Ethren | Sanctum of the Level, Ansedra | Holy | **Ice** |
  | 16 | Kesh | the Drowned Choir | all six | all six |
- **Why:** the old run (a fire temple second, lightning third, an ice temple, the holy city's own Saint, then the edge of the world) was the inspiring game's order almost step for step. Mechanics are free, but a sequence is expression (SPEC §2). Each new element is earned by its place: Pemakar's caldera still breathes ash, and ash-plumes breed dry lightning, so a smith's hammer-crack becomes thunder. Corrow has kept a storm-beacon burning on Coilspire for nine hundred years, so Wenna's signal-kite flies alight. Holy goes to Ama Quillo, whose light is the truth held up to be read, in the high passes where the dead lift fastest. Ice goes to the Order's own Saint: the Sanctum's basin is held so still that it freezes in the tropics. That is the Order's creed made visible, and a clue (pillar 2).
- **Kept on purpose:** a Vowbound at the Drowned Choir. The Choir is spec-mandated (SPEC §3.2), and Kesh is the story's thesis. The Ansedra Saint stays too, because Ysolde's arc needs Corran there, but it is no longer Holy and no longer fifth.
- **Cross-role:** Combat (element and status tables: Kahre lightning, Virel fire, Hesk Holy plus cleanse and Regen, Ethren Ice plus Slow, Stop, and wards), Character Art (Asha's S2/S3 band wording is updated in `art/characters/asha.md`), Environment (`ch05/ember_terrace` → `ch05/ashcrown`), Audio (the slice's skipping rhyme now counts "two for the ash"). Glossary rows for the Vowbound and the temples need the Lead.

### N-10. Sefir's goal is renamed **the Long Stillness**
- **Answer:** Sefir's goal is **the Long Stillness**: the sea held still forever, with himself as its heart. The old two-word name was a one-word swap of a Calm compound already on the banned list, and it is now on `tools/banned_terms.txt` too. **Last Calm** (the Order's promise) stays, as the Order's own phrase. Don't coin any other Calm compound.
- **Why:** "Stillness" is the Order's own vocabulary (the Still Water, the Stilling, "Be level. And still."), so the antagonist's dream sounds like his church's creed taken to its end. That is exactly what it is. Updated: bible §11, `characters/sefir_aurane.md`.

### N-11. The first verse is a Velamir family lullaby, and Dace ~~knew Imra~~ heard Imra hum it before she was named (heading corrected by N-24)
- **Answer:** an earlier Velamir Cantor sang the first verse toward home from the Shell Shrine door, and the women of the line have hummed its tune as a lullaby ever since, without the words. Imra hummed it as a girl, long before she was named. ~~**Dace** met her~~ **Dace** heard her (**corrected 2026-10-23 by N-23:** he never learned her name) years before Rhen was born, as a young wright trading salvage along the Low Reaches and putting in at Haluna. He heard her hum it, took the tune home to Oruvel, and hummed it to Rhen every night until he left. ~~That old friendship is also why he went with her as a guardian in 1001.~~ (**Withdrawn by N-23:** there was no friendship and no guardianship; they met only on the Corrow stair in 1001.) Asha was hummed it every night until she was seven, heard it sung once from the door, and forgot it until Ilun gave it back.
- **Why:** N-08 had Dace learn it "on the pilgrimage", but he never came home from that pilgrimage, and he hummed it to Rhen before it. The slice's central reveal depends on this, so it has to hold. Supersedes N-08's last sentence. Updated: bible §6, `characters/rhen_sallow.md`, `characters/asha_velamir.md`, `vowbound.md` §1, and ch03's source comments and line 053.

### N-12. The Reefball arena: what makes ours ours (a note for the human's call)
SPEC §6.10 mandates "a suspended sphere of water", and Cinematics flagged that as the inspiring game's signature arena image. The form is **not** changed. It is the human's call (STATUS blockers). The bible and the color script still describe the sphere.
- **If the sphere stays,** these things make it ours:
  - *Construction:* it is not a floating orb over an open stadium. The Tamsule Bell is a Lit Age bronze bell **hung mouth-down** from a gantry of lacquered timber that Tamsule has added to for centuries. The water hangs inside the bell's mouth as a slightly flattened drop, never a perfect sphere. It weeps a thin column from its lowest point into a catch-pool where children swim. Players enter by swimming *up* that falling column. Crowds watch from stilt galleries and moored boats, and at night they watch through the bell's salt-glass panels from outside.
  - *How it's held:* by the dead. The bell's ribs are lined with bound glimmer (`glimmer_bound`), so at rest the water is perfectly still, with no ripples, and it moves only when bodies move it. It is beautiful and quietly wrong, like every bound thing. At the Great Unbinding the drop **falls**. A Ch18 revisit, or a post-ending glimpse, shows the empty bell over a full catch-pool, with children playing in it.
  - *Ritual meaning:* Reefball began in the Low Reaches as a drowning-rescue drill. The ball is a woven float, and a score is *bringing it up*: the goal is a ring at the top of the drop, at the surface, never a net at the side. Before each match the captains each name one person the sea has taken, and the Tidecup is played "for the ones who didn't come up". The Ch7 side scene (the veteran's empty benches) is this rite.
- **If the human changes the form:** the **Weir**. The Bell is cast as a vast bronze bowl lying mouth-up in Tamsule's river mouth, a flooded Lit Age amphitheatre. It is sluiced full at high tide and drains as the tide turns, so a match lasts exactly one tide. Play is at and below the surface: players breathe at the top and dive for the float, and the goals are ring-gates set at the surface on the bowl's rim. Spectators sit on the stepped rim. The glimmer-tech clue survives, because the sluices are bound machines the Order "sanctified". The rescue-drill ritual carries over unchanged.

### N-13. Slice staging: cuts, the S10 hold, and two pillar-1 rewrites
- **Answer (camera grammar):** every change of setup between unrelated shots is a cut (`blend=0.0`). In ch02 that is every H05↔H06 change, and the close, where 014/015 stay on H05 and the cut to H01 lands on the `beach_path` walk, under VO 035. In ch03 it is S09↔S10 throughout, and S07→S08 cuts on a short fade instead of blending through the sinking door. No blends remain in either scene. Blends are for same-axis moves only.
- **Answer (S10):** the cut to S10 lands on line 043, the second sung line, and holds through 044–046 with at least 6 s of `@wait`, so Asha's voice plays over Rhen's face. His face is layered: `surprised` at 0.3 s (the first phrase), then `grief` at 0.6 s as he knows it. The self-blend `@camera S09 blend=2.5` is gone. The test checks the hold.
- **Answer (pillar 1):** Toma's 021 is now sincere: "She woke the house before light. We came down so they would not come ashore alone." It deepens the grief turn and sets up the choice to stay. Rhen's 054 is now a held look (`@wait 1.5`) and "...He never said where he learned it." That is in his voice, plants N-11's mystery, and is not glib. Also: a silent `@wait 0.6` before 006 (the look lands before the words), and 027 "Nope." becomes "No." (voice guide).
- **Not touched:** the `steps` node's `grade:` header (M1-ART-04 owns that change).

### N-14. Asha never hums again
- **Answer:** in `ending_dock` she draws breath for the tune, lets it go unsung, and smiles. She does not hum, and she never sings or hums again. Updated: color script `ending_dock`, `characters/asha_velamir.md`, and [act3_ending.md](beats/act3_ending.md) E6.
- **Why:** a hum gives part of the cost back and softens pillar 6. The ending's loss has to be whole to be true.

---

## 2026-10-23 (narrative, M1-NAR-08): review-sweep-C fixes

### N-15. No frozen temple before Ansedra: Ice moves to Lowlight, and the Sanctum is Glimmer
- **Answer:** [ADR 0015](../decisions/0015-vowbound-element-temple-order.md). **Nhoa (Lowlight, Ch11) is Ice**, and **Ethren (the Sanctum, Ch13) is Glimmer**. Hesk (Cloudloom, Ch12) stays Holy. Lowlight's drowned sanctum sits in the deep's cold, with motes sifting down like snow, and nothing in it is frozen. Cloudloom is an open-roofed stone weaving-hall, not a glacier cave. The Sanctum's basin is a lit mirror, not ice. No chapter, zone or Cantor moves.
- **Why:** N-09 put an Ice Saint in a frozen basin at the Order's seat, right before the wedding trap and the heretic turn. With the glacier temple just before it, that recreated the inspiring game's frozen-lake temple followed by the wedding betrayal (Cinematics, review-sweep-C). Making the Order's Saint glimmer is also the stronger clue: the church that burns Saltwright camps for binding glimmer kneels to a basin lit by it.
- **Supersedes:** N-09's Nhoa and Ethren element cells and its "Ice goes to the Order's own Saint" reasoning. Its Act I order stands. Updated: vowbound.md, bible §5.6–5.8, act_outline Ch11–Ch13, act3_ending H09, glossary, and color script `ch12` (the interior note).

### N-16. The Kite's lamps die in H09 with every other light; the countdown is the sea and the descent
- **Answer:** SPEC §3.5 is literal. Every glimmer-light in the world, **the Kite's bound lamps and engines included**, goes out in the same instant at H09. The Kite comes out of the storm already dark and flies the whole Ending on sail alone, in a long, slow, descending glide over the open sea. Liss holds it aloft. That removes the old lamp dimming countdown (E1 100% → E4 0). The countdown is now carried by (1) the sea-glow ramp, stepped per scene (act3_ending §0 rule 4), (2) the dead still rising off the sea, thinning scene by scene, and (3) the Kite's height, as the dark sea comes closer. With the lamps dark, **each farewell is keyed only by the leaving person's own motes**. Other dead rise far off the rail, out of the key, and the sea-glow is a background value that never keys a face.
- **Also:** in E1 Kerrid's "alive for a moment" cue is now **his shadow**: his own rising light throws it across the deck onto Rhen's feet, clearer for a moment than the man. The breath-fog cue is cut, because on a tropical night his breath alone fogging would read as cold, not warm.
- **Why:** the Kite holding light for ten minutes contradicted SPEC §3.5's "in the same instant" and our own line that each farewell is lit only by the person leaving.

### N-17. The final shot shows her face; ch02's "Get up" branch keeps Rhen standing
- **Answer (E6):** the locked final shot is a **three-quarter profile from the dock's side**, at her eye height. Her face is against the star-filled sea, so the smile reads. There is still no cut and no push. (It replaces "1.0 m behind her".)
- **Answer (ch02):** in the "Get up" branch Rhen stays on his feet, leaning on Toma. The closing H05 is taken at his standing eye-line, and Asha rises to meet it. There is **no offered hand**, because he is already up. `offer_hand` now plays only in the "Stay with them" branch, where he is sitting in the water. H05 is defined as Rhen's POV, and its height follows his eye (haluna.md H05).

---

## 2026-10-23 (narrative, M1-NAR-08): review-sweep-D fixes

### N-18. Act II after the wedding is re-staged (Lead decision)
- **Answer:** [ADR 0016](../decisions/0016-act-two-restaging.md).
  - **The founding truth moves to Ch13's Lamp Archive, before the wedding.** The ledgers show the founders were binders, the Cantor roll carries its *kept / spent* column (Ysolde does the maths on Corran there), and the same hands sign across four centuries.
  - **The escape goes out across the lagoon** on the bride's barge. Merel stays behind and is taken.
  - **Venn has no revenant reveal**, and **nobody goes under the city**.
  - **Ch15 is "Unlamped":** a dark barge at sea, the Wakefin, Kerrid's reveal, and Hollowmere's grief, where Toma's faith breaks.
  - **Sefir's temptation at the Choir is to go home**, with the Eighth Verse left unsung. He never asks to be sung in.
  - **Kerrid's reveal is his own confession at sea.** No Stilling is performed on him.
- **Why:** sweep D found the post-wedding run followed the inspiring game in order. SPEC §3.5 mandates only the trap, the heretic declaration, Kerrid's reveal, and the Choir truth.
- **Supersedes:** the Ch14–Ch16 beats of act_outline as written for M1-NAR-02 and M1-NAR-05. It also supersedes N-15's "snow" simile: Nhoa's motes now sift like **silt**.

### N-19. Sweep-D staging fixes
- **Released at H09, rising after:** act3_ending §0 rule 7 states it plainly. Every release is at H09. After that, `sea_glow` and the dead coming up out of the sea are the ascent of already-released motes. Nothing is released later.
- **E5 is not the first dark sea:** `sea_glow` steps down to 0.04 and holds through E5. It reaches 0.0 only on the cut to E6.
- **E6 is front three-quarter:** the camera is on the dock planks, about 4 m shoreward, looking out to sea. Asha turns back from the sea toward Haluna, so her nose line ends about 40° off the lens axis toward camera, with the dark sea behind her. The ambiguous "H10 reversed" wording is gone. This supersedes N-17's E6 framing.
- **ch02 "Stay":** after Asha's closing line, Rhen takes the hand she offered and they rise together (`take_hand`, `rise_to_stand`) before the cut to the walk. In "Get up", a `@wait 0.8` lets Asha finish rising before H05 opens.
- **E3:** Rhen's lantern is unlit, so Dace's motes stay the only key.

---

## 2026-10-23 (narrative, M1-NAR-09): Act I echo audit

### N-20. Act I is re-staged from the Prologue to Ch8 (ADR 0017)
- **Answer:** [ADR 0017](../decisions/0017-act-one-restaging.md).
  - **Sefir first appears at the end of the Ch6 Brine Shoals raid**, on his Edict progress. He stops the branding, lets Liss go, and is at neither the Tidecup nor the seawall.
  - **The Tidecup (Ch7) has no Order official.** It opens with the captains' naming rite. **Rhen dives for Oruvel's side** under its captain **Tavi Orse**, Mother Kell's grandson. Toma doesn't captain or play. Nothing interrupts the match.
  - **The seawall (Ch8) is an evacuation up the Fisher Stair**, with no weapon and no forbidden machine. Liss's contribution is a plain rope hoist, which the Stillguard cut down afterwards. The wall falls anyway.
  - **The Ch4 ferry is never attacked.** The party boards a drifting dead trader to bring its name-board home and fights the Spar-Wraith on its deck.
  - **The Prologue has no campfire circle.** The seven keep separate vigils, Rhen walks among them and sits beside Asha, and the line comes as his ~~oil wick~~ (**corrected 2026-10-23 by M1-NIT-01:** lantern's oil burner) catches. Ch19 repeats the vigil.
- **Why:** the audit found these beats followed the inspiring game's opening acts: the cleric introduced at the games, the guardian-captain with the newcomer as star, the coastal assault with forbidden weapons, the monster attacking the pilgrims' boat, and the campfire with the hero walking off to narrate. The other Act I residuals are accepted in the ADR, with reasons.
- **Supersedes:** N-01's wording "after the Brightwater ferry survives the Spar-Wraith". The band is still earned on the Ch4 crossing, and is still inked by Toma and shown from Ch5. It also supersedes N-12's "the veteran's empty benches": the Ch7 side scene is now Tavi asking Asha to bless Oruvel's empty moorings under the Bell, by the same naming rite. N-12's arena notes are otherwise unchanged.

---

## 2026-10-23 (narrative, M1-NAR-09 and M1-NAR-08): review-sweep-E fixes

### N-21. Kerrid is re-staged; the Ending order is Imra, Dace, Kerrid; the Prologue line is replaced (ADR 0020)
- **Answer:** [ADR 0020](../decisions/0020-kerrid-restaging.md), ~~proposed for Lead sign-off~~ **accepted by the Lead 2026-10-23** (noted in N-23).
  - **Kerrid was never a guardian.** He was the ~~Stillguard captain of the Corrow wall~~ captain of Corrow's fisher stair-watch (**corrected by N-23**). In 1001 AL ~~Imra and Dace were his guests for eight days~~ he ~~walked Imra to Coilspire and drank with~~ opened his wall-gate for Imra on the Coilspire path and held the line of (**corrected by N-24**) his hired diver Dace for the same eight days (**corrected by N-23**; they were strangers) during the Coilspire trial. When the Undertow came he held the Fisher Stair open, got them both up, and was taken by the sea at its foot holding the hand-line. Dace reached back for him and missed. He never went to the Choir and never fought Sefir.
  - **What keeps him is a watch, not a promise:** the stair-law "first down the stair, last up it". There are no promises to watch Asha or raise Rhen, and he never sought either child. He met the pilgrimage at Pemakar on his way to Corrow.
  - **Face:** bare and weathered, both eyes clear, no mask. His scars are rope-burns on his hands and forearms (his death-wounds), and the left forearm is wrapped.
  - **Ch5** line: "I held a stair for your mother once." **Ch8:** he works the stair's foot, and a fishwife says "Captain?". **Ch15:** the confession is about Corrow. **Ch16:** no visit to where he died; he walks last on the Rim, and at the Choir says "I carried her up so you could do this."
  - **Ending:** E1 Imra, E2 Dace, E3 Kerrid last ("Stair's clear." then "Stand up straight. Your father slouched."). The rests are R2 hands, R3 where his father stood, R4 the empty place. Durations are unchanged.
  - **Prologue line** (the human's approval, relayed by the Lead): **"Everyone I'm going to tell you about is still here tonight. Remember that, later."** The SPEC amendment is the Lead's.
- **Why:** sweep E found Kerrid's backstory followed the inspiring game's dead mentor point for point: guardian beside the hero's father, killed confronting the man responsible at the ritual's end, two promises about the children, the face cues, the return to where he died, and departing first.
- **Supersedes:** N-16's placement of Kerrid's shadow cue in E1 (it is now E3) and N-19's "E3" lantern note (Dace is now E2). ADR 0017's acceptance of the old Prologue line.

### N-22. Sweep-E residuals and staging
- **Ch7:** the newcomer filling a small island side's empty place is an accepted residual. **Oruvel's side does not win the cup:** win or lose its opening round, Tavi withdraws the side to go home and search Oruvel, and Tamsule's own side wins offscreen.
- **Ch6:** Sefir's "I knelt beside your mother" is accepted, with reasons in ADR 0020 (i).
- **Ch9:** the act break is "at the Iskarra vigil" (there is no fire, ADR 0017).
- **Liss:** her father is Hollowmere's **dock-master**, not a chief, and Hollowmere is governed by a council of hull-captains. **Tobin volunteered** as the groom and was never an heir. The Kite coming from her people's dry-dock is an accepted residual.
- **E6 blocking:** Asha starts side-on across the dock end, looking out to frame left with her left shoulder to camera, and turns about 50° to her left toward Haluna, ending 40° off the lens axis.
- **E5 sea-glow:** E4 0.07 and E5 0.06 held (were 0.06 and 0.04), so E5 still reads as glow and the cut to E6's 0.0 is visible. Rendering to confirm.
- **ch02 Stay branch:** Rhen takes Asha's hand right after her line 030, so she doesn't hold it out through Toma's introduction.

---

## 2026-10-23 (narrative, M1-NAR-11): review-sweep-F fixes

### N-23. Dace and Imra are strangers until the Corrow stair; Kerrid is a fisher-watch captain; the sweep-F residuals (ADR 0022)
- **Answer:** [ADR 0022](../decisions/0022-dace-imra-strangers-sweep-f.md), ~~proposed for Lead sign-off~~ **accepted by the Lead 2026-10-23**, including the Sefir and Kesh and Ch3 recognition residuals (noted in N-24). The decision that Dace is not Imra's guardian is the Lead's.
  - **Dace was never Imra's guardian and never walked her road.** He heard her hum the lullaby on Haluna's dock as a girl and never learned her name. In 1001 he was Kerrid's hired diver at Corrow while she was there for the Coilspire trial, and they never met. In the storm she went down the Fisher Stair into the sea for him, and Kerrid died holding the stair for them both. She gave him her comb to carry home to Asha. He began a hull at Hollowmere and sailed into the storm after her, to repay the debt: first down the stair.
  - **Kerrid** was the captain of Corrow's conscripted fisher **stair-watch**, never a Stillguard officer. He has no rank, title or fame, and there is no "Hero of Corrow". The stair-law and "Stair's clear." are the watch's. Only Corrow's old watch knows his face. Sefir sees what he is, not who.
  - **Toma** was at Ansedra 997–1002 and on the Corrow wall 1002–1009. He was sworn as Asha's guardian at her naming, at fifteen.
  - **Ch9:** Kerrid is bringing up the drowned at the stair foot during the Ebbing (a practical cause, and the tell is dropped). At dawn: "Somebody's still below." (**N-24:** alone, not with the old watch; looking out to sea, not at Asha.)
  - **Light:** the rope-burns are `glimmer_held`, from Ch10 on, never in Ch5 or Ch8. They lerp to lift at H09.
  - **E2:** Dace sees Kerrid; one shake of the head; no words.
  - **Accepted, with reasons in the ADR:** Sefir and Kesh as the founding couple; Rhen's recognition of the first verse in Ch3.
  - **Liss's** line-marks are on her right arm. The palette's night sea-glow minimum has an explicit Ending exception (E4 0.07, E5 0.06), tested.
  - **ADR 0020 was accepted by the Lead on 2026-10-23** (N-21 is marked).
- **Why:** sweep F found Dace's guardianship to be the largest remaining echo (the Lead's call), and Kerrid's new fame to be an echo of the mentor whose name precedes him. It also left consistency gaps in Toma's timeline, Kerrid's face, his reason to stay, and his light.
- **Supersedes:** N-02 item 4's "her mother's guardian"; N-11's "Dace met her" and "why he went with her as a guardian"; N-21's "Stillguard captain" and "guests for eight days" (each marked inline).

---

## 2026-10-23 (narrative, M1-NAR-11 reopened): review-sweep-G fixes

### N-24. The Ch3 lantern link is cut; Kerrid works Dace's line and keeps Imra's gate; the three dead never share a frame (ADR 0022 append note)
- **Answer:** recorded in the review-sweep-G append note on [ADR 0022](../decisions/0022-dace-imra-strangers-sweep-f.md), which the Lead accepted on 2026-10-23 with the Sefir and Kesh and Ch3 recognition residuals.
  - **Ch3 game text (B1, B2):**
    - Toma was at Ansedra in 1001: "I was at Ansedra then, at the temples. I heard of it by letter." (`ch03_verse_061`, replacing 010).
    - He has guarded Asha three years. Before that, home on leave, he had to find her in the net racks (`ch03_verse_062`, replacing 024). "Since she was nine" is gone from the game and the docs.
  - **Lead verdict (B3):** `ch03_verse_051`/`052` ("Your father. The one with the lantern." "Yeah.") are cut. Act I never voices Asha's link between the lantern and Rhen's father. The Ch2 stillness stays wordless, and the link surfaces only in Kerrid's Ch15 confession (~~"A man with that lantern brought me this. I was seven."~~ **superseded 2026-10-23 by N-25:** "A man with a lantern like that brought me this. I was seven.").
  - **S5:** Asha's line now ends "until tonight" (`ch03_verse_063`, replacing 053), so "he" can no longer read as Dace.
  - **S1, Kerrid and Dace:** they did not drink together. For eight low tides they worked the rings, Dace under the water and Kerrid on the bottom step holding his line. "Dace slouched" stays.
  - **S2, Kerrid and Imra:** he kept the stair-watch's wall-gate on the Coilspire path and opened it for her at dawn and dusk. They spoke at the gate, and he never walked beside her.
  - **S3:** "Somebody's still below." is said looking south, out to sea, not at Asha. "Below" is Imra under the storm and the held dead.
  - **S4:** in the Ch9 cutaway Kerrid is alone at the stair foot. The old watch is at the Ebbing on the shore.
  - **S6:** Dace's sleeves were torn on the stair and Imra's escort saw his line-marks. A hunted Saltwright going home brings the Order to his son, so he never went home. ~~His one message asked **Mother Kell** to keep Rhen~~ (**corrected 2026-10-23 by N-25:** the message asks nothing, and Kell takes him in unasked), and she raised him from eight to nineteen. The player reads this in Dace's Ch17 logs.
  - **S7:** Toma came to the Corrow wall in 1002, at twenty-one.
  - **S8:** Kerrid's walk to Corrow began when the Undertow stirred early this year, not at Asha's naming.
  - **S9:** Rhen learns Dace's motive from the Ch17 logs, not at the Choir.
  - **S11:** act3_ending §0 rule 8. Imra, Dace and Kerrid never share a frame from H02 to E3, and E2's look is a shot and a reverse.
  - **Nits:** voice_guide's early slouch sample is cut; the heading of N-11 and the status in N-23 are corrected inline.
- **Why:** review-sweep-G found that the shipped Ch3 text still contradicted ADR 0022's timeline, and that the early lantern link, the drinking, the daily escort, the gaze on Asha and a three-dead frame each carried a trace of the inspiring game.
- **Supersedes:** N-21's "walked Imra to Coilspire and drank with" (marked inline); N-23's Ch9 staging, which now carries an inline note.

---

## 2026-10-23 (narrative, M1-NAR-11 reopened): review-sweep-H fixes

### N-25. Kell takes Rhen in unasked; the lantern is the first of a pair; Kell is a chandler (ADR 0022 sweep-H append note)
- **Answer:** recorded in the review-sweep-H append note on [ADR 0022](../decisions/0022-dace-imra-strangers-sweep-f.md).
  - **B1:** Dace's one message, addressed to Rhen, says only "helping a friend on a long trip" and asks nothing. Mother Kell takes Rhen in unasked. Dace hears of it a season later from a Hollowmere trader ("Kell. Of course."). Her Ch1 wick is her own stock, given "for luck" as she gives one to every diver, and it is never from or about Dace. New echo rows for the request and for the gift before the opening calamity.
  - **B2:** Dace built his lanterns as a pair. Rhen's is the first one, left on its hook at Oruvel, and the one Asha saw at Haluna was its twin. Ch2 "That lantern." is unchanged (recognition of the make). The Ch15 line becomes "A man with a lantern like that brought me this. I was seven."
  - **S1:** Kell is Oruvel's chandler, who never learned to swim. The shipped Ch2 line stands.
  - **S2:** the bible's Present row: Asha was named in 1009 and sets out in 1012.
  - **S3:** act3_ending §0 rule 8 is guaranteed by authoring in C and E beats. In player-driven cameras the two lamps are drawn as light, not figures. H05 keeps Kerrid off-frame. The Ch19 outline grouping is design prose, never VO.
  - **S4:** the Ch17 logs say why not Oruvel even once (every hull knew his face), why Haluna once (no name, no-one at risk but him), and why he never fetched Rhen ("a wright's son for life ... ~~After the storm I'll go myself~~"; **corrected 2026-10-23 by N-26:** the entry breaks off at "After the storm").
- **Why:** review-sweep-H found that the sweep-G S6 fix put back the father's request to have his son raised, which ADR 0020 had removed from Kerrid, and that nothing explained how Rhen came to wear the lantern Dace had at Haluna.
- **Supersedes:** N-24's S6 "asked Mother Kell to keep Rhen" (marked inline); the "old diver" in every Kell row; N-24's Lead-verdict quote "A man with that lantern brought me this" (marked inline, added by N-26); N-02 item 4's "saw it when she was seven" (marked inline, added by N-26).

---

## 2026-10-23 (narrative, M1-NAR-12): review-sweep-I nits on M1-NAR-11

### N-26. Dace's Ch17 logs are a written ledger, never his voice; the "after the storm" entry breaks off; E2's lamp is the oil burner (ADR 0022 sweep-I append note)
- **Answer:** recorded in the review-sweep-I append note on [ADR 0022](../decisions/0022-dace-imra-strangers-sweep-f.md).
  - **S1, watch (IP):** the Ch17 logs are a **written ledger, read on screen in Rhen's hands**. They are never voiced in Dace's voice, never played back as a recording, a projection or a glimmer-echo, and never addressed to Rhen as a message ("if you're reading this", "son, ..."). Dace's voice is heard only in E2. An entry may name Rhen (his name is in every entry), but it is written about him, to nobody.
  - **S1, the entry is cut short:** the quoted entry now ends "Let him be one. After the storm" and breaks off; the next page is blank (**clarified 2026-10-23 by M1-NIT-01**, ADR 0022 sweep-J note: this is the ledger's **last** entry, written the night he went into the storm after Imra; "Kell. Of course." is an earlier entry, a season after Corrow, and every page after the broken-off one is blank). The irony stays, and the stated promise to come home is gone. Applied to act_outline Ch17 and rhen_sallow.md Act III; N-25 S4 is corrected inline.
  - **S2:** act3_ending E2 now says Dace sees "his old lantern ... still the oil burner he fitted and not glimmer (N-02)". "The oil wick" there meant N-02's fitting, but it read as Kell's wick, which the sweep-H watch keeps off the lantern and unburned for E7. The E2 line now says so in a parenthesis.
  - **S3:** decisions_log N-24's Lead-verdict quote ("A man with that lantern") is marked superseded inline, and N-02 item 4 now says Asha saw the lantern's **twin**. Both are added to N-25's Supersedes list.
  - **Nits:** Kell's stall is "on Oruvel's second mooring" everywhere (rhen_sallow.md had "two hulls along"). vertical_slice.md (H06) says "She never says why", because she does say "That lantern." The same words in the ch02 `.dlg` source comment wait for the next narrative commit that touches game data (this task is docs only).
  - **Watch carried from sweep I (concurred):** no Act I line has Asha connect the lantern's make to the man at Haluna aloud before Ch15.
- **Why:** review-sweep-I (cinematics + IP) found that the sweep-H S4 log text gave the father his own words about his son, written before he goes into the calamity, which moves our ledger toward the inspiring game's recorded messages from the father. The reasons stay ours. The delivery must not drift, and an unfinished promise is ours where a stated one is not.
- **Supersedes:** N-25 S4's quote "After the storm I'll go myself" (marked inline).

---

## 2026-10-29 (narrative seat, ui-menus track, M3-NAR-1000): Pell's echo check and the Kerrid and Pell sheet questions

### N-27. Pell's arc passes the echo check, with four authoring guards; the sheet questions answered
- **The echo check (SPEC §2, pillar 1).** The outline (a tall non-human who learns enemy abilities, carries a long pole,
  bears a mark of shame and returns to his people) shares a silhouette with a well-known beast-folk guardian. The beats
  that carry the meaning differ in kind, so **no beat changes**:
  - **Not a guardian.** Pell is never sworn to Asha and never protects her as a duty. He meets her as a critic ("beautiful,
    and pointing the wrong way") and joins after the Ebbing for his own reason (Ressa).
  - **The shame is chosen grief, not a lost fight.** His name-shell was scraped because he would not turn his back on his
    sister's death. Nothing was broken off his body, and no rival did it to him.
  - **The return is a letting-go, not a trial.** His name is carved again when he tells the elders he will turn around. He
    never fights his own people to earn it.
  - **He learns by listening.** His learning is the Kirru habit of imitating what he hears (the Listen stance), not being
    struck by a technique and taking it.
  - The visual sheet already avoids every cue (no horn, mane, blue fur, tattoos or tail; the staff is a wading bird's leg).
  - ADR 0017 passed him for Act I on the same grounds. This entry extends that to Acts II and III.
- **Authoring guards (every role):**
  1. Never call Pell a guardian, protector or sworn companion, in text, task titles or shot names.
  2. No scene where Pell fights other Kirru for his honour or his name.
  3. Never describe his ability-learning as taking a blow, or by the series' job word. In docs he "learns by listening".
     SPEC §3's roster row now says "learns enemy abilities by listening to them" (ADR 0201, the Lead, 2026-10-29), and
     the job word is on the banned list.
  4. His crest, not his body, carries emotion; keep him free of any horn or breakable feature.
- **Kerrid (the art sheet's §12 questions):**
  - **No breath: yes.** The unrisen don't breathe (bible §2). He speaks, and speech needs no idle breath: no breath
    cycle, no sighs, no fog in the cold. His lines are delivered without a visible intake.
  - **No tears: yes.** The unrisen don't weep. His grief is held in the face and the stillness.
  - **The anchor's shackle ring as the cleaver's pommel: welcome.** A stair-watch captain carrying the wall's own iron fits
    the man, and it is not an Order mark.
  - **Skin desaturation: keep 0.06.** The unrisen don't bleed; a slight pallor is right. More would read as a monster, and
    the bible says they are not monsters.
- **Pell (the art sheet's questions):**
  - **No tail: yes.** The Kirru are heron-tall and otter-faced; no tail keeps the outline far from any beast-folk echo.
  - **No lower garment: yes.** The Kirru dislike clothing; the split reed girdle is all he wears below the mantle.
  - **A spiral of notches as the name carving: yes.** Kirru names are carved, not written in a human script.
  - **No tears: yes.** Kirru grief is the farewell-tide, a song. In private it shows as a lowered crest and stillness.
  - **Keepsakes: both sources hold.** The bible's "no keepsakes" means nothing kept *of the dead*. A living Kirru wears their
    own name-shell, and it is their name, not a keepsake. Nhoa wearing her own carved shell is the point of her: Ressa is
    anchored by her own self, the one thing a Kirru keeps. vowbound.md's "(the keepsake)" is the Vowbound design term for
    the anchoring object and stays.
  - **Fur: confirmed.** A dark saddle over the back and shoulders, mid-brown on the front, and a pale throat.
- **Stale sources:** ADR 0020's stair-watch and rope-burn text and the glossary's "Stillguard" stair-law rows were
  already superseded by ADR 0022's notes and the glossary's own later rows; an append note on ADR 0020 and a glossary
  row now point at them. Mother Kell's "diver" rows (195, 254) are superseded by row 258 (chandler). The glossary's
  "unrisen" row now follows the bible: anything unfinished, not only a promise.
- **Supersedes:** nothing in canon. It adds guards for authoring.
