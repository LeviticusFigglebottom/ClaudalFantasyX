---
id: M1-NAR-08
title: Remaining IP near-miss, ending consistency, staging (review-sweep-C)
role: narrative
status: doing
reviewer: cinematics
owner_session: "worktree-agent-ac18e8281253ab668"
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
