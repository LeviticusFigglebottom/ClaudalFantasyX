---
id: M1-NAR-06
title: dlgc: near-miss speaker lines must error, not become narration
role: architect
status: doing
owner_session: architect-stream-7
depends_on: [M1-NAR-04]
milestone: M1
request-from: "narrative"
---
## Goal
Review-sweep-A found that typos silently compile to narration and ship raw text.

## Acceptance criteria
- [ ] Errors for `Name [emo] as "Alias":`, `Name as Alias:` (unquoted), `[emo] narration` (use Narrator syntax)
- [ ] A heuristic error for any line that looks like `Word...:` but parses as narration, unless tagged
- [ ] #tn error message when the note contains //
- [ ] --assign-ids fallback prefix shortened

## Notes
-

## Review log
