# 0002 — Renderer: Forward+ (desktop only)

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** Rendering, Environment, Character, UI, QA
- **Author role:** Lead

## Context
SPEC §4.1 and §8: fidelity is a first-class priority. We need SDFGI, VoxelGI/LightmapGI, volumetric fog, SSR, SSAO/SSIL, and TAA/FSR. Mobile and web are out of scope.

## Options
1. Forward+: full feature set, desktop GPUs.
2. Mobile or Compatibility: missing SDFGI and volumetrics, so it cannot meet §8.

## Decision
Use **Forward+** (`rendering/renderer/rendering_method="forward_plus"`). The targets are Windows and Linux, with macOS (Vulkan via MoltenVK) best effort.

## Consequences
- Headless CI uses the dummy renderer, so **visual output can't be tested on standard runners**. Screenshot regression needs a GPU runner, or a self-hosted runner with Vulkan or lavapipe (task M1-QA-01).
- Each zone records its GI choice (SDFGI vs. VoxelGI vs. LightmapGI) in its README, per SPEC §8.1.
- A quality-preset settings menu is mandatory (SPEC §4.2) and is owned by UI with Rendering.
