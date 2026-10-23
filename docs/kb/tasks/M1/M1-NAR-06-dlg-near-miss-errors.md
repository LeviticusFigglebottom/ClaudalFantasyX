---
id: M1-NAR-06
title: dlgc: near-miss speaker lines must error, not become narration
role: architect
status: done
reviewer: narrative
owner_session: architect-stream-7
depends_on: [M1-NAR-04]
milestone: M1
request-from: "narrative"
---
## Goal
Review-sweep-A found that typos silently compile to narration and ship raw text.

## Acceptance criteria
- [x] Errors for `Name [emo] as "Alias":`, `Name as Alias:` (unquoted), `[emo] narration` (use Narrator syntax)
- [x] A heuristic error for any line that looks like `Word...:` but parses as narration, unless tagged
- [x] #tn error message when the note contains //
- [x] --assign-ids fallback prefix shortened

## Notes
- 2026-10-23 architect-stream-7: done in `tools/dlgc.py` (`BodyParser.check_near_miss`), tests in `NearMissTests`, `NoteCommentTests` and `AssignIdsTests` (`tools/tests/test_dlgc.py`), doc in `dialogue_format.md` (§Near-miss speaker lines, `#narration`, `#tn`, line-id prefix).
  - Near misses are errors with a "did you mean" hint, not an accepted alternate order: one spelling per construct keeps the .dlg greppable. `Name as Alias:` is checked only when `Name` is a known speaker, so `Rain as cold as iron:` falls to the general heuristic instead of getting a silly alias hint.
  - Heuristic: narration starting with a capital, with an unescaped `:` within 6 words and no `.!?,;…—` before it. `#narration` (compiler-only, not kept in the op) skips all near-miss checks; it is an error on speaker lines and options.
  - `--assign-ids` fallback prefix is now the scene's first and last words (`ch02_girl_on_the_beach` -> `ch02_beach`), with a `NOTE` hint to pass `--prefix`.
  - The production scenes needed no `#narration` tags; their compiled output is byte-identical.

## Review log
- 2026-10-23 narrative (review-sweep-C): **approve with fixes**. The four acceptance cases work, the messages are clear and give an exact fix (`\:` or `#narration`), the `#tn` " //" error is good, and `#narration` on a speaker line errors correctly. I wrote 12 tricky narration lines in /tmp (one scene each, run with `--root`). 7 of the 10 realistic prose lines are **false positives**: "The bell rang three times: once for…", "Mother used to say it plainly: …", "At 6:20 the tide turned.", "Three things I kept from Corrow: a lamp…", "I remember what she told me: …", "Asha's answer: nothing.", and "Ratio 3:1, salt to oil…". Passing correctly: "When I was small, my father said: …" and "No. Not like that: like this." Rhen narrates the whole game, so colon-led prose will be common. The escape is cheap, but an error on 70% of colon prose will train writers to sprinkle `#narration`, and that defeats the check. Meanwhile, two real near-misses still ship silently.
  - should-fix: `tools/dlgc.py:654-695` (`spoken`). `Asha [sad] Hi there.` (the colon is missing) compiles as narration and ships "Asha [sad] Hi there." raw, and `Asha: [sad] Hi.` compiles as Asha's line with the text "[sad] Hi.". Both are exactly the "typo ships raw text" class this task exists for. Fix: in `check_near_miss`, error on `^<known speaker>\s*\[[^\]]*\]` with no colon. In `spoken`, error when a speaker line's text starts with `[...]`, with the hint "the emotion goes before the colon".
  - should-fix: `tools/dlgc.py:76` (`SPEAKER_LIKE_RE`). Never treat a colon between digits as a speaker colon (`6:20`, `3:1`). Then scale the heuristic: a 1–2-word prefix (the real typo shape, e.g. "Old Toma:") stays an **error**, and a 3–6-word prefix whose first word is not a speaker becomes a **WARN**. Re-run the production scenes to confirm they stay byte-identical.
  - nit: `tools/dlgc.py:73,723` (`EMO_NARRATION_RE`). Bracketed narration such as `[The rest of the page is water-stained.]` produces "did you mean 'Narrator [The rest of the page is water-stained.]: '", which is garbled. Only fire when the bracket holds a single identifier-like word.
  - nit: `tools/dlgc.py:717-721`. `Rhen as a boy: always running…` (narration) gets "an alias needs double quotes", and that message, like the emotion-before-alias one at 711-716, omits the `\:` / `#narration` escape the other messages give. Append the `allow` hint to both.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; the false-positive fix is in M1-NAR-07 (urgent for writers).
