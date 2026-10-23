---
id: M1-ART-02
title: Godot post-import scripts per asset category
role: character
status: done
owner_session: "worktree-agent-a21af6e9e71ccbfda"
depends_on: []
milestone: M1
request-from: ""
reviewer: rendering
---
## Goal
ADR 0005 step 4.

## Acceptance criteria
- [x] Material assignment, LODs, collision, and PLACEHOLDER metadata

## Notes
- One `EditorScenePostImport` per category in `game/core/import/` (`haluna_kit`, `vegetation`, `base_body`, `shader_test`, `characters`). Each one names its kind and calls `AssetImportRules` (no editor dependency). The rules are data in `game/data/import/<kind>.json`. Design and adoption: `docs/kb/tech/asset_import.md`.
- Wired into 42 `.glb.import` files: kit ×30, vegetation ×7, base body ×3, shader test ×2. The only change is the `import_script/path` line. **Asha's two `.import` files are untouched** (M1-CHR-03 is rebuilding her). She is listed under `adoption_pending` in `characters.json`, and the doc gives the five adoption steps.
- Materials go on as **surface overrides**, so the glTF slot (`resource_name`) survives for HalunaDresser, VegetationPlant and AshaStage, and their runtime overrides still win. The base bodies keep their `PLACEHOLDER_*` glTF materials. The shader-test meshes get no materials: `CharacterShaderTiers.apply_to_tree` mutates surface overrides in place, and the Low comparison leaked into High (caught by `test_character_shading`).
- LODs: authored `-lodN` chains get the dressers' default visibility ranges. Auto LODs stay the `.import` option, which the rules state and the test checks.
- Collision: a `-col` proxy (Godot leaves it visible, with a trimesh body child) becomes the body alone, with the rules' shape (trimesh or convex), layer and mask. No committed asset has one yet. HalunaCollision still builds the walk collision at runtime.
- PLACEHOLDER: glTF extras (`hymn_tag` or a `placeholder` note) → meta `hymn_tag = &"PLACEHOLDER"` on the node and the root, plus `hymn_placeholder_notes` on the root. That covers 3 base bodies and 3 kit pieces.
- Fixture `tests/fixtures/import/import_probe.glb` (pure-Python generator, byte-reproducible) goes through the real import with the kit rules.
- Shots: all 33 `char_*`, `veg_*`, `haluna_*`, `base_body_*` and `asha_*` captures are **byte-identical** before and after (same worktree, same render wrapper), and all pass compare.py.

## Review log
- 2026-10-23 rendering, fresh reviewer (review-sweep-M): **approve.** No blockers.
  - **Checks run** (fresh `--import` of the worktree at 449f856, own `XDG_DATA_HOME`): Godot `--filter=post_import` 15/0 failed and `--filter=character_shading` 14/0. Tools unittest 431 OK, including tools/tests/test_post_import.py. validate_data 0/0, gdlint and gdformat clean. I ran no shots: the author reports all 33 affected captures byte-identical, and nothing in this diff has changed since.
  - **What I read:** game/core/import/*.gd, game/data/import/*.json, docs/kb/tech/asset_import.md, the fixture generator, and both test files. Handoff character-7.
    - The real-import fixture shows that Godot 4.6 keeps the `-col` name on the proxy, so `find_children("*-col")` (asset_import_rules.gd:87) matches what the importer produces.
    - Materials go on as surface overrides, and the glTF slot is kept.
    - The `shader_test` exclusion and its reason are correct. M1-RND-19 has since removed that reason.
  - **Should-fix:**
    1. game/core/import/asset_import_rules.gd:169-183 gives *every* mesh without the suffix an LOD0 range that ends at `end_m[0]`, whether or not the asset has a `-lod1` sibling. A kit piece without a chain would vanish at 70 m with nothing behind it, and a plant at 45 m. HalunaDresser does the same today, and every committed kit glb has a `-lod1`, so nothing breaks now. But the import makes this the default for any path that instances a piece raw. Apply ranges only when the asset has at least one `<name><suffix>N` mesh. Otherwise leave visibility unset.
    2. docs/kb/tech/asset_import.md:16 says "Authored `<name><suffix>N` meshes get visibility ranges". The code applies them to every MeshInstance3D, including unchained LOD0s. Make the doc and the code agree, after fixing item 1.
    3. tests/unit/test_post_import.gd:156-157. The comment still says apply_to_tree mutates shared overrides, which M1-RND-19 fixed. Update it, and decide whether `shader_test` should get import materials now (optional, per asset_import.md:23).
    4. asset_import_rules.gd:117-119. The `convex` branch builds the shape from the proxy mesh in mesh space. The body takes `mi.transform * body.transform`, but the CollisionShape3D child keeps the transform Godot gave it. That is correct only while Godot's shape child is at identity. test_convex_rule_replaces_the_trimesh_and_keeps_the_transform builds that case by hand, so the test cannot catch a non-identity child. Add a one-line assert, or a comment that the child must be at identity.
- 2026-10-23 lead: closing on review-sweep-M approve; the should-fixes are in M2-NIT-03.
