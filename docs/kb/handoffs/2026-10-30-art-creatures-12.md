# Handoff: art (creatures), 2026-10-30, #12

Branch `claude/creatures`. The live log is docs/kb/handoffs/live/creatures.md; its last MERGE-READY is @ cd21ece0
(the sheets commit after it is docs only).

## Done (ADR 0205: Act II per track, after row 44 and M4-CRE-670)
- **The Act II regulars, from their plan sheets** (docs/kb/plan/act2/creatures/):
  - gallery ray: dusky back, margin glow, hover 0.95 m;
  - rime urchin: the KO splays its spines into a flat star;
  - conduit crawler: knuckled, collared, sleeved legs;
  - cord moth: battle scale 1.35×, dusky wing margins, hover 1.12 m;
  - rim crawler: slate flanks and seams, brighter wounds;
  - ridge lynx: shaped legs and knuckled toes;
  - fen leech: hangs at 0.85 m with draped edges.
- **enemies.json `model` keys** for the ten built Act II foes. Without them the battle drew capsules.
- **Arena checks** in the four built Act II arenas (temporary previews, viewed).
- **Palette fixes:** snow is now `gauze_white`; the sail leech's canvas is a swatch mix.
- **M4-A2P-056, the Act II wildlife, in review** (reviewer: environment). All four are placed on the greybox:
  - fen fireflies: a firefly mesh and slot, the shader's glow mode 6, WildlifeSwarm's `firefly` type;
  - fen kingfishers: the gull recipe with its own kind, rows and MultiMeshes;
  - woolback herds: the ram's build without seep or ice, drawn at 0.3; the new skinned WildlifeHerd; graze, look and walk clips with the walk's hooves solved per frame;
  - rim rays: a ray kind of the fish shoal drawn with the flap mode.
- **M4-A2P-058, the regulars' part:** the skill-effect spec in docs/kb/art/creatures/act2/skill_vfx.md, for
  M4-A2P-060 to generate.

## In progress
Nothing.

## Exact next step
- Wait on the Lead's answers in the live log:
  - the slag tortoise and scree crawler budget (17.5k against the sheet's 8k);
  - carrying M4-A2P-056's claim and its `review` status to the integration branch;
  - the baselines for the new wildlife shots and creature_gallery_ray.
- When env-art's dressed kits replace the greybox in Ossa Fen, Keth Pass and the Pale Rim, re-seat the wildlife (tools/creatures/wildlife_snap.gd, wildlife_audit.gd) and move the woolbacks to the Keth troughs.

## Known issues
- Birds can pass through greybox trunks (wildlife has no collision).
- The rim rays are under the greybox's opaque Shallows plane in the real zone. Only the review stage hides it.
- The conduit crawler has no enemy row: it waits on M4-A2P-022.

## Files touched
assets_src/creatures/{gallery_ray,rime_urchin,conduit_crawler,cord_moth,rim_crawler,ridge_lynx,fen_leech,
scree_crawler,sail_leech,woolback}/; assets_src/wildlife/{insect,kingfisher,rim_ray}/; assets/creatures/...,
assets/wildlife/..., assets/ui/portraits/creatures/...; game/world/wildlife/ (layer, swarm, shoal, buffer, herd,
shader); game/creatures/{cord_moth,woolback}/; game/data/world/wildlife/ (wildlife.json, ch10_ossa_fen,
ch12_keth_pass, ch16_pale_rim); game/data/creatures/creatures.json; game/data/battle/enemies.json (`model` only);
game/data/import/{creatures,wildlife}.json; game/levels/_tests/wildlife/; tests/unit/{test_creature_actor,
test_wildlife}.gd; tools/validate_wildlife.py; tools/tests/test_wildlife.py; tools/dev/blender_builds.json;
tests/screenshots/shots.json; assets/PROVENANCE.md; docs (plan sheets, art sheets, wildlife.md, skill_vfx.md, tasks).
