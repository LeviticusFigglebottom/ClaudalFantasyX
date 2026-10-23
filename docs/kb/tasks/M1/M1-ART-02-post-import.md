---
id: M1-ART-02
title: Godot post-import scripts per asset category
role: character
status: review
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
