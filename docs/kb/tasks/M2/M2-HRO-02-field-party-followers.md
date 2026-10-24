---
id: M2-HRO-02
title: "Field party followers: Asha and Toma follow Rhen in a trail with the same locomotion"
role: architect
status: doing
owner_session: "hero-integration (claude/hero-integration)"
reviewer: character
depends_on: [M2-HRO-01]
milestone: M2
request-from: lead
---
## Goal
The joined heroes (Game party_ids after Rhen) walk behind him in the field, on his trail, with the same gait blend and
eased turning, so the party reads as a party.

## Acceptance criteria
- [ ] Followers come from the live party (Game.state.party_ids), at most two, in party order, and appear or leave
      as heroes join (flag_changed).
- [ ] Each follows the leader's breadcrumb trail at a data-driven spacing, accelerates and decelerates on curves,
      never overlaps the leader, and catches up (teleports) after a zone load or a long jump.
- [ ] Ground-aligned by a ray to the floor; no physics body (they never block the player or trip triggers).
- [ ] Hidden while the zone's CutsceneStage shows the same hero as an actor (no doubles), and while a cutscene plays.
- [ ] Tests: trail spacing, catch-up, no follower for an absent hero, hidden while the stage actor shows. Shot
      field_hero_party (viewed).

## Review log
