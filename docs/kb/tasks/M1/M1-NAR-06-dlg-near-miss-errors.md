---
id: M1-NAR-06
title: dlgc: near-miss speaker lines must error, not become narration
role: architect
status: review
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
