---
draft: pre-gate
arenas: ansedra_lagoon_escape, bridal_barge_night, drowned_choir_ring (exist); lacquer_court_steps (new)
writer: assets_src/environments/kits/haluna/arena_scenes.py (env-art's tables); env-art-b's b_*.py wrappers where an arena needs zone looks
author: env-art-b, 2026-10-30
---
# The Ch13–Ch16 battle arenas: kit spec

Each arena is written by env-art's `arena_scenes.write_arena` from its table. The Act I pattern applies: a wrapper
(`b_*.py`) adds `KitSlotSwaps` (the zone looks for flat slots) and anything the table can't express, and
`tools/tests/test_b_arenas.py` reproduces it. Every arena is reviewed from the battle camera and every CameraHint
before its baseline (the Act I audit's method).

| Arena | Fight | State | To do at final quality |
|---|---|---|---|
| `ansedra_lagoon_escape` | Warden Malcor Venn (Ch14 boss, 2 phases) | exists, baseline | the flat slots (bridal barge lacquer and gilt, pursuit barge's black lacquer and gilt, the domes' gold): `KitSlotSwaps`. **The ripple look** round both barges (Ansedra's rendering item); the flat-engine's bound core steady (`glimmer_bound`); the lit city behind the enemy line (`ansedra_far_domes_lit`). Hints `the_engine`, `the_city_watching` |
| `bridal_barge_night` | the Wakefin (Ch15 boss, in the dark) | exists, baseline | the hull's flat lacquer and gilt: `KitSlotSwaps`. **The darkness-lit battle** (battle-presentation's system): the arena's light is the moon and the sea-glow; telegraphs read as glow and sound. Check skin reads under moon 0.25 with no warm source; the Wakefin's `BossAnchor` off the bow at the waterline |
| `drowned_choir_ring` | Sefir's Abiding guard; then the storm wakes (a `scripted_escape`) | exists, **no baseline** | the PC render and baseline; the moon between two singers in the battle camera (the art sheet's "the ring"); the storm's waking state (as `seawall_stairhead_surge`: the Undertow over the ring, a `StormFarPlane`); hints `the_mouths`, `the_ring` |
| **`lacquer_court_steps`** | the step-hold set piece (Ch14: hold the steps for N turns while Merel cuts the barge loose) | **new** | the court's water-steps as the floor (the party on the top steps, the Stillguard coming up from the court); the bridal barge and the gate behind the party; the lit dais and the Conclave gallery behind the enemy line; `ch14` dusk at peak contrast. Hints `the_steps`, `the_gate`, `the_conclave`. From `lacquer_court_ground` and `lacquer_hall` via `arena_scenes` (a new table, by agreement with env-art) |

## Shots (per arena: the battle camera, plus one per hint for the review)
`battle_arena_ansedra_lagoon_escape`, `battle_arena_bridal_barge_night`, `battle_arena_drowned_choir_ring`
(exist); `battle_arena_lacquer_court_steps` (new); and the boss intro shots `battle_boss_intro_malcor_venn`,
`battle_boss_intro_wakefin` and `battle_boss_intro_abiding_guard`, which battle-presentation registers.
