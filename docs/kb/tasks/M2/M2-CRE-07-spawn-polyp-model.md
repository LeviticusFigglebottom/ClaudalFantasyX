---
id: M2-CRE-07
title: "Spawn-polyp: final battle model and clips"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M2
request-from: lead
---
## Goal
The spawn-polyp from its design sheet, through the creature pipeline.

## Acceptance criteria
- [x] See Goal; notes below record what shipped.

## Notes

Shipped (2026-10-24, agent worktree off `claude/creatures` @ 5a873a0):
- `assets_src/creatures/spawn_polyp/build_spawn_polyp.py` + `materials.json` -> `assets/creatures/spawn_polyp/spawn_polyp.glb`
  (**4,656 triangles**, 2,631 vertices, 47 bones, about 0.78 MB) and four materials (`shell`, `core`, `tube`, `mouth`)
  on the creature shader. Job `creature_spawn_polyp` in `tools/dev/blender_builds.json` (verify: identical), PROVENANCE
  rows, import rule folder, `game/creatures/spawn_polyp/spawn_polyp_battle.tscn`, a creatures.json row (polyp_mend is
  kind heal -> `cast`), and `model` on the enemies.json row.
- **Form:** a 0.5 m dome of twelve overlapping beveled wet-lacquer plates (lacquer_black to abyss_navy, clearcoat 1.0)
  over a dark core whose spawn_wound seep shows through the gaps (pulsing slowly). Five soft tube-mouths rise from it
  with mouths at 0.27 / 0.43 / 0.60 / 0.34 / 0.24 m (average 0.376 m, so the BattleBossVfx polyp light at 0.36 m sits
  among them). They splay outward from a point behind the centre, so the hand opens toward +Z. The tubes go from
  lacquer at the root through deep_teal_shadow to sea_glow and lagoon_teal at a soft rolled lip. The thin upper wall
  lets a little inner light through, and there is a rim sheen. Each mouth is a deep throat in its own `mouth` slot,
  graded from a dark wall to a bright floor (emission 9.0, so it should carry through the flood water). Two closed
  buds on the shell have glowing tips ("more where that came from").
- **Rig:** root, base, three chain bones per tube (smooth two-bone skinning between bone centres, so bends curve), and
  six lip bones per mouth that flare out or pinch shut. The kit keys only rotation and location, so a bone scale was not an option.
- **Clips:** `idle` 2.8 s loop: the current's sway travels across the five tubes and up each one, and the mouths
  breathe open and shut out of phase (a ripple of light). `attack` 0.9 s: the tubes draw back with the mouths
  pinched, then lash forward together with the mouths open (contact about 0.46 s). `cast` 1.5 s: all five mouths flare
  wide while the tubes stretch and lean to +Z, release at 0.6 s, a second pulse at 1.0 s, then relax. `hit` 0.4 s: the
  mouths snap shut and the tubes pull down into the shell. `ko` 1.4 s: the tubes curl over one after another, tallest
  first, sinking into the shell; the mouths close last (1.25 to 1.37 s) and the pose holds.
- Design sheet corrected: the lean is toward +Z and outward, not toward the bell (polyps spawn in any slot), and the
  bones line now describes the lip rings.
- Review sheets were rendered on CreatureStage (noon, no water). The best one is
  `scratchpad/cre/spawn_polyp_agent/s7.png` (idle, attack, cast, hit, ko, battle-distance bars, top).

Honest weaknesses:
- I never saw it under the flood water: CreatureStage has no water. The mouth energy is a guess pitched high for
  noon light. Check the Flood battle shot, and lower `mouth.emission_energy` if the glow blooms out under water.
- The tubes are still fairly smooth and clean up close: no wrinkles or veins beyond the shader's detail bump. They
  read "soft and wet" more than "wrong".
- In the held KO pose, the tallest tube arches over the back of the shell instead of collapsing flat. It reads as
  wilted, but it is a little loopy.
- The plates are separate shells over the core. Where they overlap at a shallow angle the bevel edges can look
  doubled at grazing views.
- I added no CreatureStage screenshot shot here (shots are done centrally).

## Review log
