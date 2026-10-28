---
id: M3-CRE-624
title: "Build the Avalanche Ram (Act II, Ch12 boss) from its design sheet"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a1f335e70d81fd58f (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The third Act II build from M3-CRE-620's sheets: the Avalanche Ram (`avalanche_ram`,
docs/kb/art/creatures/act2/avalanche_ram.md) through the creature pipeline (docs/kb/art/creatures/pipeline.md). It is
an Ullari woolback grown huge: a long-necked shaggy pack animal, not horned and not demonic.

## Acceptance criteria
- [x] `assets_src/creatures/avalanche_ram/build_avalanche_ram.py` on the creature kit: a deep-chested barrel 4.0 m long
      (rump fleece to muzzle), the neck rising off the chest to the head at 2.86 m (the woolly cap tops out at
      3.08 m). The coat is `sand_cloth` gone grey to `overcast_slate` in the shadows and furrowed into hanging locks,
      with `salt_glass` ice plates matted into the lower coat. Six chains of nine heavy frozen locks hang to the knees
      (tips at 0.56–0.72 m), iced at their ends. There is a bib of locks down the chest front and a mane under the
      throat. `salt_glass` icicles hang at the lock tips, under the jaw and along the belly. The muzzle, jaw and legs
      are `laterite` darkened (×0.52) and the hooves are broad pads. A faded `lacquer_red` herd-cord with three knots
      and a frayed end is tied round the lower neck. Seven `spawn_wound` partings sit in grooves of the coat (three
      a side and one along the withers), their lips tinted toward `glimmer_held`. Every colour is a palette.json
      swatch, mixed or darkened.
- [x] 15,179 triangles (budget 16k), 38 bones: root, `body` (the carrier the legs hang from), spine 5, neck 5, head,
      jaw, four legs of 3 (`*_upper`, `*_lower`, `*_foot`) and six lock chains of 2 (`lock<k>_a`, `lock<k>_b`).
      Deterministic: `verify_blender_builds.py --job creature_avalanche_ram` prints 5 identical.
- [x] Clips:
      - `idle` (4 s): the neck sways, it chews, the locks swing.
      - `attack` (1.6 s): the charge. The head drops, the right fore lifts and stamps, and it drives through, with
        contact at 0.75 s. Its peak is at 0.77 s, and the hooves are back where they stood at the end.
      - `cast` (1.8 s): the bellow. The neck rises, the head lifts and the jaw opens, peaking at 0.93 s.
      - `hit` (0.6 s): it staggers back and the neck whips, peaking at 0.10 s, the locks lagging.
      - `ko` (3.8 s): it kneels on its fore knees, lies down with its legs folded under it (kush), spreads its locks
        on the ground and lays its head down. There is no thrash.
      - `hit_b` and `idle_b`: the kit's variety clips.

      The legs are keyed every frame from a grid solve in each leg's plane (`solve_leg`), so planted hooves stay at
      y 0 under the moving body and the KO's folds stay off the ground. `--report` prints the per-clip bounds
      without Blender.
- [x] Measured from the GLB (skinned at every baked frame, no render):
      - nothing goes below y 0 in any frame of any clip (lowest −0.001 m, in the KO);
      - every hoof is at y 0 in the idle and at the end of the idle, attack, cast, hit and hit_b;
      - the KO ends lying at 0.00..1.61 m, with the head at 0.26–0.68 m;
      - the head top is 3.08 m at rest and 3.72 m at the bellow's peak.
- [x] materials.json (`fleece` with the `spawn_wound` emission, `hide`, `ice`, `eye`) and write_materials.py; the
      Blender job; PROVENANCE rows (their own commit).
- [x] game/creatures/avalanche_ram/avalanche_ram_battle.tscn and the creatures.json row: contacts (attack 0.75,
      cast 0.9), `ko_fade_sec` 1.2, `stand_in.yaw_deg` 60 (three-quarter toward the camera, so the long body
      doesn't fill the lane side-on), and `portrait` yaw 40 and pitch 10 with default lights (it is pale). No phases.
- [x] Import rule lists the folder; the `.glb.import` runs the creatures post-import script.
- [x] tests/unit/test_creature_actor.gd: the charge and the bellow play with the charge's contact. It has no phases,
      and the rig has the sheet's bones. Every hoof bone is back at rest at the end of idle, attack, cast, hit and
      hit_b, and in the KO the head lies below 1 m with every bone above the ground.
- [x] Shot `creature_avalanche_ram` (three-quarter, idle) in tests/screenshots/shots.json with its stage scene.
- [ ] **PC render pending:** no captures in the cloud environment (human directive). The PC renders
      `creature_avalanche_ram`, a reviewer views it, and only then does its baseline go in.
- [ ] Encounter (not this task): an enemies.json row with `model` when the Ch12 encounter is designed.

## Notes
- The KO lowers `body` by 0.5 m, not `root`: tools/tests' grounded-KO check reads the root, and the GLB measurement
  above shows the KO never goes through the ground.
- Not modelled, by the sheet (VFX): the breath steam, the snow the bellow brings down off the terrace wall (the field
  hazard), the ice that cracks off on a hit and the `glimmer_held` the partings shed. Request VFX when the
  encounter exists.
- Things to judge on the PC render:
  - the chest front is smoother than the flanks;
  - the attack's raised fore shows its woolly upper leg at the barrel's edge;
  - the muzzle may read long at portrait distance.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.
