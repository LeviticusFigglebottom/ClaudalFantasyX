---
id: M1-NAR-08
title: Remaining IP near-miss, ending consistency, staging (review-sweep-C)
role: narrative
status: review
reviewer: cinematics
owner_session: "worktree-agent-a62a3327575b9aaf4"
depends_on: [M1-NAR-05]
milestone: M1
request-from: "cinematics"
---
## Goal
Review-sweep-C (Cinematics) findings on NAR-05 plus ART-04 doc consistency.

## Acceptance criteria
- [x] IP: Ice no longer sits at the Order's seat right before the wedding trap/heretic turn (recreates the inspiring game's frozen-lake temple then wedding betrayal); re-sequence or re-theme so no element/temple/plot-beat triad echoes it
- [x] Ending: all glimmer releases in the same instant (SPEC §3.5); remove the Kite lamps' 10-minute dimming countdown; each farewell lit only by the leaving person's motes
- [x] Final image: Asha's smile is visible (re-stage the shot)
- [x] ch02 'Get up' branch continuity (Rhen is standing; no lying-down POV, no hand up)
- [x] Art docs: haluna.md S10 hold (not the 3 s blend); the night value order covers lamp/glimmer-keyed frames (Ch4, Ch5, the ending's lifting scene); ending sea-glow figures consistent (summary vs frame row vs act3_ending.md)

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

**Done (narrative, 2026-10-23):**
- **IP:** [ADR 0015](../../decisions/0015-vowbound-element-temple-order.md) and decisions_log N-15. Nhoa (Lowlight, Ch11) becomes **Ice**: a drowned sanctum in the deep's cold, with nothing frozen in it. Ethren (the Sanctum, Ch13) becomes **Glimmer**: the basin is a mirror lit by bound glimmer. Hesk (Cloudloom, Ch12) stays Holy, and Cloudloom is now a stone weaving-hall rather than a glacier cave. No chapter, zone or Cantor moved. From here on, nothing is ice, frost or frozen in any temple from Ch12 to Ch15. Updated: vowbound.md, bible §5.6–5.8, act_outline Ch11–13, act3_ending H09, the glossary rows plus an appended note, and color script `ch12`.
- **Ending (N-16):** the Kite's lamps and engines die at H09 along with everything else. The Kite glides dark through the Ending, and the countdown is now the stepped sea-glow (E1 0.15 → E2 0.11 → E3 0.08 → E4 0.04 → 0.0 in E5), the dead thinning, and the descent. The farewells are keyed only by the leaving person's motes. Kerrid's E1 cue is now his shadow; the breath fog is cut (sweep nit).
- **Final shot (N-17):** E6 is a locked three-quarter profile from the dock's side, so the smile reads. haluna.md H10 and color script `ending_dock` are updated to match.
- **ch02:** `offer_hand` and the sitting H05 now play only in the "Stay" branch. In the "Get up" branch Asha rises (`rise_to_stand`) and H05 is taken at Rhen's standing eye-line. haluna.md H05 is defined as Rhen's POV, following his eye. dlgc compiles cleanly, and the dialogue tests pass (47/47).
- **Art docs:** haluna.md S10 now specifies the hold (a cut on 043 and at least 6 s, no blend). Color script rule 3 now covers practical- and glimmer-keyed night frames: pools are exempt from (b), and (a) and (c) still apply. The `ending_unbinding` sea-glow is the same everywhere (0.15 → 0.0 in steps).
- **Not done (other sweep nits, out of scope):** Dace's battle-camera constraint (H04–H07), the ch03 `turn_back` nit, and the banned-list additions (which are the Lead's). The element glyphs in art `ui.md` (Ice a knot, Holy a ring) were authored against the old mapping. They are generic, so Art may want to revisit them.

**Sweep-D changes (narrative, 2026-10-23):**
- **B1:** [ADR 0016](../../decisions/0016-act-two-restaging.md) and N-18.
  - (b) The founding truth is now learned in Ch13's Lamp Archive, before the wedding: the founders' ledgers, the Cantor roll's *kept / spent* column, and the same signatures across four centuries. Ysolde's Corran maths moves there. The founders' records also leave Lowlight.
  - (a) The escape goes out across the lagoon on Merel's bridal barge, and Merel is taken for it. Venn is fought as a living-seeming man on the water, with no revenant reveal. Nothing goes under the city: Underreach and Cistern are cut as zones. Ch15 becomes "Unlamped" (the Wakefin, then Hollowmere at dawn, where Toma's faith breaks).
  - (c) Sefir's temptation at the Choir is "leave the Eighth Verse in the stones, go home, live". He never asks to be sung in; in Ch21 he takes the heart himself.
  - **Kerrid's reveal** is his own confession at sea in Ch15, as held dead drift to him. No Stilling is performed on him.
  - The ADR includes an echo check of every beat from Ch9 to the ending, plus two flagged residuals outside its scope (Sefir at the Ch7 Tidecup, and the Ch8 cannons).
- **S1:** the ADR 0015 order statement is corrected (Fire and Lightning are the same pair, swapped, and Ice is 4th). Nhoa's "snow" is now "silt". 0015 records that the truth beat left Lowlight.
- **S2:** act3_ending §0 rule 7 and bible §10 now say that everything is released at H09; what follows is ascent.
- **S3:** the sea-glow holds at 0.04 through E5. It reaches 0.0 only on the cut to E6.
- **S4:** E6 is now front three-quarter. The camera sits on the dock looking out to sea, and Asha turns back toward Haluna, ending about 40° off her nose line. The "H10 reversed" wording is fixed in act3_ending, haluna.md and the color script.
- **S5 and nits:** the "Stay" branch now resolves `offer_hand` (`take_hand`, then `rise_to_stand`) before the walk. "Get up" has a `@wait 0.8` before H05. The E3 lantern is unlit. dlgc compiles cleanly, and the dialogue tests pass (48/48).

**Sweep-E changes (narrative, worktree-agent-a62a3327575b9aaf4, 2026-10-23):** [ADR 0020](../../decisions/0020-kerrid-restaging.md) (`proposed`), N-21 and N-22.
- **S1 (Kerrid):** 0020 re-stages his backstory (he died at Corrow's Fisher Stair, not the Choir), replaces the promises with a watch, and adds echo rows for the Ch15 confession, Ch16 (no visit to where he died, because he died at Corrow) and the Ending. The order is now **Imra, Dace, then Kerrid last**, so he no longer goes first. act3_ending: rules 2 and 7, the running order, E1–E3 and R2–R4 are rewritten (durations unchanged). Appended notes point 0016 and 0017 at 0020.
- **S2 (Liss):** re-staged. Her father is Hollowmere's **dock-master**, not a chief, and a council of hull-captains governs Hollowmere. **Tobin volunteered** as the groom and was never an heir. The Kite coming from her people's dry-dock is accepted, with reasons in 0020 (f).
- **S3 (E6):** she starts side-on across the dock end, looking out to frame left with her left shoulder to camera, and turns about 50° to her left toward Haluna, ending 40° off the lens axis. The same blocking is in act3_ending E6, haluna.md H10 and color_script `ending_dock`.
- **Nit (hand):** in the Stay branch, Rhen takes the hand right after line 030, before Toma's introduction. The later block is removed. dlgc compiles cleanly, and the Godot dialogue tests pass (48/48).
- **Nit (E5):** E4 is now 0.07 and E5 holds at 0.06 (interpolated on/off about 1.45×, against 1.3× at 0.04), so the cut to E6's 0.0 is a visible step. This is in act3_ending rule 4 and E5, color script rule 3, `ending_unbinding` and the strip summary. Rendering should confirm it on the mood frame.

## Review log
- 2026-10-23 cinematics + IP check (review-sweep-D): **request-changes.** I read ADR 0015, act_outline Ch1–Ending, act3_ending.md, vowbound.md, haluna.md H05/H10/S10, color_script rule 3, and the ch02 .dlg. dlgc compiles, and tools tests give 247 OK.
  - **Blocker B1 (IP): the Act II run after the wedding still follows the inspiring game's sequence, beat for beat.** ADR 0015 checks only Ch11–13. Read in order, act_outline.md:124–142 is:
    1. a wedding trap in the church's holy city, with the party declared heretics (SPEC-mandated, fine on its own);
    2. a Warden boss at the wedding revealed as a revenant (:128);
    3. flight *below the holy city* through a drowned under-passage to an undead or bound-dead construct boss, then an escape (:131–136);
    4. a journey to the world's edge, where the founding truth of the ritual is learned (:138–141);
    5. the high cleric revealing he wants the heroine to make him into the calamity's power: "sing *him* in" (:142).

    That is the inspiring game's holy-city wedding, then the condemned sent beneath the city through a water labyrinth with an undead boss, then the truth at the ruined city, with the undead-cleric reveal and the "make me the calamity" motive alongside. SPEC §3.5 requires only the wedding trap, the heretic declaration, Kerrid's reveal and the Choir truth. Items 2, 3 and 5 are our own choices. Re-stage at least two of them, for example:
    - the escape goes *up and out* (across the lacquer roofs or by sea from the court) rather than beneath the city;
    - the Cistern truth is found earlier, by Liss's investigation in Ch13;
    - Malcor Venn's revenant reveal moves out of the wedding fight;
    - Sefir's motive is something other than becoming the storm's vessel.

    Extend ADR 0015's echo check (0015:39–44) to Ch14–16, or write a new ADR. This touches SPEC-adjacent beats, so the Lead should sign off.
  - **Should-fix S1 (IP): element order.** ADR 0015:44 says the order "matches neither ... beyond the shared opening on Water". But the inspiring game's elemental temple order is Fire, Lightning, Ice, then a non-elemental aeon at the holy city. Ours is Water, then Lightning and Fire (the same pair swapped), then **Ice at #4**, then Holy and the "special" element (Glimmer) at the holy city. Lowlight is also a half-underwater cold sanctum with snow-like motes (vowbound.md:46–49) where the ritual's founding truth comes out (act_outline.md:105). That is close to the "beneath the frozen lake, where the truth of the pilgrimage lands" image, even with nothing frozen. Correct the ADR wording. Then either move Lowlight's truth beat (the Lit Age records) to Ch10 or Ch12, or drop the snow simile for Nhoa (for example, "sifts like silt"). Ideally do both.
  - **Should-fix S2 (SPEC §3.5 "same instant").** After H09 the sea-glow steps down 0.15 → 0.0 over E1–E5 (act3_ending.md:15), and the dead "rise more thinly" scene by scene (:14). Diegetically, that reads as glimmer and souls still being released across ten minutes: the old Kite-lamp countdown in a new prop. Rule 6 (:17) restates the SPEC, but nothing reconciles the two. Say explicitly that everything is *released* at H09, and that what follows is the *ascent* of already-released motes, with `sea_glow` being those motes still rising, not bound light. Or hold sea_glow flat after H09.
  - **Should-fix S3 (final image).** E5 says the sea "goes fully dark for the first time" (act3_ending.md:99). That spends SPEC §3.5's "dark for the first time in a thousand years" before E6, and color_script.md:31 calls the absence of glow in the last shot "the payoff of the entire game". Keep 0.04 or more until the cut to E6, or drop "for the first time" from E5.
  - **Should-fix S4 (E6 framing, AC 3 at risk).** "haluna.md H10 reversed" plus "about 3 m off her right shoulder" (act3_ending.md:101; haluna.md:172) puts the lens on the dock, looking seaward, behind a woman facing the sea. That is a back three-quarter view: her smile won't read, and "her face against the star-filled sea" isn't possible from there. Pin it down: either the camera sits forward of her shoulder line (about 35–45° off her nose line, for example from a mooring post or the boat, with the shore partly in frame), or she turns side-on along the dock end as she draws breath. Give the angle relative to her facing, not her shoulder.
  - **Should-fix S5 (ch02 'Stay' branch continuity).** `@anim asha offer_hand` (ch02_girl_on_the_beach.dlg:67) is never resolved. No anim has Rhen take the hand or stand, so Asha holds her hand out through lines 79–89, and Rhen goes from sitting in the shallows to `@mark rhen beach_path walk` (:93). Add `@anim rhen take_hand_rise` (or similar) after line 79 or 84 in a shared `<<if $ch02_rhen_stayed_with_dead>>`, or a comment saying the H01 cut covers it. The 'Get up' branch (:68–78) is consistent: standing, leaning on Toma, no hand, and H05 at standing eye-line.
  - Nit: in the 'Get up' branch, `@anim asha rise_to_stand` is immediately followed by `@camera H05 blend=0.0` (:77–78). If `@anim` doesn't block, H05 opens mid-rise, but haluna.md:167 says she "has risen". Add a `@wait`, or note it for the sequencer.
  - Nit: E3 "the oil wick in his old lantern" (act3_ending.md:93). State that the lantern is unlit, so the farewell stays keyed only by Dace's motes (:83).
  - Done well: Ice is off Cloudloom and the Sanctum. The Ch12–15 no-frost rule is clear (0015:37). The grep finds no stray ice, frost or glacier text in story or art docs, apart from the generic glyphs in ui.md:160 the author already noted. S10's hold and the color script's practical-keyed rule are consistent.
- 2026-10-23 cinematics + IP check (review-sweep-E): **approve-with-fixes.** I read ADR 0016 (Lead-accepted), act_outline.md Ch9-Ending (:98-207), act3_ending.md §0 and E1-E6, color_script.md:31-47 and :603-624, haluna.md:172, ch02_girl_on_the_beach.dlg:55-100, and the dd051d5, 5b80162 and 35bf109 diffs. dlgc and the tools tests are clean.
  - **Every sweep-D item is addressed.**
    - B1: the escape goes out across the lagoon, and no zone is under the city. The wedding has no revenant reveal and no rite. The founding truth comes earlier, on paper in Ch13. The temptation is "go home", and Sefir takes the heart himself in Ch21.
    - S1: the 0015 order wording is corrected, and the simile is now "silt".
    - S2: rule 7 (act3_ending.md:18), released at H09 with ascent after, reconciles the stepped glow with SPEC §3.5.
    - S3: 0.04 is held through E5, with 0.0 only on the cut to E6.
    - S4: E6 is front three-quarter, with the angle given against her nose line.
    - S5: the Stay branch resolves the hand (`take_hand`, then both rise) before the walk. The 0.8 s wait and the unlit E3 lantern are in.
    - With these, the Act II run after the wedding no longer follows the inspiring game's holy-city → beneath-the-city → ruined-city chain.
  - **Should-fix S1 (IP, cross-cutting; see M1-NAR-09 B1):** ADR 0016 passes Kerrid on staging only (0016:65, :72). The *content* of his confession still follows the inspiring game's dead mentor:
    - he was killed confronting the man behind the ritual at its last site (kerrid.md:7);
    - he is kept walking by promises to the heroine's parent and the hero's father (kerrid.md:9; act_outline.md:152 "the promise that kept him walking");
    - "Kerrid finds the spot where he died" at the ritual site (act_outline.md:158);
    - he is the first to depart in the finale (act_outline.md:203; kerrid.md Ending).

    Add a Kerrid row to 0016's check that covers these beats, and re-stage or accept each with a reason. For example, Imra goes first and Kerrid goes last, or after Dace.
  - **Should-fix S2 (IP, unrecorded residual):** Liss is the chief wright's daughter and the younger sister of the flotilla's heir (liss_varrow.md:7). The party reaches her people's haven and her father (act_outline.md:153), and the ship that opens the world is built in that haven's dry-dock (:171-177). In the inspiring game, the outlaw tinkerer girl is the chief's daughter with an elder brother, and the airship comes from her father's people at their home. Ours differs in real ways: the brother dies, the ship is Dace's, and it comes after the Choir. 0016 has no row for it. Record it as accepted with a reason, or change one element (for example, Liss is not the chief's child).
  - **Should-fix S3 (E6 blocking):** act3_ending.md:102 says "The shot opens with her facing the dark sea, side-on to the lens". But the camera is 4 m shoreward on the dock, looking out to sea. Facing the sea from there, she has her back to the lens, and the two can't both hold. State that she stands across the dock end, facing the sea on one named side, so the turn back to Haluna lands at the stated 40°. Mirror the fix in haluna.md:172 and color_script.md:624.
  - **Nit:** in the Stay branch, `offer_hand` (.dlg:67) is held across six lines (030-034, then 014/015) before `take_hand` (.dlg:95), through Toma's formal introduction. It reads, but consider taking the hand after 030, or add a comment that she keeps it out on purpose.
  - **Nit:** color_script.md:47 says E4-E5 fall below 0.08 "because there the glow is meant to fade from sight". At 0.04 the on/off ratio is 1.3× (color_script.md:40), so E5's "nearly dark, but not yet" and E6's full dark may look the same. When the mood frame is built, Rendering should confirm the cut to 0.0 is perceptible, or E5 should hold nearer 0.06.
- 2026-10-23 cinematics + IP check (review-sweep-F): **approve-with-fixes.** I read ADR 0020, act3_ending.md (all of it), act_outline Ch14-Ending, liss_varrow.md, kerrid.md, color_script.md:31-47 and :590-624, palette.json:161, haluna.md:167 and :172, and ch02_girl_on_the_beach.dlg. validate_data 0/0, tools tests 300 OK, `dlgc --check` 0/0. See M1-NAR-09's sweep-F entry for the whole-story echo pass.
  - **Every sweep-E item is addressed.**
    - **S1 (Kerrid):** re-staged, and his ending order is now Imra, Dace, Kerrid last (act3_ending.md:13, :86, :96).
    - **S2 (Liss):** she is the dock-master's daughter, Tobin volunteered as the groom, and the Kite residual is accepted with reasons (liss_varrow.md:7; 0020 (f)).
    - **S3 (E6):** the blocking is now geometrically consistent. She faces frame left with her left shoulder to a shoreward camera, so a 50° turn to her left brings her toward the lens and ends 40° off it, a front three-quarter. The same wording is in act3_ending.md:104, haluna.md:172 and color_script.md:624.
    - **Hand nit:** the hand is taken right after line 030 (.dlg:82-90).
    - **E5 nit:** 0.07 and 0.06 agree across act3_ending.md:15 and :102 and color_script.md:31, :47, :80 and :603.
    - The timings still add up: the Ending is 14.5 min, and the family goodbyes take 7.5 min plus 2 min of rests.
  - **Should-fix S1 (consistency).** palette.json:161 `sea_glow_rule` still says ">= 0.08 once the sun is below -6 deg", with no exception. `ending_unbinding` E4 at 0.07 and E5 at 0.06 are night frames below that (act3_ending.md:15). color_script.md:47 makes the exception, but palette.json doesn't. Add it there (Art owns palette.json, so open a request task) so the frame isn't flagged later.
  - **Should-fix S2 (consistency, sheet edited in this task).** liss_varrow.md:7 puts her line-marks on her left arm and collarbone. liss_varrow.md:23 sleeves the left arm in mesh and shows the line-marks on the bare right arm, up onto her cheek. Pick one side.
  - **Nit (E3 light).** Once NAR-09 S5 settles the hue of Kerrid's rope-burn light, state in E3 (act3_ending.md:96) that his hand motes are `glimmer_lift` from H09 on, after rule 1's 1.5 s lerp from held to lift. Then the last farewell can't show cyan, held light after rule 7's single release.
