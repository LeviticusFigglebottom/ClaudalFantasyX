---
id: M3-CHR-1218
title: Models for Act I's named folk and soldiers (they wear generic villagers or capsules today)
role: character
status: todo
owner_session: ""
depends_on: [M3-CIN-1217]
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters casts the Act I zones' stage actors with the villager models (M3-CIN-1217, `"cast"` on each actor row
in the zone layouts). Named people with lines or close shots wear a generic villager until they have their own:
- **Garo** (Pemakar's smith, B03 "The Smith's Question", P07): `fisher`.
- **Marra** (Corrow, Ch8-Ch9): `netmender`. **Hobb** and **Fenn** (Corrow, Ch8-Ch9): `fisher`.
- **Ione** (Sorrin's captain, Ch7, on the east prow): `vendor`.
Soldiers have no model and stay capsules: the **Stillguard** (Ch6, Ch8, Ch9), Corrow's **watch** and **officer**.

When a model lands as `assets/characters/villagers/<id>/<id>_actor.tscn` (the villager convention: the model turned
to face -Z, its AnimationPlayer with idle, talk and walk), change the actor's `"cast"` to it (or say so in the
act1-chapters live log and act1-chapters will).

## Acceptance criteria
- [ ] Models for Garo, Marra, Hobb, Fenn, Ione; a Stillguard soldier (one model for the rows).

## Review log
