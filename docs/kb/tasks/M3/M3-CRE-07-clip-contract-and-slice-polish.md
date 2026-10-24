---
id: M3-CRE-07
title: "Creature clips to the battle clip contract; slice creature polish (LOD1, shading, portraits)"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: combat
depends_on: [M2-CRE-03]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue items 2 and 3 (2026-10-24). Every creature's clips meet battle-presentation's clip contract
(M2-BPR-02, docs/kb/tech/battle_presentation.md on claude/battle-presentation): idle, attack with a contact frame,
hit, KO and a special (`cast`), with strikes in place. Then a polish pass on the five slice creatures: LOD1, shading
and the bestiary portrait renders.

## Acceptance criteria
- [x] Audit: all 27 creature GLBs have `idle`, `attack`, `cast`, `hit` and `ko`; every row has `contact` times
- [x] Strike clips in place: the kit drops the root's horizontal travel in `attack` and `cast` (17 GLBs changed, 10 byte-identical); re-audited at 0.00 m
- [x] LOD1: Godot's import LODs verified on every slice mesh (about 50% per level); `tools/dev/creature_lods.gd`; pipeline.md §4
- [x] Portraits: per-creature framing for the gull harrier (and stormgull) and the lantern eel, chosen from a yaw and pitch grid
- [x] Shots: 42 creature and battle shots re-compared; 37 unchanged. 5 re-approved after side-by-side viewing: battle_opening_banner 0.02548, battle_vowbound_call 0.01484 and battle_vowbound_out 0.01482 (the crab and gull mid-strike, now in place), creature_reef_crab_attack 0.07724 (the same strike pose without the lunge), creature_portraits 0.01443 (the gull and eel framing)

## Notes
- 2026-10-24: phase strikes. A phase's `clips` map plays stand-in clips (CreatureActor.phase_clip, followed by play_clip and contact_time, so BattleClips' contract calls get them too). The Undertow's Reach strikes from its Dark and Breach poses (5 new clips). Validator and tests updated, the job verified, the Reach shot unchanged.
- Optional contract clips (`dodge`, `defend`, `ready`, `victory`) are left to the sequencer's procedural fallback.
- Until battle-presentation's sequencer merges, BattleActorMotion plays the strike in place with no travel.

## Review log
