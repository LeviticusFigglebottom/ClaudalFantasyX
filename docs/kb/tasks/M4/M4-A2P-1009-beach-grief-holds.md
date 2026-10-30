---
id: M4-A2P-1009
title: "Request (staging): give the beach's grief beat room to land (ch02_girl_on_the_beach)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To slice-polish, from the Lead's Act I emotional-beats pass (pillars 1 and 6). Story has tightened the lines: after
Rhen sees Oruvel's dead, Asha no longer jokes ("He's nicer than his spear." is now "I'm Asha. And that's Toma.", and
"Who is very glad you aren't dead." is now "Who is glad you're here.", tender). The staging now needs to give the
moment time.

| # | Where | Now | Ask |
|---|---|---|---|
| 1 | `ch02_girl_on_the_beach.dlg:63` → `:64` | "Those are ours. Aren't they." is followed at once by Asha's answer | A `@wait 2.0` after `ch02_beach_019`: the question is answered by the water first |
| 2 | stay branch, after "Be level, Oruvel." (`:75`) | A hard cut to H05 and Asha offering her hand | A `@wait 2.0` (hold on the three of them) before the cut |

## Acceptance criteria
- [ ] Both holds in, or answered here with a reason.

## Review log
