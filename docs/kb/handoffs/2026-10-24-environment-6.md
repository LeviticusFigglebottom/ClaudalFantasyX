# Handoff — environment (env-art) — 2026-10-24 #6

Session `session_01QmWUfYxd8DMg7XM3MyR6ps`, branch `claude/env-art`. Live state: `docs/kb/handoffs/live/env-art.md`.
(#5 is the M2-ENV-07 worktree's handoff, renumbered from #3, which collided with m2-slice's #3.)

## Done
- **M2-ART-01/02/03** (done): Art Director sign-offs, approve-with-fixes; fixes filed as M2-UI-08, M2-RND-09,
  M2-RND-10; palette.json 0.2.1; art/ui.md §10.
- **M2-ENV-06** (passes 1–4, still `doing` for one item): vuggy coral stone and flat-faced tide-wall blocks,
  sand breakup and wrack line (`env_ground` `breakup` group), drowned-ruin biofilm, weathered infill and
  thatch (measured onto the `thatch` swatch), framed stilt-house/storehouse/house walls, `kit_carved_wood`
  lintel-gulls, the dock previewed from `ending_dock`.
- **M2-ENV-08** (review): the causeway-head kit and village props (18 pieces, 6 materials), the preview
  `game/levels/_tests/haluna_mood/route_preview.tscn`, and the swap-in layout `route_layout.json`.
- **M1-ENV-10** (review, merged from a worktree): `LodChain`; Character + Tools sign-off on
  `asset_import_rules.gd` pending.
- **M2-ENV-07** (review, merged from a worktree): the real hero banyan and windbreak under the old piece
  names; the crown follow-up done here; `test_post_import` updated; the H07 sky palette sample moved.
- **M2-ENV-03**: the Lead's kit comparison: m2-slice's kit adopted (Review log); env-art's kit stopped, its
  geometry kept as source-only salvage in `assets_src/environments/kits/shell_shrine_salvage/`; fixes filed
  as **M2-ENV-09**.
- Baselines re-approved after viewing: all five haluna shots (some twice); palette checks 19/19.

## In progress
- Nothing running. No worktree agents live.

## Exact next step
1. Read the Lead's answer in env-art.md "For the Lead": may env-art merge `claude/m2-slice` for M2-ENV-09,
   or wait for the integration branch? Then build M2-ENV-09 on `shrine_interior.py` (salvage per the README).
2. Merge the integration branch; when it carries m2-slice's ENV-02, re-capture `haluna_h10_dock_night`
   against this branch's kit, view, re-approve if it drifts, and close M2-ENV-06.

## Known issues
- After merging this branch, delete `.godot/imported/*.glb-*` and re-import, or `--filter=import` fails on
  stale LOD ranges (Godot doesn't reimport when only a post-import script changes).
- send_message to the Lead is refused (elevated_session_untrusted_device); report through env-art.md.
- m2-slice must apply the M1-ENV-10 dresser change and the ENV-08 layout entries to its moved Haluna
  files (swap-in notes in env-art.md).
- `kit_canopy_*` materials and the `canopy_cluster` texture are unused since M2-ENV-07.

## Files touched
`assets_src/environments/kits/haluna/{kit_textures,materials,walls,village,build,causeway,props}.py`,
`assets_src/environments/vegetation/banyan.py`, `assets/environments/kits/haluna/**`,
`game/shaders/environment/env_ground.gdshader`, `game/levels/_tests/haluna_mood/route_*`,
`assets_src/environments/kits/shell_shrine_salvage/`, `tests/unit/test_post_import.gd`,
`tools/tests/test_haluna_kit.py`, `tests/screenshots/{baselines/haluna_*,palette_checks.json}`,
`assets/PROVENANCE.md`, `docs/kb/{art,tasks,handoffs}/**`.
