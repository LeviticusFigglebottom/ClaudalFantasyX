---
id: M2-BPR-10
title: Placeholder hero battle clip poses through the clip contract (until M2-CHR-07 lands)
role: combat
status: doing
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-02]
milestone: M2
request-from: lead
---
## Goal
The heroes' battle actors (M2-UI-07, characters' asha/rhen/toma battle scenes) have a skeleton but not yet the battle
clip set (M2-CHR-07, in progress). So the choreography reads on them now, a hero actor that lacks a contract clip
gets a simple placeholder pose clip, generated at runtime on its skeleton's main bones from data. A real clip with
the same name always wins, so M2-CHR-07 replaces them without a code change.

## Acceptance criteria
- [ ] Placeholder clips per contract name (bone rotations in data, keyed by the MPFB2 rig's bone names)
- [ ] Only for actors with a Skeleton3D and missing clips; real clips win; primitives keep the procedural root motion
- [ ] Tests on a synthetic skeleton

## Review log
