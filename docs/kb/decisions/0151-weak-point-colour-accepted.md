# 0151 — One weak-point colour for every foe: accepted (supersedes palette.json's spawn-only rule)

- **Status:** accepted (the Lead, for art direction, 2026-10-27)
- **Date:** 2026-10-27
- **Roles affected:** art (palette.json), character (creatures), combat and UI (the battle read)
- **Author role:** character (creatures track)

## Context
ADR 0150 (proposed) found palette.json's `spawn_wound` limit ("never a non-Undertow creature's weak point") at odds
with the creature README (rules 3 and 4) and with every shipped non-spawn creature (the reef crab, lantern eel, gull
harrier, shoal skipper, ashwing and slag tortoise, and the Act II regulars). It proposed one weak-point colour for
every foe. The Lead approved it as proposed (request M3-CRE-629, 2026-10-27).

## Options
As ADR 0150: (1) one weak-point colour for every foe, the wound language kept for spawn; (2) a second weak-point
swatch for beasts; (3) no visible weak point on beasts.

## Decision
Option 1, accepted. `spawn_wound` marks the weak point of **every foe** (pillar 4: one answer to where to strike).
What separates spawn from beast is the form, not the colour:
- **Undertow-spawn:** open seams in the wet carapace, shedding `glimmer_held` motes, and the storm's rents.
- **Non-Undertow creatures and constructs:** one small closed mark, never an open seam, never motes.

This supersedes the spawn-only restriction in palette.json's `spawn_wound.usage_limit`, which now reads as above
(amended in the same change). ADR 0150 stays as the record of the proposal.

## Consequences
- Nothing shipped changes: no re-tint, no baseline churn.
- Sheets and reviews check a beast's weak point for its form (small and closed) as well as its colour.
- A future foe whose weak point must not read as the Undertow's raises a new ADR.
