---
id: M1-NAR-09
title: Act I echo audit (Ch1-Ch8): Sefir's tournament introduction, the seawall operation
role: narrative
status: review
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
