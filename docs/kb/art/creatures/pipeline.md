# Creature pipeline (M2-CRE-02, M2-CRE-03)

How a battle creature goes from a design sheet to the battle stage. The design sheets are in this folder
([README.md](README.md)); the reef crab is the worked example.

```
assets_src/creatures/<id>/build_<id>.py ──Blender──> assets/creatures/<id>/<id>.glb  (mesh, rig, clips)
assets_src/creatures/<id>/materials.json ─python──> assets/creatures/<id>/materials/<slot>.tres
game/creatures/<id>/<id>_battle.tscn  (CreatureActor root + the GLB)
game/data/creatures/creatures.json    (clip map, loops, KO fade, phases, breakable parts)
game/data/battle/enemies.json  "model": "res://game/creatures/<id>/<id>_battle.tscn"
```

## 1. Build (`assets_src/creatures/`)

- **`common/creature_kit.py`** is shared: a numpy mesh builder in **Godot axes** (x right, y up, the creature
  facing **+z**, metres, the ground at y = 0), primitives (`lathe`, `ellipsoid`, `tube` along a path, `bezier`),
  deterministic noise (`value_noise`, `fbm`), a bone rig (`Rig.add`, rigid or blended skinning), clips (`Clip.key`,
  `Clip.wave`), and `export_creature`, the only part that needs Blender.
- **`<id>/build_<id>.py`** builds one creature: `build_rig()`, `build_mesh(rig)`, `build_clips()`, then
  `export_creature(mesh, rig, clips, out)`. Run it with
  `blender --background --factory-startup --threads 4 --python assets_src/creatures/<id>/build_<id>.py -- --out assets/creatures/<id>/<id>.glb`.
- **Vertex data** carries the look, so no textures are needed (the shader reads it):

  | Channel | Meaning |
  |---|---|
  | `COLOR_0.rgb` | albedo, an sRGB palette colour (`ck.hexrgb("#...")`, mixed per vertex) |
  | `COLOR_0.a` | wetness, 0 dry .. 1 wet (darker, glossier, clearcoated) |
  | `TEXCOORD_0` | a rest-pose detail coordinate in metres (the shader's noise domain; `finish` derives one) |
  | `TEXCOORD_1.x` | cavity, 0 open .. 1 deep (darkens albedo, adds AO) |
  | `TEXCOORD_1.y` | emission mask: the `spawn_wound` weak points |

  `ck.finish(mesh, P, T, slot, color, bones, wet=, cavity=, emission=, flat=)` adds a part. `slot` is the glTF
  material name. `bones` is a bone index (rigid), `rig.blend(...)` or `rig.chain(...)` (two influences at most).
- **Clips.** Keys are rotations in degrees about the **rest axes** (X first, then Y, then Z), plus a location
  offset, per bone, at times in seconds. A child inherits its parent's motion. Keys ease in and out (a smooth hold
  at each key), and every frame is baked at 30 fps, so the glTF is sampled and Godot plays exactly what was
  authored. A looping clip must end where it starts (`Clip.wave` does).
- **The clip set** (design sheets; README rule 6): `idle` (loops), `attack`, `cast`, `hit`, `ko`, and for the
  boss `phase_change` plus a phase idle. Every creature has all five, even when no slice skill uses one yet.
- **Determinism.** No randomness except a seeded `np.random.default_rng(SEED)` and the kit's hash noise; no
  exported tangents (Godot makes them on import). Two runs are byte-identical, which the gate checks.
- **Budgets** are in each sheet (5k to 16k triangles). Keep each GLB well under 5 MB (the crab is about 0.8 MB).

## 2. Materials

`assets_src/creatures/<id>/materials.json` lists the slots and their parameters on
`game/shaders/creature/creature.gdshader`. `python3 assets_src/creatures/common/write_materials.py --creature <id>`
writes `assets/creatures/<id>/materials/<slot>.tres`. Colours are palette hex values.

**Why a creature shader, not the character families.** The character shaders (`game/shaders/character/`) are
built around baked texture sets (albedo, normal, ORM, skin masks) and the hero tiers. Creatures carry their look
in vertex data and need wetness with clearcoat and an emissive weak-point mask, which those shaders don't read. The
creature shader is one small, tier-independent surface (procedural detail noise and bump from TEXCOORD_0, cavity,
wet, emission with an optional slow pulse, an optional rim sheen for fins). It renders on lavapipe and is cheap on
every preset. If a creature ever needs subsurface skin, use `character_skin` for that slot.

## 3. Reproducible jobs and provenance

Each creature has a job in `tools/dev/blender_builds.json`:

```json
{"id": "creature_<id>", "owner": "character",
 "sources": ["assets_src/creatures/<id>/**", "assets_src/creatures/common/**"],
 "outputs": ["assets/creatures/<id>/*.glb", "assets/creatures/<id>/materials/*.tres"],
 "runs": [["{blender}", "--python", "assets_src/creatures/<id>/build_<id>.py", "--", "--out", "assets/creatures/<id>/<id>.glb"],
          ["{python}", "assets_src/creatures/common/write_materials.py", "--creature", "<id>"]]}
```

`python3 tools/dev/verify_blender_builds.py --job creature_<id>` must print `identical`. Add a PROVENANCE row per
committed file (GLB and each `.tres`). `tools/tests/test_creatures.py` checks the job, the rows, the import script,
the clip set and the material files. **A change to `common/` reruns every creature's job**, so rebuild and
recommit all of them after a kit change.

## 4. Import (`creatures` category)

`game/data/import/creatures.json` with `game/core/import/creatures_post_import.gd` (docs/kb/tech/asset_import.md):
each glTF material slot gets `<asset dir>/materials/<slot>.tres`. Godot's auto LODs; no collision. Add each new
creature folder to the rule's `assets` list (the folders are not searched recursively), and set
`import_script/path="res://game/core/import/creatures_post_import.gd"` in the `.glb.import` (run
`godot --headless --path . --import` once to create it, edit the line, import again).

## 5. Battle (M2-CRE-03)

- **`enemies.json` `model`** names the creature's actor scene. `CreatureModels` reads it, and
  `BattleStage.stand_in_spec` turns it into the FighterStandIn spec's `scene` (the UI track's M2-UI-07 hook) plus
  creatures.json's `stand_in` overrides (`yaw_deg` 90 turns a +Z-facing model toward the party). The spec's
  `height` (battle_sandbox.json) still places the damage numbers and the VFX anchors (effects.json
  `anchor_heights`), so **build the model to that height**. An enemy without `model` keeps its primitive.
- **`game/creatures/<id>/<id>_battle.tscn`**: a `Node3D` root with `creature_actor.gd` (`creature_id = &"<id>"`,
  `metadata/hymn_battle_actor = true`) and the GLB instanced as its first child, `Model`.
- **`CreatureActor`** (`game/creatures/creature_actor.gd`) plays what creatures.json says: an action's clip
  (`clip_by_skill`, else `clip_by_kind` by the skill's kind), `hit`, the `ko` clip held and faded to
  battle_sandbox.json's `ko_alpha` (no sink), a freeze under Petrify (FighterStandIn swaps the surfaces to stone),
  a boss's phase (`phases.<id>`: a clip, an idle afterwards, an offset and tilt of the model over `sec`, node names
  to `hide` or `show` at once, and `hide_after` nodes hidden once the clip has played), and
  breakable parts (`break_parts.<charge skill>`: node names shown `whole` or `broken`).
- **`BattleActorMotion`** (`game/creatures/battle_actor_motion.gd`) is attached by `BattleStage.spawn` and listens
  to the engine: `action_resolved` (the actor's clip, `hit` on each foe a landed damaging hit reaches),
  `phase_changed`, `charge_started` (the part mends) and `charge_broken` (it breaks). It never writes combat state,
  and battle_controller.gd is untouched.
- **Known limit:** clips start when the engine resolves the action, like the VFX (battle_vfx.md "Known limits"), so
  a strike's contact frame lands about half a second after its sparks. Deferring both to a contact marker is the
  next step once the hero clips exist.
- `tools/validate_creatures.py` (run by validate_data.py) checks creatures.json and every `model`.
  `tests/unit/test_creature_actor.gd` covers the actor, the stand-in hand-off and a live sandbox battle.

## 6. Review

`game/levels/_tests/creatures/creature_stage.tscn` (`CreatureStage`) shows one creature or a lineup in the
sandbox's noon light, holds a clip at a time, frames the camera from a named view (`creature_stage.json`:
`three_quarter`, `side`, `front`, `top`, `back`), and can add bars at the heroes' heights. The creature shots in
`tests/screenshots/shots.json` are small scenes that inherit it.

## 7. Adding a creature (checklist)

1. A design sheet in this folder.
2. `assets_src/creatures/<id>/build_<id>.py` and `materials.json` (copy the crab's structure).
3. Build, write the materials, import; set the `.glb.import` script line; add the folder to
   `game/data/import/creatures.json`.
4. `game/creatures/<id>/<id>_battle.tscn` and a creatures.json row (`scene`, any `clip_by_skill`).
5. `"model"` on the enemies.json row.
6. The Blender job, PROVENANCE rows; `verify_blender_builds.py --job creature_<id>` identical.
7. Shots (CreatureStage) and the battle shots it changes, viewed and re-approved.
8. Gates: `validate_data.py`, `python3 -m unittest discover -s tools/tests -p "test_creatures.py"` (and
   `test_post_import.py`), gdlint/gdformat, Godot `--filter=creature`, `--filter=post_import`, `--filter=battle`.
