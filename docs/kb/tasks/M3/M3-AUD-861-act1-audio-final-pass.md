---
id: M3-AUD-861
title: "Act I as played, every sound final (ADR 0041): audit title→Ch9 for silent, temp or reused sounds and fix them"
role: audio
status: done
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: integration-qa
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (the human's directive) and the Lead's refocus at 01:12 on 10-28 set the target:
- Every Act I zone has its ambience bed.
- Every enemy has its voice, hit and death sounds.
- Every ability and UI action has its sound.
- Every cutscene has its score and foley.
- There are no temp or reused-placeholder sounds.

## The audit
`python3 tools/audio/act1_audio_audit.py --md` reads the data the runtime reads. It covers:
- zones;
- enemies;
- skills (BattleVfx's map, then BattleAudio);
- cutscenes, in the sequencer's own order (the file first, then the stand-in);
- pending UI hooks;
- notes that say temp.

It reported 46 items at the start. The worked list, with the cause and plan for each, is in
docs/kb/handoffs/live/audio.md.

## Acceptance criteria
- [x] The audit dropped from 46 items to 5, and all 5 are other tracks' blockers (by-design cases are listed with
      their reasons in the tool's `BY_DESIGN`):
      - **Three cutscenes play only one stem:** undertow_rising, seawall_hold and undertow_reach. This waits on
        **M3-AUD-834**, the cutscene owner's change so `@music` goes through the MusicDeck.
      - **ShrineTravelMenu and ReefballOutfitterMenu stay `pending`** until claude/ui merges.
- [x] Done in this task:
      - Zones: music rows ×4 and bed rows ×5 were wired, and three new beds made (oruvel_raft, brightwater_deck,
        coilspire_flues).
      - The coilspire_flues stand-in is fixed, and corrow_day is an alias.
      - The Inquisitor and four borrowing enemies have their own voices; wickfry owns glassfry's set.
      - 16 skills have sounds.
      - Four UI hooks were added: CodexMenu, SettingsMenu, ReadPanel and ObjectiveHud.
      - The prologue's score (M3-AUD-862) and Ysolde's theme final (M3-AUD-863) landed.
- [x] New Act I audio is in Git LFS under `assets/lfs/audio/` (ADR 0173), and no existing file was moved. Ysolde's
      final replaces her sketch at the same path, because the sequencer needs that path. It fits the plain-git
      budget.
- [x] Every new file has its PROVENANCE row and loudness rule and renders deterministically.
      - Python tests: test_audio_loudness, test_audio_data and test_act1_audio_audit pass.
      - Godot `--filter=audio`: 173 run, 0 failed.

## Review log
- 2026-10-29 integration-qa (reviewer): **accepted, done.** On `lead/gate-big17` (audio's head included) the audit
  shows Zones, Enemies, Battles, Intros, Skills, Cutscenes, UI and temp notes at 0. The 5 blockers named above are
  cleared: the three one-stem cutscenes and the two pending ui hooks. The BY_DESIGN reasons read right.
  test_act1_audio_audit and test_audio_data pass. **3 new items** came later, from battle-presentation's
  M3-BPR-1325 (the Climb's stair skills got effect rows mapped to `status_apply`, which layers under their own
  sounds). They're outside this task's pass, so they're filed as **M3-HER-1163 (audio)** with the 3-row fix.
