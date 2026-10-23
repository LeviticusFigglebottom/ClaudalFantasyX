---
id: M1-NIT-01
title: Small fixes from review-sweep-J (UI-05, QA-06, NAR-12)
role: qa
status: doing
owner_session: "agent-a0094ffbbf8563d67"
depends_on: [M1-UI-05, M1-QA-06, M1-NAR-12]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [ ] UI-05 S1: the Swell ring steps and catches up on the same clock under Engine.time_scale (swell_ring_clock.gd ~:35 vs ~:47); S2: one metaphor in the help line, no stray punctuation (strings.csv ~:421/424); S3: the gauge frame added to art/ui.md ~:135
- [ ] QA-06 S1: base_body's known failure matched by a content hash at 1 thread, not by accessor names (blender_builds.json ~:17-22); S2: record that thread-count independence was tested on 4 CPUs only
- [ ] NAR-12 S1: the 'After the storm' break-off and the later 'Kell. Of course.' entry reconciled (act_outline ~:176, ADR 0022 append note, decisions_log ~:237); S2: the 'oil wick' remnants (decisions_log ~:14, ~:145)

## Review log
