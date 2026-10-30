---
id: M3-AUD-812
title: "FAST-TRACK: footsteps change surface on every slice ground (sand, wood, stone, shallow water) with no level edits"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-802]
milestone: M3
request-from: lead
---
## Goal
The human's playtest ("parts look primitive"): the field steps sounded the same everywhere. M3-AUD-802 had four
surfaces, but only the scene default (sand in Haluna, stone elsewhere) ever played, because no level marks wood or
water (M3-AUD-811 is still open with the level owners). Make every slice zone's ground heard now, by listening only.

## Acceptance criteria
- [x] Haluna: sand on the beach and in the village, wood on the dock (the `dock_haluna` kit mesh), water in the
      shallows (feet under the sea's rest plane, `hymn_water_level_publishers`).
- [x] Saltgrass Causeway: stone on the path (an explicit `scenes` row), water in the greybox tidepool.
- [x] Shell Shrine: stone (and water in its pools, `*PoolWater`).
- [x] Level surface areas (M3-AUD-811's groups) still win wherever a level adds them.
- [x] Steps keep their variation (6 no-repeat variants, ±4% pitch) and never machine-gun (0.15 s contact merge,
      120 ms row cooldown). Verified against hero-integration's real `HeroFieldActor.foot_contact(foot, run)`.
- [x] Tests: tests/unit/test_footstep_ground_audio.gd (stand-ins) and tests/integration/test_footsteps_slice_zones.gd
      (the real scenes; its hero-body walk runs once claude/hero-integration is merged).

## Notes
- 2026-10-25 audio: footsteps.json `mesh_surfaces` (name globs on a MeshInstance3D or its parent, tested against the
  mesh's own bounds grown `up_m`/`down_m`; LOD meshes skipped; the zone is rescanned every `rescan_sec`) and
  `water_level` (wade under the zone sea by up to `wade_m`). Order: a level's area, then a mesh rule, then wading,
  then the scene's surface. data_check validates both blocks. Haluna's Beach spawn (y 0.04, sea at 0.15) is ankle
  deep, so it steps in water: the waterline is at x ≈ −3.5.
- M3-AUD-811 stays open: level-authored areas are still the precise answer (for example under the dock, where the
  mesh bounds also cover the sand).

- 2026-10-27 audio, **verified on a scratch merge with claude/hero-integration** (the real HeroFieldActor): its
  foot_contact steps (26/0 across the footstep tests). The probe found that hero-integration's walk clip has **no
  footfall markers yet** (characters' M2-CHR-12), so the body never emits, and FootstepAudio stepped only once per
  `stall_m` (1.6 m). Fixed: after a stall it steps by distance until a contact arrives
  (test_a_hero_body_without_footfall_markers_still_walks_at_stride). The tests set the controller's `_grounded`,
  since they run no physics.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
