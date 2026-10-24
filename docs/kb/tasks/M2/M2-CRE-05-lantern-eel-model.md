---
id: M2-CRE-05
title: "Lantern eel: final battle model and clips"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M2
request-from: lead
---
## Goal
The lantern eel from its design sheet, through the creature pipeline.

## Acceptance criteria
- [x] See Goal; notes below record what shipped.

## Notes
Shipped 2026-10-24 (worktree branch off `claude/creatures` 5a873a0), through the creature pipeline:

- `assets_src/creatures/lantern_eel/build_lantern_eel.py` + `materials.json` -> `assets/creatures/lantern_eel/lantern_eel.glb`
  (8,458 triangles, budget 9k; 14 bones; 0.62 MB) and six slots: `skin` (spawn_wound gill-slit emission, slow pulse),
  `fin` (rim sheen), `bone` (teeth and cage), `eye`, `photophore` (sea_glow, faint), `lantern` (salt_glass `#BFE6E0`
  via the TEXCOORD_1.y mask, steady, energy 5).
- Form: one oval-section sweep (taller than wide) along a Catmull-Rom spine, buried tail -> a short run on the ground ->
  the S -> a moray head hooked toward the party (+Z); brow at ~2.1 m, the lure's stalk arcs to 2.31 m and the cage
  hangs in front of the snout at ~2.1 m. Swollen cheeks, brow ridge, throat folds, a separate heavy lower jaw hinged
  at the mouth's corner (root buried in the throat), 66 fine raked teeth plus two palate fangs, small forward eyes
  with a pale iris ring, tubular nostrils. Continuous fin-rayed dorsal frill (two-faced, scalloped, one old tear),
  sand_wet belly line, faint sea_glow reticulation, three healed claw-rake scars on the camera flank, 2 x 18
  photophores. Body skinned with `ck.Rig.chain` over root + 9 spine bones + head; jaw, lure_a, lure_b.
- Clips: `idle` 3.0 s loop (figure-of-eight sway travelling up the S, keyed per frame; the lure and cage lag as a
  pendulum; jaw breathing), `attack` 1.1 s (coil, lunge, snap at 0.55 s), `cast` 1.6 s (head draws back, the stalk
  stands straight up, then the cage swings forward toward the target and holds 0.75-1.15 s; release 0.9 s), `hit`
  0.5 s (mid-body kink away, head whips back, cage swings wide), `ko` 1.6 s (the lure droops first, the S slackens
  from the head down, then the body rolls over onto its side and curls into a low loop on the ground).
- Data: creatures.json row (`clip_by_skill` lure_glow -> cast), `model` on the enemies.json row, import rule folder,
  Blender job `creature_lantern_eel`, PROVENANCE rows.
- Gates: verify_blender_builds identical (7 files); validate_data 0 errors; test_creatures / test_post_import /
  test_blender_builds OK; Godot `--filter=creature` 8/0, `post_import` 17/0, `battle` 412/0; taskboard --check OK.
  No .gd files touched (gdlint/gdformat not needed). No screenshot shots added (done centrally).

Honest weaknesses:
- The body skin is plain at battle distance: a wet dark teal tube with highlights. The reticulation and scars show
  only up close, and the belly line reads mainly on the outer curves.
- At the `cast` hold the cage rises about 0.5 m above the brow (to roughly 2.6 m), so CreatureStage's rest-pose
  framing crops it. In battle the camera has room.
- The KO loop lies partly below the ground plane, which the KO fade hides.
- There's a small seam where the lower jaw's root meets the throat when the jaw opens wide (attack 0.45 s).

## Review log
