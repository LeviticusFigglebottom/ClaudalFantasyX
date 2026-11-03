---
id: M3-HER-1232
title: "Request: the sequencer sends a line's talk back to idle on bark, timed and skipped lines, and at _finish"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-HER-1231]
milestone: M3
request-from: architect
---
## Goal
M3-HER-1231 (the FAST-TRACK "Rhen's walk stops"): `CutsceneSequencer._line` plays `talk` on the speaker and
plays `idle` only after `advance_requested`. The `_fast()`, `TAG_TIMED` and `auto_advance` returns skip it, so an
overheard bark (zone_story / haluna_story `_new_overhear`), a timed line or a skipped line leaves the speaker
looping `talk`. `_finish` doesn't return held poses (`_held`) either. HeroFieldActor now releases these on the
player's stick, and on any body that travels at a walk (field.clip_release). But a standing NPC or follower can
still talk silently after a bark ends, until it moves.

## Acceptance criteria
- [ ] Every line's speaker gets `_play_clip(speaker, &"idle")` when its line ends on every path (or at the next
  line or `_finish`), unless it is in `_held`.
- [ ] A test in the sequencer suite: an auto_advance line by a stage actor with a body leaves `action == &""`.

## Review log
