# 0005 — Asset pipeline: Blender headless → glTF → Godot import scripts; LFS deferred

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** Character, Environment, Rendering, Audio, QA
- **Author role:** Lead

## Context
SPEC §2, §4.3, §7.3, and §13.6: every asset must regenerate from source in the repo, with no asset packs, and with provenance tracked.

## Decision
1. **Source** lives in `assets_src/<kind>/<name>/`: Python generators (`build.py`), optional `.blend` files saved *by* those scripts, Material Maker graphs, and synthesis scripts.
2. **Build:** `blender --background --factory-startup --python assets_src/<kind>/<name>/build.py -- --out assets/<kind>/<name>.glb`. Scripts are deterministic (fixed seeds) and parameterized (weathering, moss, LOD count). Shared helpers go in `tools/blender/`.
3. **Export:** glTF 2.0 binary (`.glb`) with tangents, and baked maps as PNG (16-bit for normal and height maps). Naming suffixes: `-col` for collision, `-lod1..3` for LODs, `-noimp` for helper nodes.
4. **Import into Godot:** an `EditorScenePostImport` script per category (`game/core/import/<kind>_post_import.gd`, task M1-ART-02) assigns our `.gdshader` materials, sets up LODs and collision, and applies the `PLACEHOLDER` metadata tag when the asset's source declares itself placeholder (SPEC §8.4).
5. **Audio:** Python DSP under `tools/audio/`, with cues under `assets_src/music/`, rendered to Ogg Vorbis in `assets/audio/`.
6. **Provenance:** each generated file gets a row in `assets/PROVENANCE.md`, and `tools/validate_data.py` fails CI on a missing one. A `tools/build_assets.py` runner (M1) regenerates everything and can rewrite PROVENANCE rows.
7. **Git LFS is deferred.** The bootstrap environment pushes through a git proxy that we did not verify supports LFS uploads, and LFS quota is a human-owned decision. Until a superseding ADR, binaries are committed as plain blobs, and any binary over **5 MB** fails the validator. The LFS patterns are already present, commented out, in `.gitattributes`.

## Consequences
- The pipeline needs Blender in CI to re-verify assets. Until a Blender CI job exists (M1-QA-02), generated outputs are committed, and reproducibility is checked by whoever regenerates them.
- **Open item for the human (STATUS blockers):** enable Git LFS (quota) before the M1 hero character, whose 4K textures will exceed the plain-blob budget.
