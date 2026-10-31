---
id: M5-A3P-1200
title: "Request: one scene per file for the Act III field barks and interactables (a trigger can only start a file)"
role: narrative
status: todo
owner_session: ""
depends_on: [M5-A3P-1000, M5-A3P-1003]
reviewer: cinematics
milestone: M5
request-from: cinematics
---
## Goal
A layout trigger's `{"dialogue": id}` plays a compiled *file* from its start node (`CutsceneSequencer.play` →
`DialogueRunner.start()`; `chapter_flow_check` knows dialogue by file stem). Each Act I and Act II bark and
interactable is its own file. Three Act III files hold several field scenes as nodes, so a trigger reaches only
the first node:
- `ch17_bark_lookout`: the lookout (wired) and four more that wait: `ch17_bark_tally_keeper`, `ch17_bark_chandler`,
  `ch17_bark_pell_windmills`, `ch17_bark_ysolde_asleep`;
- `ch17_hull_sails`: the sails (wired) and two that wait: `ch17_hull_tool_rack`, `ch17_hull_chart_wall`;
- `ch18_heirloom_rhen`: the seven heirlooms (one per hero).

## Ask
Split each node into its own `.dlg` with the same id (the lines keep their `#line:` ids), then recompile. The flow
side (act1-chapters) then adds the triggers; their places are written in `tools/act2/ch15_16_greybox.py`'s
`act3_dry_dock()`.

Files whose nodes are jumped to inside one scene (`ch21_the_letting`), or that combat plays by node
(`ch19_bark_abiding_wardens`, `ch20_bark_vowbound_fights`, `ch21_bark_sefir`, `ch21_seven_bands`), are left
alone unless their owner wants otherwise.

## Acceptance criteria
- [ ] The nine field scenes are files; `dlgc --check` is clean.

## Review log
