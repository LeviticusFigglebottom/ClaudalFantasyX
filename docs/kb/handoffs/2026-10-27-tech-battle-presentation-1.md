# Handoff — tech (battle-presentation) — 2026-10-27 #1

Session `session_015hKkhtpX67kS4yZeA8AAhv`, branch `claude/battle-presentation`. The live log
(`docs/kb/handoffs/live/battle-presentation.md`, "NEW ACCOUNT" section) has the same state with shas.

## Done
- **M3-BPR-404, FAST-TRACK (the Hullgnaw intro framed too close).**
  - The intro camera fits the boss model's bounds and keeps its feet clear of the title card. It aims lower
    first, then widens.
  - All six intros viewed on cloud lavapipe before rendering moved to the PC.
  - The code-only `git am` patch for the post-big9 pick is `docs/kb/tasks/M3/M3-BPR-404-boss-intro-fit.patch`.
    It is verified on -ze8rrn 7cccb551: 17/0.
- **M3-BPR-401 battle feel:**
  - a Screen shake setting (Full / Half / Off); Reduced motion drops every shake;
  - audio hooks `BattleImpact.landed` and `slowmo_planned`, with request M3-BPR-405 to audio;
  - **the hit-stop hold bug** (creatures' M3-CRE-617 report): the struck target's clip is now held through the stop.
- **M3-BPR-402:**
  - a body beside the path turns the melee run instead of stopping it short (`melee_approach`);
  - the real heroes' clips, contact markers and footprints checked headlessly.
- **M3-BPR-403:** the opening line-up spreads sideways on screen by footprint (BattleLineup).
- **M3-BPR-406, Ch8 set pieces on stage (doing):**
  - all four Ch8 fights play to their result panel at full pacing;
  - withdrawn foes back away and are hidden (they used to stay standing);
  - counters show the hero's riposte;
  - the Reach has a boss intro and a new shot, battle_boss_intro_reach;
  - the Breach's camera push-in (camera.pressure).
- Merged the integration branch with big9 (the real heroes). Battle filter: 714+ run, 0 failed.

## In progress
- Three render requests, waiting on the PC (live log "### Render requests"): 404's six intros, every other battle
  shot for 401/402/403, and 406's Reach intro plus four choreo shots.
- **Red until the PC render is approved:** `tools/tests/test_screenshots.py` `test_repo_manifest_is_valid_and_baselined`.
  battle_boss_intro_reach has no baseline yet.

## Exact next step
1. When the Lead relays `RENDERED @ <sha>: gpu/render-battle-presentation-<sha7>`:
   - `git fetch` that branch and VIEW every out and diff PNG;
   - approve by copying the out PNGs into `tests/screenshots/baselines/`, with the baselines.json metadata in
     TRACK-RULES;
   - commit `<task>: re-approve <ids> after viewing (PC render …)`.
2. Then post MERGE-READY for 403 and 406 with the moved shots.
3. 406 still open:
   - the intercept step-in, which needs a stair marker on the Ch8 arena (ask act1-chapters or env-art for an
     `entry_marker`);
   - a look for untargetable or damage-immune phases (ask creatures for a draw-back clip on the Reach);
   - freeze-frame shots for an intercept, a counter and a withdrawal.

## Known issues
- `battle_choreo.gd` is at about 990 of the 1000-line gdlint cap. Put new logic in BattleChoreoPlan, BattleImpact,
  BattleLineup or the camera director.
- The 404 commits 269054a3 and 4e89c967 no longer cherry-pick cleanly onto -ze8rrn (the baseline PNGs conflict with
  big9's). Use the patch.
- No cloud renders (the human's directive). Headless Godot tests are fine.

## Files touched
game/battle/scene/{battle_boss_intro,battle_impact,battle_clips,battle_stage,battle_lineup,battle_choreo,
battle_choreo_plan,battle_camera_director}.gd, game/data/battle/choreo.json, game/data/ui/accessibility.json,
game/data/loc/strings.csv, game/battle/scene/shots/battle_boss_intro_reach.tscn, tests/screenshots/shots.json,
tests/unit/test_battle_{boss_intro,impact,lineup,choreo,ko_once,set_piece_stage}.gd, docs/kb/tech/battle_presentation.md,
docs/kb/tasks/M3/M3-BPR-40{1,2,3,4,5,6}*.md, docs/kb/handoffs/live/battle-presentation.md.
