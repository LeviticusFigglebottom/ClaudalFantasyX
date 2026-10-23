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
- 2026-10-23 architect (agent-a82894145cf6d2aff): review-sweep-D changes done; back to review.
  - **Blocker 1 (Lead decision):** a name-shaped prefix of 1–2 words errors only when a word is a speaker id, a speaker's display name (`name_key` text from `game/data/loc/*.csv`, via `load_speaker_names`), or `Narrator`. Every other name-shaped prefix of 1–6 words is a WARN with the `\:` / `#narration` hint. `Chapter Two: The Raft`, `Part One:`, `Day Three:`, `The Hollow:`, `Corrow Harbour:`, `Eleven Bells:` and `The Order of Lamps:` now warn. `Old Toma:`, `Toma Vell:` and `Asha Vell:` stay errors. (`Asha Vell:` was in fp.txt, but the review's own fix lists it as an error, so it is tested as one.)
  - **Extension of the Lead rule to one bare word:** `Interlude: Ysolde` used to hit the base "unknown speaker" error. A bare `Word:` (no identity, alias or emotion) that is not a speaker and not a close misspelling of one (difflib ratio ≥ 0.7, `SPEAKER_TYPO_CUTOFF`) now compiles as narration with the same WARN. `Kerid:` and `Ahsa [sad]:` stay errors and now say "did you mean 'Kerrid'?". Trade-off: a new character's one-word lines warn rather than fail until the character is in `speakers.json`. This is in the doc.
  - `Not Asha: me.` and `Only Kerrid: ...` (blocker-1 false positives that name a speaker): a prefix that starts with a prose leader (`Not`, `Only`, `Even`, `Then`, ...) is prose. `I` and compass points are never name words (`I Remember Corrow:`, `North of Corrow:`).
  - **Blocker 2:** a `[...]` group is now a name token, and any name-shaped prefix that contains one errors (`Old Toma [sad]:`, `Mother Ilse [sad]:`).
  - Should-fix: `WRONG_BRACKET_RE` catches `Asha (sad) Hi.`, `Asha "sad": Hi.`, `{sad}` and `<sad>`. With a colon it always errors; without one, only when the word is an emotion, so `Asha (again) laughed.` is prose. `Narrator (rhen):` suggests `Narrator(rhen):`. `STRAY_PUNCT_RE` catches `Asha, [sad]: Hi.`. Full-width colons (`：`, `﹕`) before a speaker error. `Asha [sad]:: Hi.` errors ("two colons"), and `Asha: \: Hi.` still compiles. `Kerrid [cold] as The Stranger:` now gets the emotion-after-alias hint with the quotes added. The missing-colon hint drops stray `; . - —`.
  - Should-fix: `and` is out of `NAME_JOINERS`.
  - Probes: all 31 fp.txt lines and all 30 miss.txt lines are in tests. The prose lines are in `CORPUS` (no error, no warning), the captions are in `CAPTIONS` (exactly one WARN, no error), and the miss lines are in `NearMissTests`. Known limits (no grammar), tested as narration: `Asha the girl: Hi.`, `Asha. Hi.`, `Asha - Hi.`.
  - Checks: validate_data 0/0; unittest 260 OK; taskboard --check rc 0; `dlgc --check` 0 errors and 0 warnings, with the 3 repo `.dlg` files unchanged.

## Review log
- 2026-10-23 narrative (review-sweep-D): **request-changes.** Checked: `python3 -m unittest discover -s tools/tests` gives 247 OK; `dlgc --check` gives 0 errors and 0 warnings; `validate_data` gives 0 errors and 0 warnings. I compiled 31 fresh narration lines and 30 near-miss lines one at a time, through the corpus harness. Rhen's first-person colon prose all passes (`I knew it then: ...`, `I had one job that winter: ...`, `What I said next: ...`, `I said the only thing I could: sorry.`, `"Run," she said: ...`, `Even now: ...`), and so do possessive and comma prefixes and `Chapter 2:`. Digit colons, the tiering, and the missing-colon and emotion-after-colon errors work as specified.
  - **Blocker 1: two-word chapter captions and scene headings are errors.** Captions are narration (dialogue_format.md:49), and the reviewer brief named them, but every Title-Case two-word heading hits the error tier (tools/dlgc.py:775, via `NAME_WORD_RE` tools/dlgc.py:90). Errors seen: `Chapter Two: The Raft`, `Part One: Ashfall`, `Day Three: the reef.`, `The Hollow: three days later.`, `Corrow Harbour: dawn.`, `Eleven Bells: that is what they called the hour.`, `Not Asha: me.`, `Only Kerrid: he alone understood.`. That is 8 of 31 lines, close to the 7 of 10 this task set out to fix. Suggested fix: error at 1–2 words only when a token is a `speakers.json` id or `Narrator` (`Old Toma:`, `Toma Vell:`, `Asha Vell:`, `Asha {sad}:` stay errors), and make other 1–2-word name-shaped prefixes a WARN. Alternatively, skip prefixes that start with a caption word (`Chapter|Part|Day|Act|Book` plus a number or number word). Add these lines to the corpus. The doc's claim that "ordinary prose passes without escapes" (dialogue_format.md:96) only holds for `Chapter 2:` with digits, so add the spelled-out case there too.
  - **Blocker 2: `Old Toma [sad]: Lie still.` still compiles silently to narration** and ships `Old Toma [sad]:` to players. The `[sad]` token fails `NAME_WORD_RE`, so `speaker_like_prefix` (tools/dlgc.py:797) returns None, and `MISSING_COLON_RE` (tools/dlgc.py:77) needs a one-word name. This is the task's own typo shape with an emotion added. Treat a trailing `[word]` token as name-shaped, or strip it before tiering.
  - Should-fix: other silent near-misses that ship raw text. `Asha (sad) Hi.` (missing colon with parens: tools/dlgc.py:750 needs an alias or `[emo]`). `Asha "sad": Hi.` (the `"` exclusion in tools/dlgc.py:87). `Asha, [sad]: Hi.`. `Asha： Hi.` (full-width colon, from an IME). `Asha [sad]:: Hi.` ships `: Hi.`. The first two are the likeliest.
  - Should-fix: `and` in `NAME_JOINERS` (tools/dlgc.py:91) makes ordinary name lists WARN: `Asha and Toma: the only two who stayed.`, `Asha and I: ...`, `Sefir and Pell: brothers ...`. `North of Corrow: only the reef ...` warns too. Drop `and`, and require a joiner to be followed by a capitalized word that isn't a compass point. Otherwise Rhen's prose collects warnings, which is the noise the architect's note wanted to avoid.
  - Nit: the tool caught `Ahsa [sad]: Hi.`, `Asha [sad]; Hi.`, `Asha [sad]. Hi.`, `Asha [sad] — Hi.`, `Narrator(asha) [grief] The bell.`, `Asha as "The girl". Hello.`, `Asha: [sad]Hi.` and `Narrator: [grief] ...` with good hints.
