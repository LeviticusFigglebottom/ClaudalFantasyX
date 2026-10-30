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
- **Battle variety (M3-CRE-612).** Unless a build authors its own, `export_creature` adds `hit_b` (the hit mirrored
  and 1.35× heavier, so a recoil can go to the other side) and `idle_b` (the special at 0.3× and 1.4× speed, in
  place: a fidget). CreatureActor rotates hits through creatures.json `hit_variants` (outside phases that map their
  own hit) and plays the `idle_variety` fidget once every `every_sec` [min, max] while it idles on its own idle
  clip, outside phases, playing (never on a portrait's paused pose) and alive; the interval comes from a hash of its
  node path, so a scene replays the same way.
- **Hits land on the contact frame (M3-CRE-617).** Every `hit` peaks 0.10–0.20 s in (authored so). A hit cuts into
  its clip at creatures.json `hit_snap.preroll_sec` (0.067 s since M3-CRE-630 put clips on time: about half its
  recoil, measured over all 42 hits; a row overrides it for a late peak, as the ashwing's 0.1 s) with no cross-fade, so the frame
  battle-presentation's hit-stop holds (M3-BPR-401) shows the blow landing, not the pose the hit came from; the
  rest of the recoil plays after the hold. Strikes, casts and every other clip still start at 0 with the row's
  blend. A boss's hit has real weight too: the Drownbell rocks back on braced legs with its rim ringing, the Cinder
  Matron rocks back under her plates, the tower limpet clamps and tips on its foot, the Undertow's Reach's hand is
  thrown back. A new `hit` should keep its peak near 0.1 s.
- **In place (battle-presentation's clip contract, M2-BPR-02).** The strike clips `attack` and `cast` play in place:
  the sequencer moves the fighter to its target, so `export_creature` drops the `root` bone's horizontal travel in them
  (`IN_PLACE_CLIPS`). Author the lunge on `root` if you like; vertical travel (a dive, a hop), body leans and `hit`'s
  knock-back stay. The contact second in creatures.json `contact` is what the sequencer syncs the blow to. The
  contract's other names (`dodge`, `defend`, `ready`, `victory`) are optional; a creature without them gets the
  sequencer's procedural fallback. Audit of all 27 creatures (2026-10-24): each has `idle`, `attack`, `cast`, `hit`
  and `ko`, and no strike clip keeps horizontal root travel.
- **On the floor (M3-CRE-631, M3-CRE-632).** No vertex of any baked frame of any clip goes under y 0 (5 mm
  tolerance), checked by skinning the GLB for **every** creature in creatures.json (tools/tests/test_creatures.py
  `GroundedClipsTest`). A flier is measured with its `stand_in.hover` added (the stand-in lifts it by that much), so
  its KO must land on the floor. Only a creature whose sheet puts it below the floor is exempt, in the test's
  `ALLOW` with the sheet cited: the hullgnaw and the lantern eel (out of the water or sand), the Mangrove Drowner
  (roots in the water), the Undertow's Reach (out of the storm behind the wall), the Wakefin (swims), the tannin
  archer (half out of the fen's water). For a limb planted at rest, `common/grounding.py` does it:
  `grounded(rig, mesh, clips, limbs, floor)` poses the mesh at every frame as the export does and turns (or lifts)
  each listed limb by the least amount that keeps it on the floor, so a foot stays planted while the body bobs over
  it. It derives `hit_b` and `idle_b` first, so a correction is never mirrored. A limb may turn about a weighted axis
  (`(wx, wy, wz)`, a leg splayed round a body), be limited to some clips (a fifth item), or be the root (a lift of
  the whole body, e.g. a KO that rolls about a pivot on the floor); `mesh` may be a list (the body and its extra
  meshes), and a flier passes `floor=-HOVER`. Most creatures now export through it (`export_clips`). Author a KO
  that lies on the floor; the grounding only trims what is left.
- **Determinism.** No randomness except a seeded `np.random.default_rng(SEED)` and the kit's hash noise; no
  exported tangents (Godot makes them on import). Two runs are byte-identical, which the gate checks.
- **Budgets** are in each sheet (5k to 16k triangles). Keep each GLB well under 5 MB (the crab is about 0.8 MB).

### Planted feet (the Act I final-quality audit, 2026-10-29)
`grounded()` keeps a foot on the floor but let it slide along it while the body skitters, rears or recoils (the audit
measured up to 37 cm). `common/grounding.py pinned(rig, mesh, clips, legs)` holds a planted foot where it touched down:
while a leg's tip is within `PLANT_M` (3 cm) of the floor, a damped least-squares solve turns the hip (yaw and bend)
and the knee so the tip keeps its spot, lifting the target when a toe or pad would go under the floor; the correction
eases out over `RELEASE_FRAMES` once the foot lifts, and the turns are rounded so builds stay byte-identical. It runs
on idle, ready, attack, cast and hit clips (a KO collapses: its feet go where it falls). A build that uses it:
`gr.reground(rig, mesh, gr.pinned(rig, mesh, gr.grounded(...), PINNED_LEGS), GROUNDED_LIMBS)`; `PINNED_LEGS` is
`(upper bone, lower bone or None, bend axis, sign)` per leg. On: the tide crawler, the crab family (reef, wall, wreck,
root), the raid hound, the vein sparker, the bottle hermit, the shoal skipper.
- **Measure:** `python3 tools/creatures/foot_slip.py <id>` (numpy, the build's own clips) and
  `godot --headless --path . -s tools/creatures/clip_audit.gd [-- id ...]` (the imported GLBs: slip, one-frame pops,
  loop seams, floor penetration, missing hit/KO/idle/talk/walk). `tools/creatures/clip_sheet.tscn` renders each
  actor's close-up and its idle, attack, hit and KO poses on one fixed camera over a checker floor (see its header).

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

**LODs (checked 2026-10-24, the Lead's LOD1 ask).** The creatures need no authored `-lod1` chain. Godot's import-time
LODs (`meshes/generate_lods=true`) work on the skinned creature meshes: every surface carries an index-only LOD chain
whose first level is about half the triangles. For example, the reef crab's shell 3,872 → 1,936 → 968 → 484, the gull
harrier's body 6,240 → 3,120 → 1,560, and the Drownbell's body 11,024 → 5,512 → 2,756, with the `Rim` and `RimBroken`
meshes reduced the same way. Godot picks the level by screen-space error (`mesh_lod_threshold`, 1 px by default), so
a creature drops detail only where the loss is under a pixel. An authored chain (`<mesh>-lod1` plus a `lods.end_m`
table, asset_import.md §3) would add a distance cutoff, which battles, held at 5–15 m, don't need. Re-check with
`godot --headless --path . -s tools/dev/creature_lods.gd [-- <id> ...]` if a creature ever goes on the field at range.

## 5. Battle (M2-CRE-03)

- **`enemies.json` `model`** names the creature's actor scene. `CreatureModels` reads it, and
  `BattleStage.stand_in_spec` turns it into the FighterStandIn spec's `scene` (the UI track's M2-UI-07 hook) plus
  creatures.json's `stand_in` overrides (`yaw_deg` 90 turns a +Z-facing model toward the party). The spec's
  `height` (battle_sandbox.json) still places the damage numbers and the VFX anchors (effects.json
  `anchor_heights`), so **build the model to that height**. An enemy without `model` keeps its primitive.
- **A Vowbound (M3-CRE-638)** has no enemies.json row. Its creatures.json row has the Vowbound's id (a
  game/data/battle/vowbound.json row) and `"vowbound": true`, and `CreatureModels.stand_in_overrides` gives that id's
  stand-in the row's `scene` and `stand_in` the same way (Ilun: `yaw_deg` −90, facing the foes as the heroes do).
  validate_creatures.py checks the id and that no enemy uses the scene. The VFX anchors are fractions of the height
  from the ground and ignore `hover`, so a hovering Vowbound is built hovering (origin at the water) instead.
  A Vowbound with no battle_sandbox.json stand-in row (UI's) gives its own `height` and `radius` in its `stand_in`
  (M3-CRE-640, Kahre: 3.3 and 0.75), merged last, so the anchors and the ring fit the model. **Check the default
  camera**: the Vowbound slot's mark sits at 0.765 of the screen width and the safe frame's right edge at 0.85, so
  only about 0.85 m behind the mark is inside it; a model long along the battle axis has to be built compact.
  A Vowbound built ahead of its vowbound.json row (Combat's) carries `vowbound_pending` (M3-CRE-642, Nhoa): a
  string naming the task that asks for the row. The validator then allows the missing row, and it is an error once
  the row exists, so drop the key when the row lands. Its integration test binds an in-test copy of a live row under
  its id. The summon shot's bottom safe line is about 0.6 m up on the mark, so anything lower (feet, strands) sits
  under the HUD there, which is expected; check the top edge on that shot instead.
- **A Vowbound as a foe (M3-CRE-647, the Ch20 releases)** is a second creatures.json row, `<id>_held`, with no
  `vowbound` key (validate_creatures.py forbids an enemy using the ally's scene). Its scene
  `game/creatures/<id>/<id>_held_battle.tscn` instances **the same GLB** (one model, so ally and foe never drift)
  and sets `CreatureActor.material_dir = "res://assets/creatures/<id>/materials_held"`. **Why an actor override,
  not the import:** one GLB has one import, and the post-import already bakes the `materials/` set onto it as
  surface overrides, so a second set cannot come from the import. In `_ready` the actor puts
  `<material_dir>/<slot>.tres` on each surface whose current material's `resource_name` is `<slot>` (the import's
  `.tres` names itself by slot), the same slot mapping the post-import uses. The set is written by
  `write_materials.py` from a `held` block in materials.json (`emission_from` glimmer_bound, `emission_to`
  glimmer_held): every emissive slot swapped at the same energy, steady, the rest copied, so the job lists
  `materials_held/*.tres` as an output. Without the block nothing more is written. The row's `ko` is the `release`
  clip, `stand_in.yaw_deg` is 90 (a foe faces the party), and `phases.release` is `{"clip": "release", "hold":
  true}`: a **`hold`** phase stays on its clip's last frame instead of going back to idle, `settle()` jumps there,
  and a KO whose clip is the held one doesn't replay it. The change back to `glimmer_lift` and the rising motes are
  presentation (battle VFX), not the model. No enemies.json row: Combat and the chapter designer add those.
- **`game/creatures/<id>/<id>_battle.tscn`**: a `Node3D` root with `creature_actor.gd` (`creature_id = &"<id>"`,
  `metadata/hymn_battle_actor = true`) and the GLB instanced as its first child, `Model`.
- **`CreatureActor`** (`game/creatures/creature_actor.gd`) plays what creatures.json says: an action's clip
  (`clip_by_skill`, else `clip_by_kind` by the skill's kind), `hit`, the `ko` clip held and faded to
  battle_sandbox.json's `ko_alpha` (no sink), a freeze under Petrify (FighterStandIn swaps the surfaces to stone),
  a boss's phase (`phases.<id>`: a clip, an idle afterwards, an offset and tilt of the model over `sec`, node names
  to `hide` or `show` at once (nodes a phase shows start hidden), `hide_after` and `show_after` nodes changed
  once the clip has played, and a `clips` map of stand-in
  clips the phase plays instead, e.g. `attack` → `attack_dark`, which `play_clip` and `contact_time` follow), and
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

## VFX anchors (M3-CRE-651, ADR 0041)

A creatures.json row may name `vfx_anchors`: `{"core": "<bone>", "wound": "<bone>"}`. **core** is the body's centre
(a thorax, a chest, a shell), **wound** the bone that carries its `spawn_wound` weak point (ADR 0151): the bone
with the most masked vertices (`TEXCOORD_1.y`). `CreatureActor.vfx_anchor(&"core" | &"wound")` returns that bone's
world position as the clip has posed it this frame; a row without a wound uses its core, and a row without anchors
answers `Vector3.INF` (the caller falls back to the stand-in's `anchor_heights`). Every Act I regular has them
(tools/tests/test_creatures.py `ACT1_REGULARS`). Battle VFX starts the spawn effect and the KO effect there.
