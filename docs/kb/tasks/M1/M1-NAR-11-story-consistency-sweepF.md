---
id: M1-NAR-11
title: Story consistency and residual echoes after the Kerrid re-staging (review-sweep-F)
role: narrative
status: doing
reviewer: cinematics
owner_session: "worktree-agent-afdcaea09c59ff37c"
depends_on: [M1-NAR-09]
milestone: M1
request-from: "cinematics"
---
## Goal
The review-sweep-F entries on M1-NAR-09 and M1-NAR-08.

## Acceptance criteria
- [x] Kerrid is not a famous Order hero or legend: captain of Corrow's conscripted fisher watch, no "Hero of Corrow" title (consistent with ADR 0017's no-legend rule)
- [x] Lead decision: **Dace is no longer Imra's guardian** (the hero's father guarding the heroine's sacrificed parent is the largest remaining echo and SPEC does not require it); re-stage their bond and update every doc that depends on it
- [x] Consistency gaps: Toma's 1001 timeline against knowing Kerrid only "by reputation"; Toma's oath age (nine or fifteen); who can recognise Kerrid's face (Sefir in Ch6, the Corrow wall comrades); why Kerrid stays with the party after Ch8; the colour of the rope-burn glow (gold means released, cyan means held)
- [x] Echo rows (in a new ADR at the next free number, or appended to ADR 0020) for: Kerrid avoiding the Ebbing as the tell that he is dead; Sefir and Kesh as the founding couple; Rhen recognising the temple song in Ch3. Each is resolved or accepted with a reason
- [x] palette.json night sea-glow minimum gets an explicit Ending exception (0.07/0.06), validated
- [x] Liss's line-marks on one arm consistently; nits: "the place he once sent Imra"; decisions_log still says 0020 is proposed; dialogue_format.md Ch14 should be Ch15
- [x] All .dlg compile; validators pass

## Notes
- 2026-10-23 narrative (worktree-agent-a34ff8effe727a250): everything is recorded in [ADR 0022](../../decisions/0022-dace-imra-strangers-sweep-f.md) (proposed) and decisions_log N-23. Append notes are on ADRs 0016, 0017 and 0020, and the glossary is appended.
  - **Dace and Imra:** strangers until the Corrow storm of 1001. Dace was Kerrid's hired diver, re-seating the stair-foot rings. Imra was there for the Coilspire trial, and Kerrid walked her to the temple each day. They never met. In the storm she went down the Fisher Stair into the sea for him, a diver she'd never met, and Kerrid died holding the stair for both. She gave Dace her comb to carry home to Asha (the new source of Asha's Ch2 stillness at the lantern). He began the hull at Hollowmere and sailed into the storm after her, to repay the debt ("first down the stair"). He never walked her road. Rejected: "walked with her unasked" (same shape) and "the boatman who refused" (no reason for the ask; a bystander).
  - **Kerrid:** captain of Corrow's conscripted fisher stair-watch, no Order rank, no "Hero of Corrow". The stair-law and "Stair's clear." are the watch's. His cord is the watch's, in faded watch-red.
  - **Consistency:**
    - Toma was at Ansedra 997–1002 and on the Corrow wall 1002–1009, and was sworn at Asha's naming at fifteen.
    - Only Corrow's old watch knows Kerrid's face. Sefir sees what he is, not who, and lets him be in Ansedra. Kerrid sits nights at the outer moorings and is last onto Merel's barge.
    - The Ch8 fishwife beat is staged storm-dark, with Toma out of earshot.
    - He stays after Ch8 because "Somebody's still below." (Ch9 dawn).
    - The rope-burns leak `glimmer_held` from Ch10 on, never in Ch5 or Ch8, and lerp to lift at H09.
  - **Echo rows:**
    - The Ebbing: re-staged with a practical cause (he brings up the drowned at the stair foot), and the tell is dropped.
    - Sefir and Kesh: accepted with reasons (Lead to sign off).
    - Ch3 recognition: accepted with reason.
  - **Palette:** `sea_glow_rule` names the exception, and structured `sea_glow_night_exceptions` is checked by the new `tools/tests/test_palette_rules.py` (validate_data has no palette checks).
  - **Liss:** line-marks on the right arm.
  - **Nits:** fixed. The .dlg changes are comment-only, with the same line count, so the compiled JSON is unchanged.
  - **Not done:** SPEC.md:522 cites ADR 0021, which is reserved for the MPFB2 ADR (Lead/character). No edit.

## Review log
- 2026-10-23 cinematics + IP (review-sweep-G, fresh reviewer): **request-changes.** I read CLAUDE.md §2, SPEC v1.1 (§1-§3.5), ADRs 0015, 0016, 0017, 0020 and 0022, and then act_outline, act3_ending, bible, vertical_slice, voice_guide, decisions_log, glossary, every character sheet, color_script (`ch08`, `ch15`, `ending_unbinding`), palette.json `global_rules`, haluna.md, and both `.dlg` files with `dialogue.csv`. `validate_data.py` gives 0 errors and 0 warnings, `unittest discover -s tools/tests` gives 322 OK (including `test_palette_rules.py`), and `dlgc.py --check` gives 0 errors and 0 warnings.
  - **What passes:**
    - **Kerrid has no title.** "Hero of Corrow", "decorated", "cadet" and "Stillguard captain" are gone from every live doc. The remaining hits are struck through or superseded: ADR 0020:35/57/59/63, which have append notes; decisions_log:155, struck inline; and glossary:240-244, which is corrected by appended rows :247-251, as the append-only rule requires.
    - **Who can recognise him** is consistent across the outline, kerrid.md, toma_okeru.md and sefir_aurane.md: act_outline:95, :136, :148; kerrid.md:25-31; toma_okeru.md:36; sefir_aurane.md:37.
    - **The rope-burn light** is `glimmer_held` from Ch10 on, absent in Ch5 and Ch8, and lerps to lift at H09. It agrees in kerrid.md:45, color_script:334 and :465, act_outline:156 and act3_ending:96.
    - **Liss's line-marks** are on the right arm in both paragraphs (liss_varrow.md:7, :23).
    - **The palette Ending exception** is named in `sea_glow_rule`, stored as structured data, and tested against act3_ending rule 4 and the colour-script row. Color script rule 3(a) (color_script:40, :47) agrees.
    - **The nits are fixed.** "Sent Imra" is withdrawn, N-21 is marked accepted, and dialogue_format.md:53 says Ch15.
    - **"Somebody's still below."** has the same wording in act_outline:105, kerrid.md:28, voice_guide:74 and ADR 0022:67.
    - **Toma's timeline in the docs** is coherent: born 981, Ansedra 997-1002, Corrow 1002-1009, the burning in 1003, sworn in 1009 at 28, and 31 now. Asha's sheet (asha_velamir.md:34) matches.
  - **Blocker B1 (consistency, shipped slice line). Toma says he was at Corrow in 1001.** ch03_the_first_verse.dlg:52 (`ch03_verse_010`, dialogue.csv:46) has Toma say of Imra's verse in 1001: "I was on the wall at Corrow. I came home after." ADR 0022 (d) puts him at Ansedra until 1002, and home only in 1009. The task notes say the `.dlg` edits were comment-only, so this criterion is met in the docs but not in the game text. Suggested line: "I was at Ansedra, at the temples."
  - **Blocker B2 (consistency and IP). Toma has "guarded her since she was nine".** ch03_the_first_verse.dlg:75 (`ch03_verse_024`, dialogue.csv:60) and vertical_slice.md:93 keep "I have guarded her since she was nine." ADR 0022 (d) withdraws that: at nine (1003) he was on the Corrow wall. It is also the inspiring game's guardian-since-childhood beat, which sweep F set out to remove. AC 3 ("Toma's oath age") is not met in the shipped text. Re-anchor it to his leave visits, for example "I have known her since she hid in the net racks from me. I have guarded her three years."
  - **Blocker B3 (IP, unaudited echo). Asha met Rhen's father as a child.** The new backstory has the heroine meet the hero's father when she is a child, and in Act I she connects him to the hero (ch03_the_first_verse.dlg:149, `ch03_verse_051`: "Your father. The one with the lantern."). ADR 0022:105 lists this row as "(none: a consistency knock-on)". The nearest analogue is the inspiring game's heroine, who met the hero's famous father as a child, when he passed through her island on her father's pilgrimage, and makes the link to the hero early, on that island. The delivery adds a second, weaker echo: a stranger carries the sacrificed pilgrim's charge home to the child's island (ADR 0022:35-36).
    - **Needed:** an echo row with a Lead verdict.
    - **My recommendation:** keep the Ch2 stillness wordless, and cut `ch03_verse_051`/`052` so Act I never voices the link. The link then surfaces only in Ch15 ("A man with that lantern brought me this. I was seven."). Asha never knew his name, so the beat is ours if it stays unspoken until the confession.
  - **Should-fix:**
    - **S1 (IP). Dace and Kerrid drink together.** "For eight nights they drank together" (kerrid.md:9, :38, :56, :59; rhen_sallow.md:39; ADR 0022:32, :38; decisions_log:155). The hero's father's drinking is one of the inspiring father's signature traits, and the beat pairs the mentor and the hero's father as companions. Make the bond work instead, for example eight low tides at the rings together, with Kerrid holding Dace's line. Keep "Dace slouched".
    - **S2 (IP). Kerrid escorts Imra every day.** "Kerrid walked her up the headland path at every dawn and back at every dusk" (kerrid.md:9; ADR 0022:33; act_outline:156 "eight dawns walking a Cantor to Coilspire"). That puts back a slice of the mentor escorting the sacrificed parent on her pilgrimage. Make him the man who opens the wall-gate she passes through, so they speak at the gate and he never walks beside her.
    - **S3 (IP). "Somebody's still below." is staged with Kerrid "looking at Asha ahead".** That is at act_outline:105, kerrid.md:28 and ADR 0022:67. Read that way, the mentor takes over the heroine's protection on her pilgrimage, which is the function ADR 0020's Bond row removed. Stage him looking south, out to sea, so "below" means Imra under the storm and the held dead, not Asha. The watch is then not a guard on the heroine. Add the row to the 0022 table (9 (e) only clears "promise").
    - **S4 (consistency). The Ch9 cutaway puts Kerrid among his old watch.** He works "with the old watch" all night (act_outline:104, kerrid.md:28, ADR 0022:71), yet they are the only people who know his face (0022 (c)), and only the fishwife saw him in Ch8. Either stage him alone or among strangers, or make the old watch's silence an explicit beat.
    - **S5 (slice line). "He gave it back" has the wrong antecedent.** At ch03_the_first_verse.dlg:152 (`ch03_verse_053`), after `051` the line "I'd forgotten it until he gave it back" now reads as Dace, who under ADR 0022 did visit Asha at seven. The comment at :10 and decisions_log:46 mean Ilun. Name him in the line, or use "until tonight".
    - **S6 (pillar 1, E2 payoff). Dace never goes home to Rhen.** ADR 0022:37 and rhen_sallow.md:9 have him walk up Haluna's dock, a short sail from Oruvel (Ch1 to Ch2), and still not go home to a motherless eight-year-old. No doc says who kept Rhen from eight to nineteen. Give the Ch17 logs a reason the player can see, and name Rhen's keeper (Mother Kell?). Otherwise "Goodbye, Dad" rests on an unexplained abandonment.
    - **S7.** kerrid.md:57 says Toma "grew up there on the watch's story". He came to Corrow at 21.
    - **S8.** kerrid.md:17 says that "When a new Cantor was named, he started walking toward Corrow", but Asha was named in 1009 and he is still on the road in 1012 (Ch5). Tie the walk to the Undertow stirring.
    - **S9.** rhen_sallow.md:20 has Rhen learn Dace's motive "at the Drowned Choir", but act_outline:176 and ADR 0022 (j) put it in Dace's Ch17 logs, and Kerrid doesn't know it (kerrid.md:15). Align them.
    - **S10.** The heading at decisions_log:73 still says "Dace knew Imra before she was named". decisions_log:178 and this task's Notes still say 0022 is "proposed", but the ADR records the Lead's acceptance.
    - **S11 (Ending watch). Never frame the three dead together.** act3_ending:92: the inspiring game closes on its three dead together. Add a watch to act3_ending §0 that Imra, Dace and Kerrid never share a frame in E1-E3; E2's look must be a reverse, not a three-shot. At :92, "One look, no words" sits next to Dace's spoken goodbye, so write "Dace and Kerrid: one look, no words".
  - **Nits:**
    - voice_guide:79 ("Dace slouched. You slouch. Stand up straight before the end") uses up E3's line early. Mark it as a reference only, never to be scripted before E3, or cut it.
    - ADR 0016:92's append note says 0022 is "proposed". It is append-only, so leave it, but N-23 should carry the acceptance.
  - **Beat-by-beat echo judgement (residuals I concur with, unchanged):**
    - The Act I order, the tournament, the fortress, the wedding trap and heretic declaration, the airship opening the world, the dive and the final rite are SPEC-mandated (0016, 0017).
    - Sefir and Kesh as the founding couple is Lead-accepted. I concur with 0022's watches: Sefir is never the Choir's keeper, and Kesh is never the storm-ending summon.
    - The Ch3 recognition: concur.
    - 21 (a), Dace in the storm: concur. Given 0022's re-stage, the remaining skeleton ("eleven years ago the mentor, the hero's father and the sacrificed parent were together, the mentor died, and the father ended in the storm with her") is forced by SPEC §3.4's "knew both parents", so S1 and S2 above are about texture, not shape.
    - **Watch.** Ch7 ("Toma played here for Haluna as a boy", act_outline:84, toma_okeru.md:9) is a trace of the island-captain guardian. Keep it at one line.
    - **Watch.** Ch18's "heirloom weapon quests, one per party member" (act_outline:181) must not grow the inspiring game's crest-and-sigil ultimate-weapon structure.
  - **To clear:** fix B1-B3. Move the task back to review with the `.dlg` and loc line changes, and with the new ADR rows for B3 and S3.
- 2026-10-23 lead: reopened on review-sweep-G request-changes. Lead verdict on B3: cut ch03 lines 051/052 so Asha's link to Rhen's father surfaces only in Kerrid's Ch15 confession.
