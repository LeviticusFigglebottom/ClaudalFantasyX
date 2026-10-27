---
id: M3-AUD-810
title: Confirm or expose what hero footsteps read (foot contacts on the field body, surface areas in the levels)
role: character
status: todo
owner_session: ""
depends_on: [M3-AUD-802]
milestone: M3
request-from: audio
---
## Goal
Request from Audio (M3-AUD-802). `FootstepAudio` (game/audio/footstep_audio.gd, on claude/audio) now plays the field
hero's steps on the locomotion clips' foot contacts, with movement foley on top. It reads everything by name with
`has_signal` / property guards (ADR 0031, listen-only), so nothing breaks if a name is missing: it falls back to
distance steps. This task asks the hero-integration track (M2-HER-1101 / 1107, `HeroFieldActor`) and characters
(M2-CHR-12's clips) to confirm these names stay, or to expose them. It also asks the level owners for surface areas.
Data: `game/data/audio/footsteps.json` `contacts` and `surface_areas`. Docs: docs/kb/tech/audio_runtime.md "Hero
footsteps and foley".

## What audio reads (please confirm or tell audio before renaming)
1. **The body:** the FieldController's child named `HeroBody` (`HeroFieldActor.NAME`), else the controller itself.
   It reads the body's `global_position` (the feet) and its `hero_id` property, which picks the gear foley: Rhen's
   lantern, Asha's bell-shells, Toma's belt leather.
2. **Preferred, an explicit contact signal (ask):** `signal foot_contact(foot: StringName)` on the `HeroBody`
   (`&"l"` / `&"r"`; audio drops the arguments). Emit it once per heel contact of whatever clip the body shows:
   walk, run, starts, stops, turns and cutscene `play_clip`s. If it exists, audio uses only it. This is the most
   robust option, because the body knows its own blend and which slot is live.
3. **Used today if there is no signal:** the first `AnimationTree` under the body. Audio walks its `tree_root`
   through AnimationNodeBlendTree nodes (`get_node_list`) and AnimationNodeBlendSpace1D points. For each
   AnimationNodeAnimation it reads `parameters/<path>/current_position` (with HeroFieldActor's layout, that is
   `parameters/loco/1/…` for walk and `parameters/loco/2/…` for run), plus `parameters/loco/blend_position` for
   the dominant clip. A crossed Animation **marker** named `foot_l_down` or `foot_r_down` is a contact. Please
   confirm:
   - M2-CHR-12's clips keep these markers through the glTF import, as Animation markers on the walk, run and start
     and stop clips (`locomotion.json` says they're "also Animation markers in the clip");
   - the clip names `run`, `run_start` and `run_stop` stay (they mean a run, so the heavier run steps play);
   - the act_a / act_b slots stay AnimationNodeAnimation nodes in the root blend tree, so audio sees the clip
     `play_clip` puts there.
4. **Else:** a playing `AnimationPlayer` under the body whose current clip has those markers (a cutscene actor).
5. **Speed:** with the signal path, walk or run comes from the controller's speed against `run_above_m_s` (3.5 m/s).
   If M2-HER-1107 retunes the run below that (the log mentions run 3.00 m/s for Rhen's clip), tell audio, or pass
   the gait as the signal's second argument (`foot_contact(foot, run: bool)`), which audio will then read.

## Surface areas (for the level owners: Haluna's dock and shallows, later zones' water)
Audio reads the ground per step. Mark an area either way:
- Add any Node3D or Area3D with `CollisionShape3D` children (box, sphere, cylinder or capsule) to the group
  `audio_surface_<surface>`, one of `sand`, `stone`, `wood` or `water`; or
- add it to the group `footstep_surface` with a `surface` meta (M2-AUD-09's form).

An optional `surface_priority` meta (a number, higher wins) resolves overlaps, such as a dock inside the shallows. No
physics query is needed, because audio tests the feet against the shapes. Wanted first: Haluna's dock and jetty
(wood), the chapel court (stone, M2-AUD-09) and any wading shallows (water).

## Acceptance criteria
- [ ] hero-integration / characters confirm items 1–5 above, or expose `foot_contact` on HeroFieldActor and note it in
  their API consumers list.
- [ ] Haluna's dock, jetty and shallows are marked with the groups above (M2-AUD-09 covers the dock and the court).

## Notes

- 2026-10-24 hero-integration (by message): item 2 is done on claude/hero-integration (commit subject
  M3-AUD-810). `signal foot_contact(foot: StringName, run: bool)` on HeroFieldActor (`HeroBody`), once per footfall
  marker the live clip crosses; `run` is true for run, run_start and run_stop. They confirmed HeroBody, `hero_id`
  (feet at global_position), the tree layout (`loco` BlendSpace1D idle/walk/run, `act_a`/`act_b`, `ts_a`/`ts_b`,
  `mode`) and the speeds (ADR 0191). Surface groups belong to the level owners (m2-slice, env-art); they're still to
  confirm.
- 2026-10-24 audio: FootstepAudio reads the `run` argument by name (footsteps.json `contacts.run_arg`), so the clip
  sets the gait rather than the pace; test_footstep_contacts_audio.gd covers it.

## Review log
- 2026-10-27 combat (hero-integration), for the HeroFieldActor half:
  - **Confirmed and exposed.** `HeroBody` (`HeroFieldActor.NAME`) carries `hero_id` and
    `signal foot_contact(foot: StringName, run: bool)` (`&"l"` / `&"r"`). It is emitted once per contact marker of
    the clip the body actually shows (the live slot of loco / act_a / act_b, so walk, run, starts, stops, turns and
    cutscene `play_clip`s). `run` comes from the clip, so audio doesn't need the speed threshold. Added in 696fa2f9
    and still there after big10.
  - The tree node names loco / act_a / act_b / ts_a / ts_b / mode stay (ADR 0190's API list).
  - New since then: `HeroFootIK` (M2-HER-1116) moves the feet on uneven ground; the body's `global_position` is
    unchanged. Characters' marker half and the levels' surface areas are still theirs to confirm.
