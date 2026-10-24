---
id: M2-AUD-10
title: A per-area world reverb (WorldVerb) for World and Combat sounds
role: audio
status: doing
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
depends_on: [M2-AUD-06]
milestone: M2
request-from: lead
---
## Goal
mix.md §4 planned a WorldVerb bus with a preset per area; M2-AUD-06 left it out (world SFX carry their own room).

## Acceptance criteria
- [ ] A reverb on the World and Combat buses (Godot buses send to one bus, so an AudioEffectReverb on each with wet/dry from data), presets per area in mix.json (open sea, village lanes, stone shrine, cave), chosen by the zone row.
- [ ] Rendered SFX keep a dry enough room that the bus reverb doesn't double it; tests for preset switching on a zone swap.

## Notes

## Review log
