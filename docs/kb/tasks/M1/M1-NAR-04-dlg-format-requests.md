---
id: M1-NAR-04
title: Dialogue format requests from Narrative
role: architect
status: todo
owner_session: ""
depends_on: [M1-NAR-03]
milestone: M1
request-from: "narrative"
---
## Goal
Writer-facing additions to the .dlg format (ADR 0004), requested in the M1-NAR-02 report.

## Acceptance criteria
- [ ] Alias speaker name before introduction
- [ ] Emotion and VO identity for narration
- [ ] Sung-line and do-not-translate conventions
- [ ] @sfx cue, reserved @music silence, documented @vfx/@camera grade= options
- [ ] dlgc --assign-ids helper
- [ ] Declared dialogue event names, validated
- [ ] Warning for lines over 25 words
- [ ] @wait music=<marker>

## Notes
Also needs a unit test for tools/dialogue_stats.py.

## Review log
