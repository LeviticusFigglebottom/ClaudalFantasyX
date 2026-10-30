# Gate big24 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 8fe3644b (Merge lead/gate-big23).

## Pinned heads (merged --no-ff, in order)
- claude/hero-integration @ 7e0f4480 (PLAYTEST: row 38, the Encounter fallback moves into place_at)
- claude/env-art @ 51ac308c
- claude/m2-slice @ 1a805464
- claude/env-art-b @ 88607c44
- claude/creatures @ fbcf9ee2
- claude/creatures-b @ 2415d4f0
- claude/battle-presentation @ aa227a57
- claude/ui @ 32179772
- claude/audio @ 577a2b20
- claude/act2-plan @ cfc5658d
- No new commits: characters, act1-chapters, slice-polish.

## Resolutions
- hero-integration, `greybox_zone.gd`: theirs moves the before-any-fight fallback into `place_at` (the layout's first spawn).
  `build()` keeps act1-chapters' M3-HER-1159 rule, so a layout that names its own `Encounter` spawn keeps it, and
  otherwise it adds the origin marker for `place_at` to override. Both changes are kept.
- hero-integration, `test_qa_field_camera.gd` KNOWN: ours. The integration head had already dropped the M3-HER-1159 rows
  (act1-chapters' fix, big23), and theirs re-added them along with `coilspire.tscn:Encounter`.
- ui, `objectives.json`: ours at the ui step. ui's edit only touched the zone-level rows, and the integration head held act2-plan's
  per-chapter rows there.
- act2-plan, `objectives.json`: the owner now ships ui's 17 zone-level main rows (their 30 per-chapter main rows were dropped
  and kept in git; see act2-plan.md 2026-10-30), so I took theirs. ui's M4-UI-PLAYTEST `until: null` fix is
  re-applied on top to reed_clutch, low_sanctum, cloudloom_dais, archive_ledgers and court_barge. ui's qa_known
  `unraised` ch14_started and ch14_declared_heretics rows now match those rows.
- PROVENANCE: removed three stale duplicate rows that were already on the integration head (ysolde_theme .ogg/.loop.json
  from before M3-AUD-863; asha.glb from before the donor). No new duplicate PROVENANCE rows, loc keys or shot ids.

## Build checks
validate_data 0/0 · taskboard --check clean · gdlint clean · gdformat clean (1046 files) · no conflict markers.

GATE-BUILT @ 019596bb (merge tip; this log commit sits on top)

## Fast gate
- Selected: 71 test files (changed tests plus tests naming changed res:// paths or class_names). Lane A (mine) has 36;
  lane B (GATE-HELPER) has 35, in `gate-big24-lanes-b.txt` @ 797b02cc.

## Mid-batch playtest FAST-TRACK (14:3x)
- claude/hero-integration @ 99989c2b (MERGE-READY): the field stays resident through a random fight (the return
  re-attaches the zone: 389 ms black, not 1.7–6.5 s); FieldShore keeps the hero off dock edges into the sea.
  `scene_swap_probe.gd` conflicted with ui's 8df5fe2b (keeps the zone's loads through a field battle, also in big24):
  two independent probe modes, so both are kept (`--round-trip=` from ui, plus `--return=`/`--no-resident` from hero-integration).
  The runtime fixes compose: ui's in `resident_loads.gd`, hero-integration's in `scene_router.gd`.
- Re-gated: re-import, boot, and the 46 test files this merge touches (scene_router/field/shore users), run by me after my lane A.
- Characters' jog (b344b974): pushed at 14:15 but not yet MERGE-READY; it will be merged into big24 the moment it is.
- Per the Lead (14:28), also merged:
  - claude/creatures @ 6a4cbe78 (the Kirru crowd; the big23 test_resident_loads FAST-TRACK: Haluna's scene_loads.json regenerated).
    `tools/dev/blender_builds.json` conflicted where both sides appended new jobs (ours oruvel_seabed, theirs four crowd_kirru_*);
    both kept, 147 jobs, no duplicate id.
  - claude/env-art-b @ 04ad9b5d (MERGE-READY @ 02640c97, Pemakar's shore walls). Clean; a local import-written
    test_battle_screen_spread.gd.uid was removed so the committed one wins.
  - Checks after these: validate_data 0/0 · taskboard clean · gdlint and gdformat clean (1051 files) · no new duplicate PROVENANCE rows.
  - Re-gate list: 49 files (the hero-integration 46 plus 3 for these merges).
- claude/characters @ f277973a (MERGE-READY @ b344b974: the human playtest FAST-TRACK, the default run is a brisk,
  grounded jog for Asha, Rhen and Toma). Clean. Checks: validate_data 0/0 · gdlint and gdformat clean · no new duplicate PROVENANCE rows.
  big24 now carries all five playtest fixes: ui's battle return and objectives, hero-integration's resident field and
  water guard, env-art-b's shore walls, creatures' resident-loads fix, and characters' jog.
- Re-gate list: 53 files (the merges' selections, plus the jog's locomotion/clip users, plus test_causeway_route).

## Lane B (GATE-HELPER), @ 797b02cc, arrived 14:33
- 35 files: 33 green.
  - test_resident_loads: 9/1, Haluna's shop villagers unlisted. creatures' 9b29d8b3 (merged since) regenerates
    scene_loads.json for exactly this; re-gated.
  - test_causeway_route: 5/1, "at least 2 fights (206 m walk)" after the Harrier. Classifying on big23's tree; re-gated
    on the jog build.
- Per the Lead (14:48), also merged:
  - claude/act1-chapters @ d137f127 (MERGE-READY b368c93a: the causeway's generator keeps the 95–145 m band, which fixes
    test_causeway_gameplay's stale layout and big23's test_causeway_route expectation). Task file M4-A2P-0401
    `owner_session` taken from its owner, act1-chapters.
  - claude/env-art @ a01a7336 (MERGE-READY b45addab: the Prologue–Ch4 walk pass, H07 marble, Ch11 gallery arena). Clean.
  - claude/env-art-b @ 42c30e8e (MERGE-READY 4516750e: Ashcrown/Coilspire eye-height pass). Clean.
- **Merge fallout, fixed (08119e97):** tools test_npc `Kirru.test_the_clip_library_is_pells_and_up_to_date` was green on
  claude/creatures and red on the merge. characters' 5bb7e0ed (Pell pass 5) regenerated `pell_clips.tres`, from which the
  Kirru crowd's clips derive. Regenerated with `assets_src/crowd/kirru/kirru_clips.py`; test_npc is now 33/0.
- Tools suite (-j 2): reds were test_causeway_gameplay (fixed by act1-chapters' b368c93a; re-run green on the final tree),
  test_npc (fixed above), and the known test_palette_check, test_screenshots and test_villagers.
- **Process note:** lane A's last 12 files ran after the hero-integration merge landed in the same worktree without a
  re-import (FieldShore wasn't in the class cache), so they were invalid. All are re-run in the 83-file re-gate on
  the final tree (fresh import), which also covers every mid-batch merge.
- Checks on the final tree: validate_data 0/0 · taskboard clean · gdlint and gdformat clean (1052 files) · no new duplicate PROVENANCE rows.

## Re-gate on the final tree (04e26ad4): 83 files, fresh import
- Import check clean · boot 0 ERROR lines · log check 0 · 81/83 green.
- **test_causeway_route** 5/1 ("at least 2 fights (206 m walk)" after the Harrier). Red on claude/act1-chapters @ d137f127
  alone, so branch content. b368c93a fixed test_causeway_gameplay (the generator's 95–145 m band), not this test's
  2–3 fight expectation under the new pacing. Routed: **act1-chapters**.
- **test_qa_field_camera** 2/1: `lowlight.tscn:Sanctum (shot Hall): the leader is out of frame`. Batch-caused:
  green on the integration head, claude/hero-integration, claude/env-art and claude/characters; red on big24 from
  2f12e5ac (the hero-integration FAST-TRACK merge) on, and green at 0b486cd8 just before it. Root cause, found with
  the Lead's merge already done (no longer bisecting, per the Lead 15:49):
  - Lowlight's base `Water` (lowlight.tscn, y −2.05, plane box x 32–72) covers the Sanctum spawn (60, −8, 4), so the
    hero stands about 6 m under the surface. That water came in big23 (act1-chapters' M4-A2P-0411 Ch11 mount);
    hero-integration's branch has the older lowlight, with no water, so its own run is green.
  - `FieldShore.settle()` lacks the seabed exemption that `refuses()` and the class comment have ("more than
    underwater_m under the surface walks the seabed ... with no shore rule at all"). Grounded 6 m down, settle puts him
    back on `last_safe`; in the test that's the EngineHall spawn, so the Hall shot loses him. With the shore off,
    the test is green.
  - **In play:** the same gap snaps a hero back out of Lowlight's sanctum. Also check whether `refuses()` lets him walk
    down into it at all: each step deeper than deep_water_m from shallower ground is refused until he is already
    past underwater_m.
  - **Proposed patch** (verified: test_qa_field_camera 2/0 with it; the other shore tests were not finished when the Lead merged):
    ```
    @@ -93,6 +93,8 @@ func settle(body: CharacterBody3D, grounded: bool) -> bool:
     	var at := body.global_position
     	var water := water_y(body, at)
     	var under := water - at.y if not is_nan(water) else -INF
    +	if under > float(cfg.get("underwater_m", INF)):
    +		return false  # he walks the seabed (Oruvel's underway, Lowlight's sanctum): no shore rule down there
     	if under <= float(cfg.get("deep_water_m", INF)):
     		last_safe = at
     		return false
    ```
  - Routed: **integration-qa (claude/hero-integration) as a playtest FAST-TRACK**, per the Lead (FieldShore vs the
    Sanctum spawn).
- Tools suite (-j 2): reds were test_causeway_gameplay (fixed by b368c93a, re-run green), test_npc (Kirru clips,
  fixed in 08119e97), and the known test_palette_check, test_screenshots and test_villagers.

GATE-FAST-DONE @ 04e26ad4 (the Lead merged it as efe7fb10, 15:49). Routed: act1-chapters (test_causeway_route);
integration-qa FAST-TRACK (FieldShore.settle vs Lowlight's Sanctum: test_qa_field_camera); known: test_palette_check,
test_screenshots, test_villagers.
