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
- **Answer:** Asha heard her mother sing the first verse toward home from the shrine door, and hum it the night before she left. She had forgotten it until Ilun "gave it back". Dace learned it from Imra on the pilgrimage, so both children were sung to sleep by the same verse.
- **Why:** it gives Asha her own recognition in Cutscene B, so the scene is a meeting of two griefs, not just Rhen's. It is consistent with rhen_sallow.md ("a verse of the Hush, which Dace learned from Imra") and with the custom that Cantors sing and everyone else hums.
