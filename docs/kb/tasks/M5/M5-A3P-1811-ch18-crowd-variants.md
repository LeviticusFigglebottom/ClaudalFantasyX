---
id: M5-A3P-1811
title: "Ch18: the revisited towns' crowds, Haluna's backs-to-the-water and Reedhollow's farewell-tide again (flag rows)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: [M5-A3P-1810]
milestone: M5
reviewer: character
---
## Goal
act3_roster.md, Ch18: Haluna lifts its own (its villagers plus crowd people turned backs-to-the-water: a zone-file
variant, no new body) and the Kirru crowd at Reedhollow's farewell-tide again (a variants row on `ch17_complete`).
Rule 3 of the revisits: every revisited town has changed, its grief, not its quest log. Built with M5-A3P-1810's
`flag` / `not_flag` rows in ch02_haluna.json and ch10_reedhollow.json.

## Acceptance criteria
- [x] The changed rows on the declared flags, validated; the Act I/II rows `not_flag` the same flag.
- [x] Tests (the real zones with the flags flipped). No review shot: no existing shot sets these flags. A stage with the flags set is a follow-up if the Lead wants one.

## Review log
- 2026-10-31 creatures: the flags landed on the integration branch (merged @ 8b5462854).
  - **Haluna** (`ch18_haluna_lifted`, "Backs to the Water"): four beach people stand in a short line on the beach,
    their backs to the sea (yaw 90; the sea is +x, HalunaTerrain.inland_m), at the terrain's height plus the rows'
    usual 2 cm. Three are in `vigil`; the elder folder kneels (`kneel_mourn`). Their own rows carry `not_flag`.
  - **Reedhollow** (`ch17_complete`, the farewell-tide again): each platform watcher's `_tide` row is its own spot
    turned 180 degrees, its back to the lagoon. The watchers' own rows carry `not_flag`.
  - validate_npc: a crowd person's `flag` row stands at its own CrowdSpots spot with an `at`.
  - Tests: Godot `test_the_revisited_towns_crowds_change_with_the_act3_flags` (crowd 27/0, villager 50/0); tools
    test_npc OK.
