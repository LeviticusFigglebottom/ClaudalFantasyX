---
id: M3-CRE-638
title: "Build Ilun, Asha's Vowbound, as a creature model and attach it to the Vowbound stand-in"
role: character
status: review
owner_session: "creatures (worktree-agent-a9ff131d70b099e46, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-637]
milestone: M3
request-from: lead
---
## Goal
Ilun (docs/kb/story/vowbound.md §1, game/data/battle/vowbound.json `ilun`) was a teal placeholder capsule in battle
(battle_sandbox.json `stand_ins.ilun`), in the slice's one Vowbound call (shots `battle_vowbound_out`,
`battle_choreo_summon`, `battle_choreo_vowbound_rise`). Build him through the creature pipeline from a design sheet
and show him on the Vowbound stand-in without editing UI's or battle-presentation's files. **His first PC render is
pending:** this environment may not render, so he was checked numerically and on silhouette sheets drawn from the
build's own vertices (below), and his review shot has no baseline yet.

## Acceptance criteria
- [x] Design sheet `docs/kb/art/creatures/vowbound/ilun.md`: silhouette and size (4.6 m wingspan, checked against the
      camera `summon` shot and the default battle camera), palette swatches, the bound light (`glimmer_bound` 1.2,
      steady), the net, the heron's crest, the glass net-float, the clips and their timings, the rig, the budget. No
      weak point (ADR 0151 is for foes).
- [x] `assets_src/creatures/ilun/build_ilun.py` on the creature kit: a spectral manta 4.6 m across (falcate tips),
      1.85 m disc, built **hovering** (the disc's mid-plane 1.35 m over the origin, the water), wings **mantling**
      (rising 8 cm at mid-span then arching down to tips 0.80 m over the water: a heron's canopy, which also turns the
      near wing's back to the default camera); a 1.3 m drooping tail; three long and two short heron plumes to
      1.92 m; two rolled cephalic lobes (scrolls, not horns) and soft glowing eyes; the knotted net of light on both
      faces of both wings as geometry (135 strands, 63 knot beads per face, a 0.21 m diamond mesh, jittered by a seeded
      rng; per-vertex emission could not draw lines that thin); the child's glass float (19 cm) in a `sand_cloth` cord
      net on a 16 cm cord from the tail tip. 16 bones.
- [x] **13,655 triangles** (budget 16k): membrane 4,880, net 2,792, body 1,920, crest 1,320, cord 1,191, tail 544,
      lobes 448, glass 320, eyes 240. 8,697 vertices. GLB 1.29 MB. Seven slots: `body`, `membrane`, `net`, `crest`,
      `eye`, `glass`, `cord`.
- [x] Clips (13): `idle` 4.0 s loop, `ready` 1.4 s, `attack` 1.2 s (contact 0.55 s), `cast` 1.6 s (contact 0.8 s),
      `hit` 0.5 s (peak 0.12 s; GLB peak 0.13 s), an authored `hit_b` (rolled the other way, 1.35×: the kit's mirror
      would flip the wings' flinch down), `defend` 1.2 s, `ko` 1.8 s, `victory` 2.2 s, `rise` 2.6 s, `dismiss` 1.0 s,
      `special` 2.4 s (contact 1.45 s), and the kit's `idle_b`. The float counter-turns its parents' pitch and roll
      (0.85 of it, 0.15 s behind), so it hangs and swings.
- [x] materials.json and write_materials.py; every emissive slot `glimmer_bound` #4FB3B0 at 1.2 with no pulse; the
      glass and its cord are not lit. The Blender job `creature_ilun` (appended). PROVENANCE rows (their own commit).
      **`verify_blender_builds.py --job creature_ilun`: 8 identical.**
- [x] Import rule lists `res://assets/creatures/ilun/`; the `.glb.import` runs the creatures post-import script.
- [x] `game/creatures/ilun/ilun_battle.tscn` and the creatures.json row `ilun`: `"vowbound": true`, `clip_by_skill`
      (`brine_lash` → `attack`, `tidal_ward` → `cast`, `floodnet` → `special`), contacts, `stand_in.yaw_deg` −90 (he
      faces the foes, as the heroes' actors do), no `hover` (the VFX anchors are fractions of the sandbox's 2.3 m height
      from the ground and ignore hover, so he is built hovering instead: chest 1.38 m lands on his disc).
- [x] **The attach.** `CreatureModels.stand_in_overrides(base)` (which `BattleStage.stand_in_spec` already merges)
      now also answers for a creatures.json row whose id is `base` and that has `vowbound` true and a `scene`
      (`CreatureModels.vowbound_creature`): it gives `{scene, yaw_deg}` like an enemy's model. Enemies go the old way
      first; a row without `vowbound` gives nothing. No UI or battle-presentation file changed. FighterStandIn's
      `scene` hook instances him, turned by `yaw_deg`, playing his `idle`; BattleClips plays `ready` (the entry and
      dismissal) and `ko` (the fall) on him through CreatureActor, and `special` through `clip_by_skill`.
- [x] `tools/validate_creatures.py`: `vowbound` (a bool; when true the id must be a vowbound.json row and no enemy
      may use the scene as a `model`), with a test in tools/tests/test_creatures.py.
- [x] Godot tests `tests/unit/test_creature_ilun_vowbound.gd` (matched by both `--filter=creature` and
      `--filter=vowbound`): the stand-in for `ilun` resolves to the model (scene, yaw −90, no hover, the sandbox height
      kept; gallery_ray and asha get nothing); the scene loads headless with all 13 clips, the skill mapping and the
      contacts; FighterStandIn plays `ready` and `ko` on it and hands it the KO; the idle undulates, the rise starts
      folded, the KO tips him nose up with the float still hanging, Floodnet sweeps the wings down on the contact.
- [x] Shot `creature_ilun` (idle, three-quarter, with the heroes' scale bars) appended to tests/screenshots/shots.json
      with a stage scene like the others'. **Not captured; no baseline: it needs the PC render.**
- [ ] Bestiary portrait: **skipped on purpose.** The bestiary logs foes only (Bestiary.record_defeated per enemy, Read
      on foes), so Ilun has no page and no portrait was added to tools/portraits/portraits.json. See the request to
      menus below.

## Numeric check (no render)
Measured from the exported GLB by skinning every baked frame of every clip (tools/tests/test_creatures.py
`skinned_lowest`); the numpy report (`python3 assets_src/creatures/ilun/build_ilun.py --report`) gives the same.

| Clip | Length | Lowest vertex y | Notes |
|---|---|---|---|
| idle | 4.0 s | 0.341 | wings 8°/10°/13° in a travelling wave, body ±4 cm |
| ready | 1.4 s | 0.442 | wings high at 0.5 s, down-stroke at 1.0 s, rest at 1.4 s |
| attack | 1.2 s | 0.067 | the lashing wingtip at the contact (0.55 s) |
| cast | 1.6 s | 0.442 | the wings curl forward round his front by 0.8 s, held to 1.15 s |
| hit | 0.5 s | 0.364 | peak 0.13 s |
| hit_b | 0.5 s | 0.342 | peak 0.13 s |
| defend | 1.2 s | 0.347 | held 0.3–0.85 s |
| ko | 1.8 s | 0.221 | nose up 24°, settles 0.12 m (root), held from 1.45 s |
| victory | 2.2 s | 0.442 | rises 0.25 m by 0.8 s |
| rise | 2.6 s | 0.265 | starts folded (wingtips 1.6 m over the body), open by 1.4 s |
| dismiss | 1.0 s | 0.353 | ends folded, the highest frame of all (3.42 m) |
| special | 2.4 s | 0.174 | wings high and the body up 0.3 m by 0.9 s, the sweep at 1.45 s |
| idle_b | 1.14 s | 0.442 | the kit's fidget |

- Rest: x ±2.30, y 0.44 (the float's bottom) to 1.92 (the crest), z −2.15 to +0.85.
- **No clip goes under the water**, so no GroundedClipsTest allow-list entry. `rise` and `dismiss` are in place (the
  stage does the 2.6 m of travel), so they need none either. The KO test's grounded branch holds (the root drops
  0.12 m).
- Colours: `deep_teal_shadow` #0E4A55, `lagoon_teal` #1FA3A6, `salt_glass` #BFE6E0, `sand_cloth` #C9B48E (albedo) and
  `glimmer_bound` #4FB3B0 (emission), all palette.json swatches, inside the albedo floor and ceiling.
- **Silhouette sheets** (numpy and PIL from the build's vertices, painter's algorithm, no Godot):
  `/tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-638/ilun_views.png`
  (six rest views), `.../ilun_clips.png` (16 key poses), `.../ilun_summon.png` (the summon shot with the HUD safe
  frame) and `.../ilun_default_camera.png` (the default battle camera on the Vowbound slot). Scratch, not committed.

## Requests
- **battle-presentation (choreo.json, `game/battle/scene/**`): play `rise` and `dismiss`.** Set
  choreo.json `vowbound.entry.clip` and `summon_cinematic.entry.clip` to `"rise"` (2.6 s: the wings unfold from a
  closed shell over his back, timed to C10's 2.6 s rise) and `vowbound.dismiss.clip` to `"dismiss"` (1.0 s: the wings
  close over his back and the nose dips; it ends folded, and the stage's sink is 0.9 s). BattleClips.play already plays
  any clip the model has, so no code change is needed; if validate_choreo.py limits `clip` to the contract names, it
  needs `rise` and `dismiss` allowed, or a fallback to `ready` for a Vowbound without them. Until then `ready` plays
  on both and reads acceptably. `ko` is right for the fall as it is, and `special` already plays for Floodnet through
  creatures.json `clip_by_skill`. Please re-approve `battle_vowbound_out`, `battle_choreo_summon` and
  `battle_choreo_vowbound_rise` after his first render: they now show the model instead of the capsule.
- **menus (tests/unit/test_creature_portraits.gd): skip Vowbound rows.**
  `test_every_manifest_creature_exists_with_a_provenance_row` asserts that every creatures.json row has a bestiary
  portrait. Ilun is an ally with no bestiary page, so it now also fails on "creatures.json row ilun has a portrait in
  the manifest", inside the test that is already red for the PNGs the PC has not baked. The fix: skip rows whose
  `vowbound` is true in that loop (or `CreatureModels.vowbound_creature(id) != &""`). If menus would rather have a
  portrait of him (a Vowbound menu later), append a manifest row instead and the PC bakes it.

## Notes
- **Translucency.** The creature shader is opaque, so he reads as spectral through value and light: a deep core, pale
  thin margins, a strong rim sheen on the wings and crest, a faint inner glow (emission mask 0.08–0.10 on the body),
  and the bright net. True alpha would need a `creature_spectral` shader and a per-slot shader in
  `common/write_materials.py`, which reruns every creature job; decide after the first render.
- **The summon camera is behind him.** `summon` is anchored on the target and placed `back_m` along the battle axis,
  so for a party-side fighter it sits behind him and low: it looks up at his belly, the mantle and the float with the
  foes beyond. The tail was shortened and drooped so the float hangs inside the safe frame instead of reaching the lens.
- **The default camera sees him nearly edge-on** (about 8° above his wing plane on the back party slot). The mantle's
  arch is what shows the near wing's back and its net there; check this first on the render.
- **For the first PC render:** the net's brightness against the body (1.2 is the colour script's value; the frame
  limit for glimmer at a set piece is 35%), whether the body reads deep and the margins pale (spectral) or just teal,
  the float's glass on the summon frame, and the three Vowbound battle shots.

## Review log
