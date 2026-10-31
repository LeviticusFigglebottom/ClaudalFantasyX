---
id: M4-C12-100
title: "Ch12: after Ysolde's confession the objective q_on has no target, so nothing points the player back to Keth Pass (request from cloud QA, the Act II smoke)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M4
request-from: qa
reviewer: qa
priority: medium
---
## Goal
Cloud QA's Act II smoke on big36 (1983de0a2): `tools/gpu_bench/playthrough_probe.tscn` from the Ch9 start with
Act I's flags, then `--location=ch10/ossa_fen`. It plays Ch10, Ch11 and Ch12 up to `ch12_ysolde_confessed` (682 s).

From there the chapter goes on only when the party walks back down to Keth Pass. The arrive beat there,
`{"when": {"set": ["ch12_ysolde_confessed"], "unset": ["ch12_complete"]}}`, plays `ch12_down_the_other_side` and goes
to ch13/ansedra. But the objective row `q_on` (requires `ch12_ysolde_confessed`, until `ch12_complete`, zone
ch12/quellan) has no `target`. The HUD shows its line with no marker, and the probe walked Quellan ↔ Cloudloom for
40 minutes without finding the way down.

## Acceptance criteria
- [ ] `q_on` gets a target: the Quellan exit down to Keth Pass (and, in Cloudloom, the way back to Quellan if the
      row should show there too).
- [ ] Check the row's `until`. The Keth Pass beat goes to Ch13 without setting `ch12_complete`, so if nothing in
      ch13/ansedra sets it, the row (and the beat's `unset` guard) stays live.
- [ ] Cloud QA's Act II smoke reaches ch13/ansedra without a PLAY_NO_TARGET in Quellan.

## Notes
Owner: act1-chapters (`game/data/flow/chapters/ch1x.json`, objectives). See `docs/kb/handoffs/live/cloud-qa.md`
on `qa/cloud-pass6`.

## Review log
