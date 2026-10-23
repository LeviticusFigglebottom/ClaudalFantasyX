---
id: M1-RND-19
title: CharacterShaderTiers.apply_to_tree mutates shared materials and surface overrides
role: rendering
status: review
reviewer: character
owner_session: "worktree-agent-aa89bf29c8049ad55"
depends_on: [M1-ART-02]
milestone: M1
request-from: "character"
---
## Goal
From M1-ART-02 (handoff docs/kb/handoffs/2026-10-23-character-7.md): apply_to_tree swaps the shader on every material it reaches, including import-time surface overrides, without duplicating them. One tier swap then leaks into other instances sharing the material, as test_character_shading showed when the shader-test busts got import materials.

## Acceptance criteria
- [x] apply_to_tree duplicates any material it does not own (or caches per-tier copies) before swapping; shared resources are never mutated
- [x] A test with two instances sharing a material at different tiers
- [x] Asha's import-script adoption (docs/kb/tech/asset_import.md) unblocked; note it there

## Notes
- `game/shaders/character/character_shader_tiers.gd`: copy-on-swap. A material that needs a new shader is duplicated, unless the `hymn_tier_owner` meta marks it as a copy made for this same root (the meta holds the root's id and the copy's own instance id, so a duplicate of an owned copy is not owned). The copy goes into the slot, and a mesh surface material lands in the surface override. Slots that shared a source share one copy. A repeat call on the same root swaps its copies in place. Materials already at the tier are left alone (no copy). `apply_tier` is unchanged and still works in place. New helpers: `target_shader_path` and `owns`.
- Tests: `test_apply_to_tree_copies_shared_materials_per_instance` (new; two instances share an override and a mesh surface material, at low and at medium); `test_apply_to_tree_visits_each_material_once` updated (sources are now kept, and one copy is shared).
- Shots: char_* ×4 and asha_* ×10 are byte-identical before and after in this worktree. All 14 PASS against the baselines.
- Not changed: `CharacterShadingStage._build_compare` and `AshaStage._build_compare` still duplicate before swapping. That is harmless now, though redundant for the tier swap. `tests/unit/test_post_import.gd:156`'s comment describes the old behaviour (Character's file, left alone).

## Review log
