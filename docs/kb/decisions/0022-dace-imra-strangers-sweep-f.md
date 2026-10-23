# 0022 — Dace and Imra are strangers until the Corrow stair; Kerrid is a fisher-watch captain, not a hero; the sweep-F residuals

- **Status:** accepted (Lead sign-off 2026-10-23, including the accepted residuals)
- **Date:** 2026-10-23
- **Roles affected:** Narrative; Cinematics (the Ch8 stair foot, the Ch9 cutaway, the Ch14 water-steps, the Ch16 confrontation, the E2 look); Character Art (Kerrid's cord and palette, the rope-burn light, Liss's arm); Art and Rendering (palette.json `sea_glow_rule`, the rope-burn hue, color script `ch08`, `ch15`, `ch21` and `ending_unbinding` notes); Audio (none; every cue id is unchanged); Lead (sign-off; ADR 0020's "Back: Dace was Imra's guardian" row, which the Lead had accepted, is superseded here)
- **Author role:** Narrative (M1-NAR-11, from review-sweep-F on M1-NAR-09 and M1-NAR-08)
- **Amends:** [0020](0020-kerrid-restaging.md) (a), (b), (c), (d) and its "Back" rows; [0017](0017-act-one-restaging.md) (no change to any verdict; the Ch5 no-legend watch now holds in the backstory too). Both are accepted, so this ADR adds to them, and each gets a dated append note.

## Context
Review-sweep-F (the M1-NAR-09 and M1-NAR-08 Review logs) approved ADR 0020 with fixes and left these items:
- **Lead decision (sweep-F note, made a criterion of M1-NAR-11):** with Kerrid off the guardian role, the largest echo left in the game is Dace: the hero's father, guardian of the heroine's sacrificed parent, who went into the calamity for her and is found at its core in the finale. 0020 accepted this as a residual. The Lead has decided against it: **Dace is no longer Imra's guardian.**
- **S1 (IP):** Kerrid became a celebrated soldier of the church ("the most decorated Stillguard captain of his generation", "the Order's dead Hero of Corrow", a story every cadet learns). The inspiring game's mentor is also a famous former warrior of the church. It also breaks 0017's Ch5 rule that nobody names him as a legend, and makes him a second ex-Order soldier beside Toma.
- **S2:** Toma's timeline puts him in the Stillguard in 1001, possibly at Corrow, yet he knows Kerrid only by reputation. Asha's sheet has him her oath-guardian since she was nine; his own sheet has the oath at her naming, at fifteen.
- **S3:** who can recognise Kerrid's face (Sefir in Ch6, the Ch13–14 stay in Ansedra, the Stillguard on the Corrow wall in Ch8).
- **S4:** nothing says why Kerrid walks on after Corrow (Ch8), where his want is spent.
- **S5:** his rope-burns "glow faintly gold", but gold (`glimmer_lift`) means released, and his light is held until H09.
- **S6, S7, S8 (IP, unaudited):** Kerrid keeping away from the Ebbing as the tell that he is dead; Sefir and Kesh as the founding couple; Rhen recognising the temple's song in Ch3.
- **NAR-08 S1 and S2:** palette.json's `sea_glow_rule` has no Ending exception for E4 0.07 and E5 0.06; Liss's line-marks are on her left arm in one paragraph of her sheet and her right in another.
- **Nits:** "the place he once sent Imra"; decisions_log N-21 still says 0020 is proposed; dialogue_format.md says Kerrid's long speech is in Ch14 (it is Ch15).

**What SPEC fixes (§3.4, §3.5):** Rhen's father **was a Saltwright who vanished into the Undertow**. Asha's mother **was the last Cantor**. Kerrid **knew both Rhen's and Asha's parents**. In the Ending, Kerrid and Asha's mother are released, the mother **appears for one last scene**, and Rhen **loses his father for real and this time gets to say goodbye**. SPEC says nothing about any bond between Dace and Imra, nothing about Dace being on her pilgrimage, and nothing about where in the storm Dace is found.

## Options (Dace and Imra)
1. **Dace walked with Imra unasked and was never sworn** (the sweep's cheap lever: "the wright who walked with her mother"). Rejected. It changes a word, not the shape. The hero's father still walks the heroine's parent's pilgrimage beside her and goes into the calamity after her at its end.
2. **Dace is the boatman who refused to carry her** (one of the Lead's examples). Considered and rejected. The Order carries its own Cantors, so a Cantor has no reason to ask an outlawed stranger for passage. His refusal also changes nothing she does, so it makes him a bystander, and his only active beat is still following her into the storm from the Rim.
3. **Strangers until the Corrow storm, bound by a debt (chosen; the Lead's other example).** They never meet until the night of the storm. On the Fisher Stair she goes down into the sea for him, a diver she has never met, and Kerrid dies holding the stair for them both. Dace never walks a step of her pilgrimage. He goes into the storm after she sings because he owes her a life, and because a captain he drank with for eight nights taught him "first down the stair".

## Decision

### (a) Dace and Imra: strangers, then a debt
- **Before 1001.** Dace never knew Imra. Years before Rhen was born, as a young wright trading salvage along the Low Reaches, he heard a girl humming on Haluna's dock while he unloaded. He took the tune home and never learned her name. (N-11's source of the lullaby is kept. Its "Dace met her" and "that old friendship is also why he went with her as a guardian" are withdrawn.)
- **Corrow, 1001.** When Rhen was eight, Dace went up the coast for a season's wall-work. Kerrid, the captain of Corrow's stair-watch (b), had hired a Low Reaches lamp-diver to re-seat the hand-line's iron rings at the foot of the Fisher Stair, below low water, before the Rising. Dace kept his line-marks under his sleeves. For eight nights he and Kerrid drank together at the watch-house, and Dace slouched.
- **Imra came to Corrow in the same eight days** for the Coilspire trial, with her Order escort. Kerrid walked her up the headland path to Coilspire at every dawn and back at every dusk, because the path runs along his wall. She laughed at the wrong times. Dace kept out of her way, because a Saltwright under his sleeves doesn't sit at a fire with a Cantor's Stillguard. **Kerrid was the only man in Corrow who knew them both** (SPEC's "knew both parents", literally), and they never met.
- **The storm (the eighth day).** The sea drew out ahead of the Undertow and came back early. Dace was under the stair foot at the last ring. Imra, on the wall-head with her escort, heard a living lamp in the water under the stair, one man still drowning there, and **went down the stair for him against her escort's orders**. Kerrid held the wall-gate open past the hour, went down after her, and got them both onto the stair. On the climb Imra hummed to the children ahead of her on the steps to keep them climbing. It was the lullaby, and **Dace knew it**: the girl on Haluna's dock. Kerrid was the last man on the hand-line when the sea came over the stair (0020 (a), unchanged from here). Dace reached back for him and missed.
- **After.** Imra danced the Ebbing for Corrow's drowned. That night she and Dace spoke once, the only conversation they ever had. She told him the tune was the first verse. He told her he hummed it to his son. She gave him her **tortoiseshell comb** to carry home to her daughter, because she would not be coming home.
- He did. He walked up Haluna's dock with the comb and his lantern on his shoulder and put it into a seven-year-old's hands. **That is where Asha saw the lantern** (N-02's Ch2 stillness: still recognition, now of the stranger who brought her mother's comb home). Asha wears the comb all game.
- He did not go home to Oruvel. One message reached it: he was "helping a friend on a long trip". At Hollowmere he began a hull to follow her into the storm (the unfinished ship that becomes the Kite). He modelled its sails on Virel, whom he had seen flown alight over the Corrow wall on the night of the storm. The hull wasn't ready when word came that she had reached the Rim. He took a small boat south and sailed into the Undertow as it went down to sleep.
- **Why he went:** a debt, not a duty. A stranger went down a stair into the sea for him, and the man holding the stair died for them both. Dace went down for her: first down the stair, Kerrid's law, which he had learned over eight nights of drinking and took into the storm as his only creed. Inside he found he couldn't pull her out without tearing the storm loose on the coasts, on Oruvel and on his son. So he held her light together instead (ADR 0016's Ch21 staging, unchanged).
- *Why it serves the pillars:*
  - **Pillar 6:** he can neither save her nor leave her.
  - **Rhen's wound is sharper:** his father chose a stranger's debt over his son, and Rhen has to hold that and still say goodbye.
  - **The bond between the two families is an act, not an office:** Asha's mother went into the sea for Rhen's father.
  - **The lullaby (N-11) carries more weight:** it is how two strangers knew each other on a stair.
  - **Kerrid's death got both parents up,** which deepens SPEC's "knew both".

### (b) Kerrid: captain of Corrow's fisher stair-watch, not a decorated Stillguard officer
- **The stair-watch.** Corrow's Fisher Stair is kept by the **stair-watch**: the conscripted fishers of the low town (bible §5.4), under a captain chosen from among them. The Stillguard garrison holds the Bastion and the wall-head. The watch holds the stair. **"First down the stair, last up it"** and **"Stair's clear."** are the watch's law and all-clear, not the Stillguard's.
- **Kerrid** was a Corrow fisher's son, conscripted at sixteen and captain of the watch for fourteen years. He had no rank in the Order, no decoration and no title. Corrow lit his name with the rest of that Rising's drowned. The watch still tells the story at Corrow, and nobody else does. **There is no "Hero of Corrow"**, and no cadet learns him. That is 0017's Ch5 no-legend rule, now true of his past as well.
- His **knotted cord** is the watch captain's cord, three knots in faded watch-red. It is not a Stillguard cord. He was never in the Order, so the party has one ex-Order soldier, Toma. He has twice stood on the wall while the Stillguard performed the Stilling on an unrisen, so he knows what it is.

### (c) Who knows his face
- **Only Corrow's old fishers of the 1001 watch.** The Order never knew his face.
- **Ch6:** Sefir doesn't know the face. He sees what Kerrid is, as a revenant who lives on held light would, and finds it interesting rather than frightening. Kerrid keeps his back to the barge because he knows what the Order does with the unrisen and doesn't know what a High Warden can see.
- **Ch8:** the fishwife beat is staged storm-dark, at 16:40 near-night with spray. Kerrid is waist-deep at the stair foot, and the climbers face the climb. Toma and the Stillguard are on the wall-head above, out of earshot in the storm. The fishwife is the only one who looks back down. None of the Stillguard on the wall knew the watch captain's face: the garrison rotates, and Toma came in 1002.
- **Ch13–14:** Sefir lets him be. An unrisen is the Long Stillness in one man, and Stilling him in front of the Cantor would cost Sefir her trust before the Choir. He can wait. Kerrid never takes Sefir's hospitality: he sits out the nights at the city's outer moorings among the barge-polers (he declines inns) and never enters the Sanctum. At the wedding he stands at the back of the Lacquer Court among the polers. In the escape he holds the court's water-steps and is **last onto Merel's barge**.

### (d) Toma's timeline (pinned)
- Born 981. Joined the Stillguard at sixteen (997).
- **Five years at Ansedra's temples (997–1002), so he was at Ansedra in 1001** and never saw Kerrid.
- **Seven years on the Corrow wall (1002–1009),** where the watch still tells its captain's story. He knows it as Corrow's story, never the man.
- The Saltwright camp burning was at 22 (1003), on a Brine Shoals raid out of Corrow.
- He came home and took the guardian oath when Asha was named at fifteen (1009). He was 28, and he is 31 now.
- **Asha's "oath-guardian since she was nine" is withdrawn.** He has been her sworn guardian since her naming. Before that he was the Haluna boy who went away to be a soldier and came home on leave.
- **Ch12:** the breath, the rope-burns and the fishwife's one word let Toma put Corrow's story to a face.

### (e) Why Kerrid stays after Ch8: the watch moves to the pilgrimage
- At dawn after the Ebbing (Ch9), Kerrid is waiting on the road out of Corrow. Rhen: "Thought Corrow was where you were going." Kerrid: "It was." Rhen: "So?" Kerrid, looking at Asha ahead: **"Somebody's still below."**
- A Cantor's road goes down to the Choir, and a captain doesn't come off the wall while anyone is still below. That is why he walks last in the line on the Rim (Ch16). Ch15 makes the line legible.

### (f) The Ebbing: a practical cause on screen
- During the Ch9 Ebbing, Kerrid is at the stair foot with the old watch, bringing the drowned up out of the low town at slack water. One cutaway shows a big man in a straw cape carrying a child's body up the Fisher Stair while the motes go out to sea behind him.
- "He never stands near the Ebbing" is **removed** from his planted clues. His tells are that he never eats, declines inns, his breath doesn't fog in Ullar, and animals shy from him.

### (g) The rope-burn light is held, not gold
- An unrisen's light is anchored, so his rope-burns leak **`glimmer_held`** (cool cyan), very faint. It shows only in dim scenes and **only from Ch10 on**: never in Ch5's first meeting and never in the Ch8 stair-foot shots, so the clue isn't spent at the place he died.
- Ch15's motes leaving his hands are already `glimmer_held`, sideways (color script `ch15`).
- At H09 the light makes color rule 1's single 1.5 s lerp from held to lift. From then on, through E3, every mote off him is **`glimmer_lift`**, and no held cyan appears in the last farewell.

### (h) Ch16
- He walks last in the line, behind Asha, toward the Choir **where the woman he got up his stair was spent**. ("The place he once sent Imra" is withdrawn: he sent no-one.)
- **Watch:** "I carried her up so you could do this" is said, never drawn. Kerrid draws no steel on Sefir and does not lead the refusal (Asha refuses, Ysolde denounces). He holds the line only once the storm wakes.

### (i) The Ending: order unchanged, one look added, and the light pinned
- **E1 Imra, R2, E2 Dace, R3, E3 Kerrid last, R4.** Imra still goes before Dace, because his hands are only free once she has gone. Kerrid still goes last, by the watch's stair-law.
- **E2, one look, no words:** when Dace turns he knows Rhen at once. Past Rhen's shoulder he sees Kerrid, and for one beat the reach he missed on the stair is in his face. Kerrid shakes his head once. Then Dace looks only at his son. That pays off "I don't think he forgave himself" (Ch15). It is not a goodbye, so §0 rule 1 holds.
- E3's lines are unchanged ("Stair's clear." "Stand up straight. Your father slouched."). His motes are `glimmer_lift` (g).

### (j) Ch15 and Ch17: the new facts reach the player
- **Ch15 (Kerrid's confession),** to them both: "She heard a man drowning under my stair and went down for him. A diver she'd never met. Your father, Rhen." His other lines are unchanged. Asha touches her comb: "A man with that lantern brought me this. I was seven."
- **Ch17:** Dace's logs at Hollowmere tell the stair, the comb, and a Cantor whose name he learned only on it. Rhen's name is in every entry.

### (k) The palette exception, Liss's arm, the Prologue and the nits
- **palette.json** `sea_glow_rule` gets an explicit exception: `ending_unbinding` E4 0.07 and E5 0.06 are night frames below the 0.08 night minimum on purpose (color script rule 3). It is mirrored as structured data (`sea_glow_night_min`, `sea_glow_night_exceptions`), and `tools/tests/test_palette_rules.py` checks that the values sit between the 0.04 floor and the 0.08 minimum and agree with act3_ending §0 rule 4 and color script `ending_unbinding`. `validate_data.py` has no palette checks, so the test lives in its own file (CLAUDE.md §5).
- **Liss's line-marks** are on her **right** arm, her collarbone and the right side of her neck up onto her cheek. The left arm is sleeved to the shoulder in the copper-mesh work-sleeve.
- **Prologue VO direction:** read it as plain fact, not foreboding. On replay it is literally true: the held dead are still in the world until H09.
- **Nits:** N-21 marks 0020 accepted; dialogue_format.md says Ch15. SPEC.md:522 cites ADR 0021, which is reserved for the character team's MPFB2 ADR and not yet on this branch. That is the Lead's file and is not edited here.

## Echo check: sweep-F items
"Analogue" is the nearest beat in the inspiring game. **Mandated** marks a beat SPEC requires. **Lead** marks a verdict that needs the Lead's sign-off. A row marked *consistency* fixes our own canon and has no analogue to clear.

| Item | Our beat | Nearest analogue | Verdict |
|---|---|---|---|
| Back (a) | Dace and Imra are strangers until the Corrow stair; she goes into the sea for him; he never walks her road | the hero's father guarded the heroine's parent on the pilgrimage | Re-staged (a), at the Lead's decision. There is no guardianship, no shared road and no prior friendship. The two are bound by one act on one night. Supersedes 0020's "Back: Dace was Imra's guardian" accepted residual. **Pass (Lead).** |
| 21 (a) | Dace, inside the storm, holds Imra's light together for eleven years | the hero's father is inside the calamity, at its core, and is fought | **Accepted residual.** SPEC mandates that he vanished into the Undertow and that Rhen gets his goodbye. ADR 0016 made him not the storm and never fought. He now went in as a stranger repaying a debt, not as her sworn companion following his charge. **Watch:** no line or memory has Dace and Imra as a pair who travelled together (no "we", no road, no shared camp). |
| Back (a) | Asha saw the lantern when a stranger brought her mother's comb home | (none: a consistency knock-on of (a)) | *Consistency.* N-02's Ch2 stillness is still recognition, with a new source. No `.dlg` line changes. |
| Back (b) | Kerrid is the captain of Corrow's conscripted fisher stair-watch; no rank, title or fame; known only at Corrow | the mentor is a famous former warrior of the church whose name precedes him | Re-staged (b). He was never in the Order. "Hero of Corrow" and "every cadet learns" are gone, and 0017's no-legend watch now holds in his past too. Pass. |
| Roster (b) | One ex-Order soldier in the party (Toma) | (sweep-F: two ex-church soldiers) | Resolved by (b). Pass. |
| 6, 8, 13–14 (c) | Nobody outside Corrow knows his face; Sefir sees the unrisen, not the man; the fishwife is the only one who looks down | (none) | *Consistency* (S3). The Ch8 staging is pinned. Pass. |
| Toma (d) | At Ansedra in 1001, at Corrow 1002–1009; sworn at Asha's naming at fifteen | (none) | *Consistency* (S2). Pass. |
| 9 (e) | "Somebody's still below.": his watch moves to the pilgrimage | the mentor stays with the party because of promises to the dead parents | It is a watch, not a promise to anyone, and it is the stair-law the player saw at Corrow. Pass. |
| 9 (f) | Kerrid is at the stair foot bringing up the drowned during the Ebbing, seen in one cutaway | the dead mentor keeps away from the place where the dead are seen off, as the tell that he is dead | Re-staged (f): a practical cause on screen, and the clue is removed from his tells. Pass. |
| Light (g) | The rope-burns leak held cyan, from Ch10 on, never at Corrow; lift only from H09 | (none) | *Consistency* (S5) with color script rule 1. Pass. |
| Back (S7) | Sefir and his wife Kesh: she sings herself in as the first heart, and he stays outside, undying | the first of the ritual's pilgrims and her husband: one spouse is the first sacrifice, and the other stays on, undying, as keeper at the ritual's last site | **Accepted, with reasons:** (1) the marriage is the bible's thematic spine ("a man who could not let his wife go", §1). Recasting Kesh as his sister would duplicate Pell and Ressa. Recasting her as his student would turn his refusal into pride, not grief. (2) Sefir is **not the keeper at the last site**: he lives at Ansedra, the Choir has no keeper, and he arrives there in Ch16 as a visitor. (3) He never presides over or guides the final rite, and he never asks anyone to sing him in (0016). (4) The spouse who was sacrificed wants it ended and hid the Eighth Verse against him; she is the thesis, not the instrument. (5) SPEC §3.3–3.4 fix the founders binding themselves and Sefir as a centuries-old revenant who wants the heart. **Watch:** Sefir is never staged as the Choir's resident keeper, and Kesh is never offered as a summon that ends the storm. **Lead.** |
| 3 (S8) | Rhen recognises the first verse as his father's lullaby | the hero recognises the hymn sung in every temple | **Accepted, with reason:** the Order hums and never sings (bible §4), so our verse is not a temple hymn heard by everyone. Its tune is known in two households in the world. Recognising it is the literal thread between the two families (N-11), and since (a) it is also how Imra and Dace knew each other on the stair. 0017's Ch3 row gains this reason. Pass. |
| 16 (h) | Kerrid walks last behind Asha; "I carried her up so you could do this" | the mentor's fury at the ritual's keeper at its last site | Re-staged in 0020. **Watch** (h): the line is said, not drawn; no steel; he doesn't lead the refusal. Pass. |
| End (i) | E2: Dace sees Kerrid, the missed reach, a shake of the head; then only his son | (none) | No analogue. Rule 1 holds (a look, not a goodbye). Pass. |
| Pro (k) | VO direction: plain fact, not foreboding | the opening line's foreboding frame | It supports 0020 (g). Pass. |
| Ending light (k) | palette exception for E4 0.07 and E5 0.06 | (none) | *Consistency* (NAR-08 S1). Tested. Pass. |
| Liss (k) | Line-marks on the right arm; mesh sleeve on the left | (none) | *Consistency* (NAR-08 S2). Pass. |

**Watches (for Cinematics and later Narrative work):**
- No scene shows Dace and Imra together before the storm, and no line implies they travelled together.
- Kerrid has no Order rank, decoration or title in any line. Nobody outside Corrow's old watch knows his face.
- No gold light on Kerrid before H09, and no rope-burn glow in Ch5 or Ch8.
- At the Choir Kerrid draws no steel, and Sefir is never the Choir's keeper.

## Consequences
- **Narrative (done in M1-NAR-11):**
  - bible §3 (the 1001 row), §5.4 (Corrow and the stair-watch) and §6 (the Velamir lullaby);
  - act_outline: the Prologue, Ch8, Ch9, Ch13, Ch14, Ch15, Ch16, Ch17 and the Ending;
  - act3_ending: §0 rule 2, the Ending preamble, E2 and E3;
  - characters: Kerrid, Rhen, Asha, Toma, Sefir and Liss;
  - vertical_slice: the Ch2 stillness and the Ch3 choice note;
  - voice_guide: Kerrid's diction and samples, and Sefir's stale "Your guardian died here" sample;
  - decisions_log N-23 (N-21 marked accepted);
  - glossary (appended);
  - the ch02 and ch03 `.dlg` source comments (no line text changes);
  - dialogue_format.md (Ch15).
- **Art and Rendering (done here at the Lead's direction, for Art to review):**
  - palette.json `sea_glow_rule` and its structured exception, with a test;
  - color script `ch08` (no rope-burn glow at the stair foot), `ch15` and `ending_unbinding` (lift from H09).
- **Cinematics:** the Ch8 fishwife staging; the Ch9 stair-foot cutaway; Kerrid last onto Merel's barge in Ch14; the Ch16 watch; the E2 look.
- **Character Art:** Kerrid's watch cord in faded watch-red, not Stillguard red; his rope-burns emit `glimmer_held`, not gold; Liss's line-marks on the right arm.
- **Audio:** no cue changes.
- **Lead:** sign off (a) and the S7 acceptance.
- **Supersedes:**
  - in 0020: (a)'s "Stillguard captain" and "Imra and her guardian Dace ... his guests"; (b)'s "Stillguard stair-law"; (c)'s "the gold shader cue"; (d)'s Ch6 reason ("the Order knows his face ... Hero of Corrow"), its Ch12 "every Stillguard cadet", its Ch16 "the place he once sent Imra", and its Sefir "the Order's dead Hero of Corrow"; and the rows "Back: Kerrid, Corrow's Stillguard captain" (now the watch captain) and "Back: Dace was Imra's guardian" (now re-staged);
  - in decisions_log: N-02 item 4's "her mother's guardian"; N-11's "Dace met her" and "why he went with her as a guardian"; N-21's "Stillguard captain" and "guests for eight days".

- 2026-10-23 Lead: accepted as written, including Sefir and Kesh as the founding couple and the Ch3 song recognition, for the reasons given.
