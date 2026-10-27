# 0150 — One weak-point colour for every foe (`spawn_wound`), the wound language kept for spawn

- **Status:** proposed (art direction to accept and align palette.json)
- **Date:** 2026-10-27
- **Roles affected:** art (palette.json, color_script), character (creatures), combat and UI (the battle read)
- **Author role:** character (creatures track)

## Context
Two art rules disagree:
- **palette.json** `spawn_wound.usage_limit`: "Wound surfaces only: Undertow-spawn creature weak points ... and never a
  non-Undertow creature's weak point."
- **docs/kb/art/creatures/README.md rule 3**: "A creature's **weak point** glows `spawn_wound` `#3FE0C8`, the swatch
  reserved for creature weak points"; rule 4: "Reef beasts are sun-faded and dry-topped, with only a small
  `spawn_wound` weak point."

The README was followed from the slice on. Every shipped non-spawn creature has a `spawn_wound` weak point, through
its materials.json emission mask: the reef crab, the lantern eel, the gull harrier, the shoal skipper, the ashwing
and the slag tortoise. So do the Act II regulars built on 2026-10-27 (M3-CRE-627). The conflict surfaced in that
build's review.

SPEC pillar 4 (*tactical clarity: the player always knows who acts next and what an action costs*) wants one answer
to "where do I strike?" across every foe. Pillar 1 and the bible want the spawn's wounds to read as **wounds**: the
storm's language, bleeding held light.

## Options
1. **Keep one weak-point colour for every foe.** `spawn_wound` marks a weak point on any creature. On a non-spawn
   beast it is a single small mark (README rule 4); only spawn carry it as open wounds that shed `glimmer_held`
   motes. palette.json's limit is reworded to match.
2. **A second weak-point swatch for non-spawn beasts** (a sea or ember colour). Lore-pure, but the player learns two
   weak-point colours. It also means re-tinting six shipped creatures plus the Act II regulars, re-approving their
   shots and the portraits, and keeping the second colour clear of `sea_glow`, `salt_glass` and the glimmers.
3. **No visible weak point on non-spawn beasts.** It loses the read the battle UI and Ysolde's lessons rely on.

## Decision
Option 1. **`spawn_wound` is the one weak-point colour for every foe.** What tells spawn from beast is the
*wound language*, not the colour:
- **spawn:** open seams in wet lacquer carapace, drifting `glimmer_held` motes, the storm's rents;
- **beasts and constructs:** one small, closed mark (a gill slit, a seam, an old scar), never a seam that bleeds
  light, never motes.

Art direction rewords `spawn_wound.usage_limit` (request M3-CRE-629) to: "Weak points of every foe (pillar 4: one
answer to where to strike) and the Undertow's wounds and rents. On a non-Undertow creature: one small closed
mark, never an open seam and never shedding motes. Never the held light that pours from a rent (glimmer_held),
never bound light (glimmer_bound)."

## Consequences
- Nothing shipped changes; no re-tint and no baseline churn.
- Sheets and reviews check the *form* of a beast's weak point (small and closed) as well as its colour.
- If a future creature needs a non-spawn weak point that must not read as Undertow at all, it raises a new ADR
  rather than bending this one.
