---
id: M2-FP-09
title: First-playable thread hardening (review-sweep-K)
role: architect
status: done
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-04]
milestone: M2
request-from: "qa"
---
## Acceptance criteria
- [x] A defeat-path integration test (loss, then Return, Fight again, Continue)
- [x] test_fp_thread drives the story's real battle trigger, not a direct start; it adds a save then load leg
- [x] No latch is marked done before its scene change is confirmed (field_battle.gd ~:64, end_card.gd ~:84, haluna_story.gd ~:90); the router reports busy, the caller retries or waits; test it
- [x] ch02_met_asha comes from the zone JSON, not hard-coded (haluna_zone.gd ~:31); a test proves the battle strip can't be walked around
- [x] The close-up lighting rule (QA-05/CHR-04 shadow normal bias) is applied in the playable zones' suns (haluna_mood.tscn ~:83 via the zone or an override, first_verse.tscn ~:169)
- [x] The sequencer host resumes, or is cancelled, if the sequencer leaves the tree; unsupported cue args warn

## Review log

## Notes
- Renumbered from M2-FP-05 by the first-playable session: that id was already taken by M2-FP-05-playable-polish (skip, Haluna prebuild, defeat retry).
- 2026-10-24 review-sweep-O (qa): **approve with fixes.** I reviewed it on `origin/claude/first-playable` (7015a03, not yet merged here). Criteria 1-4 and 6 hold. Criterion 5 is done as written, but a later measurement contradicts it.
  - **What I read:** `git show 7015a03`, covering:
    - the new game/flow/flow_routing.gd and its callers (battle_request, end_card, field_battle, haluna_story, first_verse_scene);
    - haluna_zone.gd (the intro flag from first_playable.json's `intro_flag`, and `face_key_shadow_normal_bias`);
    - haluna.tscn and first_verse.tscn;
    - cutscene_sequencer.gd (`_await_on` and `resumed`, so leaving the tree releases `play()`, and `UNSUPPORTED_KWARGS` warns once);
    - test_fp_thread.gd (the end-to-end thread through the real trigger, the defeat, save and load legs, and the strip test), test_flow_routing.gd and test_cutscene_sequencer.gd.
  - **Not run:** Godot on that branch. Checking it out here would mean a second worktree and a full import. The session reported its gate green at 67984ce (1,244 tests). The Lead's merge gate runs it.
  - **Fix 1, the zone-sun bias:** criterion 5 set both playable suns to `shadow_normal_bias` 3.0 (Haluna through `face_key_shadow_normal_bias = 3.0`, first_verse.tscn:174). M1-RND-20's later GPU follow-up found that at Haluna's cascade, 2.5-4.5 only erases the nose shadow, that 1.0 already leaves the smile corner clean, and that the zone sun stays at 1.0 (character_shading.md "Shadows on characters"). Undo it at merge, and leave close-ups to M2-FP-10's dialogue key light.
  - **Fix 2, `FlowRouting.when_free` and two waiters:** if two hand-offs wait on one busy router, both resume on the same idle frame, and SceneRouter drops the second. So the change is "never lost" only for one waiter. Queue the changes, or prove that two can't wait at once, and test it.
  - **Filed:** both fixes as **M2-FP-11**, to land in the same batch as the claude/first-playable merge.
