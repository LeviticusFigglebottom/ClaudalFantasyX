# 0042 — The Lead decides the open human items (delegated)

- **Status:** accepted
- **Date:** 2026-10-28
- **Roles affected:** all
- **Author role:** lead

## Context
On 2026-10-28 the human wrote: "If it's just decisions, you can make them in the best way you see fit if they adhere to the desired results." The desired results are ADR 0041: Act I as played, at final quality, with no greybox or placeholders. Five items were waiting on the human. The human can overrule any of them at any time with a new ADR.

## Decisions
1. **M2 review (SPEC §16 Q7): approved; the project scales up.**
   - The human's own playtest reports of 10-28 (the crash, the run, the stacked party, the grey Prologue, the beach staging) serve as the slice review.
   - Each report is a FAST-TRACK, and further playtest notes are handled the same way.
   - M3 work under ADR 0041 continues.
2. **Music (SPEC §16 Q3): keep the self-synthesized score and keep iterating.** Nothing is commissioned or bought.
   - The quality bar is enforced by checks: loudness within budget, click-free loop seams, deterministic renders, and every cutscene `@music` resolving to its real cue (M3-HER-1146).
   - The human's listening notes, whenever they come, become audio tasks.
3. **Asha's face: keep the current direction.** That is the MPFB2 CC0 base, heavily modified (ADR 0021), with the painterly close-up shading (ADR 0019).
   - Characters improves fidelity within that direction: grounded proportions, softer hair clumps, cloth that moves.
   - No restyle.
4. **M3-RND-02 (a GPU clock cap to stand in for min-spec): don't cap the clocks of the human's GPU.** Changing someone's hardware settings is out of scope and carries risk.
   - Min-spec is estimated with the Low preset plus resolution scaling on the PC.
   - Real min-spec numbers wait for a min-spec card.
   - Scene-change hitches (New Game 3.0 s, Ch2 2.0 s, the first fight 1.7 s, Ch1 1.3 s on the RX 9070 XT) are fixed in the game with prewarm and a covered load (a fade or a card). The target is ≤ 1 s of hidden frames.
5. **`main`: fast-forward it to the integration branch after each batch that passes the PC's full gate.** That means the Godot suite green (bar listed known reds), coverage ok, Blender identical, and every drifted shot viewed and approved. The first candidate is big15. History is never rewritten.

## Process note
- Track sessions that refuse the Lead's cross-session messages as instructions are replaced with a fresh session on the same branch. Their live log carries the context.
- slice-polish (`session_01KZCgTqxhHKjvMCm1dAosvZ`) is replaced this way on 10-28.
