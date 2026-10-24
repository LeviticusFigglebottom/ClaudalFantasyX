---
id: M2-HER-1102
title: "Field party followers: Asha and Toma follow Rhen in a trail with the same locomotion"
role: architect
status: review
owner_session: "hero-integration (claude/hero-integration)"
reviewer: character
depends_on: [M2-HER-1101]
milestone: M2
request-from: lead
---
## Goal
The joined heroes (Game party_ids after Rhen) walk behind him in the field, on his trail, with the same gait blend and
eased turning, so the party reads as a party.

## Acceptance criteria
- [x] Followers come from the live party (Game.state.party_ids), at most two, in party order, and appear or leave
      as heroes join (flag_changed).
- [x] Each follows the leader's breadcrumb trail at a data-driven spacing, accelerates and decelerates on curves,
      never overlaps the leader, and catches up (teleports) after a zone load or a long jump.
- [x] Ground-aligned by a ray to the floor; no physics body (they never block the player or trip triggers).
- [x] Hidden while the zone's CutsceneStage shows the same hero as an actor (no doubles), and while a cutscene plays.
- [x] Tests: trail spacing, catch-up, no follower for an absent hero, hidden while the stage actor shows. Shot
      field_hero_party (viewed).

## Notes
- **Built (worktree agent, 2026-10-24):** `game/hero_motion/hero_field_party.gd` (HeroFieldParty, added by
  HeroFieldActor.attach under the controller). Each follower is a plain top_level Node3D anchor (no physics body)
  with a HeroFieldActor child, so it shares the gait blend and the eased turn. Tuning: hero_motion.json
  `field.followers` (spacing 1.15 m, a crumb every 0.2 m, follow gain 3/s on top of the leader's speed, accel 9,
  decel 12, min gap 0.8 m, catch-up beyond 6 m, ray 1 m up / 3 m down excluding the player).
- The party is re-read every physics frame (Game.state.party_ids, leader excluded, at most 2): this covers
  PartyJoins on EventBus.flag_changed and zones that write party_ids directly (ZoneStory) alike.
- Hidden while a CutsceneSequencer with hold_player is playing (the overhear barks, hold_player false, do not
  hide them), while the zone's CutsceneStage shows a visible `Actors/<same id>`, and while the player is hidden;
  on showing again they are laid on a fresh trail behind the leader. The zone is searched for stages and
  sequencers every rescan_sec (0.5 s) by script class name.
- Tests: tests/unit/test_hero_followers.gd 7/0 (party order and leader excluded; no follower for an absent hero
  and a join adds one at once; spacing within 0.35 m at a run and at rest, never under min_gap; feet on the floor;
  teleport catch-up with no gait; hidden while the stage shows Asha; hidden while a cutscene holds the player).
- Shot field_hero_party viewed: Rhen leads, Asha then Toma behind on his arc, all facing their travel, feet down.
- Known limits: catch_up lays the trail straight behind the leader's facing, so after a teleport next to a wall a
  follower can stand inside it for a moment until the trail fills; followers do not avoid obstacles (they walk
  the leader's own path, which is clear by construction).

## Review log
