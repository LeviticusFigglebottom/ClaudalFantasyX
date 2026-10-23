---
id: M1-RND-19
title: CharacterShaderTiers.apply_to_tree mutates shared materials and surface overrides
role: rendering
status: doing
owner_session: "worktree-agent-aa89bf29c8049ad55"
depends_on: [M1-ART-02]
milestone: M1
request-from: "character"
---
## Goal
From M1-ART-02 (handoff docs/kb/handoffs/2026-10-23-character-7.md): apply_to_tree swaps the shader on every material it reaches, including import-time surface overrides, without duplicating them. One tier swap then leaks into other instances sharing the material, as test_character_shading showed when the shader-test busts got import materials.

## Acceptance criteria
- [ ] apply_to_tree duplicates any material it does not own (or caches per-tier copies) before swapping; shared resources are never mutated
- [ ] A test with two instances sharing a material at different tiers
- [ ] Asha's import-script adoption (docs/kb/tech/asset_import.md) unblocked; note it there

## Review log
