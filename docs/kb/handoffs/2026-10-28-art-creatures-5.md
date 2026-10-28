# Handoff: art (creatures), 2026-10-28 #5

Worktree agent session on M3-CRE-654 (ADR 0041: Act I at final quality), branched from `claude/creatures`. Nothing
is pushed; the creatures coordinator merges the branch.

## Done
- **The four Act I regulars that read primitive are rebuilt to final quality** (the sheets' "Final quality
  (M3-CRE-654)" sections list every change):
  - **shoal_skipper** (1,644 to 4,952 triangles, budget 5k): a lofted mudskipper head with a jaw-split mouth line,
    goggle eyes in raised sockets with lids, mottled wet skin with salt crust, fan pectorals, a scalloped dorsal
    sail, a second dorsal and a tail fin.
  - **slag_tortoise** (4,624 to 7,786, budget raised 6k to 8k):
    - a skirted crust with drips, clinker, toned plates, copper-weeping seams and a small closed neck crack;
    - scaled, padded and nailed legs;
    - a folded neck with a collar;
    - a beaked, browed tortoise head.
  - **sail_leech** (5,728 to 4,832, now inside its 5k budget): an annulated leech body with open wound seams, oral
    and caudal suckers, eyespots, battened drooping sails with a canvas-pale frilled edge, and a ringed ribbon tail.
  - **oil_slug** (4,192 to 5,782, budget 6k):
    - an arched slug body on a flat sole, with tubercled skin and a flank band;
    - a mantle shield with a pore, and a ruffled foot fringe;
    - eye-tipped upper tentacles and oral lower tentacles;
    - flame cerata, a closed gill rosette, and an oil-film sheen.
- **Kept:**
  - every bone and bone name (creatures.json `vfx_anchors`);
  - the clip names and creatures.json contact times;
  - the spawn_wound weak points (ADR 0151's forms);
  - the palette swatches;
  - grounding: no allow-list entry. The tortoise adds a KO-only root lift and the slug a millimetre root lift through
    `common/grounding.py`.
- **Clip edits:** the skipper's jaw keys flip sign, because a positive turn now opens the head's own lower jaw.
- **Materials:**
  - slag crust: `roughness_dry` 0.55, `wet_darken` 0.9, `clearcoat_wet` 0.8, with gloss on the crowns via the wet
    channel;
  - oil slug body: slicker;
  - oil slug frill: rim sheen 0.3 and glow 2.2.
- **Variants rebuilt and viewed:**
  - the scree crawler (7,786 triangles) shares the tortoise build;
  - the fen leech (5,980) shares the leech build and sets the new `BODY_W`, `BODY_H` and `DROOP` itself, so it stays
    ribbon-flat.
- **`common/` is untouched**, so no other creature's job reruns.
- **Docs:** the four sheets and act2/variants.md are amended; the task is set to `review` (reviewer: art).

## Checks
- **verify_blender_builds:** identical for creature_shoal_skipper, creature_slag_tortoise, creature_scree_crawler,
  creature_sail_leech, creature_fen_leech and creature_oil_slug.
- **Unit tests:** `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds` runs 50 tests, all
  OK (GroundedClipsTest included).
- **Data and board:** validate_data reports 0 errors (one pre-existing warning about Haluna's shrine_offering), and
  `taskboard --check` passes.
- **Lint:** gdlint and gdformat are clean (no GDScript was touched).
- **Godot:** `res://tests/run_tests.tscn -- --filter=creature` runs 78 tests; 1 fails, the known
  test_creature_portraits missing-PNG test.
- **Self-render:** creature_shoal_skipper, creature_slag_tortoise, creature_sail_leech, creature_oil_slug,
  creature_fen_leech and creature_scree_crawler all drift from their baselines, as intended. Every out PNG was viewed;
  no baselines were written and no out or diff PNGs were committed.

## In progress
Nothing.

## Exact next step
1. The coordinator merges this branch into `claude/creatures`.
2. It logs `SELF-RENDERED` / `MERGE-READY` for the six shots in the live log, so the Lead re-approves their
   baselines on the full gate.
3. The art reviewer appends to M3-CRE-654's Review log.

## Known issues
- **The baked creature portraits for these six are stale** once baked, because the models changed. They aren't
  baked yet (test_creature_portraits is still red for missing PNGs).
- **The review shot is far from the sail leech:** it lies flat and its long tail stretches the frame. Its battle read
  is from the hover (1.38 m).
- **The slag crust's plate seams** are as crisp as a 64×24 lathe allows; a finer crust would cost the 8k budget.

## Files touched
- assets_src/creatures/{shoal_skipper,slag_tortoise,sail_leech,oil_slug}/build_*.py
- assets_src/creatures/{slag_tortoise,oil_slug}/materials.json
- assets_src/creatures/fen_leech/build_fen_leech.py
- assets/creatures/{shoal_skipper,slag_tortoise,sail_leech,oil_slug,fen_leech,scree_crawler}/*.glb
- assets/creatures/slag_tortoise/materials/crust.tres
- assets/creatures/oil_slug/materials/{body,frill}.tres
- docs/kb/art/creatures/act1/{shoal_skipper,slag_tortoise,sail_leech,oil_slug}.md
- docs/kb/art/creatures/act2/variants.md
- docs/kb/tasks/M3/M3-CRE-654-act1-regulars-polish.md
- docs/kb/handoffs/2026-10-28-art-creatures-5.md
