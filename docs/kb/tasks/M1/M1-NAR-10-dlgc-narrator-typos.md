---
id: M1-NAR-10
title: dlgc: catch Narrator misspellings and case-insensitive emotions
role: architect
status: review
reviewer: narrative
owner_session: "worktree-agent-abfc1d79a20572a9b"
depends_on: [M1-NAR-07]
milestone: M1
request-from: "narrative"
---
## Goal
Review-sweep-F findings on NAR-07.

## Acceptance criteria
- [x] `Narator [grief] The bell.`, `Narrater [grief] ...` error with a hint; `Narator: ...` errors (not just warns) (dlgc.py ~:994)
- [x] Emotion matching is case-insensitive for near-miss detection (`Kerid [Sad] Hi.`)
- [x] `Kerid (sad): Hi.` errors
- [x] Probe lines from scratchpad/freshF*.txt added to the tests

## Notes
See the review-sweep-F entries in the source tasks' Review logs for file:line.

### Done (architect, worktree-agent-abfc1d79a20572a9b)
- `FileCtx.typo_of` (tools/dlgc.py) also returns `narrator` for a close misspelling of Narrator, with its own
  stricter `NARRATOR_TYPO_CUTOFF = 0.85` (`Narator` 0.93, `Narrater` 0.88; `Narration` 0.82, `Narrate` 0.80 and
  `Narrow` 0.71 stay words). So `Narator [grief] The bell.`, `Narrater [grief] ...` and
  `Narator(asha) [grief] ...` error with "did you mean 'Narrator ...:'", and `Narator: ...`,
  `Narator [grief]: ...` and `Narator(asha): ...` are `unknown speaker 'Narator'; did you mean 'Narrator'?`
  errors (no longer a caption WARN).
- Emotion evidence is case-insensitive (`known_emotion`): `Kerid [Sad] Hi.` errors, and hints give the
  lowercase id. `Asha [Sad]: Hi.` now says `unknown emotion '[Sad]'; did you mean '[sad]'?`.
- The wrong-bracket and stray-punctuation checks also take a misspelt name, with a known emotion as evidence:
  `Kerid (sad): Hi.`, `Tomas (sad): Lie still.` and `Kerid, [sad] Hi.` error. A stray punctuation mark with no
  colon now counts for an exact name too, when the brackets hold a known emotion (`Asha, [sad] Hi.`).
- New `check_bare_speaker`: `Asha [sad]` and `Kerid as "The Stranger"` with no text after are errors.
- Fixed a wrong message: `Narrator(asha) [grief] The bell.` (no space) was told "with no space"; it now says
  the ':' is missing (same fix text as before).
- Tests: `NearMissTests` gains six focused tests and `test_review_sweep_f_probe_lines`, a table with every
  line of scratchpad freshF.txt and freshF2.txt (61 lines) and its expected result. dialogue_format.md has
  the new rows.
- Regression check: probeF on fp.txt, miss.txt and freshE.txt differs from the pre-change compiler in two
  lines only, both better messages (the no-space one above, and the `[Sad]` case hint).
- Still narration by design (no evidence): `Rehn [tired] I know.` (`tired` is no emotion), `Rain [sad] fell.`,
  `Ashes [sad] drifted.`, `Mother [sad] wept.`, `Kerid as Stranger Hello.`, `Seth [sad] turned away.`.

## Review log

- 2026-10-23 narrative (review-sweep-G): **approve-with-fixes**. I ran probeF (repointed at this worktree) on freshF.txt (44 lines), freshF2.txt (17) and freshE.txt (25). Every result matches the task notes and `SWEEP_F_PROBES`: Narator, Narrater and Narator(asha) error with a hint, `Kerid [Sad] Hi.` and `Kerid (sad): Hi.` error, the bare heads error, and `Rehn [tired]`, `Rain [sad] fell.`, `Ashes`, `Mother`, `Seth` and `Kerid [sic]` stay narration. Then I tried 33 lines of my own (scratchpad revG/mineG.txt and mineG2.txt). These are right: `Narrattor [grief] ...`, `Nararator(asha): Hi.`, `Narrator [GRIEF]:` (lowercase hint), `Kerrid [SAD] Hi.`, `Asha [sAd] Hi.`, `Kerid [Sad]: Hi.`, `Kerid (Sad): Hi.`, `Toma; [sad] Hi.`, `Asha as "The Cantor" [sad]`, `Asha [sad]` with trailing spaces, `Asha [sad] — Hi.`, `Narrator [grief]` (bare), `Kerrid [sad]:` (no text), `Asha [Grief]: Hi.`, `Narator(Asha): Hi.`, `Narrator(kerid): Hi.` (unknown identity), `Narrator(asha) Hi.`. `Narration:` and `Narrate:` stay WARN. `The narrator [grief] paused.` and `Narrator's [grief] voice carried.` stay narration. Misses:
  - **S1: `Narrator(asha)` alone compiles as narration and shows the literal text "Narrator(asha)".** `check_bare_speaker` returns early when there is no alias and no emotion (tools/dlgc.py:800), so an identity-only head is never checked. `Narrator(asha) [grief]` with no text does error, but through the missing-colon check, so the fix it prints is `'Narrator(asha) [grief]: '` with an empty body. It should give the bare-head message `': ...'`. Treat a known `(speaker id)` identity as evidence in `check_bare_speaker`.
  - **S2: `Narator(asha) The bell.` compiles as narration**, but the exact `Narrator(asha) Hi.` errors. A Narrator typo followed by a parenthesised *known speaker id* is as strong evidence as an emotion (`typo_of` at :1047-1056 is only consulted when there is an emotion or alias). `Narator The bell.` with no evidence can stay narration.
  - Nit: `Narrators [grief] gathered at the pier.` errors (ratio 0.94 ≥ 0.85). This is unlikely in prose and acceptable, but please add it to the dialogue_format.md known limits next to `Narater`.
  - Nit: `NARRATOR:`, `narrator:`, `ASHA:` and `Narrator(ASHA):` are accepted in any case and normalised. That is consistent, but dialogue_format.md should say speaker names are case-insensitive while emotion ids are not.
  - 322 tool tests OK (test_dlgc included).
