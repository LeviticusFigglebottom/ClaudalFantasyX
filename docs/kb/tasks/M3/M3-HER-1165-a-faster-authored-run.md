---
id: M3-HER-1165
title: "Request: a run clip authored near the field's 3.6 m/s (the party's run is sped up to 1.6-2.0x its clip)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The field run is 3.6 m/s (`game/data/world/field_movement.json` run_speed_mps). Running is the default, since a full
stick runs. The heroes' measured run clips are slower (`hero_motion.json` field.heroes, gait):

| hero | run clip m/s | playback needed at 3.6 |
|---|---|---|
| rhen | 2.35 | 1.53x |
| asha | 2.01 | 1.79x |
| toma | 2.26 | 1.59x |
| ysolde | 2.11 | 1.71x |
| liss | 2.19 | 1.64x |
| kerrid | 1.80 | 2.00x |
| pell | 3.13 | 1.15x |

HeroLocomotion speeds the run up above its clip speed so the feet keep planting, up to `max_playback_scale`.
That cap was 1.5, so every hero but Rhen and Pell slid 16-28% while running (the Lead's 10-29 walk audit,
integration-qa). It's now 1.8, so the feet plant for all but Kerrid (10% slide left). A leg cycle at 1.6-1.8x its
authored speed can still read as scurrying.

## Ask
A run (or a "field run") per hero authored at 3.2-3.6 m/s ground speed (the gait's walk/run blend takes it as the
`run` clip; HeroClipGait measures it). Then max_playback_scale can come back down toward 1.2-1.3. Kerrid first: he
needs 2.0x.

## Acceptance criteria
- [ ] Each Act I hero's run measures >= 3.0 m/s (test_hero_field_actor's measure test checks the rows).
- [ ] integration-qa lowers max_playback_scale and re-runs test_qa_walk_audit: no foot slide at 3.6 m/s.

## Notes
- Filed by integration-qa, 2026-10-30, from test_qa_walk_audit (the scripted-walk audit).

## Review log
