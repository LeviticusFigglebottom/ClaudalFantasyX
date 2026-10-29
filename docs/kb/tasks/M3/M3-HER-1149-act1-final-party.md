---
id: M3-HER-1149
title: "ADR 0041 (Act I at final quality): the party's capsules in the field, on cutscene stages and in battle (integration-qa's share)"
role: qa
status: doing
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
reviewer: lead
depends_on: []
milestone: M3
request-from: lead
---
## Goal
The Lead's split of the inventory's people rows (2026-10-28): wherever a party member stands as a capsule (kerrid,
kerrid_stair, liss, pell, ysolde_edge, and Ch9's vigil_* in the ch09_pell_joined variant), the hero layer swaps in the
real hero. Kerrid and Liss also need battle actors.

## Acceptance criteria
- [x] A stage actor that plays a hero under another name takes the hero's body: hero_motion.json `actor_aliases`
      (ysolde_edge, kerrid_stair) and `actor_prefixes` (vigil_), read by HeroFieldActor.hero_of
      (test_hero_field_actor::test_aliased_stage_actors_get_their_heroes_bodies).
- [x] Liss's battle row (battle_sandbox.json -> liss_battle_actor.tscn, M3-HER-1120).
- [x] Liss everywhere: liss_lod1.glb is on the integration branch. Her field row measures within tolerance
      (test_the_clip_speeds_match_the_measured_foot_plant, 2026-10-29) and liss_battle_actor.tscn wraps her.
- [x] Kerrid's field row (walk 0.71, run 1.80 m/s, measured on kerrid_lod1 with his own measure config) and battle
      wrapper (characters' game/characters/heroes/kerrid_battle.tscn by path), plus his battle_sandbox row. He's real
      everywhere once claude/characters merges. Checked on a scratch merge: hero_ green, the dawn road shows him at
      the milestone.
- [x] Pell's field row (walk 1.27, run 3.13 m/s, measured by HeroClipGait on characters' pell_lod1 in the big17
      trial tree; 2026-10-29). Ch9's `pell` and `vigil_pell` (the `vigil_` prefix) take his body once
      claude/characters merges. No battle wrapper: Ch9 says he has no battle row in Act I (M3-C09-07 is his kit).
- [ ] The audit lists no integration-qa rows. On the big17 trial tree plus Pell's row it lists 0 (5 items, none
      ours; 2026-10-29). Left to do once big17 is on integration: drop Pell's stale KNOWN rows from
      tests/integration/qa_known.json (corrow, corrow_night ×2, ossa_fen) and re-run the audit there.

## Notes
- Ch9's vigils are staged as kneeling figures (1.2 m capsules). With a body they stand at idle unless the scene plays
  a kneel. The kneel clip is in M3-CHR-1000's list (`kneel_palms_flat`, shared), and act1-chapters' vigil staging
  should call it.

## Review log
