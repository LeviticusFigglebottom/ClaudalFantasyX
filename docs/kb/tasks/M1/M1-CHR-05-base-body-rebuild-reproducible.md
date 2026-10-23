---
id: M1-CHR-05
title: Base body .glb files do not reproduce from source
role: character
status: done
owner_session: "worktree-agent-a361fe4924e35dfcf"
depends_on: [M1-QA-02]
milestone: M1
request-from: "qa"
---
## Goal
The Blender rebuild gate (M1-QA-02, `docs/kb/qa/blender_builds.md`) rebuilds `assets/characters/base_body/base_body_{slender,athletic,heavy}.glb` from `assets_src/characters/base_body/` with the pinned Blender 5.0.1. The rebuilds **don't match** the committed files: POSITION min/max differ by up to ~3 mm (slender max z 0.1831 rebuilt vs 0.1864 committed), and NORMAL, TANGENT and the indices differ too. The rebuild is stable from run to run, apart from a 1e-4 tangent wobble the gate tolerates, so the committed files were most likely exported from an intermediate state of a773ea1's sources.

## Acceptance criteria
- [x] Rebuild the three variants with `assets_src/characters/base_body/build_all.sh`, look at them, and re-approve the `base_body_*` screenshot baselines (11 shots) if they move.
- [x] `python3 tools/dev/verify_blender_builds.py --job base_body` passes, then remove the job's `expected_failure` from `tools/dev/blender_builds.json` (the gate fails until you do).
- [ ] Optional: drop `export_tangents=True` from `build.py` (Godot generates MikkTSpace tangents on import, `character_shading.md`), and then remove the TANGENT tolerance too. **Not done**: the build is byte-stable at `--threads 1` (M1-CHR-06), so tangents stay; the TANGENT tolerance was already removed in M1-QA-06.

## Notes
- Reproduce: `python3 tools/dev/verify_blender_builds.py --job base_body --keep /tmp/bb`, then compare `/tmp/bb/assets/...` with the committed files.
- 2026-10-23 (worktree-agent-a361fe4924e35dfcf):
  - **Cause:** the committed files never matched their own commit's sources. A rebuild from a773ea1's `assets_src/characters/base_body` + `third_party/mpfb2` (git archive, `--threads 1`) gives slender `5da684…`, the same bytes as today's rebuild. The later edits to `bb_donor.py`/`bb_params.py` (M1-CHR-04 `lip_rest`, `lip_close`) are no-ops at the base-body defaults. So a773ea1 exported from an intermediate state of its sources, as suspected.
  - **Fix:** rebuilt with `build_all.sh` (now `--threads 1`, M1-CHR-06) into the tree. The hashes equal the gate's pinned rebuilds (athletic `4523ba…`, heavy `58142e…`, slender `5da684…`), so the in-tree build and the sandbox build agree. The `expected_failure` marker is removed and the job reports `3 identical`. No source change, so `bb_donor.py` (shared with Asha) is untouched, and the `asha` job still rebuilds identically (`--all`).
  - **What moved** (old commit vs rebuild, measured on the .glb): topology, UVs, JOINTS_0 and WEIGHTS_0 are the same. Positions moved on ~10k of 14.5k body vertices by more than 1 mm, ≤ 8.6 / 10.1 / 10.8 mm (slender / athletic / heavy). The changes are concentrated at the feet (y < 0.1 m) and the pelvis/hips (0.8–1.0 m), with a lighter shift through the torso and arms. Quad diagonals changed on 52 / 4 / 6 triangle pairs (slender soles; athletic and heavy at the head). Slender has 60 vertices whose normals flip on the sole underside, which is clamped to the floor (z ≥ 0) and never visible.
  - **Shots:** all 11 `base_body_*` failed at rmse 0.0099–0.0170 (limit 0.008). I inspected baseline/new/diff for slender front, face and posed, athletic side and heavy q34, plus a 2× crop of slender's feet in front, side and q34. The silhouettes move a pixel or two (hips, thighs, feet outline), the toes are slightly reshaped, and the lip line differs slightly at the face shot. There are no artifacts, holes, shading seams or flipped faces in view. **Re-approved all 11** as the true output of the committed source. The `asha_*`, `char_*` and `veg_*` shots don't load base_body .glb files.
  - Review: rendering (SPEC §12.3, Rendering ↔ Character).

## Review log
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve.** No blockers.
  - **Checks:** `python3 tools/dev/verify_blender_builds.py --job base_body`: **`3 identical`, rc 0**, 32 s, pinned Blender 5.0.1 at `--threads 1`. The `expected_failure` marker is gone from blender_builds.json. Tool tests 411 OK.
  - **The 11 re-approved baselines, viewed one by one:** I rebuilt old/new/diff sheets for each from `git show 10c060d^` against 10c060d. The RMSE against the old baseline is 0.012 to 0.019, which matches the notes. I looked closely at slender front, face and posed, heavy side and q34, and a 3x crop of slender's feet in front and q34. What moved is the silhouette (by 1–2 px at the hips, thighs and arms), the feet, and the lip line in `slender_face`. The new toes are better separated than the old blobby ones. There are no holes, flipped faces, shading seams or new artefacts. The ankle-to-heel notch in the front view is in both, so it is not a regression. **The re-approval is justified:** the new images are the true output of the committed source.
  - **Not re-run:** the 11 shots on my lavapipe. The baselines are the author's renders of the bytes I just verified, and the Lead's full gate covers the comparison.
  - **Nit:** the third criterion (dropping exported tangents) is unticked and explained. Since the build is byte-stable at `--threads 1`, I'd keep it that way. Close it as won't-do rather than leave an unticked box.
- 2026-10-23 lead: closing on review-sweep-L approve; the should-fixes are in M1-NIT-02.
