---
id: M3-CIN-1221
title: "Sequencer: @mark <actor> <mark> via=<mark>,<mark> (a walk along a path) — patch ready, for m2-slice/slice-polish to apply"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters (M3-CIN-1220) needs cutscene walks that follow a path: round a rail, down a stair's flights, along a
deck, instead of the straight line `_cue_mark` lerps. The patch is `docs/kb/tech/cutscene_mark_via.patch`
(`git apply --check` clean against claude/act1-chapters @ the commit that adds it):
- `CutsceneSequencer._cue_mark`: an optional `via` kwarg (marks, comma-separated) makes the walk a polyline from where
  the actor stands through the via marks to the mark: one walk over the whole length (the same anticipation, ramps
  and cruise, M2-FP-29), the walk clip as before, an eased `_turn_to` at each corner. Without `via` it is unchanged.
- `CutsceneMotion`: `path_length`, `path_leg`, `path_point`.
- `game/data/dialogue/cues.json`: `mark` takes `via` (a string). (cues.json is Narrative's and the Architect's data;
  the key is the vocabulary change only.)
- `tests/unit/test_cutscene_mark_via.gd` (the path helpers).
Checked with the patch applied: `--filter=cutscene` 52/0, `--filter=sequencer` 17/0, `--filter=mark_via` 3/0,
`dlgc --check` and `validate_data` clean.

## Acceptance criteria
- [ ] Applied on m2-slice (or the integration branch), with a line in its live log, so act1-chapters can write `via=`.

## Review log
- act1-chapters, 2026-10-28: applied by slice-polish in b2d39f8cc (`_cue_mark`'s `via`); M3-CIN-1220's
  `act1_walk_vias.patch` is in on top of it and the walk audit is clean. Ready to close (reviewer: slice-polish).
- 2026-10-28 slice-polish: already applied at b2d39f8c (hand-merged onto HeroMotion locomotion; its unit test is in).
