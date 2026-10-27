---
id: M3-CIN-1217
title: Act I stage actors cast with the villager models (ZoneCast); the named folk wear generic villagers until theirs exist
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-CRE-610]
milestone: M3
request-from: ""
---
## Goal
Queue item "real casts": the Act I zones' stage actors were capsules. Heroes get their bodies from hero-integration
(`HeroFieldActor.attach_stage`: Rhen, Asha, Toma today). The rest are villagers.

## Done
- `game/levels/act1/zone_cast.gd` (`ZoneCast`, a `Cast` node in each Act I zone .tscn): an actor row's
  `"cast": "<villager>"` puts `assets/characters/villagers/<villager>/<villager>_actor.tscn` on the actor (facing its
  -Z), hides the capsule, plays `idle` from the actor's own phase (HeroIdleMicro.share, as FieldNpc) and adds the
  idle micro-motion; `@anim` lines find the same AnimationPlayer.
- Casts in ch04 (ferry, haluna_wake), ch05 (pemakar, ashcrown), ch06, ch07 (port, galleries), ch08 (corrow,
  coilspire), ch09: Neme, Osu and Tavi as themselves; everyone else as fisher, netmender, vendor, child or reed.
- `tests/unit/test_zone_cast.gd`.

## Not cast (on purpose)
Soldiers (stillguards, watch, officer), the Inquisitor, creatures and bosses (hound, spar_wraith, matron), the dead
(Ivo's shroud), heroes without a field body (Ysolde, Liss, Kerrid, Pell; vigil_* doubles), `board`, `figure`.

## Requests
- M3-CHR-1218 (character): models for the named Act I folk who now wear a generic villager (Garo, Marra, Hobb,
  Fenn, Ione), and the soldiers (Stillguard, the watch).
- M3-HER-1219 (hero-integration): a field body for Ysolde (her glb exists; `hero_motion.json` field.heroes has
  Rhen, Asha and Toma), so her stage actors and her follower are her.

## Review log
