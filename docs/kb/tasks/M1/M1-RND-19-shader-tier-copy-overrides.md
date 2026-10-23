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
- 2026-10-23 character, fresh reviewer (review-sweep-M): **approve.** No blockers. All three criteria are met.
  - **Checks run** (worktree at 449f856, own `XDG_DATA_HOME`): Godot `--filter=character_shading` 14/0 failed and `--filter=post_import` 15/0. gdlint and gdformat clean. I ran no shots: the author reports char_* ×4 and asha_* ×10 byte-identical, and the code is unchanged since.
  - **What I read:** commit 2860034, the callers in character_shading_stage.gd:33/:110 and asha_stage.gd:59/:74, and handoff rendering-3.
    - The copy-on-swap logic is right:
      - the `[root id, copy id]` ownership meta means a duplicate of an owned copy is not owned (character_shader_tiers.gd:137);
      - one copy per source per root (`done`, :143-155);
      - materials already at the tier are not copied.
    - AshaStage's `verse_count` and compare-skin duplicates are made after the swap, so they stay per-instance and are re-copied on the next swap. That is correct.
  - **Should-fix (minor):**
    1. character_shader_tiers.gd:104-132 still reaches only `material_override` and surface materials. `material_overlay` and `ShaderMaterial.next_pass` are neither swapped nor copied. That isn't a regression, but say so in the docstring, so nobody adds a tiered next_pass (a hair shell, an outline) and expects it to follow.
    2. A swap back to a material's source tier keeps the owned copy in the override slot rather than restoring the shared source. It is harmless (same shader and parameters), but the per-instance copies are never released while the instance lives. Note it in character_shading.md for when crowds use tiers.
    3. tests/unit/test_post_import.gd:156-157 (Character's file) still describes the old behaviour. Character fixes it under M1-ART-02's review (review-sweep-M S3 there).
