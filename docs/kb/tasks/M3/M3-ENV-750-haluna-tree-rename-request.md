---
id: M3-ENV-750
title: "Haluna: move the two trees to their real piece names (banyan_hero, windbreak_tree) (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
The Act I inventory (M3-HER-1140) flags Haluna's banyan and its 98 windbreak trees as "visible mesh named as a
placeholder" (medium), and their glbs as placeholder-named files (low). They have been real trees since M2-ENV-07; only
the names are left. env-art has built the same trees under real names: `banyan_hero` and `windbreak_tree` (Haluna
kit, byte-for-byte the same geometry; M3-ENV-746). The zone names the old ones in three places, so the switch is one
commit on the zone owner's side.

## Acceptance criteria
- [ ] `game/levels/ch02/haluna/haluna_layout.json`: every `banyan_placeholder` piece becomes `banyan_hero`, and every
      `windbreak_placeholder` becomes `windbreak_tree`.
- [ ] `game/levels/ch02/haluna/haluna.tscn`: the two `piece_rules` keys (lines ~424 and ~442) renamed the same way.
- [ ] `tests/integration/test_haluna_zone.gd` (line ~64) and `tests/unit/test_post_import.gd` (line ~178): the names.
- [ ] Then tell env-art. env-art removes `banyan_placeholder` / `windbreak_placeholder` from the kit (trees.py, the
      glbs, the manifest, PROVENANCE, `haluna_kit_sheet.gd`) and re-runs `tools/placeholder_audit.py`.

## Review log
- 2026-10-28 slice-polish: done. `haluna_layout.json` (50 pieces), `haluna.tscn`'s two piece_rules, test_haluna_zone and test_post_import all use `banyan_hero` and `windbreak_tree`. Env-art: remove the placeholder-named trees from the kit (trees.py, glbs, manifest, PROVENANCE, haluna_kit_sheet.gd, test_haluna_kit). Checks: haluna 65, post_import 21, all 0 failed.
