---
id: M3-BPR-405
title: "Impact SFX on BattleImpact's events (weight layer, hit-stop crack, KO slow-mo swell)"
role: audio
status: todo
owner_session: ""
depends_on: [M3-BPR-401]
milestone: M3
request-from: combat
---
## Goal
M3-BPR-401 gives each blow visual weight: hit-stop, shake and flash by damage, plus a KO slow-mo. The human said
battles look primitive, and sound carries half of that weight. Please layer impact SFX on the new listen-only signals
(docs/kb/tech/battle_presentation.md, "Impact", "Audio hooks"):
- `BattleImpact.landed(target_id: StringName, strength: float, stop_sec: float)`: once per contact with weight. The
  strength is 0..1 (damage over max HP; a crit adds a bonus). stop_sec > 0 means a hit-stop holds the frame for
  that long (real seconds), so a low "thump" or "crack" that sits under the frozen frame reads well.
- `BattleImpact.slowmo_planned(from_sec, sec, factor)`: the sequence that fells the last foe. The plan-time window
  is stretched by 1/factor. A low swell or a pitch-down of the collapse fits.
- Find the node as `BattleChoreo`'s child `BattleImpact` (`ctl.stage.choreo.impact`), the same way ChoreoAudio
  finds the choreography.

## Acceptance criteria
- [ ] The weight layer scales with strength (a light blow adds nothing over the existing contact sound).
- [ ] Reduced audio: one sound per action still holds (the layer replaces, never stacks).
- [ ] Original synthesis only (no packs, no AI audio), PROVENANCE rows, tests in tests/unit.

## Review log
