# Narrative Decisions Log

Small canon calls that Narrative owns: answers to other roles' open questions and staging rules for story content. They are too small for an ADR, or they don't change the spec. Anything that binds more than one role's *work* is flagged for the Lead to fold into an ADR (CLAUDE.md §6). Entries are append-only. To change an answer, add a new dated entry that supersedes it.

---

## 2026-10-22 (narrative-stream-2, M1-NAR-02): Art's open questions (docs/kb/art/README.md)

### N-01. Asha's first reach-band: yes, earned on the Ch4 crossing and shown from Ch5
- **Answer:** approve Art's proposal. Asha earns **one** band, on her left forearm, offscreen after the Brightwater ferry survives the Spar-Wraith. Toma inks it, since he carries Haluna's ink, and it's shown from Ch5. In Ch5, one line acknowledges it (Rhen notices; Asha: "My first. Toma's hand shook."). She earns **a second band only in the ending** (the dock shot), for the voyage she wasn't meant to come back from.
- **Why:** reach-bands count voyages *survived* (bible §5.1), and a Cantor's pilgrimage is the voyage nobody expects her to survive. One band all game says so without a word. The second band in the last shot is visible growth (pillar 5) that pays off pillar 6: she lost her voice but kept her life, and her arm records it. Art's generator already takes a band count, so this costs two parameter values.

### N-02. Rhen's lantern burns oil, not bound glimmer
- **Answer:** **oil.** It is a Saltwright-made brass and salt-glass housing that Dace deliberately fitted with an oil wick. The flame uses `oil_lamp`, never `glimmer_bound`, and it does **not** go dark at the Unbinding.
- **Why:**
  1. In Ch1 the lantern is the right light in the drowned tower against the held cyan motes, which is the player's first lesson in the color language (color script Ch1). If it were bound, that lesson would invert.
  2. Oil is the last light the game shows (color script rule 4, the post-credits lamp). Rhen carrying honest light all game is what that ending rhymes with.
  3. It gives Dace a wordless character note: a wright who could have bound his own lamp and chose not to. Liss reads the housing as Saltwright work in Ch6 and will notice the wick. That's a scene seed.
  4. Asha's stillness at the lantern in Cutscene A is *recognition* (she saw it on her mother's guardian when she was seven), not her hearing someone inside it. That keeps the Dace mystery human.

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

### N-11. The first verse is a Velamir family lullaby, and Dace knew Imra before she was named
- **Answer:** an earlier Velamir Cantor sang the first verse toward home from the Shell Shrine door, and the women of the line have hummed its tune as a lullaby ever since, without the words. Imra hummed it as a girl, long before she was named. **Dace** met her years before Rhen was born, as a young wright trading salvage along the Low Reaches and putting in at Haluna. He heard her hum it, took the tune home to Oruvel, and hummed it to Rhen every night until he left. That old friendship is also why he went with her as a guardian in 1001. Asha was hummed it every night until she was seven, heard it sung once from the door, and forgot it until Ilun gave it back.
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
