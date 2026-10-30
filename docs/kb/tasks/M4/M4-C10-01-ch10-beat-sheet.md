---
id: M4-C10-01
title: Ch10 "Fen of the Kirru" beat sheet (the first of Act II)
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: []
reviewer: cinematics
milestone: M4
request-from: act1-chapters
---
## Goal
The Lead approved starting the Act II greybox (Ch10 onward, M4) once Act I is at its quality bar (Lead, 2026-10-27).
act1-chapters builds the zones, flow and scripts the way it built Ch4–Ch9, from a beat sheet. Write the one for Ch10
"Fen of the Kirru" in `docs/kb/story/beats/act2_ch10.md`, in the format of `act1_ch09.md`: the chapter in one paragraph,
the running order with beat ids, each beat in detail (C cutscene, E in-engine, P play), flags (`ch10_*`, who sets and
who reads each), the side scene, the boss's placement and what it teaches, music cues, camera shots, word counts, and
requests to other roles.

From `act_outline.md` (Ch10): zones `ch10/ossa_fen` (mangrove channels) and `ch10/reedhollow` (the Kirru village);
Pell isn't allowed in; the Kirru farewell-tide at dusk (the clutch sings, turns its back, the motes lift straight up
into the stars; Asha can't stop looking); the boss, the Mangrove Drowner (spawn in the roots, two phases; creatures
has it as M3-CRE-621); the side scene, a Kirru child asking Asha why humans make their dead swim. Ch9's beat sheet §10
lists what Act I hands over (the party of seven, the S3 sleeve, three Vowbound, the flags Act II reads, Ch10 opening
at Ossa Fen's edge at dusk).

## Acceptance criteria
- [ ] `docs/kb/story/beats/act2_ch10.md` exists, every outline beat placed, timed and tagged C/E/P.
- [ ] Flags named `ch10_*` with setter and reader, and the Act I flags it reads.
- [ ] Each request to another role (env-art's fen and village kits, audio, creatures, characters for the Kirru)
      is listed with enough detail to file as a task.
- [ ] `python3 tools/validate_data.py` and the banned-terms grep are clean.

## Notes
- 2026-10-30 (act2-plan track, the Lead's assignment): **draft: pre-gate** written at `docs/kb/story/beats/act2_ch10.md`. It is not reviewed; the task stays `blocked` until the gate, then the story track takes it to review.

## Review log
- 2026-10-30 **cinematics (slice-polish → Act II cinematics, ADR 0205), staging review of the pre-gate draft.** The
  sheet's staging serves its beats; §0's five rules hold in every listed shot. Changes I ask for, by beat:
  1. **B09, the score and the release (blocking for M4-A2P-070 and M4-A2P-090).** The Ebbing's gate pauses scene
     time while the music runs on (ch09_the_ebbing.dlg), which works there because nothing lands on a note. Here the
     clutch's turn (T04) must land on the held top note, and the player sets it off by letting go. So `farewell_tide`
     can't be one 90 s file: it needs (a) a **gathering section that loops** (or holds a drone) for as long as the
     player keeps holding through T02–F02, and (b) **the top note and its tail as a separate stem or cue**, started
     on release. Audio, please build it that way; I will cue the tail on the release (`@music farewell_tide stem=N`
     or a second cue id). Without that split the top note either passes while the player isn't holding or waits in
     silence.
  2. **B09, "Release" (new mechanic, mine):** a second gate kind, `<<event release_input release>>`: it opens only
     while the action is held (the hold gate before it guarantees that), shows "Release", and the scene goes on
     when the player lets go. No timer, no fail, as the Ebbing. I am building it now in `game/cutscene/`.
  3. **T04's framing:** shoot F02 and T04 from the shore, behind and above the party (35 mm, not 50 mm: an arc of
     twenty to thirty can't be held at 50 mm from the shore). The clutch faces the lagoon in F02, so when it turns
     all at once in T04 thirty faces come round toward the camera and the party, with the motes still climbing
     behind them. That leaves the party as the only people still facing the water, which is T05's question to
     Asha. The camera never crosses to the water side (that would be the dead's side, watching them).
  4. **T02–T04:** the lift field sits over the lagoon at least 6 m from the arc's nearest Kirru, so the spiral's
     radius never carries a mote toward the singers (rule 1, "none toward anyone"). I'll check it in the stills with
     the upward-heading test rendering asks for.
  5. **O02 (one continuous move):** a backward track ahead of the line, the line walking toward the lens, so Pell's
     stop is seen from the moving line and he shrinks behind them without a cut. The layout's shots are fixed, so I
     am adding `@camera <shot> track=<actor>` (the shot keeps its offset to the actor, here Toma, the line's
     leader). The move ends as Rhen turns. Pell's answer may then cut to a long-lens single from Rhen's side (the
     stop itself has already been seen uncut).
  6. **R02, the eldest's look at Kerrid:** prefer one held single on the eldest whose eyes move across the party
     off-screen (equal beats per hero) over cut singles of each hero. A cut to Kerrid would comment on him (rule 4);
     her crest lifting a little on his beat, in her own shot, is the whole moment.
  7. **O06 ("holds until the last mote has left the top of frame"):** I am adding `@wait vfx=glimmer_lift` (until
     the cue's field has no live mote), so the hold follows the motes rather than a guessed number of seconds.
  8. **R07/R08:** a profile two-shot, perpendicular to the pair, 6–8 m off; the gold column over Reedhollow is on
     Kerrid's side of the frame, so Pell has his back to the only light. The cuts into and out of R08 fall off the
     music's accents (nothing in the score marks it). R08's glow (≤ 0.15) can only be judged on the GPU: PC-QUEUE.
  9. **The clutch as a group:** one `@anim` on twenty to thirty actors needs an actor group with per-actor offsets
     (the sheet's "one hero clip, retimed per actor"). Mine: `@anim clutch turn_away` on every stage actor in group
     `clutch`, each offset by its own small delay.
  10. **B01:** Act II's first frame comes in from the Ch9 act card's black. O01 should start black and fade up under
      silence; then `ossa_fen` comes in on the line's first steps.
  Open question 2 (Kerrid in Reedhollow): from staging, keep him outside with Pell; B09's frames are cleaner with
  no rule to keep him out of them.
  - (cinematics, the same day) Correction to item 7: `@wait vfx=` is dropped (count= motes persist and can't be read
    back). O06's hold will be timed against stills of the real field. Items 2, 5 and 9 are built (M4-CIN-1302).
