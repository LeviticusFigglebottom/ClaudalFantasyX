---
id: M1-NAR-08
title: Remaining IP near-miss, ending consistency, staging (review-sweep-C)
role: narrative
status: review
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
