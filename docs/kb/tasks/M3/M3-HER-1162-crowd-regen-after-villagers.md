---
id: M3-HER-1162
title: "Request: regenerate the crowd on the merged tree (big17); characters' new villagers make two test_npc checks red"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
`tools/tests/test_npc.py` is green on claude/creatures alone and **red on big16 and big17** (`lead/gate-big17`):
- `test_the_generator_output_is_committed`: `assets_src/crowd/gen_crowd.py` writes different params on the merged
  tree (for example a face value 0.5549 vs the committed 0.5065, and canthus_offset_m 0.00035 vs 0.00069);
- `test_bodies_span_ages_builds_and_hair_and_are_new_faces`: "crowd_girl_teen is too near wright_child_a"
  (0.229 < 0.28).

The cause: the crowd generator keeps crowd faces distinct from the named villagers. Characters' Act I villagers
(M3-CHR-510/512, e.g. `wright_child_a`) arrived through the same batch, so the crowd committed on claude/creatures
was generated against the old villager set. Neither track can see it alone; only the merged tree can.

## Acceptance criteria
- [ ] Once big17 is on the integration branch, merge it, rerun `gen_crowd.generate()` (and the crowd's Blender jobs
      if params change), commit, and get `python3 -m unittest tools.tests.test_npc` green on the merged tree.

## Notes
- Filed by integration-qa, 2026-10-29, from big17's gate (the tool suite's 4 reds, red on big16 too).
- **The other red the Lead routed to creatures, test_post_import, is already fixed** on claude/hero-integration
  @ 96bd14658: `"crowd"` is in `tools/tests/test_post_import.py`'s `KINDS` (the Godot twin was fixed in big16). No
  need to fix it again. If you already did, the merge keeps either line.

## Review log
