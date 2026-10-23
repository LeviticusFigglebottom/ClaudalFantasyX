---
id: M1-NAR-09
title: Act I echo audit (Ch1-Ch8): Sefir's tournament introduction, the seawall operation
role: narrative
status: done
reviewer: cinematics
owner_session: "worktree-agent-a62a3327575b9aaf4"
depends_on: [M1-NAR-08]
milestone: M1
request-from: "lead"
---
## Goal
ADR 0016 audited Ch9 to the ending. NAR-08 flagged two Act I beats that echo the inspiring game, and the rest of Act I has not been audited the same way.

## Acceptance criteria
- [x] Sefir is not introduced at the Ch7 tournament (the inspiring game's cleric arrives at its sports tournament); move his first appearance to Ch5 or Ch8 or another non-echoing beat
- [x] The Ch8 seawall assault is re-staged so it is not "an allied military operation using forbidden machine weapons against the monster, which fails" (the inspiring game's coastal operation)
- [x] A beat-by-beat echo table for Ch1-Ch8 in a new ADR (next free number), in the style of ADR 0016, with every risk resolved or explicitly accepted with a reason
- [x] Story docs, glossary (append-only), decisions_log, and the colour-script and art notes kept consistent; .dlg files compile

## Notes
Lead signed off ADR 0016 on 2026-10-23.

2026-10-23 (narrative, worktree-agent-a1c60c801e373ac96): done in [ADR 0017](../../decisions/0017-act-one-restaging.md), decisions_log N-20. Sefir now first appears at the end of the Ch6 Brine Shoals raid, on his Edict progress. The Ch8 seawall is an evacuation up the Fisher Stair, with no weapon and no forbidden machine. The audit also re-staged:
- the Ch7 Tidecup: no Order official, and Rhen dives for Oruvel's side under Tavi Orse instead of Toma captaining Haluna;
- the Ch4 ferry: it is never attacked, and the party boards a dead trader for its name-board;
- the Prologue: no campfire circle, and Rhen walks among the separate vigils.

Residuals accepted with reasons in the ADR: the SPEC-fixed prologue line, the Haluna island-village start, the Ch3 emergence (with a watch), the father's song in the storm, the roster archetypes, Toma's guilt toward the Saltwrights, the element order (0015), and SPEC's own Act I order. For review: Cinematics checks the staging; the Lead signs off on the ADR (it is `proposed`).

**Sweep-E changes (narrative, worktree-agent-a62a3327575b9aaf4, 2026-10-23):** [ADR 0020](../../decisions/0020-kerrid-restaging.md) (`proposed`; the rows marked **Lead** need sign-off), decisions_log N-21 and N-22.
- **B1 (Kerrid):**
  - **Death:** he was never Imra's guardian. He was the Stillguard captain of the Corrow wall. In 1001 Imra and Dace were his guests for eight days. When the storm came he held the Fisher Stair open, got them both up, and died at its foot holding the hand-line. Dace reached back and missed. He never went to the Choir or fought Sefir.
  - **Bond:** a watch, not promises. The stair-law is "first down the stair, last up it". He never watched Asha or sought Rhen.
  - **Face:** bare and weathered, both eyes clear, no mask. His scars are rope-burns on his hands and forearms (his death-wounds; the Ch15 motes leave through them), and the left forearm is wrapped.
  - **Chapters:** Ch5 "I held a stair for your mother once". Ch8: he works the stair's foot, and a fishwife says "Captain?". Ch15: the confession is about Corrow. Ch16: he walks last on the Rim; there is no "spot where he died" (it is at Corrow), and he says "I carried her up so you could do this".
  - **Ending:** Imra, Dace, then **Kerrid last**, by the stair-law ("Stair's clear." then "Stand up straight. Your father slouched.").
  - Updated: kerrid.md, the other character sheets, act_outline, act3_ending, the bible (§3, §5 unrisen, §5.4, §10), voice_guide, glossary (appended), and color script `ending_unbinding`.
- **S1:** the Ch7 island-side shape is an accepted residual. Oruvel's side withdraws after its opening round, win or lose, and Tamsule's side wins the cup offscreen.
- **S2:** "I knelt beside your mother" is accepted, with reasons in 0020 (i).
- **S3:** at the Lead's instruction (the human approved), the Prologue line is replaced by **"Everyone I'm going to tell you about is still here tonight. Remember that, later."** 0020 (g) gives the three candidates. It is in act_outline (Prologue, Ch19) and rhen_sallow.md. There is no `.dlg` or loc key yet. The SPEC edit is the Lead's.
- **S4:** "at the Iskarra vigil".
- **Watch:** Toma's Stillguard hold the stair and are never on an offensive (act_outline Ch8).
- Validators are clean: validate_data, tools tests (291 OK), taskboard, and dlgc. The Godot dialogue tests pass 48/48.

## Review log
- 2026-10-23 cinematics + IP check (review-sweep-E): **request-changes.** I read ADR 0017, act_outline.md Prologue-Ch9 (:11-103), Ch15-16 and the Ending, the character files (rhen, sefir, toma, liss, kerrid), decisions_log N-20 (:140-147), the glossary rows, color_script ch06 (:296), the ch03 `.dlg` watch comment, and the 6703678 diff. dlgc is clean.
  - **What works.** The two named echoes are resolved well:
    - Sefir first appears at the Ch6 burning, as a mercy that costs him nothing, and nobody from the Order is at the Tidecup.
    - The seawall is an evacuation with no weapon, failing at the margin.
    - The ferry boarding and the Prologue vigil are convincing re-stagings.

    These accepted residuals are justified as reasoned: the Haluna island start, the Ch3 temple shape (with its watch), the father's song (Dace is not the storm), Toma's guilt, the element order, and SPEC's own Act I order.
  - **Blocker B1: Kerrid's roster row (0017:106) passes a near-copy of the inspiring game's dead mentor.** SPEC §3.4 fixes only "silent, scarred ronin-like warrior who knew both Rhen's and Asha's parents; secretly unsent; reveals it in Act II". Everything else is our choice, and it follows the original point for point:
    - he guarded the last sacrificial pilgrim alongside the hero's father (kerrid.md:7);
    - he understood too late at the ritual's final site, drew steel on the man responsible, and was killed (:7);
    - he is kept walking by **two promises, to watch over the heroine and to bring up the hero** (:9);
    - the face cues match: the lower face covered, one ruined eye, a facial scar (kerrid.md:26, :28);
    - in Act I he joins the daughter with "I travelled with your mother" (act_outline.md:62);
    - later he returns to the spot where he died (:158) and is the first to depart in the finale (:203).

    The row checks only the introduction, the costume props and the confession's staging. Fix:
    - re-stage the death and the promise structure. For example, he died in the storm after the Choir pulling someone out, not by attacking Sefir; or he made one promise, to Imra, about Asha only; or he stays because he refused to lift, not because of a vow.
    - change one of the two face cues (the half-mask or the clouded eye).
    - add rows for the backstory, Ch16 and the Ending, and have the Lead sign them off.
  - **Should-fix S1: the Ch7 shape is not in the table.** At the tournament, the newcomer fills in as the missing player for a small island side (act_outline.md:81-82). That is still the inspiring game's shape, minus the guardian-captain. Record it as an accepted residual. Pin the outcome too: Oruvel's side must **not** win the cup, because the long-losing team's first win is the inspiring game's beat. A loss, or a match played out with no cup, fits "for the ones who didn't come up".
  - **Should-fix S2:** "He tells Asha he knelt beside her mother" moved with Sefir from Ch7 to Ch6 (act_outline.md:73; sefir_aurane.md:18). The cleric's warm first meeting that invokes the heroine's sacrificed parent is part of the inspiring game's introduction, and the table doesn't list it. Accept it with a reason (it now lands at a burning, as mercy), or move the line to Ch13.
  - **Should-fix S3:** the Prologue line is accepted "as the human's brief" (0017:83). It is the one near-verbatim text echo of the inspiring game's opening line, and CLAUDE.md §2 bans that game's text. SPEC fixes the line, so only the human can change it. Put it in STATUS.md's questions for the human instead of accepting it in an ADR.
  - **Should-fix S4 (consistency):** act_outline.md:102 still says "a Rhen voice-over at the Iskarra fire". The Prologue no longer has a fire (ADR 0017 (e)): make it "at the Iskarra vigil".
  - **Watch:** Toma "fights beside his old Stillguard comrades" (act_outline.md:93), and his Ch9 side scene finds "an old Stillguard friend among the dead" (:103). Together they loosely echo the temple soldiers lost at the inspiring game's coastal operation. That's fine now the operation is gone. Keep the Stillguard defending the stair, and never on an offensive.
- 2026-10-23 cinematics + IP check (review-sweep-F): **approve-with-fixes.** I read SPEC v1.1 §3.4–3.5, ADRs 0015, 0016, 0017 and 0020 (accepted), the whole act_outline, act3_ending, every character sheet, bible §3/§5/§5.4/§10, voice_guide (Kerrid), decisions_log N-20 to N-22, the glossary's appended rows, color_script (prologue, ch08, ch15, ch19, ending frames), haluna.md H05/H10, and the ch02 and ch03 `.dlg` files. validate_data 0/0, tools tests 300 OK, `dlgc --check` 0/0.
  - **B1 from sweep E is resolved.** Kerrid's four strongest echoes are gone. His death is a storm defence at a fortress the player has seen, not a duel at the ritual's end. A watch replaces the two promises. His face is bare with both eyes clear. He goes last, by his own stair-law. The Ch16 "return to where he died" is gone with it. S1–S4 and the watch are done: the Ch7 outcome is pinned (0020 (h)), "I knelt beside your mother" is accepted with reasons, the line is "at the Iskarra vigil", and the Stillguard only hold the stair.
  - **Prologue line (SPEC.md:77): pass.** "Everyone I'm going to tell you about is still here tonight. Remember that, later." shares no words or sense with the inspiring game's opening line, only the mandated frame narrator at the ruins. It also reads true on replay, because the held dead are still in the world until H09. Suggest a VO direction note saying so.
  - **Should-fix S1 (IP, new with the re-staging): Kerrid is now a celebrated soldier of the church.** He is "the most decorated Stillguard captain of his generation" (kerrid.md:7), "the Order's dead Hero of Corrow" (kerrid.md:22, :44; sefir_aurane.md:37; 0020:57, :63), and every cadet learns his story (bible.md:108; toma_okeru.md:36). The inspiring game's mentor is likewise a famous former warrior of the church whose name precedes him. This also undercuts 0017's Ch5 watch, "no-one names him as a legend" (0017:90, :114), and makes him a second ex-Order soldier beside Toma. Fix: make him captain of Corrow's conscripted fisher stair-watch (bible §5.4 already has conscripted fishers), not a decorated Stillguard officer, and drop "Hero of Corrow". Or add a 0020 row that accepts it with a reason.
  - **Should-fix S2 (consistency, new): Toma's timeline.** toma_okeru.md:7 has him join at 16 and serve eight years "at Corrow and Ansedra". At 31 now, that is about 997–1005, so he was a serving Stillguard, possibly at Corrow, in 1001. That conflicts with "knew Kerrid by reputation ... every cadet learns" (toma_okeru.md:36; kerrid.md:23) and with his not recognising Kerrid until Ch12. Pin it, for example: he was posted at Ansedra in 1001 and came to Corrow after. Also fix the older conflict: asha_velamir.md:34 has him her oath-guardian since she was nine, but toma_okeru.md:7 has him take the oath when she was named at fifteen.
  - **Should-fix S3 (consistency, new): who knows his face?** "The Order knows his face" (0020:57) and Sefir recognises him in Ch6 (sefir_aurane.md:37), and the Order "would Still him on sight" (kerrid.md:44).
    - Sefir then hosts the party in Ansedra for days (act_outline.md:135-141). Say why Sefir lets him be, and where Kerrid is during Ch13-14.
    - At Corrow, Toma's old Stillguard comrades are on the wall (act_outline.md:94) while their dead captain works the stair foot and a fishwife says "Captain?" (:95). The watch at 0020:118 needs staging: storm-dark, waist-deep, with Toma above and out of earshot. Otherwise the Ch12 breath beat is cheap.
  - **Should-fix S4 (motivation gap, new): why does he stay after Ch8?** His want is "to be at the stair when the sea comes" (kerrid.md:18; 0020:46), and that is spent at Corrow in Ch8. Nothing says why he walks on with the pilgrimage from Ch9 to Ch16. One line would do it: for example, Imra's daughter is walking to the same Choir, and a captain doesn't come off the wall while someone is still below.
  - **Should-fix S5 (light grammar).** kerrid.md:31 says his rope-burns "glow faintly gold", but gold is `glimmer_lift`, which means released (color_script rule 1). color_script.md:465 has the motes leaving his hands in Ch15 as `glimmer_held` cyan. An unrisen's anchored light should be held cyan (or get its own swatch) until H09. Also keep the cue out of the Ch8 stair-foot shots so the clue isn't spent early.
  - **Should-fix S6 (IP, residual not audited).** The planted clue is that the unrisen mentor keeps away from the rite that releases the dead: "he never stands near the Ebbing" (kerrid.md:22), and he is gone before Ch9's Ebbing (act_outline.md:104). The inspiring game's dead mentor likewise keeps away from the place where the dead are seen off. No ADR row covers it. Accept it with a reason, or give his absence a practical cause on screen (for example, he is on the wall-head bringing up the bodies).
  - **Should-fix S7 (IP, residual not audited; pre-existing).** The founding couple: Sefir is the undying keeper of the rite, and his wife Kesh sang herself in as its first heart (sefir_aurane.md:7, :9). That mirrors the inspiring game's first summoner and her husband: one spouse is the first sacrifice, and the other stays on, undying, as keeper at the ritual's last site. 0016's Ch16 row checks only Kesh's role at the Choir. SPEC §3.4 fixes Sefir as a revenant who wants the heart; it doesn't make Kesh his wife or the first heart. Add a row and accept or re-stage it (for example, Kesh as his sister or his student).
  - **Should-fix S8 (IP, record).** In Ch3 the hero recognises the temple's sacred song from his own past (act_outline.md:44). The inspiring game's hero also recognises the hymn sung in its temples. 0017:88 lists "a hymn sung in every temple" as the analogue but not the recognition. I think ours holds, because the lullaby is the literal thread between the two families (N-11). Write that reason into the row.
  - **Note for the Lead (not a blocker).** With Kerrid off the guardian role, the largest echo left in the game is Dace: the hero's father, guardian of the heroine's sacrificed parent, who went into the calamity's heart for her and is found at its core in the finale (0020:102, accepted by the Lead). SPEC fixes that Dace vanished into the Undertow and that Rhen gets his goodbye. It does not fix the guardianship. A cheap lever: Dace walked with Imra unasked, never sworn ("her mother's guardian" at ch02_girl_on_the_beach.dlg:9 would become "the wright who walked with her mother"). This is the Lead's call.
  - **Watch (Ch16).** "I carried her up so you could do this" should be said, not drawn. Kerrid draws no steel on Sefir and does not lead the refusal at the Choir. He holds the line once the storm wakes. The mentor's fury at the ritual's keeper at its last site is the residual shape here.
  - **Nits:**
    - "the place he once sent Imra" (act_outline.md:161; kerrid.md:23; 0020:61): he didn't send her.
    - decisions_log.md:154 still says 0020 is "proposed for Lead sign-off", but it is accepted.
    - tech/dialogue_format.md:53 says "Kerrid in Ch14"; voice_guide.md:10 says Ch15.
    - SPEC.md:522 cites ADR 0021, which is not on this branch.
- 2026-10-23 lead: closing on review-sweep-F approve-with-fixes; the remaining items are in M1-NAR-11.
