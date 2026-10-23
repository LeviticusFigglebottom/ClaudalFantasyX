---
id: M1-NAR-07
title: dlgc near-miss heuristic: kill false positives, catch the remaining silent cases
role: architect
status: review
reviewer: narrative
owner_session: "agent-a82894145cf6d2aff"
depends_on: [M1-NAR-06]
milestone: M1
request-from: "narrative"
---
## Goal
7 of 10 realistic narration lines were rejected; two real near-misses still slip through.

## Acceptance criteria
- [x] Colons between digits (6:20, 3:1) never trigger
- [x] Error only for 1-2-word prefixes before ':'; warn for longer
- [x] `Asha [sad] Hi there.` (missing colon) errors with a hint
- [x] `Asha: [sad] Hi.` errors (emotion after the colon)
- [x] Test corpus of 30+ realistic narration lines with zero false positives

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

- 2026-10-23 architect (agent-a82894145cf6d2aff): done, ready for narrative review.
  - `tools/dlgc.py`: the speaker-like heuristic now looks only at prefixes that **read like a name**: every word capitalized or a `(...)`/`{...}` group, with lowercase joiners (`of`, `the`, ...) allowed inside, and no `"` or sentence punctuation. A colon between digits is skipped. 1–2 words is an error, and 3–6 words is a WARN (`ctx.warn`, never fatal). **Interpretation of AC 2:** "warn for longer" applies to longer *name-shaped* prefixes (`The Keeper of Lamps:`). A prose prefix (`The bell rang three times:`) gets neither an error nor a warning, because a warning on most of Rhen's colon prose would be the same noise in a new form. Possessives (`Asha's answer:`) and lowercase second words (`Mother said:`) are prose by this rule.
  - New `MISSING_COLON_RE`: `Name [emo] text` and `Name as "Alias" text` with no colon error with a "did you mean 'Asha [sad]: Hi there.'" hint, but only when the name is a known speaker or `Narrator` and the brackets hold one identifier-like word (`Asha [the girl] smiled.` is still prose).
  - In `spoken()`, a speaker line whose text starts with `[word]` errors: "the emotion goes before the colon: did you mean 'Asha [sad]: Hi.'?" (it notes an unknown emotion). `Asha: [Static.] ...` still compiles. A speaker line has no `#narration` escape, by design.
  - Nits from the NAR-06 review: `[emotion] narration` fires only for a single identifier-like word in the brackets, so `[The rest of the page is water-stained.]` is prose. Both alias messages now include the `\:` / `#narration` escape.
  - Tests: `tools/tests/test_dlgc_narration_corpus.py` holds 38 lines (the review's 10 plus 28 more), each compiled alone, with 0 errors, 0 warnings, and an empty speaker. `NearMissTests` in `tools/tests/test_dlgc.py` gains tiering, digit-colon, missing-colon, emotion-after-colon, bracketed-prose, and escape-hint cases. Two old expectations (`Then she said: go home.` and `Rain as cold as iron: hm.` as errors) were the false-positive class, so they moved to the must-pass test.
  - Repo scenes: `dlgc --check` reports 0 errors and 0 warnings, and the outputs are byte-identical (all 3 `.dlg` files).
  - Doc: `docs/kb/tech/dialogue_format.md` (§Near-miss speaker lines, the escapes bullet, and the Warnings paragraph).

## Review log
